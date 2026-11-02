#!/usr/bin/env python3
"""Submit one qualified gateway-readiness repair acceptance entry under the shared lock."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl
import getpass
import hashlib
import json
import re
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent
manifest = json.loads((D / 'FROZEN_PAYLOAD.json').read_text())
B = Path(manifest['payload'])
A = D / 'admission'


def now():
    return datetime.now(timezone.utc).isoformat()


def save(name, data):
    (A / name).write_text(json.dumps(data, indent=2) + '\n')


def run(command):
    return subprocess.run(command, cwd=B, text=True, capture_output=True)


with (Q / '.slurm-admission.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    assert json.loads((D / 'validation.json').read_text())['passed']
    assert not A.exists(), 'Existing admission must be reconciled; no blind re-submission.'
    A.mkdir()
    for entry in manifest['files']:
        assert hashlib.sha256((B / entry['path']).read_bytes()).hexdigest() == entry['sha256']
    check = run(['sha256sum', '-c', 'SHA256SUMS'])
    assert check.returncode == 0, check.stderr
    queue = run(['squeue', '-h', '-u', getpass.getuser(), '-o', '%i|%T|%j|%R'])
    assert queue.returncode == 0, queue.stderr
    assert len([row for row in queue.stdout.splitlines() if row.strip()]) < 5
    site = run(['scontrol', 'show', 'partition', 'hpcai'])
    assert site.returncode == 0 and 'State=UP' in site.stdout and 'MaxTime=00:17:00' in site.stdout
    save('before.json', {'utc': now(), 'own_queue': queue.stdout, 'partition': site.stdout})
    dry = run(['sbatch', '--test-only', '--parsable', 'submit.sbatch'])
    save('test-only.json', {'utc': now(), 'returncode': dry.returncode, 'stdout': dry.stdout, 'stderr': dry.stderr})
    assert dry.returncode == 0, dry.stderr
    reservation = {
        'utc': now(), 'state': 'RESERVED_BEFORE_SBATCH', 'H200': 16, 'nodes': 2,
        'maximum_minutes': 17, 'maximum_GPU_hours': 16 * 17 / 60, 'PBS_SU': 0,
        'own_active_pending_cap': 5, 'owner_authority': '2 November final-entry acceptance continuation: one bounded readiness-race repair after 28194',
        'source_zip_sha256': manifest['source_zip_sha256'],
        'internal_manifest_sha256': manifest['internal_sha256sums_sha256'],
    }
    save('reservation.json', reservation)
    actual = run(['sbatch', '--parsable', 'submit.sbatch'])
    receipt = {'utc': now(), 'returncode': actual.returncode, 'stdout': actual.stdout,
               'stderr': actual.stderr, 'payload': str(B / 'submit.sbatch'), 'cwd': str(B)}
    save('submission-receipt.json', receipt)
    assert actual.returncode == 0, 'Saved definite failure; inspect before any new attempt.'
    assert re.fullmatch(r'\d+(?:;[\w.-]+)?', actual.stdout.strip()), 'Uncertain receipt: reconcile, never submit twice.'
    job = int(actual.stdout.strip().split(';')[0])
    receipt.update(job=job, state='SUBMITTED_NOT_MEASURED')
    reservation.update(job=job, state='SUBMITTED')
    save('submission-receipt.json', receipt)
    save('reservation.json', reservation)
    state = run(['scontrol', 'show', 'job', str(job)])
    save('scheduler-after.json', {'utc': now(), 'returncode': state.returncode, 'stdout': state.stdout, 'stderr': state.stderr})
    print(json.dumps({'job': job, 'state': 'SUBMITTED_NOT_MEASURED', 'payload': str(B),
                      'maximum_GPU_hours': reservation['maximum_GPU_hours']}))
