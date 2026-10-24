#!/usr/bin/env python3
"""CPU parser regression using allocation records from retained BF16 and FP8 runs."""
from pathlib import Path
import subprocess
import sys
import tempfile

bundle = Path(__file__).resolve().parents[1]
fixtures = Path(__file__).resolve().parent / "rank-fixtures"
checker = bundle / "check-kv-ranks.py"


def run(path, role, dtype, expected_rc):
    result = subprocess.run(
        [sys.executable, str(checker), str(path), role, "--expected", dtype],
        capture_output=True, text=True,
    )
    assert result.returncode == expected_rc, (path, role, dtype, result.stdout, result.stderr)
    return result


for run_id, dtype in ((25863, "auto"), (25864, "fp8_e4m3")):
    for role in ("prefill-0", "prefill-1", "decode-0"):
        run(fixtures / f"{run_id}-{role}.log", role, dtype, 0)

# Expected-dtype mismatches must fail closed.
run(fixtures / "25864-prefill-0.log", "prefill-0", "auto", 1)
run(fixtures / "25863-decode-0.log", "decode-0", "fp8_e4m3", 1)

# Missing and duplicate ranks must not collapse into a set-based false pass.
source = (fixtures / "25864-prefill-0.log").read_text().splitlines()
with tempfile.TemporaryDirectory(prefix="kv-rank-fixture-") as tmp:
    missing = Path(tmp) / "missing.log"
    missing.write_text("\n".join(source[:-1]) + "\n")
    run(missing, "prefill-0", "fp8_e4m3", 1)
    duplicate = Path(tmp) / "duplicate.log"
    duplicate.write_text("\n".join(source + [source[0]]) + "\n")
    run(duplicate, "prefill-0", "fp8_e4m3", 1)

decode = (fixtures / "25864-decode-0.log").read_text().replace(" TP0 EP0]", " TP0 EP1]", 1)
with tempfile.TemporaryDirectory(prefix="kv-ep-fixture-") as tmp:
    mismapped = Path(tmp) / "mismapped.log"
    mismapped.write_text(decode)
    run(mismapped, "decode-0", "fp8_e4m3", 1)

print("CPU rank parser fixtures pass: BF16/FP8 roles, wrong dtype, missing/duplicate rank, and TP/EP mismatch.")
