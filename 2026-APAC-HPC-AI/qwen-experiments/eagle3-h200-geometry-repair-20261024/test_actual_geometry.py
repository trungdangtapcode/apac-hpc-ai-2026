#!/usr/bin/env python3
"""Replay immutable job 25750 receipts and test narrow D-role exceptions."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUNDLE = ROOT / "serving-tuning-10/s43-h200-eagle3-geometry-repair"
ACTUAL = HERE / "actual-job-25750-kv-geometry"
spec = importlib.util.spec_from_file_location("validate_kv_geometry", BUNDLE / "validate_kv_geometry.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
ROLES = {"prefill-0": 4, "prefill-1": 4, "decode-0": 8}
EXPERIMENT = "eagle3-h200-worker-bytes-25750-2844ef21-162d-42ac-8331-a898ff682f01"

class ActualGeometryTests(unittest.TestCase):
    def test_all_32_actual_before_after_receipts_pass(self):
        result = validator.validate(ACTUAL, ROLES, EXPERIMENT)
        self.assertTrue(result["passed"])
        self.assertEqual(result["receipt_count"], 32)
        self.assertEqual(result["rank_count"], 16)
        self.assertEqual(result["unknown_d_heads_exception"]["observed_heads"],
                         "not_collected; not inferred or fabricated")

    def mutate_and_require_failure(self, mutator):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            for source in ACTUAL.glob("*.json"):
                shutil.copy2(source, target / source.name)
            paths = sorted(target.glob("*.json"))
            records = [json.loads(p.read_text()) for p in paths]
            for record in records:
                mutator(record)
            for p, record in zip(paths, records):
                p.write_text(json.dumps(record, sort_keys=True) + "\n")
            with self.assertRaises(ValueError):
                validator.validate(target, ROLES, EXPERIMENT)

    def test_unknown_heads_are_allowed_on_all_d_ranks_but_not_prefill(self):
        def change(row):
            if row["role_name"] == "prefill-0" and row["engine_rank"] == 0:
                row["kv_head_num"] = row["total_kv_head_num"] = "not_collected"
        self.mutate_and_require_failure(change)

    def test_unknown_head_exception_rejects_memory_or_stride_drift(self):
        for field, value in (("memory_kind", "DRAM"), ("item_bytes", 128),
                             ("page_stride_bytes", 128), ("token_stride_bytes", 128)):
            def change(row, field=field, value=value):
                if row["role_name"] == "decode-0" and row["engine_rank"] == 0:
                    row["kv_regions"][0][field] = value
            with self.subTest(field=field):
                self.mutate_and_require_failure(change)

    def test_unknown_head_exception_rejects_region_count_drift(self):
        def change(row):
            if row["role_name"] == "decode-0" and row["engine_rank"] == 0:
                row["kv_regions"].pop()
        self.mutate_and_require_failure(change)

    def test_one_missing_head_field_does_not_qualify(self):
        def change(row):
            if row["role_name"] == "decode-0" and row["engine_rank"] == 0:
                row["kv_head_num"] = 1
        self.mutate_and_require_failure(change)

if __name__ == "__main__":
    unittest.main(verbosity=2)
