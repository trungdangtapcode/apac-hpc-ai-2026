"""Extend existing independent terminal reviews and seal the two H100-derived chunk trials."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import math
import statistics
import subprocess
import sys

D = Path(__file__).resolve().parent
Q = D.parent

def distribution(values):
    values = sorted(values)
    if not values:
        return None
    def percentile(p):
        x = (len(values) - 1) * p
        lo, hi = math.floor(x), math.ceil(x)
        return values[lo] + (values[hi] - values[lo]) * (x - lo)
    return dict(count=len(values), min=values[0], mean=statistics.mean(values),
                p50=percentile(.5), p95=percentile(.95), p99=percentile(.99), max=values[-1])

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def args(job, role):
    text = (Q / f'runs/{job}/{role}.log').read_text()
    rows = [line.split('server_args=', 1)[1] for line in text.splitlines()
            if 'server_args=ServerArgs(' in line]
    assert len(rows) == 1
    call = ast.parse(rows[0], mode='eval').body
    assert isinstance(call, ast.Call)
    return {kw.arg: ast.dump(kw.value, include_attributes=False) for kw in call.keywords}

for job in map(int, sys.argv[1:]):
    assert job in (27804, 27806)
    A = Q / f'runs/{job}'
    destination = D / f'result-{job}.json'
    assert not destination.exists(), 'Preserve existing extended review'
    r = json.loads((Q / f'h200-full-load-review-20261026/review-{job}.json').read_text())
    assert r['state'] == 'LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY'
    cfg = json.loads((A / 'config.json').read_text())
    n = cfg['concurrency']
    account_text = subprocess.check_output([
        'sacct', '-X', '-j', str(job), '-P',
        '--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList,AllocTRES'], text=True)
    fields = [line.split('|') for line in account_text.splitlines()]
    account = [dict(zip(fields[0], row)) for row in fields[1:] if row[0] == str(job)]
    assert len(account) == 1 and account[0]['State'] == 'COMPLETED' and account[0]['ExitCode'] == '0:0'
    assert str(job) not in subprocess.check_output(['squeue', '-h', '-u', 'apacsc42', '-o', '%i'], text=True).split()
    rows = [json.loads(line) for line in (A / f'confirm/n{n}/artifacts/profile_export.jsonl').open()]
    rows = [row for row in rows if row['metadata']['benchmark_phase'] == 'profiling']
    lo = min(row['metadata']['request_start_ns'] for row in rows)
    hi = max(row['metadata']['request_start_ns'] for row in rows)
    hardware = {}
    for path in (A / 'resource-telemetry').glob('*.jsonl'):
        samples = [json.loads(line) for line in path.open()]
        role = samples[0]['role']
        samples = [s for s in samples if s['kind'] == 'sample' and lo <= s['utc_ns'] <= hi]
        metrics = {}
        for key in ('utilization.gpu', 'utilization.memory', 'memory.used', 'power.draw',
                    'temperature.gpu', 'clocks.sm', 'clocks.mem'):
            values, missing = [], 0
            for sample in samples:
                for gpu in sample.get('gpus', []):
                    try:
                        value = float(gpu[key])
                        assert math.isfinite(value)
                    except (KeyError, TypeError, ValueError, AssertionError):
                        missing += 1
                        continue
                    values.append(value)
            metrics[key] = dict(distribution=distribution(values), missing_or_unsupported=missing)
        hardware[role] = dict(sample_rows=len(samples), metrics=metrics)
    warm_path = A / 'pair-warmup-failed-responses.jsonl'
    failed_warmup = [json.loads(line) for line in warm_path.open()] if warm_path.exists() else []
    delta = None
    if job == 27779:
        delta = {}
        for role in ('prefill-0', 'prefill-1', 'decode-0'):
            control, candidate = args(27777, role), args(job, role)
            changes = {key: [control.get(key), candidate.get(key)]
                       for key in control.keys() | candidate.keys()
                       if control.get(key) != candidate.get(key)}
            allowed = {'random_seed', 'decode_attention_backend'} if role == 'decode-0' else {'random_seed'}
            assert not set(changes) - allowed, (role, changes)
            delta[role] = changes
    (A / 'scheduler-accounting.psv').write_text(account_text)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
    result = dict(job=job, reviewed_vietnam_time=now, state=r['state'], hardware='16 H200 on g1/g4',
                  concurrency=n, summary=r['summary'], raw_fixed_workload=r['raw_fixed_workload'],
                  ttft_breaches=r['ttft_breaches'], itl_breaches=r['itl_breaches'],
                  runtime=json.loads((A / 'runtime-readiness.json').read_text()),
                  raw_log_review=r['runtime'], telemetry=r['telemetry_in_admission_envelope'],
                  hardware_distributions=hardware,
                  latency_distributions_ms={key: distribution([row['metrics'][key]['value'] for row in rows])
                      for key in ('time_to_first_token', 'inter_token_latency', 'request_latency')},
                  setup_failed_response_counts={str(code): sum(row.get('http_status') == code for row in failed_warmup)
                      for code in sorted({row.get('http_status') for row in failed_warmup}, key=str)},
                  serving_argument_changes_vs_control=delta,
                  actual_GPU_hours=16 * int(account[0]['ElapsedRaw']) / 3600,
                  maximum_reserved_GPU_hours=16 * 17 / 60, PBS_SU=0, scheduler=account[0],
                  official_accuracy='UNKNOWN', promotion=False,
                  limits='One run per recipe. Setup retries precede scoring. Sparse five-second samples in request-start envelope; clocks uncalibrated. No heavy kernel, per-thread, Xid/throttle-reason profile or authoritative output token IDs. GPU activity, VRAM and KV token occupancy are different metrics.')
    destination.write_text(json.dumps(result, indent=2) + '\n')
    manifest = A / 'artifact-manifest.json'
    if not manifest.exists():
        files = []
        for path in sorted(A.rglob('*')) + [Q / f'runs/{job}.out', Q / f'runs/{job}.err']:
            if not path.is_file() or path.is_symlink() or '__pycache__' in path.parts or path == manifest:
                continue
            before = path.stat()
            digest = sha(path)
            after = path.stat()
            assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
            files.append(dict(path=str(path.relative_to(Q)), bytes=after.st_size, sha256=digest))
        manifest.write_text(json.dumps(dict(job=job, sealed_vietnam_time=now,
                                            terminal_accounting=account[0], files=files), indent=2) + '\n')
    print(json.dumps(dict(job=job, state=result['state'], good_tokens_s=r['summary']['good_output_tokens_s'],
                         actual_GPU_hours=result['actual_GPU_hours'])))
