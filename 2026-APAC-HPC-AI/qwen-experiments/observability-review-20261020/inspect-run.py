"""Inspect existing sealed run artifacts without launching model traffic or GPU work."""
import argparse
import collections
import hashlib
import json
import math
import re
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def distribution(values):
    if not values:
        return {'samples': 0, 'p50': None, 'p95': None, 'max': None}
    values = sorted(values)
    return {'samples': len(values), 'p50': values[math.ceil(.5 * len(values)) - 1],
            'p95': values[math.ceil(.95 * len(values)) - 1], 'max': values[-1]}


def inspect(root, job, review):
    run = root / 'runs' / job
    accepted = json.loads(review.read_text())
    assert accepted['job'] == job and accepted['state'] == 'LOCAL_PROTOCOL_SLA_OUTPUT_PASS'
    seal_path = run / 'artifact-manifest.json'
    assert sha(seal_path) == accepted['point']['seal_sha256']
    seal = {row['path']: row['sha256'] for row in json.loads(seal_path.read_text())['files']}
    evidence = []

    def sealed(path):
        digest = sha(path)
        assert seal[str(path.relative_to(root))] == digest, path
        evidence.append({'path': str(path), 'sha256': digest})
        return path.read_text(errors='replace')

    n = accepted['point']['concurrency']
    export_path = run / 'confirm' / ('n' + str(n)) / 'artifacts/profile_export_aiperf.json'
    exported = json.loads(sealed(export_path))
    fields = ['time_to_first_token', 'inter_token_latency', 'request_latency',
              'effective_concurrency', 'request_count', 'error_summary']
    telemetry = exported.get('telemetry_data') or {}
    result = {'job': job, 'source_review': str(review), 'source_review_sha256': sha(review),
              'accepted_review_state': accepted['state'], 'score': accepted['point']['metrics'],
              'client': {key: exported.get(key) for key in fields},
              'telemetry_endpoints_configured': telemetry.get('summary', {}).get('endpoints_configured', []),
              'telemetry_endpoints_successful': telemetry.get('summary', {}).get('endpoints_successful', []),
              'roles': {}, 'evidence': evidence, 'accuracy_verified': False,
              'limits': ['Role log statistics cover the entire deployment, including warmup, output checks and any separate profile.',
                         'Batch log samples are sparse and event-weighted, not uniform time samples or proven scored-phase statistics.',
                         'Token usage is logged KV token occupancy, not GPU utilization, allocated VRAM or HBM bandwidth.',
                         'KV allocation sizes are reported by the server; they are not sampled total or peak VRAM.',
                         'No timestamp conversion or cross-rank alignment is assumed for the naive client/server wall clocks.',
                         'Warning/error matches require triage and are not counts of failed scored requests.',
                         'Uncollected GPU/CPU/network telemetry cannot be reconstructed from goodput or kernel duration sums.']}
    for role in ['prefill-0', 'prefill-1', 'decode-0', 'router']:
        path = run / (role + '.log')
        text = sealed(path)
        lines = [line for line in text.splitlines() if 'server_args=' not in line]
        batches = [line for line in lines if 'Prefill batch,' in line or 'Decode batch,' in line]
        metrics = {}
        for name in ['#running-req', '#queue-req', '#new-seq', '#new-token', '#cached-token',
                     '#inflight-req', '#retracted-req', '#transfer-req', 'token usage']:
            pattern = r'(?:^|, )' + re.escape(name) + r': ([0-9.]+)'
            metrics[name] = distribution([float(m.group(1)) for line in batches
                                           if (m := re.search(pattern, line))])
        alloc = collections.Counter()
        for line in lines:
            m = re.search(r'KV Cache is allocated\. dtype: ([^,]+), #tokens: (\d+), K size: ([\d.]+) GB, V size: ([\d.]+) GB', line)
            if m:
                alloc[m.groups()] += 1
        issue_patterns = {'out_of_memory_mentions': r'out of memory|OutOfMemoryError',
                          'traceback_mentions': r'Traceback \(most recent call last\)',
                          'cuda_error_mentions': r'CUDA error:',
                          'warning_lines': r'\bWARNING\b|\bWARN\b',
                          'error_lines': r'\bERROR\b|\bFATAL\b'}
        result['roles'][role] = {'log_lines': len(lines), 'batch_samples': len(batches),
            'log_distributions': metrics,
            'kv_allocation_records': [{'dtype': x[0], 'token_capacity': int(x[1]),
                                      'K_reported_GB': float(x[2]), 'V_reported_GB': float(x[3]),
                                      'rank_records': count} for x, count in alloc.items()],
            'issue_mentions': {key: sum(bool(re.search(pattern, line, re.I)) for line in lines)
                               for key, pattern in issue_patterns.items()}}
    # These fields are deliberately null when no corresponding measurements were retained.
    result['hardware_time_series'] = {key: None for key in
        ['gpu_utilization_pct', 'memory_activity_pct', 'vram_used_MiB', 'power_W',
         'temperature_C', 'sm_clock_MHz', 'cpu_usage_pct', 'host_memory_MiB',
         'network_bytes_per_second', 'nvlink_bytes_per_second']}
    return result


