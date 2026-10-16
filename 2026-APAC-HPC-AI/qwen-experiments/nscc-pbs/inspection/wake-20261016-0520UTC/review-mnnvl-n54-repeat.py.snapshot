#!/usr/bin/env python3
"""Review the one bounded MNNVL N54 repeat; read only, no submission or promotion."""
import argparse
import datetime
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('wave10', ROOT / 'serving-tuning-10/review-wave10.py')
wave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)
core = wave.core
NAME = 's10-mnnvl-repeat-n54'


def review():
    result = dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  state='WAITING_FOR_SEALED_RESULTS', accuracy_verified=False,
                  new_jobs_submitted=False, automatic_followup=False)
    entries = [e for e in core.read(ROOT / 'serving-tuning/registry.json')['entries']
               if e['id'] == NAME]
    if not entries:
        return dict(result, reason='Prepared pilot has no registered job yet.')
    try:
        core.require(len(entries) == 1 and entries[0]['planned_ns'] == [54], 'repeat plan mismatch')
        entry = entries[0]
        core.require(len(entry['attempts']) == 1, 'unexpected additional attempt; review manually')
        job = entry['attempts'][0]['job']
        result['job'] = job
        if not (ROOT / 'runs' / job / 'artifact-manifest.json').exists():
            return dict(result, reason='No terminal artifact seal; queue is not a measurement.')
        candidate = core.point(ROOT, job, 54)
        original = core.point(ROOT, '23924', 54)
        # Config, protocol, twelve execution files and resolved runtime must match.
        same_load = core.compare_points(ROOT, candidate, [original])
        wave.matched(ROOT, candidate, original)  # Explicitly require eight MNNVL ranks.
        controls = [core.point(ROOT, j, 52) for j in ('23778', '23839')]
        historical = core.compare_points(ROOT, candidate, controls)
        fresh = None
        if (ROOT / 'runs/23974/artifact-manifest.json').exists():
            fresh = core.point(ROOT, '23974', 52)
            # Fresh control has different provenance metadata; compare actual execution/runtime.
            wave.matched(ROOT, candidate, fresh)
        mean = lambda points: {k: sum(p['metrics'][k] for p in points) / len(points)
                               for k in ('good_tokens_s', 'ttft_ms', 'itl_ms')}
        n54_mean = mean([original, candidate])
        all_controls = controls + ([fresh] if fresh else [])
        control_mean = mean(all_controls)
        result.update(state='MEASURED_SLA_PASS' if candidate['metrics']['sla_pass'] else 'MEASURED_SLA_FAIL',
                      candidate=candidate, same_load_vs_23924=same_load,
                      candidate_vs_historical_n52=historical,
                      n54_mean=n54_mean, n52_control_jobs=[p['job'] for p in all_controls],
                      n52_mean=control_mean, n54_mean_vs_n52_mean=core.metric_delta(n54_mean, control_mean),
                      fresh_control_state='SEALED_REVIEWED' if fresh else 'WAITING_FOR_SEALED_RESULTS',
                      caveat='Two N54 measurements remain descriptive; engine seed is unpinned. '
                             'Do not infer backend effect from cross-load combo comparison. '
                             'Short checks do not establish BTC accuracy; no N56 or third repeat.')
        if fresh:
            result['fresh_control_metrics'] = fresh['metrics']
            result['each_n54_vs_fresh_control'] = {
                p['job']: core.metric_delta(p['metrics'], fresh['metrics']) for p in [original, candidate]}
            result['fresh_control_drift'] = core.metric_delta(fresh['metrics'], mean(controls))
    except (KeyError, ValueError, OSError, StopIteration, SyntaxError, TypeError) as exc:
        return dict(result, state='INCOMPLETE_OR_INVALID_EVIDENCE', reason=f'{type(exc).__name__}: {exc}')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = review()
    with args.out.open('x') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    print(json.dumps({k: report[k] for k in ('state', 'accuracy_verified', 'new_jobs_submitted')}))
