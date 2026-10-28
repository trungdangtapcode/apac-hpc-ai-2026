#!/usr/bin/env python3
"""Resolve native shallow-EAGLE arguments without launching workers or reading weights."""
from pathlib import Path
import argparse,hashlib,inspect,json,os,sys,traceback
Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');A=Q/'runs'/os.environ['SLURM_JOB_ID'];A.mkdir(parents=True,exist_ok=True)
result={'state':'RUNNING_ARGUMENT_CONFIGURATION_ONLY','scope':'One visible H200; TP8/EP8 is configuration intent, not distributed operation. No model worker, inference, KV, P/D, quality or speed claim.'}
def write():(A/'arguments.json').write_text(json.dumps(result,indent=2)+'\n')
try:
 import torch
 assert torch.cuda.is_available() and torch.cuda.device_count()==1 and 'H200' in torch.cuda.get_device_name(0)
 assert not torch.distributed.is_initialized()
 result['gpu']=torch.cuda.get_device_name(0);result['visible_devices']=1
 # Stop Python-level attempts to open binary weight shards; metadata/index JSON is allowed.
 def audit(event,args):
  if event=='open' and args and isinstance(args[0],(str,bytes)):
   path=os.fsdecode(args[0])
   if path.endswith(('.safetensors','.bin')):raise RuntimeError('Binary model-weight reads are forbidden in argument prerequisite')
 sys.addaudithook(audit)
 from sglang.srt.server_args import prepare_server_args,ServerArgs
 native=Path(inspect.getfile(ServerArgs));h=hashlib.sha256(native.read_bytes()).hexdigest();assert h=='79d9bbb61b429574e31e7a7e319831fcd129a83a475e6ffe2b7e8a5e8eb06b0f'
 argv=['--model-path','/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8','--trust-remote-code','--context-length','8192','--tp-size','8','--ep-size','8','--dtype','bfloat16','--mem-fraction-static','0.90','--disaggregation-mode','decode','--disaggregation-transfer-backend','nixl','--max-running-requests','256','--decode-attention-backend','flashinfer','--moe-runner-backend','hpc_ops','--flashinfer-allreduce-fusion-backend','mnnvl','--cuda-graph-backend-prefill','disabled','--cuda-graph-max-bs-decode','64','--cuda-graph-bs-decode',*[str(i) for i in range(1,65)],'--speculative-algorithm','EAGLE3','--speculative-draft-model-path',str(Q/'hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09'),'--speculative-num-steps','1','--speculative-eagle-topk','1','--speculative-num-draft-tokens','2','--speculative-draft-attention-backend','flashinfer','--speculative-draft-model-quantization','unquant']
 parser=argparse.ArgumentParser();ServerArgs.add_cli_args(parser);raw=parser.parse_args(argv)
 assert (raw.speculative_num_steps,raw.speculative_eagle_topk,raw.speculative_num_draft_tokens)==(1,1,2)
 actual=prepare_server_args(argv)
 fields=['tp_size','ep_size','dtype','disaggregation_mode','speculative_algorithm','speculative_num_steps','speculative_eagle_topk','speculative_num_draft_tokens','speculative_draft_model_path','speculative_draft_attention_backend','speculative_draft_model_quantization','moe_runner_backend','decode_attention_backend','flashinfer_allreduce_fusion_backend']
 selected={k:getattr(actual,k) for k in fields}
 assert (actual.speculative_num_steps,actual.speculative_eagle_topk,actual.speculative_num_draft_tokens)==(1,1,2),'Native policy silently changed proposed shallow geometry'
 assert actual.tp_size==actual.ep_size==8 and actual.dtype=='bfloat16' and actual.disaggregation_mode=='decode'
 assert actual.speculative_algorithm=='EAGLE3' and actual.speculative_draft_attention_backend=='flashinfer' and actual.speculative_draft_model_quantization is None
 assert not torch.distributed.is_initialized()
 assert torch.cuda.max_memory_allocated(0)<256*1024**2,'Unexpected large CUDA allocation in configuration-only probe'
 result.update(state='PASS_NATIVE_ARGUMENT_CONFIGURATION_ONLY',source_sha256=h,resolved=selected,max_cuda_allocated_bytes=torch.cuda.max_memory_allocated(0),distributed_initialized=False,binary_weight_reads_allowed=False)
 write();print(result['state'])
except BaseException as e:
 result.update(state='FAIL_ARGUMENT_PREREQUISITE',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());write();raise
