"""Append command status evidence without mutating any source inputs."""
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
items = json.loads(path.read_text()) if path.exists() else []
items.append({'stage': sys.argv[2], 'return_code': int(sys.argv[3])})
path.write_text(json.dumps(items, indent=2) + '\n')
