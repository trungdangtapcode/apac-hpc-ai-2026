#!/usr/bin/env python3
"""CPU launch contract for explicit BF16 and deterministic S49 worker flags."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE/"worker.sh").read_text()
marker="exec python3 -m sglang.launch_server \
"
assert marker in text,"worker must launch SGLang directly"
launch=text.split(marker,1)[1].split(" --host ",1)[0]
assert "--dtype bfloat16" in text,"S49 role launch args must explicitly declare BF16"
assert "--enable-deterministic-inference" in launch,"deterministic inference must stay enabled"
print("S49 WORKER EXPLICIT BF16 AND DETERMINISTIC CPU CONTRACT PASS")
