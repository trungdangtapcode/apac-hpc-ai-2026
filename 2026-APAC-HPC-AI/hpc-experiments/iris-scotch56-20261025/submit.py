"""Admit exactly one sealed Iris cut; preserve reservations on uncertain replies."""
import datetime, fcntl, hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tools'))
from iris_bridge import run_json

def save(path, data):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)

with (HERE / 'budget.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    intent = HERE / 'submission-intent.json'
    if intent.exists():
        raise SystemExit('Existing intent: reconcile its remote receipt; never resubmit automatically.')
    deployment = json.loads((HERE / 'deployment.json').read_text())
    expected = deployment['files']
    for relative, digest in expected.items():
        assert hashlib.sha256((HERE / 'payload' / relative).read_bytes()).hexdigest() == digest
    budget = json.loads((HERE / 'budget.json').read_text())
    maximum = 56 * 40 / 60
    assert budget['reserved_maximum_allocated_CPU_hours'] + maximum <= budget['branch_planning_ceiling_allocated_CPU_hours']
    # Read-only preflight precedes the durable local reservation.
    preflight = run_json("""import subprocess, socket
result={'hostname':socket.gethostname(),'queue':subprocess.check_output(['squeue','-h','-u','rdmaworkshop30','-o','%i|%j|%T'],universal_newlines=True)}
""", timeout=55)
    assert re.fullmatch(r'login\d+(?:\.hpcadvisorycouncil\.com)?', preflight['hostname'])
    assert not any('|tu-' in row for row in preflight['queue'].splitlines()), preflight
    record = {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'state':'RESERVED_SUBMISSION_UNCERTAIN', 'root':deployment['root'],
              'maximum_allocated_CPU_hours':maximum, 'preflight':preflight}
    with intent.open('x') as target:
        target.write(json.dumps(record, indent=2) + '\n')
    budget['reserved_maximum_allocated_CPU_hours'] += maximum
    budget['jobs'].append(record)
    save(HERE / 'budget.json', budget)
    body = """import datetime, hashlib, json, pathlib, re, socket, subprocess
root=pathlib.Path(ROOT)
assert re.fullmatch(r'login\d+(?:\.hpcadvisorycouncil\.com)?',socket.gethostname())
queue=subprocess.check_output(['squeue','-h','-u','rdmaworkshop30','-o','%i|%j|%T'],universal_newlines=True)
assert not any('|tu-' in row for row in queue.splitlines()),queue
for relative,digest in EXPECTED.items():
    assert hashlib.sha256((root/'kit'/relative).read_bytes()).hexdigest()==digest,relative
assert not (root/'artifacts'/'ready-N56-scotch').exists()
remote_intent=root/'submission-intent.json'
with remote_intent.open('x') as target:
    json.dump({'utc':datetime.datetime.utcnow().isoformat()+'Z','queue_before':queue,'state':'CALLING_SBATCH'},target)
p=subprocess.run(['sbatch','--parsable','job.sbatch'],cwd=str(root/'kit'),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=30)
result={'utc':datetime.datetime.utcnow().isoformat()+'Z','root':str(root),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'queue_before':queue}
(root/'submission-receipt.json').write_text(json.dumps(result,indent=2)+'\\n')
"""
    body = 'ROOT=' + repr(deployment['root']) + '\nEXPECTED=' + repr(expected) + '\n' + body
    receipt = run_json(body, timeout=100)
    save(HERE / 'submission-receipt.json', receipt)
    assert receipt['returncode'] == 0, receipt
    job_id = receipt['stdout'].strip().split(';')[0]
    assert job_id.isdigit(), receipt
    record.update(state='SUBMITTED', job_id=job_id)
    save(intent, record)
    save(HERE / 'budget.json', budget)
    print(json.dumps({'job_id':job_id,'maximum_allocated_CPU_hours':maximum,'root':deployment['root']}))
