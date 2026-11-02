"""Admit one native Scotch package-tree graph filter and conditional initialization."""
from pathlib import Path
import argparse,base64,datetime,fcntl,hashlib,io,json,os,sys,tarfile
E=Path(__file__).resolve().parent;C=E.parent/'iris-scotch56-20261025';sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json

def save(path,data,exclusive=False):
 target=path if exclusive else path.with_suffix('.tmp')
 with target.open('x' if exclusive else 'w') as f:f.write(json.dumps(data,indent=2)+'\n');f.flush();os.fsync(f.fileno())
 if not exclusive:target.replace(path)
 fd=os.open(path.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)

def seal():
 paths=[E/n for n in ['init.py','job.sbatch','expected-mesh.json','source-pins.json','native_checks.py','interface_graph.py','seal_tree.py','README.md','candidate.json','validate_cut.py','accepted-control-manifest.json','source-reference.json']]+[p for p in (E/'payload-case').rglob('*') if p.is_file()]
 assert len(paths)==53 and all(not p.is_symlink() for p in paths)
 files={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
 p=E/'payload-sha256.json'
 if p.exists():assert json.loads(p.read_text())['files']==files
 else:save(p,{'files':files},exclusive=True)
 text=''.join(v+'  '+k+'\n' for k,v in files.items());p=E/'payload-sha256.txt'
 if p.exists():assert p.read_text()==text
 else:p.write_text(text)
 return files

def deploy(files):
 assert not(E/'deployment.json').exists()
 root='/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch2x28-w100-init-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 stream=io.BytesIO()
 with tarfile.open(fileobj=stream,mode='w:gz') as tar:
  for name in [*files,'payload-sha256.json','payload-sha256.txt']:tar.add(E/name,arcname=name,recursive=False)
 code='ROOT='+repr(root)+'\nFILES='+repr(files)+'\nDATA='+repr(base64.b64encode(stream.getvalue()).decode())+'''\nfrom pathlib import Path
import tarfile,base64,io,hashlib,json
r=Path(ROOT);r.mkdir(exist_ok=False);k=r/'kit';k.mkdir();(k/'runs').mkdir();(r/'runs').mkdir()
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(DATA)),mode='r:gz') as tar:
 for m in tar.getmembers():
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  p=k/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(m).read())
assert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==v for n,v in FILES.items())
result={'root':str(r),'kit':str(k),'files':FILES,'state':'DEPLOYED_NOT_SUBMITTED'}
'''
 result=run_json(code,timeout=55);assert result['files']==files;save(E/'deployment.json',result,exclusive=True);print(json.dumps({'root':root}))

def submit(files):
 deployment=json.loads((E/'deployment.json').read_text());assert deployment['files']==files
 review=json.loads((E/'ROOT_REVIEW.json').read_text());assert review['passed'] and review['payload_sha256']==files
 prior_path=E.parent/'iris-scotch2x28-init-20261102/completed-2294657/REVIEW.json';prior_raw=prior_path.read_bytes();assert hashlib.sha256(prior_raw).hexdigest()==review['parent_review_sha256'];prior=json.loads(prior_raw);assert prior['passed'] and prior['native_cut_offline_replay_passed'] and prior['job_id']=='2294657'
 maximum=56*30/60;intent=E/'submission-intent.json'
 with (C/'budget.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not any((E/n).exists() for n in ['submission-intent.json','submission-receipt.json','submission-uncertain.json']),'Reconcile original intent, never submit twice'
  budget=json.loads((C/'budget.json').read_text());assert budget['cluster']=='Iris' and budget['account']=='rdmaworkshop';assert budget['reserved_maximum_allocated_CPU_hours']==0 and all(j.get('reservation_retired') for j in budget['jobs']), 'Outstanding own maximum must be reconciled first';committed=budget['reserved_maximum_allocated_CPU_hours']+budget['consumed_planning_allowance_allocated_CPU_hours'];assert committed+maximum<=budget['branch_planning_ceiling_allocated_CPU_hours']
  pre=run_json("import subprocess,socket\nresult={'host':socket.gethostname(),'queue':subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],universal_newlines=True)}",timeout=55)
  assert not any('|tu-' in row for row in pre['queue'].splitlines()),pre
  record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'RESERVED_SUBMISSION_UNCERTAIN','root':deployment['root'],'maximum_allocated_CPU_hours':maximum,'stage':'native_scotch2x28_weight100_targeted_graph_falsification','prior_committed_allocated_CPU_hours':committed,'preflight':pre}
  save(intent,record,exclusive=True);budget['reserved_maximum_allocated_CPU_hours']+=maximum;budget['jobs'].append(record);save(C/'budget.json',budget)
  code='ROOT='+repr(deployment['root'])+'\nFILES='+repr(files)+'''\nfrom pathlib import Path
import subprocess,hashlib,json,datetime,os
r=Path(ROOT);k=r/'kit';stage='PRECHECK'
def work():
 global stage
 queue=subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],universal_newlines=True)
 assert not any('|tu-' in row for row in queue.splitlines()),queue
 assert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==v for n,v in FILES.items())
 with (r/'submission-intent.json').open('x') as f:
  json.dump({'state':'CALLING_SBATCH','queue_before':queue},f);f.flush();os.fsync(f.fileno())
 stage='CALLING_SBATCH'
 p=subprocess.run(['sbatch','--parsable','job.sbatch'],cwd=str(k),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=30)
 result={'utc':datetime.datetime.utcnow().isoformat()+'Z','returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'queue_before':queue,'root':str(r)}
 (r/'submission-receipt.json').write_text(json.dumps(result,indent=2)+'\\n');return result
try:result=work()
except Exception as error:result={'error_type':type(error).__name__,'stage':stage,'instruction':'Retain reservation and inspect remote intent; no blind retry'}
'''
  receipt=run_json(code,timeout=55);save(E/'submission-receipt.json',receipt,exclusive=True);assert receipt.get('returncode')==0,receipt
  job=receipt['stdout'].strip().split(';')[0];assert job.isdigit(),receipt;record.update(state='SUBMITTED',job_id=job);save(intent,record);save(C/'budget.json',budget);print(json.dumps({'job_id':job,'maximum_allocated_CPU_hours':maximum}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['seal','deploy','submit']);a=p.parse_args();files=seal()
 if a.action=='deploy':deploy(files)
 elif a.action=='submit':submit(files)
 else:print(json.dumps({'sealed':True,'files':len(files)}))
