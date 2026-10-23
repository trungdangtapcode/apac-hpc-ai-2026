#!/usr/bin/env python3
"""Adversarial CPU fixtures for the independent TP4 geometry/readiness gates."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent / "payload"
sys.path.insert(0, str(PAYLOAD))
from check_probe import (DERIVED_NIXL_SHA256, DRAFT_PATH, PINNED_DRAFT_SHA256,
                         TARGET_PATH, inspect)

TEST_EXPERIMENT_ID = "fixture-eagle3-h100-geometry-20261023"
from validate_prefill_geometry import validate


def record(rank: int, phase: str) -> dict:
    return {
        "schema": "h200-kv-registration-geometry-v1",
        "role_name": "prefill-0", "experiment_id": TEST_EXPERIMENT_ID,
        "engine_rank": rank, "pp_rank": 0, "gpu_rank": rank, "tp_size": 4,
        "page_size_tokens": 16, "kv_head_num": 8, "total_kv_head_num": 32,
        "kv_layer_ids": [0, 1],
        "kv_regions": [{"index": 0, "region_bytes": 4096, "item_bytes": 256,
                        "page_stride_bytes": 256, "memory_kind": "VRAM",
                        "page_count": 16, "token_stride_bytes": 16}],
        "aux_region_lengths_bytes": [], "state_region_lengths_bytes": [],
        "dtype": "not_collected", "tensor_strides": "not_collected",
        "phase": phase, "registration_returned": None if phase == "before" else True,
    }


def good_log() -> str:
    lines = ["NATIVE_GRAPH_SOURCE_VERIFIED {\"graph\":\"pinned\"}",
             'H100_RUNTIME_VERIFIED ["NVIDIA H100 80GB HBM3"]',
             f"PINNED_DRAFT_VERIFIED {PINNED_DRAFT_SHA256}",
             f"NIXL_PATCH_VERIFIED {DERIVED_NIXL_SHA256}",
             "HPC_OPS_PREFLIGHT_PASSED NVIDIA H100 80GB HBM3",
             f"server_args=ServerArgs(model_path='{TARGET_PATH}', tp_size=4, dtype='bfloat16', context_length=8192, chunked_prefill_size=4096, moe_runner_backend='hpc_ops', speculative_algorithm='EAGLE3', speculative_draft_model_path='{DRAFT_PATH}', speculative_num_steps=2, speculative_eagle_topk=1, speculative_num_draft_tokens=3, speculative_draft_model_quantization=None, disaggregation_mode='prefill', disaggregation_transfer_backend='nixl', mem_fraction_static=0.9)",
             "The server is fired up and ready to roll!"]
    for rank in range(4):
        lines.extend([f"[TP{rank}] KV Cache is allocated. dtype: torch.bfloat16, #tokens: 100, K size: 1 GB, V size: 1 GB",
                      f"[TP{rank}] KV Cache is allocated. dtype: torch.bfloat16, #tokens: 100, K size: 1 GB, V size: 1 GB"])
        lines.extend([f"[TP{rank}] Disable prefill CUDA graph because cuda_graph_config resolved prefill.backend='disabled'.",
                      f"[TP{rank}] Disable prefill CUDA graph because cuda_graph_config resolved prefill.backend='disabled'."])
        lines.append(f"[TP{rank}] NIXL KVManager initialized with backend: UCX")
    return "\n".join(lines) + "\n"


def write_receipts(root: Path, *, omit=None, extra=False, false_after=False,
                   malformed_value=False, changed_after=False) -> None:
    directory = root / "kv-geometry"
    directory.mkdir(parents=True)
    for rank in range(4):
        if omit == rank:
            continue
        for phase in ("before", "after"):
            row = record(rank, phase)
            if phase == "after" and false_after and rank == 0:
                row["registration_returned"] = False
            if phase == "after" and changed_after and rank == 0:
                row["kv_regions"][0]["region_bytes"] = 8192
            if malformed_value and rank == 0 and phase == "before":
                row["engine_rank"] = True
            name = f"{TEST_EXPERIMENT_ID}-prefill-0-e{rank}-pp0-gpu{rank}-{phase}-{rank}{phase}.json"
            (directory / name).write_text(json.dumps(row, sort_keys=True) + "\n")
    if extra:
        (directory / "unexpected-extra.json").write_text("{}\n")


class GeometryValidationTests(unittest.TestCase):
    def test_exact_four_rank_inventory_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_receipts(root)
            result = validate(root / "kv-geometry", TEST_EXPERIMENT_ID)
            self.assertTrue(result["passed"])
            self.assertEqual((result["rank_count"], result["receipt_count"]), (4, 8))

    def test_missing_false_extra_malformed_and_mutated_geometry_fail(self):
        cases = [
            {"name": "missing rank pair", "options": {"omit": 2}},
            {"name": "false registration result", "options": {"false_after": True}},
            {"name": "extra rank file", "options": {"extra": True}},
            {"name": "malformed boolean rank", "options": {"malformed_value": True}},
            {"name": "changed geometry", "options": {"changed_after": True}},
        ]
        for case in cases:
            with self.subTest(case=case["name"]), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                write_receipts(root, **case["options"])
                with self.assertRaises((ValueError, TypeError)):
                    validate(root / "kv-geometry", TEST_EXPERIMENT_ID)

    def test_extra_non_json_entry_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_receipts(root)
            (root / "kv-geometry" / "extra.log").write_text("unexpected\n")
            with self.assertRaises(ValueError):
                validate(root / "kv-geometry", TEST_EXPERIMENT_ID)


class RuntimeLogGateTests(unittest.TestCase):
    def evaluate(self, mutate=None, health="200", ready=True):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_receipts(root)
            text = good_log()
            if mutate:
                text = mutate(text)
            (root / "prefill.log").write_text(text)
            context = {"experiment_id": TEST_EXPERIMENT_ID, "pbs_job_id": "12345.server",
                       "t0_epoch_seconds": 1000, "startup_deadline_epoch_seconds": 2100,
                       "semantic_check_deadline_epoch_seconds": 2140,
                       "cleanup_deadline_epoch_seconds": 2170}
            context_path = root / "experiment-context.json"
            context_path.write_text(json.dumps(context))
            return inspect(root, health, ready, TEST_EXPERIMENT_ID, "12345.server", context_path)

    def test_complete_h100_prefill_readiness_and_geometry_pass(self):
        result = self.evaluate()
        self.assertTrue(result["passed"])
        self.assertEqual(result["proof"]["kv_cache_dtype_counts_by_rank"],
                         {str(i): ["torch.bfloat16", "torch.bfloat16"] for i in range(4)})

    def test_malformed_rank_logs_fail_closed(self):
        cases = [
            ("missing KV line", lambda s: s.replace("[TP3] KV Cache is allocated. dtype: torch.bfloat16, #tokens: 100, K size: 1 GB, V size: 1 GB\n", "", 1)),
            ("unexpected rank", lambda s: s + "[TP4] NIXL KVManager initialized with backend: UCX\n"),
            ("missing NIXL rank", lambda s: s.replace("[TP2] NIXL KVManager initialized with backend: UCX\n", "")),
            ("wrong KV dtype", lambda s: s.replace("[TP1] KV Cache is allocated. dtype: torch.bfloat16", "[TP1] KV Cache is allocated. dtype: torch.float16", 1)),
            ("graph capture started", lambda s: s + "Capture draft prefill CUDA graph begin\n"),
            ("wrong health status", None),
            ("readiness loop failed", None),
        ]
        for name, mutate in cases:
            with self.subTest(case=name):
                result = self.evaluate(mutate,
                                       health="503" if name == "wrong health status" else "200",
                                       ready=False if name == "readiness loop failed" else True)
                self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
