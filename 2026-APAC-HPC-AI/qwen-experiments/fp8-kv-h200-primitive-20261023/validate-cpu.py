#!/usr/bin/env python3
"""Dependency-free CPU checks; never fabricates GPU metadata or a pass receipt."""

import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("primitive.py")
spec = importlib.util.spec_from_file_location("fp8_kv_primitive", MODULE)
primitive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(primitive)


class PrimitiveCpuTests(unittest.TestCase):
    def test_requested_head_geometries(self):
        for geometry in primitive.GEOMETRIES:
            primitive.validate_geometry(geometry["q_heads"], geometry["kv_heads"], 128)
        with self.assertRaises(ValueError):
            primitive.validate_geometry(15, 2, 128)
        with self.assertRaises(ValueError):
            primitive.validate_geometry(16, 1, 64)

    def test_lower_right_mask(self):
        self.assertEqual(
            primitive.lower_right_mask(3, 5),
            [
                [True, True, True, False, False],
                [True, True, True, True, False],
                [True, True, True, True, True],
            ],
        )
        with self.assertRaises(ValueError):
            primitive.lower_right_mask(4, 3)

    def test_production_mask_is_lower_right_causal(self):
        # Three final queries in a 4,000-token cache see 3,998, 3,999,
        # and 4,000 keys respectively. This pins the API convention used by
        # the native custom-mask call, independent of any FlashInfer install.
        mask = primitive.lower_right_mask(primitive.VERIFY_TOKENS, primitive.CONTEXT)
        self.assertEqual([sum(row) for row in mask], [3998, 3999, 4000])
        self.assertTrue(all(row[:-1] for row in mask))
        self.assertEqual([row[-1] for row in mask], [False, False, True])

    def test_fixed_scale_cases_and_agreement_gate(self):
        self.assertEqual(primitive.SEED, 2026)
        self.assertEqual(
            primitive.SCALE_CASES,
            (
                {"name": "unit", "k_scale": 1.0, "v_scale": 1.0},
                {"name": "half", "k_scale": 0.5, "v_scale": 0.5},
            ),
        )
        self.assertEqual(primitive.REL_L2_TOLERANCE, 0.02)
        # The native result carries separate metrics for kernel agreement on
        # the same rounded cache and total FP8-vs-original-BF16 loss.
        source = MODULE.read_text()
        self.assertIn('"decode_rel_l2_vs_same_rounded_fp8"', source)
        self.assertIn('"prefill_rel_l2_vs_same_rounded_fp8"', source)
        self.assertIn('"decode_rel_l2_vs_original_bf16_kv"', source)
        self.assertIn('"prefill_rel_l2_vs_original_bf16_kv"', source)

    def test_scalar_oracle_uses_gqa_mask_and_scales(self):
        # Zero Q/K makes every permitted position equiprobable. Stored V is 2x
        # the source V and v_scale=0.5 must restore it in the FP32 reference.
        q = [[[0.0], [0.0]], [[0.0], [0.0]]]
        k_stored = [[[0.0]], [[0.0]], [[0.0]]]
        v_stored = [[[2.0]], [[4.0]], [[16.0]]]
        got = primitive.scalar_attention_reference(q, k_stored, v_stored, 1.0, 0.5)
        self.assertAlmostEqual(got[0][0][0], 1.5)
        self.assertAlmostEqual(got[0][1][0], 1.5)
        self.assertAlmostEqual(got[1][0][0], 11.0 / 3.0)
        self.assertAlmostEqual(got[1][1][0], 11.0 / 3.0)

    def test_native_controller_fails_closed_without_cuda(self):
        class NoCudaTorch:
            class cuda:
                @staticmethod
                def is_available():
                    return False

        with self.assertRaisesRegex(RuntimeError, "CUDA is unavailable"):
            primitive.runtime_gpu_metadata(NoCudaTorch)
        # The validator never creates a successful runtime result or fake GPU ID.
        source = MODULE.read_text()
        self.assertIn('"status": "passed"', source)
        self.assertIn('gpu = runtime_gpu_metadata(torch)', source)
        self.assertNotIn('"gpu_uuid": "FAKE"', source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
