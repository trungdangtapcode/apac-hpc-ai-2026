"""Hash zero-time fields over every processor and compare seals when requested."""
from pathlib import Path
import hashlib,json,sys
case=Path(sys.argv[1]);out=Path(sys.argv[2]);ranks=int(sys.argv[3]);expected=Path(sys.argv[4]) if len(sys.argv)>4 else None;rows=[]
for i in range(ranks):
 proc=case/('processor'+str(i));assert proc.is_dir() and not proc.is_symlink();zero=proc/'0';assert zero.is_dir() and not zero.is_symlink();times=sorted(x.name for x in proc.iterdir() if x.is_dir() and x.name.replace('.','',1).isdigit());assert times==['0'],(i,times)
 for p in sorted(zero.rglob('*')):
  if p.is_file():
   h=hashlib.sha256()
   with p.open('rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
   rows.append({'file':str(p.relative_to(case)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
assert len(rows)>=ranks*6,len(rows)
if expected: assert rows==json.loads(expected.read_text())['files'],'zero-time field set/hash changed'
out.write_text(json.dumps({'case':str(case),'rank_count':ranks,'file_count':len(rows),'files':rows},indent=2)+'\n')
