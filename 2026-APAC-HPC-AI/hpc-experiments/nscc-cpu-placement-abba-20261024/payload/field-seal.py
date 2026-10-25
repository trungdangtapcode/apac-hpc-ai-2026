"""Hash every rank's zero-time field files and optionally compare to a prior seal."""
from pathlib import Path
import hashlib,json,sys
case=Path(sys.argv[1]);out=Path(sys.argv[2]);expected=Path(sys.argv[3]) if len(sys.argv)>3 else None
rows=[]
for i in range(512):
 proc=case/('processor'+str(i)); assert proc.is_dir() and not proc.is_symlink(),str(proc)
 zero=proc/'0'; assert zero.is_dir() and not zero.is_symlink(),str(zero)
 assert sorted(x.name for x in proc.iterdir() if x.is_dir() and x.name.replace('.','',1).isdigit())==['0'],str(proc)
 for p in sorted(zero.rglob('*')):
  if p.is_file():
   h=hashlib.sha256()
   with p.open('rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
   rows.append({'file':str(p.relative_to(case)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
assert len(rows)>=512*6, len(rows)
if expected: assert rows==json.loads(expected.read_text())['files'],'zero-time field set/hash changed'
out.write_text(json.dumps({'case':str(case),'rank_count':512,'file_count':len(rows),'files':rows},indent=2)+'\n')
