#!/usr/bin/env python3
"""Collect only the owned native-wave run's small evidence; never retire credit."""
from pathlib import Path
import argparse,base64,datetime,hashlib,io,json,re,shlex,subprocess,tarfile

EXPERIMENT=Path(__file__).resolve().parents[1]/'native-wave'
RESEARCH=EXPERIMENT.parents[1]
SSH=RESEARCH/'tools/nscc-cpu-ssh.sh'
MAX_TOTAL=64*1024*1024

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(data): return hashlib.sha256(data).hexdigest()
def save(path,data):
 with path.open('xb') as stream:stream.write(data)
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--experiment',type=Path,default=EXPERIMENT);args=a.parse_args();e=args.experiment.resolve()
 assert e==EXPERIMENT.resolve(),'This collector is restricted to its reviewed bundle.'
 deployment=json.loads((e/'deployment.json').read_text());receipt=json.loads((e/'submission.json').read_text())
 root=deployment['root'];job=receipt.get('job_id',receipt.get('stdout','').strip());assert receipt['root']==root
 assert re.fullmatch(r'/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-nscc-native-\d{8}T\d{6}Z',root)
 assert re.fullmatch(r'\d+\.pbs\d+',job);short=job.split('.')[0];out=e/('collected-'+short);assert not out.exists(),'Existing evidence must be reviewed, never overwritten.'
 body=r'''from pathlib import Path
import base64,datetime,hashlib,io,json,os,stat,subprocess,tarfile
root=Path(ROOT);run=root/'runs'/SHORT
p=subprocess.run(['qstat','-xf','-F','json',JOB],capture_output=True,text=True)
status={'query_rc':p.returncode,'stderr':p.stderr,'stdout_sha256':hashlib.sha256(p.stdout.encode()).hexdigest()}
if p.returncode==0:
 d=json.loads(p.stdout);j=d['Jobs'][JOB]
 status['job']={k:j[k] for k in ['Job_Name','job_state','project','Exit_status','Resource_List','resources_used','stime','obittime'] if k in j}
 assert j['job_state']=='F','Refuse a completed-run collection while PBS says this job remains active.'
else:
 status['limit']='Fresh terminal history unavailable. This is preserved evidence only; no terminal outcome or charge inferred.'
assert run.is_dir(),str(run)
paths=set()
def add(p):
 if p.is_symlink():return
 if p.is_file():
  assert p.stat().st_size<=20*1024*1024,('Individual evidence file exceeds reviewed limit',str(p))
  paths.add(p)
def tree(p):
 if not p.is_dir():return
 for base,dirs,files in os.walk(p,followlinks=False):
  dirs[:]=[d for d in dirs if not (Path(base)/d).is_symlink()]
  for name in files:add(Path(base)/name)
for p in run.iterdir():
 if p.is_file():add(p)
tree(run/'logs')
manifest=json.loads((root/'payload-sha256.json').read_text())['files']
case_rel=[str(Path(k).relative_to('payload/case')) for k in manifest if k.startswith('payload/case/')]
if (run/'arms').is_dir():
 for arm in sorted((run/'arms').iterdir()):
  assert arm.is_dir() and arm.name in ['S0','Hxyz','Hzyx'],str(arm)
  for p in arm.iterdir():
   if p.is_file():add(p)
  tree(arm/'logs')
  case=arm/'case'
  for rel in case_rel:add(case/rel)
  tree(case/'logFiles');tree(case/'postProcessing')
# PBS log location is derived only from the submitted reviewed job name.
batch=root/('native-wave-3arm.o'+SHORT)
if batch.exists():add(batch)
total=sum(p.stat().st_size for p in paths);assert total<=MAX_TOTAL,total
archive=io.BytesIO();records={}
with tarfile.open(fileobj=archive,mode='w:gz') as tf:
 for p in sorted(paths):
  before=p.stat();data=p.read_bytes();after=p.stat();assert before.st_size==len(data)==after.st_size and before.st_mtime_ns==after.st_mtime_ns,('Evidence changed during read',str(p))
  rel=str(p.relative_to(root));entry=tarfile.TarInfo(rel);entry.size=len(data);entry.mtime=int(after.st_mtime);entry.mode=0o644;tf.addfile(entry,io.BytesIO(data))
  records[rel]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
raw=archive.getvalue()
print(json.dumps({'scheduler':status,'files':records,'uncompressed_bytes':total,'archive_sha256':hashlib.sha256(raw).hexdigest(),'archive_bytes':len(raw),'archive_base64':base64.b64encode(raw).decode(),'frozen_payload_manifest':manifest,'pbs_stdout_present':batch.exists(),'collected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
'''.replace('ROOT',repr(root)).replace('SHORT',repr(short)).replace('JOB',repr(job)).replace('MAX_TOTAL',str(MAX_TOTAL))
 p=subprocess.run(['bash',str(SSH),'bash -lc '+shlex.quote('python3 -c '+shlex.quote(body))],capture_output=True,text=True,timeout=180,check=True)
 d=json.loads(p.stdout);raw=base64.b64decode(d.pop('archive_base64'),validate=True);assert len(raw)==d['archive_bytes'] and digest(raw)==d['archive_sha256']
 assert d['frozen_payload_manifest']==deployment['files']
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tf:
  members=tf.getmembers();assert len(members)==len(d['files']) and len({m.name for m in members})==len(members)
  for m in members:
   rel=Path(m.name);assert m.isfile() and not rel.is_absolute() and '..' not in rel.parts
   b=tf.extractfile(m).read();assert d['files'][m.name]=={'bytes':len(b),'sha256':digest(b)}
 out.mkdir();save(out/'raw-evidence.tar.gz',raw)
 d.update(root=root,job_id=job,local_verified_utc=utc(),limits='Text evidence and original case inputs only; excludes processor meshes/fields, authentication, environment dumps and compiled runtime caches. No credit ledger mutation or performance acceptance.')
 save(out/'collection.json',(json.dumps(d,indent=2)+'\n').encode())
 print(json.dumps({'output':str(out),'job_id':job,'files':len(d['files']),'archive_bytes':len(raw),'terminal_state':d['scheduler'].get('job',{}).get('job_state'),'acceptance':'NOT REVIEWED'}))
if __name__=='__main__':main()
