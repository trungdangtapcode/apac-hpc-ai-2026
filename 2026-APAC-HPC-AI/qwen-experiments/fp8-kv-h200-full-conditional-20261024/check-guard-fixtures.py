#!/usr/bin/env python3
"""Exercise guard CLI exit semantics with injected CPU-only evidence."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent
bundle = root.parent / "serving-tuning-10"
script = bundle / "s50-h200-bf16-kv-full/guard-full-pair.py"
worker = (bundle / "s50-h200-bf16-kv-full/worker.sh").read_text()
assert "kv_extra=(--kv-cache-dtype fp8_e4m3)" in worker
assert "QWEN_KV_CACHE_DTYPE:-auto" in worker and "!= auto" in worker

cases = [
    ("valid_win", "control", 0, "PROCEED"),
    ("valid_lose", "control", 0, "SKIPPED_GUARD_FALSE"),
    ("error", "control", 2, "FAILED_GUARD_UNKNOWN"),
    ("missing_artifact", "control", 2, "FAILED_GUARD_UNKNOWN"),
    ("candidate_missing_control", "candidate", 2, "FAILED_CONTROL_INVALID"),
    ("candidate_invalid_control", "candidate", 2, "FAILED_CONTROL_INVALID"),
]
with tempfile.TemporaryDirectory(prefix="h200-kv-guard-cli-") as tmp:
    for case, role, expected_rc, expected_status in cases:
        out = Path(tmp) / f"{case}.json"
        proc = subprocess.run(
            [sys.executable, str(script), "--role", role, "--out", str(out), "--fixture-case", case],
            capture_output=True, text=True,
        )
        assert proc.returncode == expected_rc, (case, proc.returncode, proc.stdout, proc.stderr)
        result = json.loads(out.read_text())
        assert result["status"] == expected_status, (case, result)
        assert result["gpu_workers_started"] is False

print("Guard CLI fixtures pass: winner=0, known loss=0 skip, unknown/missing=2, missing full control=2; no GPU/runtime validation implied")
