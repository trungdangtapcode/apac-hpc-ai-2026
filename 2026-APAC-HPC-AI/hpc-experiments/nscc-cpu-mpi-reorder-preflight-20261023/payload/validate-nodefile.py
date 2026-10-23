"""Require exactly four PBS slots on one host for this bounded preflight."""
from collections import Counter
from pathlib import Path
import json
import sys

rows = [x.strip().split('.', 1)[0] for x in Path(sys.argv[1]).read_text().splitlines() if x.strip()]
counts = Counter(rows)
assert len(rows) == 4 and len(counts) == 1 and list(counts.values()) == [4], (len(rows), counts)
print(json.dumps({'passed': True, 'slots': len(rows), 'host': next(iter(counts)), 'ranks': 4}, indent=2))
