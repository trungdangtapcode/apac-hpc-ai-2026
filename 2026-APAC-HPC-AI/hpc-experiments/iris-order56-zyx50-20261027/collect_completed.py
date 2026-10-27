"""Collect only owned text evidence; exclude mesh and initialized binary fields."""
from pathlib import Path
import base64,datetime,hashlib,io,json,sys,tarfile
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json
assert not (E/'completed-2294148/collection.json').exists(), 'Do not overwrite a collection'
root=json.loads((E/'deployment.json').read_text())['root']
body='ROOT='+repr(root)+'''
from pathlib import Path
import base64,datetime,hashlib,io,json,subprocess,tarfile
r=Path(ROOT);paths=set()
for top in [r/'runs/2294148',r/'kit/runs']:
 for p in top.rglob('*'):
  if p.is_file() and not p.is_symlink():paths.add(p)
for arm in ['xyz','zyx']:
 a=r/'cases'/arm
 for name in ['simpleFoam.log','solver.stderr','resource-time.log','return-code.json','source-before.json','source-after.json','copy-check.json','solver-before-node-snapshot.json','solver-after-node-snapshot.json','READY','postProcessing/wallClockTimeStatistics/0/wallClockTime.dat','postProcessing/forceCoeffsAll/0/coefficient.dat']:
  p=a/name
  if p.is_file() and not p.is_symlink():paths.add(p)
 for top in [a/'system',a/'affinity']:
  for p in top.rglob('*'):
   if p.is_file() and not p.is_symlink():paths.add(p)
for name in ['payload-sha256.json','payload-sha256.txt']:
 paths.add(r/'kit'/name)
files={};stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as tar:
 for p in sorted(paths):
  raw=p.read_bytes();assert len(raw)<3000000
  name=str(p.relative_to(r));files[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
  info=tarfile.TarInfo(name);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
account=subprocess.check_output(['sacct','-j','2294148','-P','-o','JobID,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList,MaxRSS'],universal_newlines=True)
expected=json.loads((r/'kit/payload-sha256.json').read_text())['files']
actual={name:hashlib.sha256((r/'kit'/name).read_bytes()).hexdigest() for name in expected}
assert actual==expected
raw=stream.getvalue();assert len(raw)<1200000
result={'utc':datetime.datetime.utcnow().isoformat()+'Z','root':str(r),'accounting':account,'files':files,'remote_runtime_hashes':actual,'archive_bytes':len(raw),'archive_sha256':hashlib.sha256(raw).hexdigest(),'archive_base64':base64.b64encode(raw).decode()}
'''
d=run_json(body,timeout=55);raw=base64.b64decode(d.pop('archive_base64'),validate=True)
assert len(raw)==d['archive_bytes'] and hashlib.sha256(raw).hexdigest()==d['archive_sha256']
out=E/'completed-2294148';out.mkdir(exist_ok=False)
(out/'raw-evidence.tar.gz').write_bytes(raw)
(out/'collection.json').write_text(json.dumps(d,indent=2)+'\n')
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 for m in tar.getmembers():
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  data=tar.extractfile(m).read();expected=d['files'][m.name]
  assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256']
  p=out/'collected'/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
print(json.dumps({'collected':len(d['files']),'archive_bytes':len(raw),'accounting':d['accounting']}))
