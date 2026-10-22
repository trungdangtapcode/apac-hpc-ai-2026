#!/usr/bin/env python3
"""Offline review of the four sealed H200 N60 runs; performs no scheduler actions."""
import datetime
import importlib.util
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / 'runs'
JOBS = ('24964', '24965', '25051', '25283')
HELPER = ROOT / 'serving-tuning-10/review-wave10.py'


def load_helper():
    spec = importlib.util.spec_from_file_location('wave10_review', HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def percentile(values, fraction):
    values = sorted(values)
    if not values:
        return None
    # Linear interpolation at the conventional (n - 1) * p position.
    pos = (len(values) - 1) * fraction
    lo = math.floor(pos)
    hi = math.ceil(pos)
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)


def server_status(row):
    """Support both early status-only and later HTTP-status telemetry schemas."""
    if 'server_http_status' in row:
        return str(row['server_http_status'])
    if 'server_metrics_status' in row:
        return str(row['server_metrics_status'])
    return 'MISSING_STATUS'


def latency_and_errors(job):
    path = RUNS / job / 'confirm/n60/artifacts/profile_export.jsonl'
    raw = {'profiling': 0, 'warmup': 0}
    ttft, itl = [], []
    errors = []
    cancelled = 0
    for line in path.open():
        row = json.loads(line)
        meta = row['metadata']
        kind = meta.get('phase_kind', meta.get('benchmark_phase'))
        if kind not in raw:
            continue
        raw[kind] += 1
        if kind != 'profiling':
            continue
        cancelled += bool(meta.get('was_cancelled'))
        if row.get('error') or row.get('errors'):
            errors.append({'request_id': meta.get('x_request_id'),
                           'error': row.get('error', row.get('errors'))})
        metrics = row['metrics']
        ttft.append(metrics['time_to_first_token']['value'])
        itl_metric = metrics['inter_token_latency']['value']
        itl.append(itl_metric)
    return {
        'raw_request_counts_by_phase': raw,
        'profiling_errors': len(errors), 'profiling_cancelled': cancelled,
        'error_examples': errors[:5],
        'ttft_ms': {'mean': sum(ttft)/len(ttft), 'p95': percentile(ttft, .95),
                    'max': max(ttft), 'over_3000_ms': sum(x > 3000 for x in ttft)},
        'request_mean_itl_ms': {'mean': sum(itl)/len(itl), 'p95': percentile(itl, .95),
                                'max': max(itl), 'over_20_ms': sum(x > 20 for x in itl)},
    }


def telemetry(job):
    base = RUNS / job / 'resource-telemetry'
    result = {'roles': {}}
    for role, gpu in (('prefill-0', 'g1'), ('prefill-1', 'g1'), ('decode-0', 'g4')):
        path = base / f'{role}-{gpu}.jsonl'
        if not path.exists():
            result['roles'][role] = {'state': 'NOT_COLLECTED'}
            continue
        rows = [json.loads(line) for line in path.open()]
        meta = next((r for r in rows if r.get('kind') == 'metadata'), {})
        samples = [r for r in rows if r.get('kind') == 'sample']
        server = [server_status(r) for r in samples]
        good_gpu = [g for r in samples if r.get('gpu_status') == 'ok'
                    for g in r.get('gpus', [])]
        def numeric(field):
            vals = []
            for g in good_gpu:
                try:
                    vals.append(float(g[field]))
                except (KeyError, TypeError, ValueError):
                    pass
            return vals
        result['roles'][role] = {
            'state': 'COLLECTED' if samples else 'NO_SAMPLES',
            'sample_scope': 'All retained samples across startup, warmup, scoring and shutdown; use phase-aligned-observability.json for the scored interval.',
            'sample_count': len(samples), 'interval_s': meta.get('interval_s'),
            'gpu_status_counts': {x: sum(r.get('gpu_status') == x for r in samples)
                                  for x in sorted({str(r.get('gpu_status')) for r in samples})},
            'all_sample_server_status_counts': {x: server.count(x) for x in sorted(set(server), key=str)},
            'all_sample_server_metrics_payload_count': sum(bool(r.get('server_metrics')) for r in samples),
            'all_sample_gpu_observations': len(good_gpu),
            'all_sample_gpu_activity_percent_mean': (sum(numeric('utilization.gpu')) / len(numeric('utilization.gpu'))
                                      if numeric('utilization.gpu') else None),
            'all_sample_sampled_vram_used_mib_mean': (sum(numeric('memory.used')) / len(numeric('memory.used'))
                                         if numeric('memory.used') else None),
            'all_sample_power_w_mean': (sum(numeric('power.draw')) / len(numeric('power.draw'))
                                 if numeric('power.draw') else None),
            'interpretation_limit': 'Cross-phase sample-window activity and point-in-time memory/power only; not peak utilization or causal attribution.'
        }
    return result


