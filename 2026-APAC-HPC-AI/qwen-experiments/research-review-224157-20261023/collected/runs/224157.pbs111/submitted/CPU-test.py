#!/usr/bin/env python3
"""AST-extracted native NIXL methods with recording arrays and sparse mock memory."""
import json, logging, sys, types
from pathlib import Path
from types import MethodType, SimpleNamespace
from typing import List, Tuple
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import native_probe as n
import cpu_eagle_layout as eagle_layout
from cpu_numpy import np as MiniNP, Array

class SparseMockAgent:
    def __init__(self,source_ptrs,dest_ptrs,source_aux,dest_aux):
        self.source_ptrs=source_ptrs; self.dest_ptrs=dest_ptrs
        self.source_aux=source_aux; self.dest_aux=dest_aux
        self.registrations=[]; self.xfer_calls=[]; self.dest_pages={}; self.aux_dest={}
        self.pending=None; self.fail_wrong_origin=True; self.expected_regions=190
    def register_memory(self,rows,kind):
        rows=list(rows); self.registrations.append((kind,rows))
        expected=190 if kind=="VRAM" else 10
        if kind=="VRAM" and len(rows)!=190: raise ValueError("mock rejects missing KV regions")
        if kind=="DRAM" and len(rows)!=10: raise ValueError("mock rejects missing auxiliary regions")
        for row in rows:
            if len(row)!=4 or int(row[1])<=0: raise ValueError("malformed registration row")
            if kind=="VRAM" and int(row[1])!=n.REGION_BYTES: raise ValueError("KV region length mismatch")
            if kind=="DRAM" and int(row[1]) not in n.AUX_LENGTHS: raise ValueError("auxiliary region length mismatch")
        return [f"registered-{kind}-{len(rows)}"]
    def get_xfer_descs(self,rows,kind):
        rows=rows.tolist() if hasattr(rows,"tolist") else list(rows)
        self.xfer_calls.append((kind,rows)); return rows
    def initialize_xfer(self,op,src,dst,peer,notification):
        if op!="WRITE" or peer!="cpu-peer": raise ValueError("bad native peer or operation")
        if notification not in (b"cpu-kv",b"cpu-aux"): raise ValueError("bad native notification")
        if len(src)!=len(dst): raise ValueError("source/destination descriptor count mismatch")
        self.pending=(src,dst,notification); return "mock-handle"
    def transfer(self,handle):
        if handle!="mock-handle" or self.pending is None: raise ValueError("missing native transfer")
        src_rows,dst_rows,notification=self.pending
        if notification==b"cpu-kv":
            if len(src_rows)!=len(dst_rows) or len(src_rows)!=self.expected_regions*2: raise ValueError("wrong selected KV descriptor count")
            for sr,dr in zip(src_rows,dst_rows):
                sp,sl,sd=map(int,sr); dp,dl,dd=map(int,dr)
                if sl!=256 or dl!=256 or sd!=0 or dd!=0: raise ValueError("unexpected KV descriptor width/device")
                si,so=self.find(sp,self.source_ptrs,n.REGION_BYTES)
                di,do=self.find(dp,self.dest_ptrs,n.REGION_BYTES)
                page=so//256
                if so%256 or do%256 or page not in n.SELECTED_SRC_PAGES: raise ValueError("wrong KV page byte offset")
                if self.fail_wrong_origin and si!=di: raise ValueError("source region origin does not match destination region")
                data=n.page_pattern(si,page)
                if self.dest_pages.get((di,do//256)) not in (None,bytes([0xA5])*256): raise ValueError("destination page overwritten unexpectedly")
                self.dest_pages[(di,do//256)]=data
        else:
            if len(src_rows)!=10 or len(dst_rows)!=10: raise ValueError("auxiliary transfer must cover exactly ten items")
            for i,(sr,dr) in enumerate(zip(src_rows,dst_rows)):
                sp,sl,sd=map(int,sr); dp,dl,dd=map(int,dr)
                if sl!=n.AUX_LENGTHS[i] or dl!=n.AUX_LENGTHS[i] or sd!=0 or dd!=0: raise ValueError("auxiliary whole-buffer item geometry mismatch")
                si,so=self.find(sp,self.source_aux_ptrs,n.AUX_LENGTHS[i]); di,do=self.find(dp,self.dest_aux_ptrs,n.AUX_LENGTHS[i])
                if si!=i or di!=i or so!=0 or do!=0: raise ValueError("auxiliary origin or offset mismatch")
                self.aux_dest[i]=bytes(self.source_aux[i])
        self.pending=None; return "IN PROGRESS"
    @staticmethod
    def find(addr,ptrs,lengths):
        if isinstance(lengths,int): lengths=[lengths]*len(ptrs)
        for i,(p,size) in enumerate(zip(ptrs,lengths)):
            if int(p)<=addr and addr<size+int(p): return i,addr-int(p)
        raise ValueError("descriptor outside registered region")
    def release_xfer_handle(self,h):
        if h!="mock-handle": raise ValueError("unknown handle")
    def check_xfer_state(self,h): return "DONE"


def make_manager(methods,src_ptrs,dst_ptrs,src_aux,dst_aux,agent):
    args=SimpleNamespace(kv_data_ptrs=list(src_ptrs),kv_data_lens=[n.REGION_BYTES]*190,
        kv_data_mem_kinds=["VRAM"]*190,kv_item_lens=[256]*190,page_size=1,gpu_id=0,
        engine_rank=0,total_kv_head_num=4,kv_head_num=1,prefill_start_layer=0,
        aux_data_ptrs=list(src_aux),aux_data_lens=list(n.AUX_LENGTHS),aux_item_lens=list(n.AUX_LENGTHS),
        state_data_ptrs=[],state_data_lens=[],kv_layer_ids=[])
    mgr=SimpleNamespace(kv_args=args,agent=agent,attn_tp_size=4,_ondemand_slice_plans={},
                       _expected_src_pointer_order=list(src_ptrs),_expected_dst_pointer_order=list(dst_ptrs))
    agent.source_aux_ptrs=list(src_aux); agent.dest_aux_ptrs=list(dst_aux)
    for name in ("register_buffer_to_engine","_init_hetero_tp_prep_handle","send_kvcache_slice","send_aux"):
        setattr(mgr,name,MethodType(methods[name],mgr))
    mgr.get_mha_kv_ptrs_with_pp=MethodType(methods["get_mha_kv_ptrs_with_pp"],mgr)
    mgr._probe_peer_name="cpu-peer"
    return mgr


def native_methods():
    common=HERE/"source/common-conn.py"; nixl=HERE/"nixl-conn.py"
    if n.desc.digest(nixl)!=n.desc.SOURCE_SHA or n.desc.digest(common)!=n.desc.COMMON_SHA:
        raise AssertionError("pinned native source hashes changed")
    staging_path=HERE/"staging_buffer.py"
    helper=n.desc.extract(staging_path,"compute_head_slice_params",globs={"Tuple":Tuple})
    chain=("sglang","sglang.srt","sglang.srt.disaggregation","sglang.srt.disaggregation.common")
    for name in chain:
        mod=sys.modules.setdefault(name,types.ModuleType(name)); mod.__path__=[]
    staging=types.ModuleType("sglang.srt.disaggregation.common.staging_buffer")
    staging.compute_head_slice_params=helper
    sys.modules[staging.__name__]=staging
    return n.source_methods(nixl,common,np_module=MiniNP)


def test_registration_native_geometry_and_send_methods():
    methods=native_methods()
    src=[0x100000000+i*(n.REGION_BYTES+4096) for i in range(190)]
    dst=[0x100000000000+i*(n.REGION_BYTES+4096) for i in range(190)]
    src_aux=[0x300000000000+i*0x100000 for i in range(10)]
    dst_aux=[0x400000000000+i*0x100000 for i in range(10)]
    source_aux=[n.aux_pattern(i,n.AUX_LENGTHS[i]) for i in range(10)]
    dest_aux=[bytes([0xA5])*w for w in n.AUX_LENGTHS]
    agent=SparseMockAgent(src,dst,source_aux,dest_aux)
    mgr=make_manager(methods,src,dst,src_aux,dst_aux,agent)
    mgr.kv_args.kv_data_ptrs=src; mgr.kv_args.kv_data_lens=[n.REGION_BYTES]*190
    mgr.kv_args.kv_data_mem_kinds=["VRAM"]*190; mgr.kv_args.kv_item_lens=[256]*190
    mgr.kv_args.aux_data_ptrs=src_aux; mgr.kv_args.aux_data_lens=list(n.AUX_LENGTHS)
    mgr.kv_args.aux_item_lens=list(n.AUX_LENGTHS)
    mgr.register_buffer_to_engine()
    assert [(k,len(rows)) for k,rows in agent.registrations]==[("VRAM",190),("DRAM",10)]
    assert [int(row[1]) for row in agent.registrations[0][1]]==[n.REGION_BYTES]*190
    assert [int(row[1]) for row in agent.registrations[1][1]]==list(n.AUX_LENGTHS)
    cases=(("94-to-94",94,94),("94-to-95",94,95),("95-to-95",95,95))
    for name,sl,dl in cases:
        mgr.kv_args.kv_data_ptrs=src[:2*sl]
        mgr.kv_args.kv_data_lens=[n.REGION_BYTES]*(2*sl)
        mgr.kv_args.kv_data_mem_kinds=["VRAM"]*(2*sl)
        mgr.kv_args.kv_item_lens=[256]*(2*sl)
        dst_info=SimpleNamespace(decode_tp_size=8,decode_tp_rank=0,dst_kv_item_len=256,
            dst_kv_ptrs=dst[:2*dl],dst_kv_item_lens=[256]*(2*dl),gpu_id=0,dst_num_slots=n.SLOTS)
        mgr._init_hetero_tp_prep_handle("cpu-peer",dst_info)
        plan=mgr._ondemand_slice_plans["cpu-peer"]
        if list(plan["src_ptrs"])!=src[:2*sl] or list(plan["dst_ptrs"])!=dst[:2*sl]:
            raise AssertionError(f"{name}: native selector changed flat region origins")
        if (plan["src_stride"],plan["dst_stride"],plan["length"])!=(256,256,256):
            raise AssertionError(f"{name}: malformed native item geometry")
        agent.dest_pages={}; agent.xfer_calls=[]; agent.expected_regions=2*sl
        h=mgr.send_kvcache_slice("cpu-peer",n.SELECTED_SRC_PAGES,n.SELECTED_DST_PAGES,b"cpu-kv".decode())
        agent.check_xfer_state(h)
        expected={(r,dp):n.page_pattern(r,sp) for r in range(2*sl)
                  for sp,dp in zip(n.SELECTED_SRC_PAGES,n.SELECTED_DST_PAGES)}
        if agent.dest_pages!=expected: raise AssertionError(f"{name}: independent page-origin bytes differ")
        if len(agent.xfer_calls)!=2 or len(agent.xfer_calls[0][1])!=2*sl*2:
            raise AssertionError(f"{name}: native descriptors omitted selected regions/pages")
    # One item per auxiliary buffer, using whole-buffer lengths and diagnostic slot zero.
    mgr.kv_args.aux_data_ptrs=src_aux; mgr.kv_args.aux_item_lens=list(n.AUX_LENGTHS)
    h=mgr.send_aux("cpu-peer",0,dst_aux,0,"cpu-aux")
    agent.check_xfer_state(h)
    if agent.aux_dest!=dict(enumerate(source_aux)): raise AssertionError("native send_aux bytes/origins differ")
    assert len(agent.xfer_calls[-2][1])==len(agent.xfer_calls[-1][1])==10


def test_reject_malformed_or_missing_geometry_and_wrong_origin():
    methods=native_methods(); src=[0x100000000+i*(n.REGION_BYTES+4096) for i in range(190)]
    dst=[0x100000000000+i*(n.REGION_BYTES+4096) for i in range(190)]
    src_aux=[0x300000000000+i*0x100000 for i in range(10)]; dst_aux=[0x400000000000+i*0x100000 for i in range(10)]
    # Registration method plus a strict independent contract rejects missing region and stride errors.
    a=SparseMockAgent(src,dst,[b""]*10,[b""]*10); mgr=make_manager(methods,src,dst,src_aux,dst_aux,a)
    mgr.kv_args.kv_data_ptrs=src[:-1]
    try: mgr.register_buffer_to_engine()
    except ValueError: pass
    else: raise AssertionError("missing 190th region was accepted")
    mgr=make_manager(methods,src,dst,src_aux,dst_aux,SparseMockAgent(src,dst,[b""]*10,[b""]*10))
    n.validate_geometry(mgr.kv_args)
    mgr.kv_args.kv_item_lens[188]=128
    try: n.validate_geometry(mgr.kv_args)
    except ValueError: pass
    else: raise AssertionError("malformed item stride escaped strict validator")
    # Reverse registration order; native selector must preserve flat order and the independent origin gate rejects it.
    mgr=make_manager(methods,list(reversed(src)),dst,src_aux,dst_aux,SparseMockAgent(src,dst,[b""]*10,[b""]*10))
    mgr.kv_args.kv_data_ptrs=list(reversed(src)); mgr.kv_args.kv_data_lens=[n.REGION_BYTES]*190
    mgr.kv_args.kv_data_mem_kinds=["VRAM"]*190; mgr.kv_args.kv_item_lens=[256]*190
    d=SimpleNamespace(decode_tp_size=8,decode_tp_rank=0,dst_kv_item_len=256,dst_kv_ptrs=dst,
                      dst_kv_item_lens=[256]*190,gpu_id=0,dst_num_slots=n.SLOTS)
    mgr._expected_src_pointer_order=src; mgr._expected_dst_pointer_order=dst
    try: n.init_case(mgr,"cpu-peer",dst)
    except RuntimeError: pass
    else: raise AssertionError("wrong source origin order passed independent expected mapping")
    # Invoke the unmodified send method with reversed regions; the sparse backend rejects wrong-origin bytes.
    mgr._init_hetero_tp_prep_handle("cpu-peer",d)
    try: mgr.send_kvcache_slice("cpu-peer",n.SELECTED_SRC_PAGES,n.SELECTED_DST_PAGES,"cpu-kv")
    except ValueError: pass
    else: raise AssertionError("wrong-origin selected page bytes were accepted")
    # A destination with only 189 entries must be rejected before native setup.
    mgr=make_manager(methods,src,dst,src_aux,dst_aux,SparseMockAgent(src,dst,[b""]*10,[b""]*10))
    mgr.kv_args.kv_data_ptrs=src; mgr.kv_args.kv_data_lens=[n.REGION_BYTES]*190
    mgr.kv_args.kv_data_mem_kinds=["VRAM"]*190; mgr.kv_args.kv_item_lens=[256]*190
    try: n.init_case(mgr,"cpu-peer",dst[:-1])
    except RuntimeError: pass
    else: raise AssertionError("malformed destination geometry was accepted")


def test_patterns_are_distinct_and_receipt_gate_rejects_incomplete():
    pages=n.expected_kv_page_hashes()
    assert len(pages)==380
    assert len({row["sha256"] for row in pages})==380, "selected region/page identities must all differ"
    assert all(n.page_pattern(r,p)[:4]==r.to_bytes(4,"little") and
               n.page_pattern(r,p)[4:12]==p.to_bytes(8,"little")
               for r in range(190) for p in n.SELECTED_SRC_PAGES)
    assert sum(n.AUX_LENGTHS)==sum(len(n.aux_pattern(i,w)) for i,w in enumerate(n.AUX_LENGTHS))
    assert n.check_art(Path("/nonexistent-production-span-result"))["status"]=="fail"


def test_actual_role_builders_and_source_selector_keep_production_order():
    both=eagle_layout.result["both_roles_have_eagle3"]
    assert both["source_pointer_count"]==both["destination_pointer_count"]==190
    assert both["selected_layer_count"]==95
    assert both["final_source_pointer_order_matches_expected_origin_order"] is True
    assert both["final_destination_pointer_order_matches_expected_origin_order"] is True
    assert both["final_source_pointer_order_equals_input"] is True
    assert both["final_destination_pointer_order_equals_input"] is True
    plain=eagle_layout.result["plain_prefill_to_eagle_decode"]
    assert plain["source_pointer_count"]==188 and plain["destination_pointer_count"]==190
    assert plain["selected_layer_count"]==94
    assert plain["final_destination_pointer_order_matches_expected_origin_order"] is True


def test_only_source_is_patterned_and_receiver_starts_cold():
    calls=[]
    original=n.fill_source_pages
    n.fill_source_pages=lambda torch,mgr:calls.append(mgr)
    try:
        source,destination=object(),object()
        n.initialize_role_patterns(0,None,source)
        n.initialize_role_patterns(1,None,destination)
        assert calls==[source], "receiver must retain KV and auxiliary sentinels"
        try:n.initialize_role_patterns(2,None,destination)
        except ValueError:pass
        else:raise AssertionError("invalid physical rank accepted")
    finally:n.fill_source_pages=original

    class Truth:
        def __init__(self,value):self.value=value
        def item(self):return self.value
    class View:
        def __init__(self,pages,lo,hi):self.pages=pages;self.lo=lo;self.hi=hi
        def detach(self):return self
        def cpu(self):return self
        def numpy(self):return self
        def tobytes(self):
            assert self.hi-self.lo==256
            return self.pages.get(self.lo//256,bytes([0xA5])*256)
        def __eq__(self,scalar):
            return Truth(all(all(b==scalar for b in value[max(0,self.lo-page*256):min(256,self.hi-page*256)])
                for page,value in self.pages.items() if page*256<self.hi and (page+1)*256>self.lo))
    class Tensor:
        def __init__(self,pages):self.pages=pages
        def __getitem__(self,sl):return View(self.pages,sl.start,sl.stop)
    torch=SimpleNamespace(all=lambda truth:truth)
    tensors=[Tensor({dp:n.page_pattern(r,sp) for sp,dp in zip(n.SELECTED_SRC_PAGES,n.SELECTED_DST_PAGES)}) for r in range(190)]
    mgr=SimpleNamespace(_production_kv_tensors=tensors)
    assert n.verify_destination(torch,mgr)["untouched_registered_bytes_gpu_scanned"]==n.TOTAL_KV_BYTES-190*512
    # Reproduce the rejected prefilled-receiver bug: source-only pages remain
    # dirty outside the destination writes, and the real verifier must fail.
    tensors[188].pages[n.SELECTED_SRC_PAGES[-1]]=n.page_pattern(188,n.SELECTED_SRC_PAGES[-1])
    try:n.verify_destination(torch,mgr)
    except RuntimeError:pass
    else:raise AssertionError("receiver prefill contamination escaped untouched-span scan")


def main():
    test_only_source_is_patterned_and_receiver_starts_cold()
    test_registration_native_geometry_and_send_methods()
    test_reject_malformed_or_missing_geometry_and_wrong_origin()
    test_patterns_are_distinct_and_receipt_gate_rejects_incomplete()
    test_actual_role_builders_and_source_selector_keep_production_order()
    print("PASS: AST-extracted role builders/selector, native registration, 94/94 + 94/95 + 95/95 pointer selection, KV slice writes, ten-item aux write, unique page identities, and failure gates")
if __name__=="__main__": main()
