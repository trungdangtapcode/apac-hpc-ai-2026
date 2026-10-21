"""Freeze reusable initialized control fields on allocated compute CPUs."""
from pathlib import Path
import hashlib,json
control=Path('/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-basic-h128-headerfix-20261021T141522Z/artifacts/hierarchical-N128-h1642')
receipt=Path('/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-solve-h128-20261021T143551Z/runs/25905114/semantic-result.json')
assert json.loads(receipt.read_text())['passed'] is True
rows=[]
for i in range(128):
 for p in sorted((control/('processor'+str(i))/'0').rglob('*')):
  if not p.is_file():continue
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  rows.append(dict(file=str(p.relative_to(control)),bytes=p.stat().st_size,sha256=h.hexdigest()))
assert len(rows)>=128*6
Path('control-initial-fields.json').write_text(json.dumps(dict(control=str(control),baseline_job='25905114.pbs101',scope='Initialized zero-time fields for immutable reuse, not a full mesh seal',files=rows),indent=2)+'\n')
