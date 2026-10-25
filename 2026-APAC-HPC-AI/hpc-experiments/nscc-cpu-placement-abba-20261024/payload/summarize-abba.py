"""Summarize four independently validated runs as two order-balanced paired blocks."""
import argparse
import json
import math
import statistics
from pathlib import Path

ARMS = ('A1', 'B1', 'B2', 'A2')


def percentile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low = int(math.floor(position))
    high = int(math.ceil(position))
    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arms-root', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root = Path(args.arms_root)
    runs = {}
    for arm in ARMS:
        report = json.loads((root / arm / 'native-solver-review.json').read_text())
        assert report['passed'] is True and report['steps'] == 150 and report['timed_samples'] == 149
        samples = [float(row['time_function_seconds']) for row in report['timing_samples']]
        assert len(samples) == 149 and all(math.isfinite(x) and x > 0 for x in samples)
        runs[arm] = {'mean_seconds_step': statistics.mean(samples),
                     'median_seconds_step': statistics.median(samples),
                     'p95_seconds_step_linear': percentile(samples, 0.95),
                     'max_seconds_step': max(samples),
                     'max_time': int(report['timing_samples'][samples.index(max(samples))]['time']),
                     'samples': samples}
    blocks = []
    for pair, control, candidate in (('AB', 'A1', 'B1'), ('BA', 'A2', 'B2')):
        a, b = runs[control]['mean_seconds_step'], runs[candidate]['mean_seconds_step']
        blocks.append({'block_order': pair, 'identity_arm': control, 'candidate_arm': candidate,
                       'identity_minus_candidate_seconds_step': a - b,
                       'identity_minus_candidate_percent_of_identity': 100.0 * (a - b) / a})
    treatment = {}
    for label, arms in (('identity', ('A1', 'A2')), ('candidate', ('B1', 'B2'))):
        samples = runs[arms[0]]['samples'] + runs[arms[1]]['samples']
        treatment[label] = {'runs': list(arms), 'samples': len(samples),
                            'descriptive_pooled_mean_seconds_step': statistics.mean(samples),
                            'descriptive_pooled_median_seconds_step': statistics.median(samples),
                            'descriptive_pooled_p95_seconds_step_linear': percentile(samples, 0.95),
                            'descriptive_pooled_max_seconds_step': max(samples),
                            'sample_interpretation': 'Repeated time steps from two solver runs; not independent treatment replications.'}
    result = {'passed': True, 'arm_sequence': list(ARMS),
              'runs': {arm: {k: v for k, v in stats.items() if k != 'samples'}
                       for arm, stats in runs.items()},
              'paired_blocks': blocks, 'descriptive_treatment_summaries': treatment,
              'interpretation_limit': 'Two paired blocks on one allocation; no independent confidence interval or cross-allocation claim.'}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
