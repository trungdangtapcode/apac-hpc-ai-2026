"""Independently replay collected native40 outputs after terminal accounting."""
from pathlib import Path
import hashlib
import json
import re
import statistics
import math

from native_output import review_native_output
from run import comparison_metrics

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
accepted = {key: json.loads((E / name).read_text()) for key, name in [('scotch', 'accepted-source-manifest.json'), ('zyx', 'accepted-zyx-source-manifest.json')]}
source_fields = {}
for key in ['scotch', 'zyx']:
    for suffix in ['source-before.json', 'source-after.json']:
        assert json.loads((run / (key + '-' + suffix)).read_text())['manifest'] == accepted[key]
    source_fields[key] = json.loads((run / (key + '-source-fields.json')).read_text())
arms = []
cd_traces = {}
for label, handler in [('B1-our-zyx', 'collated'), ('A1-scotch', 'collated'), ('A2-scotch', 'collated'), ('B2-our-zyx', 'collated')]:
    key = 'zyx' if label.startswith('B') else 'scotch'
    arm = run / 'arms' / label
    log, times, cd, counts = review_native_output(arm)
    assert re.search(r'^I/O\s*:\s*' + handler + r'\b', log, re.M)
    assert json.loads((arm / 'return-code.json').read_text())['returncode'] == 0
    assert json.loads((arm / 'postsolve-fields.json').read_text()) == source_fields[key]
    copied = json.loads((run / (label + '-copy.json')).read_text())
    assert copied['passed'] and copied['manifest'] == accepted[key] and copied['no_source_inodes_reused']
    command = json.loads((arm / 'command.json').read_text())['command']
    base = ['mpirun', '-np', '56', '--report-bindings', '--display-map', '--map-by', 'socket', '--bind-to', 'core']
    common = base + ['--', 'simpleFoam', '-parallel', '-fileHandler', 'collated']
    assert command == common
    saved = next(a for a in comparison['arms'] if a['arm'] == label)
    assert saved['timings_seconds'] == times and saved['Cd_by_step'] == cd
    cd_traces[label] = cd
    arms.append({'arm': label,
                 'p95_nearest_rank_s_step': sorted(times)[math.ceil(0.95 * len(times)) - 1],
                 'first10_mean_s_step': statistics.mean(times[:10]),
                 'last10_mean_s_step': statistics.mean(times[-10:]),
                 'population_cv_percent': 100 * statistics.pstdev(times) / statistics.mean(times), 'mean_s_step': statistics.mean(times),
                 'median_s_step': statistics.median(times), 'maximum_s_step': max(times),
                 'steps': 40, 'intervals': 39, 'final_Cd': cd[-1][1],
                 'fixed_iterations': counts,
                 'native_sample_recommendation': re.findall(r'Minimum number of measured time steps[^\n]*', log)})
before = json.loads((run / 'runtime-before.json').read_text())
after = json.loads((run / 'runtime-after.json').read_text())
assert before['tools'] == after['tools'] and before['libraries'] == after['libraries']
result = {'passed': True, 'job_id': job, 'scheduler': collection['scheduler'],
          'all_transfer_hashes_verified': True, 'all_native_gates_passed': True,
          'scored_result': False, 'arms': arms,
          **comparison_metrics(arms),
          'same_method_repeat_Cd_exact_match': {key: cd_traces[first] == cd_traces[second] for key, first, second in [('scotch', 'A1-scotch', 'A2-scotch'), ('zyx', 'B1-our-zyx', 'B2-our-zyx')]},
          'cross_method_Cd_first_repeats_max_absolute_difference': max(abs(a[1] - b[1]) for a, b in zip(cd_traces['A1-scotch'], cd_traces['B1-our-zyx'])),
          'Cd_comparison_scope': 'Diagnostic method-specific trajectory difference; not a universal Basic +/-0.5% acceptance gate.',
          'inspection_required_before_claim': ['Read native warnings/stderr, sampling recommendations and resource logs; diagnostic summary is not a causal profile.', 'Full Cd/timing arrays remain in the collected comparison.json; inspect nonlinear drift and repeat consistency.', 'No sustained frequency, bandwidth/cycles, NUMA pages or solver helper-affinity counters were collected.'],
          'limits': ['One BAAB allocation under common teammate runtime on Iris; inspect adjacent/repeat consistency and nonlinear drift before attributing a gain.',
                     'No Gadi/NSCC performance result; no actual solver helper affinity or hardware bandwidth counters.']}
(out / 'REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
