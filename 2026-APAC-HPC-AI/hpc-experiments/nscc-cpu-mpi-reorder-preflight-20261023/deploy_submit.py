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
PARENT = '25940700.pbs101'
MAXIMUM = 6.4


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
    root = '/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-mpi-reorder-preflight-' + stamp
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
    assert not intent.exists(), 'Prior intent exists: query PBS instead of retrying'
    d = json.loads((E / 'deployment.json').read_text())
    assert d['files'] == members
    root = d['root']
    assert re.fullmatch(r'/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-mpi-reorder-preflight-\d{8}T\d{6}Z', root)
    with (B / 'cpu-budget.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        assert not intent.exists()
        # Recheck the already deployed bounded text, not a mesh or compute run.
        code = "import json,hashlib;from pathlib import Path;r=Path(" + repr(root) + ");x=json.loads((r/'payload-sha256.json').read_text())['files'];assert all(hashlib.sha256((r/n).read_bytes()).hexdigest()==h for n,h in x.items());print('HASH_PASS')"
        assert remote('python3 -c ' + shlex.quote(code)).stdout.strip() == 'HASH_PASS'
        queue = remote('qstat -u apacsc42').stdout
        ids = re.findall(r'^(\d+\.\S+)\s+apacsc42\b', queue, re.M)
        assert set(ids) == {PARENT}, 'Review changed CPU queue before any submission'
        parent = json.loads(remote('qstat -fx -F json ' + PARENT).stdout)['Jobs'][PARENT]
        assert parent['job_state'] in ('Q', 'R') and str(parent['project']) == '59000042'
        ai = subprocess.run(['bash', str(H / 'workspace/vpn-rootless/vpn.sh'), 'ssh-batch',
                             "bash -lc 'qstat -u apacsc42'"], capture_output=True,
                            text=True, timeout=30, check=True)
        ai_count = len(re.findall(r'^\d+\S*\s+apacsc42\b', ai.stdout, re.M))
        assert len(ids) + ai_count + 1 <= 3, 'Preserve combined PBS job cap'
        project = remote('myprojects -p 59000042').stdout
        rows = [x for x in project.splitlines() if x.startswith('| SU')]
        assert len(rows) == 1
        grant, used, balance, in_doubt = [float(x.strip()) for x in rows[0].split('|')[2:-1]]
        rates = [x for x in project.splitlines() if x.startswith('| CPU Hour')]
        assert grant == 30000 and balance >= MAXIMUM and in_doubt == 0
        assert len(rates) == 1 and float(rates[0].split('|')[3].strip()) == 1
        b = json.loads((B / 'cpu-budget.json').read_text())
        assert b['schema'] == 2 and b['project'] == '59000042'
        consumed = max(b['consumed_ceiling_SU'], math.ceil(used - b['published_snapshot']['used_SU'] + 1))
        committed = consumed + b['outstanding_reserved_max_SU']
        assert committed + MAXIMUM <= b['baseline_wave_planning_ceiling_SU']
        safe_parent = {k: parent[k] for k in ('job_state', 'Resource_List', 'project', 'comment') if k in parent}
        save(E / 'pre-submit-checks.json', dict(utc=utc(), CPU_queue=queue,
             AI_queue_read_only=ai.stdout, combined_PBS_before=len(ids) + ai_count,
             parent=safe_parent, project_report=project, consumed_ceiling_SU=consumed,
             prior_outstanding_max_SU=b['outstanding_reserved_max_SU'],
             new_conservative_maximum_SU=MAXIMUM, requested_core_hour_max_SU=0.2,
             ceiling_SU=b['baseline_wave_planning_ceiling_SU'],
             dependency='afterany:' + PARENT, shared_unknown_maxima_retained=True))
        save(intent, dict(utc=utc(), root=root, files=members, maximum_SU=MAXIMUM,
             dependency='afterany:' + PARENT, state='RESERVED_DO_NOT_RETRY_BLINDLY'), exclusive=True)
        b['consumed_ceiling_SU'] = consumed
        b['outstanding_reserved_max_SU'] += MAXIMUM
        b['planning_committed_SU'] = b['reserved_max_SU'] = consumed + b['outstanding_reserved_max_SU']
        entry = dict(id=None, root=root, maximum_SU=MAXIMUM, requested_maximum_SU=0.2,
                     state='SUBMISSION_INTENT', branch='actual_MPI_world_rank_reorder_interface_preflight',
                     dependency_afterany=PARENT, observed_utc=utc())
        b['jobs'].append(entry)
        b['updated_utc'] = utc()
        save(B / 'cpu-budget.json', b)
        script = next(n for n in members if n.endswith('.pbs'))
        try:
            result = remote('cd ' + shlex.quote(root) + ' && qsub -W ' +
                            shlex.quote('depend=afterany:' + PARENT) + ' ' + shlex.quote(script))
            job = result.stdout.strip()
            save(E / 'submission.json', dict(utc=utc(), root=root, stdout=result.stdout,
                 stderr=result.stderr, returncode=result.returncode, maximum_SU=MAXIMUM,
                 requested_maximum_SU=0.2, dependency_afterany=PARENT), exclusive=True)
            assert re.fullmatch(r'\d+\.pbs\d+', job), 'Ambiguous submission response'
        except Exception as exc:
            save(E / 'submission-uncertain.json', dict(utc=utc(), root=root,
                 reason=type(exc).__name__, instruction='Retain reservation and inspect PBS; never blindly retry'))
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
