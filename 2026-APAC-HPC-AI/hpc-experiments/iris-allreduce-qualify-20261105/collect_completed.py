"""Collect the terminal Allreduce probe, preserving logs and raw latency samples."""
from pathlib import Path
import base64,hashlib,io,json,sys,tarfile
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent/'tools'));from iris_bridge import run_json
r=json.loads((E/'submission-receipt.json').read_text());job=r['job_id'];assert job.isdigit();C=E/('completed-'+job);assert not C.exists()
body='ROOT='+repr(r['root'])+'\nJOB='+repr(job)+'''\nfrom pathlib import Path
import subprocess,json,hashlib,base64,io,tarfile,datetime
k=Path(ROOT)/'kit';p=subprocess.run(['sacct','-j',JOB,'-X','-P','-n','-o','JobID,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList'],capture_output=True,text=True,timeout=15)
row=p.stdout.strip().split('|');assert p.returncode==0 and row[0]==JOB and row[1] in ['COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY']
files={};stream=io.BytesIO()
paths=list((k/'runs').rglob('*'))+[x for x in k.iterdir() if x.suffix in ['.json','.txt','.log','.out','.err']]
with tarfile.open(fileobj=stream,mode='w:gz') as tar:
 for f in sorted(set(paths)):
  if not f.is_file() or f.is_symlink():continue
  raw=f.read_bytes();assert len(raw)<12000000
  rel=str(f.relative_to(k));files[rel]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};info=tarfile.TarInfo(rel);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
raw=stream.getvalue();assert len(raw)<1400000
result={'utc':datetime.datetime.utcnow().isoformat()+'Z','accounting':p.stdout,'files':files,'archive_bytes':len(raw),'archive_sha256':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode()}
'''
d=run_json(body,timeout=55);raw=base64.b64decode(d.pop('base64'),validate=True);assert hashlib.sha256(raw).hexdigest()==d['archive_sha256'];C.mkdir();(C/'raw-evidence.tar.gz').write_bytes(raw)
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 for item in tar.getmembers():
  assert item.isfile() and not Path(item.name).is_absolute() and '..' not in Path(item.name).parts
  data=tar.extractfile(item).read();meta=d['files'][item.name];assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'];f=C/'collected'/item.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
(C/'collection.json').write_text(json.dumps(d,indent=2)+'\n');print('Verified',len(d['files']),'files;',d['accounting'].strip())
