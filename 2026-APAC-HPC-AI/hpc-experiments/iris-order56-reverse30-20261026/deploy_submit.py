"""Seal, deploy, then explicitly submit the reverse-order Iris screen."""
from pathlib import Path
import argparse, base64, datetime, fcntl, hashlib, io, json, os, tarfile, sys
E=Path(__file__).resolve().parent
B=E.parent
C=B/'iris-scotch56-20261025'
sys.path.insert(0,str(B/'tools'))
from iris_bridge import run_json
RUNTIME=['run.py','job.sbatch','source-pins.json','native_checks.py','case_checks.py','native_output.py','affinity-probe.py','tree-manifest.py']
def save(path,data,exclusive=False):
    target=path if exclusive else path.with_suffix('.tmp')
    with target.open('x' if exclusive else 'w') as f:
        json.dump(data,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    if not exclusive: target.replace(path)
def expected_paths():
    paths=[E/n for n in RUNTIME]+[p for p in (E/'payload-case').rglob('*') if p.is_file()]
    assert len(paths)==49 and all(not p.is_symlink() for p in paths)
    return paths
def compute_files(paths=None):
    paths=expected_paths() if paths is None else paths
    root=Path(os.path.commonpath([str(p.parent if p.is_file() else p) for p in paths]))
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
def seal():
    files=compute_files()
    for n,data in [('payload-sha256.json',{'files':files}),('payload-sha256.txt',None)]:
        p=E/n
        if n.endswith('.json'):
            if p.exists(): assert json.loads(p.read_text())['files']==files
            else: save(p,data,exclusive=True)
        else:
            text=''.join(v+'  '+k+'\n' for k,v in files.items())
            if p.exists(): assert p.read_text()==text
            else: p.write_text(text)
    return files
def require_parent_review():
    path=B/'iris-order56-screen30-20261026/completed-2294099/review.json'
    review=json.loads(path.read_text())
    assert review.get('passed') is True, 'parent completed-2294099 review must independently pass'
    return review
def require_no_own_jobs(queue):
    assert not any('|tu-' in row for row in queue.splitlines()),'One-own-job Iris cap reached'
def require_root_review(files):
    review=json.loads((E/'ROOT_REVIEW.json').read_text())
    assert review['passed'] and review['payload_sha256']==files
def deploy(files):
    require_parent_review();require_root_review(files)
    assert not (E/'deployment.json').exists()
    root='/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-reverse30-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w:gz') as tar:
        for name in [*files,'payload-sha256.json','payload-sha256.txt']: tar.add(E/name,arcname=name,recursive=False)
    code='ROOT='+repr(root)+'\nFILES='+repr(files)+'\nDATA='+repr(base64.b64encode(stream.getvalue()).decode())+'''\nfrom pathlib import Path\nimport tarfile,base64,io,hashlib,json\nr=Path(ROOT);r.mkdir(exist_ok=False);k=r/'kit';k.mkdir();(k/'runs').mkdir();(r/'runs').mkdir()\nwith tarfile.open(fileobj=io.BytesIO(base64.b64decode(DATA)),mode='r:gz') as tar:\n for m in tar.getmembers():\n  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts\n  p=k/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(m).read())\nassert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==v for n,v in FILES.items())\nresult={'root':str(r),'kit':str(k),'files':FILES,'state':'DEPLOYED_NOT_SUBMITTED'}\n'''
    result=run_json(code,timeout=80); assert result['files']==files
    save(E/'deployment.json',result,exclusive=True); return result
def submit(files):
    deployment=json.loads((E/'deployment.json').read_text()); assert deployment['files']==files and deployment['state']=='DEPLOYED_NOT_SUBMITTED'
    require_parent_review();require_root_review(files)
    maximum=56*45/60
    intent=E/'submission-intent.json'
    with (C/'budget.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        assert not intent.exists(),'Uncertain-intent guard: inspect existing intent/receipt before any retry'
        budget=json.loads((C/'budget.json').read_text())
        committed=budget['reserved_maximum_allocated_CPU_hours']+budget['consumed_planning_allowance_allocated_CPU_hours']
        assert committed+maximum<=budget['branch_planning_ceiling_allocated_CPU_hours'],'Iris budget ceiling would be exceeded'
        pre=run_json("import subprocess,socket\nresult={'host':socket.gethostname(),'queue':subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],universal_newlines=True)}",timeout=55)
        require_no_own_jobs(pre['queue'])
        record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'RESERVED_SUBMISSION_UNCERTAIN','root':deployment['root'],'maximum_allocated_CPU_hours':maximum,'stage':'reverse_order_matched_zyx_xyz_30step_screen','prior_committed_allocated_CPU_hours':committed,'preflight':pre}
        save(intent,record,exclusive=True); budget['reserved_maximum_allocated_CPU_hours']+=maximum; budget['jobs'].append(record); save(C/'budget.json',budget)
        code='ROOT='+repr(deployment['root'])+'\nFILES='+repr(files)+'''\nfrom pathlib import Path\nimport subprocess,hashlib,json,datetime\nr=Path(ROOT);k=r/'kit';stage='PRECHECK'\ndef work():\n global stage\n queue=subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],universal_newlines=True)\n assert not any('|tu-' in row for row in queue.splitlines()),queue\n assert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==v for n,v in FILES.items())\n with (r/'submission-intent.json').open('x') as f:json.dump({'state':'CALLING_SBATCH','queue_before':queue},f)\n stage='CALLING_SBATCH'\n p=subprocess.run(['sbatch','--parsable','job.sbatch'],cwd=str(k),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=30)\n result={'utc':datetime.datetime.utcnow().isoformat()+'Z','returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'queue_before':queue,'root':str(r)}\n (r/'submission-receipt.json').write_text(json.dumps(result,indent=2)+'\\n');return result\ntry:result=work()\nexcept Exception as error:result={'error_type':type(error).__name__,'stage':stage,'instruction':'Retain reservation and inspect remote intent; no blind retry'}\n'''
        receipt=run_json(code,timeout=80); save(E/'submission-receipt.json',receipt,exclusive=True)
        assert receipt.get('returncode')==0,receipt
        job=receipt['stdout'].strip().split(';')[0]; assert job.isdigit(),receipt
        record.update(state='SUBMITTED',job_id=job); save(intent,record); save(C/'budget.json',budget)
        return job
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['seal','deploy','submit']);args=parser.parse_args()
    files=seal()
    if args.action=='seal': print(json.dumps({'sealed':True,'files':len(files)}))
    elif args.action=='deploy': print(json.dumps(deploy(files)))
    else: print(json.dumps({'job_id':submit(files)}))
