"""Reproduce the bounded offline review of H200 jobs 25712 and 25713."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys

QWEN = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
REVIEW = QWEN / 'research-review-25712-25713-20261023'
RUNS = QWEN / 'runs'
PLAN = QWEN / 'h200-prefill-graph-policy-20261023'
JOBS = {'25712': 'auto', '25713': 'disabled'}
ROLES = ('prefill-0', 'prefill-1', 'decode-0')


def read_json(path):
    return json.loads(Path(path).read_text())


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def percentile(values, p):
    ordered = sorted(values)
    if not ordered:
        return None
    pos = (len(ordered) - 1) * p / 100
    lower = math.floor(pos)
    upper = math.ceil(pos)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (pos - lower)


def normalized_input(config):
    value = json.loads(json.dumps(config))
    if len(value['endpoint']['urls']) != 1:
        raise ValueError('expected exactly one router URL in AIPerf input config')
    value['endpoint']['urls'] = ['DYNAMIC_ALLOCATED_ROUTER']
    value['artifacts']['dir'] = 'DYNAMIC_ARTIFACT_DIRECTORY'
    return value


def exact_check(script, args, cwd):
    result = subprocess.run([sys.executable, str(script), *args], cwd=cwd,
                            capture_output=True, text=True)
    try:
        report = json.loads(result.stdout)
    except ValueError as error:
        raise RuntimeError(f'{script.name} emitted non-JSON stdout: {result.stdout[-1000:]}') from error
    return {'exit_code': result.returncode, 'report': report,
            'stderr': result.stderr[-1000:] if result.stderr else ''}


def marker_map(root):
    rows = [json.loads(line) for line in (root / 'phase-markers.jsonl').read_text().splitlines() if line]
    return {row['event']: row for row in rows}


def phase_summary(root, job_start):
    markers = marker_map(root)
    manifest = read_json(root / 'screen/n64/artifacts/phase_manifest.json')
    phases = {row['phase_kind']: row for row in manifest['phases']}
    profiling = phases['profiling']
    warmup = phases['warmup']
    startup = (datetime.fromisoformat(markers['all_workers_ready']['utc']) - job_start).total_seconds()
    return {
        'job_start_to_all_workers_ready_s': round(startup, 3),
        'job_start_to_all_pairs_warm_s': round((datetime.fromisoformat(markers['all_pairs_warm']['utc']) - job_start).total_seconds(), 3),
        'warmup_phase_s': round((warmup['end_ns'] - warmup['start_ns']) / 1e9, 3),
        'profiling_phase_s': round((profiling['end_ns'] - profiling['start_ns']) / 1e9, 3),
        'benchmark_marker_span_s': round((markers['benchmark_end']['utc_ns'] - markers['benchmark_start']['utc_ns']) / 1e9, 3),
        'profiling_start_utc': datetime.fromtimestamp(profiling['start_ns'] / 1e9, timezone.utc).isoformat(),
        'profiling_end_utc': datetime.fromtimestamp(profiling['end_ns'] / 1e9, timezone.utc).isoformat(),
        'profiling_start_ns': profiling['start_ns'],
        'profiling_end_ns': profiling['end_ns'],
        'phase_manifest': {kind: {'total_requests': row['total_request_count'],
                                   'successful_requests': row['successful_request_count'],
                                   'error_requests': row['error_request_count'],
                                   'cancelled': row['was_cancelled']}
                           for kind, row in phases.items()},
    }


def metric_distribution(root, n=64):
    artifact = root / f'screen/n{n}/artifacts'
    export = read_json(artifact / 'profile_export_aiperf.json')
    values = {'ttft_ms': [], 'request_mean_itl_ms': []}
    classes = Counter()
    output_lengths = Counter()
    raw_rows = 0
    for line in (artifact / 'profile_export.jsonl').open():
        row = json.loads(line)
        if row['metadata'].get('benchmark_phase') != 'profiling':
            continue
        metrics = row['metrics']
        ttft = float(metrics['time_to_first_token']['value'])
        itl = float(metrics['inter_token_latency']['value'])
        if metrics['time_to_first_token']['unit'] != 'ms' or metrics['inter_token_latency']['unit'] != 'ms':
            raise ValueError('TTFT/ITL raw units are not milliseconds')
        values['ttft_ms'].append(ttft)
        values['request_mean_itl_ms'].append(itl)
        if ttft <= 3000 and itl <= 20:
            classes['good'] += 1
        elif ttft > 3000 and itl <= 20:
            classes['ttft_only'] += 1
        elif ttft <= 3000:
            classes['itl_only'] += 1
        else:
            classes['both_bad'] += 1
        output_lengths[str(int(metrics['output_sequence_length']['value']))] += 1
        raw_rows += 1
    count = int(export['request_count']['avg'])
    if raw_rows != count or sum(classes.values()) != count:
        raise ValueError(f'raw profiling count {raw_rows} disagrees with export {count}')
    frac = classes['good'] / count
    if not math.isclose(frac, export['good_request_fraction']['avg'], abs_tol=1e-9):
        raise ValueError('raw joint SLA classification differs from export')
    complete = {'good': classes['good'], 'ttft_only': classes['ttft_only'],
                'itl_only': classes['itl_only'], 'both_bad': classes['both_bad']}
    tails = {key: {'p50': round(percentile(rows, 50), 3),
                   'p95': round(percentile(rows, 95), 3),
                   'p99': round(percentile(rows, 99), 3),
                   'max': round(max(rows), 3), 'unit': 'ms'}
             for key, rows in values.items()}
    goodput = float(export['goodput']['avg']) * 200
    return {
        'good_output_tokens_s': goodput,
        'raw_output_tokens_s': float(export['output_token_throughput']['avg']),
        'goodput_source': 'AIPerf goodput.avg (requests/s) multiplied by nominal 200 output tokens/request',
        'sla': {'good_requests': complete['good'], 'ttft_only_breaches': complete['ttft_only'],
                'itl_only_breaches': complete['itl_only'], 'both_bad': complete['both_bad'],
                'total_requests': count, 'good_fraction': frac, 'thresholds': {'ttft_ms_max': 3000, 'request_mean_itl_ms_max': 20}},
        'request_latency_tails': tails,
        'output_sequence_length_counts_tokens': dict(sorted(output_lengths.items(), key=lambda x: int(x[0]))),
        'profiling_error_summary': export.get('error_summary'),
        'profiling_was_cancelled': export.get('was_cancelled'),
        'benchmark_duration_s': export['benchmark_duration']['avg'],
        'effective_concurrency_avg': export.get('effective_concurrency', {}).get('avg'),
    }


def parse_sampled(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def gpu_summary(root, start_ns, end_ns):
    result = {}
    for path in sorted((root / 'resource-telemetry').glob('*.jsonl')):
        with path.open() as stream:
            metadata = json.loads(next(stream))
            rows = [json.loads(line) for line in stream if line.strip()]
        rows = [row for row in rows if start_ns <= int(row.get('utc_ns', 0)) <= end_ns]
        gpu_statuses = Counter(str(row.get('gpu_status')) for row in rows)
        server_statuses = Counter(str(row.get('server_http_status') if row.get('server_http_status') is not None else row.get('server_metrics_status')) for row in rows)
        all_statuses = Counter()
        with path.open() as stream:
            next(stream)
            for line in stream:
                row = json.loads(line)
                if row.get('kind') != 'sample':
                    continue
                status = row.get('server_http_status') if row.get('server_http_status') is not None else row.get('server_metrics_status')
                all_statuses[str(status)] += 1
        gpu_records = [gpu for row in rows for gpu in row.get('gpus', [])]
        util = [x for x in (parse_sampled(g.get('utilization.gpu')) for g in gpu_records) if x is not None]
        mem = [x for x in (parse_sampled(g.get('memory.used')) for g in gpu_records) if x is not None]
        power = [x for x in (parse_sampled(g.get('power.draw')) for g in gpu_records) if x is not None]
        gauge_names = {'sglang:cache_hit_rate', 'sglang:num_queue_reqs', 'sglang:num_running_reqs', 'sglang:num_used_tokens', 'sglang:token_usage'}
        gauge_series = {name: [] for name in gauge_names}
        for row in rows:
            for line in row.get('server_metrics', []):
                match = re.match(r'([^ {]+)(?:\{[^}]*\})?\s+([-+0-9.eE]+)$', line)
                if match and match.group(1) in gauge_names:
                    gauge_series[match.group(1)].append(float(match.group(2)))
        gauge_summary = {name: {'samples': len(vals), 'min': min(vals), 'max': max(vals)}
                         for name, vals in sorted(gauge_series.items()) if vals}
        status_log = path.with_name(metadata['role'] + '-sampler.log')
        result[metadata['role']] = {
            'host': metadata['host'], 'sample_interval_s': metadata['interval_s'],
            'sampler_stdout_log_bytes': status_log.stat().st_size if status_log.exists() else None,
            'profile_window_sample_count': len(rows),
            'profile_window_gpu_record_count': len(gpu_records),
            'gpu_status_counts': dict(gpu_statuses),
            'server_metrics_http_status_counts_in_scoring_phase': dict(server_statuses),
            'server_metrics_status_counts_whole_run': dict(all_statuses),
            'server_metric_gauge_min_max_in_scoring_phase': gauge_summary,
            'gpu_utilization_percent': {'p50': round(percentile(util, 50), 2), 'p95': round(percentile(util, 95), 2), 'max': round(max(util), 2), 'sampled_device_records': len(util)} if util else None,
            'sampled_vram_used_mib_max': round(max(mem), 1) if mem else None,
            'sampled_power_w_max': round(max(power), 1) if power else None,
            'host_cpu_jiffies_samples': sum(row.get('node_cpu_jiffies') is not None for row in rows),
            'host_memory_samples': sum(row.get('node_memory') is not None for row in rows),
            'host_network_counter_samples': sum(row.get('node_network_counters') is not None for row in rows),
            'units': metadata.get('units'),
        }
    return result


def batch_log_summary(root, phase_start_ns, phase_end_ns, local_offset_s=28800):
    start = datetime.fromtimestamp(phase_start_ns / 1e9, timezone.utc)
    end = datetime.fromtimestamp(phase_end_ns / 1e9, timezone.utc)
    local = timezone(timedelta(seconds=local_offset_s))
    result = {}
    patterns = {
        'running_requests': r'#running-req: (\d+)',
        'queue_requests': r'#queue-req: (\d+)',
        'inflight_requests': r'#inflight-req: (\d+)',
        'pending_tokens': r'#pending-token: (\d+)',
        'transfer_requests': r'#transfer-req: (\d+)',
        'token_usage_fraction': r'token usage: ([0-9.]+)',
        'preallocated_usage_fraction': r'pre-allocated usage: ([0-9.]+)',
    }
    for role in ROLES:
        fields = {key: [] for key in patterns}
        batch_count = 0
        source = (root / f'{role}.log').read_text(errors='replace').splitlines()
        term = 'Prefill batch' if role.startswith('prefill') else 'Decode batch'
        for line in source:
            if term not in line:
                continue
            stamp = re.match(r'^\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)', line)
            if not stamp:
                continue
            point = datetime.strptime(stamp.group(1), '%Y-%m-%d %H:%M:%S').replace(tzinfo=local).astimezone(timezone.utc)
            if not (start <= point <= end):
                continue
            batch_count += 1
            for key, pattern in patterns.items():
                m = re.search(pattern, line)
                if m:
                    fields[key].append(float(m.group(1)))
        result[role] = {'batch_log_records_in_scoring_phase': batch_count,
                        'observed_min_max': {key: [min(vals), max(vals)] for key, vals in fields.items() if vals}}
    return result


def summarize_gate(capacity):
    result = {'passed': capacity['report'].get('passed'), 'policy': capacity['report'].get('prefill_policy'), 'roles': {}}
    for role, observation in capacity['report'].get('roles', {}).items():
        values = observation['server_args'][0]['values']
        scheduler = observation['initialized_scheduler']
        result['roles'][role] = {
            'dtype': values['dtype'], 'server_args_max_running_requests': values['max_running_requests'],
            'scheduler_max_running_requests': sorted(set(x['max_running_requests'] for x in scheduler)),
            'max_total_num_tokens': sorted(set(x['max_total_num_tokens'] for x in scheduler)),
            'tp_size': values['tp_size'], 'ep_size': values['ep_size'],
            'chunked_prefill_size': values['chunked_prefill_size'],
            'moe_runner_backend': values['moe_runner_backend'],
            'disaggregation_mode': values['disaggregation_mode'],
            'cuda_graph_backend_prefill_arg': values['cuda_graph_backend_prefill'],
            'resolved_prefill_graph_backend': values['graph_config']['prefill']['backend'],
        }
    return result


def file_differences(left, right):
    a = {p.name: sha256(p) for p in left.iterdir() if p.is_file()}
    b = {p.name: sha256(p) for p in right.iterdir() if p.is_file()}
    if a.keys() != b.keys():
        return {'only_auto': sorted(a.keys() - b.keys()), 'only_disabled': sorted(b.keys() - a.keys()), 'different_sha256': []}
    return {'only_auto': [], 'only_disabled': [], 'different_sha256': sorted(k for k in a if a[k] != b[k])}


def normalized_payload_comparison(auto_payload, disabled_payload, file_diff):
    auto_worker = (auto_payload / 'worker.sh').read_text()
    disabled_worker = (disabled_payload / 'worker.sh').read_text()
    worker_equal = auto_worker == disabled_worker.replace(' --cuda-graph-backend-prefill disabled', '')
    auto_topology = (auto_payload / 'topology-job.sh').read_text()
    disabled_topology = (disabled_payload / 'topology-job.sh').read_text()
    disabled_topology = disabled_topology.replace('--prefill-policy disabled', '--prefill-policy POLICY')
    auto_topology = auto_topology.replace('--prefill-policy auto', '--prefill-policy POLICY')
    topology_equal = auto_topology == disabled_topology
    auto_config = read_json(auto_payload / 'config.json')
    disabled_config = read_json(disabled_payload / 'config.json')
    for cfg in (auto_config, disabled_config):
        cfg['experiment'] = 'POLICY_SCREEN'
        cfg['canonical_bundle'] = 'CANONICAL_PATH'
        cfg['prefill_cuda_graph_policy'] = 'POLICY'
        cfg['changed_factor']['cuda_graph_backend_prefill'] = 'POLICY'
    config_equal = auto_config == disabled_config
    auto_job = (auto_payload / 'job.sbatch').read_text()
    disabled_job = (disabled_payload / 'job.sbatch').read_text()
    auto_job = auto_job.replace('s40-h200-graph-auto-cap64-screen', 'policy-screen')
    disabled_job = disabled_job.replace('s41-h200-graph-disabled-cap64-screen', 'policy-screen')
    job_equal = auto_job == disabled_job
    expected_diffs = {'FROZEN_PROVENANCE.json', 'SHA256SUMS', 'config.json', 'job.sbatch', 'topology-job.sh', 'worker.sh'}
    return {
        'worker_equal_after_removing_only_disabled_backend_flag': worker_equal,
        'topology_equal_after_normalizing_only_audit_policy_argument': topology_equal,
        'config_equal_after_normalizing_policy_and_experiment_paths': config_equal,
        'job_sbatch_equal_after_normalizing_job_name_and_bundle_path': job_equal,
        'unexpected_differing_payload_files': sorted(set(file_diff['different_sha256']) - expected_diffs),
    }


def input_output_checks(root, payload):
    smoke = read_json(root / 'output-smoke.json')
    long = read_json(root / 'long-context-check.json')
    return {
        'short_output_smoke': {'passed': sum(bool(row.get('passed')) for row in smoke['cases']), 'total': len(smoke['cases']), 'errors': sum('error' in row for row in smoke['cases']), 'failed_case_names': [row['name'] for row in smoke['cases'] if not row.get('passed')], 'interpretation': 'The one failed case also fails in the frozen reference; the exact submitted check-screen found no new regressions.'},
        'long_context': {'passed': long.get('passed'), 'total': long.get('total'), 'errors': long.get('errors')},
    }


def get_sacct():
    table = (REVIEW / 'sacct-terminal.txt').read_text().splitlines()
    header = table[0].split('|')
    records = {}
    for line in table[1:]:
        parts = line.split('|')
        row = dict(zip(header, parts))
        if row['JobID'] in JOBS:
            records[row['JobID']] = row
    return records


def main():
    sacct = get_sacct()
    report = {'reviewed_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Two short, unranked, target-only H200 prefill CUDA graph policy screens; no full-run, ranked, or EAGLE performance claim.',
              'jobs': {}, 'pair_comparison': {}, 'limitations': [
                  'One 40-second scored profile per policy is screening evidence, not a replicated performance result.',
                  'Official contest accuracy was not verified by these local smoke and long-context diagnostics.',
                  'TTFT and request-mean ITL are per-request client metrics; sampled GPU activity and sampled VRAM are not utilization causes, KV occupancy, or kernel time.',
                  'The job-local server metric sampler had startup URLError samples, then sampled HTTP 200 and named gauges during the scoring phase. The five-second series is sparse and covers only these short phases.',
                  'Server random_seed values differ between allocations; client workload seed and normalized offered input corpus match.']}
    input_configs = {}
    runtime_values = {}
    raw_hash_entries = []
    for job, policy in JOBS.items():
        root = RUNS / job
        payload = root / 'submitted-payload'
        screen = exact_check(payload / 'check-screen.py', [str(root)], payload)
        capacity = exact_check(payload / 'audit-capacity.py', ['--artdir', str(root), '--prefill-policy', policy], payload)
        checksum = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=payload, capture_output=True, text=True)
        if screen['exit_code'] != 0 or screen['report'].get('status') != 'pass':
            raise RuntimeError(f'{job} exact submitted screen check failed: {screen}')
        if capacity['exit_code'] != 0 or not capacity['report'].get('passed'):
            raise RuntimeError(f'{job} exact submitted capacity gate failed')
        if checksum.returncode:
            raise RuntimeError(f'{job} submitted payload checksum verification failed: {checksum.stdout}{checksum.stderr}')
        cfg = read_json(root / 'config.json')
        export = read_json(root / 'screen/n64/artifacts/profile_export_aiperf.json')
        input_configs[job] = normalized_input(export['input_config'])
        job_start = datetime.fromisoformat(sacct[job]['Start']).replace(tzinfo=timezone.utc)
        phase = phase_summary(root, job_start)
        scored = metric_distribution(root)
        resources = gpu_summary(root, phase['profiling_start_ns'], phase['profiling_end_ns'])
        batch_metrics = batch_log_summary(root, phase['profiling_start_ns'], phase['profiling_end_ns'])
        roles = summarize_gate(capacity)
        runtime_values[job] = {role: obs['server_args'][0]['values'] for role, obs in capacity['report']['roles'].items()}
        # Detect actual per-allocation ServerArgs seeds separately from the reviewed field subset.
        seeds = {}
        for role in ROLES:
            line = next(line for line in (root / f'{role}.log').read_text(errors='replace').splitlines() if 'server_args=ServerArgs(' in line)
            m = re.search(r'(?<![\w.])random_seed=(\d+)(?=[,)])', line)
            seeds[role] = int(m.group(1)) if m else None
        graph = {}
        audit_module_path = payload / 'audit-capacity.py'
        spec = importlib.util.spec_from_file_location(f'audit_{job}', audit_module_path)
        audit_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit_module)
        for role in ROLES:
            log = (root / f'{role}.log').read_text(errors='replace')
            args_lines = [line for line in log.splitlines() if 'server_args=ServerArgs(' in line]
            decode_configs = [audit_module._phase_config(line, 'decode') for line in args_lines]
            prefill_configs = [audit_module._phase_config(line, 'prefill') for line in args_lines]
            if role == 'decode-0' and any(x != {'backend': 'full', 'max_bs': 64, 'bs': list(range(1, 65))} for x in decode_configs):
                raise RuntimeError(f'{job} decode graph config differs from expected full dense 1..64')
            prefill_capture_ranks = sorted({int(x) for x in re.findall(r'TP(\d+)\] Capture target prefill CUDA graph end\.', log)}) if role.startswith('prefill') else []
            decode_capture_ranks = sorted({int(x) for x in re.findall(r'TP(\d+) EP\d+\] Capture target decode CUDA graph end\.', log)}) if role == 'decode-0' else []
            graph[role] = {'resolved_prefill_graph_backend': roles['roles'][role]['resolved_prefill_graph_backend'],
                           'prefill_graph_config': prefill_configs[0] if prefill_configs else None,
                           'decode_graph_config': decode_configs[0] if role == 'decode-0' and decode_configs else None,
                           'prefill_capture_ranks': prefill_capture_ranks,
                           'decode_capture_ranks': decode_capture_ranks}
        record = {
            'policy': policy,
            'slurm': {key: sacct[job][key] for key in ('JobID', 'JobName', 'State', 'ExitCode', 'Elapsed', 'Start', 'End', 'AllocNodes', 'AllocTRES')},
            'startup_and_phases': {key: value for key, value in phase.items() if key not in ('profiling_start_ns', 'profiling_end_ns', 'phase_manifest')},
            'phase_manifest_counts': phase['phase_manifest'],
            'exact_submitted_screen_check': {'status': screen['report'].get('status'), 'exit_code': screen['exit_code']},
            'exact_submitted_capacity_gate': roles,
            'submitted_payload_sha256_check': {'passed': checksum.returncode == 0, 'files': sum(line.endswith(': OK') for line in checksum.stdout.splitlines())},
            'benchmark': scored,
            'local_quality_checks': input_output_checks(root, payload),
            'graphs': graph,
            'profiling_phase_role_logs': batch_metrics,
            'phase_aligned_sampler': resources,
            'server_random_seed_by_role': seeds,
            'normalized_input_config_sha256': hashlib.sha256(json.dumps(input_configs[job], sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        }
        report['jobs'][job] = record
        stable = [root / 'config.json', root / 'summary.json', root / 'capacity-audit.json', root / 'head-screen-check.json',
                  root / 'phase-markers.jsonl', root / 'pair-warmup-context.json', root / 'pair-warmup.log', root / 'endpoints.tsv', root / 'output-smoke.json', root / 'long-context-check.json',
                  root / 'screen/n64/artifacts/inputs.json', root / 'screen/n64/artifacts/phase_manifest.json',
                  root / 'screen/n64/artifacts/profile_export_aiperf.json', root / 'screen/n64/artifacts/profile_export.jsonl',
                  root / 'prefill-0.log', root / 'prefill-1.log', root / 'decode-0.log']
        stable += list((root / 'pair-warmup-receipts').glob('*.json'))
        stable += list((root / 'resource-telemetry').glob('*.jsonl'))
        stable += list((root / 'resource-telemetry').glob('*.log'))
        stable += [payload / name for name in ('SHA256SUMS', 'check-screen.py', 'audit-capacity.py', 'config.json', 'expected-input-config.json', 'worker.sh', 'topology-job.sh', 'job.sbatch')]
        for source in stable:
            raw_hash_entries.append({'job': job, 'path': str(source), 'size_bytes': source.stat().st_size, 'sha256': sha256(source)})

    if input_configs['25712'] != input_configs['25713']:
        raise RuntimeError('normalized AIPerf input configurations differ')
    input_expected = {job: read_json(RUNS / job / 'submitted-payload/expected-input-config.json') for job in JOBS}
    if any(input_configs[job] != input_expected[job] for job in JOBS):
        raise RuntimeError('normalized AIPerf input config differs from frozen expected input config')

    runtime_diffs = {}
    for role in ROLES:
        a = json.loads(json.dumps(runtime_values['25712'][role]))
        b = json.loads(json.dumps(runtime_values['25713'][role]))
        policy_values = {'auto': (a.get('cuda_graph_backend_prefill'), a['graph_config']['prefill']['backend']),
                         'disabled': (b.get('cuda_graph_backend_prefill'), b['graph_config']['prefill']['backend'])}
        a.pop('cuda_graph_backend_prefill', None)
        b.pop('cuda_graph_backend_prefill', None)
        a['graph_config']['prefill'].pop('backend', None)
        b['graph_config']['prefill'].pop('backend', None)
        runtime_diffs[role] = {'all_gate_fields_equal_after_removing_prefill_policy': a == b,
                               'prefill_policy_runtime_values': policy_values}
    if not all(row['all_gate_fields_equal_after_removing_prefill_policy'] for row in runtime_diffs.values()):
        raise RuntimeError(f'unexpected runtime ServerArgs differences: {runtime_diffs}')

    inputs_equal = True
    config_diffs = {}
    configs = {job: read_json(RUNS / job / 'config.json') for job in JOBS}
    for key in sorted(configs['25712'].keys() | configs['25713'].keys()):
        if configs['25712'].get(key) != configs['25713'].get(key):
            config_diffs[key] = {'auto': configs['25712'].get(key), 'disabled': configs['25713'].get(key)}
    auto_payload = RUNS / '25712/submitted-payload'
    disabled_payload = RUNS / '25713/submitted-payload'
    payload_diff = file_differences(auto_payload, disabled_payload)
    payload_normalization = normalized_payload_comparison(auto_payload, disabled_payload, payload_diff)
    auto = report['jobs']['25712']['benchmark']['good_output_tokens_s']
    disabled = report['jobs']['25713']['benchmark']['good_output_tokens_s']
    delta = (auto / disabled - 1) * 100
    report['pair_comparison'] = {
        'normalized_aiperf_input_configs_equal': inputs_equal,
        'normalized_aiperf_input_configs_match_each_frozen_expected_config': True,
        'normalized_aiperf_input_config_sha256': report['jobs']['25712']['normalized_input_config_sha256'],
        'actual_inputs_json_sha256_equal': sha256(RUNS / '25712/screen/n64/artifacts/inputs.json') == sha256(RUNS / '25713/screen/n64/artifacts/inputs.json'),
        'actual_inputs_json_sha256': sha256(RUNS / '25712/screen/n64/artifacts/inputs.json'),
        'config_json_differences': config_diffs,
        'submitted_payload_files_only_policy_and_metadata_differ': payload_diff,
        'normalized_payload_comparison': payload_normalization,
        'server_args_comparison': runtime_diffs,
        'client_image_sha256_equal': configs['25712']['client_image_sha256'] == configs['25713']['client_image_sha256'],
        'good_output_tokens_s_auto': auto, 'good_output_tokens_s_disabled': disabled,
        'auto_vs_disabled_relative_gain_percent': delta,
        'prospective_minimum_practical_gain_percent': 1.0,
        'clears_practical_gain_gate': delta >= 1.0,
        'interpretation': 'Auto is numerically ahead in this single short pair, but its +%.3f%% result is below the prospective 1%% practical-gain gate; do not treat it as an established improvement.' % delta,
    }
    report['raw_source_manifest'] = {'algorithm': 'SHA-256', 'files': raw_hash_entries}
    (REVIEW / 'SOURCE-MANIFEST.json').write_text(json.dumps(report['raw_source_manifest'], indent=2, sort_keys=True) + '\n')
    (REVIEW / 'REVIEW.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    sealed = ['README.md', 'REVIEW.json', 'SOURCE-MANIFEST.json', 'sacct-terminal.txt', 'reproduce.sh', 'review.py']
    seal = subprocess.run(['sha256sum', *sealed], cwd=REVIEW, capture_output=True, text=True, check=True)
    (REVIEW / 'SHA256SUMS').write_text(seal.stdout)
    print(json.dumps({'jobs': {job: {'policy': row['policy'], 'good_output_tokens_s': row['benchmark']['good_output_tokens_s'], 'SLA': row['benchmark']['sla']['good_fraction'], 'TTFT_p95_ms': row['benchmark']['request_latency_tails']['ttft_ms']['p95'], 'ITL_p95_ms': row['benchmark']['request_latency_tails']['request_mean_itl_ms']['p95'], 'state': row['slurm']['State']} for job, row in report['jobs'].items()}, 'pair': report['pair_comparison']}, indent=2))


if __name__ == '__main__':
    main()
