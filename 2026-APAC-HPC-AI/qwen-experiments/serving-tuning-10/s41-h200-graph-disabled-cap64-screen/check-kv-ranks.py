#!/usr/bin/env python3
"""Require exact per-rank BF16 KV allocation log records for a worker."""
import re
import sys
from pathlib import Path

path, worker = Path(sys.argv[1]), sys.argv[2]
if worker.startswith("prefill-"):
    expected = set(range(4))
    pattern = re.compile(
        r"^\[[^\]\r\n]+ TP([0-9]+)\] KV Cache is allocated\. dtype: torch\.bfloat16, "
        r"#tokens: ([1-9][0-9]*), K size: ([0-9]+(?:\.[0-9]+)?) GB, "
        r"V size: ([0-9]+(?:\.[0-9]+)?) GB\s*$"
    )
    def is_valid_rank(match):
        return (match is not None and int(match.group(1)) in expected
                and float(match.group(3)) > 0 and float(match.group(4)) > 0)
    def rank_of(match):
        return int(match.group(1))
elif worker == "decode-0":
    expected = set(range(8))
    pattern = re.compile(
        r"^\[[^\]\r\n]+ TP([0-9]+) EP([0-9]+)\] KV Cache is allocated\. dtype: torch\.bfloat16, "
        r"#tokens: ([1-9][0-9]*), K size: ([0-9]+(?:\.[0-9]+)?) GB, "
        r"V size: ([0-9]+(?:\.[0-9]+)?) GB\s*$"
    )
    def is_valid_rank(match):
        return (match is not None and int(match.group(1)) in expected
                and int(match.group(2)) == int(match.group(1))
                and float(match.group(4)) > 0 and float(match.group(5)) > 0)
    def rank_of(match):
        return int(match.group(1))
else:
    raise SystemExit(f"FATAL: unknown target worker name {worker!r}")

found = set()
for line in path.read_text(errors="replace").splitlines():
    match = pattern.fullmatch(line)
    if is_valid_rank(match):
        found.add(rank_of(match))
missing = sorted(expected - found)
if missing or found != expected:
    raise SystemExit(f"FATAL: {worker} BF16 KV rank evidence incomplete; found={sorted(found)} missing={missing}")
print(f"BF16_KV_RANKS_CONFIRMED worker={worker} ranks={','.join(map(str, sorted(found)))}")
