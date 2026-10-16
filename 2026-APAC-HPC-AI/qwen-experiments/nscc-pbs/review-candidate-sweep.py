"""Compare sealed H100 candidate sweeps to220575; CPU only, no promotion."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('sweep', ROOT / 'review-load-sweep.py')
sweep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sweep)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def long_review(snapshot, job):
    run = snapshot / 'runs' / job
    seal = sweep.read(snapshot / 'evidence-sha256.json')
    names = ['long-context-check.json', 'long-context-check-failed.txt',
             'long-context-check-deferred.txt']
    present = [run / name for name in names if (run / name).exists()]
    if not present:
        return {'state': 'MISSING'}
    if any(seal.get(str(p.relative_to(snapshot))) != sha(p) for p in present):
        return {'state': 'UNSEALED'}
    result = run / names[0]
    if (run / names[1]).exists():
        return {'state': 'FAILED', 'result': sweep.read(result) if result.exists() else None}
    if (run / names[2]).exists():
        return {'state': 'INCONSISTENT' if result.exists() else 'DEFERRED'}
    data = sweep.read(result)
    cases = data.get('cases', [])
    passed = (data.get('total') == data.get('passed') == 12 and data.get('errors') == 0
              and len(cases) == 12 and len({c.get('name') for c in cases}) == 12
              and all(c.get('passed') is True and 'error' not in c for c in cases))
    return {'state': 'PASSED' if passed else 'FAILED',
            'passed': data.get('passed'), 'total': data.get('total'), 'errors': data.get('errors')}


def compare(candidate, baseline, smoke, pilot):
    reference = sweep.review(baseline, smoke)
    observed = sweep.review(candidate, smoke)
    if reference['job'] != '220575.pbs111':
        raise ValueError('Require the retained H100 sweep220575 as baseline')
    plan = sweep.read(ROOT / 'continuous-plan.json')
    matches = [p for group in ('pilots', 'startup_pilots') for p in plan[group] if p['id'] == pilot]
    if len(matches) != 1 or matches[0]['job_id'] != observed['job']:
        raise ValueError('Pilot/job differs from frozen plan; review replacements manually')
    frozen = matches[0]
    submitted = candidate / 'runs' / observed['job'] / 'submitted'
    seal = sweep.read(candidate / 'evidence-sha256.json')
    payload = {name: ((submitted / name).is_file()
                     and seal.get(str((submitted / name).relative_to(candidate))) == digest
                     and sha(submitted / name) == digest)
               for name, digest in frozen['payload_sha256'].items()}
    refs = {p['concurrency']: p for p in reference['points']}
    rows = []
    for point in observed['points']:
        control = refs.get(point['concurrency'])
        row = {'candidate': point, 'baseline': control, 'comparison': 'NO_MATCHED_BASELINE'}
        if control:
            numeric = (reference['seal_pass'] and observed['seal_pass'] and all(payload.values())
                       and all(p['protocol_pass'] and p['phase_complete'] for p in (point, control))
                       and all(isinstance(p[k], (int, float)) and math.isfinite(p[k])
                               for p in (point, control)
                               for k in ('good_output_tokens_s', 'ttft_avg_ms', 'itl_avg_ms')))
            row['comparison'] = 'DESCRIPTIVE_MATCHED_N' if numeric else 'INCOMPLETE_PROTOCOL'
            if numeric and control['good_output_tokens_s']:
                row.update(goodput_change_pct=100 * (point['good_output_tokens_s'] / control['good_output_tokens_s'] - 1),
                           ttft_change_ms=point['ttft_avg_ms'] - control['ttft_avg_ms'],
                           itl_change_ms=point['itl_avg_ms'] - control['itl_avg_ms'])
        rows.append(row)
    evidence_ok = all(r['seal_pass'] and r['snapshot_terminal'] and r['exit_status'] == 0
                      and r['short_nonregression_vs_h100_baseline'] for r in (reference, observed))
    return {'reviewed_utc': datetime.now(timezone.utc).isoformat(), 'pilot': pilot,
            'candidate_job': observed['job'], 'baseline_job': reference['job'],
            'candidate_review': observed, 'baseline_review': reference,
            'frozen_candidate_payload': payload, 'terminal_seal_short_payload_pass': evidence_ok and all(payload.values()),
            'matched_points': rows, 'long_diagnostic': long_review(candidate, observed['job']),
            'runtime_status': 'MANUAL_REVIEW_REQUIRED: inspect PBS output and resolved ServerArgs; payload hashes do not establish backend execution.',
            'accuracy_verified': False, 'promotion_authorized': False,
            'interpretation': 'Single candidate vs historical H100 control. Keep failed SLA points. No baseline beyond N36; no effect attribution, repeatability or statistical claim. Long checks are synthetic diagnostics only.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--baseline-smoke', type=Path, required=True)
    parser.add_argument('--pilot', choices=['h100-mnnvl-04', 'h100-flashinfer-05', 'h100-loader-prefetch-06'], required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.candidate, args.baseline, args.baseline_smoke, args.pilot)
    with args.out.open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps({k: result[k] for k in ['candidate_job', 'terminal_seal_short_payload_pass', 'long_diagnostic', 'promotion_authorized']}))


if __name__ == '__main__':
    main()