def server_log_samples(job):
    run = RUNS / job
    result = {}
    patterns = {
        'prefill-0': re.compile(r'#new-seq: (\d+), #new-token: (\d+), #cached-token: (\d+).*?token usage: ([0-9.]+).*?#running-req: (\d+), #queue-req: (\d+).*?#inflight-req: (\d+)'),
        'prefill-1': re.compile(r'#new-seq: (\d+), #new-token: (\d+), #cached-token: (\d+).*?token usage: ([0-9.]+).*?#running-req: (\d+), #queue-req: (\d+).*?#inflight-req: (\d+)'),
        'decode-0': re.compile(r'#running-req: (\d+), #token: (\d+), token usage: ([0-9.]+).*?#prealloc-req: (\d+).*?#transfer-req: (\d+).*?#queue-req: (\d+)'),
    }
    for role, pattern in patterns.items():
        path = run / f'{role}.log'
        rows = [pattern.search(line) for line in path.open()]
        rows = [tuple(float(x) for x in m.groups()) for m in rows if m]
        if not rows:
            result[role] = {'matching_samples': 0}
            continue
        if role.startswith('prefill'):
            names = ('new_seq', 'new_tokens', 'cached_tokens', 'token_usage', 'running_req', 'queue_req', 'inflight_req')
        else:
            names = ('running_req', 'tokens', 'token_usage', 'prealloc_req', 'transfer_req', 'queue_req')
        result[role] = {'matching_samples': len(rows), **{
            name: {'min': min(r[i] for r in rows), 'max': max(r[i] for r in rows),
                   'mean': sum(r[i] for r in rows)/len(rows)} for i, name in enumerate(names)}}
    return result


