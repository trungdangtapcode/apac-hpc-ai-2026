#!/usr/bin/env python3
"""Admit one diagnosed FP8 geometry correction; preserve existing candidate queue position."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl
import getpass
import hashlib
import json
import re
import subprocess

S = Path(__file__).resolve().parent
Q = S.parent
B = S / 'jobs/reference-pilot-r2'


def now():
    return datetime.now(timezone.utc).isoformat()


def cmd(argv, cwd=S):
    p = subprocess.run(argv, cwd=cwd, text=True, capture_output=True)
    return {'utc': now(), 'argv': argv, 'cwd': str(cwd), 'returncode': p.returncode,
            'stdout': p.stdout, 'stderr': p.stderr}


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')


with (Q / '.slurm-admission.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    assert not (S / 'admission-reference-r2').exists(), 'Reconcile existing receipt; never submit twice.'
    A = S / 'admission-reference-r2'
    A.mkdir()
    frozen = json.loads((S / 'frozen-reference-r2/FROZEN_PAYLOAD.json').read_text())
    for row in frozen['files']:
        assert hashlib.sha256((S / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    old = cmd(['sacct', '-j', '28367', '-X', '--noheader', '--parsable2', '--format=JobID,State,ExitCode,ElapsedRaw'])
    queue = cmd(['squeue', '-u', getpass.getuser(), '-h', '-o', '%i|%T|%j|%R'])
    site = cmd(['scontrol', 'show', 'partition', 'hpcai'])
    save(A / 'before.json', {'original_accounting': old, 'queue': queue, 'partition': site})
    assert old['returncode'] == queue['returncode'] == site['returncode'] == 0
    records = [line.split('|') for line in old['stdout'].splitlines() if line.startswith('28367|')]
    assert len(records) == 1 and records[0][1] == 'FAILED'
    assert not any(line.startswith('28367|') for line in queue['stdout'].splitlines())
    assert len([line for line in queue['stdout'].splitlines() if line.strip()]) < 5
    assert 'State=UP' in site['stdout'] and 'MaxTime=00:17:00' in site['stdout']
    assert (B / 'logs').is_dir()
    dry = cmd(['sbatch', '--test-only', '--parsable', 'submit.sbatch'], B)
    save(A / 'test-only.json', dry)
    assert dry['returncode'] == 0, dry['stderr']
    cost = 16 * int(records[0][3]) / 3600
    reservation = {'utc': now(), 'state': 'RESERVED_BEFORE_SUBMISSION',
                   'purpose': 'native EP8 FP8 block-geometry correction after failed reference 28367',
                   'owner_authority': 'Explicit quality measurement objective; diagnosed necessary reference continuation',
                   'maximum_GPU_hours': 16 * 17 / 60, 'PBS_SU': 0,
                   'failed_reference_actual_GPU_hours': cost,
                   'candidate_maximum_GPU_hours': 16 * 17 / 60,
                   'current_actual_plus_outstanding_maximum_GPU_hours': cost + 2 * 16 * 17 / 60,
                   'candidate_job_untouched': 28368,
                   'frozen_manifest_sha256': hashlib.sha256((S / 'frozen-reference-r2/FROZEN_PAYLOAD.json').read_bytes()).hexdigest()}
    save(A / 'reservation.json', reservation)
    receipt = cmd(['sbatch', '--parsable', 'submit.sbatch'], B)
    save(A / 'submission-receipt.json', receipt)
    assert receipt['returncode'] == 0, 'Inspect the saved receipt before any retry.'
    assert re.fullmatch(r'\d+(?:;[\w.-]+)?', receipt['stdout'].strip()), 'Ambiguous scheduler acceptance.'
    job = int(receipt['stdout'].strip().split(';')[0])
    receipt.update(job=job, role='reference-r2', state='SUBMITTED_NOT_MEASURED')
    reservation.update(job=job, state='SUBMITTED')
    save(A / 'submission-receipt.json', receipt)
    save(A / 'reservation.json', reservation)
    save(A / 'scheduler-after.json', cmd(['scontrol', 'show', 'job', str(job)]))
    initial = json.loads((S / 'admission/reservation.json').read_text())
    initial.update(state='ORIGINAL_REFERENCE_RETIRED_FAILED_CANDIDATE_OUTSTANDING',
                   reference_actual_GPU_hours=cost, original_reference_reservation_retired=True,
                   reference_replacement_job=job, candidate_job_unchanged=28368)
    save(S / 'admission/reservation.json', initial)
    print(json.dumps({'job': job, 'role': 'reference-r2', 'state': 'SUBMITTED_NOT_MEASURED',
                      'current_actual_plus_outstanding_max_GPU_hours': reservation['current_actual_plus_outstanding_maximum_GPU_hours']}))
