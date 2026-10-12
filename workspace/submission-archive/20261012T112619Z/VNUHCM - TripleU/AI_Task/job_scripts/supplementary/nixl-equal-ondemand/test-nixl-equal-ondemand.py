"""CPU equivalence of actual prepared and generic equal-TP transfer geometry."""
import ast
from collections import deque
import json
import logging
from pathlib import Path
import time
import types
import numpy as np

ROOT = Path(__file__).resolve().parent
if ROOT.name == 'nixl-equal-ondemand':
    ROOT = ROOT.parent
PATCH = ROOT/'nixl-equal-ondemand'

def extract(path, names, cls=None):
    tree=ast.parse(path.read_text())
    body=tree.body if cls is None else next(n.body for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
    funcs=[n for n in body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert len(funcs)==len(names)
    scope={'np':np,'logger':logging.getLogger('equal-test'),'deque':deque,
           '_nixl_device_id':lambda kind,gpu:gpu if kind=='VRAM' else 0}
    code=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]+funcs,type_ignores=[])
    exec(compile(ast.fix_missing_locations(code),str(path),'exec'),scope)
    return {name:scope[name] for name in names}

reference=Path('/tmp/apac42-equal-reference/sgl-workspace/sglang/python/sglang/srt/disaggregation')
common=Path('/tmp/apac42-repair-source/sgl-workspace/sglang/python/sglang/srt/disaggregation/common/conn.py')
# Preserve the exact upstream helper sources with the result.
for target,source in [('reference-utils.py',reference/'utils.py'),
                      ('reference-common-utils.py',reference/'common/utils.py'),
                      ('reference-common-conn.py',common)]:
    if not (PATCH/target).exists():
        (PATCH/target).write_bytes(source.read_bytes())
names={'_prepare_payload_xfer','_init_equal_tp_prep_handle','_prep_equal_tp_dlist','_send_kvcache_generic'}
old=extract(PATCH/'original-conn.py',names,'NixlKVManager')
new=extract(PATCH/'conn.py',names,'NixlKVManager')
helpers=extract(PATCH/'original-conn.py',{'repeat_indices_over_layers','_homogeneous_kv_mem_kind'})
helpers.update(extract(PATCH/'reference-utils.py',{'build_transfer_entry_pairs'}))
helpers.update(extract(PATCH/'reference-common-utils.py',{'group_concurrent_contiguous'}))
get_mha=extract(PATCH/'reference-common-conn.py',{'get_mha_kv_ptrs_with_pp'},'CommonKVManager')['get_mha_kv_ptrs_with_pp']
for functions in (old,new):
    for fn in functions.values():fn.__globals__.update(helpers)

class Agent:
    def prep_xfer_dlist(self,peer,array,kind):return array.copy()
    def make_prepped_xfer(self,op,src,si,dst,di,notif):
        self.sent=(src[si],dst[di],notif);return object()
    def get_xfer_descs(self,array,kind):return array.copy()
    def initialize_xfer(self,op,src,dst,peer,notif):
        self.sent=(src,dst,notif);return object()
    def transfer(self,handle):return 'DONE'

def make(functions,page,heads,rank,layers=3,slots=16):
    item=page*max(1,heads//8)*256
    ptrs=[10_000_000*(i+1) for i in range(layers*2)]
    m=types.SimpleNamespace(attn_tp_size=8,pp_size=1,is_mla_backend=False,
        is_hybrid_mla_backend=False,src_mem_kind='VRAM',agent=Agent(),prep_handles={},
        _num_slots_src=slots,decode_kv_args_table={})
    m.kv_args=types.SimpleNamespace(kv_item_lens=[item]*(2*layers),kv_data_ptrs=ptrs,
        kv_data_lens=[slots*item]*(2*layers),gpu_id=rank,kv_layer_ids=list(range(layers))*2,
        prefill_start_layer=0,page_size=page)
    for name,fn in functions.items():setattr(m,name,types.MethodType(fn,m))
    m.get_mha_kv_ptrs_with_pp=types.MethodType(get_mha,m)
    peer=types.SimpleNamespace(decode_tp_size=8,dst_kv_item_lens=[item]*(2*layers),
        dst_kv_ptrs=[1_000_000_000+10_000_000*i for i in range(2*layers)],
        dst_num_slots=24,gpu_id=rank,dst_kv_mem_kinds=['VRAM']*(2*layers),
        dst_kv_layer_ids=list(range(layers))*2,requires_dcp_relayout=False,agent_name='peer')
    m.decode_kv_args_table['peer']=peer
    return m,peer

def ranges(rows):
    src,dst,notification=rows
    assert src.shape==dst.shape
    result=[]
    for s,d in zip(src,dst):
        assert s[1]==d[1] and int(s[1])%256==0
        for offset in range(0,int(s[1]),256):
            result.append((int(s[0])+offset,int(d[0])+offset,256,int(s[2]),int(d[2])))
    return result,notification

def send(m,p,si,di):
    m._send_kvcache_generic('peer',m.kv_args.kv_data_ptrs,p.dst_kv_ptrs,
        m.kv_args.kv_item_lens,np.asarray(si,dtype=np.int32),np.asarray(di,dtype=np.int32),
        p.gpu_id,'123_0_1_0')

rng=np.random.default_rng(2026)
cases=0
for heads in (4,8,16):
 for page in (1,4,16):
  for rank in range(8):
   a,pa=make(old,page,heads,rank);b,pb=make(new,page,heads,rank)
   a._prepare_payload_xfer(pa);b._prepare_payload_xfer(pb)
   assert a.prep_handles and not b.prep_handles
   patterns=[([0,1,3,4,9],[2,3,7,8,13]),([15],[23]),([2,3,4],[5,6,7])]
   patterns += [(rng.choice(16,10,replace=False).tolist(),rng.choice(24,10,replace=False).tolist()) for _ in range(10)]
   for si,di in patterns:
    send(a,pa,si,di);send(b,pb,si,di)
    assert ranges(a.agent.sent)==ranges(b.agent.sent),(heads,page,rank,si,di)
    cases+=1

# Unsupported layouts continue to create the original prepared handles.
for scenario in ('tp4','pp2','mla','host','reordered-layers'):
    m,p=make(new,1,4,0)
    if scenario=='tp4':m.attn_tp_size=p.decode_tp_size=4
    if scenario=='pp2':m.pp_size=2
    if scenario=='mla':m.is_mla_backend=True
    if scenario=='host':p.dst_kv_mem_kinds=['DRAM']*6
    if scenario=='reordered-layers':p.dst_kv_layer_ids=[2,1,0]*2
    m._prepare_payload_xfer(p)
    assert m.prep_handles,scenario

m,p=make(new,1,4,0,layers=94,slots=2_148_119)
p.dst_num_slots=2_148_119
t=time.monotonic();m._prepare_payload_xfer(p)
send(m,p,np.arange(4000),np.arange(5000,9000))
assert not m.prep_handles and m.agent.sent[0].shape==(188,3)
output={'passed':True,'range_equivalence_cases':cases,'fallback_guard_cases':5,
        'full_scale_request_descriptors':188,'avoided_prepared_descriptors_per_side':2148119*188,
        'full_scale_cpu_seconds':time.monotonic()-t,'real_gpu_transport_validated':False}
(PATCH/'geometry-test.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
