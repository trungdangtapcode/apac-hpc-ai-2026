#!/usr/bin/env python3
"""CPU-only tests of source-extracted pointer selection and fixture arithmetic."""
import sys
import tempfile
import json
import logging
import types
from pathlib import Path
from types import MethodType
from typing import List, Tuple
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
COMMON = HERE / "source/common-conn.py"
NIXL = HERE / "nixl-conn.py"
STAGING = HERE / "staging_buffer.py"
sys.path.insert(0, str(HERE))
import descriptor as d


def test_pointer_selection():
    assert d.digest(COMMON) == d.COMMON_SHA
    method = d.extract(COMMON, "get_mha_kv_ptrs_with_pp", "CommonKVManager",
                       {"List": List, "Tuple": Tuple})
    manager = type("Manager", (), {"get_mha_kv_ptrs_with_pp": method})()
    manager.kv_args = type("Args", (), {"prefill_start_layer": 0})()
    for src_layers, dst_layers, expected_k, expected_v in (
        (94, 94, list(range(94)), list(range(94, 188))),
        (94, 95, list(range(94)), list(range(94, 188))),
        (95, 95, list(range(95)), list(range(95, 190))),
    ):
        src, dst = list(range(2*src_layers)), list(range(2*dst_layers))
        sk, sv, dk, dv, layers = method(manager, src, dst)
        assert layers == src_layers and sk == expected_k and sv == expected_v
        assert dk == expected_k and dv == expected_v, (src_layers, dst_layers, dk, dv)


def test_real_nixl_helpers_and_peer_name():
    assert d.digest(NIXL) == d.SOURCE_SHA
    device_id = d.extract(NIXL, "_nixl_device_id")
    assert device_id("VRAM", 3) == 3 and device_id("HOST", 3) == 0

    class Vector:
        def __init__(self, values): self.values = list(values)
        def __len__(self): return len(self.values)
        def __getitem__(self, key):
            if key == (slice(None), None): return Column(self.values)
            if key == (None, slice(None)): return Row(self.values)
            return Vector(self.values[key])
        def ravel(self): return self
        def __iter__(self): return iter(self.values)

    class Column:
        def __init__(self, values): self.values = list(values)
        def __mul__(self, value): return Column([x*value for x in self.values])
        def __add__(self, other):
            if isinstance(other, Row):
                return Matrix([[x+y for y in other.values] for x in self.values])
            return Column([x+other for x in self.values])

    class Row:
        def __init__(self, values): self.values = list(values)
        def __mul__(self, value): return Row([x*value for x in self.values])

    class Matrix:
        def __init__(self, rows): self.rows = rows
        def __add__(self, value): return Matrix([[x+value for x in row] for row in self.rows])
        def ravel(self): return Vector([x for row in self.rows for x in row])

    class NumpyStub:
        uint64 = int
        @staticmethod
        def asarray(values, dtype=None): return Vector(values)
        @staticmethod
        def arange(count, dtype=None): return Vector(range(count))
        @staticmethod
        def full(count, value, dtype=None): return Vector([value]*count)
        @staticmethod
        def tile(values, count): return Vector(list(values)*count)
        @staticmethod
        def full_like(values, value): return Vector([value]*len(values))
        @staticmethod
        def column_stack(cols): return [list(row) for row in zip(*(c.values for c in cols))]

    np = NumpyStub
    send = d.extract(NIXL, "send_kvcache_slice", "NixlKVManager",
                     {"np": np, "_nixl_device_id": device_id})

    class Agent:
        remote = {"registered-peer"}
        def get_xfer_descs(self, rows, kind):
            return (rows, kind)
        def initialize_xfer(self, op, src, dst, peer, notif):
            assert op == "WRITE" and peer in self.remote
            assert len(src[0]) == len(dst[0]) == 1
            return "handle"
        def transfer(self, handle):
            assert handle == "handle"
            return "IN PROGRESS"

    manager = type("Manager", (), {})()
    manager.send_kvcache_slice = MethodType(send, manager)
    manager.kv_args = type("Args", (), {"page_size": 1, "gpu_id": 0})()
    manager.agent = Agent()
    manager._ondemand_slice_plans = {"registered-peer": {
        "src_ptrs": Vector([0x100000]),
        "dst_ptrs": Vector([0x200000]),
        "src_stride": 256, "dst_stride": 256, "length": 128,
        "src_offset": 0, "dst_offset": 0,
        "src_mem_kind": "VRAM", "dst_mem_kind": "VRAM", "dst_gpu_id": 0}}
    assert d.send_slice(manager, "registered-peer", [1], [0], "case-0") == "handle"
    try:
        d.send_slice(manager, "case-label-is-not-peer", [1], [0], "case-0")
    except KeyError:
        pass
    else:
        raise AssertionError("case label was accepted as a registered peer name")


