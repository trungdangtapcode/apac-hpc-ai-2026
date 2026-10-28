#!/usr/bin/env python3
"""Verify frozen run 27141 artifacts and regenerate its compact review record."""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
RAW_MANIFEST = HERE / "RAW_SHA256SUMS"
OUT = BASE / "review-27141.json"


def main():
    for line in RAW_MANIFEST.read_text().splitlines():
        expected, rel = line.split(maxsplit=1)
        path = HERE / rel.strip()
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"raw hash mismatch: {path.name}")

    data = json.loads((HERE / "prefill.json").read_text())
    cases = data["cases"]
    assert data["state"] == "DIAGNOSTIC_COMPLETE_NO_PASS_CLAIM"
    assert len(cases) == data["expected_case_count"] == data["observed_case_count"] == 42
    errors = [c for c in cases if c.get("error")]
    assert not errors and data.get("execution_error_cases") == 0
    assert Counter(c["backend"] for c in cases) == {"fa3": 42}
    assert all(c["finite"] and c["output_shape_and_dtype_ok"] for c in cases)
    assert all(c.get("cache_write_exact", True) for c in cases)

    paged = [c for c in cases if c["kind"] == "paged_causal"]
    ragged = [c for c in cases if c["kind"] == "ragged_causal"]
    pairs = [c for c in paged if c["page_size_tokens"] == 16]
    assert (len(paged), len(ragged), len(pairs)) == (28, 14, 14)
    assert all(c["relative_l2_vs_page1"] == 0.0 for c in pairs)
    assert all(c["original_threshold_flags"]["relative_l2_le_0_01"] for c in cases)
    abs_failures = [c for c in cases if not c["original_threshold_flags"]["max_absolute_le_0_005"]]

    def metrics(rows):
        return {
            "case_count": len(rows),
            "relative_l2_min": min(c["relative_l2_vs_fp32"] for c in rows),
            "relative_l2_max": max(c["relative_l2_vs_fp32"] for c in rows),
            "max_absolute_error_max": max(c["max_absolute_vs_fp32"] for c in rows),
            "relative_l2_threshold_failures": sum(not c["original_threshold_flags"]["relative_l2_le_0_01"] for c in rows),
            "max_absolute_threshold_failures": sum(not c["original_threshold_flags"]["max_absolute_le_0_005"] for c in rows),
        }

    summary = {
        "job_id": "27141",
        "state": data["state"],
        "raw_files": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in ("prefill.json", "slurm.out", "slurm.err")},
        "scope": data["scope"],
        "gpu_name": data["gpu_name"],
        "gpu_uuid": data["gpu_uuid"],
        "source_sha256": {
            "model_config": data["model_config_sha256"],
            "MHATokenToKVPool": data["pool_source_sha256"],
            "FlashInfer_prefill": data["flashinfer_prefill_source_sha256"],
            "SGLang_backend": data["sglang_backend_source_sha256"],
        },
        "tf32_allowed_for_oracle": data["tf32_allowed_for_oracle"],
        "geometry": data["head_geometry"],
        "data": {"seed": data["seed"], "cache": data["cache"], "long_case_oracle": data["long_case_oracle"],
                 "lengths_tokens": data["lengths_tokens"], "page_sizes_tokens": data["page_sizes_tokens"]},
        "case_count": len(cases),
        "execution_error_count": len(errors),
        "backend_counts": dict(Counter(c["backend"] for c in cases)),
        "all_finite": all(c["finite"] for c in cases),
        "all_shape_dtype_checks_pass": all(c["output_shape_and_dtype_ok"] for c in cases),
        "all_cache_write_checks_pass": all(c.get("cache_write_exact", True) for c in cases),
        "ragged_vs_fp32": metrics(ragged),
        "paged_vs_fp32": metrics(paged),
        "original_threshold_flags": {
            "relative_l2_failures_total": sum(not c["original_threshold_flags"]["relative_l2_le_0_01"] for c in cases),
            "max_absolute_failures_total": len(abs_failures),
            "max_absolute_failure_cases": [
                {"kind": c["kind"], "tp": c["tp"], "page_size_tokens": c.get("page_size_tokens"),
                 "length_tokens": c["length_tokens"], "max_absolute_vs_fp32": c["max_absolute_vs_fp32"]}
                for c in abs_failures
            ],
        },
        "paged_page16_vs_page1": {
            "pair_count": len(pairs), "relative_l2_max": max(c["relative_l2_vs_page1"] for c in pairs),
            "nonzero_pairs": sum(c["relative_l2_vs_page1"] != 0 for c in pairs),
            "all_pairs_within_0_01": all(c["page1_delta_le_0_01"] for c in pairs),
        },
        "long_case_records": [
            {"kind": c["kind"], "tp": c["tp"], "page_size_tokens": c.get("page_size_tokens"),
             "query_rows": c["query_rows"], "sampled_query_positions": c["sampled_query_positions"],
             "relative_l2_vs_fp32": c["relative_l2_vs_fp32"], "max_absolute_vs_fp32": c["max_absolute_vs_fp32"],
             "relative_l2_vs_page1": c.get("relative_l2_vs_page1")}
            for c in cases if c["length_tokens"] == 4000
        ],
    }
    OUT.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"SEALED job 27141: {len(cases)} cases, {len(errors)} execution errors, {len(abs_failures)} max-absolute flag failures")


if __name__ == "__main__":
    main()
