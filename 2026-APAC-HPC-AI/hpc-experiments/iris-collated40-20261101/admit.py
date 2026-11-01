#!/usr/bin/env python3
"""One-shot admission of the bounded native Iris 40-step I/O pair."""
from pathlib import Path
import base64, datetime, fcntl, hashlib, io, json, math, os, re, sys, tarfile
E=Path(__file__).resolve().parent
C=E.parent/'iris-scotch56-20261025'
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json
MAXIMUM=56*4500/3600

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,value,exclusive=False):
    target=path if exclusive else path.with_name('.'+path.name+'.tmp')
    with target.open('x') as f:
        json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    if not exclusive:target.replace(path)
    fd=os.open(path.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)

def reviewed():
    d=json.loads((E/'ROOT_REVIEW.json').read_text());files=d['payload_sha256']
    assert d['passed'] is True and {'job.sbatch','run.py','accepted-source-manifest.json','native_output.py'} <= set(files)
    assert not {'admit_screen.py','ROOT_REVIEW.json','submission-intent.json','submission-receipt.json'} & set(files)
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts and not (E/n).is_symlink() and hashlib.sha256((E/n).read_bytes()).hexdigest()==h for n,h in files.items())
    parent=E.parent/'iris-graphmap-reverse-20261029'
    pointer=json.loads((parent/'REVIEW.json').read_text())
    assert pointer['passed'] is True and pointer['job_id']=='2294390'
    raw=(parent/pointer['review_path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==pointer['review_sha256']
    reviewed_parent=json.loads(raw)
    assert reviewed_parent['all_native_gates_passed'] is True and reviewed_parent['scored_result'] is False
    text=(E/'job.sbatch').read_text()
    required = (
      ('#SBATCH -J tu-iris-io40', '#SBATCH --job-name=tu-iris-io40'),
      ('#SBATCH -p iris', '#SBATCH --partition=iris'),
      ('#SBATCH -A rdmaworkshop', '#SBATCH --account=rdmaworkshop'),
      ('#SBATCH --qos=low',), ('#SBATCH --exclusive',), ('#SBATCH --gpus=0',),
      ('#SBATCH -N 1', '#SBATCH --nodes=1'),
      ('#SBATCH -n 56', '#SBATCH --ntasks=56'),
      ('#SBATCH -t 01:15:00', '#SBATCH --time=01:15:00'))
    for variants in required:
        assert sum(text.splitlines().count(line) for line in variants)==1, variants
    return files

def financial(b):
    assert b['cluster']=='Iris' and b['account']=='rdmaworkshop'
    vals=[float(b[k]) for k in ('branch_planning_ceiling_allocated_CPU_hours','consumed_planning_allowance_allocated_CPU_hours','reserved_maximum_allocated_CPU_hours')]
    assert all(math.isfinite(x) and x>=0 for x in vals)
    assert vals[1]+vals[2]+MAXIMUM<=vals[0]+1e-9
    assert not [j for j in b['jobs'] if not j.get('reservation_retired')]
    return {'ceiling_CPU_hours':vals[0],'consumed_CPU_hours':vals[1],'reserved_before_CPU_hours':vals[2],'new_maximum_CPU_hours':MAXIMUM}

def deploy(files):
    assert not (E/'deployment.json').exists()
    root='/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-io40-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w:gz') as t:
        for n in sorted(files):t.add(E/n,arcname=n,recursive=False)
        t.add(E/'payload-sha256.txt',arcname='payload-sha256.txt',recursive=False)
    body='ROOT='+repr(root)+'\nFILES='+repr(files)+'\nDATA='+repr(base64.b64encode(stream.getvalue()).decode())+'''
from pathlib import Path
import io,tarfile,base64,hashlib
r=Path(ROOT);r.mkdir(parents=True,exist_ok=False);k=r/'kit';k.mkdir();(k/'runs').mkdir()
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(DATA)),mode='r:gz') as t:
 for m in t.getmembers():
  assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  (k/m.name).parent.mkdir(parents=True,exist_ok=True)
  (k/m.name).write_bytes(t.extractfile(m).read())
assert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==h for n,h in FILES.items())
result={'root':ROOT,'payload_sha256':FILES,'state':'DEPLOYED_NOT_SUBMITTED'}
'''
    d=run_json(body,timeout=55);assert d['state']=='DEPLOYED_NOT_SUBMITTED' and d['root']==root;save(E/'deployment.json',d,True);return d

def submit(files):
    for name in ('submission-intent.json','submission-receipt.json','submission-uncertain.json'):assert not (E/name).exists(),'Existing attempt: reconcile; never retry blindly'
    dep=json.loads((E/'deployment.json').read_text());assert dep['payload_sha256']==files
    root=dep['root'];assert re.fullmatch(r'/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-io40-\d{8}T\d{6}Z',root)
    with (C/'budget.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for name in ('submission-intent.json','submission-receipt.json','submission-uncertain.json'):assert not (E/name).exists()
        reviewed();b=json.loads((C/'budget.json').read_text());fin=financial(b)
        q=run_json("import subprocess,datetime\np=subprocess.run(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)\nassert p.returncode==0\nresult={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queue':p.stdout}",timeout=55)
        assert not any('|tu-' in r for r in q['queue'].splitlines()),'Own Iris allocation cap is occupied'
        row={'utc':utc(),'state':'RESERVED_SUBMISSION_UNCERTAIN','stage':'native40_default_vs_collated','root':root,'maximum_allocated_CPU_hours':MAXIMUM,'preflight':q,'financial':fin}
        save(E/'submission-intent.json',row,True);b['jobs'].append(row);b['reserved_maximum_allocated_CPU_hours']+=MAXIMUM;b['updated_utc']=utc();save(C/'budget.json',b)
        body='ROOT='+repr(root)+'\nFILES='+repr(files)+'''
from pathlib import Path
import subprocess,json,hashlib,os,datetime
r=Path(ROOT);k=r/'kit'
assert not any(p.is_symlink() for p in k.rglob('*'))
assert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==h for n,h in FILES.items())
q=subprocess.run(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert q.returncode==0 and not any('|tu-' in v for v in q.stdout.splitlines())
assert not (r/'submission-intent.json').exists() and not (r/'sbatch-response.json').exists()
with (r/'submission-intent.json').open('x') as f:
 json.dump({'state':'CALLING_SBATCH','utc':datetime.datetime.utcnow().isoformat()+'Z','queue':q.stdout},f);f.flush();os.fsync(f.fileno())
fd=os.open(r,os.O_RDONLY);os.fsync(fd);os.close(fd)
p=subprocess.run(['sbatch','--parsable','job.sbatch'],cwd=k,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40)
result={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'root':ROOT,'utc':datetime.datetime.utcnow().isoformat()+'Z'}
if p.returncode==0 and p.stdout.strip().split(';')[0].isdigit():result['job_id']=p.stdout.strip().split(';')[0]
with (r/'sbatch-response.json').open('x') as f:json.dump(result,f);f.flush();os.fsync(f.fileno())
'''
        try:
            response=run_json(body,timeout=55);save(E/'submission-receipt.json',response,True)
            assert response.get('returncode')==0 and str(response.get('job_id','')).isdigit(),'Uncertain response; retain reservation'
        except Exception as exc:
            save(E/'submission-uncertain.json',{'utc':utc(),'error_type':type(exc).__name__,'root':root,'instruction':'Keep reservation and inspect actual scheduler/remote intent before any retry.'},True);raise
        row.update(job_id=response['job_id'],state='SUBMITTED',submitted_utc=utc());b['jobs'][-1]=row;b['updated_utc']=utc();save(C/'budget.json',b);save(E/'submission-intent.json',row)
        return response

if __name__=='__main__':
    action=sys.argv[1];f=reviewed()
    if action=='deploy':r=deploy(f)
    elif action=='submit':r=submit(f)
    else:raise ValueError('deploy or submit required')
    print(json.dumps(r))
