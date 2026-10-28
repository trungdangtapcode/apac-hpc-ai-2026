"""Collect bounded text evidence for completed Iris job 2294234; omit mesh/fields."""
from pathlib import Path
import base64, datetime, hashlib, io, json, sys, tarfile

E = Path(__file__).resolve().parent
sys.path.insert(0, str(E.parent / 'tools'))
from iris_bridge import run_json

JOB = '2294234'
OUT = E / ('completed-' + JOB)
assert not OUT.exists(), f'Preserve existing collection: {OUT}'
deployment = json.loads((E / 'deployment.json').read_text())
root = deployment['root']
body = 'ROOT=' + repr(root) + '\nJOB=' + repr(JOB) + r'''
from pathlib import Path
import base64,datetime,hashlib,io,json,subprocess,tarfile
r=Path(ROOT); paths=set()
# Run metadata, phase statuses, resource/environment records and Slurm stdout/stderr.
for top in [r/'runs'/JOB, r/'kit/runs']:
 if top.exists():
  for p in top.rglob('*'):
   if p.is_file() and not p.is_symlink(): paths.add(p)
# Native solver outputs and per-case provenance/configuration. Never walk numeric
# time directories or processor data: only explicitly named evidence and system.
for arm in ['zyx','xyz']:
 a=r/'cases'/arm
 for name in ['simpleFoam.log','solver.stderr','resource-time.log','return-code.json',
              'source-before.json','source-after.json','copy-check.json','copy-field-seal.json',
              'full150-control-validation.json','runtime-source-hashes.json',
              'solver-before-node-snapshot.json','solver-after-node-snapshot.json','READY']:
  p=a/name
  if p.is_file() and not p.is_symlink(): paths.add(p)
 for top in [a/'system',a/'affinity']:
  if top.exists():
   for p in top.rglob('*'):
    if p.is_file() and not p.is_symlink(): paths.add(p)
# Source field seals and runtime-before/after tool+library identities are in run dir.
for name in ['payload-sha256.json','payload-sha256.txt']:
 p=r/'kit'/name
 if p.is_file(): paths.add(p)
files={}; stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as tar:
 for p in sorted(paths):
  raw=p.read_bytes()
  if len(raw)>3_000_000: raise ValueError('unexpected large evidence file: '+str(p))
  name=str(p.relative_to(r)); files[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
  info=tarfile.TarInfo(name);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
account=subprocess.run(['sacct','-j',JOB,'-P','-o','JobID,JobName,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList,MaxRSS'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
queue=subprocess.run(['squeue','-j',JOB,'-h','-o','%i|%j|%T|%M|%l|%D|%C|%N'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
expected=json.loads((r/'kit/payload-sha256.json').read_text())['files']
actual={name:hashlib.sha256((r/'kit'/name).read_bytes()).hexdigest() for name in expected}
assert actual==expected,'frozen runtime-kit hash mismatch'
raw=stream.getvalue(); assert len(raw)<1_200_000,('transfer archive too large',len(raw))
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(r),
 'accounting_returncode':account.returncode,'accounting':account.stdout,'accounting_stderr':account.stderr,
 'queue_returncode':queue.returncode,'queue':queue.stdout,'queue_stderr':queue.stderr,
 'files':files,'remote_runtime_hashes':actual,'archive_bytes':len(raw),
 'archive_sha256':hashlib.sha256(raw).hexdigest(),'archive_base64':base64.b64encode(raw).decode()}
'''
d = run_json(body, timeout=55)
raw = base64.b64decode(d.pop('archive_base64'), validate=True)
assert len(raw) == d['archive_bytes'] and hashlib.sha256(raw).hexdigest() == d['archive_sha256']
OUT.mkdir()
(OUT/'raw-evidence.tar.gz').write_bytes(raw)
(OUT/'collection.json').write_text(json.dumps(d, indent=2) + '\n')
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 for member in tar.getmembers():
  path = Path(member.name)
  assert member.isfile() and not path.is_absolute() and '..' not in path.parts
  data = tar.extractfile(member).read(); expected = d['files'][member.name]
  assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256']
  dest = OUT/'collected'/member.name; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
print(json.dumps({'collected_files':len(d['files']),'archive_bytes':len(raw),
 'archive_sha256':d['archive_sha256'],'accounting':d['accounting'],'queue':d['queue']}))
