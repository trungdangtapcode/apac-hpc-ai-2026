"""One-shot deployment and bounded admission for mandatory Scotch40 initialization."""
from pathlib import Path
import argparse,base64,datetime,fcntl,hashlib,io,json,os,sys,tarfile
E=Path(__file__).resolve().parent; C=E.parent/'iris-scotch56-20261025'
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json

def save(path,data,exclusive=False):
 target=path if exclusive else path.with_suffix(path.suffix+'.tmp')
 with target.open('x' if exclusive else 'w') as f:f.write(json.dumps(data,indent=2)+'\n');f.flush();os.fsync(f.fileno())
 if not exclusive:target.replace(path)
 fd=os.open(path.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)

def seal():
 review=json.loads((E/'ROOT_REVIEW.json').read_text());assert review['passed']
 files=review['payload_sha256'];assert len(files)==47 and review['payload_file_count']==47
 assert all(not Path(n).is_absolute() and '..' not in Path(n).parts and not (E/n).is_symlink() and hashlib.sha256((E/n).read_bytes()).hexdigest()==v for n,v in files.items())
 assert json.loads((E/'payload-sha256.json').read_text())['files']==files
 assert (E/'payload-sha256.txt').read_text()==''.join(v+'  '+n+'\n' for n,v in files.items())
 return files

