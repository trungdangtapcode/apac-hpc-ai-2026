#!/usr/bin/env python3
"""Execute actual native registration/KV/aux methods against bounded CPU memory."""
import json,sys
from pathlib import Path
from types import MethodType,ModuleType,SimpleNamespace
from typing import Tuple
from unittest.mock import patch
import numpy as np
import native_probe as n

O=Path(__file__).resolve().parent
methods=n.methods_from_source(O/'nixl-conn.py',O/'source/common-conn.py')
staging=ModuleType('sglang.srt.disaggregation.common.staging_buffer')
staging.compute_head_slice_params=n.desc.extract(O/'staging_buffer.py','compute_head_slice_params',globs={'Tuple':Tuple})
srcptr=[0x1000000+i*0x2000 for i in range(190)];dstptr=[0x2000000+i*0x2000 for i in range(190)]
saux=[0x3000000+i*0x2000 for i in range(3)];daux=[0x4000000+i*0x2000 for i in range(3)]
memory={p:bytearray(1024) for p in srcptr+dstptr}
memory.update({p:bytearray(w*4) for pointers in (saux,daux) for p,w in zip(pointers,n.AUX_WIDTHS)})
class CPUBackend:
 def __init__(self):self.registrations=[];self.posted=0
 def register_memory(self,rows,kind):
  self.registrations.append((kind,len(rows)));return list(rows)
 def get_xfer_descs(self,rows,kind):return list(rows),kind
 def initialize_xfer(self,op,source,dest,peer,notification):
  assert op=='WRITE' and peer=='registered-native-peer' and source[1]==dest[1]
  assert len(source[0])==len(dest[0]);self.source=source;self.dest=dest;return 'cpu-handle'
 def transfer(self,handle):
  assert handle=='cpu-handle';self.posted+=1
  for source,dest in zip(self.source[0],self.dest[0]):
   sp,sn,sd=map(int,source);dp,dn,dd=map(int,dest);assert sn==dn and sd==dd==0
   sr=next((p for p,b in memory.items() if p<=sp and sp+sn<=p+len(b)),None)
   dr=next((p for p,b in memory.items() if p<=dp and dp+dn<=p+len(b)),None)
   assert sr is not None and dr is not None
   memory[dr][dp-dr:dp-dr+dn]=memory[sr][sp-sr:sp-sr+sn]
  return 'IN PROGRESS'
backend=CPUBackend()
args=SimpleNamespace(kv_data_ptrs=srcptr,kv_data_lens=[1024]*190,kv_data_mem_kinds=['VRAM']*190,kv_item_lens=[256]*190,
 page_size=1,gpu_id=0,engine_rank=0,total_kv_head_num=4,kv_head_num=1,prefill_start_layer=0,
 aux_data_ptrs=saux,aux_data_lens=[4*w for w in n.AUX_WIDTHS],aux_item_lens=list(n.AUX_WIDTHS),state_data_ptrs=[],state_data_lens=[])
mgr=SimpleNamespace(kv_args=args,agent=backend,attn_tp_size=4)
for name,method in methods.items():setattr(mgr,name,MethodType(method,mgr))
mgr.register_buffer_to_engine();assert backend.registrations==[('VRAM',190),('DRAM',3)]
mgr._probe_all_kv_ptrs=srcptr;mgr._probe_all_kv_lens=[1024]*190;mgr._probe_all_kv_mem_kinds=['VRAM']*190;mgr._probe_all_kv_item_lens=[256]*190
mgr._probe_all_dst_ptrs=dstptr;mgr._probe_all_dst_item_lens=[256]*190;mgr._probe_peer_name='registered-native-peer'
mgr.agent=n.CheckedAgent(backend,[(p,1024) for p in srcptr],[(p,1024) for p in dstptr],[(p,4*w) for p,w in zip(saux,n.AUX_WIDTHS)],[(p,4*w) for p,w in zip(daux,n.AUX_WIDTHS)])
dst=SimpleNamespace(decode_tp_size=8,decode_tp_rank=0,dst_kv_item_len=256,gpu_id=0)
rows=[]
for ci,(case,sl,dl) in enumerate(n.CASES):
 for ri,p in enumerate(srcptr):memory[p][:]=b''.join(n.pattern(ri,page,ci) for page in range(4))
 for p in dstptr:memory[p][:]=bytes([0xA5])*1024
 with patch.dict(sys.modules,{staging.__name__:staging}):plan=n.configure_case(mgr,dst,sl,dl)
 handle=mgr.send_kvcache_slice('registered-native-peer',n.SRC_PAGES,n.DST_PAGES,'cpu-kv')
 assert handle=='cpu-handle';actual=b''.join(bytes(memory[p]) for p in dstptr)
 assert actual==n.expected_kv(ci,sl)
 rows.append(dict(case=case,source_regions=len(args.kv_data_ptrs),destination_regions=len(dst.dst_kv_ptrs),actual_hash=n.sha(actual)))
for p,w in zip(saux,n.AUX_WIDTHS):
 memory[p][:]=bytes([0xA5])*(4*w);memory[p][w:2*w]=bytes((w+i*5)&255 for i in range(w))
for p,w in zip(daux,n.AUX_WIDTHS):memory[p][:]=bytes([0xA5])*(4*w)
mgr.send_aux('registered-native-peer',1,daux,2,'cpu-aux')
assert b''.join(memory[p] for p in daux)==b''.join(n.expected_aux(w,0) for w in n.AUX_WIDTHS)
assert backend.posted==4
print(json.dumps(dict(passed=True,numpy_version=np.__version__,python_version=sys.version,registration_groups=backend.registrations,kv_cases=rows,aux_buffers=3,native_write_calls=4,scope='Actual pinned Python methods with CPU memory backend only; no GPU/native NIXL backend or network'),indent=2))
