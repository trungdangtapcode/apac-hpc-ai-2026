"""Submit the reviewed policy pair serially without displacing correctness job25682."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RECEIPT = HERE / 'slurm-receipt.json'


def save(record):
    temp = RECEIPT.with_suffix('.tmp')
    temp.write_text(json.dumps(record, indent=2) + '\n')
    temp.replace(RECEIPT)


def own_queue():
    result = subprocess.run(['squeue', '-h', '-u', 'apacsc42', '-o', '%A|%T|%j'],
                            capture_output=True, text=True, check=True)
    return [line for line in result.stdout.splitlines() if line.strip()]


def main():
    assert not RECEIPT.exists(), 'Do not retry an existing/uncertain submission'
    frozen = json.loads((HERE / 'frozen.json').read_text())
    assert frozen['ready_for_slurm'] and json.loads((HERE / 'validation.json').read_text())['passed']
    queue = own_queue()
    assert len(queue) + 2 <= 5, 'Own active/pending cap is five'
    (HERE / 'pre-submit-queue.txt').write_text('\n'.join(queue) + '\n')
    partition = subprocess.run(['scontrol', 'show', 'partition', 'hpcai', '-o'],
                               capture_output=True, text=True, check=True).stdout
    (HERE / 'partition-preflight.txt').write_text(partition)
    assert 'MaxTime=00:17:00' in partition, 'Review changed partition limit before submitting'
    parent = subprocess.run(['scontrol', 'show', 'job', '25682', '-o'],
                            capture_output=True, text=True, check=True).stdout
    (HERE / 'parent-25682-preflight.txt').write_text(parent)
    assert 'UserId=apacsc42(' in parent and 's39-h200-eagle3-correctness' in parent
    bundles = [Path(x) for x in frozen['bundles']]
    for bundle in bundles:
        subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=bundle,
                       capture_output=True, check=True)
    record = dict(state='PREPARED_FOR_SUBMISSION', started_utc=datetime.now(timezone.utc).isoformat(),
                  parent_job='25682', gpus_per_job=16, nodes_per_job=2, minutes_per_job=17,
                  pbs_su_reserved=0, screen_unranked=True, jobs=[])
    for index, bundle in enumerate(bundles):
        assert len(own_queue()) < 5, 'Own cap reached before this submission'
        dependency = 'afterany:25682' if index == 0 else 'afterok:' + record['jobs'][0]['job']
        row = dict(bundle=str(bundle), dependency=dependency, state='SUBMISSION_IN_PROGRESS',
                   manifest_sha256=hashlib.sha256((bundle / 'SHA256SUMS').read_bytes()).hexdigest())
        record['jobs'].append(row)
        save(record)
        try:
            result = subprocess.run(['sbatch', '--parsable', '--dependency=' + dependency,
                                     str(bundle / 'job.sbatch')], cwd=ROOT,
                                    capture_output=True, text=True, timeout=30)
        except Exception:
            row['state'] = record['state'] = 'SUBMISSION_UNCERTAIN'
            save(record)
            raise
        (HERE / f'submit-{index}.stdout').write_text(result.stdout)
        (HERE / f'submit-{index}.stderr').write_text(result.stderr)
        match = re.fullmatch(r'(\d+)(?:;[\w.-]+)?\s*', result.stdout)
        if result.returncode != 0 or match is None:
            row['state'] = record['state'] = 'SUBMISSION_UNCERTAIN'
            save(record)
            raise RuntimeError('Inspect scheduler before any retry; never duplicate an uncertain sbatch')
        row.update(job=match[1], state='SUBMITTED', submitted_utc=datetime.now(timezone.utc).isoformat())
        save(record)
    record['state'] = 'SUBMITTED_SERIAL_PAIR'
    save(record)
    (HERE / 'post-submit-queue.txt').write_text('\n'.join(own_queue()) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
