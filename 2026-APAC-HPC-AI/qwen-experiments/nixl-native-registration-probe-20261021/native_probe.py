#!/usr/bin/env python3
"""Prospective no-model NIXL registration and transfer exercise."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, socket, sys, time, uuid
from pathlib import Path
from types import MethodType, SimpleNamespace
from typing import List, Tuple

HERE = Path(__file__).resolve().parent
BASE_DIR = HERE
SPEC = importlib.util.spec_from_file_location("native_descriptor", BASE_DIR / "descriptor-base.py")
if SPEC is None or SPEC.loader is None: raise RuntimeError("bundled descriptor helper unavailable")
desc = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(desc)
CASES = desc.CASES
REGIONS, PAGES, STRIDE = 190, 4, 256
SRC_PAGES, DST_PAGES = (1, 3), (0, 2)
AUX_WIDTHS, AUX_SLOTS, AUX_SRC_SLOT, AUX_DST_SLOT = (16, 32, 64), 4, 1, 2
DEADLINE = 300


def pattern(region, page, case_i):
    seed = (case_i * 37 + region * 19 + page * 7 + 23) & 255
    return bytes((seed + i * 11) & 255 for i in range(STRIDE))


def expected_kv(case_i, layers):
    out = bytearray([0xA5]) * (REGIONS * PAGES * STRIDE)
    for region in range(2 * layers):
        for sp, dp in zip(SRC_PAGES, DST_PAGES):
            off = (region * PAGES + dp) * STRIDE
            out[off:off+STRIDE] = pattern(region, sp, case_i)
    return bytes(out)


def expected_aux(width, case_i):
    out = bytearray([0xA5]) * (AUX_SLOTS * width)
    payload = bytes((case_i * 29 + width + i * 5) & 255 for i in range(width))
    out[AUX_DST_SLOT*width:(AUX_DST_SLOT+1)*width] = payload
    return bytes(out)


def sha(data): return hashlib.sha256(data).hexdigest()


def methods_from_source(path, common_path):
    if desc.digest(path) != desc.SOURCE_SHA:
        raise RuntimeError("NIXL source hash mismatch")
    np = __import__("numpy")
    globs = {"np": np, "List": List, "Tuple": Tuple,
             "logger": __import__("logging").getLogger("native-registration-probe"),
             "_nixl_device_id": desc.extract(path, "_nixl_device_id")}
    return {
        "register_buffer_to_engine": desc.extract(path, "register_buffer_to_engine", "NixlKVManager", globs),
        "send_aux": desc.extract(path, "send_aux", "NixlKVManager", globs),
        "_init_hetero_tp_prep_handle": desc.extract(path, "_init_hetero_tp_prep_handle", "NixlKVManager", globs),
        "send_kvcache_slice": desc.extract(path, "send_kvcache_slice", "NixlKVManager", globs),
        "get_mha_kv_ptrs_with_pp": desc.extract(common_path, "get_mha_kv_ptrs_with_pp", "CommonKVManager", {"List": List, "Tuple": Tuple}),
    }


def runtime_methods():
    # descriptor.source_bundle verifies all three source pins against the loaded runtime.
    _, hashes = desc.source_bundle()
    nixl_path = Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py")
    common_path = Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/common/conn.py")
    return methods_from_source(nixl_path, common_path), hashes


def wait_done(agent, handle, deadline):
    while time.time() < deadline:
        state = agent.check_xfer_state(handle)
        if state == "DONE": return
        if state == "ERR": raise RuntimeError("NIXL transfer reached ERR")
        time.sleep(.001)
    raise TimeoutError("NIXL transfer exceeded 300-second cap")


class RegistrationAudit:
    def __init__(self, agent): self.agent, self.calls = agent, []
    def __getattr__(self, key): return getattr(self.agent, key)
    def register_memory(self, rows, mem_kind):
        self.calls.append((mem_kind, len(rows)))
        return self.agent.register_memory(rows, mem_kind)


def init_native_manager(agent, torch, rank, methods):
    kv_tensors = [torch.empty(PAGES*STRIDE, dtype=torch.uint8, device="cuda:0") for _ in range(REGIONS)]
    aux_tensors = [torch.empty(AUX_SLOTS*w, dtype=torch.uint8, pin_memory=True) for w in AUX_WIDTHS]
    for t in kv_tensors: t.fill_(0xA5)
    for t in aux_tensors: t.fill_(0xA5)
    args = SimpleNamespace(
        kv_data_ptrs=[int(t.data_ptr()) for t in kv_tensors],
        kv_data_lens=[PAGES*STRIDE]*REGIONS, kv_data_mem_kinds=["VRAM"]*REGIONS,
        kv_item_lens=[STRIDE]*REGIONS, page_size=1, gpu_id=0,
        engine_rank=0, total_kv_head_num=4, kv_head_num=1, prefill_start_layer=0,
        aux_data_ptrs=[int(t.data_ptr()) for t in aux_tensors],
        aux_data_lens=[AUX_SLOTS*w for w in AUX_WIDTHS], aux_item_lens=list(AUX_WIDTHS),
        state_data_ptrs=[], state_data_lens=[])
    audit = RegistrationAudit(agent)
    mgr = SimpleNamespace(kv_args=args, agent=audit, attn_tp_size=4)
    mgr.register_buffer_to_engine = MethodType(methods["register_buffer_to_engine"], mgr)
    mgr.send_aux = MethodType(methods["send_aux"], mgr)
    mgr._init_hetero_tp_prep_handle = MethodType(methods["_init_hetero_tp_prep_handle"], mgr)
    mgr.send_kvcache_slice = MethodType(methods["send_kvcache_slice"], mgr)
    mgr.get_mha_kv_ptrs_with_pp = MethodType(methods["get_mha_kv_ptrs_with_pp"], mgr)
    mgr.register_buffer_to_engine()
    if audit.calls != [("VRAM", REGIONS), ("DRAM", len(AUX_WIDTHS))]:
        raise RuntimeError(f"native register_buffer_to_engine used unexpected groups: {audit.calls}")
    mgr.agent = agent
    # Set buffers after allocation to keep all source layers distinct and auditable.
    mgr._probe_kv_tensors, mgr._probe_aux_tensors = kv_tensors, aux_tensors
    mgr._probe_all_kv_ptrs = list(args.kv_data_ptrs)
    mgr._probe_all_kv_lens = list(args.kv_data_lens)
    mgr._probe_all_kv_mem_kinds = list(args.kv_data_mem_kinds)
    mgr._probe_all_kv_item_lens = list(args.kv_item_lens)
    mgr._probe_registration_groups = [{"mem_kind": k, "count": c} for k, c in audit.calls]
    mgr._probe_ranges = [(int(t.data_ptr()), t.numel()) for t in kv_tensors]
    mgr._probe_aux_ranges = [(int(t.data_ptr()), t.numel()) for t in aux_tensors]
    return mgr


class CheckedAgent:
    """Guard descriptor bounds, retaining real NIXL behavior behind the proxy."""
    def __init__(self, agent, local, remote, local_aux, remote_aux):
        self._agent, self.calls = agent, 0
        self.local, self.remote = local, remote
        self.local_aux, self.remote_aux = local_aux, remote_aux
    def __getattr__(self, key): return getattr(self._agent, key)
    def get_xfer_descs(self, rows, kind):
        src = self.calls % 2 == 0; self.calls += 1
        bounds = (self.local if src else self.remote) if kind == "VRAM" else (self.local_aux if src else self.remote_aux)
        for row in rows:
            addr, length = int(row[0]), int(row[1])
            if length <= 0 or not any(addr >= p and addr+length <= p+n for p,n in bounds):
                raise RuntimeError(f"{kind} descriptor outside registered memory")
        return self._agent.get_xfer_descs(rows, kind)



def configure_case(mgr, dst_obj, src_layers, dst_layers):
    """Set case-local pointer lists while leaving all 190 registrations intact."""
    nsrc, ndst = 2 * src_layers, 2 * dst_layers
    args = mgr.kv_args
    args.kv_data_ptrs = mgr._probe_all_kv_ptrs[:nsrc]
    args.kv_data_lens = mgr._probe_all_kv_lens[:nsrc]
    args.kv_data_mem_kinds = mgr._probe_all_kv_mem_kinds[:nsrc]
    args.kv_item_lens = mgr._probe_all_kv_item_lens[:nsrc]
    dst_obj.dst_kv_ptrs = mgr._probe_all_dst_ptrs[:ndst]
    dst_obj.dst_kv_item_lens = mgr._probe_all_dst_item_lens[:ndst]
    mgr._init_hetero_tp_prep_handle(mgr._probe_peer_name, dst_obj)
    plan = mgr._ondemand_slice_plans[mgr._probe_peer_name]
    if len(args.kv_data_ptrs) != nsrc or len(dst_obj.dst_kv_ptrs) != ndst:
        raise RuntimeError("case-local native pointer geometry mismatch")
    if len(plan["src_ptrs"]) != nsrc or len(plan["dst_ptrs"]) != nsrc:
        raise RuntimeError("native helper selected wrong source/destination layer count")
    if (plan["src_stride"], plan["dst_stride"], plan["length"],
            plan["src_offset"], plan["dst_offset"]) != (STRIDE, STRIDE, STRIDE, 0, 0):
        raise RuntimeError("probe requires uniform equal whole-head item geometry")
    return plan


def rank_receipt(rank, local, peer, metadata, peer_metadata, identity, source_hashes,
                 registration_groups, cases, aux_state, aux_sha, aux_expected_sha):
    return {"schema":"nixl-native-registration-rank-v1","rank":rank,"status":"complete",
        "host":local["host"],"gpu_uuid":local["gpu_uuid"],"agent_name":local["agent_name"],
        "peer_name":peer["agent_name"],"metadata_sha256":sha(metadata),
        "peer_metadata_sha256":sha(peer_metadata),"runtime_identity":identity,
        "source_hashes":source_hashes,"registration_groups":registration_groups,
        "cases":cases,"aux_state":aux_state,"aux_sha256":aux_sha,
        "aux_expected_sha256":aux_expected_sha}


def fill_case(torch, mgr, case_i, source):
    import numpy as np
    for region, tensor in enumerate(mgr._probe_kv_tensors):
        buf = bytearray([0xA5]) * (PAGES*STRIDE)
        if source:
            for page in range(PAGES): buf[page*STRIDE:(page+1)*STRIDE] = pattern(region, page, case_i)
        tensor.copy_(torch.from_numpy(np.frombuffer(buf, dtype=np.uint8).copy()).to("cuda:0"))
    for width, tensor in zip(AUX_WIDTHS, mgr._probe_aux_tensors):
        tensor.fill_(0xA5)
        if source:
            payload = bytes((case_i*29 + width + i*5) & 255 for i in range(width))
            tensor[AUX_SRC_SLOT*width:(AUX_SRC_SLOT+1)*width].copy_(torch.tensor(list(payload), dtype=torch.uint8))
    torch.cuda.synchronize()


def tensor_bytes(t): return t.detach().cpu().numpy().tobytes()
def aux_bytes(t): return bytes(t.tolist())


def rank_run(rank, art, exchange):
    import torch
    from nixl._api import nixl_agent, nixl_agent_config, nixl_thread_sync_t
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1: raise RuntimeError("require one visible CUDA GPU per rank")
    torch.cuda.set_device(0)
    prop = torch.cuda.get_device_properties(0); gpu_uuid = str(getattr(prop, "uuid", ""))
    if not gpu_uuid: raise RuntimeError("GPU UUID unavailable")
    ib = desc.base.active_ib_devices()
    if not ib or os.environ.get("UCX_NET_DEVICES") != ",".join(ib):
        raise RuntimeError("UCX_NET_DEVICES does not match active worker IB autodetection")
    if os.environ.get("UCX_POSIX_USE_PROC_LINK") != "n":
        raise RuntimeError("UCX_POSIX_USE_PROC_LINK must be n")
    methods, source_hashes = runtime_methods()
    private = exchange / ".native-registration-private"
    private.mkdir(mode=0o700, parents=True, exist_ok=True); os.chmod(private, 0o700)
    start = private / "start.json"
    if rank == 0:
        if start.exists(): raise RuntimeError("stale exchange directory")
        desc.base.atomic_json(start, {"started": time.time()})
    desc.base.wait_until(start.exists, time.time()+30, "run start")
    deadline = json.loads(start.read_text())["started"] + DEADLINE
    cfg = nixl_agent_config(backends=[], num_threads=8, sync_mode=nixl_thread_sync_t.NIXL_THREAD_SYNC_STRICT)
    agent = nixl_agent(f"native-reg-{rank}-{uuid.uuid4()}", cfg); agent.create_backend("UCX", {"num_threads":"8"})
    mgr = init_native_manager(agent, torch, rank, methods)
    # Native call above registers exactly 190 VRAM regions and 3 pinned DRAM aux tensors.
    metadata = agent.get_agent_metadata()
    (private/f"agent-{rank}.bin").write_bytes(metadata)
    local = {"rank":rank,"name":agent.name,"gpu_uuid":gpu_uuid,
             "kv_ptrs":mgr.kv_args.kv_data_ptrs,"aux_ptrs":mgr.kv_args.aux_data_ptrs,
             "kv_ranges":mgr._probe_ranges,"aux_ranges":mgr._probe_aux_ranges,
             "metadata_sha256":sha(metadata),"metadata_len":len(metadata)}
    desc.base.atomic_json(private/f"rank-{rank}.json",local)
    other_path=private/f"rank-{1-rank}.json"
    desc.base.wait_until(other_path.exists,deadline,"peer registration metadata")
    peer=json.loads(other_path.read_text()); peer_meta=(private/f"agent-{1-rank}.bin").read_bytes()
    if len(peer_meta)!=peer["metadata_len"] or sha(peer_meta)!=peer["metadata_sha256"]: raise RuntimeError("peer metadata mismatch")
    agent.add_remote_agent(peer_meta)
    identity=desc.base._source_identity()
    ready={"host":socket.gethostname(),"gpu_uuid":gpu_uuid,"agent_name":agent.name,"metadata_sha256":sha(metadata),"source_hashes":source_hashes,"runtime_identity":identity}
    desc.base.atomic_json(private/f"ready-{rank}.json",ready)
    desc.base.wait_until(lambda:all((private/f"ready-{i}.json").exists() for i in (0,1)),deadline,"source-ready barrier")
    peers=[json.loads((private/f"ready-{i}.json").read_text()) for i in (0,1)]
    if peers[0]["host"]==peers[1]["host"] or peers[0]["gpu_uuid"]==peers[1]["gpu_uuid"]: raise RuntimeError("ranks must use distinct hosts and GPUs")
    if peers[0]["agent_name"]==peers[1]["agent_name"] or peer["name"]!=peers[1-rank]["agent_name"]: raise RuntimeError("remote peer identity mismatch")
    if peers[0]["source_hashes"]!=peers[1]["source_hashes"] or peers[0].get("runtime_identity")!=peers[1].get("runtime_identity"):
        raise RuntimeError("rank source identity mismatch")
    rows=[]
    if rank==0:
        peer_name=peer["name"]
        guard=CheckedAgent(agent,mgr._probe_ranges,peer["kv_ranges"],mgr._probe_aux_ranges,peer["aux_ranges"])
        mgr.agent=guard
        mgr._probe_peer_name=peer_name
        mgr._probe_all_dst_ptrs=list(peer["kv_ptrs"])
        mgr._probe_all_dst_item_lens=[STRIDE]*REGIONS
        dst=SimpleNamespace(decode_tp_size=8,decode_tp_rank=0,dst_kv_item_len=STRIDE,gpu_id=0)
        for ci,(case,sl,dl) in enumerate(CASES):
            fill_case(torch,mgr,ci,True)
            plan=configure_case(mgr,dst,sl,dl)
            desc.base.wait_until((private/f"kv-ready-{ci}.json").exists,deadline,f"receiver ready {case}")
            handle=mgr.send_kvcache_slice(peer_name,SRC_PAGES,DST_PAGES,f"kv-{ci}")
            wait_done(agent,handle,deadline)
            desc.base.atomic_json(private/f"kv-done-{ci}.json",{"case":case,"state":"DONE","src_layers":sl,"dst_layers":dl,"src_pages":list(SRC_PAGES),"dst_pages":list(DST_PAGES)})
            desc.base.wait_until((private/f"kv-verified-{ci}.json").exists,deadline,f"receiver verifies {case}")
            ack=json.loads((private/f"kv-verified-{ci}.json").read_text())
            agent.release_xfer_handle(handle)
            rows.append({"case":case,"src_layers":sl,"dst_layers":dl,"state":"DONE","gpu_sha256":ack["gpu_sha256"],"expected_sha256":ack["expected_sha256"]})
        fill_case(torch,mgr,0,True)
        desc.base.wait_until((private/"aux-ready.json").exists,deadline,"aux receiver ready")
        ah=mgr.send_aux(peer_name,AUX_SRC_SLOT,peer["aux_ptrs"],AUX_DST_SLOT,"native-aux-1-to-2")
        wait_done(agent,ah,deadline)
        desc.base.atomic_json(private/"aux-done.json",{"state":"DONE"})
        desc.base.wait_until((private/"aux-verified.json").exists,deadline,"aux receiver verification")
        aux_ack=json.loads((private/"aux-verified.json").read_text())
        agent.release_xfer_handle(ah)
        rank0=rank_receipt(rank,peers[0],peers[1],metadata,peer_meta,identity,source_hashes,
                           mgr._probe_registration_groups,rows,"DONE",aux_ack["sha256"],aux_ack["expected_sha256"])
        desc.base.atomic_json(art/"rank0-result.json",rank0)
        desc.base.atomic_json(art/"result.json",{"schema":"nixl-native-registration-v1","status":"complete",
            "rank_receipts":["rank0-result.json","rank1-result.json"]})
        desc.base.atomic_json(private/"final.json",{"complete":True})
    else:
        for ci,(case,sl,dl) in enumerate(CASES):
            fill_case(torch,mgr,ci,False)
            desc.base.atomic_json(private/f"kv-ready-{ci}.json",{"ready":True})
            desc.base.wait_until((private/f"kv-done-{ci}.json").exists,deadline,f"sender KV {case}")
            done=json.loads((private/f"kv-done-{ci}.json").read_text())
            if done!={"case":case,"state":"DONE","src_layers":sl,"dst_layers":dl,"src_pages":list(SRC_PAGES),"dst_pages":list(DST_PAGES)}: raise RuntimeError("sender case receipt mismatch")
            actual=b"".join(tensor_bytes(t) for t in mgr._probe_kv_tensors)
            expected=expected_kv(ci,sl)
            if actual!=expected: raise RuntimeError(f"{case} KV bytes or sentinels mismatch")
            h=sha(actual); eh=sha(expected)
            desc.base.atomic_json(private/f"kv-verified-{ci}.json",{"gpu_sha256":h,"expected_sha256":eh})
            rows.append({"case":case,"src_layers":sl,"dst_layers":dl,"state":"verified","gpu_sha256":h,"expected_sha256":eh})
        for t in mgr._probe_aux_tensors: t.fill_(0xA5)
        desc.base.atomic_json(private/"aux-ready.json",{"ready":True})
        desc.base.wait_until((private/"aux-done.json").exists,deadline,"native aux send completion")
        if json.loads((private/"aux-done.json").read_text())!={"state":"DONE"}: raise RuntimeError("native aux send did not reach DONE")
        hashes=[]
        for width,t in zip(AUX_WIDTHS,mgr._probe_aux_tensors):
            actual=aux_bytes(t); expected=expected_aux(width,0)
            if actual!=expected: raise RuntimeError(f"aux width {width} host bytes/sentinels mismatch")
            hashes.append((actual,expected))
        combined=b"".join(a for a,_ in hashes); expected=b"".join(e for _,e in hashes)
        aux_hash, aux_expected_hash = sha(combined), sha(expected)
        rank1=rank_receipt(rank,peers[1],peers[0],metadata,peer_meta,identity,source_hashes,
                           mgr._probe_registration_groups,rows,"verified",aux_hash,aux_expected_hash)
        desc.base.atomic_json(art/"rank1-result.json",rank1)
        desc.base.atomic_json(private/"aux-verified.json",{"sha256":aux_hash,"expected_sha256":aux_expected_hash})
        desc.base.wait_until((private/"final.json").exists,deadline,"final sender result barrier")


def check(art):
    try:
        root=json.loads((art/"result.json").read_text())
        if root!={"schema":"nixl-native-registration-v1","status":"complete",
                  "rank_receipts":["rank0-result.json","rank1-result.json"]}:
            raise ValueError("combined result receipt mismatch")
        a,b=[json.loads((art/f"rank{i}-result.json").read_text()) for i in (0,1)]
        keys={"schema","rank","status","host","gpu_uuid","agent_name","peer_name",
              "metadata_sha256","peer_metadata_sha256","runtime_identity","source_hashes",
              "registration_groups","cases","aux_state","aux_sha256","aux_expected_sha256"}
        if any(set(r)!=keys for r in (a,b)): raise ValueError("rank receipt schema mismatch")
        if any(r["schema"]!="nixl-native-registration-rank-v1" or r["rank"]!=i or r["status"]!="complete" for i,r in enumerate((a,b))):
            raise ValueError("both rank-complete receipts are required")
        if not all(isinstance(r["host"],str) and r["host"] for r in (a,b)) or a["host"]==b["host"]:
            raise ValueError("rank receipts must identify distinct hosts")
        if not all(isinstance(r["gpu_uuid"],str) and r["gpu_uuid"] for r in (a,b)) or a["gpu_uuid"]==b["gpu_uuid"]:
            raise ValueError("rank receipts must identify distinct GPU UUIDs")
        if (not a["agent_name"] or not b["agent_name"] or a["agent_name"]==b["agent_name"]
                or a["peer_name"]!=b["agent_name"] or b["peer_name"]!=a["agent_name"]):
            raise ValueError("peer agent identities are not reciprocal")
        sha_ok=lambda x: isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x)
        if any(not sha_ok(r[k]) for r in (a,b) for k in ("metadata_sha256","peer_metadata_sha256")):
            raise ValueError("metadata identity hash malformed")
        if a["metadata_sha256"]!=b["peer_metadata_sha256"] or b["metadata_sha256"]!=a["peer_metadata_sha256"]:
            raise ValueError("peer metadata hashes are not reciprocal")
        if a["runtime_identity"]!=b["runtime_identity"] or a["source_hashes"]!=b["source_hashes"]:
            raise ValueError("rank runtime/source identities differ")
        ident=a["runtime_identity"]
        ident_keys={"runtime_source_sha256","nixl_api_sha256","nixl_bindings_sha256","torch_file_sha256",
                    "nixl_api_path","nixl_bindings_path","torch_path","nixl_version","torch_version"}
        if set(ident)!=ident_keys or any(not isinstance(ident[k],str) or not ident[k] for k in ident_keys):
            raise ValueError("runtime identity is incomplete")
        for k in ("runtime_source_sha256","nixl_api_sha256","nixl_bindings_sha256","torch_file_sha256"):
            if not sha_ok(ident[k]): raise ValueError(f"malformed runtime identity hash {k}")
        if ident["runtime_source_sha256"]!=desc.SOURCE_SHA or ident["nixl_api_sha256"]!=desc.base.EXPECTED_NIXL_API_SHA256:
            raise ValueError("runtime NIXL/API source pin mismatch")
        sources=a["source_hashes"]
        source_keys={"nixl_conn_sha256","common_conn_sha256","staging_buffer_sha256","compute_head_slice_params_sha256"}
        if set(sources)!=source_keys or any(not sha_ok(v) for v in sources.values()): raise ValueError("source hash manifest malformed")
        if sources["nixl_conn_sha256"]!=desc.SOURCE_SHA or sources["common_conn_sha256"]!=desc.COMMON_SHA or sources["staging_buffer_sha256"]!=desc.STAGING_SHA:
            raise ValueError("pinned source identity mismatch")
        groups=[{"mem_kind":"VRAM","count":REGIONS},{"mem_kind":"DRAM","count":len(AUX_WIDTHS)}]
        if a["registration_groups"]!=groups or b["registration_groups"]!=groups:
            raise ValueError("native registration groups/counts mismatch")
        if any(not isinstance(r["cases"],list) or len(r["cases"])!=len(CASES) for r in (a,b)):
            raise ValueError("each rank must provide all three case receipts")
        for i,((case,sl,dl),ra,rb) in enumerate(zip(CASES,a["cases"],b["cases"])):
            for row,state in ((ra,"DONE"),(rb,"verified")):
                if (row.get("case")!=case or row.get("src_layers")!=sl or row.get("dst_layers")!=dl
                        or row.get("state")!=state): raise ValueError("case geometry/state mismatch")
                expected=sha(expected_kv(i,sl))
                if row.get("expected_sha256")!=expected or row.get("gpu_sha256")!=expected:
                    raise ValueError("destination KV hash differs from independently expected bytes")
            if (ra["gpu_sha256"],ra["expected_sha256"])!=(rb["gpu_sha256"],rb["expected_sha256"]):
                raise ValueError("sender and receiver case hashes differ")
        aux_expected=sha(b"".join(expected_aux(w,0) for w in AUX_WIDTHS))
        if a["aux_state"]!="DONE" or b["aux_state"]!="verified" or any(r["aux_expected_sha256"]!=aux_expected or r["aux_sha256"]!=aux_expected for r in (a,b)):
            raise ValueError("native aux transfer or receiver hash mismatch")
        if (a["aux_sha256"],a["aux_expected_sha256"])!=(b["aux_sha256"],b["aux_expected_sha256"]):
            raise ValueError("sender and receiver aux hashes differ")
        return {"status":"pass","rank_receipts":2,"kv_geometries":3,
                "native_vram_regions":REGIONS,"native_pinned_dram_aux_buffers":len(AUX_WIDTHS),"model":"none"}
    except Exception as e: return {"status":"fail","reason":f"{type(e).__name__}: {e}"}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--rank",type=int,choices=(0,1));p.add_argument("--art",type=Path,required=True);p.add_argument("--exchange-dir",type=Path);p.add_argument("--check",action="store_true");a=p.parse_args()
    if a.check:
        out=check(a.art);print(json.dumps(out,sort_keys=True));return 0 if out["status"]=="pass" else 1
    if a.rank is None or a.exchange_dir is None:p.error("rank mode requires --rank and --exchange-dir")
    a.art.mkdir(parents=True,exist_ok=True)
    try: rank_run(a.rank,a.art,a.exchange_dir)
    except Exception as exc:
        desc.base.atomic_json(a.art/f"rank{a.rank}-failure.json",{"rank":a.rank,**desc.failure_details(exc)})
        print(f"native registration probe failed: {type(exc).__name__}",file=sys.stderr);return 1
    return 0
if __name__=="__main__":raise SystemExit(main())