def deploy(files):
 assert not any((E/n).exists() for n in ('deployment-intent.json','deployment.json'))
 cut=json.loads((E.parent/'iris-scotch40-cut-20261105/deployment.json').read_text())['root']
 intent={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':cut,'state':'CALLING_DEPLOY','files':files}
 save(E/'deployment-intent.json',intent,exclusive=True)
 stream=io.BytesIO()
 with tarfile.open(fileobj=stream,mode='w:gz') as tar:
  for name,digest in files.items():tar.add(E/name,arcname=name,recursive=False)
  for name in ('payload-sha256.json','payload-sha256.txt'):tar.add(E/name,arcname=name,recursive=False)
 body='ROOT='+repr(cut)+'\nFILES='+repr(files)+'\nDATA='+repr(base64.b64encode(stream.getvalue()).decode())+'''\nfrom pathlib import Path
import tarfile,base64,io,hashlib,json
r=Path(ROOT);art=r/'artifacts/cut-N40-scotch';kit=r/'init-kit'
assert art.is_dir() and not art.is_symlink()
assert not (art/'READY').exists() and not (art/'.INIT_IN_PROGRESS').exists() and not (art/'.INIT_STARTED').exists()
assert not kit.exists() and not kit.is_symlink()
kit.mkdir();(r/'init-runs').mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(DATA)),mode='r:gz') as tar:
 for m in tar.getmembers():
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  p=kit/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(m).read())
assert all(hashlib.sha256((kit/n).read_bytes()).hexdigest()==v for n,v in FILES.items())
result={'root':str(r),'kit':str(kit),'files':FILES,'state':'DEPLOYED_NOT_SUBMITTED'}
'''
 result=run_json(body,timeout=70);assert result['files']==files
 save(E/'deployment.json',result,exclusive=True);print(json.dumps({'root':cut,'kit':result['kit'],'files':len(files),'state':result['state']}))

def submit(files):
 deployment=json.loads((E/'deployment.json').read_text());assert deployment['files']==files and deployment['state']=='DEPLOYED_NOT_SUBMITTED'
 review=json.loads((E/'ROOT_REVIEW.json').read_text());assert review['passed'] and review['payload_sha256']==files
 cut_review=json.loads((E.parent/'iris-scotch40-cut-20261105/completed-2294919/REVIEW.json').read_text());assert cut_review['passed']
 qpath=E.parent/'iris-rank-probe-files-qualify-20261106/completed-2294996/REVIEW.json';q=json.loads(qpath.read_text());assert q['passed'] and hashlib.sha256(qpath.read_bytes()).hexdigest()==review['protocol_qualification_review_sha256']
 maximum=56*20/60;intent=E/'submission-intent.json'
 with (C/'budget.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  assert not any((E/n).exists() for n in ('submission-intent.json','submission-receipt.json','submission-uncertain.json'))
  budget=json.loads((C/'budget.json').read_text());assert budget['cluster']=='Iris' and budget['account']=='rdmaworkshop'
  assert budget['consumed_planning_allowance_allocated_CPU_hours']==1626 and budget['reserved_maximum_allocated_CPU_hours']==0
  assert all(j.get('reservation_retired') for j in budget['jobs'])
  committed=budget['consumed_planning_allowance_allocated_CPU_hours'];ceiling=budget['branch_planning_ceiling_allocated_CPU_hours']
  assert ceiling==1724 and committed+maximum<=ceiling
  pre=run_json("import socket,subprocess,datetime\np=subprocess.run(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],capture_output=True,text=True,timeout=15)\nresult={'host':socket.gethostname(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':p.returncode,'queue':p.stdout,'stderr':p.stderr}\n",timeout=55)
  assert pre['returncode']==0 and not pre['stderr'] and not any('|tu-' in line for line in pre['queue'].splitlines()),pre
  record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'RESERVED_SUBMISSION_UNCERTAIN','root':deployment['root'],'maximum_allocated_CPU_hours':maximum,'stage':'Scotch40_native_initialization_N40_READY_only','prior_committed_allocated_CPU_hours':committed,'preflight':pre}
  save(intent,record,exclusive=True);budget['reserved_maximum_allocated_CPU_hours']=maximum;budget['jobs'].append(record);save(C/'budget.json',budget)
  body='ROOT='+repr(deployment['root'])+'\nFILES='+repr(files)+'\nJOB='+repr('tu-iris-s40-init')+'''\nfrom pathlib import Path
import subprocess,hashlib,json,datetime
r=Path(ROOT);kit=r/'init-kit';art=r/'artifacts/cut-N40-scotch'
queue=subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],text=True)
assert not any('|tu-' in line for line in queue.splitlines()),queue
assert not (art/'READY').exists() and not (art/'.INIT_IN_PROGRESS').exists() and not (art/'.INIT_STARTED').exists()
assert all(hashlib.sha256((kit/n).read_bytes()).hexdigest()==v for n,v in FILES.items())
accounting=subprocess.check_output(['sacct','-j','2294919','--noheader','--parsable2','-o','JobIDRaw,State,ExitCode,AllocCPUS'],text=True)
rows=[x.strip().split('|') for x in accounting.splitlines() if x.strip()]
assert [x for x in rows if x[0]=='2294919']==[['2294919','COMPLETED','0:0','56']],accounting
with (r/'init-submission-intent.json').open('x') as f:json.dump({'state':'CALLING_SBATCH','queue_before':queue,'cut_accounting':accounting},f);f.flush()
p=subprocess.run(['sbatch','--parsable','init.sbatch'],cwd=str(kit),capture_output=True,text=True,timeout=30)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'queue_before':queue,'cut_accounting':accounting,'root':str(r)}
(r/'init-submission-receipt.json').write_text(json.dumps(result,indent=2)+'\\n')
'''
  receipt=run_json(body,timeout=70)
  if receipt.get('returncode')==0 and receipt.get('stdout','').strip().split(';')[0].isdigit():receipt['job_id']=receipt['stdout'].strip().split(';')[0]
  save(E/'submission-receipt.json',receipt,exclusive=True);assert receipt.get('returncode')==0 and receipt.get('job_id','').isdigit(),receipt
  record.update(state='SUBMITTED',job_id=receipt['job_id']);save(intent,record);budget['jobs'][-1]=record;save(C/'budget.json',budget)
  print(json.dumps({'job_id':receipt['job_id'],'maximum_allocated_CPU_hours':maximum,'root':deployment['root']}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=('seal','deploy','submit'));a=p.parse_args();files=seal()
 if a.action=='deploy':deploy(files)
 elif a.action=='submit':submit(files)
 else:print(json.dumps({'sealed':True,'files':len(files)}))
