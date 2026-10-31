"""Compare reviewed HPC chunk ports with source-bound same-day H200 references."""
from pathlib import Path
import ast
import datetime
import json
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent
jobs = (27777, 27783, 27804, 27806)
reviews = {j: json.loads((Q / f'h200-full-load-review-20261026/review-{j}.json').read_text()) for j in jobs}
assert all(r['state'] == 'LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY' for r in reviews.values())

def args(job, role):
    text = (Q / f'runs/{job}/{role}.log').read_text()
    records = [line.split('server_args=', 1)[1] for line in text.splitlines() if 'server_args=ServerArgs(' in line]
    assert len(records) == 1
    root = ast.parse(records[0], mode='eval').body
    return {kw.arg: ast.dump(kw.value, include_attributes=False) for kw in root.keywords}

def compare(old, new, allowed_prefill):
    result = {}
    for role in ('prefill-0', 'prefill-1', 'decode-0'):
        a, b = args(old, role), args(new, role)
        delta = {k: [a.get(k), b.get(k)] for k in a.keys() | b.keys() if a.get(k) != b.get(k)}
        allowed = {'random_seed'} if role == 'decode-0' else allowed_prefill
        assert set(delta) <= allowed, (old, new, role, sorted(delta))
        result[role] = delta
    return result

changes = {
    'HPC4096_to_6144': compare(27783, 27804, {'random_seed', 'chunked_prefill_size', 'cuda_graph_config'}),
    'HPC4096_to_8192': compare(27783, 27806, {'random_seed', 'chunked_prefill_size', 'cuda_graph_config'}),
    'DeepGEMM8192_to_HPC8192': compare(27777, 27806,
        {'random_seed', 'moe_runner_backend', 'speculative_moe_runner_backend'}),
}
account = subprocess.check_output(['sacct', '-X', '-j', '27804,27806', '-P',
    '--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList'], text=True)
fields = [row.split('|') for row in account.splitlines()]
terminal = [dict(zip(fields[0], row)) for row in fields[1:] if row[0] in ('27804', '27806')]
assert len(terminal) == 2 and all(row['State'] == 'COMPLETED' and row['ExitCode'] == '0:0' for row in terminal)
queue = subprocess.check_output(['squeue', '-h', '-u', 'apacsc42', '-o', '%i|%j|%T|%M|%D|%R'], text=True)
assert not any(line.split('|')[0] in ('27804', '27806') for line in queue.splitlines())
scores = {j: reviews[j]['summary']['good_output_tokens_s'] for j in jobs}
comparison = dict(
    reviewed_vietnam_time=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
    hardware='16 H200, g1/g4', state='TWO_REVIEWED_LOCAL_PASSES_NO_INCUMBENT_GAIN',
    scores_good_output_tokens_per_second=scores,
    HPC6144_vs_HPC4096_percent=100 * (scores[27804] / scores[27783] - 1),
    HPC8192_vs_HPC4096_percent=100 * (scores[27806] / scores[27783] - 1),
    HPC6144_vs_incumbent_percent=100 * (scores[27804] / scores[27777] - 1),
    HPC8192_vs_incumbent_percent=100 * (scores[27806] / scores[27777] - 1),
    serving_argument_changes=changes, terminal_accounting=terminal, fresh_queue=queue,
    actual_pair_GPU_hours=sum(16 * int(row['ElapsedRaw']) / 3600 for row in terminal),
    maximum_pair_GPU_hours=2 * 16 * 17 / 60, PBS_SU=0, official_accuracy='UNKNOWN',
    requested_additional_distinct_ports=4, admitted_additional_distinct_ports=2,
    missing_qualified_candidate_slots=2, promotion=False,
    decision='Larger chunks recover performance in the HPC-Ops branch, but retain DeepGEMM prefill/chunk8192. No unchanged repeat or blind extrapolation.',
    limits='Single runs and prior same-day controls, not contemporaneous interleaving. Engine seeds vary. Chunk settings include native dependent prefill graph ranges. Runner comparison includes an inactive speculative-runner fallback field, no draft. No per-request queue/compute/transport decomposition or kernel causal proof.')
target = D / 'comparison.json'
assert not target.exists(), 'Preserve existing comparison'
target.write_text(json.dumps(comparison, indent=2) + '\n')
print(json.dumps({key: comparison[key] for key in ('state', 'HPC6144_vs_HPC4096_percent',
    'HPC8192_vs_HPC4096_percent', 'HPC6144_vs_incumbent_percent', 'HPC8192_vs_incumbent_percent', 'actual_pair_GPU_hours')}))
