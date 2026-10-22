#!/usr/bin/env python3
"""CPU-only tests for extracted native registration, geometry, and result gates."""
import json, logging, sys, tempfile, types
from pathlib import Path
from types import MethodType, SimpleNamespace
from typing import List, Tuple

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import native_probe as n


def test_native_register_and_aux_methods():
    nixl=HERE/"nixl-conn.py"
    assert n.desc.digest(nixl)==n.desc.SOURCE_SHA
    device=n.desc.extract(nixl,"_nixl_device_id")
    globs={"_nixl_device_id":device,"logger":logging.getLogger("native-cpu-test")}
    register=n.desc.extract(nixl,"register_buffer_to_engine","NixlKVManager",globs)
    send_aux=n.desc.extract(nixl,"send_aux","NixlKVManager")
    class Agent:
        def __init__(self): self.registrations=[]; self.desc_requests=[]
        def register_memory(self,rows,kind):
            self.registrations.append((kind,list(rows))); return [f"registered-{kind}-{len(self.registrations)}"]
        def get_xfer_descs(self,rows,kind):
            self.desc_requests.append((kind,list(rows))); return (kind,list(rows))
        def initialize_xfer(self,op,src,dst,peer,notif):
            assert op=="WRITE" and peer=="actual-peer-name" and notif==b"cpu-aux"; return "aux-handle"
        def transfer(self,h): assert h=="aux-handle"; return "IN PROGRESS"
    agent=Agent(); aux_ptrs=[0x900000+i*0x1000 for i in range(3)]
    args=SimpleNamespace(kv_data_ptrs=[0x100000+i*0x1000 for i in range(190)],
        kv_data_lens=[1024]*190,kv_data_mem_kinds=["VRAM"]*190,gpu_id=0,
        aux_data_ptrs=aux_ptrs,aux_data_lens=[64,128,256],aux_item_lens=[16,32,64],
        state_data_ptrs=[],state_data_lens=[])
    mgr=SimpleNamespace(kv_args=args,agent=agent); MethodType(register,mgr)()
    assert [(k,len(rows)) for k,rows in agent.registrations]==[("VRAM",190),("DRAM",3)]
    assert all(row[2]==0 for _,rows in agent.registrations for row in rows)
    assert [row[1] for row in agent.registrations[1][1]]==[64,128,256]
    mgr.send_aux=MethodType(send_aux,mgr)
    assert mgr.send_aux("actual-peer-name",1,[0xA00000,0xA01000,0xA02000],2,"cpu-aux")=="aux-handle"
    src=agent.desc_requests[0][1]; dst=agent.desc_requests[1][1]
    assert src==[(aux_ptrs[i]+w,w,0) for i,w in enumerate((16,32,64))]
    assert dst==[(0xA00000+i*0x1000+2*w,w,0) for i,w in enumerate((16,32,64))]


def test_configure_case_uses_case_local_layers():
    nixl=HERE/"nixl-conn.py"; common=HERE/"source/common-conn.py"; staging=HERE/"staging_buffer.py"
    try:
        import numpy as np
    except ImportError:
        class Array(list):
            def tolist(self): return list(self)
        np=types.SimpleNamespace(uint64=int,asarray=lambda value,dtype=None:Array(value))
    helper=n.desc.extract(staging,"compute_head_slice_params",globs={"Tuple":Tuple})
    common_get=n.desc.extract(common,"get_mha_kv_ptrs_with_pp","CommonKVManager",{"List":List,"Tuple":Tuple})
    init=n.desc.extract(nixl,"_init_hetero_tp_prep_handle","NixlKVManager",
        {"np":np,"logger":logging.getLogger("native-configure-test")})
    staging_mod=types.ModuleType("sglang.srt.disaggregation.common.staging_buffer")
    staging_mod.compute_head_slice_params=helper
    modules={name:types.ModuleType(name) for name in ("sglang","sglang.srt","sglang.srt.disaggregation","sglang.srt.disaggregation.common")}
    for mod in modules.values():mod.__path__=[]
    modules["sglang.srt.disaggregation.common.staging_buffer"]=staging_mod
    with __import__("unittest.mock",fromlist=["patch"]).patch.dict(sys.modules,modules):
        mgr=SimpleNamespace(kv_args=SimpleNamespace(engine_rank=0,kv_data_ptrs=[],kv_data_lens=[],
            kv_data_mem_kinds=[],kv_item_lens=[],page_size=1,total_kv_head_num=4,kv_head_num=1,
            prefill_start_layer=0,gpu_id=0),attn_tp_size=4,_probe_peer_name="peer")
        mgr._probe_all_kv_ptrs=[0x1000000+i*0x1000 for i in range(190)]
        mgr._probe_all_kv_lens=[1024]*190; mgr._probe_all_kv_mem_kinds=["VRAM"]*190
        mgr._probe_all_kv_item_lens=[256]*190; mgr._probe_all_dst_ptrs=[0x4000000+i*0x1000 for i in range(190)]
        mgr._probe_all_dst_item_lens=[256]*190; mgr._ondemand_slice_plans={}
        mgr.get_mha_kv_ptrs_with_pp=MethodType(common_get,mgr)
        mgr._init_hetero_tp_prep_handle=MethodType(init,mgr)
        dst=SimpleNamespace(decode_tp_size=8,decode_tp_rank=0,dst_kv_item_len=256,gpu_id=0)
        for case,sl,dl in n.CASES:
            plan=n.configure_case(mgr,dst,sl,dl)
            assert len(mgr.kv_args.kv_data_ptrs)==2*sl
            assert len(mgr.kv_args.kv_data_lens)==2*sl
            assert len(mgr.kv_args.kv_data_mem_kinds)==2*sl
            assert len(mgr.kv_args.kv_item_lens)==2*sl
            assert len(dst.dst_kv_ptrs)==2*dl and len(dst.dst_kv_item_lens)==2*dl
            assert len(plan["src_ptrs"])==len(plan["dst_ptrs"])==2*sl
            assert len(mgr._probe_all_kv_ptrs)==len(mgr._probe_all_dst_ptrs)==190


