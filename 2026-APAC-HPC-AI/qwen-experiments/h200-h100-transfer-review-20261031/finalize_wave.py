"""Audit the four reviewed H200 trials and exact serving-argument comparisons."""
from pathlib import Path
import ast
import datetime
import json
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent
JOBS = (27777, 27779, 27781, 27783)

def nodes(job, role):
    text = (Q / f'runs/{job}/{role}.log').read_text()
    rows = [s.split('server_args=', 1)[1] for s in text.splitlines() if 'server_args=ServerArgs(' in s]
    assert len(rows) == 1
    return {kw.arg: kw.value for kw in ast.parse(rows[0], mode='eval').body.keywords}

def compare(a, b, allowed_prefill, allowed_decode):
    result = {}
    for role in ('prefill-0', 'prefill-1', 'decode-0'):
        x, y = nodes(a, role), nodes(b, role)
        delta = {key: [ast.dump(x[key], include_attributes=False), ast.dump(y[key], include_attributes=False)]
                 for key in x.keys() | y.keys()
                 if key not in x or key not in y or ast.dump(x[key]) != ast.dump(y[key])}
        allowed = allowed_decode if role == 'decode-0' else allowed_prefill
        assert set(delta) <= allowed, (a, b, role, sorted(delta))
        assert ast.literal_eval(y['speculative_algorithm']) is None
        result[role] = delta
    return result

reviews = {job: json.loads((Q / f'h200-full-load-review-20261026/review-{job}.json').read_text()) for job in JOBS}
assert all(r['state'] == 'LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY' for r in reviews.values())
account = subprocess.check_output(['sacct', '-X', '-j', ','.join(map(str, JOBS)), '-P',
    '--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList'], text=True)
rows = [line.split('|') for line in account.splitlines()]
accounts = {int(row[0]): dict(zip(rows[0], row)) for row in rows[1:] if row[0] in set(map(str, JOBS))}
assert set(accounts) == set(JOBS)
assert all(row['State'] == 'COMPLETED' and row['ExitCode'] == '0:0' for row in accounts.values())
queue = subprocess.check_output(['squeue', '-h', '-u', 'apacsc42', '-o', '%i|%j|%T|%M|%D|%R'], text=True)
assert not any(line.split('|')[0] in set(map(str, JOBS)) for line in queue.splitlines())
changes = {
    'control_to_FA3': compare(27777, 27779, {'random_seed'}, {'random_seed', 'decode_attention_backend'}),
    'H100_recipe_N54_to_N64': compare(27781, 27783, {'random_seed'}, {'random_seed'}),
    'control_to_H100_recipe_N64': compare(27777, 27783,
        {'random_seed', 'moe_runner_backend', 'chunked_prefill_size', 'cuda_graph_config', 'speculative_moe_runner_backend'},
        {'random_seed'}),
}
# Native chunk derivation: preserve the common graph fields and exactly truncate prefill buckets.
for role in ('prefill-0', 'prefill-1'):
    graphs = []
    for job in (27777, 27783):
        graph = {kw.arg: kw.value for kw in nodes(job, role)['cuda_graph_config'].keywords}
        prefill = {kw.arg: ast.literal_eval(kw.value) for kw in graph['prefill'].keywords}
        graphs.append(prefill)
    assert graphs[0]['max_bs'] == 8192 and graphs[1]['max_bs'] == 4096
    assert graphs[1]['bs'] == [size for size in graphs[0]['bs'] if size <= 4096]
    assert {k: v for k, v in graphs[0].items() if k not in ('max_bs', 'bs')} == {
        k: v for k, v in graphs[1].items() if k not in ('max_bs', 'bs')}
scores = {job: reviews[job]['summary']['good_output_tokens_s'] for job in JOBS}
result = dict(checked_vietnam_time=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
    state='ALL_FOUR_REVIEWED_LOCAL_PASSES_NO_NEW_WINNER', hardware='16 H200, g1/g4',
    scores_good_output_tokens_per_second=scores, serving_argument_changes=changes,
    FA3_vs_control_percent=100 * (scores[27779] / scores[27777] - 1),
    H100_recipe_N64_vs_control_percent=100 * (scores[27783] / scores[27777] - 1),
    H100_recipe_N64_vs_N54_percent=100 * (scores[27783] / scores[27781] - 1),
    total_actual_GPU_hours=sum(16 * int(row['ElapsedRaw']) / 3600 for row in accounts.values()),
    total_maximum_reserved_GPU_hours=4 * 16 * 17 / 60, PBS_SU=0, accounting=accounts,
    fresh_queue=queue, official_accuracy='UNKNOWN', promotion=False,
    decision='Retain H200 DeepGEMM-prefill/chunk8192 and FlashInfer decode. Close these losing ports without unchanged repeats.',
    limits='One run per arm; generated engine seeds vary. Recipe changes runner and chunk with native dependent graph/fallback fields. N54/N64 is load sensitivity, not a pure hardware ratio. No official quality certification.')
target = D / 'final-comparison.json'
assert not target.exists(), 'Preserve the prior final comparison'
target.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('state', 'FA3_vs_control_percent',
    'H100_recipe_N64_vs_control_percent', 'H100_recipe_N64_vs_N54_percent', 'total_actual_GPU_hours')}))
