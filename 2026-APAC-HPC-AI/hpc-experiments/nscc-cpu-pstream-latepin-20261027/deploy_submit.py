#!/usr/bin/env python3
"""Seal, deploy, or submit the reviewed NSCC 512-rank pin qualification bundle."""
from pathlib import Path
import argparse
import datetime
import fcntl
import hashlib
import io
import json
import math
import os
import re
import shlex
import subprocess
import tarfile

E = Path(__file__).resolve().parent
R = Path('/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments')
H = Path('/home/apacsc42')
SSH = R / 'tools/nscc-cpu-ssh.sh'
B = R / 'nscc-cpu-timing-probe-20261021'
PARENTS = ('26016270.pbs101',)
MAXIMUM = 512 * 600 / 3600


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value, exclusive=False):
    target = path if exclusive else path.with_name('.' + path.name + '.new')
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, 'w') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    if not exclusive:
        target.replace(path)


def remote(command):
    return subprocess.run(['bash', str(SSH), 'bash -lc ' + shlex.quote(command)],
                          capture_output=True, text=True, timeout=90, check=True)


def payload():
    base = E / 'payload'
    members = {p.relative_to(E).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(base.rglob('*'))
               if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    assert 4 <= len(members) <= 20
    assert sum((E / name).stat().st_size for name in members) < 220000
    assert not any((E / name).is_symlink() for name in members)
    assert len([name for name in members if name.endswith('.pbs')]) == 1
    assert 'payload/mpi-init-probe.c' in members and 'payload/latepin-pmpi-adapter.c' in members
    path = E / 'payload-sha256.json'
    if path.exists():
        assert json.loads(path.read_text())['files'] == members, 'Frozen payload changed; inspect and reseal explicitly'
    else:
        save(path, {'created_utc': utc(), 'files': members}, exclusive=True)
    lines = ''.join(digest + '  ' + name + '\n' for name, digest in members.items())
    text_path = E / 'payload-sha256.txt'
    if text_path.exists():
        assert text_path.read_text() == lines, 'Frozen hash text changed'
    else:
        text_path.write_text(lines)
    return members


def deploy(members):
    root_review = json.loads((E / 'ROOT_REVIEW.json').read_text())
    assert root_review['passed'] and root_review['payload_sha256'] == members
    path = E / 'deployment.json'
    assert not path.exists(), 'Deployment exists; inspect, never overwrite'
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    root = '/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-pstream-latepin-' + stamp
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w:gz') as archive:
        for name in [*members, 'payload-sha256.json', 'payload-sha256.txt']:
            archive.add(E / name, arcname=name, recursive=False)
    code = '''from pathlib import Path
import sys,tarfile,io,json,hashlib
r=Path(ROOT);r.mkdir(parents=True,exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as t:
 for m in t.getmembers():
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  p=r/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
x=json.loads((r/'payload-sha256.json').read_text())['files']
assert all(hashlib.sha256((r/n).read_bytes()).hexdigest()==h for n,h in x.items())
print(json.dumps({'root':str(r),'files':x}))
'''.replace('ROOT', repr(root))
    result = subprocess.run(['bash', str(SSH), 'python3 -c ' + shlex.quote(code)],
                            input=stream.getvalue(), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=90, check=True)
    record = json.loads(result.stdout)
    assert record == {'root': root, 'files': members}
    record.update(created_utc=utc(), state='DEPLOYED_NOT_SUBMITTED')
    save(path, record, exclusive=True)
    print(root)


def submit(members):
    intent = E / 'submission-intent.json'
    assert not intent.exists(), 'Existing intent must be inspected; never retry blindly'
    root_review = json.loads((E / 'ROOT_REVIEW.json').read_text())
    assert root_review['passed'] and root_review['payload_sha256'] == members
    deployment = json.loads((E / 'deployment.json').read_text())
    assert deployment['files'] == members
    root = deployment['root']
    assert re.fullmatch(r'/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-pstream-latepin-\d{8}T\d{6}Z', root)
    parent_path = R / 'nscc-cpu-postinit-pin-20261027/completed-26016270/review.json'
    parent = json.loads(parent_path.read_text())
    assert parent.get('passed') is True and parent['job_id'] == PARENTS[0]
    assert parent['terminal']['job_state'] == 'F' and parent['terminal']['Exit_status'] == 0
    assert parent.get('pin_masks_stable_in_all_four_audit_phases') is True
    assert parent.get('localrank_world_order_verified_per_host') is True

    with (B / 'cpu-budget.lock').open('a') as cpu_lock, (H / '2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/budget.lock').open('a') as ai_lock:
        fcntl.flock(cpu_lock, fcntl.LOCK_EX)
        fcntl.flock(ai_lock, fcntl.LOCK_EX)
        assert not intent.exists()
        verify = "import json,hashlib;from pathlib import Path;r=Path(" + repr(root) + ");x=json.loads((r/'payload-sha256.json').read_text())['files'];assert all(hashlib.sha256((r/n).read_bytes()).hexdigest()==h for n,h in x.items());print('HASH_PASS')"
        assert remote('python3 -c ' + shlex.quote(verify)).stdout.strip() == 'HASH_PASS'
        cpu_queue = remote('qstat -u apacsc42').stdout
        cpu_jobs = re.findall(r'^(\d+\.\S+)\s+apacsc42\b', cpu_queue, re.M)
        assert not cpu_jobs, 'Own CPU PBS queue must be empty before admission'
        ai_result = subprocess.run(['bash', str(H / 'workspace/vpn-rootless/vpn.sh'), 'ssh-batch',
                                    "bash -lc 'qstat -u apacsc42'"], capture_output=True,
                                   text=True, timeout=40, check=True)
        ai_jobs = re.findall(r'^(\d+\S*)\s+apacsc42\b', ai_result.stdout, re.M)
        assert len(cpu_jobs) + len(ai_jobs) + 1 <= 3, 'Combined CPU/AI PBS cap would be exceeded'
        report = remote('myprojects -p 59000042').stdout
        su_rows = [line for line in report.splitlines() if line.startswith('| SU')]
        rate_rows = [line for line in report.splitlines() if line.startswith('| CPU Hour')]
        assert len(su_rows) == len(rate_rows) == 1
        grant, used, balance, in_doubt = [float(value.strip()) for value in su_rows[0].split('|')[2:-1]]
        assert grant == 30000 and balance >= MAXIMUM and in_doubt >= 0
        assert float(rate_rows[0].split('|')[3].strip()) == 1
        budget_path = B / 'cpu-budget.json'
        budget = json.loads(budget_path.read_text())
        assert budget['schema'] == 2 and budget['project'] == '59000042'
        budget['consumed_ceiling_SU']=max(budget['consumed_ceiling_SU'],math.ceil(used-budget['published_snapshot']['used_SU']+1))
        assert budget['consumed_ceiling_SU'] + budget['outstanding_reserved_max_SU'] + MAXIMUM <= budget['baseline_wave_planning_ceiling_SU']
        assert in_doubt <= sum(job.get('maximum_SU', 0) for job in budget['jobs'] if job['id'] in PARENTS)
        precheck = {'utc': utc(), 'cpu_queue': cpu_queue, 'ai_queue_read_only': ai_result.stdout,
                    'combined_PBS_before': len(cpu_jobs) + len(ai_jobs), 'verified_parent': parent['job_id'],
                    'parent_terminal_source': parent['terminal_evidence_source'], 'project_report': report,
                    'planning_ceiling_SU': budget['baseline_wave_planning_ceiling_SU'],
                    'consumed_ceiling_SU': budget['consumed_ceiling_SU'],
                    'outstanding_reserved_max_SU': budget['outstanding_reserved_max_SU'],
                    'new_maximum_SU': MAXIMUM,
                    'scope': 'Native control, rank-only PMPI adapter and real OpenFOAM checkMesh on a tiny diagnostic mesh; no contest solver or scored result.'}
        save(E / 'pre-submit-checks.json', precheck, exclusive=True)
        save(intent, {'utc': utc(), 'root': root, 'files': members, 'maximum_SU': MAXIMUM,
                      'parent': parent['job_id'], 'state': 'RESERVED_DO_NOT_RETRY_BLINDLY'}, exclusive=True)
        entry={'id':None,'root':root,'maximum_SU':MAXIMUM,'branch':'actual_pstream_pmpi_latepin_qualification','state':'SUBMISSION_INTENT','observed_utc':utc(),'parent':parent['job_id']}
        budget['jobs'].append(entry)
        budget['outstanding_reserved_max_SU'] += MAXIMUM
        budget['planning_committed_SU'] = budget['reserved_max_SU'] = budget['consumed_ceiling_SU'] + budget['outstanding_reserved_max_SU']
        budget['updated_utc'] = utc()
        save(budget_path, budget)
        pbs = next(name for name in members if name.endswith('.pbs'))
        try:
            result = remote('cd ' + shlex.quote(root) + ' && qsub ' + shlex.quote(pbs))
            job_id = result.stdout.strip()
            save(E / 'submission.json', {'utc': utc(), 'root': root, 'stdout': result.stdout,
                 'stderr': result.stderr, 'returncode': result.returncode, 'maximum_SU': MAXIMUM}, exclusive=True)
            assert re.fullmatch(r'\d+\.pbs\d+', job_id), 'Ambiguous qsub response; inspect PBS'
        except Exception as error:
            save(E / 'submission-uncertain.json', {'utc': utc(), 'root': root,
                 'reason': type(error).__name__, 'instruction': 'Retain reservation and inspect PBS; never blindly retry'}, exclusive=True)
            raise
        entry.update(id=job_id,state='SUBMITTED',observed_utc=utc())
        save(intent,{'utc':utc(),'root':root,'files':members,'maximum_SU':MAXIMUM,'parent':parent['job_id'],'state':'SUBMITTED','job_id':job_id})
        budget['updated_utc'] = utc()
        save(budget_path, budget)
        print(job_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('seal', 'deploy', 'submit'))
    action = parser.parse_args().action
    files = payload()
    if action == 'deploy':
        deploy(files)
    elif action == 'submit':
        submit(files)
    else:
        print(json.dumps({'sealed': True, 'file_count': len(files), 'maximum_SU': MAXIMUM}, indent=2))
