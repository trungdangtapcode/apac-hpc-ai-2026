"""Stream zero-time fields and compare seals outside solver timing."""
from pathlib import Path
import hashlib,json,sys
case=Path(sys.argv[1]);output=Path(sys.argv[2]);expected=Path(sys.argv[3]) if len(sys.argv)>3 else None
rows=[]
for i in range(256):
 p=case/('processor'+str(i));assert sorted(x.name for x in p.iterdir() if x.is_dir() and x.name.replace('.','',1).isdigit())==['0']
 for f in sorted((p/'0').rglob('*')):
  if not f.is_file():continue
  h=hashlib.sha256()
  with f.open('rb') as stream:
   for b in iter(lambda:stream.read(1048576),b''):h.update(b)
  rows.append(dict(file=str(f.relative_to(case)),bytes=f.stat().st_size,sha256=h.hexdigest()))
assert len(rows)>=256*6
if expected:assert rows==json.loads(expected.read_text())['files'],'Zero-time input fields changed'
output.write_text(json.dumps(dict(case=str(case),files=rows),indent=2)+'\n')
