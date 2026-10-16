#!/usr/bin/env python3
"""Offline evidence review for the two existing N54 jobs; never submits work."""
import argparse
import ast
import copy
import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BRANCHES = {'23924': ('23778', '23839'), '23934': ('23780', '23859')}


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def normalized(config):
    result = copy.deepcopy(config)
    result['endpoint'].pop('urls')
    result['artifacts'].pop('dir')
    for phase in result['phases']:
        phase['concurrency'] = '<matched-load>'
    result['runtime']['workers'] = '<matched-load>'
    return result


def validate_metrics(data, manifest, n):
    """Reject incomplete/incorrect protocol independently of the SLA verdict."""
    cfg = data['input_config']
    phases = cfg['phases']
    require([(p['kind'], p['duration'], p['concurrency']) for p in phases]
            == [('warmup', 60, n), ('profiling', 120, n)], 'protocol/load mismatch')
    require(phases[0]['exclude_from_results'] is True
            and phases[1]['grace_period'] == 30, 'warmup/grace mismatch')
    require(cfg['runtime']['workers'] == n, 'worker count mismatch')
    require(cfg['slos'] == {'time_to_first_token': 3000.0, 'inter_token_latency': 20.0},
            'SLO mismatch')
    require(cfg['endpoint']['streaming'] is True and cfg['endpoint']['extra'] == {
        'min_tokens': 200, 'max_tokens': 200, 'ignore_eos': True,
        'temperature': 0.0, 'repetition_penalty': 1.0}, 'request settings mismatch')
    require(cfg['datasets'] == [{
        'name': 'main', 'type': 'synthetic', 'entries': 12800, 'random_seed': 2026,
        'prompts': {'isl': {'mean': 4000.0, 'stddev': 0.0},
                    'osl': {'mean': 200.0, 'stddev': 0.0},
                    'cache_bust': {'target': 'first_turn_prefix'}}}], 'dataset mismatch')
    require(data['was_cancelled'] is False and data['error_summary'] == [],
            'cancelled/error export')
    require('error_request_count' not in data or data['error_request_count']['avg'] == 0,
            'error metric nonzero')
    rows = manifest['phases']
    require([p['phase_kind'] for p in rows] == ['warmup', 'profiling'], 'phase manifest mismatch')
    timings = []
    for p, duration in zip(rows, (60, 120)):
        require(p['was_cancelled'] is False and p['error_request_count'] == 0
                and p['error_summary'] == [], 'phase cancelled/error')
        require(p['total_request_count'] == p['successful_request_count'] > 0,
                'incomplete request counts')
        elapsed = (p['end_ns'] - p['start_ns']) / 1e9
        require(duration <= elapsed <= duration + 30, 'phase duration outside protocol')
        timings.append({'kind': p['phase_kind'], 'elapsed_s': elapsed,
                        'requests': p['total_request_count']})
    metric = lambda k: data[k]['avg']
    require(metric('request_count') == rows[1]['total_request_count'], 'profiling count mismatch')
    values = {k: metric(k) for k in ('goodput', 'good_request_fraction',
                                   'time_to_first_token', 'inter_token_latency')}
    require(all(math.isfinite(v) and v >= 0 for v in values.values()), 'invalid metric')
    require(0 <= metric('good_request_count') <= metric('request_count')
            and 0 <= values['good_request_fraction'] <= 1, 'invalid good request counts')
    require(math.isclose(metric('good_request_count') / metric('request_count'),
                         values['good_request_fraction']), 'SLA fraction mismatch')
    return {'good_tokens_s': values['goodput'] * 200,
            'sla_fraction': values['good_request_fraction'],
            'sla_pass': values['good_request_fraction'] >= .90,
            'ttft_ms': values['time_to_first_token'],
            'itl_ms': values['inter_token_latency'], 'phases': timings}


def server_args(path):
    line = next(l.split('server_args=', 1)[1] for l in path.read_text().splitlines()
                if 'server_args=ServerArgs(' in l)
    return {k.arg: ast.unparse(k.value) for k in ast.parse(line, mode='eval').body.keywords}


