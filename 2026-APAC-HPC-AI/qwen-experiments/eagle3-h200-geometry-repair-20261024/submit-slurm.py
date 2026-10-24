"""Submit the frozen H200 correctness diagnostic once under the GPU queue lock."""
from datetime import datetime, timezone
from pathlib import Path
import csv
import fcntl
import json
import sys
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
reference_path = R / 'research-review-25585-20261023/REVIEW.json'
reference = json.loads(reference_path.read_text())
assert reference['state'] == 'H200_TARGET_REFERENCE_ACCEPTED' and reference['accepted_reference'] is True
assert reference['actual_output_token_ids'] == 1600
prepared = json.loads((O / 'prepared.json').read_text())
assert prepared['state'] == 'FROZEN_NOT_SUBMITTED' and prepared['diagnostic_only']
assert prepared['accepted_reference_sha256'] == 'a3b51d20cd6d67a3f659a5f84e6e787f319fb1e5464e5ddc912cdbdd78824c49'
assert json.loads((O / 'validation.json').read_text())['passed']
B = Path(prepared['bundle'])
assert prepared['id'] == 's43-h200-eagle3-geometry-repair'
assert prepared['state'] == 'FROZEN_NOT_SUBMITTED'
assert prepared['model_config_sha256'] == 'f056921e486d3e22aed125b5218b87146ea2ac838ccf1521dea5b08f809e8d59'
assert prepared['payload_sha256'].get('validate_kv_geometry.py') == __import__('hashlib').sha256((B / 'validate_kv_geometry.py').read_bytes()).hexdigest()
assert prepared['bundle_manifest_sha256'] == __import__('hashlib').sha256((B / 'SHA256SUMS').read_bytes()).hexdigest()
subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=B, check=True, capture_output=True)
subprocess.run(['python3', '-B', str(B / 'preflight-assets.py')],
               check=True, capture_output=True)
draft = subprocess.run(['python3', '-B', str(B / 'verify-draft.py'), '--draft',
    '/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09'],
    check=True, capture_output=True, text=True, timeout=60)
(O / 'draft-submit-preflight.json').write_text(draft.stdout)

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
        'sacct', '-X', '-j', '25750', '-P',
        '--format=JobID,State%30,ExitCode,Elapsed,Start,End'], text=True)
    (O / 'source-accounting.txt').write_text(accounting)
    source = list(csv.DictReader(accounting.splitlines(), delimiter='|'))
    assert len(source) == 1 and source[0]['JobID'] == '25750'
    assert source[0]['State'] == 'FAILED' and source[0]['ExitCode'] == '1:0'
    source_run = R / 'runs/25750'
    geometry = subprocess.run([sys.executable, str(B / 'validate_kv_geometry.py'),
        str(source_run / 'kv-geometry'), '--experiment-id',
        'eagle3-h200-worker-bytes-25750-2844ef21-162d-42ac-8331-a898ff682f01',
        '--expected-role', 'prefill-0=4', '--expected-role', 'prefill-1=4',
        '--expected-role', 'decode-0=8'], capture_output=True, text=True, check=True)
    assert json.loads(geometry.stdout)['receipt_count'] == 32
    receipt = dict(id=prepared['id'], bundle=str(B), state='SUBMISSION_IN_PROGRESS',
                   attempted_utc=now(), requested_gpus=16, nodes=2, minutes=17,
                   diagnostic_only=True, pbs_su_reserved=0,
                   asset_manifest_sha256=prepared['asset_manifest_sha256'],
                   purpose='Narrow D-role geometry metadata validator repair after actual job 25750; retain 1600-ID/reference/runtime gates; no score')
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
         expected_result='H200_EAGLE3_CANDIDATE_ACCEPTED_EXACT_IDS_AND_RUNTIME_RECEIPTS',
         expected_output_ids=1600, scored_benchmark=False))
    print(job, prepared['id'], '16 H200 / 17 minutes / no PBS SU', flush=True)
