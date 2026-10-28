"""Collect only owned small text probe evidence; never copy its compiled binary."""
from pathlib import Path
import base64,hashlib,io,json,subprocess,sys,tarfile
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json
receipt=json.loads((E/'submission-receipt.json').read_text());job=receipt['job_id'];root=receipt['root'];OUT=E/('completed-'+job)
assert not OUT.exists(),'Preserve existing collection'
body='ROOT='+repr(root)+'\nJOB='+repr(job)+'''
from pathlib import Path
import subprocess,json,datetime,io,tarfile,base64,hashlib
r=Path(ROOT);k=r/'kit'
p=subprocess.run(['sacct','-j',JOB,'-P','-o','JobID,JobName,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList,MaxRSS'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert p.returncode==0
lines=p.stdout.splitlines();rows=[dict(zip(lines[0].split('|'),v.split('|'))) for v in lines[1:]]
row=next((x for x in rows if x.get('JobID')==JOB),None)
q=subprocess.run(['squeue','-j',JOB,'-h','-o','%i|%j|%T|%M|%C|%N'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
result={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':JOB,'root':ROOT,'accounting':p.stdout,'scheduler':row,'queue':q.stdout,'terminal':False}
if row and row['State'] in ('COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY'):
 result['terminal']=True
 paths=set()
 for top in [k/'runs'/JOB]:
  for f in top.rglob('*'):
   if f.is_file() and not f.is_symlink() and f.name!='affinity_probe':paths.add(f)
 for suffix in ('.out','.err'):
  f=k/'runs'/(JOB+suffix)
  if f.is_file() and not f.is_symlink():paths.add(f)
 stream=io.BytesIO();files={}
 with tarfile.open(fileobj=stream,mode='w:gz') as tar:
  for f in sorted(paths):
   raw=f.read_bytes();assert len(raw)<1000000
   name=str(f.relative_to(k));files[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
   info=tarfile.TarInfo(name);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
 raw=stream.getvalue();assert len(raw)<1200000
 result.update(files=files,archive_bytes=len(raw),archive_sha256=hashlib.sha256(raw).hexdigest(),archive_base64=base64.b64encode(raw).decode())
'''
d=run_json(body,timeout=55)
if not d['terminal']:
 (E/'post-submit-status.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d));sys.exit(0)
raw=base64.b64decode(d.pop('archive_base64'));assert len(raw)==d['archive_bytes'] and hashlib.sha256(raw).hexdigest()==d['archive_sha256']
OUT.mkdir();(OUT/'raw-evidence.tar.gz').write_bytes(raw);(OUT/'collection.json').write_text(json.dumps(d,indent=2)+'\n')
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 for m in tar.getmembers():
  assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  data=tar.extractfile(m).read();assert len(data)==d['files'][m.name]['bytes'] and hashlib.sha256(data).hexdigest()==d['files'][m.name]['sha256']
  f=OUT/'collected'/m.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
if d['scheduler']['State']=='COMPLETED' and d['scheduler']['ExitCode']=='0:0':
 actual=subprocess.check_output([sys.executable,str(E/'analyze.py'),str(OUT/'collected/runs'/job)],text=True)
 report=json.loads(actual);saved=json.loads((OUT/'collected/runs'/job/'analysis.json').read_text());assert report==saved
 review={'passed':True,'job_id':job,'scheduler':d['scheduler'],'analysis':report,'collected_files':len(d['files']),'all_transfer_hashes_verified':True,'limits':['Native probe calling main-thread masks, not solver speed or page placement.']}
 (OUT/'REVIEW.json').write_text(json.dumps(review,indent=2)+'\n')
 print(json.dumps({'job_id':job,'state':d['scheduler']['State'],'elapsed_seconds':d['scheduler']['ElapsedRaw'],'local_replay_passed':True,'A_vs_B':report['A_default_vs_B_fill_rank_masks'],'B_vs_C':report['B_fill_vs_C_span_rank_mapping'],'files':len(d['files'])}))
else:print(json.dumps({'job_id':job,'scheduler':d['scheduler'],'collection':str(OUT),'measurement_passed':False}))
