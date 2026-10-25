#!/usr/bin/env python3
"""Verify per-role native S62 runtime settings and rank-level readiness."""
import ast, collections, json, re, sys
from pathlib import Path
art=Path(sys.argv[1]); arm=sys.argv[2]; prefill_cap=int(sys.argv[3]) if len(sys.argv)>3 else 64
if arm!='control' or prefill_cap<1: raise SystemExit('usage: check-fast-runtime.py ART control [prefill-cap]')
roles={'prefill-0':4,'prefill-1':4,'decode-0':4,'decode-1':4}; evidence={}
model='/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8'
def kwmap(node,label):
 if not isinstance(node,ast.Call) or node.args: raise ValueError(f'{label}: expected keyword-only call')
 names=[x.arg for x in node.keywords]
 if any(n is None for n in names) or len(names)!=len(set(names)): raise ValueError(f'{label}: duplicate or expanded keyword')
 return {x.arg:x.value for x in node.keywords}
def lit(m,key,label):
 if key not in m: raise ValueError(f'{label}: missing {key}')
 try:return ast.literal_eval(m[key])
 except (ValueError,TypeError) as e: raise ValueError(f'{label}: {key} is not a literal') from e
for role,nranks in roles.items():
 text=(art/f'{role}.log').read_text(errors='replace')
 if text.count('The server is fired up and ready to roll!')!=1: raise ValueError(f'{role}: native ready marker absent or duplicated')
 records=[x.split('server_args=',1)[1] for x in text.splitlines() if 'server_args=ServerArgs(' in x]
 if len(records)!=1: raise ValueError(f'{role}: expected one resolved ServerArgs')
 node=ast.parse(records[0],mode='eval').body
 if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id!='ServerArgs': raise ValueError(f'{role}: malformed ServerArgs')
 args=kwmap(node,role); is_p=role.startswith('prefill'); tp=nranks
 common={'model_path':model,'dtype':'bfloat16','context_length':8192,'mem_fraction_static':0.9,
  'disaggregation_mode':'prefill' if is_p else 'decode','disaggregation_transfer_backend':'nixl','trust_remote_code':True,
  'kv_cache_dtype':'auto','tp_size':tp,'ep_size':1 if is_p else 4,'moe_dp_size':1,
  'max_running_requests':prefill_cap if is_p else 128,'enable_deterministic_inference':False,
  'sampling_backend':'flashinfer','disable_custom_all_reduce':False,'attention_backend':'fa3'}
 if is_p: common.update(chunked_prefill_size=8192,moe_runner_backend='deep_gemm',flashinfer_allreduce_fusion_backend='auto')
 else: common.update(moe_runner_backend='hpc_ops',decode_attention_backend='flashinfer',flashinfer_allreduce_fusion_backend='mnnvl')
 for key,wanted in common.items():
  got=lit(args,key,role)
  if got!=wanted: raise ValueError(f'{role}: {key}={got!r}, expected {wanted!r}')
 spec={'speculative_algorithm':None,'speculative_draft_model_path':None,'speculative_num_steps':None,
  'speculative_eagle_topk':None,'speculative_num_draft_tokens':None,'speculative_draft_attention_backend':None,
  'speculative_draft_model_quantization':None}
 for key,wanted in spec.items():
  if lit(args,key,role)!=wanted: raise ValueError(f'{role}: expected target-only {key}={wanted!r}')
 graph=kwmap(args.get('cuda_graph_config'),role+'.cuda_graph_config')
 if set(graph)!={'decode','prefill'}: raise ValueError(f'{role}: incomplete graph config')
 pg=kwmap(graph['prefill'],role+'.prefill-graph'); dg=kwmap(graph['decode'],role+'.decode-graph')
 if lit(pg,'backend',role)!='disabled': raise ValueError(f'{role}: prefill CUDA graphs must be disabled')
 if is_p:
  if lit(dg,'backend',role)!='disabled': raise ValueError(f'{role}: prefill worker decode graphs must be disabled')
 else:
  if lit(dg,'backend',role)!='full' or lit(dg,'max_bs',role)!=64 or lit(dg,'bs',role)!=list(range(1,65)):
   raise ValueError(f'{role}: decode graph batches must resolve to full 1..64')
 kv=re.findall(r'TP(\d+)(?: EP(\d+))?\] KV Cache is allocated\. dtype: torch\.([a-z0-9]+), #tokens: ([1-9][0-9]*), K size: ([0-9]+(?:\.[0-9]+)?) GB, V size: ([0-9]+(?:\.[0-9]+)?) GB',text)
 got=collections.Counter(x[0] for x in kv)
 if got!=collections.Counter({str(i):1 for i in range(nranks)}) or {x[2] for x in kv}!={'bfloat16'} or any(float(x[4])<=0 or float(x[5])<=0 for x in kv): raise ValueError(f'{role}: BF16 KV allocation rank/count mismatch: {dict(got)}')
 nixl=collections.Counter(re.findall(r'TP(\d+)(?: EP\d+)?\] NIXL KVManager initialized',text))
 if nixl!=collections.Counter({str(i):1 for i in range(nranks)}): raise ValueError(f'{role}: NIXL rank initialization mismatch')
 disabled=collections.Counter(re.findall(r"TP(\d+)(?: EP\d+)?\] Disable prefill CUDA graph because cuda_graph_config resolved prefill\.backend='disabled'",text))
 if disabled!=collections.Counter({str(i):1 for i in range(nranks)}): raise ValueError(f'{role}: prefill graph-disabled markers incomplete')
 if not is_p:
  mnnvl=set(re.findall(r'FlashInfer AllReduce Fusion enabled and workspace initialized: backend=mnnvl, rank=(\d+), world_size=4',text))
  if mnnvl!=set(map(str,range(nranks))): raise ValueError(f'{role}: native MNNVL initialization missing ranks')
  captured=set(re.findall(r'TP(\d+) EP\d+\] Capture target decode CUDA graph end\.',text))
  if captured!=set(map(str,range(nranks))): raise ValueError(f'{role}: target decode graph completion missing ranks')
 evidence[role]={'tp_ranks':nranks,'bf16_kv_records':len(kv),'nixl_rank_records':sum(nixl.values()),'decode_graph':'full 1..64' if not is_p else 'disabled'}
print(json.dumps({'state':'PASS_FAST_RUNTIME','arm':arm,'prefill_cap':prefill_cap,'roles':evidence,
 'scope':'Resolved native arguments and rank-level BF16 KV, NIXL, graph and MNNVL startup checks; not a kernel-performance or model-quality proof.'},indent=2))
