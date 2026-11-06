"""Collect a compact terminal record for the four-arm Iris rank-density comparison; omit binary fields."""
from pathlib import Path
import base64,hashlib,io,json,sys,tarfile
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'tools'))
from deploy_submit import remote as run_json
receipt=json.loads((E/'submission-receipt.json').read_text());job=receipt['job_id'];root=receipt['root'];OUT=E/('completed-'+job)
assert not OUT.exists(),'Preserve existing evidence collection'
expected=json.loads((E/'deployment.json').read_text())['files']
body='ROOT='+repr(root)+'\nJOB='+repr(job)+'\nEXPECTED='+repr(expected)+r'''
from pathlib import Path
import subprocess,json,datetime,hashlib,base64,io,tarfile
k=Path(ROOT)/'kit';run=k/'runs'/JOB
import sys
sys.path.insert(0,str(k))
from sampler import validate_sample_file
p=subprocess.run(['sacct','-j',JOB,'-P','-o','JobID,JobName,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList,MaxRSS,TotalCPU'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert p.returncode==0
lines=p.stdout.splitlines();rows=[dict(zip(lines[0].split('|'),v.split('|'))) for v in lines[1:]]
row=next(x for x in rows if x.get('JobID')==JOB)
assert row['State'] in ('COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY'),row
actual={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in EXPECTED};assert actual==EXPECTED
paths=set()
for f in run.iterdir():
 if f.is_file() and not f.is_symlink() and f.name!='affinity_probe':paths.add(f)
for folder in ('probes','mapping'):
 for f in (run/folder).rglob('*'):
  if f.is_file() and not f.is_symlink():paths.add(f)
telemetry_checks={}
for label in ('A1-control48','B1-candidate40','B2-candidate40','A2-control48'):
 a=run/'arms'/label
 if not a.is_dir():
  telemetry_checks[label]={'state':'NOT_STARTED'}
  continue
 status=json.loads((a/'telemetry-status.json').read_text()) if (a/'telemetry-status.json').is_file() else {'state':'status_absent'}
 telemetry=validate_sample_file(a/'telemetry-samples.jsonl',optional=True)
 assert telemetry['bytes']<2000000
 if status.get('state')=='sampling':assert telemetry['present'] and telemetry['sample_count']==status.get('sample_count')
 telemetry_checks[label]={'status':status,'validation':telemetry}
 for name in ('simpleFoam.log','solver.stderr','resource-time.log','return-code.json','command.json','rank-probe-launch.log','rank-proof-verifier.log','rank-proofs.json','solver-binding-review.json','solver-memory-policy.json','control-change.json','postsolve-fields.json','rank-policy-verification.json','solver-before-node-snapshot.json','solver-after-node-snapshot.json','telemetry-samples.jsonl','telemetry-status.json','telemetry-stderr.log','postProcessing/wallClockTimeStatistics/0/wallClockTime.dat','postProcessing/forceCoeffsAll/0/coefficient.dat'):
  f=a/name
  if f.is_file() and not f.is_symlink():
   assert f.stat().st_size < 2000000, ('arm evidence file exceeds compact collector cap', str(f), f.stat().st_size)
   paths.add(f)
 for f in (a/'rank-probe-proofs').glob('rank-*.json'):
  if f.is_file() and not f.is_symlink():paths.add(f)
 for f in (a/'system').rglob('*'):
  if f.is_file() and not f.is_symlink():paths.add(f)
for f in (k/'runs').glob(JOB+'*'):
 if f.is_file() and not f.is_symlink():paths.add(f)
paths.add(k/'payload-sha256.txt')
for f in (k/(JOB+'.out'),k/(JOB+'.err')):
 if f.is_file() and not f.is_symlink():paths.add(f)
files={};stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as tar:
 for f in sorted(paths):
  raw=f.read_bytes();assert len(raw)<2000000
  rel=str(f.relative_to(k));files[rel]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
  info=tarfile.TarInfo(rel);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
raw=stream.getvalue();assert len(raw)<1200000,len(raw)
result={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':JOB,'root':ROOT,'scheduler':row,'accounting':p.stdout,'frozen_runtime_hashes':actual,'telemetry_sample_checks':telemetry_checks,'files':files,'archive_bytes':len(raw),'archive_sha256':hashlib.sha256(raw).hexdigest(),'archive_base64':base64.b64encode(raw).decode()}
'''
d=run_json(body,timeout=55);raw=base64.b64decode(d.pop('archive_base64'),validate=True);assert len(raw)==d['archive_bytes'] and hashlib.sha256(raw).hexdigest()==d['archive_sha256']
OUT.mkdir();(OUT/'raw-evidence.tar.gz').write_bytes(raw);(OUT/'collection.json').write_text(json.dumps(d,indent=2)+'\n')
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 for m in tar.getmembers():
  assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  data=tar.extractfile(m).read();meta=d['files'][m.name];assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256']
  f=OUT/'collected'/m.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
print(json.dumps({'job_id':job,'scheduler':d['scheduler'],'files':len(d['files']),'archive_bytes':len(raw),'all_hashes_verified':True}))
