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

ROOT = Path(__file__).resolve().parent

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
new=select_functions(ROOT/'nixl-ondemand/conn.py',{'_init_hetero_tp_prep_handle','send_kvcache_slice'},'NixlKVManager')

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
for heads in (4,8):
 for p in (2,4,8):
  for d in (2,4,8):
   if p==d:continue
   for page in (1,4,16):
    for pr in range(p):
     for dr in range(d):
      if p>d and not dr*(p//d)<=pr<(dr+1)*(p//d):continue
      if d>p and dr//(d//p)!=pr:continue
      a,b=manager(p,d,pr,page,heads),manager(p,d,pr,page,heads)
      dst=peer(d,dr,page,heads)
      old['_init_hetero_tp_prep_handle'](a,'peer',dst)
      new['_init_hetero_tp_prep_handle'](b,'peer',dst)
      for source_idx,target_idx in (([0,1,3,4,9],[2,3,7,8,13]),([15],[23]),([2,3,4],[5,6,7])):
       si,di=np.array(source_idx,dtype=np.int32),np.array(target_idx,dtype=np.int32)
       old['send_kvcache_slice'](a,'peer',si,di,'123_0_1_0')
       new['send_kvcache_slice'](b,'peer',si,di,'123_0_1_0')
       assert transfers(a.agent.sent)==transfers(b.agent.sent),(p,d,pr,dr,page,heads)
       cases+=1

# Full-scale pools must not allocate full-scale dlists. A contiguous 4000-token
# TP8->TP4 prompt should require one descriptor per K/V layer, i.e. 188.
m=manager(8,4,0,1,4,layers=94,src_slots=2_148_119)
dst=peer(4,0,1,4,layers=94);dst.dst_num_slots=1_531_197
t=time.monotonic();new['_init_hetero_tp_prep_handle'](m,'peer',dst)
new['send_kvcache_slice'](m,'peer',np.arange(4000,dtype=np.int32),np.arange(5000,9000,dtype=np.int32),'room')
assert m.agent.sent[0].shape==(188,3)
out={'passed':True,'range_equivalence_cases':cases,'full_scale_prompt_descriptors':188,
     'full_scale_cpu_geometry_seconds':time.monotonic()-t,'real_gpu_transport_validated':False}
(ROOT/'nixl-ondemand/geometry-test.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
