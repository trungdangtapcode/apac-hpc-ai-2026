#!/usr/bin/env python3
"""One-shot deployment and locked, bounded native Iris admission."""
from pathlib import Path
import argparse,base64,datetime,fcntl,hashlib,io,json,os,subprocess,sys,tarfile
E=Path(__file__).resolve().parent;C=E.parent/'iris-scotch56-20261025'
INIT=E.parent/'iris-scotch40-init-20261106';R2=E.parent/'iris-best-recipes40-r2-20261106'
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json

def remote(body,timeout=70):
    # Start the framed response on a clean terminal line; retain bridge nonce/hash checks.
    return run_json("print('\\n', flush=True)\n"+body,timeout=timeout)

def save(path,data,exclusive=False):
    p=path if exclusive else path.with_suffix(path.suffix+'.tmp')
    with p.open('x' if exclusive else 'w') as f:
        f.write(json.dumps(data,indent=2,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    if not exclusive:p.replace(path)
    fd=os.open(path.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)

def seal():
    review=json.loads((E/'ROOT_REVIEW.json').read_text());assert review['passed']
    files=review['payload_sha256'];assert len(files)==review['payload_file_count']
    assert json.loads((E/'payload-sha256.json').read_text())['files']==files
    assert (E/'payload-sha256.txt').read_text()==''.join(v+'  '+n+'\n' for n,v in sorted(files.items()))
    for n,digest in files.items():
        p=E/n;assert not Path(n).is_absolute() and '..' not in Path(n).parts
        assert p.is_file() and not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==digest,n
    return files

def deploy(files):
    assert not any((E/n).exists() for n in ('deployment-intent.json','deployment.json'))
    timestamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    root='/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-rank40-vs48-'+timestamp
    intent={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':root,'files':files,'state':'DEPLOYMENT_CALL_UNCERTAIN'}
    save(E/'deployment-intent.json',intent,exclusive=True)
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w:gz') as tar:
        for n in sorted(files):tar.add(E/n,arcname=n,recursive=False)
        tar.add(E/'payload-sha256.json',arcname='payload-sha256.json',recursive=False)
        tar.add(E/'payload-sha256.txt',arcname='payload-sha256.txt',recursive=False)
    body='ROOT='+repr(root)+'\nFILES='+repr(files)+'\nDATA='+repr(base64.b64encode(stream.getvalue()).decode())+r'''
from pathlib import Path
import tarfile,io,base64,hashlib,json
r=Path(ROOT);assert not r.exists();r.mkdir(parents=True);k=r/'kit';k.mkdir();(r/'runs').mkdir()
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(DATA,validate=True)),mode='r:gz') as t:
 for m in t.getmembers():
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  p=k/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
assert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==v for n,v in FILES.items())
result={'root':str(r),'kit':str(k),'files':FILES,'state':'DEPLOYED_NOT_SUBMITTED'}
'''
    try:r=remote(body)
    except Exception as exc:
        save(E/'deployment-uncertain.json',{'root':root,'exception_type':type(exc).__name__,'state':'RECONCILIATION_REQUIRED'},exclusive=True)
        raise
    assert r['files']==files
    save(E/'deployment.json',r,exclusive=True)
    print(json.dumps({'root':root,'files':len(files),'state':r['state']}))

def reconcile_deployment():
    intent=json.loads((E/'deployment-intent.json').read_text());root=intent['root'];files=intent['files']
    body='ROOT='+repr(root)+'\nFILES='+repr(files)+r'''
from pathlib import Path
import hashlib,datetime
r=Path(ROOT);k=r/'kit'
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':ROOT,'root_exists':r.is_dir(),'kit_exists':k.is_dir(),
        'hashes':{n:hashlib.sha256((k/n).read_bytes()).hexdigest()==v for n,v in FILES.items() if (k/n).is_file()},
        'submission_intent_exists':(r/'submission-intent.json').exists()}
'''
    r=remote(body,timeout=50)
    if r['kit_exists'] and len(r['hashes'])==len(files) and all(r['hashes'].values()) and not r['submission_intent_exists']:
        deployment={'root':root,'kit':root+'/kit','files':files,'state':'DEPLOYED_NOT_SUBMITTED','reconciled_after_transport_timeout':True}
        save(E/'deployment.json',deployment,exclusive=True);print(json.dumps({'reconciled':True,'state':deployment['state']}));return
    raise RuntimeError('deployment could not be proven complete; preserve frozen intent and do not retry blindly')

def submit(files):
    deployment=json.loads((E/'deployment.json').read_text());assert deployment['files']==files and deployment['state']=='DEPLOYED_NOT_SUBMITTED'
    review=json.loads((E/'ROOT_REVIEW.json').read_text());assert review['passed'] and review['payload_sha256']==files
    init=json.loads((INIT/'completed-2294998/REVIEW.json').read_text());assert init['passed'] and init['terminal_state']=='COMPLETED'
    parent=json.loads((R2/'completed-2294997/REVIEW.json').read_text());assert parent['measurement_valid'] and parent['complete_six_arm_matrix'] and parent['rank_proofs_all_passed'] and parent['runtime_identity_stable']
    auth=json.loads((E/'budget-authorisation.json').read_text());maximum=140
    assert auth['selected_request_maximum_allocated_CPU_hours']==maximum and auth['prior_consumed_allocated_CPU_hours']==1634
    intentpath=E/'submission-intent.json'
    with (C/'budget.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        assert not any((E/n).exists() for n in ('submission-intent.json','submission-receipt.json','submission-uncertain.json'))
        b=json.loads((C/'budget.json').read_text())
        assert b['cluster']=='Iris' and b['account']=='rdmaworkshop'
        assert b['consumed_planning_allowance_allocated_CPU_hours']==1634 and b['reserved_maximum_allocated_CPU_hours']==0
        assert b['branch_planning_ceiling_allocated_CPU_hours']==1769 and all(x.get('reservation_retired') for x in b['jobs'])
        assert 1634+maximum<=auth['new_internal_stage_CPU_hours']
        pre=remote("import socket,subprocess,datetime\np=subprocess.run(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],capture_output=True,text=True,timeout=15)\nresult={'host':socket.gethostname(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':p.returncode,'queue':p.stdout,'stderr':p.stderr}\n",timeout=50)
        assert pre['returncode']==0 and not pre['stderr'] and not any('|tu-' in x for x in pre['queue'].splitlines()),pre
        record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'RESERVED_SUBMISSION_UNCERTAIN',
          'root':deployment['root'],'maximum_allocated_CPU_hours':maximum,'prior_committed_allocated_CPU_hours':1634,
          'stage':'native_rank_density_scotch40_vs_scotch48_abba_four40steps','preflight':pre}
        save(intentpath,record,exclusive=True)
        b['reserved_maximum_allocated_CPU_hours']=maximum
        b['branch_planning_ceiling_allocated_CPU_hours']=auth['new_internal_stage_CPU_hours']
        b.setdefault('ceiling_history',[]).append(auth);b['jobs'].append(record)
        b['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save(C/'budget.json',b)
        body='ROOT='+repr(deployment['root'])+'\nFILES='+repr(files)+r'''
from pathlib import Path
import subprocess,hashlib,json,datetime
r=Path(ROOT);k=r/'kit';source40=Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch40-cut-20261105T162039Z/artifacts/cut-N40-scotch')
source48=Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch48-cut-20261105T073707Z/artifacts/cut-N48-scotch')
assert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==v for n,v in FILES.items())
assert (source40/'READY').read_text().startswith('N=40\nmethod=scotch\n')
assert (source48/'READY').read_text().startswith('N=48\nmethod=scotch\n')
q=subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],text=True)
assert not any('|tu-' in row for row in q.splitlines()),q
cut=subprocess.check_output(['sacct','-j','2294998','--noheader','--parsable2','-o','JobIDRaw,State,ExitCode,AllocCPUS'],text=True)
rows=[x.strip().split('|') for x in cut.splitlines() if x.strip()]
assert [x for x in rows if x[0]=='2294998']==[['2294998','COMPLETED','0:0','56']],cut
with (r/'submission-intent.json').open('x') as f:json.dump({'state':'CALLING_SBATCH','queue_before':q,'n40_initializer':cut},f);f.flush()
p=subprocess.run(['sbatch','--parsable','job.sbatch'],cwd=str(k),capture_output=True,text=True,timeout=30)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'queue_before':q,'n40_initializer':cut,'root':str(r)}
(r/'submission-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
'''
        try:receipt=remote(body,timeout=55)
        except Exception as exc:
            save(E/'submission-uncertain.json',{'root':deployment['root'],'exception_type':type(exc).__name__,'state':'RECONCILIATION_REQUIRED','job_may_or_may_not_have_been_submitted':True},exclusive=True)
            raise
        if receipt.get('returncode')==0 and receipt.get('stdout','').strip().split(';')[0].isdigit():
            receipt['job_id']=receipt['stdout'].strip().split(';')[0]
        save(E/'submission-receipt.json',receipt,exclusive=True)
        assert receipt.get('returncode')==0 and str(receipt.get('job_id','')).isdigit(),receipt
        record.update(state='SUBMITTED',job_id=receipt['job_id']);save(intentpath,record)
        b['jobs'][-1]=record;save(C/'budget.json',b)
        print(json.dumps({'job_id':receipt['job_id'],'maximum_allocated_CPU_hours':maximum,'root':deployment['root']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('seal','deploy','reconcile-deployment','submit'));a=p.parse_args()
    files=seal()
    if a.action=='deploy':deploy(files)
    elif a.action=='reconcile-deployment':reconcile_deployment()
    elif a.action=='submit':submit(files)
    else:print(json.dumps({'sealed':True,'payload_files':len(files)}))