def markdown(data):
    lines = ['# Extended artifact inspection: H200 job ' + data['job'], '',
             'Generated offline from sealed raw artifacts. This supplements the accepted protocol/output review; it does not replace it or rerun the benchmark.', '',
             '## Client distribution', '',
             '| Metric | Unit | Mean | p50 | p95 | p99 | Maximum |', '|---|---|---:|---:|---:|---:|---:|']
    for key in ['time_to_first_token', 'inter_token_latency', 'request_latency', 'effective_concurrency']:
        d = data['client'][key]
        values = [str(round(d[x], 4)) if d.get(x) is not None else 'N/A' for x in ['avg','p50','p95','p99','max']]
        lines.append('| ' + ' | '.join([key, d['unit']] + values) + ' |')
    lines += ['', '## Full-deployment server log samples', '',
              'These include warmup, scored traffic, output checks and any separate diagnostic. They are event samples, not time-weighted scored-phase means.', '',
              '| Role | Batch lines | Running requests p50 / p95 / max | Queue p50 / p95 / max | Logged KV token usage p50 / p95 / max |',
              '|---|---:|---|---|---|']
    for role, d in data['roles'].items():
        def cell(key):
            a = d['log_distributions'][key]
            return ' / '.join(str(a[k]) if a[k] is not None else 'N/A' for k in ['p50','p95','max'])
        lines.append('| ' + ' | '.join([role, str(d['batch_samples']), cell('#running-req'), cell('#queue-req'), cell('token usage')]) + ' |')
    lines += ['', '## Collection gaps and interpretation', '',
              'AIPerf telemetry endpoints configured: `' + str(data['telemetry_endpoints_configured']) + '`; successful: `' + str(data['telemetry_endpoints_successful']) + '`.', '',
              'GPU utilization, HBM activity, sampled VRAM, power, clocks, temperature, CPU/RAM and link throughput are **not available as dedicated continuous hardware measurements in this inspection**. Missing is not zero. A separate profile can still describe recorded kernel execution; it does not reconstruct missing hardware samples.', '',
              'KV allocation records and warning/error mention counts are in the adjacent JSON. A nonzero queue or token-usage peak somewhere in the whole deployment is not proof of the scored benchmark bottleneck.']
    # Keep the renderer explicit; no raw model text or whole server_args is copied.
    lines += ['', '## Limits', ''] + ['- ' + x for x in data['limits']]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--job', required=True)
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    result = inspect(args.root, args.job, args.review)
    args.out.mkdir(exist_ok=True, parents=True)
    (args.out / (args.job + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    (args.out / (args.job + '.md')).write_text(markdown(result))
    print(args.job, 'sealed files inspected:', len(result['evidence']))
