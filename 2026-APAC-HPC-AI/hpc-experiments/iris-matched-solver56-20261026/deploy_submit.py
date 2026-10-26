"""Admit one sealed same-allocation Iris pair with a retained budget intent."""
import argparse,base64,datetime,fcntl,hashlib,io,json,os,re,sys,tarfile
from pathlib import Path
E=Path(__file__).resolve().parent;R=E.parent;C=R/'iris-scotch56-20261025'
sys.path.insert(0,str(R/'tools'))
from iris_bridge import run_json

def save(path,data,exclusive=False):
    temp=path if exclusive else path.with_suffix(path.suffix+'.tmp')
    with temp.open('x' if exclusive else 'w') as stream:
        stream.write(json.dumps(data,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
    if not exclusive:temp.replace(path)

def seal():
    files=[E/n for n in ['run-pair.sbatch','review-pair.py','source-observations.json','source-pins.json']]
    files+=list((E/'payload-case').rglob('*'))+list((E/'lib').rglob('*'))
    files=sorted(p for p in files if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    assert 45<=len(files)<=65 and all(not p.is_symlink() for p in files)
    members={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    p=E/'payload-sha256.json'
    if p.exists():assert json.loads(p.read_text())['files']==members,'Preserve sealed payload'
    else:save(p,{'files':members},exclusive=True)
    lines=''.join(v+'  '+k+'\n' for k,v in members.items());p=E/'payload-sha256.txt'
    if p.exists():assert p.read_text()==lines
    else:p.write_text(lines)
    return members

def deploy(members):
    assert not (E/'deployment.json').exists()
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    root='/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-pair150-'+stamp
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w:gz') as archive:
        for name in [*members,'payload-sha256.json','payload-sha256.txt']:archive.add(E/name,arcname=name,recursive=False)
    body='ROOT='+repr(root)+'\nDATA='+repr(base64.b64encode(stream.getvalue()).decode('ascii'))+'\nEXPECTED='+repr(members)+'''\nimport base64,pathlib,tarfile,io,hashlib,json
r=pathlib.Path(ROOT);r.mkdir(exist_ok=False);kit=r/'kit';kit.mkdir();(kit/'runs').mkdir();(r/'RUNS').mkdir()
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(DATA)),mode='r:gz') as archive:
 for member in archive.getmembers():
  assert member.isfile() and not member.name.startswith('/') and '..' not in pathlib.Path(member.name).parts
  p=kit/member.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.extractfile(member).read())
assert all(hashlib.sha256((kit/name).read_bytes()).hexdigest()==digest for name,digest in EXPECTED.items())
result={'root':str(r),'kit':str(kit),'files':EXPECTED,'state':'DEPLOYED_NOT_SUBMITTED'}
(r/'deployment.json').write_text(json.dumps(result,indent=2)+'\\n')
'''
    result=run_json(body,timeout=80);assert result['files']==members;save(E/'deployment.json',result,exclusive=True);print(json.dumps({'root':root,'files':len(members)}))

def submit(members):
    maximum=140.0;intent=E/'submission-intent.json'
    review=json.loads((E/'ROOT_REVIEW.json').read_text());assert review['passed'] and review['payload_sha256']==members
    intake=json.loads((E/'remote-input-intake.json').read_text());assert review['remote_input_intake_sha256']==hashlib.sha256((E/'remote-input-intake.json').read_bytes()).hexdigest()
    assert json.loads((R/'iris-scotch56-init-20261026/completed-review.json').read_text())['passed']
    deployment=json.loads((E/'deployment.json').read_text());assert deployment['files']==members
    with (C/'budget.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not intent.exists(),'Reconcile previous intent; no blind retry'
        b=json.loads((C/'budget.json').read_text());committed=b['consumed_planning_allowance_allocated_CPU_hours']+b['reserved_maximum_allocated_CPU_hours']
        assert committed+maximum<=b['branch_planning_ceiling_allocated_CPU_hours']
        pre=run_json("import subprocess,socket\nresult={'host':socket.gethostname(),'queue':subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],universal_newlines=True)}",timeout=55)
        assert not any('|tu-' in row for row in pre['queue'].splitlines()),pre
        record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'RESERVED_SUBMISSION_UNCERTAIN','root':deployment['root'],'maximum_allocated_CPU_hours':maximum,'stage':'same_allocation_H_then_S_150_steps','preflight':pre,'prior_committed_allocated_CPU_hours':committed}
        save(intent,record,exclusive=True);b['reserved_maximum_allocated_CPU_hours']+=maximum;b['jobs'].append(record);save(C/'budget.json',b)
        code='ROOT='+repr(deployment['root'])+'\nEXPECTED='+repr(members)+'\nSOURCES='+repr(intake['sources'])+'''\nimport pathlib,subprocess,hashlib,json,datetime
r=pathlib.Path(ROOT);kit=r/'kit';stage='PRECHECK'
def work():
 global stage
 queue=subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],universal_newlines=True)
 assert not any('|tu-' in row for row in queue.splitlines()),queue
 for name,digest in EXPECTED.items():assert hashlib.sha256((kit/name).read_bytes()).hexdigest()==digest,name
 for arm,source in SOURCES.items():
  case=pathlib.Path(source['root']);assert (case/'READY').read_text()==source['READY']
  for name,want in source['source_files'].items():
   p=case/name;assert p.is_file()==want['exists'],(arm,name)
   if want['exists']:assert hashlib.sha256(p.read_bytes()).hexdigest()==want['sha256'],(arm,name)
 accounting=subprocess.check_output(['sacct','-j','2294046','-n','-P','-o','JobIDRaw,State,ExitCode,AllocCPUS'],universal_newlines=True)
 rows=[line.strip().split('|') for line in accounting.splitlines() if line.strip()]
 assert [row for row in rows if row[0]=='2294046']==[['2294046','COMPLETED','0:0','56']]
 with (r/'submission-intent.json').open('x') as target:json.dump({'state':'CALLING_SBATCH','queue_before':queue,'init_accounting':accounting},target)
 stage='CALLING_SBATCH'
 p=subprocess.run(['sbatch','--parsable','run-pair.sbatch'],cwd=str(kit),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=30)
 receipt={'utc':datetime.datetime.utcnow().isoformat()+'Z','root':str(r),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'queue_before':queue,'init_accounting':accounting}
 (r/'submission-receipt.json').write_text(json.dumps(receipt,indent=2)+'\\n')
 return receipt
try:result=work()
except Exception as exc:result={'error_type':type(exc).__name__,'stage':stage,'instruction':'Retain reservation and reconcile remote intent; never retry blindly'}
'''
        receipt=run_json(code,timeout=80);save(E/'submission-receipt.json',receipt,exclusive=True);assert receipt.get('returncode')==0,receipt
        job=receipt['stdout'].strip().split(';')[0];assert job.isdigit(),receipt
        record.update(state='SUBMITTED',job_id=job);save(intent,record);save(C/'budget.json',b);print(json.dumps({'job_id':job,'maximum_allocated_CPU_hours':maximum}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['seal','deploy','submit']);args=parser.parse_args();members=seal()
    if args.action=='deploy':deploy(members)
    elif args.action=='submit':submit(members)
    else:print(json.dumps({'sealed':True,'files':len(members)}))
