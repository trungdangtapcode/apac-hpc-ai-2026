"""Deploy and admit one Iris initialization after the reviewed native cut."""
import argparse,base64,datetime,fcntl,hashlib,io,json,os,re,sys,tarfile
from pathlib import Path
E=Path(__file__).resolve().parent;C=E.parent/'iris-scotch56-20261025'
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json

def save(path,data,exclusive=False):
    target=path if exclusive else path.with_suffix(path.suffix+'.tmp')
    with target.open('x' if exclusive else 'w') as stream:
        stream.write(json.dumps(data,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
    if not exclusive:target.replace(path)

def seal():
    files=[E/n for n in ['init.sbatch','verify-init.py','source-pins.json']]+sorted((E/'payload-case').rglob('*'))
    files=[p for p in files if p.is_file()]
    assert len(files)==44 and all(not p.is_symlink() for p in files)
    members={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    manifest=E/'payload-sha256.json'
    if manifest.exists():assert json.loads(manifest.read_text())['files']==members,'Frozen source changed'
    else:save(manifest,{'files':members},exclusive=True)
    text=''.join(digest+'  '+name+'\n' for name,digest in members.items())
    path=E/'payload-sha256.txt'
    if path.exists():assert path.read_text()==text
    else:path.write_text(text)
    return members

def deploy(members):
    assert not (E/'deployment.json').exists(),'Existing deployment must be inspected'
    root=json.loads((C/'deployment.json').read_text())['root']
    assert re.fullmatch(r'/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-\d{8}T\d{6}Z',root)
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w:gz') as archive:
        for name in [*members,'payload-sha256.json','payload-sha256.txt']:archive.add(E/name,arcname=name,recursive=False)
    encoded=base64.b64encode(stream.getvalue()).decode('ascii')
    body='ROOT='+repr(root)+'\nARCHIVE='+repr(encoded)+'\nEXPECTED='+repr(members)+'''\nimport pathlib,base64,tarfile,io,hashlib,json
root=pathlib.Path(ROOT);kit=root/'init-kit'
assert (root/'runs/2294040-cut-validation.json').is_file()
assert not (root/'artifacts/ready-N56-scotch/READY').exists()
kit.mkdir(exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(ARCHIVE)),mode='r:gz') as archive:
 for member in archive.getmembers():
  assert member.isfile() and not member.name.startswith('/') and '..' not in pathlib.Path(member.name).parts
  out=kit/member.name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(archive.extractfile(member).read())
assert all(hashlib.sha256((kit/name).read_bytes()).hexdigest()==digest for name,digest in EXPECTED.items())
(root/'init-runs').mkdir(exist_ok=True)
result={'root':str(root),'kit':str(kit),'files':EXPECTED,'state':'DEPLOYED_NOT_SUBMITTED'}
(root/'init-deployment.json').write_text(json.dumps(result,indent=2)+'\\n')
'''
    result=run_json(body,timeout=80);assert result['files']==members
    save(E/'deployment.json',result,exclusive=True)
    print(json.dumps({'kit':result['kit'],'files':len(members)}))

def submit(members,resume=False):
    assert json.loads((C/'cut-review.json').read_text())['passed']
    review=json.loads((E/'ROOT_REVIEW.json').read_text());assert review['passed'] and review['payload_sha256']==members
    deployment=json.loads((E/'deployment.json').read_text());assert deployment['files']==members
    maximum=56*20/60;intent=E/'submission-intent.json'
    with (C/'budget.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if not resume:assert not intent.exists(),'Inspect existing intent; never retry blindly'
        else:
            proof=json.loads((E/'preflight-reconciliation.json').read_text())
            assert proof['remote_intent_exists'] is False and proof['remote_receipt_exists'] is False
            assert proof['root']==deployment['root'] and proof['failed_before_sbatch'] is True
        budget=json.loads((C/'budget.json').read_text())
        assert budget['consumed_planning_allowance_allocated_CPU_hours']+budget['reserved_maximum_allocated_CPU_hours']+(0 if resume else maximum)<=budget['branch_planning_ceiling_allocated_CPU_hours']
        preflight=run_json("""import subprocess,socket
result={'host':socket.gethostname(),'queue':subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],universal_newlines=True)}
""",timeout=55)
        assert not any('|tu-' in line for line in preflight['queue'].splitlines()),preflight
        if resume:
            prior=json.loads(intent.read_text())
            matches=[j for j in budget['jobs'] if j.get('utc')==prior['utc'] and j.get('stage')==prior['stage']]
            assert len(matches)==1 and matches[0]['state']=='RESERVED_SUBMISSION_UNCERTAIN'
            record=matches[0];assert record['maximum_allocated_CPU_hours']==maximum
            record['resumed_after_reviewed_preflight_assertion']=True
        else:
            record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'RESERVED_SUBMISSION_UNCERTAIN','root':deployment['root'],'maximum_allocated_CPU_hours':maximum,'preflight':preflight,'stage':'mandatory_scotch56_initialization'}
            save(intent,record,exclusive=True);budget['reserved_maximum_allocated_CPU_hours']+=maximum;budget['jobs'].append(record);save(C/'budget.json',budget)
        body='ROOT='+repr(deployment['root'])+'\nEXPECTED='+repr(members)+'''\nimport pathlib,subprocess,hashlib,json,datetime
root=pathlib.Path(ROOT);kit=root/'init-kit'
queue=subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],universal_newlines=True)
assert not any('|tu-' in line for line in queue.splitlines()),queue
for name,digest in EXPECTED.items():assert hashlib.sha256((kit/name).read_bytes()).hexdigest()==digest,name
accounting=subprocess.check_output(['sacct','-j','2294040','-n','-P','-o','JobIDRaw,State,ExitCode,AllocCPUS'],universal_newlines=True)
rows=[line.strip().split('|') for line in accounting.splitlines() if line.strip()]
assert [row for row in rows if row[0]=='2294040']==[['2294040','COMPLETED','0:0','56']]
case=root/'artifacts/ready-N56-scotch'
for marker in ['READY','INIT_COMPLETE','INIT_COMPLETE.json','.INIT_IN_PROGRESS','.INIT_STARTED']:assert not (case/marker).exists(),marker
with (root/'init-submission-intent.json').open('x') as target:json.dump({'state':'CALLING_SBATCH','queue_before':queue,'cut_accounting':accounting},target)
p=subprocess.run(['sbatch','--parsable','init.sbatch'],cwd=str(kit),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=30)
result={'utc':datetime.datetime.utcnow().isoformat()+'Z','returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'root':str(root),'queue_before':queue,'cut_accounting':accounting}
(root/'init-submission-receipt.json').write_text(json.dumps(result,indent=2)+'\\n')
'''
        receipt=run_json(body,timeout=80);save(E/'submission-receipt.json',receipt,exclusive=True)
        assert receipt['returncode']==0,receipt
        job=receipt['stdout'].strip().split(';')[0];assert job.isdigit(),receipt
        record.update(state='SUBMITTED',job_id=job);save(intent,record);save(C/'budget.json',budget)
        print(json.dumps({'job_id':job,'maximum_allocated_CPU_hours':maximum,'root':deployment['root']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['seal','deploy','submit','resume-submit']);args=parser.parse_args();members=seal()
    if args.action=='deploy':deploy(members)
    elif args.action in ('submit','resume-submit'):submit(members,resume=args.action=='resume-submit')
    else:print(json.dumps({'files':len(members),'sealed':True}))
