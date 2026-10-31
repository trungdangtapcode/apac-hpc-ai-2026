"""Admit two phase ports and their explicit H200 control under the shared Slurm lock."""
from pathlib import Path
import datetime
import fcntl
import getpass
import hashlib
import json
import re
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')

def run(args):
    return subprocess.run(args, cwd=Q, text=True, capture_output=True)

assert json.loads((D / 'validation.json').read_text())['passed']
prep = json.loads((D / 'preparation.json').read_text())
assert len(prep['bundles']) == 3
with (Q / '.slurm-admission.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    assert not (D / 'admission').exists(), 'Existing admission must be reconciled; never retry uncertain sbatch.'
    A = D / 'admission'
    A.mkdir()
    snap = run(['sinfo', '-p', 'hpcai', '-h', '-o', '%P|%a|%l|%D|%t|%N'])
    assert snap.returncode == 0 and 'hpcai' in snap.stdout, snap.stderr
    save(A / 'site-snapshot.json', dict(utc=now(), output=snap.stdout))
    for item in prep['bundles']:
        B = Q / item['bundle']
        R = A / B.name
        R.mkdir()
        queue = run(['squeue', '-h', '-u', getpass.getuser(), '-o', '%i|%T|%j|%R'])
        assert queue.returncode == 0, queue.stderr
        lines = [line for line in queue.stdout.splitlines() if line.strip()]
        assert len(lines) < 5, 'Own active/pending cap five reached'
        manifest = hashlib.sha256((B / 'SHA256SUMS').read_bytes()).hexdigest()
        assert manifest == item['manifest_sha256']
        verify = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=B, text=True, capture_output=True)
        assert verify.returncode == 0, verify.stderr
        dry = run(['sbatch', '--test-only', '--parsable', str(B / 'job.sbatch')])
        assert dry.returncode == 0, dry.stderr
        reservation = dict(utc=now(), state='RESERVED_BEFORE_SBATCH', H200=16, nodes=2,
                           minutes=17, maximum_GPU_hours=16*17/60, PBS_SU=0,
                           queue_before=queue.stdout, manifest_sha256=manifest,
                           study_arm='phase_inference_'+item['phase'], owner_authority='31 October H100-to-H200 verification')
        save(R / 'reservation.json', reservation)
        actual = run(['sbatch', '--parsable', str(B / 'job.sbatch')])
        receipt = dict(utc=now(), returncode=actual.returncode, stdout=actual.stdout,
                       stderr=actual.stderr, test_only_stderr=dry.stderr,
                       payload=str(B / 'job.sbatch'), manifest_sha256=manifest)
        save(R / 'submission-receipt.json', receipt)
        assert actual.returncode == 0, 'sbatch failed: inspect saved receipt; do not retry blindly'
        assert re.fullmatch(r'\d+(?:;[\w.-]+)?', actual.stdout.strip()), 'Uncertain submission outcome; stop and reconcile'
        job = int(actual.stdout.strip().split(';')[0])
        receipt.update(job=job, state='SUBMITTED_NOT_MEASURED')
        reservation.update(job=job, state='SUBMITTED')
        save(R / 'submission-receipt.json', receipt)
        save(R / 'reservation.json', reservation)
        control = run(['scontrol', 'show', 'job', str(job)])
        save(R / 'scheduler-after.json', dict(utc=now(), returncode=control.returncode,
                                             output=control.stdout, stderr=control.stderr))
        print(json.dumps(dict(job=job, concurrency=item['concurrency'], phase=item['phase'], state='SUBMITTED_NOT_MEASURED')), flush=True)
    final = run(['squeue', '-h', '-u', getpass.getuser(), '-o', '%i|%T|%j|%R'])
    assert final.returncode == 0, final.stderr
    save(A / 'queue-after.json', dict(utc=now(), output=final.stdout))