def test_pinned_head_helper_and_gqa_routes():
    helper = d.extract(STAGING, "compute_head_slice_params", globs={"Tuple": Tuple})
    assert d.digest(STAGING) == d.STAGING_SHA
    for src in range(4):
        for dst in range(8):
            assert helper(4, 8, src, dst, 4) == (0, 1, 0, 1)
    routes = [(dst // (8 // 4), dst) for dst in range(8)]
    assert routes == [(0, 0), (0, 1), (1, 2), (1, 3),
                      (2, 4), (2, 5), (3, 6), (3, 7)]


def test_actual_init_geometries_and_routes():
    class Array(list):
        def tolist(self): return list(self)
    np = types.SimpleNamespace(uint64=int, asarray=lambda values, dtype=None: Array(values))
    helper = d.extract(STAGING, "compute_head_slice_params", globs={"Tuple": Tuple})
    common_get = d.extract(COMMON, "get_mha_kv_ptrs_with_pp", "CommonKVManager",
                           {"List": List, "Tuple": Tuple})
    init = d.extract(NIXL, "_init_hetero_tp_prep_handle", "NixlKVManager",
                     {"np": np, "logger": logging.getLogger("cpu-test")})
    staging_module = types.ModuleType("sglang.srt.disaggregation.common.staging_buffer")
    staging_module.compute_head_slice_params = helper
    modules = {"sglang": types.ModuleType("sglang"),
               "sglang.srt": types.ModuleType("sglang.srt"),
               "sglang.srt.disaggregation": types.ModuleType("sglang.srt.disaggregation"),
               "sglang.srt.disaggregation.common": types.ModuleType("sglang.srt.disaggregation.common"),
               "sglang.srt.disaggregation.common.staging_buffer": staging_module}
    for name in ("sglang", "sglang.srt", "sglang.srt.disaggregation",
                 "sglang.srt.disaggregation.common"):
        modules[name].__path__ = []
    calls = 0
    with patch.dict(sys.modules, modules):
        for case, src_layers, dst_layers in d.CASES:
            for dst_rank in range(8):
                src_rank = dst_rank // 2
                assert helper(4, 8, src_rank, dst_rank, 4) == (0, 1, 0, 1)
                src_ptrs = [0x1000000 + src_rank*0x100000 + i*1024
                            for i in range(2*src_layers)]
                dst_ptrs = [0x4000000 + dst_rank*0x100000 + i*1024
                            for i in range(2*dst_layers)]
                src_args = types.SimpleNamespace(engine_rank=src_rank,
                    kv_data_ptrs=src_ptrs, kv_item_lens=[256]*len(src_ptrs),
                    kv_data_lens=[1024]*len(src_ptrs), page_size=1,
                    total_kv_head_num=4, kv_head_num=1, prefill_start_layer=0, gpu_id=0)
                dst_args = types.SimpleNamespace(decode_tp_size=8, decode_tp_rank=dst_rank,
                    dst_kv_item_len=256, dst_kv_item_lens=[256]*len(dst_ptrs),
                    dst_kv_ptrs=dst_ptrs, gpu_id=0)
                manager = types.SimpleNamespace(kv_args=src_args, attn_tp_size=4)
                manager.get_mha_kv_ptrs_with_pp = MethodType(common_get, manager)
                manager._init_hetero_tp_prep_handle = MethodType(init, manager)
                manager._init_hetero_tp_prep_handle("registered-peer", dst_args)
                plan = manager._ondemand_slice_plans["registered-peer"]
                assert len(plan["src_ptrs"]) == len(plan["dst_ptrs"]) == 2*src_layers
                assert plan["src_ptrs"].tolist() == src_ptrs
                assert plan["dst_ptrs"].tolist() == dst_ptrs[:2*src_layers]
                assert (plan["src_stride"], plan["dst_stride"], plan["length"],
                        plan["src_offset"], plan["dst_offset"]) == (256, 256, 256, 0, 0)
                assert set(manager._ondemand_slice_plans) == {"registered-peer"}
                calls += 1
    assert calls == 24


def test_bounds_patterns_and_sentinels():
    base, size = 0x100000, 4 * d.STRIDE
    d.check_desc_bounds([(base + d.STRIDE, d.STRIDE, 0)], base, size, "cpu fixture")
    for bad in ((base - 1, 1, 0), (base + size - 1, 2, 0)):
        try:
            d.check_desc_bounds([bad], base, size, "cpu fixture")
        except RuntimeError:
            pass
        else:
            raise AssertionError(f"out-of-range descriptor accepted: {bad}")
    assert d.pattern(0, 0, 1, 1) != d.pattern(1, 0, 1, 1)
    assert d.pattern(0, 0, 1, 1) != d.pattern(0, 0, 1, 3)
    initial = bytearray([0xA5] * (2 * 4 * d.STRIDE))
    expected = bytearray(initial)
    for region in range(2):
        for src_page, dst_page in zip(d.SRC_PAGES, d.DST_PAGES):
            off = (region * d.PAGE_COUNT + dst_page) * d.STRIDE
            expected[off:off+d.STRIDE] = d.pattern(2, 1, region, src_page)
    assert expected != initial
    for page in (1, 3):
        for region in range(2):
            off = (region * d.PAGE_COUNT + page) * d.STRIDE
            assert expected[off:off+d.STRIDE] == bytes([0xA5]) * d.STRIDE
    full = d.expected_destination(0, 2, 94)
    assert len(full) == 190 * 4 * 256
    for region in range(190):
        for page in (1, 3):
            off = (region * 4 + page) * 256
            assert full[off:off+256] == bytes([0xA5]) * 256
        if region >= 188:
            for page in (0, 2):
                off = (region * 4 + page) * 256
                assert full[off:off+256] == bytes([0xA5]) * 256


def test_semantic_check():
    identity = {"runtime_source_sha256": d.SOURCE_SHA,
                "nixl_api_sha256": d.base.EXPECTED_NIXL_API_SHA256,
                "nixl_bindings_sha256": "d"*64, "torch_file_sha256": "e"*64,
                "nixl_api_path": "/p/nixl-api", "nixl_bindings_path": "/p/nixl-bindings",
                "torch_path": "/p/torch", "nixl_version": "1", "torch_version": "2"}
    hashes = {"nixl_conn_sha256": d.SOURCE_SHA, "common_conn_sha256": d.COMMON_SHA,
              "staging_buffer_sha256": d.STAGING_SHA, "compute_head_slice_params_sha256": "b"*64}
    sent, recv = [], []
    for case, src_layers, dst_layers in d.CASES:
        case_i = next(i for i, row in enumerate(d.CASES) if row[0] == case)
        for dst in range(8):
            src = dst // 2
            sent.append({"case": case, "src_layers": src_layers, "dst_layers": dst_layers,
                         "src_rank": src, "dst_rank": dst, "state": "DONE",
                         "src_pages": list(d.SRC_PAGES), "dst_pages": list(d.DST_PAGES),
                         "descriptor_pairs": src_layers*4})
            expected_sha = __import__("hashlib").sha256(
                d.expected_destination(case_i, src, src_layers)).hexdigest()
            recv.append({"case": case, "src_layers": src_layers, "dst_layers": dst_layers,
                         "src_rank": src, "dst_rank": dst,
                         "src_pages": list(d.SRC_PAGES), "dst_pages": list(d.DST_PAGES),
                         "state": "verified", "gpu_sha256": expected_sha,
                         "expected_sha256": expected_sha})
    rank0 = {"schema": "nixl-descriptor-v1", "rank": 0, "status": "complete", "host": "h0", "gpu_uuid": "g0",
             "agent_id": "a0", "peer_id": "a1", "metadata_sha256": "0"*64,
             "peer_metadata_sha256": "1"*64, "source_hashes": hashes,
             "runtime_identity": identity, "cases": sent}
    rank1 = {"schema": "nixl-descriptor-v1", "rank": 1, "status": "complete", "host": "h1", "gpu_uuid": "g1",
             "agent_id": "a1", "peer_id": "a0", "metadata_sha256": "1"*64,
             "peer_metadata_sha256": "0"*64, "source_hashes": hashes,
             "runtime_identity": identity, "cases": recv}
    with tempfile.TemporaryDirectory() as tmp:
        art = Path(tmp)
        for i, row in enumerate((rank0, rank1)):
            (art / f"rank{i}-result.json").write_text(json.dumps(row))
        assert d.check(art)["status"] == "pass"
        bad_hash = [dict(row) for row in recv]
        bad_hash[0]["gpu_sha256"] = "f"*64
        bad_hash[0]["expected_sha256"] = "f"*64  # A matching pair of false hashes must also fail.
        (art / "rank1-result.json").write_text(json.dumps({**rank1, "cases": bad_hash}))
        assert d.check(art)["status"] == "fail"
        swapped_sent, swapped_recv = [dict(row) for row in sent], [dict(row) for row in recv]
        for rows in (swapped_sent, swapped_recv):
            for row in rows:
                if row["case"] == d.CASES[0][0] and row["dst_rank"] == 0:
                    row["src_rank"] = 1
                elif row["case"] == d.CASES[0][0] and row["dst_rank"] == 2:
                    row["src_rank"] = 0
        (art / "rank0-result.json").write_text(json.dumps({**rank0, "cases": swapped_sent}))
        (art / "rank1-result.json").write_text(json.dumps({**rank1, "cases": swapped_recv}))
        assert d.check(art)["status"] == "fail"
        (art / "rank1-result.json").write_text(json.dumps({**rank1, "cases": recv[:-1]}))
        assert d.check(art)["status"] == "fail"


if __name__ == "__main__":
    test_pointer_selection()
    test_real_nixl_helpers_and_peer_name()
    test_pinned_head_helper_and_gqa_routes()
    test_actual_init_geometries_and_routes()
    test_bounds_patterns_and_sentinels()
    test_semantic_check()
    print("CPU source/helper/range/sentinel tests passed; mock-agent call path only, no GPU/backend claim")
