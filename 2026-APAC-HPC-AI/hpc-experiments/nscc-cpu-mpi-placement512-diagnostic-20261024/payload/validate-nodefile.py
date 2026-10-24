"""Require four PBS hosts with exactly 128 requested rank slots each."""
from collections import Counter
from pathlib import Path
import json
import sys

hosts = [x.strip().split('.', 1)[0] for x in Path(sys.argv[1]).read_text().splitlines() if x.strip()]
counts = Counter(hosts)
assert len(hosts) == 512 and len(counts) == 4 and sorted(counts.values()) == [128] * 4, (len(hosts), counts)
print(json.dumps({'passed': True, 'slots': len(hosts), 'hosts': dict(sorted(counts.items()))}, indent=2))