def valid_rank_receipt(rank):
    host=f"host-{rank}"; gpu=f"GPU-{rank}"; agent=f"agent-{rank}"; peer=f"agent-{1-rank}"
    identity={"runtime_source_sha256":n.desc.SOURCE_SHA,"nixl_api_sha256":n.desc.base.EXPECTED_NIXL_API_SHA256,
        "nixl_bindings_sha256":"b"*64,"torch_file_sha256":"c"*64,
        "nixl_api_path":"/p/api","nixl_bindings_path":"/p/bindings","torch_path":"/p/torch",
        "nixl_version":"1","torch_version":"2"}
    sources={"nixl_conn_sha256":n.desc.SOURCE_SHA,"common_conn_sha256":n.desc.COMMON_SHA,
        "staging_buffer_sha256":n.desc.STAGING_SHA,"compute_head_slice_params_sha256":"a"*64}
    cases=[]
    for i,(case,sl,dl) in enumerate(n.CASES):
        h=n.sha(n.expected_kv(i,sl))
        cases.append({"case":case,"src_layers":sl,"dst_layers":dl,
            "state":"DONE" if rank==0 else "verified","gpu_sha256":h,"expected_sha256":h})
    aux=n.sha(b"".join(n.expected_aux(w,0) for w in n.AUX_WIDTHS)); metadata=["0"*64,"1"*64]
    return {"schema":"nixl-native-registration-rank-v1","rank":rank,"status":"complete",
        "host":host,"gpu_uuid":gpu,"agent_name":agent,"peer_name":peer,
        "metadata_sha256":metadata[rank],"peer_metadata_sha256":metadata[1-rank],
        "runtime_identity":identity,"source_hashes":sources,
        "registration_groups":[{"mem_kind":"VRAM","count":190},{"mem_kind":"DRAM","count":3}],
        "cases":cases,"aux_state":"DONE" if rank==0 else "verified","aux_sha256":aux,"aux_expected_sha256":aux}


def write_valid_art(art):
    for rank in (0,1):(art/f"rank{rank}-result.json").write_text(json.dumps(valid_rank_receipt(rank)))
    (art/"result.json").write_text(json.dumps({"schema":"nixl-native-registration-v1","status":"complete",
        "rank_receipts":["rank0-result.json","rank1-result.json"]}))


def test_checker_requires_both_rank_receipts_and_registration_groups():
    with tempfile.TemporaryDirectory() as td:
        art=Path(td); write_valid_art(art); assert n.check(art)["status"]=="pass"
        (art/"rank1-result.json").unlink(); assert n.check(art)["status"]=="fail"
        write_valid_art(art); r=json.loads((art/"rank1-result.json").read_text()); r["registration_groups"][0]["count"]=189
        (art/"rank1-result.json").write_text(json.dumps(r)); assert n.check(art)["status"]=="fail"
        write_valid_art(art); r=json.loads((art/"rank0-result.json").read_text()); r["cases"][0]["gpu_sha256"]="f"*64
        (art/"rank0-result.json").write_text(json.dumps(r)); assert n.check(art)["status"]=="fail"
        write_valid_art(art); r=json.loads((art/"rank0-result.json").read_text()); r["peer_name"]="wrong-peer"
        (art/"rank0-result.json").write_text(json.dumps(r)); assert n.check(art)["status"]=="fail"


def test_patterns_and_layout():
    for ci,(_,layers,_) in enumerate(n.CASES):
        expected=n.expected_kv(ci,layers); assert len(expected)==190*4*256
        for region in range(190):
            for page in (1,3):
                off=(region*4+page)*256; assert expected[off:off+256]==bytes([0xA5])*256
        for region in range(2*layers,190):
            for page in range(4):
                off=(region*4+page)*256; assert expected[off:off+256]==bytes([0xA5])*256
    for width in n.AUX_WIDTHS:
        val=n.expected_aux(width,0); assert val[:width]==bytes([0xA5])*width and val[3*width:]==bytes([0xA5])*width


def main():
    test_native_register_and_aux_methods(); test_configure_case_uses_case_local_layers()
    test_checker_requires_both_rank_receipts_and_registration_groups(); test_patterns_and_layout()
    print("PASS: native registration/send_aux, per-case pointer counts, dual-rank semantic receipts, and sentinels")
if __name__=="__main__":main()
