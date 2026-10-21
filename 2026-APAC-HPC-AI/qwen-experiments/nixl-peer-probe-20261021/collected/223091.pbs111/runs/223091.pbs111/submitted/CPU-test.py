#!/usr/bin/env python3
"""CPU-only tests for NIXL call protocol and result semantics; no GPU claim."""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import itertools
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("nixl_peer_probe", HERE / "probe.py")
probe = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(probe)


class CpuBuffer:
    def __init__(self, size: int):
        self.data = bytearray(size)
        self.ptr = ctypes.addressof(ctypes.c_char.from_buffer(self.data))

    def data_ptr(self):
        return self.ptr


class MockArray(list):
    dtype = "uint64"
    shape = (1, 3)

    def copy(self):
        return MockArray([list(row) for row in self])


class MockNumpy:
    uint64 = "uint64"

    @staticmethod
    def asarray(value, dtype=None):
        assert dtype == "uint64"
        return MockArray([list(row) for row in value])


class MockAgent:
    def __init__(self, memory: dict[int, bytearray]):
        self.memory = memory
        self.calls = []
        self.request = None

    def get_xfer_descs(self, array, memory_kind):
        self.calls.append(("get_xfer_descs", memory_kind, array.copy()))
        assert memory_kind == "VRAM"
        assert array.dtype == "uint64" and array.shape == (1, 3)
        return array.copy()

    def initialize_xfer(self, operation, source, destination, peer, notification):
        self.calls.append(("initialize_xfer", operation, peer, notification))
        assert operation == "WRITE"
        self.request = (source, destination)
        return "mock-handle"

    def transfer(self, handle):
        self.calls.append(("transfer", handle))
        assert handle == "mock-handle"
        src_ptr, size = int(self.request[0][0][0]), int(self.request[0][0][1])
        dst_ptr = int(self.request[1][0][0])
        payload = ctypes.string_at(src_ptr, size)
        ctypes.memmove(dst_ptr, payload, size)
        return "INPROGRESS"

    def check_xfer_state(self, handle):
        self.calls.append(("check_xfer_state", handle))
        return "DONE"


def make_valid_results():
    ranks = []
    for rank in (0, 1):
        ranks.append({
            "rank": rank, "status": "complete", "sent": [], "received": [],
            "host": f"node-{rank}", "gpu_uuid": f"GPU-{rank}",
            "agent_id": f"agent-{rank}", "peer_id": f"agent-{1-rank}",
            "metadata_bytes": 100 + rank, "metadata_sha256": f"md-{rank}",
            "peer_metadata_bytes": 100 + (1-rank),
            "peer_metadata_sha256": f"md-{1-rank}",
            "runtime_source_sha256": "runtime-sha",
            "nixl_api_sha256": "api-sha",
            "nixl_bindings_sha256": "bindings-sha",
        })
    sequence = 0
    for size in probe.SIZES:
        for _ in range(probe.REPETITIONS):
            for sender in (0, 1):
                receiver = 1 - sender
                digest = hashlib.sha256(
                    f"mock-pattern-{size}-{sender}-{sequence}".encode("ascii")
                ).hexdigest()
                send = {
                    "sequence": sequence, "sender_rank": sender,
                    "receiver_rank": receiver, "size": size,
                    "expected_sha256": digest, "sha256": digest, "state": "DONE",
                }
                recv = {
                    "sequence": sequence, "sender_rank": sender,
                    "receiver_rank": receiver, "size": size,
                    "expected_sha256": digest, "sha256": digest, "status": "verified",
                }
                ranks[sender]["sent"].append(send)
                ranks[receiver]["received"].append(recv)
                sequence += 1
    return ranks


