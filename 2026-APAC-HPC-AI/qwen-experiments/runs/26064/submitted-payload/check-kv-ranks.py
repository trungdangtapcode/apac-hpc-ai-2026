#!/usr/bin/env python3
"""Require exact per-rank BF16 KV allocation records for a placed worker."""
import re,sys
from pathlib import Path
path,worker,tp=Path(sys.argv[1]),sys.argv[2],int(sys.argv[3])
if tp not in (4,8) or (worker.startswith('prefill-') and tp!=4): raise SystemExit('invalid role TP size')
pattern=re.compile(r"^\[[^\]\r\n]+ TP([0-9]+)(?: EP([0-9]+))?\] KV Cache is allocated\. dtype: torch\.bfloat16, #tokens: ([1-9][0-9]*), K size: ([0-9]+(?:\.[0-9]+)?) GB, V size: ([0-9]+(?:\.[0-9]+)?) GB\s*$")
found=set()
for line in path.read_text(errors='replace').splitlines():
 m=pattern.fullmatch(line)
 if not m or not (0<=int(m.group(1))<tp) or float(m.group(4))<=0 or float(m.group(5))<=0: continue
 if worker.startswith('decode-') and int(m.group(2) or -1)!=int(m.group(1)): continue
 if worker.startswith('prefill-') and m.group(2) is not None: continue
 found.add(int(m.group(1)))
expected=set(range(tp)); missing=sorted(expected-found)
if missing or found!=expected: raise SystemExit(f'FATAL: {worker} BF16 KV ranks incomplete; found={sorted(found)} missing={missing}')
print(f'BF16_KV_RANKS_CONFIRMED worker={worker} ranks={",".join(map(str,sorted(found)))}')
