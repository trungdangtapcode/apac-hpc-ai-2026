"""Collect small native xzy initialization evidence after terminal accounting."""
from pathlib import Path
import base64,hashlib,io,json,sys,tarfile
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json
receipt=json.loads((E/'submission-receipt.json').read_text());job=receipt['stdout'].strip().split(';')[0];root=receipt['root'];OUT=E/('completed-'+job)
assert not OUT.exists(),'Preserve existing evidence'
expected=json.loads((E/'ROOT_REVIEW.json').read_text())['payload_sha256']
body='ROOT='+repr(root)+'\nJOB='+repr(job)+'\nEXPECTED='+repr(expected)+'''
from pathlib import Path
import subprocess,json,datetime,hashlib,base64,io,tarfile
r=Path(ROOT);k=r/'kit';run=r/'runs'/JOB
p=subprocess.run(['sacct','-j',JOB,'-P','-o','JobID,JobName,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList,MaxRSS,TotalCPU'],text=True,capture_output=True,timeout=20);assert p.returncode==0
lines=p.stdout.splitlines();rows=[dict(zip(lines[0].split('|'),line.split('|'))) for line in lines[1:]];row=next(x for x in rows if x['JobID']==JOB)
assert row['State'] in ['COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY'],row
actual={name:hashlib.sha256((k/name).read_bytes()).hexdigest() for name in EXPECTED};assert actual==EXPECTED
paths=[x for x in run.iterdir() if x.is_file() and not x.is_symlink()]
for x in (k/'runs').glob(JOB+'*'):
 if x.is_file() and not x.is_symlink():paths.append(x)
for name in ['READY','source-before.json','source-after-copy.json','source-after-init.json']:
 f=r/'initialized/order-xzy'/name
 if f.is_file() and not f.is_symlink():paths.append(f)
files={};buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz') as tar:
 for f in sorted(set(paths)):
  raw=f.read_bytes();assert len(raw)<2000000
  rel=str(f.relative_to(r));files[rel]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};info=tarfile.TarInfo(rel);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
raw=buf.getvalue();assert len(raw)<1200000
result={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':JOB,'root':ROOT,'scheduler':row,'accounting':p.stdout,'frozen_payload_sha256':actual,'files':files,'archive_sha256':hashlib.sha256(raw).hexdigest(),'archive_bytes':len(raw),'archive_base64':base64.b64encode(raw).decode()}
'''
d=run_json(body,timeout=55);raw=base64.b64decode(d.pop('archive_base64'),validate=True);assert len(raw)==d['archive_bytes'] and hashlib.sha256(raw).hexdigest()==d['archive_sha256'];OUT.mkdir();(OUT/'raw-evidence.tar.gz').write_bytes(raw);(OUT/'collection.json').write_text(json.dumps(d,indent=2)+'\n')
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 for m in tar.getmembers():
  assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  data=tar.extractfile(m).read();meta=d['files'][m.name];assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'];f=OUT/'collected'/m.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
print(json.dumps({'job_id':job,'scheduler':d['scheduler'],'files':len(d['files']),'all_hashes_verified':True}))
