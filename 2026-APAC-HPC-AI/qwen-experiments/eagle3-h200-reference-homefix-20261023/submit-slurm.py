"""Submit the frozen H200 correctness diagnostic once under the GPU queue lock."""
from datetime import datetime, timezone
from pathlib import Path
import csv
import fcntl
import json
import re
import subprocess

O = Path(__file__).resolve().parent
R = O.parent
RECEIPT = O / 'slurm-receipt.json'


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


assert not RECEIPT.exists(), 'Never retry a recorded or uncertain submission'
failure_path = R / 'research-review-25495-20261023/REVIEW.json'
failure = json.loads(failure_path.read_text())
assert failure['state'] == 'FAILED_CLIENT_CONTAINER_HOME_MOUNT' and not failure['accepted_reference']

prepared = json.loads((O / 'prepared.json').read_text())
assert prepared['state'] == 'FROZEN_NOT_SUBMITTED' and prepared['diagnostic_only']
assert json.loads((O / 'validation.json').read_text())['passed']
B = Path(prepared['bundle'])
subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=B,
               check=True, capture_output=True)
subprocess.run(['python3', '-B', str(B / 'preflight-assets.py')],
               check=True, capture_output=True)
with (R / 'serving-tuning/watcher.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    assert not RECEIPT.exists(), 'Concurrent submission was already recorded'
    partition = subprocess.check_output(['scontrol', 'show', 'partition', 'hpcai'], text=True)
    (O / 'partition-preflight.txt').write_text(partition)
    limit = re.search(r'MaxTime=(\S+)', partition).group(1)
    assert limit == 'UNLIMITED' or sum(int(v) * f for v, f in
                                     zip(limit.split(':'), (3600, 60, 1))) >= 1020
    queue = subprocess.check_output(['squeue', '-h', '-u', 'apacsc42',
                                     '-o', '%i|%T|%j'], text=True)
    (O / 'slurm-pre-submit.txt').write_text(queue)
    assert len(queue.splitlines()) + 1 <= 5, 'Five-job own queue cap'
    accounting = subprocess.check_output([
        'sacct', '-X', '-j', '25373', '-P',
        '--format=JobID,State%30,ExitCode,Elapsed,Start,End'], text=True)
    (O / 'source-accounting.txt').write_text(accounting)
    source = list(csv.DictReader(accounting.splitlines(), delimiter='|'))
    assert len(source) == 1 and source[0]['JobID'] == '25373'
    assert source[0]['State'] == 'COMPLETED' and source[0]['ExitCode'] == '0:0'
    proof = json.loads((R / 'research-review-25373-20261022/REVIEW.json').read_text())
    assert proof['state'] == 'LOCAL_PROTOCOL_SLA_OUTPUT_PASS'
    receipt = dict(id=prepared['id'], bundle=str(B), state='SUBMISSION_IN_PROGRESS',
                   attempted_utc=now(), requested_gpus=16, nodes=2, minutes=17,
                   diagnostic_only=True, pbs_su_reserved=0,
                   asset_manifest_sha256=prepared['asset_manifest_sha256'],
                   purpose='Repair proven missing token-client HOME in 25495; unchanged exact-ID reference protocol')
    save(RECEIPT, receipt)
    try:
        result = subprocess.run(['sbatch', '--parsable', str(B / 'job.sbatch')],
                                cwd=R, capture_output=True, text=True, timeout=60)
    except Exception:
        receipt['state'] = 'SUBMISSION_UNCERTAIN'
        save(RECEIPT, receipt)
        raise
    (O / 'submission.stdout').write_text(result.stdout)
    (O / 'submission.stderr').write_text(result.stderr)
    job = result.stdout.strip().split(';')[0]
    if result.returncode or not job.isdigit():
        receipt['state'] = 'SUBMISSION_UNCERTAIN'
        save(RECEIPT, receipt)
        raise RuntimeError('Inspect scheduler; do not retry blindly')
    receipt.update(state='SUBMITTED', job=job, submitted_utc=now())
    save(RECEIPT, receipt)
    detail = subprocess.check_output(['scontrol', 'show', 'job', job], text=True)
    (O / (job + '-detail.txt')).write_text(detail)
    assert 'TimeLimit=00:17:00' in detail and 'Reason=PartitionTimeLimit' not in detail
    (O / 'slurm-post-submit.txt').write_text(subprocess.check_output([
        'squeue', '-u', 'apacsc42', '-o', '%i|%T|%M|%j|%R'], text=True))
    # Keep correctness diagnostics out of the serving-score registry.
    save(O / 'diagnostic-status.json', dict(job=job, state='SUBMITTED',
         expected_result='H200_TARGET_REFERENCE_SEMANTIC_GATE_PASSED',
         expected_output_ids=1600, scored_benchmark=False))
    print(job, prepared['id'], '16 H200 / 17 minutes / no PBS SU', flush=True)