def point(root, job, n):
    run = root / 'runs' / job
    seal_path = run / 'artifact-manifest.json'
    seal = read(seal_path)
    require(seal['job'] == job, 'seal job mismatch')
    require(seal['status_at_seal']['state'] == 'COMPLETED'
            and seal['status_at_seal']['exit'] == '0:0', 'no successful terminal seal')
    sealed = {}
    for entry in seal['files']:
        path = (root / entry['path']).resolve()
        require(path.is_relative_to(run.resolve()), 'seal path outside own run')
        require(entry['path'] not in sealed, 'duplicate seal path')
        require(path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'],
                'seal mismatch: ' + entry['path'])
        sealed[entry['path']] = entry
    artifacts = run / f'confirm/n{n}/artifacts'
    required = [artifacts / f for f in ('profile_export_aiperf.json', 'profile_export.jsonl',
                                       'phase_manifest.json')]
    required += [run / f for f in ('output-smoke.json', 'decode-0.log', 'prefill-0.log',
                                  'prefill-1.log', 'pair-warmup.log', 'connection-warmup.log')]
    registry = read(root / 'serving-tuning/registry.json')
    entry = next(e for e in registry['entries'] if any(a['job'] == job for a in e['attempts']))
    for f, expected in entry['payload_sha256'].items():
        submitted = run / 'submitted' / f
        require(sha(submitted) == expected, 'submitted payload mismatch: ' + f)
        required.append(submitted)
    require(all(str(p.relative_to(root)) in sealed for p in required), 'required evidence unsealed')
    data = read(required[0])
    metrics = validate_metrics(data, read(artifacts / 'phase_manifest.json'), n)
    lengths = []
    raw_counts = {'warmup': 0, 'profiling': 0}
    with (artifacts / 'profile_export.jsonl').open() as raw:
        for line in raw:
            row = json.loads(line)
            require(not row['metadata']['was_cancelled'] and not row.get('error')
                    and not row.get('errors'), 'raw cancelled/error request')
            kind = row['metadata']['phase_kind']
            require(kind in raw_counts, 'unexpected raw phase')
            raw_counts[kind] += 1
            if kind == 'profiling':
                lengths.append(row['metrics']['output_sequence_length']['value'])
    require(raw_counts == {p['kind']: p['requests'] for p in metrics['phases']},
            'raw phase request counts mismatch')
    output = data['output_sequence_length']
    require(sum(lengths) == output['sum'] and min(lengths) == output['min']
            and max(lengths) == output['max'], 'raw output lengths mismatch')
    compare = runpy.run_path(str(root / 'watch-serving-tuning.py'))['compare_output_baseline']
    smoke = read(run / 'output-smoke.json')
    smoke_comparison = compare(smoke, root / 'runs/23146/output-diagnostic.jsonl')
    require(smoke_comparison['research_eligible'] and not smoke_comparison['new_failed_cases'],
            'short output regression')
    log = (run / 'decode-0.log').read_text()
    ranks = sorted({int(x) for x in re.findall(
        r'TP(\d+) EP\d+\] NIXL KVManager initialized with backend: UCX', log)})
    require(ranks == list(range(8)), 'missing NIXL decode ranks')
    if job in ('23778', '23839', '23924'):
        require(sorted({int(x) for x in re.findall(r'backend=mnnvl, rank=(\d+), world_size=8', log)})
                == list(range(8)), 'missing MNNVL decode ranks')
    require('ALL 2 P/D paths initialized' in (run / 'pair-warmup.log').read_text(),
            'pair warmup incomplete')
    require(sum(' 200 ' in l for l in (run / 'connection-warmup.log').read_text().splitlines()) == 8,
            'connection warmup incomplete')
    return dict(job=job, concurrency=n, metrics=metrics, sealed_files=len(sealed),
                seal_sha256=sha(seal_path), output_lengths=output,
                short_output_comparison=smoke_comparison,
                normalized_protocol=normalized(data['input_config']),
                server_args={role: server_args(run / (role + '.log'))
                             for role in ('prefill-0', 'prefill-1', 'decode-0')},
                payload_files=list(entry['payload_sha256']), status_at_seal=seal['status_at_seal'])


