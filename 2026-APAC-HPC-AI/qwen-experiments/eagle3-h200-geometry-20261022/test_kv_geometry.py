#!/usr/bin/env python3
"""CPU-only fixtures for the pinned native NIXL registration method."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from derive import DEFAULT_SOURCE, EXPECTED_SOURCE_SHA256
import kv_geometry
from kv_geometry import instrument_registration
from validate_kv_geometry import validate


def native_method():
    source = DEFAULT_SOURCE.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    if digest != EXPECTED_SOURCE_SHA256:
        raise AssertionError(f"pinned native source drift: {digest}")
    tree = ast.parse(source.decode("utf-8"), filename=str(DEFAULT_SOURCE))
    manager_class = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "NixlKVManager"
    )
    method = next(
        node for node in manager_class.body
        if isinstance(node, ast.FunctionDef) and node.name == "register_buffer_to_engine"
    )
    module = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "_nixl_device_id": lambda kind, gpu: gpu if kind == "VRAM" else 0,
        "logger": type("Logger", (), {"debug": lambda *args, **kwargs: None})(),
    }
    exec(compile(module, "pinned-native-register-buffer", "exec"), namespace)
    return namespace["register_buffer_to_engine"]


class NativeArgs:
    engine_rank = 2
    pp_rank = 1
    gpu_id = 3
    page_size = 16
    kv_head_num = 8
    total_kv_head_num = 64
    kv_layer_ids = [11, 12]
    kv_data_ptrs = [0xDEADBEEF12345678, 0xCAFEBABE87654321]
    kv_data_lens = [4096, 2048]
    kv_item_lens = [256, 128]
    kv_data_mem_kinds = ["VRAM", "DRAM"]
    aux_data_ptrs = [0xBAD0A11]
    aux_data_lens = [384]
    state_data_ptrs = [[0xFACE0001, 0xFACE0002]]
    state_data_lens = [[512, 256]]


class FakeAgent:
    def __init__(self, fail_call=None):
        self.calls = []
        self.fail_call = fail_call

    def register_memory(self, addresses, kind):
        self.calls.append((list(addresses), kind))
        if self.fail_call == len(self.calls):
            return []
        return [f"descriptor-{len(self.calls)}"]


class Manager:
    def __init__(self, fail_call=None):
        self.kv_args = NativeArgs()
        self.server_args = type("ServerArgs", (), {"tp_size": 4})()
        self.agent = FakeAgent(fail_call)


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {
            "QWEN_ROLE_NAME": "prefill-0",
            "QWEN_EXPERIMENT_ID": "fixture-run-20261022",
            "QWEN_ARTDIR": self.temp.name,
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(self.temp.cleanup)
        self.native_register = native_method()

    def receipts(self):
        paths = sorted((Path(self.temp.name) / "kv-geometry").glob("*.json"))
        return [json.loads(path.read_text()) for path in paths]

    def test_real_native_method_calls_and_geometry_whitelist(self):
        manager = Manager()
        result = instrument_registration(manager, lambda: self.native_register(manager))
        self.assertIsNone(result)
        self.assertEqual(manager.agent.calls, [
            ([(NativeArgs.kv_data_ptrs[0], 4096, 3, "")], "VRAM"),
            ([(NativeArgs.kv_data_ptrs[1], 2048, 0, "")], "DRAM"),
            ([(NativeArgs.aux_data_ptrs[0], 384, 0, "")], "DRAM"),
            ([(NativeArgs.state_data_ptrs[0][0], 512, 3, ""),
              (NativeArgs.state_data_ptrs[0][1], 256, 3, "")], "VRAM"),
        ])
        records = self.receipts()
        self.assertEqual({r["phase"] for r in records}, {"before", "after"})
        self.assertEqual({r["registration_returned"] for r in records}, {None, True})
        for record in records:
            self.assertEqual(set(record), {
                "schema", "role_name", "experiment_id", "engine_rank", "pp_rank", "gpu_rank",
                "tp_size", "page_size_tokens", "kv_head_num", "total_kv_head_num",
                "kv_layer_ids", "kv_regions", "aux_region_lengths_bytes",
                "state_region_lengths_bytes", "dtype", "tensor_strides", "phase",
                "registration_returned",
            })
            self.assertEqual(record["role_name"], "prefill-0")
            self.assertEqual(record["experiment_id"], "fixture-run-20261022")
            self.assertEqual((record["engine_rank"], record["pp_rank"], record["gpu_rank"]), (2, 1, 3))
            self.assertEqual(record["tp_size"], 4)
            self.assertEqual(record["page_size_tokens"], 16)
            self.assertEqual(record["kv_head_num"], 8)
            self.assertEqual(record["total_kv_head_num"], 64)
            self.assertEqual(record["kv_layer_ids"], [11, 12])
            self.assertEqual(record["kv_regions"], [
                {"index": 0, "region_bytes": 4096, "item_bytes": 256,
                 "page_stride_bytes": 256,
                 "memory_kind": "VRAM", "page_count": 16, "token_stride_bytes": 16},
                {"index": 1, "region_bytes": 2048, "item_bytes": 128,
                 "page_stride_bytes": 128,
                 "memory_kind": "DRAM", "page_count": 16, "token_stride_bytes": 8},
            ])
            self.assertEqual(record["aux_region_lengths_bytes"], [384])
            self.assertEqual(record["state_region_lengths_bytes"], [[512, 256]])
            self.assertEqual(record["dtype"], "not_collected")
            self.assertEqual(record["tensor_strides"], "not_collected")
        raw = b"".join(path.read_bytes() for path in (Path(self.temp.name) / "kv-geometry").glob("*.json"))
        for pointer in NativeArgs.kv_data_ptrs + NativeArgs.aux_data_ptrs + NativeArgs.state_data_ptrs[0]:
            self.assertNotIn(hex(pointer).encode(), raw)
            self.assertNotIn(str(pointer).encode(), raw)

    def test_native_registration_failure_is_unchanged_and_recorded(self):
        baseline = Manager(fail_call=3)
        with self.assertRaisesRegex(Exception, "NIXL memory registration failed for aux tensors") as baseline_error:
            self.native_register(baseline)
        instrumented = Manager(fail_call=3)
        with self.assertRaisesRegex(Exception, "NIXL memory registration failed for aux tensors") as caught:
            instrument_registration(instrumented, lambda: self.native_register(instrumented))
        self.assertEqual(instrumented.agent.calls, baseline.agent.calls)
        self.assertEqual((type(caught.exception), str(caught.exception)),
                         (type(baseline_error.exception), str(baseline_error.exception)))
        self.assertEqual(len(instrumented.agent.calls), 3)
        records = self.receipts()
        self.assertEqual(len(records), 2)
        self.assertEqual({r["phase"]: r["registration_returned"] for r in records},
                         {"before": None, "after": False})
        self.assertIs(type(caught.exception), Exception)

    def test_wrapper_preserves_return_and_exact_exception_identity(self):
        manager = Manager()
        sentinel = object()
        self.assertIs(instrument_registration(manager, lambda: sentinel), sentinel)
        manager = Manager()
        error = RuntimeError("native sentinel failure")
        def fail():
            raise error
        with self.assertRaises(RuntimeError) as caught:
            instrument_registration(manager, fail)
        self.assertIs(caught.exception, error)

    def test_malformed_or_missing_geometry_fails_before_native_registration(self):
        for field, value in (("kv_data_lens", None),
                             ("kv_data_mem_kinds", ["VRAM"]),
                             ("aux_data_lens", [1, 2]),
                             ("state_data_lens", [[1]])):
            manager = Manager()
            setattr(manager.kv_args, field, value)
            called = []
            with self.subTest(field=field), self.assertRaises(ValueError):
                instrument_registration(manager, lambda: called.append(True))
            self.assertEqual(called, [])
            self.assertFalse((Path(self.temp.name) / "kv-geometry").exists())

    def test_region_and_receipt_byte_limits_fail_before_native_registration(self):
        manager = Manager()
        manager.kv_args.kv_data_ptrs = [0] * (kv_geometry.MAX_REGIONS + 1)
        called = []
        with self.assertRaises(ValueError):
            instrument_registration(manager, lambda: called.append(True))
        self.assertEqual(called, [])
        manager = Manager()
        with patch.object(kv_geometry, "MAX_RECEIPT_BYTES", 64):
            with self.assertRaisesRegex(ValueError, "byte limit"):
                instrument_registration(manager, lambda: called.append(True))
        self.assertEqual(called, [])
        self.assertFalse((Path(self.temp.name) / "kv-geometry").exists())

    def test_nondivisible_strides_are_explicitly_not_collected(self):
        manager = Manager()
        manager.kv_args.kv_data_lens = [4097, 2048]
        manager.kv_args.kv_item_lens = [255, 128]
        instrument_registration(manager, lambda: self.native_register(manager))
        records = self.receipts()
        self.assertTrue(all(r["kv_regions"][0]["page_count"] == "not_collected" for r in records))
        self.assertTrue(all(r["kv_regions"][0]["token_stride_bytes"] == "not_collected" for r in records))

    def test_missing_role_or_experiment_identity_fails_closed(self):
        for key in ("QWEN_ROLE_NAME", "QWEN_EXPERIMENT_ID"):
            manager = Manager()
            with patch.dict(os.environ, {key: "invalid value"}):
                with self.assertRaises(ValueError):
                    instrument_registration(manager, lambda: self.native_register(manager))
            self.assertEqual(manager.agent.calls, [])

    def make_full_rank_receipts(self):
        native = self.native_register
        roles = {"prefill-0": 4, "prefill-1": 4, "decode-0": 8}
        for role, tp in roles.items():
            for rank in range(tp):
                manager = Manager()
                manager.server_args.tp_size = tp
                manager.kv_args.engine_rank = rank
                manager.kv_args.pp_rank = 0
                with patch.dict(os.environ, {"QWEN_ROLE_NAME": role}):
                    instrument_registration(manager, lambda manager=manager: native(manager))
        return roles

    def test_full_expected_sixteen_rank_inventory_passes(self):
        roles = self.make_full_rank_receipts()
        result = validate(Path(self.temp.name) / "kv-geometry", roles, "fixture-run-20261022")
        self.assertTrue(result["passed"])
        self.assertEqual(result["rank_count"], 16)
        self.assertEqual(result["receipt_count"], 32)

    def test_validator_rejects_missing_pair_and_unapproved_fields(self):
        roles = self.make_full_rank_receipts()
        receipt_dir = Path(self.temp.name) / "kv-geometry"
        next(receipt_dir.glob("*.json")).unlink()
        with self.assertRaises(ValueError):
            validate(receipt_dir, roles, "fixture-run-20261022")

    def test_validator_rejects_adversarial_whitelisted_values_and_false_strides(self):
        roles = self.make_full_rank_receipts()
        receipt_dir = Path(self.temp.name) / "kv-geometry"
        paths = sorted(receipt_dir.glob("*.json"))
        records = {path: json.loads(path.read_text()) for path in paths}
        target = next(path for path, record in records.items()
                      if record["role_name"] == "prefill-0" and record["engine_rank"] == 0)
        identity = records[target]
        pair = [path for path, record in records.items()
                if (record["role_name"], record["engine_rank"], record["pp_rank"])
                == (identity["role_name"], identity["engine_rank"], identity["pp_rank"])]

        def set_field(record, key, value):
            record[key] = value

        def set_region_field(record, key, value):
            record["kv_regions"][0][key] = value

        cases = [
            ("aux string", lambda row: set_field(row, "aux_region_lengths_bytes", ["secret"])),
            ("state string", lambda row: set_field(row, "state_region_lengths_bytes", [["bad"]])),
            ("negative KV heads", lambda row: set_field(row, "kv_head_num", -1)),
            ("negative total heads", lambda row: set_field(row, "total_kv_head_num", -1)),
            ("negative page size", lambda row: set_field(row, "page_size_tokens", -1)),
            ("string GPU rank", lambda row: set_field(row, "gpu_rank", "3")),
            ("string layer ID", lambda row: set_field(row, "kv_layer_ids", ["layer"])),
            ("empty KV regions", lambda row: set_field(row, "kv_regions", [])),
            ("false page count", lambda row: set_region_field(row, "page_count", 999)),
            ("false token stride", lambda row: set_region_field(row, "token_stride_bytes", 999)),
            ("boolean page count", lambda row: (set_region_field(row, "region_bytes", 256),
                                                  set_region_field(row, "page_count", True))),
            ("boolean token stride", lambda row: (set_field(row, "page_size_tokens", 256),
                                                    set_region_field(row, "token_stride_bytes", True))),
            ("invented dtype", lambda row: set_field(row, "dtype", "bfloat16")),
            ("invented strides", lambda row: set_field(row, "tensor_strides", [])),
        ]
        for label, mutate in cases:
            with self.subTest(case=label):
                try:
                    for path in pair:
                        changed = json.loads(path.read_text())
                        mutate(changed)
                        path.write_text(json.dumps(changed))
                    with self.assertRaises(ValueError):
                        validate(receipt_dir, roles, "fixture-run-20261022")
                finally:
                    for path, original in records.items():
                        path.write_text(json.dumps(original, sort_keys=True, separators=(",", ":")) + "\n")

    def test_validator_enforces_per_file_byte_limit(self):
        roles = self.make_full_rank_receipts()
        receipt_dir = Path(self.temp.name) / "kv-geometry"
        sample = next(receipt_dir.glob("*.json"))
        with sample.open("ab") as stream:
            stream.write(b" " * (1024 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "per-file byte limit"):
            validate(receipt_dir, roles, "fixture-run-20261022")

        # Rebuild in a clean directory and inject a non-whitelisted address field.
        shutil.rmtree(receipt_dir)
        roles = self.make_full_rank_receipts()
        sample = next(receipt_dir.glob("*.json"))
        record = json.loads(sample.read_text())
        record["pointer"] = "0xDEADBEEF"
        sample.write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            validate(receipt_dir, roles, "fixture-run-20261022")


if __name__ == "__main__":
    unittest.main(verbosity=2)
