#!/usr/bin/env python3
"""Offline wave10 comparison. Never submits jobs or promotes a configuration."""
import argparse
import datetime
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('n54_review', ROOT / 'serving-tuning/review-n54.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
JOBS = {'23973': '23904', '23974': '23778', '23975': '23904'}
LONG = '23975'


def long_check(run):
    """A timeout/deferred check cannot become a pass from benchmark completion."""
    paths = {p.name: p for p in run.glob('long-context-check*') if p.is_file()}
    summary = paths.get('long-context-check.json')
    result = {'state': 'MISSING', 'accuracy_verified': False}
    if not paths:
        return result
    seal = core.read(run / 'artifact-manifest.json')
    sealed = {e['path']: e for e in seal['files']}
    for path in paths.values():
        key = str(path.relative_to(ROOT))
        core.require(key in sealed and core.sha(path) == sealed[key]['sha256']
                     and path.stat().st_size == sealed[key]['bytes'], 'long diagnostic unsealed')
    failed = 'long-context-check-failed.txt' in paths
    deferred = 'long-context-check-deferred.txt' in paths
    if not summary:
        return dict(result, state='FAILED' if failed else 'DEFERRED' if deferred else 'INCOMPLETE')
    data = core.read(summary)
    cases = data['cases']
    core.require(data['total'] == len(cases) == 12, 'long case count mismatch')
    core.require({c['name'] for c in cases} == {f'retrieval-{i}' for i in range(12)},
                 'long names mismatch')
    passed = errors = 0
    for c in cases:
        i = int(c['name'].split('-')[1])
        core.require(c['expected'] == str(73160429 + i * 137)
                     and isinstance(c['input_tokens'], int) and c['input_tokens'] > 0,
                     'long expected value/token count mismatch')
        core.require(isinstance(c['prompt'], str)
                     and f'archive_key_{i}' in c['prompt'], 'long prompt missing')
        error = 'error' in c
        errors += error
        if not error:
            text = c['response']['choices'][0]['message']['content']
            core.require(text == c['text'], 'long response/text mismatch')
            actual = text.strip(' \t\n\r\"\'`.') == c['expected']
        else:
            actual = False
        core.require(type(c['passed']) is bool and c['passed'] == actual,
                     'long answer/summary mismatch')
        passed += actual
    core.require(data['passed'] == passed and data['errors'] == errors, 'long totals mismatch')
    return dict(result, state='PASSED' if passed == 12 and errors == 0 and not failed and not deferred
                else 'FAILED', passed=passed, total=12, errors=errors,
                input_tokens=[c['input_tokens'] for c in cases],
                failed_cases=[c['name'] for c in cases if not c['passed']])


def matched(root, candidate, source):
    """Check exact replication against the approved source, including runtime."""
    job = candidate['job']
    run = root / 'runs' / job
    previous = root / 'runs' / source['job']
    core.require(candidate['normalized_protocol'] == source['normalized_protocol'], 'protocol drift')
    for name in candidate['payload_files']:
        if name in {'config.json', 'job.sbatch', 'long-context-check.py'}:
            continue
        a, b = run / 'submitted' / name, previous / 'submitted' / name
        if name == 'benchmark.sh' and job == LONG:
            suffix = '\n# Separate post-measurement diagnostic; not included in ranked AIPerf exports.\n'
            core.require(a.read_text().split(suffix)[0] == b.read_text(),
                         'long benchmark prefix drift')
        else:
            core.require(core.sha(a) == core.sha(b), 'execution payload drift: ' + name)
    deltas = {}
    for role, args in candidate['server_args'].items():
        before = source['server_args'][role]
        delta = {k: [before.get(k), args.get(k)] for k in args.keys() | before.keys()
                 if args.get(k) != before.get(k)}
        core.require(not set(delta) - {'random_seed'}, 'replication runtime drift: ' + role)
        deltas[role] = delta
    log = (run / 'decode-0.log').read_text()
    core.require(sorted({int(n) for n in re.findall(r'backend=mnnvl, rank=(\d+), world_size=8', log)})
                 == list(range(8)), 'missing MNNVL ranks')
    if source['job'] == '23904':
        core.require(sorted({int(n) for n in re.findall(
            r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3', log)})
                     == list(range(8)), 'missing FlashInfer decode ranks')
    return deltas


def aggregate(points, long_result):
    controls = [points[j]['metrics'] for j in ('23778', '23839', '23974')]
    combos = [points[j]['metrics'] for j in ('23904', '23973', '23975')]
    means = lambda rows: {k: sum(r[k] for r in rows) / len(rows)
                          for k in ('good_tokens_s', 'ttft_ms', 'itl_ms')}
    control_mean, combo_mean = means(controls), means(combos)
    full_sla = all(p['metrics']['sla_pass'] for p in points.values())
    gain = core.metric_delta(combo_mean, control_mean)
    # Report each observation; a positive pooled average alone does not reproduce gain.
    repeats_beat_fresh = all(points[j]['metrics']['good_tokens_s'] >
                             points['23974']['metrics']['good_tokens_s'] for j in ('23973', '23975'))
    reproduced = full_sla and gain['goodput_gain_percent'] > 0 and repeats_beat_fresh
    gate = reproduced and long_result['state'] == 'PASSED' and all(
        r['sla_fraction'] >= .95 and r['itl_ms'] <= 19.3 for r in combos)
    return {'control_mean': control_mean, 'combo_mean': combo_mean, 'vs_control_mean': gain,
            'fresh_control_vs_historical_mean': core.metric_delta(points['23974']['metrics'], means(controls[:2])),
            'each_combo_vs_each_control': {j: {b: core.metric_delta(points[j]['metrics'], points[b]['metrics'])
                for b in ('23778', '23839', '23974')} for j in ('23904', '23973', '23975')},
            'performance_gain_reproduced_descriptively': reproduced,
            'combo_n54_plan_gate_met': gate, 'submission_authorized': False,
            'caveat': 'Three observations per variant; no statistical significance claim. '
                      'Gate supports writing a bounded plan, never automatic submission. '
                      'Long retrieval is separate from performance and organiser accuracy.'}


def review(root):
    result = {'reviewed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'state': 'WAITING_FOR_SEALED_RESULTS', 'accuracy_verified': False,
              'scheduler_refreshed': False, 'jobs': {}, 'new_jobs_submitted': False}
    available = [j for j in JOBS if (root / 'runs' / j / 'artifact-manifest.json').exists()]
    for job in JOBS:
        result['jobs'][job] = {'state': 'NO_TERMINAL_SEAL'}
    if not available:
        return result
    points = {}
    reviewing = None
    try:
        for j in ('23778', '23839', '23904'):
            reviewing = j
            points[j] = core.point(root, j, 52)
        for j in available:
            reviewing = j
            result['jobs'][j] = {'state': 'REVIEWING_SEALED_EVIDENCE'}
            p = core.point(root, j, 52)
            delta = matched(root, p, points[JOBS[j]])
            points[j] = p
            result['jobs'][j] = {'state': 'MEASURED_SLA_PASS' if p['metrics']['sla_pass'] else 'MEASURED_SLA_FAIL',
                                 'point': p, 'runtime_vs_source': delta}
        if LONG in points:
            result['long_diagnostic'] = long_check(root / 'runs' / LONG)
        if len(available) == len(JOBS):
            result['comparison'] = aggregate(points, result['long_diagnostic'])
            result['state'] = 'COMPLETE_COMPARISON'
        else:
            result['state'] = 'PARTIAL_RESULTS'
    except (KeyError, ValueError, OSError, StopIteration, SyntaxError, TypeError) as exc:
        reason = f'{type(exc).__name__}: {exc}'
        if reviewing in result['jobs']:
            result['jobs'][reviewing] = {'state': 'INCOMPLETE_OR_INVALID_EVIDENCE', 'reason': reason}
        result.update(state='INCOMPLETE_OR_INVALID_EVIDENCE', evidence_job=reviewing, reason=reason)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    result = review(ROOT)
    with args.out.open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps({k: result[k] for k in ('state', 'accuracy_verified', 'new_jobs_submitted')}))
