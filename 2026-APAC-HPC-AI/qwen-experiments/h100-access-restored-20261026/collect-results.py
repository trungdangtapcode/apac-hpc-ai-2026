#!/usr/bin/env python3
"""Collect bounded selected terminal AI run artifacts; excludes weights/caches/auth state."""
from pathlib import Path
import io,json,shlex,subprocess,tarfile,hashlib,datetime
Q=Path(__file__).resolve().parent.parent;OUT=Q/'h100-recovered-runs-20261026';OUT.mkdir(exist_ok=True)
selected={'eagle3-pd-serial-init-r6-replacement-20261024':'224554.pbs111','dp5-h100-readiness-r3-20261024':'224555.pbs111','eagle3-h100-single-node-equal-tp-20261024':'224560.pbs111','dp5-h100-unified-output-r5-20261024':'224561.pbs111'}
remote='''from pathlib import Path
import io,json,sys,tarfile
base=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015')
selected=SELECTED
files=[];total=0
for name,job in selected.items():
 candidates=[base/name/'runs'/job,base/'runs'/job]
 roots=[p for p in candidates if p.is_dir()]
 if len(roots)!=1:raise RuntimeError('Missing or ambiguous selected run '+name)
 root=roots[0]
 for p in sorted(root.rglob('*')):
  if not p.is_file() or p.is_symlink():continue
  rel=p.relative_to(root)
  if any(part in {'home','private','exchange','cache','__pycache__','submitted','submitted-payload','diagnostic-profile'} for part in rel.parts):continue
  if p.suffix not in {'.json','.jsonl','.log','.txt','.tsv','.sha256','.out','.err'}:continue
  size=p.stat().st_size;total+=size
  if size>50*1024**2 or total>100*1024**2 or len(files)>3000:raise RuntimeError('Bounded collection exceeded')
  files.append((p,Path(name)/'runs'/job/rel))
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz') as tar:
 for p,rel in files:tar.add(str(p),arcname=str(rel),recursive=False)
'''.replace('SELECTED',repr(selected))
cmd='bash -lc '+shlex.quote('python3 -c '+shlex.quote(remote))
r=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch',cmd],capture_output=True,timeout=120);
if r.returncode:
 print(r.stderr.decode(errors='replace')[-1000:]);raise SystemExit('Bounded read-only collection failed before local extraction')
archive=OUT/'selected-terminal-artifacts.tar.gz';assert not archive.exists(),'Preserve prior collection';archive.write_bytes(r.stdout)
manifest=[]
with tarfile.open(fileobj=io.BytesIO(r.stdout),mode='r:gz') as tar:
 for member in tar.getmembers():
  p=Path(member.name);assert not p.is_absolute() and '..' not in p.parts and member.isfile()
  dest=OUT/p;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();data=tar.extractfile(member).read();dest.write_bytes(data)
  manifest.append({'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(OUT/'COLLECTION.json').write_text(json.dumps({'collected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selected':selected,'files':manifest,'archive_bytes':len(r.stdout),'limits':'Selected terminal AI log/JSON/text artifacts only; no diagnostic trace binaries, model/cache/auth state. Native run content acceptance remains a separate review.'},indent=2)+'\n');print('Collected',len(manifest),'files;',len(r.stdout),'compressed bytes')