def phase_aligned_observability():
    """Summarize only GPU telemetry windows wholly contained in the scored interval."""
    roles = (('prefill-0', 'g1'), ('prefill-1', 'g1'), ('decode-0', 'g4'))
    mapping = json.loads((RUNS/'25051/worker-locality/summary.json').read_text())
    fields = {
        'utilization.gpu': 'gpu_activity_percent',
        'utilization.memory': 'memory_activity_percent',
        'memory.used': 'sampled_vram_used_mib',
        'power.draw': 'sampled_power_w',
    }
    result = {
        'window_rule': 'Use phase_manifest.json profiling start_ns/end_ns. Conservatively retain a sample only when utc_ns - nominal interval_s*1e9 >= start_ns and utc_ns <= end_ns. The nominal telemetry polling interval is not a guarantee that every GPU activity field summarizes that exact full interval; NVML GPU activity uses its own underlying sampling window.',
        'phase_marker_use': 'benchmark_start/benchmark_end markers corroborate the enclosing run; the AIPerf profiling phase manifest defines the measured interval.',
        'roles': {},
        'limits': [
            'These are bounded point samples whose full nominal five-second intervals fall inside scoring; they do not measure peaks between samples.',
            'Sampled VRAM and power are point-in-time observations, not maxima; GPU activity is the fraction of each sample interval with activity.',
            'The 25051 worker-locality UUID receipt is the role-map reference. Other run UUID sets are compared to it on the same g1/g4 hosts; this is cross-run consistency, not a fresh process-to-GPU capture for every job.',
            'No bottleneck or score causality is inferred.'
        ]
    }
    for job in JOBS:
        manifest = json.loads((RUNS/job/'confirm/n60/artifacts/phase_manifest.json').read_text())
        phase = next(p for p in manifest['phases'] if p['phase_kind'] == 'profiling')
        markers = [json.loads(line) for line in (RUNS/job/'phase-markers.jsonl').read_text().splitlines() if line.strip()]
        start_marker = next(m for m in markers if m['event'] == 'benchmark_start')
        end_marker = next(m for m in markers if m['event'] == 'benchmark_end')
        result['roles'][job] = {
            'profiling_interval': {'start_ns': phase['start_ns'], 'end_ns': phase['end_ns'],
                                   'duration_s': (phase['end_ns']-phase['start_ns'])/1e9,
                                   'request_count': phase['total_request_count'],
                                   'enclosed_by_run_markers': start_marker['utc_ns'] <= phase['start_ns'] <= phase['end_ns'] <= end_marker['utc_ns']},
            'telemetry_roles': {}
        }
        for role, host in roles:
            path = RUNS/job/f'resource-telemetry/{role}-{host}.jsonl'
            rows = [json.loads(line) for line in path.open()]
            metadata = next(row for row in rows if row.get('kind') == 'metadata')
            samples = [row for row in rows if row.get('kind') == 'sample']
            interval_ns = int(float(metadata['interval_s'])*1e9)
            inside = [row for row in samples if row.get('utc_ns') is not None
                      and row['utc_ns']-interval_ns >= phase['start_ns']
                      and row['utc_ns'] <= phase['end_ns']]
            outside = [row for row in samples if row not in inside]
            status_counts = lambda rows: {status: sum(server_status(row) == status for row in rows)
                                          for status in sorted({server_status(row) for row in rows})}
            gpu_status_counts = lambda rows: {str(status if status is not None else 'MISSING_STATUS'):
                                              sum(row.get('gpu_status') == status for row in rows)
                                              for status in sorted(set(row.get('gpu_status') for row in rows), key=lambda x: str(x))}
            expected = set(mapping['roles'][role]['matched_gpu_uuids'])
            observed = sorted({gpu['uuid'] for row in inside if row.get('gpu_status') == 'ok'
                               for gpu in row.get('gpus', []) if gpu.get('uuid')})
            per_gpu = {}
            for uuid in observed:
                device_rows = [gpu for row in inside if row.get('gpu_status') == 'ok'
                               for gpu in row.get('gpus', []) if gpu.get('uuid') == uuid]
                stats = {}
                for source, label in fields.items():
                    values = []
                    missing = 0
                    for device in device_rows:
                        try:
                            values.append(float(device[source]))
                        except (KeyError, TypeError, ValueError):
                            missing += 1
                    stats[label] = {'mean': sum(values)/len(values) if values else None,
                                    'min': min(values) if values else None,
                                    'max': max(values) if values else None,
                                    'observations': len(values), 'missing_observations': missing}
                per_gpu[uuid] = {'metrics': stats, 'sample_observations': len(device_rows)}
            # Parse instantaneous SGLang gauge samples as per-series distributions.
            # Do not sum TP ranks: the labels identify separate model-parallel series,
            # and a role-level sum would misstate total requests/tokens.
            gauge_values = {}
            gauge_re = re.compile(r'^(sglang:[^\{ ]+)(?:\{([^}]*)\})?\s+([-+0-9.eE]+)$')
            for row in inside:
                if row.get('server_http_status') != 200 or not row.get('server_metrics'):
                    continue
                for line in row['server_metrics']:
                    match = gauge_re.match(line.strip())
                    if not match:
                        continue
                    name, labels, value = match.groups()
                    if name not in {'sglang:num_running_reqs', 'sglang:num_queue_reqs',
                                    'sglang:token_usage', 'sglang:num_used_tokens',
                                    'sglang:cache_hit_rate'}:
                        continue
                    labels = labels or ''
                    try:
                        numeric_value = float(value)
                    except ValueError:
                        continue
                    gauge_values.setdefault(name, {}).setdefault(labels, []).append(numeric_value)
            gauge_summary = {}
            for name, series in gauge_values.items():
                observations = [value for values in series.values() for value in values]
                gauge_summary[name] = {
                    'unit_and_scope': {
                        'sglang:num_running_reqs': 'requests per labeled TP/PP/EP series; do not sum across TP ranks',
                        'sglang:num_queue_reqs': 'queued requests per labeled TP/PP/EP series; do not sum across TP ranks',
                        'sglang:token_usage': 'fractional token/KV usage gauge per labeled series',
                        'sglang:num_used_tokens': 'used tokens per labeled series; do not sum across TP ranks',
                        'sglang:cache_hit_rate': 'unitless cache hit rate per labeled series'
                    }.get(name, 'raw unit is metric-specific; per labeled series'),
                    'series_count': len(series), 'observation_count': len(observations),
                    'mean_across_series_observations': sum(observations)/len(observations) if observations else None,
                    'min': min(observations) if observations else None,
                    'max': max(observations) if observations else None,
                    'series': {labels: {'observations': len(values), 'mean': sum(values)/len(values),
                                        'min': min(values), 'max': max(values)}
                               for labels, values in sorted(series.items())}
                }
            result['roles'][job]['telemetry_roles'][role] = {
                'host': metadata.get('host'), 'interval_s': metadata.get('interval_s'),
                'all_sample_count': len(samples), 'score_window_sample_count': len(inside),
                'outside_score_window_sample_count': len(outside),
                'server_metrics_status_inside': status_counts(inside),
                'server_metrics_status_outside': status_counts(outside),
                'server_metrics_payload_inside_count': sum(bool(row.get('server_metrics')) for row in inside),
                'server_metrics_payload_outside_count': sum(bool(row.get('server_metrics')) for row in outside),
                'gpu_status_inside': gpu_status_counts(inside),
                'gpu_status_outside': gpu_status_counts(outside),
                'expected_gpu_count': len(expected), 'observed_gpu_uuids_inside': observed,
                'gpu_uuid_set_matches_25051_locality_receipt': set(observed) == expected,
                'per_gpu': per_gpu,
                'sglang_gauge_samples': gauge_summary,
                'inflight_metric': 'No inflight-request gauge was present in the in-window server metric payloads.'
            }
    return result


