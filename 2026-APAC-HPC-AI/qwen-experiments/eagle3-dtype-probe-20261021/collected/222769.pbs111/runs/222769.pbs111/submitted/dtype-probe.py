"""Allocated native dtype/shared-embedding/norm fixture; no full attention inference."""
import argparse,hashlib,json,os,traceback
from datetime import datetime,timezone
from pathlib import Path
from gpu_identity import require_same_device

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--draft',type=Path,required=True);p.add_argument('--target',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
r=dict(created_utc=datetime.now(timezone.utc).isoformat(),job=os.environ.get('PBS_JOBID'),passed=False,full_target_loaded=False,target_embedding_loaded=False,attention_or_target_inference=False,modes=[])
def save(stage):
 r['stage']=stage;a.out.write_text(json.dumps(r,indent=2)+'\n')
try:
 save('importing')
 import torch
 from safetensors import safe_open
 from sglang.srt.configs.model_config import ModelConfig
 from sglang.srt.model_loader.utils import get_model_architecture
 from sglang.srt.runtime_context import publish
 from sglang.srt.server_args import ServerArgs
 from sglang.srt.distributed import init_distributed_environment,initialize_model_parallel
 from sglang.srt.layers.dp_attention import initialize_dp_attention
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 assert torch.cuda.device_count()==1
 require_same_device(os.environ['CUDA_VISIBLE_DEVICES'],str(torch.cuda.get_device_properties(0).uuid))
 for path,digest in json.loads((Path(__file__).parent/'expected-sources.json').read_text()).items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
 expected=json.loads((Path(__file__).parent/'target-staging-record.json').read_text());assert expected['complete'] and not expected.get('errors')
 for name in ['config.json','model.safetensors.index.json']:
  assert hashlib.sha256((a.target/name).read_bytes()).hexdigest()==expected['verified'][name]['sha256'],name
 key='model.embed_tokens.weight';index=json.loads((a.target/'model.safetensors.index.json').read_text());shard=index['weight_map'][key]
 assert '/' not in shard and (a.target/shard).stat().st_size==expected['verified'][shard]['bytes']
 with safe_open(a.target/shard,framework='pt',device='cpu') as store:embedding=store.get_tensor(key)
 assert embedding.dtype==torch.bfloat16 and list(embedding.shape)==[151936,4096]
 target_embedding=torch.nn.Parameter(embedding.to('cuda:0'),requires_grad=False)
 r.update(target_embedding_loaded=True,embedding=dict(shard=shard,shape=list(embedding.shape),dtype=str(embedding.dtype),staged_shard_sha256=expected['verified'][shard]['sha256'],limit='Reuses full verified staging digest with fresh shard size; does not rehash entire large shard'))
 digest=hashlib.sha256()
 with (a.draft/'model.safetensors').open('rb') as f:
  while block:=f.read(4194304):digest.update(block)
 assert digest.hexdigest()=='bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'
 grouped=False
 for mode in ['auto','bfloat16']:
  save('config_'+mode)
  server=ServerArgs(model_path=str(a.target),dtype=mode,skip_tokenizer_init=True,disable_cuda_graph=True,disable_custom_all_reduce=True,attention_backend='flashinfer',speculative_algorithm='EAGLE3',speculative_draft_model_path=str(a.draft),speculative_num_steps=2,speculative_eagle_topk=1,speculative_num_draft_tokens=3,speculative_draft_model_quantization='unquant' if mode=='bfloat16' else None)
  target=ModelConfig.from_server_args(server,model_path=str(a.target),context_length=8192)
  draft=ModelConfig.from_server_args(server,model_path=str(a.draft),is_draft_model=True,context_length=8192)
  assert target.dtype==torch.bfloat16 and target.quantization=='fp8'
  assert draft.quantization is None and draft.dtype==(torch.float16 if mode=='auto' else torch.bfloat16)
  publish(server,role='scheduler',hf_config=target.hf_config)
  if not grouped:
   torch.cuda.set_device(0);init_distributed_environment(world_size=1,rank=0,local_rank=0,distributed_init_method='file:///tmp/eagle3-dtype-dist',backend='nccl',timeout=30);initialize_model_parallel(tensor_model_parallel_size=1,pipeline_model_parallel_size=1,backend='nccl');grouped=True
  initialize_dp_attention(server,draft)
  cls,arch=get_model_architecture(draft);assert arch=='LlamaForCausalLMEagle3'
  previous=torch.get_default_dtype()
  try:
   torch.set_default_dtype(draft.dtype)
   with torch.device('cuda:0'):model=cls(draft.hf_config,quant_config=None).eval()
  finally:torch.set_default_dtype(previous)
  with safe_open(a.draft/'model.safetensors',framework='pt',device='cpu') as store:model.load_weights((name,store.get_tensor(name)) for name in store.keys())
  model.set_embed(target_embedding)
  assert model.get_embed() is target_embedding and model.get_embed().data_ptr()==target_embedding.data_ptr()
  ids=torch.tensor([1,2,7,151645],dtype=torch.int64,device='cuda:0')
  with torch.inference_mode():embeds=model.model.embed_tokens(ids)
  norm=model.model.layers[0].input_layernorm
  row=dict(mode=mode,target_dtype=str(target.dtype),target_quantization=target.quantization,draft_dtype=str(draft.dtype),draft_quantization=draft.quantization,embedding_output_dtype=str(embeds.dtype),norm_weight_dtype=str(norm.weight.dtype),embedding_alias_exact=True)
  r['modes'].append(row);save('norm_'+mode)
  try:
   with torch.inference_mode():output=norm(embeds)
   torch.cuda.synchronize();row['native_norm_passed']=True
  except Exception as error:
   row.update(native_norm_passed=False,error=dict(type=type(error).__name__,message=str(error)))
   if mode!='auto':raise
  if mode=='auto':
   assert not row['native_norm_passed'] and 'expected dtype=bfloat16' in row['error']['message'],'Auto mismatch not reproduced'
   r['auto_mismatch_reproduced']=True
  else:
   assert row['native_norm_passed'] and output.dtype==torch.bfloat16 and torch.isfinite(output).all().item()
   with torch.inference_mode():
    for _ in range(3):norm(embeds)
    torch.cuda.synchronize();graph=torch.cuda.CUDAGraph()
    with torch.cuda.graph(graph):graph_output=norm(embeds)
    graph.replay();torch.cuda.synchronize()
   assert torch.equal(output,graph_output) and torch.isfinite(graph_output).all().item()
   row.update(cuda_graph_replay_exact=True,finite_output=True)
  del model,embeds,norm
  torch.cuda.empty_cache()
 r.update(passed=True,peak_fixture_vram_bytes=torch.cuda.max_memory_allocated())
 save('dtype_norm_fixture_pass_full_pd_unverified')
except Exception as error:
 r['failure']=dict(type=type(error).__name__,message=str(error));traceback.print_exc();save('failed')
finally:
 try:
  if 'torch' in locals() and torch.distributed.is_initialized():torch.distributed.destroy_process_group()
 except Exception:traceback.print_exc()
raise SystemExit(0 if r['passed'] else 1)
