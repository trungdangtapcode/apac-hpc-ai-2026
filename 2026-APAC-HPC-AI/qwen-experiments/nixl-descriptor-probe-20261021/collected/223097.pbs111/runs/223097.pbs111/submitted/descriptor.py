#!/usr/bin/env python3
"""Source-pinned, no-model exercise of SGLang's NIXL KV slice path."""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import logging
import os
import re
import socket
import sys
import time
import traceback
import uuid
from pathlib import Path
from types import MethodType, SimpleNamespace
from typing import List, Tuple

_BASE_PATH = Path(__file__).resolve().with_name("base-peer.py")
_BASE_SPEC = importlib.util.spec_from_file_location("descriptor_base_peer", _BASE_PATH)
if _BASE_SPEC is None or _BASE_SPEC.loader is None:
    raise RuntimeError(f"cannot load bundled peer probe helper: {_BASE_PATH}")
base = importlib.util.module_from_spec(_BASE_SPEC)
_BASE_SPEC.loader.exec_module(base)

PAGE_SIZE, PAGE_COUNT, STRIDE = 1, 4, 256
REGION_COUNT = 190
SOURCE_SHA = "912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f"
COMMON_SHA = "ba33d63c6920f87b55cf57f9224bb7d08af67e1476bd70b8e1a70067f33a29d7"
STAGING_SHA = "52693777d6ee25d1919555a5b910677ba58fa6c18e35782faa7a0470b43839ab"
CASES = (("target-only-94-94", 94, 94),
         ("decode-only-draft-94-95", 94, 95),
         ("both-draft-95-95", 95, 95))
