"""Complete phase-mode comparison using the fresh explicit H200 control."""
from pathlib import Path
import ast
import datetime
import json
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent
JOBS = (27826, 27828, 27830)
reviews = {j: json.loads((Q / f'h200-full-load-review-20261026/review-{j}.json').read_text()) for j in JOBS}
assert all(r['state'] == 'LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY' for r in reviews.values())

def args(job, role):
    text = (Q / f'runs/{job}/{role}.log').read_text()
    records = [line.split('server_args=', 1)[1] for line in text.splitlines() if 'server_args=ServerArgs(' in line]
    assert len(records) == 1
    return {kw.arg: ast.dump(kw.value, include_attributes=False)
            for kw in ast.parse(records[0], mode='eval').body.keywords}

activation, changes, workers = {}, {}, []
for job in JOBS:
    A = Q / f'runs/{job}'
    cfg = json.loads((A / 'config.json').read_text())
    runtime = json.loads((A / 'runtime-readiness.json').read_text())
    assert runtime['state'] == 'PASS_FAST_RUNTIME'
    activation[job], changes[job] = {}, {}
    for role in ('prefill-0', 'prefill-1', 'decode-0'):
        wanted = cfg['phase_inference_mode']['prefill' if role.startswith('prefill') else 'decode']
        actual = runtime['roles'][role]['native_provider_preflight_inference_mode']
        assert actual is wanted
        activation[job][role] = actual
        baseline, candidate = args(27826, role), args(job, role)
        delta = {key: [baseline.get(key), candidate.get(key)] for key in baseline.keys() | candidate.keys()
                 if baseline.get(key) != candidate.get(key)}
        assert not (set(delta) - {'random_seed'}), (job, role, sorted(delta))
        changes[job][role] = delta
    worker = (A / 'submitted-payload/worker.sh').read_text()
    for value in ('0', '1'):
        worker = worker.replace('export SGLANG_ENABLE_TORCH_INFERENCE_MODE=' + value,
                                'export SGLANG_ENABLE_TORCH_INFERENCE_MODE=PHASE_VALUE')
    workers.append(worker)
assert len(set(workers)) == 1
account = subprocess.check_output(['sacct', '-X', '-j', ','.join(map(str, JOBS)), '-P',
    '--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList'], text=True)
lines = [line.split('|') for line in account.splitlines()]
terminal = [dict(zip(lines[0], row)) for row in lines[1:] if row[0] in set(map(str, JOBS))]
assert len(terminal) == 3 and all(row['State'] == 'COMPLETED' and row['ExitCode'] == '0:0' for row in terminal)
queue = subprocess.check_output(['squeue', '-h', '-u', 'apacsc42', '-o', '%i|%j|%T|%M|%D|%R'], text=True)
assert not any(line.split('|')[0] in set(map(str, JOBS)) for line in queue.splitlines())
scores = {j: reviews[j]['summary']['good_output_tokens_s'] for j in JOBS}
comparison = dict(
    reviewed_vietnam_time=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
    hardware='16 H200, g1/g4', state='THREE_LOCAL_PASSES_NO_USEFUL_PHASE_GAIN',
    scores_good_output_tokens_per_second=scores,
    decode_only_vs_explicit_control_percent=100 * (scores[27828] / scores[27826] - 1),
    prefill_only_vs_explicit_control_percent=100 * (scores[27830] / scores[27826] - 1),
    native_role_provider_preflight_activation=activation,
    resolved_serving_argument_changes=changes, frozen_worker_change_is_phase_flags_only=True,
    actual_three_job_GPU_hours=sum(16 * int(row['ElapsedRaw']) / 3600 for row in terminal),
    maximum_three_job_GPU_hours=3 * 16 * 17 / 60, PBS_SU=0,
    terminal_accounting=terminal, fresh_queue=queue, official_accuracy='UNKNOWN', promotion=False,
    requested_four_distinct_ports_reviewed=[27804, 27806, 27828, 27830],
    extra_explicit_control_not_a_candidate=27826,
    decision='Retain the current H200 recipe and native default provider. Both phase gains are below the prospective 1% useful-gain gate; no unchanged repeat or combined-mode sweep.',
    limits='One run per arm, generated engine seeds vary and node/cache state is not controlled. Role-level provider preflight and inherited environment are verified; no per-rank steady-state mode/kernel trace or direct queue/compute/transfer decomposition. Source H100 studies used a different base recipe/load; these are intervention ports, not full-recipe reproductions.')
target = D / 'comparison.json'
assert not target.exists(), 'Preserve previous review'
target.write_text(json.dumps(comparison, indent=2) + '\n')
print(json.dumps({key: comparison[key] for key in ('state', 'decode_only_vs_explicit_control_percent',
    'prefill_only_vs_explicit_control_percent', 'actual_three_job_GPU_hours')}))
