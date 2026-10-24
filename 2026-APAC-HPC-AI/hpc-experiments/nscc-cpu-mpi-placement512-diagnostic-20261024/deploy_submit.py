#!/usr/bin/env python3
"""Deploy once and submit one budgeted CPU preflight after the existing job."""
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
R = E.parent
H = R.parents[1]
SSH = R / 'tools/nscc-cpu-ssh.sh'
B = R / 'nscc-cpu-timing-probe-20261021'
PARENTS = ('25940700.pbs101', '25943865.pbs101', '25947168.pbs101')
DEPENDENCY = None
MAXIMUM = 25.6


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
                          capture_output=True, text=True, timeout=60, check=True)


def payload():
    members = {p.relative_to(E).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted((E / 'payload').rglob('*'))
               if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    assert 3 <= len(members) <= 16
    assert sum((E / n).stat().st_size for n in members) < 150000
    assert not any((E / n).is_symlink() for n in members)
    assert len([n for n in members if n.endswith('.pbs')]) == 1
    path = E / 'payload-sha256.json'
    if path.exists():
        assert json.loads(path.read_text())['files'] == members, 'Preserve frozen payload'
    else:
        save(path, dict(created_utc=utc(), files=members), exclusive=True)
    return members


def deploy(members):
    path = E / 'deployment.json'
    assert not path.exists(), 'Deployment exists; inspect, never overwrite'
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    root = '/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-mpi-placement512-diagnostic-' + stamp
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w:gz') as archive:
        for name in [*members, 'payload-sha256.json']:
            archive.add(E / name, arcname=name, recursive=False)
    code = '''from pathlib import Path
import sys,tarfile,io,json,hashlib
r=Path(ROOT);r.mkdir(exist_ok=False)
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
    assert record['root'] == root and record['files'] == members
    record.update(created_utc=utc(), state='DEPLOYED_NOT_SUBMITTED')
    save(path, record, exclusive=True)
    print(root)


def submit(members):
    intent = E / 'submission-intent.json'
    assert not intent.exists(), 'A prior intent must be inspected, never retried blindly'
    reviewed = json.loads((E / 'ROOT_REVIEW.json').read_text())
    assert reviewed['passed'] and reviewed['payload_sha256'] == members
    deployed = json.loads((E / 'deployment.json').read_text())
    assert deployed['files'] == members
    root = deployed['root']
    assert re.fullmatch(r'/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-mpi-placement512-diagnostic-\d{8}T\d{6}Z', root)
    with (B / 'cpu-budget.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        assert not intent.exists()
        code = "import json,hashlib;from pathlib import Path;r=Path(" + repr(root) + ");x=json.loads((r/'payload-sha256.json').read_text())['files'];assert all(hashlib.sha256((r/n).read_bytes()).hexdigest()==h for n,h in x.items());print('HASH_PASS')"
        assert remote('python3 -c ' + shlex.quote(code)).stdout.strip() == 'HASH_PASS'
        queue = remote('qstat -u apacsc42').stdout
        queued = re.findall(r'^(\d+\.\S+)\s+apacsc42\b', queue, re.M)
        assert not queued, 'One active CPU allocation: review any unexpected CPU work first'
        raw = json.loads(remote('qstat -fx -F json ' + ' '.join(PARENTS)).stdout)['Jobs']
        assert set(raw) == set(PARENTS)
        assert all(str(raw[j]['project']) == '59000042' for j in PARENTS)
        assert all(raw[j]['job_state'] == 'F' for j in PARENTS), 'Review all three completed jobs first'
        assert raw[PARENTS[0]]['job_state'] in ('Q', 'R', 'F'), 'Review an unexplained hold on the original confirmation'
        assert sum(raw[j]['job_state'] == 'R' for j in PARENTS) <= 1
        assert {j: raw[j]['Exit_status'] for j in PARENTS} == {'25940700.pbs101': 0, '25943865.pbs101': 0, '25947168.pbs101': 1}, 'Unexpected terminal outcome; do not retry blindly'
        prior_review = json.loads((R / 'completed-review-20261024/review.json').read_text())
        assert prior_review['confirmation_25940700']['native_validator_replay_matches_recorded_json'] and prior_review['placement_512_25947168']['candidate_launched'] is False
        ai = subprocess.run(['bash', str(H / 'workspace/vpn-rootless/vpn.sh'), 'ssh-batch',
                             "bash -lc 'qstat -u apacsc42'"], capture_output=True,
                            text=True, timeout=30, check=True)
        ai_count = len(re.findall(r'^\d+\S*\s+apacsc42\b', ai.stdout, re.M))
        assert len(queued) + ai_count + 1 <= 3, 'Preserve combined PBS cap'
        report = remote('myprojects -p 59000042').stdout
        rows = [line for line in report.splitlines() if line.startswith('| SU')]
        assert len(rows) == 1
        grant, used, balance, in_doubt = [float(x.strip()) for x in rows[0].split('|')[2:-1]]
        rates = [line for line in report.splitlines() if line.startswith('| CPU Hour')]
        assert grant == 30000 and balance >= MAXIMUM and in_doubt >= 0
        assert len(rates) == 1 and float(rates[0].split('|')[3].strip()) == 1
        b = json.loads((B / 'cpu-budget.json').read_text())
        assert b['schema'] == 2 and b['project'] == '59000042'
        parent_maxima = sum(j['maximum_SU'] for j in b['jobs'] if j['id'] in PARENTS)
        assert in_doubt <= parent_maxima, 'Unexplained prepayment: retain budget and review'
        consumed = max(b['consumed_ceiling_SU'], math.ceil(used - b['published_snapshot']['used_SU'] + 1))
        if consumed > b['consumed_ceiling_SU']:
            b['consumed_ceiling_SU'] = consumed
            b['planning_committed_SU'] = b['reserved_max_SU'] = consumed + b['outstanding_reserved_max_SU']
            b['updated_utc'] = utc()
            save(B / 'cpu-budget.json', b)
        assert consumed + b['outstanding_reserved_max_SU'] + MAXIMUM <= b['baseline_wave_planning_ceiling_SU']
        safe_parents = {j: {k: raw[j][k] for k in ('job_state', 'Exit_status', 'Resource_List', 'project', 'comment') if k in raw[j]} for j in PARENTS}
        save(E / 'pre-submit-checks.json', dict(utc=utc(), CPU_queue=queue,
             AI_queue_read_only=ai.stdout, combined_PBS_before=len(queued) + ai_count,
             parents=safe_parents, dependency=DEPENDENCY, project_report=report,
             current_consumed_allowance_SU=consumed, prior_outstanding_maximum_SU=b['outstanding_reserved_max_SU'],
             new_maximum_SU=MAXIMUM, ceiling_SU=b['baseline_wave_planning_ceiling_SU'],
             shared_unknown_maxima_retained=True, scope='Derived topology failure diagnostic. Previous failing payload preserved; only diagnostics and collective failure handling changed. No solver or existing queue modification'))
        save(intent, dict(utc=utc(), root=root, files=members, maximum_SU=MAXIMUM,
             dependency=DEPENDENCY, state='RESERVED_DO_NOT_RETRY_BLINDLY'), exclusive=True)
        b['outstanding_reserved_max_SU'] += MAXIMUM
        b['planning_committed_SU'] = b['reserved_max_SU'] = consumed + b['outstanding_reserved_max_SU']
        entry = dict(id=None, root=root, maximum_SU=MAXIMUM, state='SUBMISSION_INTENT',
                     branch='four_host_512_rank_topology_failure_diagnostic',
                     dependency_afterok=[], reviewed_terminal_jobs=list(PARENTS), observed_utc=utc())
        b['jobs'].append(entry)
        b['updated_utc'] = utc()
        save(B / 'cpu-budget.json', b)
        script = next(name for name in members if name.endswith('.pbs'))
        try:
            result = remote('cd ' + shlex.quote(root) + ' && qsub ' + shlex.quote(script))
            job = result.stdout.strip()
            save(E / 'submission.json', dict(utc=utc(), root=root, stdout=result.stdout,
                 stderr=result.stderr, returncode=result.returncode, maximum_SU=MAXIMUM,
                 dependency_afterok=[], reviewed_terminal_jobs=list(PARENTS)), exclusive=True)
            assert re.fullmatch(r'\d+\.pbs\d+', job), 'Ambiguous submission response'
        except Exception as exc:
            save(E / 'submission-uncertain.json', dict(utc=utc(), root=root,
                 reason=type(exc).__name__, instruction='Retain reservation and inspect PBS; no blind retry'))
            raise
        entry.update(id=job, state='SUBMITTED', observed_utc=utc())
        b['updated_utc'] = utc()
        save(B / 'cpu-budget.json', b)
        print(job)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['seal', 'deploy', 'submit'])
    args = parser.parse_args()
    manifest = payload()
    if args.action == 'deploy':
        deploy(manifest)
    elif args.action == 'submit':
        submit(manifest)
    else:
        print(json.dumps(dict(passed=True, files=len(manifest))))


