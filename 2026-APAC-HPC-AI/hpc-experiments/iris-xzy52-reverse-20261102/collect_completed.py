"""Collect selected text/native evidence for one terminal Iris xzy comparison."""
from pathlib import Path
import base64
import hashlib
import io
import json
import sys
import tarfile

E = Path(__file__).resolve().parent
sys.path.insert(0, str(E.parent / 'tools'))
from iris_bridge import run_json

receipt = json.loads((E / 'submission-receipt.json').read_text())
job, remote_root = receipt['job_id'], receipt['root']
out = E / ('completed-' + job)
assert not out.exists(), 'Preserve any existing evidence collection'
expected = json.loads((E / 'ROOT_REVIEW.json').read_text())['payload_sha256']
labels = ['A1-scotch', 'B1-our-xzy', 'B2-our-xzy', 'A2-scotch']
body = 'ROOT=' + repr(remote_root) + '\nJOB=' + repr(job) + '\nEXPECTED=' + repr(expected) + '\nLABELS=' + repr(labels) + r'''
from pathlib import Path
import subprocess,json,datetime,hashlib,base64,io,tarfile
k=Path(ROOT)/'kit';run=k/'runs'/JOB
p=subprocess.run(['sacct','-j',JOB,'-P','-o','JobID,JobName,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList,MaxRSS,TotalCPU'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert p.returncode==0,p.stderr
lines=p.stdout.splitlines();rows=[dict(zip(lines[0].split('|'),v.split('|'))) for v in lines[1:]]
row=next(x for x in rows if x.get('JobID')==JOB)
assert row['State'] in ('COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY'),row
actual={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in EXPECTED};assert actual==EXPECTED
paths=set()
for f in run.iterdir():
 if f.is_file() and not f.is_symlink():paths.add(f)
for folder in ('probes','mapping'):
 q=run/folder
 if q.is_dir():
  for f in q.rglob('*'):
   if f.is_file() and not f.is_symlink():paths.add(f)
for label in LABELS:
 a=run/'arms'/label
 for name in ('simpleFoam.log','solver.stderr','resource-time.log','return-code.json','command.json','control-change.json','postsolve-fields.json','solver-before-node-snapshot.json','solver-after-node-snapshot.json','postProcessing/wallClockTimeStatistics/0/wallClockTime.dat','postProcessing/forceCoeffsAll/0/coefficient.dat'):
  f=a/name
  if f.is_file() and not f.is_symlink():paths.add(f)
 for f in (a/'system').rglob('*'):
  if f.is_file() and not f.is_symlink():paths.add(f)
for f in (k/'runs').glob(JOB+'*'):
 if f.is_file() and not f.is_symlink():paths.add(f)
paths.add(k/'payload-sha256.txt')
files={};stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as tar:
 for f in sorted(paths):
  raw=f.read_bytes();assert len(raw)<2000000
  rel=str(f.relative_to(k));files[rel]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
  info=tarfile.TarInfo(rel);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
raw=stream.getvalue();assert len(raw)<1200000,len(raw)
result={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':JOB,'root':ROOT,'scheduler':row,'accounting':p.stdout,'frozen_runtime_hashes':actual,'files':files,'archive_bytes':len(raw),'archive_sha256':hashlib.sha256(raw).hexdigest(),'archive_base64':base64.b64encode(raw).decode()}
'''
data = run_json(body, timeout=55)
raw = base64.b64decode(data.pop('archive_base64'), validate=True)
assert len(raw) == data['archive_bytes'] and hashlib.sha256(raw).hexdigest() == data['archive_sha256']
out.mkdir()
(out / 'raw-evidence.tar.gz').write_bytes(raw)
(out / 'collection.json').write_text(json.dumps(data, indent=2) + '\n')
with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
    for member in archive.getmembers():
        assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
        content = archive.extractfile(member).read()
        meta = data['files'][member.name]
        assert len(content) == meta['bytes'] and hashlib.sha256(content).hexdigest() == meta['sha256']
        dest = out / 'collected' / member.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
print(json.dumps({'job_id': job, 'scheduler': data['scheduler'], 'files': len(data['files']),
                  'archive_bytes': len(raw), 'all_hashes_verified': True}))
