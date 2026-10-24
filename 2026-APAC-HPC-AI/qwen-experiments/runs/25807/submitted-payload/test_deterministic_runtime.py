"""CPU fixture for strict resolved deterministic-runtime parser; not GPU evidence."""
import json,subprocess,sys,tempfile
from pathlib import Path
checker=Path(__file__).with_name("check-deterministic-runtime.py")
roles={"prefill-0":4,"prefill-1":4,"decode-0":8}
def log(role,n,sampling="pytorch",eagle=False):
 decode="GraphConfig(backend='full', max_bs=64, bs="+repr(list(range(1,65)))+")" if role=="decode-0" else "GraphConfig(backend='disabled')"
 args=f"ServerArgs(model_path='/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8', dtype='bfloat16', context_length=8192, mem_fraction_static=0.9, disaggregation_transfer_backend='nixl', disaggregation_mode={'prefill' if role.startswith('prefill') else 'decode'!r}, tp_size={n}, ep_size={1 if role.startswith('prefill') else 8}, kv_cache_dtype='auto', trust_remote_code=True, enable_deterministic_inference=True, sampling_backend={sampling!r}, attention_backend='fa3', prefill_attention_backend=None, disable_custom_all_reduce=True, cuda_graph_config=Graph(decode={decode}, prefill=GraphConfig(backend='disabled'))"
 if role=="decode-0": args+=", decode_attention_backend='flashinfer', flashinfer_allreduce_fusion_backend=None"
 if eagle: args+=", speculative_algorithm='EAGLE3', speculative_num_steps=2, speculative_eagle_topk=1, speculative_num_draft_tokens=3, speculative_draft_attention_backend='flashinfer', speculative_draft_model_path='/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09', speculative_draft_model_quantization='unquant'"
 args+=")"
 tp=[]
 for i in range(n):
  copies=2 if eagle else 1
  suffix=f" TP{i} EP{i}" if role=="decode-0" else f" TP{i}"
  tp += [f"[{role}{suffix}] KV Cache is allocated. dtype: torch.bfloat16" for _ in range(copies)] + [f"[{role}{suffix}] NIXL KVManager initialized"]
 msgs=["server_args="+args,"Sampling backend is set to pytorch for deterministic inference.","NCCL_ALGO is set to 'allreduce:tree' and custom all reduce is disabled for deterministic inference when TP size > 1."]
 if role=="decode-0": msgs.append("Disable --flashinfer-allreduce-fusion-backend because deterministic inference is enabled.")
 return "\n".join(msgs+tp)+"\n"
def invoke(bad=False,eagle=False):
 with tempfile.TemporaryDirectory() as td:
  root=Path(td)
  for role,n in roles.items(): (root/(role+".log")).write_text(log(role,n,"top_k" if bad and role=="prefill-0" else "pytorch",eagle=eagle))
  return subprocess.run([sys.executable,str(checker),td]+(["--eagle"] if eagle else []),capture_output=True,text=True)
candidate=Path(__file__).with_name("candidate-control.py").exists()
r=invoke(eagle=candidate); assert r.returncode==0,r.stderr
assert json.loads(r.stdout)["state"]=="PASS"
if not candidate:
 r=invoke(True); assert r.returncode!=0 and "sampling_backend" in r.stderr+r.stdout
print("DETERMINISTIC_RUNTIME_CPU_FIXTURES_PASS; parser fixtures are not GPU or kernel evidence")