def compare_points(root, candidate, baselines):
    job = candidate['job']
    result = {}
    for base in baselines:
        require(candidate['normalized_protocol'] == base['normalized_protocol'], 'client protocol drift')
        operational = [f for f in candidate['payload_files'] if f not in ('config.json', 'job.sbatch')]
        require(len(operational) == 12, 'unexpected operational payload')
        for f in operational:
            require(sha(root / 'runs' / job / 'submitted' / f)
                    == sha(root / 'runs' / base['job'] / 'submitted' / f), 'operational payload drift: ' + f)
        ca = read(root / 'runs' / job / 'submitted/config.json')
        cb = read(root / 'runs' / base['job'] / 'submitted/config.json')
        require(not {k for k in ca.keys() | cb.keys() if ca.get(k) != cb.get(k)}
                - {'experiment', 'purpose', 'concurrency'}, 'run config drift')
        differences = {}
        for role, args in candidate['server_args'].items():
            other = base['server_args'][role]
            delta = {k: [other.get(k), args.get(k)] for k in args.keys() | other.keys()
                     if args.get(k) != other.get(k)}
            require(not set(delta) - {'random_seed'}, 'unexpected resolved ServerArgs: ' + role)
            differences[role] = delta
        result[base['job']] = dict(runtime_differences=differences,
            **metric_delta(candidate['metrics'], base['metrics']))
    means = {k: sum(b['metrics'][k] for b in baselines) / len(baselines)
             for k in ('good_tokens_s', 'ttft_ms', 'itl_ms')}
    return {'each_baseline': result, 'baseline_mean': means,
            'vs_mean': metric_delta(candidate['metrics'], means)}


def metric_delta(candidate, baseline):
    require(baseline['good_tokens_s'] > 0, 'zero baseline goodput')
    return {'goodput_gain_percent': 100 * (candidate['good_tokens_s'] / baseline['good_tokens_s'] - 1),
            'ttft_delta_ms': candidate['ttft_ms'] - baseline['ttft_ms'],
            'itl_delta_ms': candidate['itl_ms'] - baseline['itl_ms']}


def review(root, job):
    require(job in BRANCHES, 'only existing authorized N54 jobs are supported')
    result = dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), job=job,
                  state='INCOMPLETE_OR_INVALID_EVIDENCE', accuracy_verified=False,
                  submission_authorized=False, scheduler_refreshed=False,
                  scope='Offline sealed evidence only; no GPU, scheduler mutation or promotion.')
    if not (root / 'runs' / job / 'artifact-manifest.json').exists():
        return dict(result, reason='No terminal artifact seal; pending/running is not a result.')
    try:
        candidate = point(root, job, 54)
        baselines = [point(root, b, 52) for b in BRANCHES[job]]
        comparison = compare_points(root, candidate, baselines)
    except (KeyError, ValueError, OSError, StopIteration, SyntaxError, TypeError) as exc:
        return dict(result, reason=f'{type(exc).__name__}: {exc}')
    # SLA failure with complete evidence remains a valid measured frontier point.
    result.update(state='MEASURED_SLA_PASS' if candidate['metrics']['sla_pass'] else 'MEASURED_SLA_FAIL',
                  candidate=candidate, comparison=comparison,
                  caveat='One N54 run is provisional. Engine seed is unpinned. Short smoke is not BTC accuracy. '
                         'Fresh scheduler and stored launcher review remain separate; no repeat or N56 authorization.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', choices=BRANCHES)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = review(ROOT, args.job)
    with args.out.open('x') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
    print(json.dumps({k: result[k] for k in ('job', 'state', 'accuracy_verified')}))


if __name__ == '__main__':
    main()
