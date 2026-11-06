"""Collect terminal qualification evidence without model, mesh, or session data."""
from pathlib import Path
import json,base64,hashlib,tarfile,io,sys
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent/'tools'));from iris_bridge import run_json
receipt=json.loads((E/'submission-receipt.json').read_text());job=receipt['job_id'];root=receipt['root'];expected=json.loads((E/'deployment.json').read_text())['files'];O=E/('completed-'+job);assert not O.exists()
body='ROOT='+repr(root)+'\nJOB='+repr(job)+'\nEXPECTED='+repr(expected)+'''\nfrom pathlib import Path
import json,base64,hashlib,tarfile,io,subprocess,datetime
k=Path(ROOT)/'kit';r=k/'runs'/JOB;p=subprocess.run(['sacct','-j',JOB,'--noheader','--parsable2','-o','JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=20);assert p.returncode==0
row=next(x.split('|') for x in p.stdout.splitlines() if x.split('|')[0]==JOB);assert row[1] in ['COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY']
actual={name:hashlib.sha256((k/name).read_bytes()).hexdigest() for name in EXPECTED};assert actual==EXPECTED
paths=[q for q in r.rglob('*') if q.is_file() and not q.is_symlink()]
paths += [q for q in (k/'runs').glob(JOB+'*') if q.is_file() and not q.is_symlink()]
paths += [k/'payload-sha256.txt'];files={};stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as tar:
 for q in sorted(set(paths)):
  raw=q.read_bytes();assert len(raw)<256000;name=str(q.relative_to(k));files[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};item=tarfile.TarInfo(name);item.size=len(raw);tar.addfile(item,io.BytesIO(raw))
raw=stream.getvalue();assert len(raw)<1000000
result={'utc':datetime.datetime.utcnow().isoformat()+'Z','job_id':JOB,'root':ROOT,'accounting':p.stdout,'terminal_row':row,'frozen_hashes':actual,'files':files,'archive_sha256':hashlib.sha256(raw).hexdigest(),'archive_bytes':len(raw),'archive_base64':base64.b64encode(raw).decode()}
'''
r=run_json(body,timeout=55);raw=base64.b64decode(r.pop('archive_base64'));assert len(raw)==r['archive_bytes'] and hashlib.sha256(raw).hexdigest()==r['archive_sha256'];O.mkdir();(O/'raw-evidence.tar.gz').write_bytes(raw);(O/'collection.json').write_text(json.dumps(r,indent=2)+'\n')
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 for item in tar.getmembers():
  assert item.isfile() and not Path(item.name).is_absolute() and '..' not in Path(item.name).parts
  b=tar.extractfile(item).read();meta=r['files'][item.name];assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256'];q=O/'collected'/item.name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
print(json.dumps({'job_id':job,'terminal':r['terminal_row'],'verified_files':len(r['files'])}))