SRC_PAGES, DST_PAGES = (1, 3), (0, 2)
DEADLINE_S = 300


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def extract(path: Path, name: str, owner: str | None = None, globs=None):
    tree = ast.parse(path.read_text())
    if owner:
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner]
        nodes = [n for c in classes for n in c.body
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    else:
        nodes = [n for n in tree.body
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    if len(nodes) != 1:
        raise RuntimeError(f"expected one {owner or ''}.{name} in {path}, got {len(nodes)}")
    scope = dict(globs or {})
    exec(compile(ast.Module(body=[nodes[0]], type_ignores=[]), str(path), "exec"), scope)
    return scope[name]


def source_bundle():
    nixl = Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py")
    common = Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/common/conn.py")
    staging = Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/common/staging_buffer.py")
    if (digest(nixl) != SOURCE_SHA or digest(common) != COMMON_SHA
            or digest(staging) != STAGING_SHA):
        raise RuntimeError("patched NIXL, common connection, or staging helper source hash mismatch")
    import numpy as np
    env = {"np": np, "List": List, "Tuple": Tuple, "logger": logging.getLogger("descriptor-probe"),
           "_nixl_device_id": extract(nixl, "_nixl_device_id")}
    env["_init_hetero_tp_prep_handle"] = extract(nixl, "_init_hetero_tp_prep_handle", "NixlKVManager", env)
    env["send_kvcache_slice"] = extract(nixl, "send_kvcache_slice", "NixlKVManager", env)
    env["get_mha_kv_ptrs_with_pp"] = extract(common, "get_mha_kv_ptrs_with_pp", "CommonKVManager")
    import sglang.srt.disaggregation.common.staging_buffer as staging_mod
    helper = staging_mod.compute_head_slice_params
    return env, {"nixl_conn_sha256": digest(nixl), "common_conn_sha256": digest(common),
                 "staging_buffer_sha256": digest(staging),
                 "compute_head_slice_params_sha256": hashlib.sha256(
                     __import__("inspect").getsource(helper).encode()).hexdigest()}


def pattern(rank: int, case: int, region: int, page: int) -> bytes:
    seed = (rank * 43 + case * 31 + region * 17 + page * 11) & 255
    return bytes((seed + i * 13) & 255 for i in range(STRIDE))


def expected_destination(case_i: int, src_rank: int, src_layers: int) -> bytes:
    expected = bytearray([0xA5]) * (REGION_COUNT * PAGE_COUNT * STRIDE)
    for region in range(2 * src_layers):
        for src_page, dst_page in zip(SRC_PAGES, DST_PAGES):
            off = (region * PAGE_COUNT + dst_page) * STRIDE
            expected[off:off + STRIDE] = pattern(src_rank, case_i, region, src_page)
    return bytes(expected)


def check_desc_bounds(rows, base_ptr: int, size: int, label: str):
    lo, hi = base_ptr, base_ptr + size
    for addr, length, _device in rows:
        addr, length = int(addr), int(length)
        if length <= 0 or addr < lo or addr + length > hi:
            raise RuntimeError(f"{label} descriptor escapes registered region")


def check_desc_any_region(rows, bounds, label):
    for addr, length, _device in rows:
        addr, length = int(addr), int(length)
        if length <= 0 or not any(addr >= p and addr + length <= p + n for p, n in bounds):
            raise RuntimeError(f"actual {label} NIXL descriptor escapes all registered regions")


def guarded_agent(agent, local_bounds, remote_bounds):
    class Guard:
        def __init__(self):
            self.calls = 0

        def __getattr__(self, name):
            return getattr(agent, name)

        def get_xfer_descs(self, rows, mem_kind):
            source = self.calls % 2 == 0
            check_desc_any_region(rows, local_bounds if source else remote_bounds,
                                  "source" if source else "destination")
            self.calls += 1
            return agent.get_xfer_descs(rows, mem_kind)
    return Guard()


def wait_done(agent, handle, deadline):
    while time.time() < deadline:
        state = agent.check_xfer_state(handle)
        if state == "DONE":
            return
        if state == "ERR":
            raise RuntimeError("NIXL transfer reached ERR")
        time.sleep(0.001)
    raise TimeoutError("NIXL handle did not reach DONE inside 300-second cap")


def send_slice(manager, peer_name, pages, dst_pages, notification):
    return manager.send_kvcache_slice(peer_name, pages, dst_pages, notification)


def failure_details(exc):
    message = re.sub(r"0x[0-9a-fA-F]{6,}", "<address>", str(exc))[:800]
    frames = [{"path": f.filename, "line": f.lineno, "function": f.name}
              for f in traceback.extract_tb(exc.__traceback__)[-6:]]
    return {"error_type": type(exc).__name__, "error": message, "frames": frames}


def alloc_regions(torch, agent, rank, cases):
    """Allocate one registered contiguous region for every logical TP rank."""
    count = max(layers for _, layers, _ in cases) * 2 * PAGE_COUNT * STRIDE
    n = 4 if rank == 0 else 8
    regions, tables = [], []
    for logical_rank in range(n):
        buf = torch.empty(count, dtype=torch.uint8, device="cuda:0")
        host = bytearray(count)
        for region in range(max(layers for _, layers, _ in cases) * 2):
            for page in range(PAGE_COUNT):
                off = (region * PAGE_COUNT + page) * STRIDE
                block = pattern(logical_rank, 0 if rank == 0 else 3, region, page)
                host[off:off + STRIDE] = block if rank == 0 else bytes([0xA5]) * STRIDE
        import numpy as np
        buf.copy_(torch.from_numpy(np.frombuffer(host, dtype=np.uint8).copy()).to("cuda:0"))
        ptr = int(buf.data_ptr())
        reg = agent.register_memory([(ptr, count, 0, "")], "VRAM")
        if reg is None or reg is False:
            raise RuntimeError("NIXL registration failed for a logical rank region")
        tables.append([ptr + i * PAGE_COUNT * STRIDE for i in range(count // (PAGE_COUNT * STRIDE))])
        regions.append((buf, host, ptr, count))
    torch.cuda.synchronize()
    return regions, tables


def fill_source_case(torch, regions, case_i):
    import numpy as np
    for logical_rank, (buf, _initial, _ptr, _size) in enumerate(regions):
        host = bytearray(buf.numel())
        for region in range(190):
            for page in range(PAGE_COUNT):
                off = (region * PAGE_COUNT + page) * STRIDE
                host[off:off + STRIDE] = pattern(logical_rank, case_i, region, page)
        buf.copy_(torch.from_numpy(np.frombuffer(host, dtype=np.uint8).copy()).to("cuda:0"))
    torch.cuda.synchronize()


def rank_run(rank: int, art: Path, exchange: Path):
    import torch
    import numpy as np
    from nixl._api import nixl_agent, nixl_agent_config, nixl_thread_sync_t
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("require exactly one visible CUDA GPU per process")
    torch.cuda.set_device(0)
    prop = torch.cuda.get_device_properties(0)
    gpu_uuid = str(getattr(prop, "uuid", ""))
    if not gpu_uuid:
        raise RuntimeError("Torch did not provide a GPU UUID")
    ib = base.active_ib_devices()
    if not ib or os.environ.get("UCX_NET_DEVICES") != ",".join(ib):
        raise RuntimeError("UCX_NET_DEVICES does not match active worker IB autodetection")
    if os.environ.get("UCX_POSIX_USE_PROC_LINK") != "n":
        raise RuntimeError("UCX_POSIX_USE_PROC_LINK must be n")
    methods, source_hashes = source_bundle()
    private = exchange / ".descriptor-private"
    private.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(private, 0o700)
    start_path = private / "start.json"
    if rank == 0:
        if start_path.exists():
            raise RuntimeError("exchange directory is stale; use an empty per-job path")
        base.atomic_json(start_path, {"start_epoch_s": time.time()})
    base.wait_until(start_path.exists, time.time() + 30, "common run start marker")
    deadline = float(json.loads(start_path.read_text())["start_epoch_s"]) + DEADLINE_S
    cfg = nixl_agent_config(backends=[], num_threads=8,
                            sync_mode=nixl_thread_sync_t.NIXL_THREAD_SYNC_STRICT)
    agent = nixl_agent(f"descriptor-{rank}-{uuid.uuid4()}", cfg)
    agent.create_backend("UCX", {"num_threads": "8"})
    regions, tables = alloc_regions(torch, agent, rank, CASES)
    metadata = agent.get_agent_metadata()
    (private / f"agent-{rank}.bin").write_bytes(metadata)
    local = {"rank": rank, "name": agent.name, "gpu_uuid": gpu_uuid,
             "gpu_id": 0, "ptr_tables": tables,
             "region_bounds": [[p, n] for _, _, p, n in regions],
             "metadata_sha256": hashlib.sha256(metadata).hexdigest(),
             "metadata_len": len(metadata)}
    base.atomic_json(private / f"rank-{rank}.json", local)
    other_path = private / f"rank-{1-rank}.json"
    base.wait_until(other_path.exists, deadline, "peer descriptor table")
    peer = json.loads(other_path.read_text())
    peer_meta = (private / f"agent-{1-rank}.bin").read_bytes()
    if (len(peer_meta) != peer["metadata_len"]
            or hashlib.sha256(peer_meta).hexdigest() != peer["metadata_sha256"]):
        raise RuntimeError("peer metadata hash mismatch")
    agent.add_remote_agent(peer_meta)
    identity = base._source_identity()
    base.atomic_json(private / f"ready-{rank}.json", {
        "host": socket.gethostname(), "gpu_uuid": gpu_uuid, **identity, **source_hashes})
    base.wait_until(lambda: all((private / f"ready-{i}.json").exists() for i in (0, 1)),
                    deadline, "both source-pinned agents ready")
    ready = [json.loads((private / f"ready-{i}.json").read_text()) for i in (0, 1)]
    if ready[0]["host"] == ready[1]["host"] or ready[0]["gpu_uuid"] == ready[1]["gpu_uuid"]:
        raise RuntimeError("the two agents must be on distinct hosts and GPUs")
    for key in (*identity.keys(), *source_hashes.keys()):
        if ready[0].get(key) != ready[1].get(key):
            raise RuntimeError(f"rank source identity mismatch for {key}")

    rows = []
    if rank == 0:
        helper = __import__("sglang.srt.disaggregation.common.staging_buffer",
                            fromlist=["compute_head_slice_params"]).compute_head_slice_params
        # Bootstrap's GQA topology routes consecutive decoder ranks to each
        # source head; the staging helper validates whole-head offsets only.
        replicas = 8 // 4
        mapping = [(dst_rank // replicas, dst_rank) for dst_rank in range(8)]
        if len(set(mapping)) != 8:
            raise RuntimeError("logical rank mapping is not eight unique pairs")
        source_counts = {src: sum(pair[0] == src for pair in mapping) for src in range(4)}
        if source_counts != {0: 2, 1: 2, 2: 2, 3: 2}:
            raise RuntimeError(f"GQA route must replicate each of four KV heads twice: {source_counts}")
        for case_i, (case, src_layers, dst_layers) in enumerate(CASES):
            fill_source_case(torch, regions, case_i)
            for src_rank, dst_rank in mapping:
                src_ptrs = tables[src_rank][:2*src_layers]
                dst_ptrs = peer["ptr_tables"][dst_rank][:2*dst_layers]
                src_obj = SimpleNamespace(engine_rank=src_rank, kv_data_ptrs=src_ptrs,
                    kv_item_lens=[STRIDE] * len(src_ptrs), kv_data_lens=[STRIDE*PAGE_COUNT]*len(src_ptrs),
                    page_size=PAGE_SIZE, total_kv_head_num=4, kv_head_num=1,
                    prefill_start_layer=0, gpu_id=0)
                dst_obj = SimpleNamespace(decode_tp_size=8, decode_tp_rank=dst_rank,
                    dst_kv_item_len=STRIDE, dst_kv_item_lens=[STRIDE]*len(dst_ptrs),
                    dst_kv_ptrs=dst_ptrs, gpu_id=0)
                # Validate the helper's actual whole-head result for this pair.
                hs, nh, _, _ = helper(4, 8, src_rank, dst_rank, 4)
                if (hs, nh) != (0, 1):
                    raise RuntimeError(f"unexpected partial/nonlocal head slice: {hs}, {nh}")
                mgr = SimpleNamespace(kv_args=src_obj, attn_tp_size=4)
                mgr.get_mha_kv_ptrs_with_pp = MethodType(methods["get_mha_kv_ptrs_with_pp"], mgr)
                mgr._init_hetero_tp_prep_handle = MethodType(methods["_init_hetero_tp_prep_handle"], mgr)
                mgr.send_kvcache_slice = MethodType(methods["send_kvcache_slice"], mgr)
                mgr.agent = guarded_agent(agent, [(p, n) for _, _, p, n in regions],
                                          peer["region_bounds"])
                peer_name = peer["name"]
                mgr._init_hetero_tp_prep_handle(peer_name, dst_obj)
                plan = mgr._ondemand_slice_plans[peer_name]
                if plan["src_stride"] != plan["dst_stride"] or plan["length"] != STRIDE:
                    raise RuntimeError("fixture requires equal whole-head strides")
                if plan["src_offset"] != 0 or plan["dst_offset"] != 0:
                    raise RuntimeError("fixture only accepts whole local KV-head offsets")
                if (len(set(src_obj.kv_item_lens)) != 1
                        or len(set(dst_obj.dst_kv_item_lens)) != 1
                        or src_obj.kv_item_lens[0] != dst_obj.dst_kv_item_lens[0]):
                    raise RuntimeError("fixture requires uniform equal source/destination item lengths")
                if len(plan["src_ptrs"]) != 2*src_layers or len(plan["dst_ptrs"]) != 2*src_layers:
                    raise RuntimeError("source-faithful layer selection returned unexpected count")
                # Check every generated descriptor against registered source and peer bounds.
                src_tokens = np.array(SRC_PAGES, dtype=np.uint64)
                dst_tokens = np.array(DST_PAGES, dtype=np.uint64)
                for sp, dp in zip(plan["src_ptrs"], plan["dst_ptrs"]):
                    for si, di in zip(src_tokens, dst_tokens):
                        check_desc_bounds([(int(sp)+int(si)*STRIDE, STRIDE, 0)], *regions[src_rank][2:], "source")
                        check_desc_bounds([(int(dp)+int(di)*STRIDE, STRIDE, 0)], *peer["region_bounds"][dst_rank], "destination")
                base.wait_until((private / f"ready-case-{case_i}-{dst_rank}.json").exists,
                                deadline, f"receiver case {case}/{dst_rank} ready")
                handle = send_slice(mgr, peer_name, SRC_PAGES, DST_PAGES,
                                    f"case-{case_i}-{dst_rank}")
                wait_done(agent, handle, deadline)
                row = {"case": case, "src_layers": src_layers, "dst_layers": dst_layers,
                       "src_rank": src_rank, "dst_rank": dst_rank,
                       "src_pages": list(SRC_PAGES), "dst_pages": list(DST_PAGES),
                       "state": "DONE", "descriptor_pairs": len(plan["src_ptrs"])*2}
                rows.append(row)
                base.atomic_json(private / f"done-{case_i}-{dst_rank}.json", row)
                base.wait_until((private / f"verified-{case_i}-{dst_rank}.json").exists,
                                deadline, f"receiver byte verification {case}/{dst_rank}")
    else:
        for case_i, (case, src_layers, dst_layers) in enumerate(CASES):
            for dst_rank in range(8):
                if dst_rank % 8 != dst_rank:
                    continue
                base.atomic_json(private / f"ready-case-{case_i}-{dst_rank}.json", {"ready": True})
                base.wait_until((private / f"done-{case_i}-{dst_rank}.json").exists,
                                deadline, f"sender completion {case}/{dst_rank}")
                done = json.loads((private / f"done-{case_i}-{dst_rank}.json").read_text())
                if done.get("state") != "DONE":
                    raise RuntimeError("sender did not observe NIXL DONE")
                # Independently construct exact full-region expected bytes.
                buf, _initial, _ptr, _size = regions[dst_rank]
                actual = buf.detach().cpu().numpy().tobytes()
                src_rank = int(done["src_rank"])
                if (done.get("case") != case or done.get("src_layers") != src_layers
                        or done.get("dst_layers") != dst_layers or src_rank != dst_rank // 2
                        or done.get("src_pages") != list(SRC_PAGES)
                        or done.get("dst_pages") != list(DST_PAGES)):
                    raise RuntimeError("sender case, GQA route, or page identity mismatch")
                expected = expected_destination(case_i, src_rank, src_layers)
                actual_sha = hashlib.sha256(actual).hexdigest()
                expected_sha = hashlib.sha256(expected).hexdigest()
                if actual != expected or actual_sha != expected_sha:
                    raise RuntimeError(f"{case}/{dst_rank} GPU destination bytes or untouched sentinels mismatch")
                rows.append({"case": case, "src_layers": src_layers, "dst_layers": dst_layers,
                             "src_rank": src_rank, "dst_rank": dst_rank,
                             "src_pages": list(SRC_PAGES), "dst_pages": list(DST_PAGES),
                             "state": "verified", "gpu_sha256": actual_sha,
                             "expected_sha256": expected_sha})
                base.atomic_json(private / f"verified-{case_i}-{dst_rank}.json", {"verified": True})
    if rank == 0:
        base.atomic_json(art / "rank0-result.json", {"schema": "nixl-descriptor-v1", "status": "complete",
            "rank": 0, "host": socket.gethostname(), "gpu_uuid": gpu_uuid,
            "agent_id": agent.name, "peer_id": peer["name"],
            "metadata_sha256": hashlib.sha256(metadata).hexdigest(),
            "peer_metadata_sha256": peer["metadata_sha256"],
            "source_hashes": source_hashes, "runtime_identity": identity, "cases": rows})
    else:
        base.atomic_json(art / "rank1-result.json", {"schema": "nixl-descriptor-v1", "status": "complete",
            "rank": 1, "host": socket.gethostname(), "gpu_uuid": gpu_uuid,
            "agent_id": agent.name, "peer_id": peer["name"],
            "metadata_sha256": hashlib.sha256(metadata).hexdigest(),
            "peer_metadata_sha256": peer["metadata_sha256"],
            "source_hashes": source_hashes, "runtime_identity": identity, "cases": rows})


def check(art: Path):
    try:
        a, b = [json.loads((art / f"rank{i}-result.json").read_text()) for i in (0, 1)]
        result_keys = {"schema", "rank", "status", "host", "gpu_uuid", "agent_id", "peer_id",
                       "metadata_sha256", "peer_metadata_sha256", "source_hashes", "runtime_identity", "cases"}
        if any(x.keys() != result_keys for x in (a, b)):
            raise ValueError("rank result fields differ from the pointer-free schema")
        if (any(x.get("schema") != "nixl-descriptor-v1" for x in (a, b))
                or [x.get("rank") for x in (a, b)] != [0, 1]
                or any(x.get("status") != "complete" for x in (a, b))):
            raise ValueError("both complete rank results are required")
        if (not all(isinstance(x.get("host"), str) and x["host"] for x in (a, b))
                or not all(isinstance(x.get("gpu_uuid"), str) and x["gpu_uuid"] for x in (a, b))
                or a.get("host") == b.get("host") or a["gpu_uuid"] == b["gpu_uuid"]):
            raise ValueError("results must identify distinct hosts and GPU UUIDs")
        if a.get("source_hashes") != b.get("source_hashes") or a.get("runtime_identity") != b.get("runtime_identity"):
            raise ValueError("source identities differ between ranks")
        if a.get("runtime_identity", {}).get("runtime_source_sha256") != SOURCE_SHA:
            raise ValueError("patched NIXL runtime source is not the pinned build")
        if a.get("runtime_identity", {}).get("nixl_api_sha256") != base.EXPECTED_NIXL_API_SHA256:
            raise ValueError("installed NIXL Python API is not the pinned build")
        identity = a.get("runtime_identity", {})
        identity_keys = {"runtime_source_sha256", "nixl_api_sha256", "nixl_bindings_sha256",
                         "torch_file_sha256", "nixl_api_path", "nixl_bindings_path",
                         "torch_path", "nixl_version", "torch_version"}
        if identity.keys() != identity_keys or any(not isinstance(identity[k], str) or not identity[k]
                                                     for k in identity_keys):
            raise ValueError("runtime source identity is incomplete")
        sha_ok = lambda value: (isinstance(value, str) and len(value) == 64
                                and all(c in "0123456789abcdef" for c in value))
        for key in ("runtime_source_sha256", "nixl_api_sha256", "nixl_bindings_sha256", "torch_file_sha256"):
            if not sha_ok(identity[key]):
                raise ValueError(f"invalid runtime source hash: {key}")
        if a.get("source_hashes", {}).get("common_conn_sha256") != COMMON_SHA:
            raise ValueError("common connection helper source is not the pinned build")
        if a.get("source_hashes", {}).get("nixl_conn_sha256") != SOURCE_SHA:
            raise ValueError("patched NIXL method source hash mismatch")
        if a.get("source_hashes", {}).get("staging_buffer_sha256") != STAGING_SHA:
            raise ValueError("staging helper source hash mismatch")
        source_keys = {"nixl_conn_sha256", "common_conn_sha256", "staging_buffer_sha256",
                       "compute_head_slice_params_sha256"}
        if a.get("source_hashes", {}).keys() != source_keys:
            raise ValueError("source hash manifest keys differ from the pinned contract")
        if any(not sha_ok(v) for v in a.get("source_hashes", {}).values()):
            raise ValueError("source hash manifest is incomplete")
        if (not a.get("agent_id") or not b.get("agent_id") or a["agent_id"] == b["agent_id"]
                or a.get("peer_id") != b.get("agent_id") or b.get("peer_id") != a.get("agent_id")
                or a.get("peer_metadata_sha256") != b.get("metadata_sha256")
                or b.get("peer_metadata_sha256") != a.get("metadata_sha256")):
            raise ValueError("peer agent or metadata identity mismatch")
        if any(not sha_ok(x.get(key)) for x in (a, b)
               for key in ("metadata_sha256", "peer_metadata_sha256")):
            raise ValueError("peer metadata hash is malformed")
        sent, received = a.get("cases", []), b.get("cases", [])
        if len(sent) != 24 or len(received) != 24:
            raise ValueError("expected exactly 24 sender and receiver case rows")
        send_keys = {"case", "src_layers", "dst_layers", "src_rank", "dst_rank", "src_pages",
                     "dst_pages", "state", "descriptor_pairs"}
        receive_keys = {"case", "src_layers", "dst_layers", "src_rank", "dst_rank", "src_pages",
                        "dst_pages", "state", "gpu_sha256", "expected_sha256"}
        if any(r.keys() != send_keys for r in sent) or any(r.keys() != receive_keys for r in received):
            raise ValueError("case rows differ from the pointer-free result schema")
        if any(r.get("state") != "DONE" for r in sent) or any(r.get("state") != "verified" for r in received):
            raise ValueError("all transfers must reach DONE and all destinations verify")
        keys = {(case, d) for case, _, _ in CASES for d in range(8)}
        sent_keys = {(r.get("case"), r.get("dst_rank")) for r in sent}
        recv_keys = {(r.get("case"), r.get("dst_rank")) for r in received}
        if sent_keys != keys or recv_keys != keys:
            raise ValueError("case/rank mapping is incomplete or duplicated")
        sent_map = {(r["case"], r["dst_rank"]): r["src_rank"] for r in sent}
        recv_map = {(r["case"], r["dst_rank"]): r["src_rank"] for r in received}
        if sent_map != recv_map or any(not (0 <= src < 4) for src in sent_map.values()):
            raise ValueError("receiver mapping does not match helper-derived sender pairs")
        for case, src_layers, dst_layers in CASES:
            for dst in range(8):
                if sent_map[(case, dst)] != dst // 2:
                    raise ValueError("GQA source rank does not match decoder-rank replication")
        for r in sent:
            layers = next(n for name, n, _ in CASES if name == r["case"])
            dst_layers = next(n for name, _, n in CASES if name == r["case"])
            if r.get("src_layers") != layers or r.get("dst_layers") != dst_layers:
                raise ValueError("sender case layer identity mismatch")
            if r.get("src_pages") != list(SRC_PAGES) or r.get("dst_pages") != list(DST_PAGES):
                raise ValueError("sender page mapping mismatch")
            if r.get("descriptor_pairs") != layers * 4:
                raise ValueError("unexpected number of per-page descriptor pairs")
        for r in received:
            src_layers = next(n for name, n, _ in CASES if name == r["case"])
            dst_layers = next(n for name, _, n in CASES if name == r["case"])
            if r.get("src_layers") != src_layers or r.get("dst_layers") != dst_layers:
                raise ValueError("receiver case layer identity mismatch")
            if r.get("src_pages") != list(SRC_PAGES) or r.get("dst_pages") != list(DST_PAGES):
                raise ValueError("receiver page mapping mismatch")
            value = r.get("gpu_sha256", "")
            case_i = next(i for i, (name, _, _) in enumerate(CASES) if name == r["case"])
            expected = hashlib.sha256(expected_destination(case_i, r["src_rank"], src_layers)).hexdigest()
            if r.get("expected_sha256") != expected or not sha_ok(value) or value != expected:
                raise ValueError("destination GPU hash differs from the independently expected layout")
        return {"status": "pass", "transfers": 24, "scope": "source-extracted SGLang NIXL KV descriptors; no model or inference"}
    except Exception as exc:
        return {"status": "fail", "reason": f"{type(exc).__name__}: {exc}"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rank", type=int, choices=(0, 1)); p.add_argument("--art", type=Path)
    p.add_argument("--exchange-dir", type=Path); p.add_argument("--check", action="store_true")
    a = p.parse_args()
    if a.art is None: p.error("--art is required")
    if a.check:
        result = check(a.art); print(json.dumps(result, sort_keys=True)); return 0 if result["status"] == "pass" else 1
    if a.rank is None or a.exchange_dir is None: p.error("rank mode requires --rank and --exchange-dir")
    a.art.mkdir(parents=True, exist_ok=True)
    try:
        rank_run(a.rank, a.art, a.exchange_dir)
    except Exception as exc:
        base.atomic_json(a.art / f"rank{a.rank}-result.json", {"schema": "nixl-descriptor-v1", "status": "failed",
            "rank": a.rank, "host": socket.gethostname(), **failure_details(exc)})
        print(f"descriptor probe failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
