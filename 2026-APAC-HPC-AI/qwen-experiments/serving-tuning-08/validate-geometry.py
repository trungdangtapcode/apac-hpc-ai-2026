"""Compare byte ranges with the image's original prebuilt-descriptor algorithm.

CPU only: no torch, GPU, weights or live requests. Real NIXL/GPU validation is
still required; this proves descriptor geometry, not transport completion.
"""
import ast
import json
import logging
import sys
import time
import types
from pathlib import Path
import numpy as np

DIR = Path(__file__).resolve().parent
ROOT = DIR.parent

def select_functions(path, names, cls=None):
    tree=ast.parse(path.read_text())
    body=tree.body if cls is None else next(n.body for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
    funcs=[n for n in body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert len(funcs)==len(names)
    code=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]+funcs,type_ignores=[])
    scope={'np':np,'logger':logging.getLogger('geometry-test'),'_nixl_device_id':lambda kind,gpu:gpu}
    exec(compile(ast.fix_missing_locations(code),str(path),'exec'),scope)
    return {n:scope[n] for n in names}

staging=ROOT/'nixl-ondemand/head-slice-reference.py'
module=types.ModuleType('sglang.srt.disaggregation.common.staging_buffer')
module.compute_head_slice_params=select_functions(staging,{'compute_head_slice_params'})['compute_head_slice_params']
sys.modules[module.__name__]=module
oldfile=ROOT/'nixl-ondemand/original-conn.py'
old=select_functions(oldfile,{'_init_hetero_tp_prep_handle','send_kvcache_slice'},'NixlKVManager')
old['send_kvcache_slice'].__globals__.update(select_functions(oldfile,{'expand_page_indices_for_slice'}))
new=select_functions(DIR/'s8-rr-dpa8-deepep-n52/nixl-conn.py',{'_init_hetero_tp_prep_handle','send_kvcache_slice'},'NixlKVManager')

class Agent:
    def prep_xfer_dlist(self,peer,array,kind):return array.copy()
    def make_prepped_xfer(self,op,src,si,dst,di,notif):
        self.sent=(src[si],dst[di],notif);return object()
    def get_xfer_descs(self,array,kind):return array.copy()
    def initialize_xfer(self,op,src,dst,peer,notif):
        self.sent=(src,dst,notif);return object()
    def transfer(self,handle):return 'DONE'

def manager(p,d,rank,page,heads,layers=3,src_slots=16):
    item=page*max(1,heads//p)*256
    ptrs=[10_000_000*(i+1) for i in range(layers*2)]
    m=types.SimpleNamespace(attn_tp_size=p,agent=Agent(),prep_handle_slice_src=None,prep_handles_slice_dst={})
    m.kv_args=types.SimpleNamespace(page_size=page,total_kv_head_num=heads,kv_head_num=max(1,heads//p),
        engine_rank=rank,kv_item_lens=[item]*(layers*2),kv_data_lens=[src_slots*item]*(layers*2),
        kv_data_ptrs=ptrs,gpu_id=rank)
    m.get_mha_kv_ptrs_with_pp=lambda src,dst:(src[:layers],src[layers:],dst[:layers],dst[layers:],layers)
    return m

def peer(d,rank,page,heads,layers=3):
    return types.SimpleNamespace(decode_tp_size=d,decode_tp_rank=rank,dst_kv_item_len=page*max(1,heads//d)*256,
        dst_kv_ptrs=[1_000_000_000+10_000_000*i for i in range(layers*2)],dst_num_slots=24,gpu_id=rank)

def transfers(rows):
    src,dst,notif=rows
    assert src.shape==dst.shape
    result=[]
    for s,d in zip(src,dst):
        assert s[1]==d[1] and int(s[1])%256==0
        for offset in range(0,int(s[1]),256):
            result.append((int(s[0])+offset,int(d[0])+offset,256,int(s[2]),int(d[2])))
    return result,notif

cases=0
for dp_rank in range(8):
 for prefill_rank in range(4):
  for source_idx,target_idx in (([0,1,3,4,9],[2,3,7,8,13]),([15],[23]),([2,3,4],[5,6,7])):
   a=manager(4,1,prefill_rank,1,4);b=manager(4,1,prefill_rank,1,4)
   dst=peer(1,0,1,4);dst.gpu_id=dp_rank
   old['_init_hetero_tp_prep_handle'](a,'peer',dst)
   new['_init_hetero_tp_prep_handle'](b,'peer',dst)
   si,di=np.array(source_idx,dtype=np.int32),np.array(target_idx,dtype=np.int32)
   old['send_kvcache_slice'](a,'peer',si,di,'room')
   new['send_kvcache_slice'](b,'peer',si,di,'room')
   actual,notif=transfers(b.agent.sent)
   assert transfers(a.agent.sent)==(actual,notif)
   # Independent expected byte mapping: each P rank sends its one KV head
   # into the four-head destination on the selected physical DP GPU.
   expected=[]
   for src_ptr,dst_ptr in zip(a.kv_args.kv_data_ptrs,dst.dst_kv_ptrs):
    for src_slot,dst_slot in zip(source_idx,target_idx):
     expected.append((src_ptr+src_slot*256,dst_ptr+dst_slot*1024+prefill_rank*256,256,prefill_rank,dp_rank))
   assert sorted(actual)==sorted(expected),(dp_rank,prefill_rank,source_idx)
   cases+=1
report=dict(passed=True,physical_decode_dp_ranks=8,prefill_attention_tp=4,decode_attention_tp=1,
            reference_and_independent_mapping_cases=cases,real_gpu_transport_validated=False)
(DIR/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
