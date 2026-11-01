"""Independently replay collected native40 outputs after terminal accounting."""
from pathlib import Path
import hashlib
import json
import re
import statistics

from native_output import review_native_output

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
accepted = json.loads((E / 'accepted-source-manifest.json').read_text())
for name in ['source-before.json', 'source-after.json']:
    assert json.loads((run / name).read_text())['manifest'] == accepted
source_fields = json.loads((run / 'source-fields.json').read_text())
arms = []
for label, handler in [('A1-organizer', 'uncollated'), ('B1-teammate', 'collated'), ('B2-teammate', 'collated'), ('A2-organizer', 'uncollated')]:
    arm = run / 'arms' / label
    log, times, cd, counts = review_native_output(arm)
    assert re.search(r'^I/O\s*:\s*' + handler + r'\b', log, re.M)
    assert json.loads((arm / 'return-code.json').read_text())['returncode'] == 0
    assert json.loads((arm / 'postsolve-fields.json').read_text()) == source_fields
    copied = json.loads((run / (label + '-copy.json')).read_text())
    assert copied['passed'] and copied['manifest'] == accepted and copied['no_source_inodes_reused']
    command = json.loads((arm / 'command.json').read_text())['command']
    base = ['mpirun', '-np', '56', '--report-bindings', '--display-map']
    mapping = ['--map-by', 'socket', '--bind-to', 'core'] if label.startswith('B') else []
    common = base + mapping + ['--', 'simpleFoam', '-parallel']
    assert command == common + (['-fileHandler', 'collated'] if label.startswith('B') else [])
    saved = next(a for a in comparison['arms'] if a['arm'] == label)
    assert saved['timings_seconds'] == times and saved['Cd_by_step'] == cd
    arms.append({'arm': label, 'mean_s_step': statistics.mean(times),
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
          'teammate_vs_organizer_percent': 100 * ((arms[1]['mean_s_step'] + arms[2]['mean_s_step']) / (arms[0]['mean_s_step'] + arms[3]['mean_s_step']) - 1),
          'first_adjacent_B1_vs_A1_percent': 100 * (arms[1]['mean_s_step'] / arms[0]['mean_s_step'] - 1),
          'reverse_adjacent_B2_vs_A2_percent': 100 * (arms[2]['mean_s_step'] / arms[3]['mean_s_step'] - 1),
          'control_repeat_A2_vs_A1_percent': 100 * (arms[3]['mean_s_step'] / arms[0]['mean_s_step'] - 1),
          'candidate_repeat_B2_vs_B1_percent': 100 * (arms[2]['mean_s_step'] / arms[1]['mean_s_step'] - 1),
          'limits': ['One ABBA allocation on Iris; inspect adjacent/repeat consistency and nonlinear drift before attributing a gain.',
                     'No Gadi/NSCC performance result; no actual solver helper affinity or hardware bandwidth counters.']}
(out / 'REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
