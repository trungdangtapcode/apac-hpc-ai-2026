#!/usr/bin/env python3
"""Bounded no-model native NIXL production-span registration and transfer pilot."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, logging, os, re, socket, sys, time, traceback, uuid
from pathlib import Path
from types import MethodType, SimpleNamespace
from typing import List, Tuple

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("production_span_descriptor", HERE / "descriptor-base.py")
if spec is None or spec.loader is None: raise RuntimeError("source descriptor helper unavailable")
desc = importlib.util.module_from_spec(spec); spec.loader.exec_module(desc)
REGIONS, PAGE_BYTES, PAGE_SIZE = 190, 256, 1
SLOTS = 297391
REGION_BYTES = SLOTS * PAGE_BYTES
TOTAL_KV_BYTES = REGIONS * REGION_BYTES
SELECTED_SRC_PAGES, SELECTED_DST_PAGES = (1, 297390), (0, 297389)
AUX_LENGTHS = (6144, 6144, 6144, 6144, 49152, 49152, 6144, 12288, 786432, 6144)
AUX_TOTAL = sum(AUX_LENGTHS)
TP_SOURCE, TP_DEST, LOCAL_KV_HEADS, TOTAL_KV_HEADS = 4, 8, 1, 4
T0_LIMIT_S = 570
KV_CASE = "native-eagle-flat-95-to-95"


def digest_bytes(value: bytes) -> str: return hashlib.sha256(value).hexdigest()
def sha_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()


def region_origin(i: int) -> str:
    if i < 94: return f"target.K[{i}]"
    if i < 188: return f"target.V[{i-94}]"
    return "draft.K[0]" if i == 188 else "draft.V[0]"


def page_pattern(region: int, source_page: int) -> bytes:
    # Explicit identity header prevents collisions among the 380 selected
    # (region, page) pairs; the body also varies by identity and byte offset.
    if not 0 <= region < REGIONS or not 0 <= source_page < SLOTS:
        raise ValueError("pattern identity outside production geometry")
    header=region.to_bytes(4,"little")+source_page.to_bytes(8,"little")
    seed=(region*37 + source_page*53 + 19) & 255
    body=bytes((seed + offset*29 + (offset >> 3)*7) & 255 for offset in range(PAGE_BYTES-len(header)))
    return header+body


def aux_pattern(index: int, length: int) -> bytes:
    seed=(index*41 + length*3 + 7) & 255
    return bytes((seed + i*17 + (i >> 5)*11) & 255 for i in range(length))


def expected_kv_page_hashes() -> list[dict]:
    return [{"region":r,"origin":region_origin(r),"source_page":sp,"destination_page":dp,
             "sha256":digest_bytes(page_pattern(r,sp))}
            for r in range(REGIONS) for sp,dp in zip(SELECTED_SRC_PAGES,SELECTED_DST_PAGES)]


def source_methods(nixl_path: Path, common_path: Path, np_module=None):
    if desc.digest(nixl_path) != desc.SOURCE_SHA: raise RuntimeError("pinned native NIXL source hash mismatch")
    if desc.digest(common_path) != desc.COMMON_SHA: raise RuntimeError("pinned common connection source hash mismatch")
    if np_module is None: import numpy as np
    else: np=np_module
    globs={"np":np,"List":List,"Tuple":Tuple,"logger":logging.getLogger("production-span-probe"),
           "_nixl_device_id":desc.extract(nixl_path,"_nixl_device_id")}
    return {
        "register_buffer_to_engine":desc.extract(nixl_path,"register_buffer_to_engine","NixlKVManager",globs),
        "_init_hetero_tp_prep_handle":desc.extract(nixl_path,"_init_hetero_tp_prep_handle","NixlKVManager",globs),
        "send_kvcache_slice":desc.extract(nixl_path,"send_kvcache_slice","NixlKVManager",globs),
        "send_aux":desc.extract(nixl_path,"send_aux","NixlKVManager",globs),
        "get_mha_kv_ptrs_with_pp":desc.extract(common_path,"get_mha_kv_ptrs_with_pp","CommonKVManager",{"List":List,"Tuple":Tuple}),
    }


def runtime_source_methods():
    nixl=Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py")
    common=Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/common/conn.py")
    staging=Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/common/staging_buffer.py")
    if desc.digest(staging) != desc.STAGING_SHA: raise RuntimeError("pinned staging helper source hash mismatch")
    identity=desc.base._source_identity()
    methods=source_methods(nixl,common)
    hashes={"nixl_conn_sha256":desc.digest(nixl),"common_conn_sha256":desc.digest(common),
            "staging_buffer_sha256":desc.digest(staging),"nixl_api_sha256":identity["nixl_api_sha256"]}
    return methods,identity,hashes


def rss_kib() -> int | None:
    try:
        for line in Path("/proc/self/status").read_text().splitlines():
            if line.startswith("VmRSS:"): return int(line.split()[1])
    except OSError: pass
    return None


class Phases:
    def __init__(self, torch, t0): self.torch=torch; self.t0=t0; self.rows=[]
    def sample(self):
        free,total=self.torch.cuda.mem_get_info()
        return {"elapsed_from_component_t0_s":round(time.time()-self.t0,3),"rss_kib":rss_kib(),
                "gpu_free_bytes":int(free),"gpu_total_bytes":int(total),
                "gpu_allocated_bytes":int(self.torch.cuda.memory_allocated()),
                "gpu_reserved_bytes":int(self.torch.cuda.memory_reserved())}
    def start(self,name): return {"name":name,"start":self.sample()}
    def finish(self,row):
        end=self.sample(); row["end"]=end
        row["duration_s"]=round(end["elapsed_from_component_t0_s"]-row["start"]["elapsed_from_component_t0_s"],3)
        self.rows.append(row)
    def mark(self,name,fn):
        row=self.start(name)
        try: return fn()
        finally: self.finish(row)


def wait_done(agent, handle, deadline):
    while time.time() < deadline:
        state=agent.check_xfer_state(handle)
        if state=="DONE": return
        if state=="ERR": raise RuntimeError("native NIXL transfer entered ERR")
        time.sleep(.002)
    raise TimeoutError("native NIXL transfer exceeded component-relative deadline")


def wait_marker(path: Path, private: Path, deadline: float, what: str):
    error0=private/"error-rank0.json"; error1=private/"error-rank1.json"
    def ready():
        for err in (error0,error1):
            if err.exists(): raise RuntimeError(f"peer failed while waiting for {what}")
        return path.exists()
    desc.base.wait_until(ready,deadline,what)


def active_gpu_and_ib(torch):
    if not torch.cuda.is_available() or torch.cuda.device_count()!=1:
        raise RuntimeError("require exactly one visible CUDA GPU per physical-rank process")
    torch.cuda.set_device(0)
    prop=torch.cuda.get_device_properties(0); gpu_uuid=str(getattr(prop,"uuid",""))
    if not gpu_uuid: raise RuntimeError("CUDA device UUID unavailable")
    ib=desc.base.active_ib_devices()
    if not ib or os.environ.get("UCX_NET_DEVICES") != ",".join(ib):
        raise RuntimeError("UCX_NET_DEVICES must match active IB autodetection")
    if os.environ.get("UCX_POSIX_USE_PROC_LINK")!="n": raise RuntimeError("UCX_POSIX_USE_PROC_LINK must be n")
    return gpu_uuid,ib


def init_buffers_and_manager(torch, agent, rank, methods, phases):
    free,total=torch.cuda.mem_get_info()
    min_free=TOTAL_KV_BYTES + 3*(1<<30)
    if int(free)<min_free:
        raise RuntimeError(f"insufficient preallocation GPU free memory: need {min_free} bytes, have {int(free)}")
    def allocate():
        kv=[torch.empty(REGION_BYTES,dtype=torch.uint8,device="cuda:0") for _ in range(REGIONS)]
        for t in kv: t.fill_(0xA5)
        aux=[torch.empty(n,dtype=torch.uint8,pin_memory=True) for n in AUX_LENGTHS]
        for t in aux: t.fill_(0xA5)
        torch.cuda.synchronize()
        return kv,aux
    kv_tensors,aux_tensors=phases.mark("allocation_and_sentinel_initialization",allocate)
    pointers=[int(t.data_ptr()) for t in kv_tensors]
    aux_ptrs=[int(t.data_ptr()) for t in aux_tensors]
    args=SimpleNamespace(kv_data_ptrs=list(pointers),kv_data_lens=[REGION_BYTES]*REGIONS,
        kv_data_mem_kinds=["VRAM"]*REGIONS,kv_item_lens=[PAGE_BYTES]*REGIONS,
        page_size=PAGE_SIZE,gpu_id=0,engine_rank=0,total_kv_head_num=TOTAL_KV_HEADS,
        kv_head_num=LOCAL_KV_HEADS,prefill_start_layer=0,pp_rank=0,
        kv_layer_ids=[],aux_data_ptrs=aux_ptrs,aux_data_lens=list(AUX_LENGTHS),
        aux_item_lens=list(AUX_LENGTHS),state_data_ptrs=[],state_data_lens=[])
    audit=RegistrationAudit(agent)
    mgr=SimpleNamespace(kv_args=args,agent=audit,attn_tp_size=TP_SOURCE)
    for name in ("register_buffer_to_engine","_init_hetero_tp_prep_handle","send_kvcache_slice","send_aux"):
        setattr(mgr,name,MethodType(methods[name],mgr))
    validate_geometry(args)
    phases.mark("native_register_buffer_to_engine",mgr.register_buffer_to_engine)
    expected=[("VRAM",REGIONS),("DRAM",len(AUX_LENGTHS))]
    if audit.calls!=expected: raise RuntimeError(f"native registration groups mismatch: {audit.calls}")
    mgr.agent=agent
    mgr.get_mha_kv_ptrs_with_pp=MethodType(methods["get_mha_kv_ptrs_with_pp"],mgr)
    mgr._production_kv_tensors=kv_tensors; mgr._production_aux_tensors=aux_tensors
    mgr._production_kv_ranges=[(int(t.data_ptr()),int(t.numel())) for t in kv_tensors]
    mgr._production_aux_ranges=[(int(t.data_ptr()),int(t.numel())) for t in aux_tensors]
    mgr._production_registration_groups=[{"mem_kind":k,"count":c} for k,c in audit.calls]
    return mgr


class RegistrationAudit:
    def __init__(self,agent): self.agent=agent; self.calls=[]
    def __getattr__(self,name): return getattr(self.agent,name)
    def register_memory(self,rows,kind):
        self.calls.append((kind,len(rows)))
        return self.agent.register_memory(rows,kind)


class CheckedAgent:
    """Retain native NIXL methods while checking every descriptor against registered spans."""
    def __init__(self,agent,local_kv,remote_kv,local_aux,remote_aux):
        self.agent=agent; self.calls=0
        self.bounds={"VRAM":(local_kv,remote_kv),"DRAM":(local_aux,remote_aux)}
    def __getattr__(self,name): return getattr(self.agent,name)
    def get_xfer_descs(self,rows,kind):
        source=self.calls%2==0; self.calls+=1
        bounds=self.bounds[kind][0 if source else 1]
        for row in rows:
            addr,length=int(row[0]),int(row[1])
            if length<=0 or not any(addr>=p and addr+length<=p+n for p,n in bounds):
                raise RuntimeError(f"native {kind} descriptor escaped registered source/destination spans")
        return self.agent.get_xfer_descs(rows,kind)


def validate_geometry(args):
    if len(args.kv_data_ptrs)!=REGIONS or len(args.kv_data_lens)!=REGIONS or len(args.kv_item_lens)!=REGIONS or len(args.kv_data_mem_kinds)!=REGIONS:
        raise ValueError("expected exactly 190 KV pointers, lengths, item sizes, and memory kinds")
    if args.kv_data_lens!=[REGION_BYTES]*REGIONS or args.kv_item_lens!=[PAGE_BYTES]*REGIONS or args.kv_data_mem_kinds!=["VRAM"]*REGIONS:
        raise ValueError("KV region span/item/memory-kind geometry mismatch")
    if args.page_size!=1 or args.total_kv_head_num!=TOTAL_KV_HEADS or args.kv_head_num!=LOCAL_KV_HEADS:
        raise ValueError("TP/head/page geometry differs from source-backed pilot contract")
    if args.kv_layer_ids not in ([],None): raise ValueError("pilot requires observed-empty positional KV layer metadata")
    if len(args.aux_data_ptrs)!=10 or args.aux_data_lens!=list(AUX_LENGTHS) or args.aux_item_lens!=list(AUX_LENGTHS):
        raise ValueError("ten auxiliary buffer lengths/item sizes mismatch")
    if args.state_data_ptrs not in ([],None) or args.state_data_lens not in ([],None):
        raise ValueError("no state regions are in scope for this MHA pilot")


def init_case(mgr, peer_name, dst_ptrs):
    args=mgr.kv_args
    if len(args.kv_data_ptrs)!=REGIONS or len(dst_ptrs)!=REGIONS: raise RuntimeError("95→95 requires 190 pointer entries per side")
    dst=SimpleNamespace(decode_tp_size=TP_DEST,decode_tp_rank=0,dst_kv_item_len=PAGE_BYTES,
                        dst_kv_ptrs=list(dst_ptrs),dst_kv_item_lens=[PAGE_BYTES]*REGIONS,
                        gpu_id=0,dst_num_slots=SLOTS)
    mgr._init_hetero_tp_prep_handle(peer_name,dst)
    plan=mgr._ondemand_slice_plans[peer_name]
    src_order=list(plan["src_ptrs"]); dst_order=list(plan["dst_ptrs"])
    expected_src=list(getattr(mgr,"_expected_src_pointer_order",args.kv_data_ptrs))
    expected_dst=list(getattr(mgr,"_expected_dst_pointer_order",dst_ptrs))
    if src_order!=expected_src or dst_order!=expected_dst:
        raise RuntimeError("native 95→95 selector did not preserve independently expected flat registration order")
    if (plan["src_stride"],plan["dst_stride"],plan["length"],plan["src_offset"],plan["dst_offset"]) != (256,256,256,0,0):
        raise RuntimeError("native 95→95 transfer plan differs from actual 256-byte item geometry")
    return dst,plan


def fill_source_pages(torch,mgr):
    for t in mgr._production_kv_tensors: t.fill_(0xA5)
    for region,t in enumerate(mgr._production_kv_tensors):
        for page in SELECTED_SRC_PAGES:
            start=page*PAGE_BYTES
            pat=torch.tensor(list(page_pattern(region,page)),dtype=torch.uint8,device="cuda:0")
            t[start:start+PAGE_BYTES].copy_(pat)
    for i,t in enumerate(mgr._production_aux_tensors):
        pat=torch.tensor(list(aux_pattern(i,AUX_LENGTHS[i])),dtype=torch.uint8)
        t.copy_(pat)
    torch.cuda.synchronize()


def initialize_role_patterns(rank, torch, mgr):
    if rank == 0:
        fill_source_pages(torch, mgr)
    elif rank != 1:
        raise ValueError("physical rank must be zero or one")
    # Rank one retains allocation-time sentinels in KV and auxiliary buffers.
    # Pre-filling its expected payload would hide failed writes and corrupt the
    # untouched-span baseline when source and destination page indices differ.


def verify_destination(torch,mgr, target_pages=SELECTED_DST_PAGES):
    page_hashes=[]; untouched=0
    for region,t in enumerate(mgr._production_kv_tensors):
        for sp,dp in zip(SELECTED_SRC_PAGES,target_pages):
            start=dp*PAGE_BYTES; got=t[start:start+PAGE_BYTES].detach().cpu().numpy().tobytes()
            expected=page_pattern(region,sp)
            if got!=expected: raise RuntimeError(f"KV selected page mismatch at region {region}, source page {sp}")
            page_hashes.append({"region":region,"origin":region_origin(region),"source_page":sp,
                                "destination_page":dp,"sha256":digest_bytes(got)})
        # GPU reductions scan every destination byte outside the two expected page writes.
        segments=((0,target_pages[0]*PAGE_BYTES),
                  ((target_pages[0]+1)*PAGE_BYTES,target_pages[1]*PAGE_BYTES),
                  ((target_pages[1]+1)*PAGE_BYTES,REGION_BYTES))
        for lo,hi in segments:
            if hi>lo and not bool(torch.all(t[lo:hi]==0xA5).item()):
                raise RuntimeError(f"untouched GPU bytes changed in registered region {region}")
            untouched+=max(0,hi-lo)
    return {"state":"verified","regions_checked":REGIONS,"selected_pages_checked":len(page_hashes),
            "selected_page_bytes_checked":len(page_hashes)*PAGE_BYTES,
            "untouched_registered_bytes_gpu_scanned":untouched,
            "selected_page_sha256":page_hashes}


def verify_auxiliary(mgr):
    rows=[]; combined=bytearray()
    for i,t in enumerate(mgr._production_aux_tensors):
        actual=t.detach().numpy().tobytes(); expected=aux_pattern(i,AUX_LENGTHS[i])
        if actual!=expected: raise RuntimeError(f"auxiliary full-span mismatch at item {i}")
        h=digest_bytes(actual); rows.append({"index":i,"length_bytes":len(actual),"sha256":h}); combined.extend(actual)
    return {"state":"verified","buffer_count":len(rows),"total_bytes":len(combined),
            "item_sha256":rows,"combined_sha256":digest_bytes(bytes(combined)),
            "item_stride_interpretation":"one whole-buffer item per registered auxiliary region; not a native request-slot layout"}


def safe_error(exc):
    message=re.sub(r"0x[0-9a-fA-F]{6,}","<address>",str(exc))[:700]
    return {"type":type(exc).__name__,"message":message,
            "frames":[{"file":f.filename,"line":f.lineno,"function":f.name} for f in traceback.extract_tb(exc.__traceback__)[-6:]]}


def public_rank_result(rank,host,gpu_uuid,agent_name,peer_name,metadata,peer_metadata,identity,source_hashes,
                       groups,geometry,kv_receipt,aux_receipt,phases,elapsed):
    return {"schema":"nixl-production-span-rank-v1","rank":rank,"status":"complete",
        "host":host,"gpu_uuid":gpu_uuid,"agent_name":agent_name,"peer_name":peer_name,
        "metadata_sha256":digest_bytes(metadata),"peer_metadata_sha256":digest_bytes(peer_metadata),
        "runtime_identity":identity,"source_hashes":source_hashes,"registration_groups":groups,
        "geometry":geometry,"kv_transfer":kv_receipt,"aux_transfer":aux_receipt,
        "phase_samples":phases,"elapsed_from_component_t0_s":round(elapsed,3)}


def geometry_receipt(rank):
    return {"physical_pair_size":2,"physical_rank":rank,"one_gpu_per_distinct_node_required":True,
        "role":"prefill-source" if rank==0 else "decode-destination","mapped_source_tp_size":TP_SOURCE,
        "mapped_destination_tp_size":TP_DEST,"mapped_engine_rank":0,"mapped_decode_tp_rank":0,
        "this_is_not_a_full_tp_collective":True,"target_mha_layers":94,"draft_mha_layers":1,
        "registration_order_origins":{"regions_0_93":"target.K[0..93]","regions_94_187":"target.V[0..93]",
                                       "region_188":"draft.K[0]","region_189":"draft.V[0]"},
        "kv_regions":REGIONS,"bytes_per_region":REGION_BYTES,"total_advertised_bytes":TOTAL_KV_BYTES,
        "item_bytes_per_slot":PAGE_BYTES,"page_size_tokens":PAGE_SIZE,"slot_count":SLOTS,
        "local_kv_heads":LOCAL_KV_HEADS,"total_kv_heads":TOTAL_KV_HEADS,"pp_rank":0,
        "kv_layer_ids_observed_by_this_fixture":[],"kv_layer_ids_interpretation":"positional region order is exercised; semantic layer IDs are not invented",
        "auxiliary_region_lengths_bytes":list(AUX_LENGTHS),"auxiliary_item_lengths_bytes":list(AUX_LENGTHS),
        "auxiliary_slot_interpretation":"one diagnostic whole-buffer item per region, slot zero only; not native request strides",
        "state_regions":0}


def rank_run(rank:int,art:Path,exchange:Path):
    import torch
    from nixl._api import nixl_agent,nixl_agent_config,nixl_thread_sync_t
    t0_record=json.loads((exchange/"component-start.json").read_text())
    t0=float(t0_record["t0_epoch_s"]); deadline=t0+T0_LIMIT_S
    phases=Phases(torch,t0); agent=None; mgr=None
    try:
        gpu_uuid,ib=phases.mark("device_and_active_ib_check",lambda:active_gpu_and_ib(torch))
        methods,identity,source_hashes=phases.mark("source_hash_and_runtime_identity",runtime_source_methods)
        private=exchange/".production-span-private"
        private.mkdir(mode=0o700,parents=True,exist_ok=True); os.chmod(private,0o700)
        def initialize_agent():
            cfg=nixl_agent_config(backends=[],num_threads=8,sync_mode=nixl_thread_sync_t.NIXL_THREAD_SYNC_STRICT)
            created=nixl_agent(f"prod-span-{rank}-{uuid.uuid4()}",cfg)
            created.create_backend("UCX",{"num_threads":"8"})
            return created
        agent=phases.mark("nixl_agent_initialization",initialize_agent)
        mgr=init_buffers_and_manager(torch,agent,rank,methods,phases)
        kv_ptrs=list(mgr.kv_args.kv_data_ptrs); aux_ptrs=list(mgr.kv_args.aux_data_ptrs)
        metadata=agent.get_agent_metadata()
        (private/f"agent-{rank}.bin").write_bytes(metadata)
        local={"rank":rank,"host":socket.gethostname(),"gpu_uuid":gpu_uuid,"agent_name":agent.name,
               "metadata_sha256":digest_bytes(metadata),"metadata_len":len(metadata),
               "kv_ptrs":kv_ptrs,"region_origins":[region_origin(i) for i in range(REGIONS)],"kv_ranges":mgr._production_kv_ranges,
               "aux_ptrs":aux_ptrs,"aux_ranges":mgr._production_aux_ranges,
               "registration_groups":mgr._production_registration_groups}
        desc.base.atomic_json(private/f"rank-{rank}.json",local)
        peer_path=private/f"rank-{1-rank}.json"
        wait_marker(peer_path,private,deadline,"peer registration record")
        peer=json.loads(peer_path.read_text());
        if peer.get("region_origins") != [region_origin(i) for i in range(REGIONS)]: raise RuntimeError("private peer pointer-origin labels differ")
        peer_metadata=(private/f"agent-{1-rank}.bin").read_bytes()
        if len(peer_metadata)!=peer["metadata_len"] or digest_bytes(peer_metadata)!=peer["metadata_sha256"]:
            raise RuntimeError("private peer metadata hash mismatch")
        phases.mark("remote_agent_exchange",lambda:agent.add_remote_agent(peer_metadata))
        ready={"rank":rank,"host":socket.gethostname(),"gpu_uuid":gpu_uuid,"agent_name":agent.name,
               "metadata_sha256":digest_bytes(metadata),"runtime_identity":identity,"source_hashes":source_hashes,
               "ib_devices":ib}
        desc.base.atomic_json(private/f"ready-{rank}.json",ready)
        wait_marker(private/"ready-1.json",private,deadline,"rank1 ready")
        wait_marker(private/"ready-0.json",private,deadline,"rank0 ready")
        peers=[json.loads((private/f"ready-{i}.json").read_text()) for i in (0,1)]
        if peers[0]["host"]==peers[1]["host"] or peers[0]["gpu_uuid"]==peers[1]["gpu_uuid"]:
            raise RuntimeError("pilot requires two distinct physical hosts and GPU UUIDs")
        if peers[0]["source_hashes"]!=peers[1]["source_hashes"] or peers[0]["runtime_identity"]!=peers[1]["runtime_identity"]:
            raise RuntimeError("rank source/runtime identities differ")
        peer_name=peer["agent_name"]
        if peer_name!=peers[1-rank]["agent_name"]: raise RuntimeError("peer identity mismatch")
        checked=CheckedAgent(agent,mgr._production_kv_ranges,peer["kv_ranges"],
                             mgr._production_aux_ranges,peer["aux_ranges"])
        mgr.agent=checked
        phases.mark("source_and_auxiliary_pattern_initialization",lambda:initialize_role_patterns(rank,torch,mgr))
        kv_receipt={"case":KV_CASE,"source_layers":95,"destination_layers":95,
            "native_methods":["_init_hetero_tp_prep_handle","send_kvcache_slice"],
            "source_pages":list(SELECTED_SRC_PAGES),"destination_pages":list(SELECTED_DST_PAGES),
            "region_count":REGIONS,"bytes_per_region":REGION_BYTES,
            "selected_payload_bytes":REGIONS*len(SELECTED_SRC_PAGES)*PAGE_BYTES}
        if rank==0:
            def prepare():
                mgr._probe_peer_name=peer_name
                mgr._expected_dst_pointer_order=list(peer["kv_ptrs"])
                dst,plan=init_case(mgr,peer_name,peer["kv_ptrs"])
                return dst,plan
            dst,plan=phases.mark("native_95_to_95_transfer_plan",prepare)
            if len(plan["src_ptrs"])!=REGIONS or len(plan["dst_ptrs"])!=REGIONS:
                raise RuntimeError("native plan does not include every target and draft region")
            wait_marker(private/"receiver-kv-ready.json",private,deadline,"receiver KV readiness")
            def send_kv():
                handle=mgr.send_kvcache_slice(peer_name,SELECTED_SRC_PAGES,SELECTED_DST_PAGES,"production-span-kv")
                wait_done(agent,handle,deadline)
                agent.release_xfer_handle(handle)
            phases.mark("native_full_span_kv_send",send_kv)
            desc.base.atomic_json(private/"kv-done.json",{"state":"DONE","case":KV_CASE})
            wait_marker(private/"kv-verified.json",private,deadline,"full-span GPU verification")
            kv_receipt.update({"state":"DONE","native_dlist_entries":REGIONS*len(SELECTED_SRC_PAGES),
                               "receiver_verification":json.loads((private/"kv-verified.json").read_text())})
            wait_marker(private/"aux-ready.json",private,deadline,"receiver auxiliary readiness")
            def send_aux():
                handle=mgr.send_aux(peer_name,0,peer["aux_ptrs"],0,"production-span-aux-whole-item")
                wait_done(agent,handle,deadline)
                agent.release_xfer_handle(handle)
            phases.mark("native_ten_buffer_aux_send",send_aux)
            desc.base.atomic_json(private/"aux-done.json",{"state":"DONE","buffer_count":len(AUX_LENGTHS)})
            wait_marker(private/"aux-verified.json",private,deadline,"ten-buffer auxiliary verification")
            aux_receipt=json.loads((private/"aux-verified.json").read_text())
            kv_receipt["source_pointer_order_matches_pinned_native_flat_order"]=True
            kv_receipt["source_preservation"]=phases.mark(
                "gpu_full_span_source_preservation_scan",
                lambda:verify_destination(torch,mgr,SELECTED_SRC_PAGES))
            phases.mark("source_auxiliary_preservation",lambda:verify_auxiliary(mgr))
        else:
            def verify_kv():
                result=verify_destination(torch,mgr)
                if result["regions_checked"]!=REGIONS or result["selected_pages_checked"]!=380:
                    raise RuntimeError("incomplete full-span KV destination coverage")
                return result
            phases.mark("receiver_kv_ready_barrier",lambda:desc.base.atomic_json(private/"receiver-kv-ready.json",{"ready":True}))
            wait_marker(private/"kv-done.json",private,deadline,"native KV transfer")
            kv_receipt.update(phases.mark("gpu_full_span_kv_destination_scan",verify_kv))
            desc.base.atomic_json(private/"kv-verified.json",kv_receipt)
            phases.mark("auxiliary_receiver_ready",lambda:desc.base.atomic_json(private/"aux-ready.json",{"ready":True}))
            wait_marker(private/"aux-done.json",private,deadline,"native ten-buffer auxiliary transfer")
            aux_receipt=phases.mark("gpu_pinned_auxiliary_full_span_verification",lambda:verify_auxiliary(mgr))
            desc.base.atomic_json(private/"aux-verified.json",aux_receipt)
        if time.time()>deadline: raise TimeoutError("component-relative T0 exceeded 570 seconds")
        # Registered spans remain alive until process teardown: freeing them
        # before the agent/backend destructor could leave NIXL with stale MR.
        phases.mark("registered_buffer_lifetime_check",lambda:check_buffer_lifetime(torch,mgr))
        if time.time()>deadline: raise TimeoutError("cleanup exceeded component-relative T0 limit")
        result=public_rank_result(rank,socket.gethostname(),gpu_uuid,agent.name,peer_name,metadata,peer_metadata,
            identity,source_hashes,mgr._production_registration_groups,geometry_receipt(rank),kv_receipt,
            aux_receipt,phases.rows,time.time()-t0)
        desc.base.atomic_json(art/f"rank{rank}-result.json",result)
        if rank==1:
            desc.base.atomic_json(private/"rank1-public-result-written.json",{"state":"DONE"})
            wait_marker(private/"final.json",private,deadline,"head result completion")
        else:
            wait_marker(private/"rank1-public-result-written.json",private,deadline,"rank1 public receipt")
            desc.base.atomic_json(art/"result.json",{"schema":"nixl-production-span-v1","status":"complete",
                "rank_receipts":["rank0-result.json","rank1-result.json"],"t0_limit_s":T0_LIMIT_S})
            desc.base.atomic_json(private/"final.json",{"state":"DONE"})
    except BaseException as exc:
        private=exchange/".production-span-private"
        try:
            private.mkdir(mode=0o700,parents=True,exist_ok=True); os.chmod(private,0o700)
            desc.base.atomic_json(private/f"error-rank{rank}.json",safe_error(exc))
            desc.base.atomic_json(art/f"rank{rank}-failure.json",{"schema":"nixl-production-span-failure-v1",
                "rank":rank,"status":"failed","error":safe_error(exc),"phase_samples":phases.rows,
                "elapsed_from_component_t0_s":round(time.time()-float(json.loads((exchange/"component-start.json").read_text())["t0_epoch_s"]),3)})
        except Exception: pass
        raise


def check_buffer_lifetime(torch,mgr):
    torch.cuda.synchronize()
    if len(mgr._production_kv_tensors)!=REGIONS or len(mgr._production_aux_tensors)!=len(AUX_LENGTHS):
        raise RuntimeError("registered buffers lost their owning tensor references before process teardown")
    return {"registered_kv_buffers_retained":REGIONS,"registered_aux_buffers_retained":len(AUX_LENGTHS),
            "release":"process teardown after receipt; registered spans are not freed while NIXL agent is live"}


def expected_receipt(rank:int):
    expected_pages=expected_kv_page_hashes()
    expected_aux=[{"index":i,"length_bytes":n,"sha256":digest_bytes(aux_pattern(i,n))}
                  for i,n in enumerate(AUX_LENGTHS)]
    return expected_pages,expected_aux


def check_art(art:Path):
    try:
        root=json.loads((art/"result.json").read_text())
        if root!={"schema":"nixl-production-span-v1","status":"complete",
                 "rank_receipts":["rank0-result.json","rank1-result.json"],"t0_limit_s":T0_LIMIT_S}:
            raise ValueError("combined gate receipt mismatch")
        a,b=[json.loads((art/f"rank{i}-result.json").read_text()) for i in (0,1)]
        for i,r in enumerate((a,b)):
            if r.get("schema")!="nixl-production-span-rank-v1" or r.get("rank")!=i or r.get("status")!="complete":
                raise ValueError("both complete physical-rank receipts required")
            if r.get("registration_groups")!=[{"mem_kind":"VRAM","count":190},{"mem_kind":"DRAM","count":10}]:
                raise ValueError("actual native registration group counts differ")
            g=r.get("geometry",{})
            for k,v in {"physical_pair_size":2,"physical_rank":i,"this_is_not_a_full_tp_collective":True,
                "target_mha_layers":94,"draft_mha_layers":1,"kv_regions":190,"bytes_per_region":REGION_BYTES,
                "total_advertised_bytes":TOTAL_KV_BYTES,"item_bytes_per_slot":256,"page_size_tokens":1,
                "slot_count":SLOTS,"local_kv_heads":1,"total_kv_heads":4,"pp_rank":0,"state_regions":0}.items():
                if g.get(k)!=v: raise ValueError(f"rank {i} geometry mismatch: {k}")
            if g.get("auxiliary_region_lengths_bytes")!=list(AUX_LENGTHS) or g.get("auxiliary_item_lengths_bytes")!=list(AUX_LENGTHS):
                raise ValueError("actual ten auxiliary lengths/item sizes mismatch")
            if r.get("elapsed_from_component_t0_s",T0_LIMIT_S+1)>T0_LIMIT_S:
                raise ValueError("component-relative T0 exceeded 570 seconds")
            if not r.get("phase_samples") or any("start" not in p or "end" not in p for p in r["phase_samples"]):
                raise ValueError("phase timing/resource samples incomplete")
            for phase in r["phase_samples"]:
                for snap in (phase["start"],phase["end"]):
                    if not all(k in snap for k in ("elapsed_from_component_t0_s","rss_kib","gpu_free_bytes","gpu_total_bytes","gpu_allocated_bytes","gpu_reserved_bytes")):
                        raise ValueError("phase resource sample missing fields")
            ident=r.get("runtime_identity",{})
            if ident.get("runtime_source_sha256")!=desc.SOURCE_SHA or ident.get("nixl_api_sha256")!=desc.base.EXPECTED_NIXL_API_SHA256:
                raise ValueError("actual runtime source/API identity mismatch")
            sh=r.get("source_hashes",{})
            if sh.get("nixl_conn_sha256")!=desc.SOURCE_SHA or sh.get("common_conn_sha256")!=desc.COMMON_SHA or sh.get("staging_buffer_sha256")!=desc.STAGING_SHA:
                raise ValueError("pinned native source hash mismatch")
        if a["host"]==b["host"] or a["gpu_uuid"]==b["gpu_uuid"]: raise ValueError("two distinct hosts and GPUs are required")
        if a["geometry"].get("registration_order_origins")!=b["geometry"].get("registration_order_origins"): raise ValueError("rank pointer-origin layout labels differ")
        if a["agent_name"]==b["agent_name"] or a["peer_name"]!=b["agent_name"] or b["peer_name"]!=a["agent_name"]:
            raise ValueError("peer identities are not reciprocal")
        if a["metadata_sha256"]!=b["peer_metadata_sha256"] or b["metadata_sha256"]!=a["peer_metadata_sha256"]:
            raise ValueError("private peer metadata hashes are not reciprocal")
        if a["source_hashes"]!=b["source_hashes"] or a["runtime_identity"]!=b["runtime_identity"]:
            raise ValueError("rank source/runtime identity mismatch")
        pages,aux=expected_receipt(1)
        for r in (a,b):
            kv=r.get("kv_transfer",{})
            if kv.get("case")!=KV_CASE or kv.get("source_layers")!=95 or kv.get("destination_layers")!=95:
                raise ValueError("95→95 production geometry case missing")
            if kv.get("source_pages")!=list(SELECTED_SRC_PAGES) or kv.get("destination_pages")!=list(SELECTED_DST_PAGES):
                raise ValueError("selected source/destination pages mismatch")
            if kv.get("region_count")!=REGIONS or kv.get("bytes_per_region")!=REGION_BYTES or kv.get("selected_payload_bytes")!=REGIONS*2*PAGE_BYTES:
                raise ValueError("selected-region transfer coverage mismatch")
        recv=b["kv_transfer"]
        if recv.get("state")!="verified" or recv.get("regions_checked")!=REGIONS or recv.get("selected_pages_checked")!=380:
            raise ValueError("rank 1 did not independently verify all selected pages")
        if recv.get("selected_page_bytes_checked")!=REGIONS*2*PAGE_BYTES or recv.get("untouched_registered_bytes_gpu_scanned")!=TOTAL_KV_BYTES-REGIONS*2*PAGE_BYTES:
            raise ValueError("rank 1 full-span GPU scan byte counts mismatch")
        if recv.get("selected_page_sha256")!=pages: raise ValueError("independent per-region/per-page hash mismatch")
        if a["kv_transfer"].get("receiver_verification")!=recv: raise ValueError("sender receipt does not bind full-span receiver verification")
        if a["kv_transfer"].get("state")!="DONE" or a["kv_transfer"].get("native_dlist_entries")!=REGIONS*2 or a["kv_transfer"].get("source_pointer_order_matches_pinned_native_flat_order") is not True:
            raise ValueError("native 95→95 sender transfer gate failed")
        for r in (a,b):
            auxr=r.get("aux_transfer",{})
            if auxr.get("state")!="verified" or auxr.get("buffer_count")!=10 or auxr.get("total_bytes")!=AUX_TOTAL:
                raise ValueError("full-span ten-buffer auxiliary verification missing")
            if auxr.get("item_sha256")!=aux: raise ValueError("auxiliary per-buffer hash/length mismatch")
        source=a["kv_transfer"].get("source_preservation",{})
        expected_source_pages=[dict(row,destination_page=row["source_page"]) for row in pages]
        if (source.get("state")!="verified" or source.get("selected_page_sha256")!=expected_source_pages
            or source.get("selected_page_bytes_checked")!=REGIONS*2*PAGE_BYTES
            or source.get("untouched_registered_bytes_gpu_scanned")!=TOTAL_KV_BYTES-REGIONS*2*PAGE_BYTES):
            raise ValueError("independent source preservation scan missing or mismatched")
        if a["aux_transfer"]!=b["aux_transfer"]: raise ValueError("rank auxiliary receipts differ")
        # Raw addresses are private-only: reject pointer tables or raw address fields in public output.
        for r in (a,b):
            if any(k in r for k in ("kv_ptrs","aux_ptrs","kv_ranges","aux_ranges","metadata_bytes")):
                raise ValueError("private addresses or metadata bytes leaked into public receipt")
        return {"status":"pass","physical_ranks":2,"hosts":[a["host"],b["host"]],
            "gpu_uuids":[a["gpu_uuid"],b["gpu_uuid"]],"registered_kv_bytes_per_rank":TOTAL_KV_BYTES,
            "registered_aux_bytes_per_rank":AUX_TOTAL,"selected_kv_bytes":REGIONS*2*PAGE_BYTES,
            "untouched_destination_bytes_gpu_scanned":TOTAL_KV_BYTES-REGIONS*2*PAGE_BYTES,
            "component_relative_t0_s_max":max(a["elapsed_from_component_t0_s"],b["elapsed_from_component_t0_s"]),
            "scope":"Two physical H100 rank pair, no weights/model; native full-span NIXL registration and sparse selected-page transfer; not full TP collective or EAGLE output proof"}
    except Exception as exc:
        return {"status":"fail","error":re.sub(r"0x[0-9a-fA-F]{6,}","<address>",str(exc))[:600]}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--rank",type=int); ap.add_argument("--art",type=Path); ap.add_argument("--exchange-dir",type=Path); ap.add_argument("--check",action="store_true")
    a=ap.parse_args()
    if a.check:
        result=check_art(a.art); print(json.dumps(result,indent=2)); return 0 if result["status"]=="pass" else 1
    if a.rank not in (0,1) or not a.art or not a.exchange_dir: ap.error("rank mode requires --rank 0|1 --art DIR --exchange-dir PRIVATE_DIR")
    rank_run(a.rank,a.art,a.exchange_dir); return 0
if __name__=="__main__": raise SystemExit(main())
