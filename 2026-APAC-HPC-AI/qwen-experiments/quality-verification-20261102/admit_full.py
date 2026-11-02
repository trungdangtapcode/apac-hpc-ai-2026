#!/usr/bin/env python3
"""Admit fixed full-corpus shards; qualify the first native-N64 pair before filling the cap."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import fcntl
import getpass
import hashlib
import json
import re
import shlex
import subprocess

S = Path(__file__).resolve().parent
Q = S.parent


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')


def cmd(argv, cwd=S):
    try:
        p = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=60)
        return {'utc': now(), 'argv': argv, 'cwd': str(cwd), 'returncode': p.returncode,
                'stdout': p.stdout, 'stderr': p.stderr}
    except subprocess.TimeoutExpired as exc:
        # A timed-out sbatch may already have been accepted. Preserve ambiguity,
        # never blindly retry, and require scheduler/receipt reconciliation.
        def output(value):
            return value.decode(errors='replace') if isinstance(value, bytes) else (value or '')
        return {'utc': now(), 'argv': argv, 'cwd': str(cwd), 'returncode': None,
                'stdout': output(exc.stdout), 'stderr': output(exc.stderr),
                'error': 'CLI timeout after 60 seconds; actual submission may be ambiguous, no automatic retry.'}


p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--wave', choices=('first', 'fill'), required=True)
p.add_argument('--chain', action='store_true', help='Finite completion callbacks for the remaining fixed shards only; no watcher, retries or Codex.')
a = p.parse_args()
with (Q / '.slurm-admission.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    assert not (S / 'workflow/STOP.json').exists(), 'Finite quality workflow stopped; no further admission.'
    if a.chain:
        assert a.wave == 'fill', 'First pair must be manually reviewed before finite continuation.'
        guard = json.loads((S / 'workflow/CODE_GUARD.json').read_text())
        for row in guard['files']:
            assert hashlib.sha256((S / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    assert json.loads((S / 'frozen-full8/validation.json').read_text())['passed']
    frozen = json.loads((S / 'frozen-full8/FROZEN_PAYLOAD.json').read_text())
    for row in frozen['files']:
        assert hashlib.sha256((S / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    A = S / 'admission-full8'
    A.mkdir(exist_ok=True)
    lp = A / 'ledger.json'
    if lp.exists():
        ledger = json.loads(lp.read_text())
    else:
        ledger = {'created_utc': now(), 'purpose': 'full local MMLU-Pro; not organiser certification',
                  'planned_jobs': 16, 'planned_maximum_GPU_hours': 16 * 16 * 17 / 60,
                  'PBS_SU': 0, 'jobs': {}, 'own_active_pending_cap': 5,
                  'first_pair_qualified': False,
                  'frozen_manifest_sha256': hashlib.sha256((S / 'frozen-full8/FROZEN_PAYLOAD.json').read_bytes()).hexdigest()}
        save(lp, ledger)
    for directory in A.iterdir():
        if directory.is_dir():
            assert directory.name in ledger['jobs'], 'Unreconciled admission directory: inspect receipt, never retry blindly.'
    queue = cmd(['squeue', '-u', getpass.getuser(), '-h', '-o', '%i|%T|%j|%R'])
    site = cmd(['scontrol', 'show', 'partition', 'hpcai'])
    assert queue['returncode'] == site['returncode'] == 0
    assert 'State=UP' in site['stdout'] and 'MaxTime=00:17:00' in site['stdout']
    capacity = 5 - len([line for line in queue['stdout'].splitlines() if line.strip()])
    assert capacity > 0, 'Own active/pending cap is full; retain queue positions.'
    if a.wave == 'first':
        assert not ledger['jobs'], 'First wave is already admitted; do not duplicate it.'
        assert capacity >= 2
        todo = [('reference', 0), ('candidate', 0)]
    else:
        qualification = json.loads((S / 'reviews/first-full-pair-qualification.json').read_text())
        assert qualification['passed'] is True, 'First N64 full pair must qualify service/time/coverage.'
        ledger['first_pair_qualified'] = True
        todo = [(role, k) for k in range(8) for role in ('reference', 'candidate')
                if f'{role}-{k:02d}' not in ledger['jobs']][:capacity]
    for role, k in todo:
        key = f'{role}-{k:02d}'
        assert key not in ledger['jobs'] and len(ledger['jobs']) < 16
        cwd = S / (f'jobs/full-ref-{k:02d}of08' if role == 'reference'
                   else f'jobs/full-cand-{k:02d}of08/AI_Task/job_scripts')
        for prefix in ('#SBATCH --output=', '#SBATCH --error='):
            value = next(line[len(prefix):] for line in (cwd / 'submit.sbatch').read_text().splitlines() if line.startswith(prefix))
            assert (cwd / value).parent.resolve().is_dir(), value
        D = A / key
        D.mkdir(exist_ok=False)
        save(D / 'before.json', {'utc': now(), 'queue': queue, 'partition': site})
        argv = ['sbatch', '--parsable', 'submit.sbatch']
        wrapper = None
        if a.chain:
            # Slurm headers apply to the wrapper allocation; the original frozen
            # science script is then run without any source changes.
            resources = [line[len('#SBATCH '):].strip() for line in (cwd / 'submit.sbatch').read_text().splitlines() if line.startswith('#SBATCH ')]
            assert all(flag.startswith('--') and ' ' not in flag for flag in resources)
            stop = shlex.quote(str(S / 'workflow/STOP.json'))
            driver = shlex.quote(str(cwd / 'submit.sbatch'))
            callback = shlex.quote(str(S / 'workflow/finite_event.py'))
            wrapper = (f'if [ -f {stop} ]; then echo FINITE_WORKFLOW_STOP; exit 86; fi; '
                       f'bash {driver}; driver_rc=$?; '
                       f'python3 {callback} --job "$SLURM_JOB_ID" --role {role} --shard {k} --driver-rc "$driver_rc"; '
                       'callback_rc=$?; if [ "$driver_rc" -ne 0 ]; then exit "$driver_rc"; fi; exit "$callback_rc"')
            argv = ['sbatch', '--parsable', *resources, '--wrap', wrapper]
            save(D / 'finite-wrapper.json', {'utc': now(), 'argv': argv, 'wrapper': wrapper,
                 'original_frozen_payload': str(cwd / 'submit.sbatch'),
                 'purpose': 'Finite fixed 16-shard continuation; no watcher, retry or AI process.',
                 'workflow_code_guard_sha256': hashlib.sha256((S / 'workflow/CODE_GUARD.json').read_bytes()).hexdigest()})
        dry = cmd([argv[0], '--test-only', *argv[1:]], cwd)
        save(D / 'test-only.json', dry)
        assert dry['returncode'] == 0, dry['stderr']
        record = {'utc': now(), 'role': role, 'shard_index': k, 'shard_count': 8,
                  'questions': 1504, 'concurrency': 64, 'gpus': 16, 'nodes': 2,
                  'maximum_minutes': 17, 'maximum_GPU_hours': 16 * 17 / 60, 'PBS_SU': 0,
                  'state': 'RESERVED_BEFORE_SUBMISSION', 'cwd': str(cwd),
                  'payload': str(cwd / 'submit.sbatch'), 'finite_completion_callback': a.chain}
        save(D / 'reservation.json', record)
        receipt = cmd(argv, cwd)
        save(D / 'submission-receipt.json', receipt)
        assert receipt['returncode'] == 0, 'Saved failure: reconcile before another admission.'
        assert re.fullmatch(r'\d+(?:;[\w.-]+)?', receipt['stdout'].strip()), 'Ambiguous receipt; reconcile before any further admission.'
        job = int(receipt['stdout'].strip().split(';')[0])
        receipt.update(job=job, state='SUBMITTED_NOT_MEASURED', role=role, shard_index=k)
        record.update(job=job, state='SUBMITTED')
        save(D / 'submission-receipt.json', receipt)
        save(D / 'reservation.json', record)
        ledger['jobs'][key] = record
        ledger['updated_utc'] = now()
        ledger['submitted_count'] = len(ledger['jobs'])
        ledger['submitted_maximum_GPU_hours'] = sum(x['maximum_GPU_hours'] for x in ledger['jobs'].values())
        save(lp, ledger)
        save(D / 'scheduler-after.json', cmd(['scontrol', 'show', 'job', str(job)]))
        print(json.dumps({'role': role, 'shard': k, 'job': job,
                          'questions': 1504, 'state': 'SUBMITTED_NOT_MEASURED'}), flush=True)
