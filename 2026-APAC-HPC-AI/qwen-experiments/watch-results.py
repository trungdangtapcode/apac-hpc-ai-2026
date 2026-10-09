"""Observe only our submitted jobs; keep reports current while Slurm queues them."""
import csv
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent
ids = ['22130', '22131', '22135', '22143', '22147', '22197', '22200']
terminal = {'COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT', 'NODE_FAIL',
            'OUT_OF_MEMORY', 'PREEMPTED', 'BOOT_FAIL', 'DEADLINE', 'REVOKED'}
previous = None

def update_tracker(status):
    path = Path('/home/apacsc42/workspace/research-optimization/experiments.csv')
    with path.open(newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    existing = {r['experiment']: r for r in rows}
    for metric in json.loads((root / 'comparison.json').read_text()):
        key = f"J{metric['job']}-{metric['phase']}-N{metric['concurrency']}"
        row = existing.get(key)
        if row is None:
            row = dict.fromkeys(fields, '')
            rows.append(row)
            existing[key] = row
        row.update(experiment=key, task='qwen', priority='1',
                   status='measured_pass' if metric['sla_pass'] else 'measured_fail_sla',
                   change=f"{metric['topology']}; N{metric['concurrency']}; {metric['phase']}",
                   platform='Firmus H200', job_id=metric['job'],
                   good_fraction=metric['good_request_fraction'],
                   good_output_tokens_s=metric['good_output_tokens_s'],
                   ttft_ms=metric['ttft_avg_ms'], itl_ms=metric['itl_avg_ms'],
                   notes=f"Local only; accuracy not checked; cancelled={metric['cancelled_requests']}")
    existing['Q01'].update(status=status.get('22135', {}).get('State', 'unknown').lower(), job_id='22135')
    existing['Q03'].update(status=status.get('22131', {}).get('State', 'unknown').lower(), job_id='22131')
    # Q02 tracks the additional baseline confirmation; Q06 remains a final submission plan.
    existing['Q02'].update(status=status.get('22197', {}).get('State', 'unknown').lower(),
                          job_id='22197', notes='Full N32; fixed metrics conflict 22143 and registration race 22147')
    temp = path.with_suffix('.csv.tmp')
    with temp.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)

while True:
    try:
        out = subprocess.run(
            ['sacct', '-j', ','.join(ids), '-X', '-P',
             '--format=JobID,State,ExitCode,Elapsed,Start,End'],
            capture_output=True, text=True, check=True, timeout=20,
        )
        status = {r['JobID']: r for r in csv.DictReader(out.stdout.splitlines(), delimiter='|')}
        temp = root / 'job-status.json.tmp'
        temp.write_text(json.dumps(status, indent=2))
        temp.replace(root / 'job-status.json')
        subprocess.run(['python3', str(root / 'compare.py')],
                       cwd=root, stdout=subprocess.DEVNULL, check=True, timeout=20)
        update_tracker(status)
        subprocess.run(['python3', str(root / 'audit-runs.py')],
                       cwd=root, stdout=subprocess.DEVNULL, check=True, timeout=120)
        states = {job: row['State'] for job, row in status.items()}
        if states != previous:
            print(datetime.now(timezone.utc).isoformat(), states, flush=True)
            previous = states
        if all(job in status and status[job]['State'].split()[0].rstrip('+') in terminal for job in ids):
            print('All submitted jobs finished; reports updated. Watcher exits.', flush=True)
            break
    except Exception as error:
        print(datetime.now(timezone.utc).isoformat(), type(error).__name__, str(error), flush=True)
    time.sleep(30)
