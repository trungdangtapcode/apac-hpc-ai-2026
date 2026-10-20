"""Inspect sealed job-local samples against the client's epoch-nanosecond phases."""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import statistics


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def distribution(values):
    values = sorted(values)
    if not values:
        return dict(count=0)
    def percentile(p):
        at = (len(values) - 1) * p
        lo = math.floor(at)
        hi = math.ceil(at)
        return values[lo] + (values[hi] - values[lo]) * (at - lo)
    return dict(count=len(values), mean=statistics.mean(values), minimum=values[0],
                p50=percentile(.5), p95=percentile(.95), maximum=values[-1])


def inspect(run, concurrency):
    root = run.parent.parent
    seal = json.loads((run / 'artifact-manifest.json').read_text())
    sealed = {row['path']: row['sha256'] for row in seal['files']}
    checked = {}
    def read(path):
        digest = sha(path)
        assert digest == sealed[str(path.relative_to(root))], path
        checked[str(path)] = digest
        return path.read_text()
    manifest = json.loads(read(run / f'confirm/n{concurrency}/artifacts/phase_manifest.json'))
    phases = [p for p in manifest['phases'] if p['phase_kind'] == 'profiling']
    assert len(phases) == 1
    phase = phases[0]
    start, end = phase['start_ns'], phase['end_ns']
    assert end > start and (end - start) / 1e9 >= 120
    markers = [json.loads(x) for x in read(run / 'phase-markers.jsonl').splitlines()]
    begin = next(m for m in markers if m['event'] == 'benchmark_start' and m['detail'] == ['confirm', str(concurrency)])
    finish = next(m for m in markers if m['event'] == 'benchmark_end' and m['detail'] == ['confirm', str(concurrency)])
    assert begin['utc_ns'] < start < end < finish['utc_ns']
    result = dict(job=run.name, phase=phase, orchestration_host=begin['host'],
                  source_hashes=checked, roles={}, nodes={}, accuracy_verified=False,
                  alignment='Epoch nanoseconds from the explicit AIPerf phase manifest; no naive local-time conversion.',
                  limitations=[
                      'Five-second samples cannot reveal short stalls or exact peaks; statistics are sample-weighted.',
                      'GPU activity and memory activity are sampled active-time percentages, not FLOPS or bandwidth efficiency.',
                      'Node counters are shared by co-located roles and are reported once per hostname.',
                      'Cross-node clock skew is not independently calibrated; remote-role phase alignment assumes the host clocks agree.',
                      'Server metric series retain their labels; no summation across overlapping series is inferred.',
                      'Node interface byte counters do not establish RDMA or NVLink link utilization.',
                  ])
    all_uuids = set()
    host_sources = {}
    for path in sorted((run / 'resource-telemetry').glob('*.jsonl')):
        rows = [json.loads(x) for x in read(path).splitlines()]
        meta = rows[0]
        assert meta['kind'] == 'metadata'
        role, host = meta['role'], meta['host']
        expected = 8 if role == 'decode-0' else 4
        samples = [row for row in rows if row['kind'] == 'sample']
        ranked = [row for row in samples if start <= row['utc_ns'] <= end]
        assert len(ranked) >= 20, (role, len(ranked))
        assert [s['utc_ns'] for s in samples] == sorted(s['utc_ns'] for s in samples)
        ids = [{gpu['uuid'] for gpu in row.get('gpus', [])} for row in ranked]
        assert all(len(x) == expected for x in ids) and all(x == ids[0] for x in ids)
        assert not (all_uuids & ids[0]), 'Role GPU UUID overlap'
        all_uuids |= ids[0]
        status = collections.Counter(row['gpu_status'] for row in ranked)
        assert set(status) == {'ok'}
        metrics, unsupported = {}, collections.Counter()
        for field in ['utilization.gpu', 'utilization.memory', 'memory.used', 'power.draw',
                      'temperature.gpu', 'clocks.sm', 'clocks.mem']:
            values = []
            for row in ranked:
                for gpu in row['gpus']:
                    try:
                        value = float(gpu[field])
                        if not math.isfinite(value):
                            raise ValueError('Nonfinite sample')
                        values.append(value)
                    except (ValueError, TypeError, KeyError):
                        unsupported[field] += 1
            metrics[field] = distribution(values)
        series = collections.Counter()
        for row in ranked:
            for line in row.get('server_metrics', []):
                series[line.rsplit(' ', 1)[0]] += 1
        first, last = ranked[0]['utc_ns'], ranked[-1]['utc_ns']
        gaps = [(b['utc_ns'] - a['utc_ns']) / 1e9 for a, b in zip(ranked, ranked[1:])]
        result['roles'][role] = dict(host=host, requested_visible_ids=meta['gpu_ids_requested'],
            gpu_uuids=sorted(ids[0]), all_samples=len(samples), scored_samples=len(ranked),
            first_sample_after_phase_start_s=(first - start) / 1e9,
            phase_end_after_last_sample_s=(end - last) / 1e9,
            sampling_gaps_s=distribution(gaps), gpu_query_status=dict(status),
            gpu_metrics=metrics, unsupported_field_observations=dict(unsupported),
            server_http_status=dict(collections.Counter(str(x.get('server_http_status', x.get('server_metrics_status', 'missing'))) for x in ranked)),
            server_metric_series_sample_counts=dict(series),
            sampler_elapsed_s=distribution([x['sampler_elapsed_s'] for x in ranked]),
            sampler_stop_recorded=any(x['kind'] == 'sampler_stop' for x in rows),
            clock_alignment='Same host as orchestration' if host == begin['host'] else 'Remote host; independent skew measurement unavailable')
        # The first stable role series per hostname is used; no role-level double counting.
        if host not in host_sources:
            host_sources[host] = (role, ranked)
    assert len(all_uuids) == 16 and set(result['roles']) == {'prefill-0', 'prefill-1', 'decode-0'}
    for host, (role, rows) in host_sources.items():
        busy, rates = [], collections.defaultdict(list)
        for a, b in zip(rows, rows[1:]):
            seconds = (b['utc_ns'] - a['utc_ns']) / 1e9
            acpu, bcpu = a['node_cpu_jiffies'][:8], b['node_cpu_jiffies'][:8]
            delta = [y - x for x, y in zip(acpu, bcpu)]
            total = sum(delta)
            if seconds <= 0 or total <= 0 or min(delta) < 0:
                continue
            busy.append(100 * (total - delta[3] - delta[4]) / total)
            for iface in a.get('node_network_counters', {}).keys() & b.get('node_network_counters', {}).keys():
                if iface == 'lo':
                    continue
                for direction in ['rx_bytes', 'tx_bytes']:
                    change = b['node_network_counters'][iface][direction] - a['node_network_counters'][iface][direction]
                    if change >= 0:
                        rates[iface + ':' + direction + '_per_s'].append(change / seconds)
        result['nodes'][host] = dict(source_role=role, cpu_busy_percent=distribution(busy),
            memory_available_KiB=distribution([x['node_memory']['MemAvailable_KiB'] for x in rows]),
            network_bytes_per_second={k: distribution(v) for k, v in rates.items()})
    result['unique_gpus'] = len(all_uuids)
    result['phase_marker_order_passed'] = True
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--concurrency', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    data = inspect(args.run, args.concurrency)
    args.out.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(dict(job=data['job'], unique_gpus=data['unique_gpus'],
                         scored_samples={k: v['scored_samples'] for k, v in data['roles'].items()})))
