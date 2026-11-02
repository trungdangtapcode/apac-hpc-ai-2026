"""Independently replay a completed 20-step Iris xyz/Scotch directional screen."""
from pathlib import Path
import hashlib
import json
import re
import statistics

from native_output import review_native_output
from sampler import validate_sample_file

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
sampler_gate = json.loads((run / 'sampler-preflight.json').read_text())
accepted = {
    'scotch': json.loads((E / 'accepted-source-manifest.json').read_text()),
    'xyz': json.loads((E / 'accepted-xyz-source-manifest.json').read_text()),
}
source_fields = {}
for key in ['scotch', 'xyz']:
    for suffix in ['source-before.json', 'source-after.json']:
        assert json.loads((run / (key + '-' + suffix)).read_text())['manifest'] == accepted[key]
    source_fields[key] = json.loads((run / (key + '-source-fields.json')).read_text())
arms = []
for label, handler in [('S1-scotch', 'uncollated'), ('X1-hierarchical-xyz', 'uncollated'),
                       ('X2-hierarchical-xyz', 'uncollated'), ('S2-scotch', 'uncollated')]:
    key = 'xyz' if label.startswith('X') else 'scotch'
    arm = run / 'arms' / label
    log, times, cd, counts = review_native_output(arm)
    assert re.search(r'^I/O\s*:\s*' + handler + r'\b', log, re.M)
    assert json.loads((arm / 'return-code.json').read_text())['returncode'] == 0
    assert json.loads((arm / 'postsolve-fields.json').read_text()) == source_fields[key]
    copied = json.loads((run / (label + '-copy.json')).read_text())
    assert copied['passed'] and copied['manifest'] == accepted[key] and copied['no_source_inodes_reused']
    command = json.loads((arm / 'command.json').read_text())['command']
    expected = ['mpirun', '-np', '56', '--report-bindings', '--display-map', '--', 'simpleFoam', '-parallel']
    assert command == expected
    saved = next(a for a in comparison['arms'] if a['arm'] == label)
    assert saved['timings_seconds'] == times and saved['Cd_by_step'] == cd
    assert len(times) == 19 and len(cd) == 20
    telemetry = json.loads((arm / 'telemetry-status.json').read_text())
    samples_path = arm / 'telemetry-samples.jsonl'
    sample_check = validate_sample_file(samples_path, optional=True)
    samples = []
    if samples_path.is_file():
        for line in samples_path.read_text().splitlines():
            if line.strip(): samples.append(json.loads(line))
    assert telemetry.get('sample_count', 0) == len(samples) == sample_check['sample_count']
    if sampler_gate.get('enabled'):
        assert telemetry.get('state') in ('sampling', 'unavailable')
        if telemetry.get('state') == 'sampling': assert samples
    else:
        assert telemetry.get('state') == 'disabled_by_preflight' and not samples
    for sample in samples:
        assert sample['collection_ms'] >= 0 and sample['timestamp_utc'] and sample['timestamp_monotonic_seconds'] > 0
        assert isinstance(sample.get('availability'), dict) and isinstance(sample.get('pressure'), dict)
        assert all(name in sample['pressure'] for name in ('cpu','io','memory'))
    collection_ms = [sample['collection_ms'] for sample in samples]
    arms.append({'arm': label, 'mean_s_step': statistics.mean(times),
                 'median_s_step': statistics.median(times), 'maximum_s_step': max(times),
                 'steps': 20, 'intervals': 19, 'final_Cd': cd[-1][1],
                 'fixed_iterations': counts,
                 'native_sample_recommendation': re.findall(r'Minimum number of measured time steps[^\n]*', log),
                 'node_sampler': {'state': telemetry.get('state'), 'sample_count': len(samples),
                                  'sample_bytes': sample_check['bytes'],
                                  'sampler_exit': telemetry.get('stop'),
                                  'collection_ms_max': max(collection_ms) if collection_ms else None,
                                  'all_sample_sources_explicit': all(isinstance(row.get('availability'), dict) for row in samples),
                                  'scope': 'Diagnostic aggregate procfs series; collection duration is not an interference estimate.'}})
before = json.loads((run / 'runtime-before.json').read_text())
after = json.loads((run / 'runtime-after.json').read_text())
assert before['tools'] == after['tools'] and before['libraries'] == after['libraries']
result = {'passed': True, 'job_id': job, 'scheduler': collection['scheduler'],
          'all_transfer_hashes_verified': True, 'all_native_gates_passed': True,
          'scored_result': False, 'classification': 'directional_only_19_intervals_not_confirmatory',
          'telemetry_summary_only': 'Five-second whole-node sampling; inspect raw per-arm JSONL and availability fields. Do not infer causality or observer interference from collection_ms.',
          'arms': arms,
          'hierarchical_xyz_vs_scotch_percent': 100 * ((arms[1]['mean_s_step'] + arms[2]['mean_s_step']) / (arms[0]['mean_s_step'] + arms[3]['mean_s_step']) - 1),
          'first_adjacent_X1_vs_S1_percent': 100 * (arms[1]['mean_s_step'] / arms[0]['mean_s_step'] - 1),
          'reverse_adjacent_X2_vs_S2_percent': 100 * (arms[2]['mean_s_step'] / arms[3]['mean_s_step'] - 1),
          'control_repeat_S2_vs_S1_percent': 100 * (arms[3]['mean_s_step'] / arms[0]['mean_s_step'] - 1),
          'candidate_repeat_X2_vs_X1_percent': 100 * (arms[2]['mean_s_step'] / arms[1]['mean_s_step'] - 1),
          'limits': ['One short ABBA allocation is directional only; xyz historically recommended 361 samples versus 19 observed.',
                     'No improvement, contest score, NSCC or Gadi result is established by this Iris screen.',
                     'No hardware bandwidth or solver helper-affinity claim; report missing telemetry explicitly.',
                     'Five-second procfs samples are diagnostic; collection_ms is not an interference estimate.']}
(out / 'REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
