#!/usr/bin/env python3
"""Fail closed on resolved H200 target/draft runtime, graph, BF16 KV, and NIXL evidence."""
import ast
import collections
import json
import re
import sys
from pathlib import Path

art=Path(sys.argv[1]); expected={'prefill-0':4,'prefill-1':4,'decode-0':8}; evidence={}
draft='/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09'
target='/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8'

def keywords(node, label):
    if not isinstance(node, ast.Call) or node.args:
        raise ValueError(f'{label}: expected keyword-only resolved call')
    names=[kw.arg for kw in node.keywords]
    if len(names)!=len(set(names)) or any(name is None for name in names):
        raise ValueError(f'{label}: duplicate or expanded keyword arguments')
    return {kw.arg:kw.value for kw in node.keywords}

def literal(mapping,name,label):
    if name not in mapping: raise ValueError(f'{label}: missing resolved field {name}')
    try: return ast.literal_eval(mapping[name])
    except (ValueError,TypeError) as error: raise ValueError(f'{label}: {name} is not a literal resolved value') from error

for role,n in expected.items():
    text=(art/f'{role}.log').read_text(errors='replace')
    if 'The server is fired up and ready to roll!' not in text: raise ValueError(f'{role}: missing native ready marker')
    kv=re.findall(r'TP(\d+)(?: EP\d+)?\] KV Cache is allocated\. dtype: torch\.([a-z0-9]+)',text)
    if collections.Counter(rank for rank,dtype in kv)!=collections.Counter({str(i):2 for i in range(n)}) or {dtype for _,dtype in kv}!={'bfloat16'}:
        raise ValueError(f'{role}: require two real BF16 target/draft KV allocation lines per rank')
    nixl=collections.Counter(re.findall(r'TP(\d+)(?: EP\d+)?\] NIXL KVManager initialized',text))
    if nixl!=collections.Counter({str(i):1 for i in range(n)}): raise ValueError(f'{role}: NIXL rank initialization mismatch')
    disabled=collections.Counter(re.findall(r"TP(\d+)(?: EP\d+)?\] Disable prefill CUDA graph because cuda_graph_config resolved prefill\.backend='disabled'",text))
    if disabled!=collections.Counter({str(i):2 for i in range(n)}): raise ValueError(f'{role}: resolved eager prefill backend missing for target/draft ranks')
    if re.search(r'Capture (?:target |draft )?prefill CUDA graph',text,re.I): raise ValueError(f'{role}: unsupported target/draft prefill graph capture observed')
    records=[line.split('server_args=',1)[1] for line in text.splitlines() if 'server_args=ServerArgs(' in line]
    if len(records)!=1: raise ValueError(f'{role}: expected exactly one resolved ServerArgs record, found {len(records)}')
    try: server_node=ast.parse(records[0],mode='eval').body
    except SyntaxError as error: raise ValueError(f'{role}: malformed resolved ServerArgs record') from error
    if not isinstance(server_node,ast.Call) or not isinstance(server_node.func,ast.Name) or server_node.func.id!='ServerArgs':
        raise ValueError(f'{role}: resolved call is not ServerArgs')
    args=keywords(server_node,f'{role}.ServerArgs')
    common={'model_path':target,'dtype':'bfloat16','context_length':8192,'mem_fraction_static':0.9,
      'disaggregation_transfer_backend':'nixl','disaggregation_mode':'prefill' if role.startswith('prefill') else 'decode',
      'kv_cache_dtype':'auto','trust_remote_code':True,'tp_size':4 if role.startswith('prefill') else 8,
      'ep_size':1 if role.startswith('prefill') else 8,'speculative_algorithm':'EAGLE3',
      'speculative_draft_model_path':draft,'speculative_num_steps':2,'speculative_eagle_topk':1,
      'speculative_num_draft_tokens':3,'speculative_draft_attention_backend':'flashinfer',
      'speculative_draft_model_quantization':None}
    if role.startswith('prefill'): common.update(chunked_prefill_size=8192,moe_runner_backend='deep_gemm')
    else: common.update(moe_runner_backend='hpc_ops',decode_attention_backend='flashinfer',flashinfer_allreduce_fusion_backend='mnnvl')
    for field,wanted in common.items():
        actual=literal(args,field,role)
        if actual!=wanted: raise ValueError(f'{role}: resolved {field}={actual!r}, expected {wanted!r}')
    graph_node=args.get('cuda_graph_config')
    graph=keywords(graph_node,f'{role}.cuda_graph_config')
    if set(graph)!={'decode','prefill'}: raise ValueError(f'{role}: incomplete decode/prefill graph configuration')
    decode_graph=keywords(graph['decode'],f'{role}.cuda_graph_config.decode')
    prefill_graph=keywords(graph['prefill'],f'{role}.cuda_graph_config.prefill')
    if literal(prefill_graph,'backend',role)!='disabled': raise ValueError(f'{role}: resolved prefill graph backend is not disabled')
    if role.startswith('prefill'):
        if literal(decode_graph,'backend',role)!='disabled': raise ValueError(f'{role}: target-only prefill worker unexpectedly enables decode graphs')
    else:
        if literal(decode_graph,'backend',role)!='full' or literal(decode_graph,'max_bs',role)!=64 or literal(decode_graph,'bs',role)!=list(range(1,65)):
            raise ValueError(f'{role}: dense decode CUDA graph sizes must resolve exactly to 1 through 64')
        for marker in ('Capture draft decode CUDA graph end','Capture draft extend CUDA graph end'):
            if marker not in text: raise ValueError(f'{role}: missing actual dense decode graph completion {marker}')
    evidence[role]={'ranks':n,'bf16_kv_allocation_records':len(kv),'nixl_rank_records':sum(nixl.values()),
      'prefill_eager_resolution_records':sum(disabled.values()),'resolved_server_args_records':len(records),
      'resolved_decode_graph_backend':literal(decode_graph,'backend',role),'resolved_decode_graph_batches':literal(decode_graph,'bs',role) if role=='decode-0' else 'not_applicable'}
print(json.dumps({'state':'PASS','roles':evidence,'scope':'Runtime readiness only; no output correctness or performance claim'},indent=2))
