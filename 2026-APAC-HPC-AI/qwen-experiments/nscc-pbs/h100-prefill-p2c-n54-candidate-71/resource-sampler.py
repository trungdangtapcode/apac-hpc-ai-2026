"""Bounded job-local resource sampler. No model imports, credentials, writes to devices or persistent service."""
import argparse
import csv
import datetime
import io
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request

GPU_FIELDS = ['index', 'uuid', 'name', 'utilization.gpu', 'utilization.memory',
              'memory.used', 'memory.total', 'power.draw', 'temperature.gpu',
              'clocks.sm', 'clocks.mem', 'pstate']
METRICS = {'sglang:num_running_reqs', 'sglang:num_queue_reqs', 'sglang:token_usage',
           'sglang:cache_hit_rate', 'sglang:num_used_tokens', 'sglang:num_prefill_tokens',
           'sglang:num_retracted_reqs_total', 'sglang:time_to_first_token_seconds_sum',
           'sglang:time_to_first_token_seconds_count', 'sglang:inter_token_latency_seconds_sum',
           'sglang:inter_token_latency_seconds_count'}


def sample(gpus, port, proc_root=Path('/proc'), command=subprocess.run):
    begin = time.monotonic()
    row = {'kind': 'sample', 'utc_ns': time.time_ns(), 'monotonic_ns': time.monotonic_ns(),
           'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'local_utc_offset_s': getattr(time.localtime(), 'tm_gmtoff', None)}
    try:
        args = ['nvidia-smi', '--query-gpu=' + ','.join(GPU_FIELDS), '--format=csv,noheader,nounits']
        if gpus:
            args += ['--id=' + gpus]
        result = command(args, capture_output=True, text=True, timeout=2)
        if result.returncode:
            row['gpu_status'] = 'query_failed_exit_' + str(result.returncode)
        else:
            parsed = list(csv.reader(io.StringIO(result.stdout)))
            if not parsed or any(len(values) != len(GPU_FIELDS) for values in parsed):
                row['gpu_status'] = 'invalid_csv_shape'
            else:
                row['gpu_status'] = 'ok'
                # Keep unsupported driver values such as [N/A] explicitly as strings.
                row['gpus'] = [dict(zip(GPU_FIELDS, [x.strip() for x in values])) for values in parsed]
    except (OSError, subprocess.TimeoutExpired) as error:
        row['gpu_status'] = type(error).__name__
    try:
        row['node_cpu_jiffies'] = [int(x) for x in (proc_root / 'stat').read_text().splitlines()[0].split()[1:]]
        memory = {}
        for line in (proc_root / 'meminfo').read_text().splitlines():
            key, value = line.split(':', 1)
            if key in {'MemTotal', 'MemAvailable'}:
                memory[key + '_KiB'] = int(value.split()[0])
        row['node_memory'] = memory
        network = {}
        for line in (proc_root / 'net/dev').read_text().splitlines():
            if ':' not in line:
                continue
            name, value = line.split(':', 1)
            data = value.split()
            network[name.strip()] = {'rx_bytes': int(data[0]), 'tx_bytes': int(data[8])}
        row['node_network_counters'] = network
    except (OSError, ValueError, IndexError) as error:
        row['proc_status'] = type(error).__name__
    try:
        with urllib.request.urlopen('http://127.0.0.1:' + str(port) + '/metrics', timeout=2) as response:
            text = response.read(2 * 1024 * 1024).decode('utf-8', errors='replace')
            row['server_http_status'] = response.status
            row['server_metrics'] = [line for line in text.splitlines()
                if line.split('{', 1)[0].split(' ', 1)[0] in METRICS]
    except (OSError, urllib.error.HTTPError) as error:
        row['server_metrics_status'] = type(error).__name__
    row['sampler_elapsed_s'] = time.monotonic() - begin
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--role', required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--parent', type=int, required=True)
    parser.add_argument('--gpus', default='')
    parser.add_argument('--interval', type=float, default=5)
    parser.add_argument('--duration', type=float, default=2800)
    args = parser.parse_args()
    assert args.interval >= 2 and 0 < args.duration <= 2900 and args.parent > 1
    args.out.mkdir(parents=True, exist_ok=True)
    name = args.role + '-' + socket.gethostname() + '.jsonl'
    deadline = time.monotonic() + args.duration
    stopping = False

    def stop(*_):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    with (args.out / name).open('a', buffering=1) as handle:
        header = {'kind': 'metadata', 'role': args.role, 'host': socket.gethostname(),
                  'parent_pid': args.parent, 'gpu_ids_requested': args.gpus, 'interval_s': args.interval,
                  'max_duration_s': args.duration, 'gpu_fields': GPU_FIELDS,
                  'units': {'utilization.gpu': 'percent of sample period with kernel activity',
                            'utilization.memory': 'percent of sample period with memory activity',
                            'memory.used': 'MiB', 'memory.total': 'MiB', 'power.draw': 'W',
                            'temperature.gpu': 'degrees_C', 'clocks.sm': 'MHz', 'clocks.mem': 'MHz'},
                  'limits': 'Role GPU IDs require UUID verification. Node CPU/network counters are shared by co-located roles; deduplicate by host. Missing fields are not zero. No peak FLOPS or bandwidth utilization claim.'}
        handle.write(json.dumps(header) + '\n')
        while not stopping and time.monotonic() < deadline:
            try:
                os.kill(args.parent, 0)
            except ProcessLookupError:
                break
            begin = time.monotonic()
            handle.write(json.dumps(sample(args.gpus, args.port)) + '\n')
            remaining = max(0, min(args.interval - (time.monotonic() - begin), deadline - time.monotonic()))
            time.sleep(remaining)
        handle.write(json.dumps({'kind': 'sampler_stop', 'utc_ns': time.time_ns()}) + '\n')


if __name__ == '__main__':
    main()
