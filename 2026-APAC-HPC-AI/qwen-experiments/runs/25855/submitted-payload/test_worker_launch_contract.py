#!/usr/bin/env python3
"""CPU launch contract: the real worker must request BF16 and deterministic mode."""
from pathlib import Path

HERE = Path(__file__).resolve().parent

def validate(text: str) -> None:
    marker = "exec python3 -m sglang.launch_server \
"
    assert marker in text, "worker must launch the server directly"
    launch = text.split(marker, 1)[1].split(" --host ", 1)[0]
    assert "--dtype bfloat16" in launch, "server launch must explicitly declare BF16"
    assert "--enable-deterministic-inference" in launch, "deterministic inference must stay enabled"

validate((HERE / "worker.sh").read_text())
old = (HERE.parent / "s44-h200-deterministic-reference" / "worker.sh").read_text()
try:
    validate(old)
except AssertionError as exc:
    assert "explicitly declare BF16" in str(exc)
else:
    raise AssertionError("frozen S44 omission unexpectedly passed the S46 worker contract")
print("WORKER_EXPLICIT_DTYPE_CPU_CONTRACT_PASS; S44 missing dtype rejected")
