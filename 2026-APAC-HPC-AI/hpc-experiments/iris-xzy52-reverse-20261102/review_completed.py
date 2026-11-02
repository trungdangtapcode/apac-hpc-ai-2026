"""Independently replay the native xzy/Scotch result and summarize limits."""
from pathlib import Path
import hashlib
import json
import re
import statistics

from native_output import review_native_output
from run import ARMS, SOURCES, comparison_metrics, method_key, nearest_rank, solver_launch

E = Path(__file__).resolve().parent
job = json.loads((E / 'submission-receipt.json').read_text())['job_id']
out = E / ('completed-' + job)
collection = json.loads((out / 'collection.json').read_text())
assert collection['scheduler']['State'] == 'COMPLETED'
assert collection['scheduler']['ExitCode'] == '0:0'
assert collection['scheduler']['AllocCPUS'] == '56'
root = out / 'collected'
for rel, meta in collection['files'].items():
    raw = (root / rel).read_bytes()
    assert len(raw) == meta['bytes'] and hashlib.sha256(raw).hexdigest() == meta['sha256']

run = root / 'runs' / job
comparison = json.loads((run / 'comparison.json').read_text())
assert comparison['passed'] and comparison['scored_result'] is False
assert [row['arm'] for row in comparison['arms']] == ARMS
accepted = {
    'scotch': json.loads((E / 'accepted-source-manifest.json').read_text()),
    'xzy': json.loads((E / 'accepted-xzy-source-manifest.json').read_text()),
}
source_fields = {}
for key in ('scotch', 'xzy'):
    for suffix in ('source-before.json', 'source-after.json'):
        assert json.loads((run / (key + '-' + suffix)).read_text())['manifest'] == accepted[key]
    source_fields[key] = json.loads((run / (key + '-source-fields.json')).read_text())

rows = []
all_cd = {}
all_resource = {}
for label in ARMS:
    key = method_key(label)
    arm = run / 'arms' / label
    log, times, cd, counts = review_native_output(arm)
    assert re.search(r'^I/O\s*:\s*uncollated\b', log, re.M)
    assert json.loads((arm / 'return-code.json').read_text())['returncode'] == 0
    assert json.loads((arm / 'postsolve-fields.json').read_text()) == source_fields[key]
    selection = json.loads((run / (label + '-source-selection.json')).read_text())
    assert selection['method_key'] == key
    assert selection['source'] == str(SOURCES[key])
    assert selection['manifest_sha256'] == hashlib.sha256((E / ('accepted-source-manifest.json' if key == 'scotch' else 'accepted-xzy-source-manifest.json')).read_bytes()).hexdigest()
    copied = json.loads((run / (label + '-copy.json')).read_text())
    assert copied['passed'] and copied['manifest'] == accepted[key] and copied['no_source_inodes_reused']
    command = json.loads((arm / 'command.json').read_text())['command']
    assert command == solver_launch(label)
    saved = next(row for row in comparison['arms'] if row['arm'] == label)
    assert saved['timings_seconds'] == times and saved['Cd_by_step'] == cd
    assert saved['steps'] == 52 and saved['intervals'] == 51
    assert saved['mean_s_step'] == statistics.mean(times)
    assert saved['p95_s_step_nearest_rank'] == nearest_rank(times, .95)
    assert saved['p99_s_step_nearest_rank'] == nearest_rank(times, .99)
    rows.append({'arm': label, 'method_key': key,
        'mean_s_step': statistics.mean(times), 'median_s_step': statistics.median(times),
        'p95_s_step_nearest_rank': nearest_rank(times, .95),
        'p99_s_step_nearest_rank': nearest_rank(times, .99), 'max_s_step': max(times),
        'steps': 52, 'intervals': 51, 'final_Cd': cd[-1][1], 'fixed_iterations': counts,
        'native_sample_recommendation': re.findall(r'Minimum number of measured time steps[^\n]*', log)})
    all_cd[label] = {int(row[0]): row[1] for row in cd}
    resource = (arm / 'resource-time.log').read_text()
    parsed = {}
    for key_name, pattern in {
        'user_seconds': r'User time \(seconds\):\s*([\d.]+)',
        'system_seconds': r'System time \(seconds\):\s*([\d.]+)',
        'cpu_percent': r'Percent of CPU this job got:\s*([\d.]+)%',
        'max_rss_kib': r'Maximum resident set size \(kbytes\):\s*(\d+)',
        'major_faults': r'Major \(requiring I/O\) page faults:\s*(\d+)',
        'swaps': r'Swaps:\s*(\d+)',
    }.items():
        match = re.search(pattern, resource)
        parsed[key_name] = float(match[1]) if match else None
    all_resource[label] = parsed

before = json.loads((run / 'runtime-before.json').read_text())
after = json.loads((run / 'runtime-after.json').read_text())
assert before['tools'] == after['tools'] and before['libraries'] == after['libraries']
metrics = comparison_metrics(rows)
repeat = {}
for key, pair in [('scotch', ('A1-scotch', 'A2-scotch')),
                  ('xzy', ('B1-our-xzy', 'B2-our-xzy'))]:
    deltas = [abs(all_cd[pair[0]][step] - all_cd[pair[1]][step]) for step in range(1, 53)]
    repeat[key] = {'arms': list(pair), 'mean_absolute_repeat_delta_Cd': statistics.mean(deltas),
                   'maximum_absolute_repeat_delta_Cd': max(deltas),
                   'final_Cd_by_arm': {label: all_cd[label][52] for label in pair}}
mean_xzy = [(all_cd['B1-our-xzy'][i] + all_cd['B2-our-xzy'][i]) / 2 for i in range(1, 53)]
mean_scotch = [(all_cd['A1-scotch'][i] + all_cd['A2-scotch'][i]) / 2 for i in range(1, 53)]
between_cd = [abs(a - b) for a, b in zip(mean_xzy, mean_scotch)]

result = {'passed': True, 'job_id': job, 'scheduler': collection['scheduler'],
    'all_transfer_hashes_verified': True, 'all_native_gates_passed': True,
    'scored_result': False, 'arms': rows, **metrics,
    'resources_gnu_time': all_resource,
    'Cd_repeat_diagnostics_by_method': repeat,
    'method_mean_Cd_trajectory': {'mean_absolute_stepwise_delta': statistics.mean(between_cd),
        'maximum_absolute_stepwise_delta': max(between_cd), 'final_mean_Cd_xzy': mean_xzy[-1],
        'final_mean_Cd_scotch': mean_scotch[-1]},
    'limits': ['One native reverse-order ABBA allocation on Iris; inspect adjacent and repeat consistency plus nonlinear drift before attributing a gain.',
        'Structural interface counts are not solver-speed predictions; busiest-rank surface may offset lower total interface count.',
        'Cd comparisons are descriptive; no task-specific acceptance tolerance is imposed here.',
        'No Gadi/NSCC performance result. Hardware bandwidth, solver helper affinity and NUMA page residency were not collected.']}
(out / 'REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
