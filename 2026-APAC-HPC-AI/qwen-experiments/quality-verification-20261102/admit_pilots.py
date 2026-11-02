#!/usr/bin/env python3
"""Admit exactly the two qualified local-quality pilots, recording every scheduler receipt."""
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
targets = {'reference': S / 'jobs/reference-pilot',
           'candidate': S / 'jobs/candidate-pilot/AI_Task/job_scripts'}


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')


def command(argv, cwd=S):
    r = subprocess.run(argv, cwd=cwd, text=True, capture_output=True)
    return {'utc': now(), 'argv': argv, 'cwd': str(cwd), 'returncode': r.returncode,
            'stdout': r.stdout, 'stderr': r.stderr}


with (Q / '.slurm-admission.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    assert json.loads((S / 'validation.json').read_text())['passed']
    prepared = json.loads((S / 'prepared-4k/prepare-manifest.json').read_text())
    assert prepared['status'] == 'READY' and prepared['question_count'] == 12032 and prepared['pilot_count'] == 128
    frozen = json.loads((S / 'frozen-pilot/FROZEN_PAYLOAD.json').read_text())
    for item in frozen['files']:
        assert hashlib.sha256((S / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
    assert not (S / 'admission').exists(), 'Reconcile existing admissions; do not submit duplicate pilots.'
    A = S / 'admission'
    A.mkdir()
    queue = command(['squeue', '-h', '-u', getpass.getuser(), '-o', '%i|%T|%j|%R'])
    site = command(['scontrol', 'show', 'partition', 'hpcai'])
    save(A / 'before.json', {'utc': now(), 'queue': queue, 'partition': site})
    assert queue['returncode'] == site['returncode'] == 0
    assert len([line for line in queue['stdout'].splitlines() if line.strip()]) + 2 <= 5
    assert 'State=UP' in site['stdout'] and 'MaxTime=00:17:00' in site['stdout']
    assert (S / 'jobs/reference-pilot/logs').is_dir()
    assert (targets['candidate'].parent / 'logs/slurm').is_dir()
    dry = {}
    for role, cwd in targets.items():
        check = command(['sbatch', '--test-only', '--parsable', 'submit.sbatch'], cwd)
        dry[role] = check
        save(A / (role + '-test-only.json'), check)
        assert check['returncode'] == 0, check['stderr']
    reservation = {'utc': now(), 'state': 'RESERVED_BEFORE_SUBMISSION',
                   'owner_authority': 'Explicit request to research and measure model quality now',
                   'purpose': 'paired 128-question local accuracy feasibility pilots; full-set follows review',
                   'allocations': 2, 'gpus_each': 16, 'nodes_each': 2, 'maximum_minutes_each': 17,
                   'maximum_GPU_hours': 2 * 16 * 17 / 60, 'PBS_SU': 0, 'own_active_pending_cap': 5,
                   'frozen_manifest_sha256': hashlib.sha256((S / 'frozen-pilot/FROZEN_PAYLOAD.json').read_bytes()).hexdigest(),
                   'jobs': {}}
    save(A / 'reservation.json', reservation)
    for role, cwd in targets.items():
        receipt = command(['sbatch', '--parsable', 'submit.sbatch'], cwd)
        save(A / (role + '-submission-receipt.json'), receipt)
        assert receipt['returncode'] == 0, 'Inspect saved failed receipt; never submit blindly.'
        raw = receipt['stdout'].strip()
        assert re.fullmatch(r'\d+(?:;[\w.-]+)?', raw), 'Ambiguous acceptance: reconcile scheduler before any further action.'
        job = int(raw.split(';')[0])
        receipt.update(job=job, role=role, state='SUBMITTED_NOT_MEASURED', payload=str(cwd / 'submit.sbatch'))
        save(A / (role + '-submission-receipt.json'), receipt)
        reservation['jobs'][role] = job
        reservation['state'] = 'SUBMITTED' if len(reservation['jobs']) == 2 else 'PARTIALLY_SUBMITTED'
        save(A / 'reservation.json', reservation)
        save(A / (role + '-scheduler-after.json'), command(['scontrol', 'show', 'job', str(job)]))
        print(json.dumps({'role': role, 'job': job, 'state': 'SUBMITTED_NOT_MEASURED'}), flush=True)