class ProbeTests(unittest.TestCase):
    def test_transfer_uses_pinned_nixl_write_sequence_and_copies_bytes(self):
        source = CpuBuffer(4096)
        destination = CpuBuffer(4096)
        payload = probe.pattern_bytes(4096, 0, 3)
        source.data[:] = payload
        memory = {source.ptr: source.data, destination.ptr: destination.data}
        agent = MockAgent(memory)
        with patch.dict("sys.modules", {"numpy": MockNumpy}):
            probe.transfer_one(
                agent, "peer-1", source, destination.ptr, 4096, 0, "tx-003",
                time.time() + 2,
            )
        self.assertEqual(destination.data, source.data)
        self.assertEqual([call[0] for call in agent.calls], [
            "get_xfer_descs", "get_xfer_descs", "initialize_xfer",
            "transfer", "check_xfer_state",
        ])
        self.assertEqual(agent.calls[2][1:4], ("WRITE", "peer-1", b"tx-003"))

    def test_expired_epoch_deadline_blocks_before_any_agent_call(self):
        source, destination = CpuBuffer(16), CpuBuffer(16)
        agent = MockAgent({source.ptr: source.data, destination.ptr: destination.data})
        with self.assertRaises(TimeoutError):
            probe.transfer_one(agent, "peer-1", source, destination.ptr, 16, 0,
                               "expired", time.time() - 1)
        self.assertEqual(agent.calls, [])

    def test_pending_transfer_expires_using_same_epoch_clock(self):
        source, destination = CpuBuffer(16), CpuBuffer(16)
        agent = MockAgent({source.ptr: source.data, destination.ptr: destination.data})
        agent.check_xfer_state = lambda handle: "INPROGRESS"
        ticks = itertools.count()
        with patch.dict("sys.modules", {"numpy": MockNumpy}), \
             patch.object(probe.time, "time", side_effect=lambda: 1000 + next(ticks) * 10), \
             patch.object(probe.time, "sleep", return_value=None):
            with self.assertRaises(TimeoutError):
                probe.transfer_one(agent, "peer-1", source, destination.ptr, 16, 0,
                                   "bounded", 2000)

    def test_result_gate_accepts_complete_80_row_bidirectional_evidence(self):
        rank0, rank1 = make_valid_results()
        self.assertEqual(probe.result_rows_valid(rank0, rank1),
                         (True, "80 transfers completed with matching GPU byte hashes"))

    def test_result_gate_rejects_checksum_mismatch(self):
        rank0, rank1 = make_valid_results()
        rank1["received"][0]["sha256"] = "0" * 64
        passed, reason = probe.result_rows_valid(rank0, rank1)
        self.assertFalse(passed)
        self.assertIn("checksum mismatch", reason)

    def test_result_gate_rejects_missing_or_duplicate_rows(self):
        rank0, rank1 = make_valid_results()
        rank0["sent"].pop()
        passed, reason = probe.result_rows_valid(rank0, rank1)
        self.assertFalse(passed)
        self.assertIn("exactly 40", reason)
        rank0, rank1 = make_valid_results()
        rank0["sent"][0] = dict(rank0["sent"][1])
        passed, reason = probe.result_rows_valid(rank0, rank1)
        self.assertFalse(passed)
        self.assertIn("duplicate", reason)

    def test_result_gate_rejects_non_done_and_non_verified_rows(self):
        rank0, rank1 = make_valid_results()
        rank0["sent"][0]["state"] = "ERR"
        passed, reason = probe.result_rows_valid(rank0, rank1)
        self.assertFalse(passed)
        self.assertIn("non-DONE", reason)
        rank0, rank1 = make_valid_results()
        rank1["received"][0]["status"] = "failed"
        passed, reason = probe.result_rows_valid(rank0, rank1)
        self.assertFalse(passed)
        self.assertIn("unverified", reason)

    def test_result_gate_rejects_same_node_gpu_or_nonreciprocal_peer_identity(self):
        rank0, rank1 = make_valid_results()
        rank1["host"] = rank0["host"]
        passed, reason = probe.result_rows_valid(rank0, rank1)
        self.assertFalse(passed)
        self.assertIn("distinct hosts", reason)
        rank0, rank1 = make_valid_results()
        rank1["gpu_uuid"] = rank0["gpu_uuid"]
        passed, reason = probe.result_rows_valid(rank0, rank1)
        self.assertFalse(passed)
        self.assertIn("GPU UUIDs", reason)
        rank0, rank1 = make_valid_results()
        rank1["peer_id"] = "wrong-peer"
        passed, reason = probe.result_rows_valid(rank0, rank1)
        self.assertFalse(passed)
        self.assertIn("reciprocal", reason)

    def test_explicit_checker_writes_fail_closed_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            art = Path(temp)
            rank0, rank1 = make_valid_results()
            rank1["received"][0]["sha256"] = "f" * 64
            (art / "rank0-result.json").write_text(json.dumps(rank0))
            (art / "rank1-result.json").write_text(json.dumps(rank1))
            result = probe.check_results(art)
            self.assertEqual(result["status"], "fail")
            self.assertTrue((art / "final.json").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
