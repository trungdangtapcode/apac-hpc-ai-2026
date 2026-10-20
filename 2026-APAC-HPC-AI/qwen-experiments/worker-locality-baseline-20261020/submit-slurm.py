"""Submit one reviewed locality baseline once, retaining uncertain outcomes."""
import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

O = Path(__file__).resolve().parent
R = O.parent
D = R / 'serving-tuning'
receipt = O / 'slurm-receipt.json'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


assert not receipt.exists(), 'Prior submission receipt exists: never blindly retry'
assert json.loads((O / 'validation.json').read_text())['passed']
pilot = json.loads((O / 'pilot.json').read_text())
bundle = Path(pilot['bundle'])
with (D / 'watcher.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    queue = subprocess.check_output(['squeue', '-h', '-u', 'apacsc42', '-o', '%i|%T|%j'], text=True)
    (O / 'slurm-pre-submit.txt').write_text(now() + '\n' + queue)
    assert len([line for line in queue.splitlines() if line.strip()]) + 1 <= 5, 'Five-job cap'
    state = json.loads((D / 'registry.json').read_text())
    assert not any(e['id'] == pilot['id'] for e in state['entries'])
    subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=bundle, capture_output=True, check=True)
    hashes = {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
              for f in bundle.iterdir() if f.is_file() and f.name != 'SHA256SUMS'}
    record = dict(id=pilot['id'], state='SUBMISSION_IN_PROGRESS', attempted_utc=now(),
                  bundle=str(bundle), payload_sha256=hashes)
    save(receipt, record)
    try:
        result = subprocess.run(['sbatch', '--parsable', str(bundle / 'job.sbatch')],
                                cwd=R, capture_output=True, text=True, timeout=45)
    except Exception:
        record['state'] = 'SUBMISSION_UNCERTAIN'
        save(receipt, record)
        raise
    (O / 'submit.stdout').write_text(result.stdout)
    (O / 'submit.stderr').write_text(result.stderr)
    job = result.stdout.strip().split(';')[0]
    if result.returncode or not job.isdigit():
        record['state'] = 'SUBMISSION_UNCERTAIN'
        save(receipt, record)
        raise RuntimeError('No definite sbatch receipt; do not retry')
    record.update(job=job, state='SUBMITTED', submitted_utc=now())
    save(receipt, record)
    entry = dict(pilot, state='ACTIVE', payload_sha256=hashes, measurements=[],
                 missing_ns=[60], benchmark_complete=False, profile_complete=False, traces=[],
                 attempts=[dict(job=job, bundle=str(bundle), state='SUBMITTED',
                                submitted_utc=record['submitted_utc'])])
    state['entries'].append(entry)
    state.update(updated_utc=now(), active=True)
    save(D / 'registry.json', state)
    planpath = R / 'serving-tuning-10/prepared-pilots.json'
    plan = json.loads(planpath.read_text())
    plan['pilots'].append(dict(pilot, state='SUBMITTED', job=job))
    plan.update(updated_utc=now(), state='ACTIVE')
    save(planpath, plan)
    queue = subprocess.check_output(['squeue', '-u', 'apacsc42', '-o', '%.18i %.12P %.34j %.8T %.10M %.6D %R'], text=True)
    (O / 'slurm-post-submit.txt').write_text(now() + '\n' + queue)
    print(job, flush=True)
