#!/usr/bin/env python3
"""Verify resolved fast-default H200 runtime state; this is not kernel-performance proof."""
import ast, collections, json, re, sys
from pathlib import Path

art=Path(sys.argv[1]); arm=sys.argv[2]
prefill_cap=int(sys.argv[3]) if len(sys.argv)>3 else 64
if arm not in ('control','candidate') or prefill_cap<1: raise SystemExit('usage: check-fast-runtime.py ART control|candidate [prefill-cap]')
roles={'prefill-0':4,'prefill-1':4,'decode-0':8}; evidence={}
cfg=json.loads((Path(__file__).resolve().parent/'config.json').read_text())
prefill_cap=cfg['prefill_max_running_requests']
model='/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8'
draft='/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09'
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
    args=kwmap(node,role)
    common={'model_path':model,'dtype':'bfloat16','context_length':8192,'mem_fraction_static':0.9,
      'disaggregation_mode':'prefill' if role.startswith('prefill') else 'decode','disaggregation_transfer_backend':'nixl',
      'trust_remote_code':True,'kv_cache_dtype':'auto','tp_size':4 if role.startswith('prefill') else 8,
      'ep_size':1 if role.startswith('prefill') else 8,'moe_dp_size':1,'max_running_requests':prefill_cap if role.startswith('prefill') else 256,
      'enable_deterministic_inference':False,'sampling_backend':'flashinfer','disable_custom_all_reduce':False,
      'attention_backend':'fa3'}
    if role.startswith('prefill'):
        common.update(chunked_prefill_size=cfg['prefill_chunked_prefill_size'],moe_runner_backend='deep_gemm',flashinfer_allreduce_fusion_backend='auto')
    else:
        common.update(moe_runner_backend='hpc_ops',decode_attention_backend='flashinfer',flashinfer_allreduce_fusion_backend='mnnvl')
    common.update(enable_dynamic_batch_tokenizer=cfg['prefill_dynamic_tokenizer'] if role.startswith('prefill') else False,
        dynamic_batch_tokenizer_batch_size=32,
        dynamic_batch_tokenizer_batch_timeout=cfg['prefill_tokenizer_batch_timeout'] if role.startswith('prefill') else 0.002,
        enable_tokenizer_batch_encode=False,skip_tokenizer_init=False)
    common['disaggregation_decode_polling_interval']=cfg['decode_transfer_polling_interval'] if role=='decode-0' else cfg['prefill_transfer_polling_interval']
    for key,wanted in common.items():
        got=lit(args,key,role)
        if got!=wanted: raise ValueError(f'{role}: {key}={got!r}, expected {wanted!r}')
    spec={'speculative_algorithm':'EAGLE3' if arm=='candidate' else None,
      'speculative_draft_model_path':draft if arm=='candidate' else None,
      'speculative_num_steps':2 if arm=='candidate' else None,
      'speculative_eagle_topk':1 if arm=='candidate' else None,
      'speculative_num_draft_tokens':3 if arm=='candidate' else None,
      'speculative_draft_attention_backend':'flashinfer' if arm=='candidate' else None,
      'speculative_draft_model_quantization':None}
    for key,wanted in spec.items():
        got=lit(args,key,role)
        if got!=wanted: raise ValueError(f'{role}: {key}={got!r}, expected {wanted!r}')
    graph=kwmap(args.get('cuda_graph_config'),role+'.cuda_graph_config')
    if set(graph)!={'decode','prefill'}: raise ValueError(f'{role}: incomplete graph config')
    pg=kwmap(graph['prefill'],role+'.prefill-graph'); dg=kwmap(graph['decode'],role+'.decode-graph')
    expected_pg=cfg['prefill_cuda_graph'] if role.startswith('prefill') else 'disabled'
    if lit(pg,'backend',role)!=expected_pg: raise ValueError(f'{role}: actual prefill graph differs from arm')
    if expected_pg=='breakable':
        starts=set(re.findall(r'TP(\d+)\] Capture target prefill CUDA graph begin\. backend=breakable',text))
        ends=set(re.findall(r'TP(\d+)\] Capture target prefill CUDA graph end\.',text))
        if starts!=set(map(str,range(nranks))) or ends!=starts: raise ValueError(f'{role}: breakable prefill capture incomplete')
    if role.startswith('prefill'):
        if lit(dg,'backend',role)!='disabled': raise ValueError(f'{role}: prefill worker decode graphs must be disabled')
    else:
        if lit(dg,'backend',role)!='full' or lit(dg,'max_bs',role)!=64 or lit(dg,'bs',role)!=list(range(1,65)):
            raise ValueError('decode-0: decode graph batches must resolve to full 1..64')
    expected_kv=1 if arm=='control' else 2
    kv=re.findall(r'TP(\d+)(?: EP(\d+))?\] KV Cache is allocated\. dtype: torch\.([a-z0-9]+), #tokens: ([1-9][0-9]*), K size: ([0-9]+(?:\.[0-9]+)?) GB, V size: ([0-9]+(?:\.[0-9]+)?) GB',text)
    expected=collections.Counter({str(i):expected_kv for i in range(nranks)})
    got=collections.Counter(x[0] for x in kv)
    if got!=expected or {x[2] for x in kv}!={'bfloat16'} or any(float(x[4])<=0 or float(x[5])<=0 for x in kv): raise ValueError(f'{role}: BF16 KV allocation rank/count mismatch: {dict(got)}')
    nixl=collections.Counter(re.findall(r'TP(\d+)(?: EP\d+)?\] NIXL KVManager initialized',text))
    if nixl!=collections.Counter({str(i):1 for i in range(nranks)}): raise ValueError(f'{role}: NIXL rank initialization mismatch')
    prefill_disabled=collections.Counter(re.findall(r"TP(\d+)(?: EP\d+)?\] Disable prefill CUDA graph because cuda_graph_config resolved prefill\.backend='disabled'",text))
    if expected_pg=='disabled':
        if prefill_disabled!=collections.Counter({str(i):expected_kv for i in range(nranks)}): raise ValueError(f'{role}: native target/draft prefill graph-disabled markers incomplete')
    elif prefill_disabled: raise ValueError(f'{role}: graph arm unexpectedly disabled capture')
    if role=='decode-0':
        mnnvl=set(re.findall(r'FlashInfer AllReduce Fusion enabled and workspace initialized: backend=mnnvl, rank=(\d+), world_size=8',text))
        if mnnvl!=set(map(str,range(nranks))): raise ValueError('decode-0: native MNNVL initialization missing ranks')
        graph_kind='target verify' if arm=='candidate' else 'target decode'
        captured=set(re.findall(r'TP(\d+) EP\d+\] Capture '+re.escape(graph_kind)+r' CUDA graph end\.',text))
        if captured!=set(map(str,range(nranks))): raise ValueError('decode-0: target decode graph completion missing ranks')
        if arm=='candidate' and ('Capture draft decode CUDA graph end' not in text or 'Capture draft extend CUDA graph end' not in text): raise ValueError('decode-0: native draft decode/extend graph completion marker missing')
    evidence[role]={'tp_ranks':nranks,'bf16_kv_records':len(kv),'expected_per_rank':expected_kv,
      'nixl_rank_records':sum(nixl.values()),'resolved_fast_defaults':{'deterministic':False,'sampling':'flashinfer','custom_allreduce_disabled':False,
      'mnnvl_fusion':'mnnvl' if role=='decode-0' else 'auto'},'prefill_graph':expected_pg,
      'decode_graph':'full 1..64' if role=='decode-0' else 'disabled','server_args_records':1,'decode_transfer_polling_interval':common['disaggregation_decode_polling_interval']}
print(json.dumps({'state':'PASS_FAST_RUNTIME','arm':arm,'prefill_cap':prefill_cap,'roles':evidence,
 'scope':'Resolved native arguments, rank-level BF16 KV/NIXL allocations, and startup graph/MNNVL markers only; not a kernel-performance or model-quality proof.'},indent=2))
