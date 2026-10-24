#!/usr/bin/env python3
"""Require resolved deterministic mode and all-rank runtime evidence; CPU parser only."""
import ast,collections,json,re,sys
from pathlib import Path
art=Path(sys.argv[1]); expected={"prefill-0":4,"prefill-1":4,"decode-0":8}; out={}
for role,n in expected.items():
 text=(art/f"{role}.log").read_text(errors="replace")
 lines=[x.split("server_args=",1)[1] for x in text.splitlines() if "server_args=ServerArgs(" in x]
 if len(lines)!=1: raise SystemExit(f"{role}: expected one resolved ServerArgs")
 call=ast.parse(lines[0],mode="eval").body
 kw={x.arg:x.value for x in call.keywords}
 def get(k):
  if k not in kw: raise ValueError(f"{role}: missing {k}")
  return ast.literal_eval(kw[k])
 checks={"model_path":"/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8","dtype":"bfloat16","context_length":8192,"mem_fraction_static":0.9,"disaggregation_transfer_backend":"nixl","disaggregation_mode":"prefill" if role.startswith("prefill") else "decode","tp_size":4 if role.startswith("prefill") else 8,"ep_size":1 if role.startswith("prefill") else 8,"kv_cache_dtype":"auto","trust_remote_code":True,"enable_deterministic_inference":True,"sampling_backend":"pytorch","attention_backend":"fa3","disable_custom_all_reduce":True,"prefill_attention_backend":None}
 if role=="decode-0": checks.update(decode_attention_backend="flashinfer",flashinfer_allreduce_fusion_backend=None)
 for k,v in checks.items():
  got=get(k)
  if got!=v: raise SystemExit(f"{role}: resolved {k}={got!r}; expected {v!r}")
 graph=kw.get("cuda_graph_config")
 if graph is None: raise SystemExit(f"{role}: missing resolved cuda_graph_config")
 graphkw={x.arg:x.value for x in graph.keywords}
 if set(graphkw)!={"decode","prefill"}: raise SystemExit(f"{role}: missing resolved decode/prefill graph settings")
 prefillkw={x.arg:x.value for x in graphkw["prefill"].keywords}
 if ast.literal_eval(prefillkw["backend"])!="disabled": raise SystemExit(f"{role}: prefill graph must resolve disabled")
 decodekw={x.arg:x.value for x in graphkw["decode"].keywords}
 if role.startswith("prefill"):
  if ast.literal_eval(decodekw["backend"])!="disabled": raise SystemExit(f"{role}: target-only decode graphs must resolve disabled")
 else:
  if ast.literal_eval(decodekw["backend"])!="full" or ast.literal_eval(decodekw["max_bs"])!=64 or ast.literal_eval(decodekw["bs"])!=list(range(1,65)): raise SystemExit("decode-0: decode graph must resolve full 1..64")
 if role=="decode-0":
  deterministic_marker="Disable --flashinfer-allreduce-fusion-backend because deterministic inference is enabled."
  enforced_marker="FlashInfer allreduce fusion is forcibly disabled via --enforce-disable-flashinfer-allreduce-fusion."
  enforced=kw.get("enforce_disable_flashinfer_allreduce_fusion")
  if enforced is not None and ast.literal_eval(enforced) is True:
   if enforced_marker not in text: raise SystemExit("decode-0: enforced allreduce disable lacks its native source marker")
  elif deterministic_marker not in text:
   raise SystemExit("decode-0: missing native deterministic or enforced MNNVL disable marker")
 if "Sampling backend is set to pytorch for deterministic inference." not in text: raise SystemExit(f"{role}: missing native deterministic sampling marker")
 if "NCCL_ALGO is set to 'allreduce:tree' and custom all reduce is disabled" not in text: raise SystemExit(f"{role}: missing native TP allreduce marker")
 kv=re.findall(r"TP(\d+)(?: EP\d+)?\] KV Cache is allocated\. dtype: torch\.([a-z0-9]+)",text)
 nixl=collections.Counter(re.findall(r"TP(\d+)(?: EP\d+)?\] NIXL KVManager initialized",text))
 if collections.Counter(r for r,d in kv)!=collections.Counter({str(i):2 for i in range(n)}) or {d for _,d in kv}!={"bfloat16"}: raise SystemExit(f"{role}: expected two BF16 EAGLE3 allocations on every TP rank")
 if nixl!=collections.Counter({str(i):1 for i in range(n)}): raise SystemExit(f"{role}: NIXL rank coverage mismatch")
 out[role]={"tp_ranks":n,"bf16_kv_records":len(kv),"bf16_allocations_per_rank":2,"nixl_rank_records":sum(nixl.values()),"sampling":"pytorch","global_attention":"fa3","deterministic":True}
print(json.dumps({"state":"PASS","roles":out,"scope":"source-shaped log checker; runtime evidence required from actual job; not GPU proof"},indent=2))
