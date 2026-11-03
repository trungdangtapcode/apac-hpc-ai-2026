from pathlib import Path
import sys,json,hashlib,base64,io,tarfile
E=Path(__file__).resolve().parent;R=E.parent;OUT=E/'completed-2294675';assert not OUT.exists();sys.path.insert(0,str(R/'tools'));from iris_bridge import run_json
r=json.loads((E/'submission-receipt.json').read_text());files=json.loads((E/'payload-sha256.json').read_text())['files']
body='ROOT='+repr(r['root'])+'\nFILES='+repr(files)+'''
from pathlib import Path
import subprocess,hashlib,json,datetime,base64,tarfile,io
k=Path(ROOT)/'kit';run=k/'runs/2294675';actual={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in FILES};assert actual==FILES
p=subprocess.run(['sacct','-j','2294675','-P','-n','-o','JobID,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList'],text=True,capture_output=True,timeout=15);assert p.returncode==0
paths=[k/'2294675.out',k/'2294675.err']+list(run.glob('*.json'));meta={};stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as t:
 for f in sorted(paths):
  assert f.is_file() and not f.is_symlink();raw=f.read_bytes();assert len(raw)<600000;rel=str(f.relative_to(k));meta[rel]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};i=tarfile.TarInfo(rel);i.size=len(raw);t.addfile(i,io.BytesIO(raw))
raw=stream.getvalue();assert len(raw)<1000000
q=subprocess.run(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],text=True,capture_output=True,timeout=15)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':'2294675','root':ROOT,'accounting':p.stdout,'frozen_hashes':actual,'queue':{'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr},'files':meta,'archive_sha256':hashlib.sha256(raw).hexdigest(),'archive_base64':base64.b64encode(raw).decode()}
'''
d=run_json(body,timeout=55);raw=base64.b64decode(d.pop('archive_base64'),validate=True);assert hashlib.sha256(raw).hexdigest()==d['archive_sha256'];OUT.mkdir();(OUT/'raw.tar.gz').write_bytes(raw);(OUT/'collection.json').write_text(json.dumps(d,indent=2)+'\n')
with tarfile.open(fileobj=io.BytesIO(raw)) as t:
 for m in t.getmembers():
  assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  data=t.extractfile(m).read();meta=d['files'][m.name];assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'];p=OUT/'collected'/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
print(json.dumps({'job':d['job_id'],'accounting':d['accounting'],'files':len(d['files']),'queue':d['queue']},indent=2))
print((OUT/'collected/runs/2294675/qualification.json').read_text())