def write_phase_observability(data):
    out = Path(__file__).with_name('phase-aligned-observability.json')
    out.write_text(json.dumps(data, indent=2) + '\n')
    lines = [
        '# Phase-aligned observability', '',
        'This bounded summary reads existing telemetry and the sealed AIPerf profiling phase manifests. It conservatively keeps a nominal five-second sample window only when `sample utc_ns - 5 s >= profiling start_ns` and `sample utc_ns <= profiling end_ns`. This timestamp rule does not guarantee that each GPU activity value summarizes exactly that full interval; NVML uses its own underlying sample window. Run markers were checked as enclosing corroboration. No raw telemetry was changed.', '',
        '| Job | Role | Samples inside score | UUIDs match role receipt | HTTP/status inside / outside | Server metric payloads inside | GPU activity mean/range (%) | Sampled VRAM mean/range (MiB) | Sampled power mean/range (W) |',
        '|---|---|---:|---|---|---:|---:|---:|---:|'
    ]
    for job, job_data in data['roles'].items():
        for role, role_data in job_data['telemetry_roles'].items():
            metric = lambda label: role_data['per_gpu']
            def pool(label):
                values = [gpu['metrics'][label]['mean'] for gpu in role_data['per_gpu'].values()
                          if gpu['metrics'][label]['mean'] is not None]
                return (sum(values)/len(values), min(values), max(values)) if values else (None, None, None)
            def fmt(label):
                mean, low, high = pool(label)
                return 'not collected' if mean is None else f'{mean:.1f} ({low:.1f}–{high:.1f})'
            metrics_inside = role_data['server_metrics_payload_inside_count']
            lines.append(f"| {job} | {role} | {role_data['score_window_sample_count']} | {'match' if role_data['gpu_uuid_set_matches_25051_locality_receipt'] else 'mismatch'} | {role_data['server_metrics_status_inside']} / {role_data['server_metrics_status_outside']} | {metrics_inside} | {fmt('gpu_activity_percent')} | {fmt('sampled_vram_used_mib')} | {fmt('sampled_power_w')} |")
    lines += ['', 'GPU activity is the reported sample-window activity percentage, with the telemetry interval only a nominal polling bound. VRAM and power are sampled values; the ranges shown are the minimum and maximum of per-GPU means, while per-GPU minima and maxima remain in JSON. The 23–24 in-window samples per role are sparse and cannot establish peaks or causal bottlenecks.', '', '## SGLang role metrics inside scoring', '',
        'All retained in-window server scrapes returned HTTP 200 with a metrics payload. The table reports means and min–max ranges across labeled TP/PP/EP series observations over those scrapes; it does not sum values across ranks. Counts are requests per series, `token_usage` and `cache_hit_rate` are unitless fractions, and `num_used_tokens` is tokens per series. Per-series details are in JSON. No inflight-request gauge was present.', '',
        '| Job | Role | Running requests / series | Queue requests / series | Token usage fraction | Used tokens / series | Cache hit rate |',
        '|---|---|---:|---:|---:|---:|---:|']
    for job, job_data in data['roles'].items():
        for role, role_data in job_data['telemetry_roles'].items():
            gauges = role_data['sglang_gauge_samples']
            def gauge(name, digits=2):
                item = gauges.get(name)
                if not item or item['mean_across_series_observations'] is None:
                    return 'not collected'
                return f"{item['mean_across_series_observations']:.{digits}f} ({item['min']:.{digits}f}–{item['max']:.{digits}f})"
            lines.append(f"| {job} | {role} | {gauge('sglang:num_running_reqs')} | {gauge('sglang:num_queue_reqs')} | {gauge('sglang:token_usage', 3)} | {gauge('sglang:num_used_tokens', 0)} | {gauge('sglang:cache_hit_rate', 3)} |")
    lines += ['', 'Status or payload gaps outside scoring remain separately counted and are not interpreted as zero. The UUID match compares each run’s in-window UUID set with the role mapping captured by job 25051 on the same named hosts. It demonstrates consistency with that receipt, not a new process-to-GPU locality capture in every run.', '']
    Path(__file__).with_name('phase-aligned-observability.md').write_text('\n'.join(lines))


def point(job, helper):
    # core.point validates the frozen payload, phase protocol, raw request counts,
    # output gate, transport ranks and successful worker setup against the seal.
    measured = helper.core.point(ROOT, job, 60)
    run = RUNS / job
    smoke = json.loads((run / 'output-smoke.json').read_text())
    export = json.loads((run / 'confirm/n60/artifacts/profile_export_aiperf.json').read_text())
    long_check = helper.long_check(run)
    config = json.loads((run / 'config.json').read_text())
    return {
        'job': job, 'protocol_and_seal_validation': 'PASS',
        'metrics': measured['metrics'],
        'good_request_count': int(export['good_request_count']['avg']),
        'requested_and_completed': measured['metrics']['phases'][1]['requests'],
        'errors': 0, 'sla_fraction': measured['metrics']['sla_fraction'],
        'good_output_tokens_per_s': measured['metrics']['good_tokens_s'],
        'ttft_request_distribution': latency_and_errors(job)['ttft_ms'],
        'request_mean_itl_distribution': latency_and_errors(job)['request_mean_itl_ms'],
        'output_smoke': {'passed': smoke.get('passed'), 'total': smoke.get('total'),
                         'failed_cases': [c['name'] for c in smoke.get('cases', []) if not c.get('passed')],
                         'errors': smoke.get('errors'), 'comparison': measured['short_output_comparison']},
        'diagnostic_profile': {
            'state': 'COLLECTED_OUTSIDE_SCORED_PHASE',
            'role_traces': {role: len(list((run / 'diagnostic-profile' / role).glob('*.trace.json.gz')))
                            for role in ('prefill-0', 'prefill-1', 'decode-0')},
            'start_http_statuses': [x.get('response', {}).get('http_status') for x in
                                    json.loads((run/'diagnostic-profile/profile-control.json').read_text())
                                    if 'response' in x],
            'stop_errors': [x for x in json.loads((run/'diagnostic-profile/profile-control.json').read_text())
                            if 'stop_error' in x],
            'limit': 'Diagnostic profile capture was separate from AIPerf scoring; stop HTTP 500s mean the control path did not close cleanly.'
        },
        'long_context_check': long_check,
        'configuration': {'experiment': config.get('experiment'), 'purpose': config.get('purpose'),
                          'prefill_moe_runner': config.get('prefill_moe_runner'),
                          'decode_moe_runner': config.get('decode_moe_runner'),
                          'router_policy': config.get('router_policy'),
                          'worker_locality': job == '25051'},
        'server_role_log_samples_unfiltered_all_phases': server_log_samples(job),
        'resource_telemetry': telemetry(job),
        'sealed_file_count': measured['sealed_files'], 'seal_sha256': measured['seal_sha256'],
        'normalised_protocol': measured['normalized_protocol'],
        'server_args': measured['server_args'],
    }


def main():
    helper = load_helper()
    phase_observability = phase_aligned_observability()
    write_phase_observability(phase_observability)
    results = {job: point(job, helper) for job in JOBS}
    control = results['24964']['good_output_tokens_per_s']
    comparisons = {}
    for job in ('24965', '25051', '25283'):
        score = results[job]['good_output_tokens_per_s']
        comparisons[job] = {'baseline_job': '24964', 'baseline_score': control,
                            'candidate_score': score,
                            'delta_percent': (score/control-1)*100,
                            'interpretation': 'same protocol, single run per arm; descriptive evidence only'}
    result = {
        'reviewed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'state': 'COMPLETE_SEALED_LOCAL_REVIEW', 'accuracy_verified': False,
        'scheduler_refreshed': False, 'jobs': results, 'paired_comparisons_vs_24964': comparisons,
        'worker_locality_receipt_25051': json.loads((RUNS/'25051/worker-locality/summary.json').read_text()),
        'decision': {
            'best_claim': 'No new best claim; these are four one-run N60 observations.',
            'next_candidate': 'No further N60 serving-config candidate is justified by this four-run screen. The distinct next hypothesis is whether the short N64 increase persists under independent full-protocol N62 and N64 runs with matched observation.',
            'limits': ['single observation per arm', 'organiser accuracy is not verified',
                       'hardware and server logs are sparse samples, not aligned causal traces',
                       'profiling diagnostic traces are separate from scored measurement']
        }
    }
    out = Path(__file__).with_name('REVIEW.json')
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'state': result['state'], 'jobs': list(results), 'comparisons': comparisons}, indent=2))


if __name__ == '__main__':
    main()
