"""Low-overhead, whole-node procfs sampler; never inspects per-process state."""
from pathlib import Path
import argparse
import datetime
import json
import math
import statistics
import subprocess
import sys
import threading
import time

PROC = Path('/proc')
INTERVAL_SECONDS = 5.0
MAX_PREFLIGHT_READ_MS = 50.0
REQUIRED = ('meminfo', 'vmstat', 'stat_cpu', 'cpu_frequency')
MEM_KEYS = ('MemAvailable', 'MemFree', 'Cached', 'SwapTotal', 'SwapFree', 'SwapCached',
            'Active', 'Inactive', 'Active(anon)', 'Inactive(anon)',
            'Active(file)', 'Inactive(file)')
VM_PREFIXES = ('pgmajfault', 'pswpin', 'pswpout', 'pgscan', 'pgsteal', 'numa_')
_STOP = threading.Event()


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _key_values(path):
    values = {}
    for line in path.read_text(errors='replace').splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try:
                values[parts[0].rstrip(':')] = int(parts[1])
            except ValueError:
                continue
    return values


def _cpu_stat(path):
    for line in path.read_text(errors='replace').splitlines():
        parts = line.split()
        if parts and parts[0] == 'cpu':
            try:
                return {name: int(value) for name, value in zip(
                    ('user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'),
                    parts[1:])}
            except ValueError:
                return None
    return None


def _frequencies(path):
    values = []
    for line in path.read_text(errors='replace').splitlines():
        if line.startswith('cpu MHz'):
            try:
                value = float(line.split(':', 1)[1].strip())
                if math.isfinite(value):
                    values.append(value)
            except (ValueError, IndexError):
                continue
    if not values:
        return {'count': 0, 'minimum_mhz': None, 'median_mhz': None, 'maximum_mhz': None}
    return {'count': len(values), 'minimum_mhz': min(values),
            'median_mhz': statistics.median(values), 'maximum_mhz': max(values)}


def _pressure(path):
    result = {}
    for line in path.read_text(errors='replace').splitlines():
        fields = line.split()
        if not fields:
            continue
        row = {}
        for item in fields[1:]:
            if '=' not in item:
                continue
            key, value = item.split('=', 1)
            try:
                row[key] = float(value)
            except ValueError:
                row[key] = value
        result[fields[0]] = row
    return result


def collect_sample(proc_root=PROC):
    """Collect selected aggregate host counters and explicit component availability."""
    root = Path(proc_root)
    started_ns = time.monotonic_ns()
    timestamp_utc = _utc()
    timestamp_monotonic = time.monotonic()
    sample = {'timestamp_utc': timestamp_utc,
              'timestamp_monotonic_seconds': timestamp_monotonic,
              'availability': {}, 'missing': {}, 'errors': {}}

    try:
        mem = _key_values(root / 'meminfo')
        sample['meminfo_kb'] = {key: mem[key] for key in MEM_KEYS if key in mem}
        sample['availability']['meminfo'] = all(key in mem for key in ('MemAvailable', 'MemFree', 'Cached'))
        if not sample['availability']['meminfo']:
            sample['missing']['meminfo_keys'] = [k for k in ('MemAvailable', 'MemFree', 'Cached') if k not in mem]
    except Exception as exc:
        sample['availability']['meminfo'] = False
        sample['errors']['meminfo'] = type(exc).__name__

    try:
        vm = _key_values(root / 'vmstat')
        sample['vmstat_pages_or_events'] = {key: value for key, value in vm.items()
                                             if key.startswith(VM_PREFIXES)}
        sample['availability']['vmstat'] = any(key.startswith('pgmajfault') for key in vm)
        sample['missing']['vmstat_keys'] = [k for k in ('pgmajfault', 'pswpin', 'pswpout') if k not in vm]
    except Exception as exc:
        sample['availability']['vmstat'] = False
        sample['errors']['vmstat'] = type(exc).__name__

    try:
        sample['aggregate_cpu_ticks'] = _cpu_stat(root / 'stat')
        sample['availability']['stat_cpu'] = sample['aggregate_cpu_ticks'] is not None
        if sample['aggregate_cpu_ticks'] is None:
            sample['missing']['stat_cpu'] = 'aggregate cpu line absent or malformed'
    except Exception as exc:
        sample['aggregate_cpu_ticks'] = None
        sample['availability']['stat_cpu'] = False
        sample['errors']['stat'] = type(exc).__name__

    try:
        sample['cpuinfo_frequency'] = _frequencies(root / 'cpuinfo')
        sample['availability']['cpu_frequency'] = sample['cpuinfo_frequency']['count'] > 0
        if not sample['availability']['cpu_frequency']:
            sample['missing']['cpu_frequency'] = 'no parseable cpu MHz records'
    except Exception as exc:
        sample['cpuinfo_frequency'] = {'count': 0, 'minimum_mhz': None, 'median_mhz': None, 'maximum_mhz': None}
        sample['availability']['cpu_frequency'] = False
        sample['errors']['cpuinfo'] = type(exc).__name__

    pressure = {}
    for name in ('cpu', 'io', 'memory'):
        try:
            pressure[name] = {'available': True, 'metrics': _pressure(root / 'pressure' / name)}
        except FileNotFoundError:
            pressure[name] = {'available': False, 'missing': 'procfs pressure file not present'}
        except PermissionError:
            pressure[name] = {'available': False, 'missing': 'procfs pressure file not readable'}
        except Exception as exc:
            pressure[name] = {'available': False, 'error': type(exc).__name__}
    sample['pressure'] = pressure
    sample['collection_ms'] = (time.monotonic_ns() - started_ns) / 1e6
    sample['required_components_available'] = all(sample['availability'].get(k, False) for k in REQUIRED)
    return sample


def preflight(proc_root=PROC, reader=None, reads=5, max_read_ms=MAX_PREFLIGHT_READ_MS):
    """Probe five reads. Disable telemetry if a required source is missing or any read is slow."""
    reader = reader or collect_sample
    results = []
    for _ in range(reads):
        try:
            row = reader(proc_root)
            elapsed = float(row.get('collection_ms', 0.0))
            results.append({'collection_ms': elapsed,
                            'required_components_available': bool(row.get('required_components_available')),
                            'availability': row.get('availability', {}),
                            'missing': row.get('missing', {}),
                            'errors': row.get('errors', {}),
                            'pressure': {name: row.get('pressure', {}).get(name, {}).get('available', False)
                                         for name in ('cpu', 'io', 'memory')}})
        except Exception as exc:
            results.append({'collection_ms': None, 'required_components_available': False,
                            'error': type(exc).__name__})
    slow = [i for i, row in enumerate(results) if row.get('collection_ms') is None or row['collection_ms'] > max_read_ms]
    unavailable = [i for i, row in enumerate(results) if not row.get('required_components_available')]
    enabled = not slow and not unavailable and len(results) == reads
    return {'enabled': enabled, 'interval_seconds': INTERVAL_SECONDS,
            'preflight_reads': reads, 'maximum_read_ms': max_read_ms,
            'reads_over_cost_gate': slow, 'reads_missing_required_sources': unavailable,
            'reads': results,
            'pressure_availability': {name: all(row.get('pressure', {}).get(name, False) for row in results)
                                      for name in ('cpu', 'io', 'memory')},
            'reason': 'ready' if enabled else 'sampler disabled: procfs source missing, probe failed, or one read exceeded 50 ms'}


def _on_stop(_signum, _frame):
    _STOP.set()


def sample_loop(output, proc_root=PROC, interval=INTERVAL_SECONDS):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    _STOP.clear()
    try:
        import signal
        signal.signal(signal.SIGTERM, _on_stop)
        signal.signal(signal.SIGINT, _on_stop)
    except ValueError:
        pass
    next_at = time.monotonic()
    sample_index = 0
    with path.open('a', buffering=1) as stream:
        while not _STOP.is_set():
            row = collect_sample(proc_root)
            row['sample_index'] = sample_index
            row['schedule_lag_ms'] = max(0.0, (time.monotonic() - next_at) * 1000.0)
            stream.write(json.dumps(row, separators=(',', ':'), sort_keys=True) + '\n')
            stream.flush()
            sample_index += 1
            next_at += interval
            wait_for = max(0.0, next_at - time.monotonic())
            _STOP.wait(wait_for)
    return sample_index


def start_sampler(output, proc_root=PROC, interval=INTERVAL_SECONDS, stderr_path=None):
    err = open(stderr_path, 'ab') if stderr_path else subprocess.DEVNULL
    try:
        return subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--sample',
                                 '--output', str(output), '--proc-root', str(proc_root),
                                 '--interval', str(interval)],
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=err, close_fds=True)
    finally:
        if stderr_path and not err.closed:
            err.close()



def wait_for_first_sample(process, output, timeout_seconds=1.0):
    path = Path(output)
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return {'available': False, 'reason': 'sampler exited before first sample',
                    'returncode': process.returncode}
        try:
            if path.is_file() and path.stat().st_size > 0:
                return {'available': True, 'first_sample_seen': True}
        except OSError:
            pass
        time.sleep(0.01)
    return {'available': False, 'reason': 'first sample not observed before bounded startup timeout'}


def validate_sample_file(path, max_bytes=2_000_000, optional=True):
    """Validate compact per-arm JSONL and enforce the collection size ceiling."""
    path = Path(path)
    if not path.is_file():
        if optional:
            return {'present': False, 'sample_count': 0, 'bytes': 0}
        raise FileNotFoundError(path)
    size = path.stat().st_size
    if size >= max_bytes:
        raise ValueError(f'per-arm telemetry sample exceeds {max_bytes}-byte limit: {size}')
    count = 0
    last_index = -1
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or not isinstance(row.get('availability'), dict):
            raise ValueError('telemetry row is not a structured sample')
        if not isinstance(row.get('timestamp_utc'), str) or not isinstance(row.get('timestamp_monotonic_seconds'), (int, float)):
            raise ValueError('telemetry sample timestamp is missing')
        if not isinstance(row.get('collection_ms'), (int, float)) or row['collection_ms'] < 0:
            raise ValueError('telemetry collection duration is missing or invalid')
        if 'sample_index' in row:
            if row['sample_index'] <= last_index:
                raise ValueError('telemetry sample indexes are not increasing')
            last_index = row['sample_index']
        count += 1
    return {'present': True, 'sample_count': count, 'bytes': size, 'maximum_bytes': max_bytes}


def stop_sampler(process, timeout_seconds=5):
    if process is None:
        return {'stopped': True, 'returncode': None, 'process_was_started': False}
    if process.poll() is None:
        process.terminate()
        try:
            code = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            code = process.wait(timeout=timeout_seconds)
            return {'stopped': True, 'returncode': code, 'killed_after_timeout': True}
    else:
        code = process.returncode
    return {'stopped': True, 'returncode': code, 'process_was_started': True,
            'sampler_exit_success': code == 0}


def run_with_sampler(process, command, **kwargs):
    """Run one solver child and stop/reap the sampler even if launch/wait raises."""
    try:
        result = subprocess.run(command, **kwargs)
    finally:
        stopped = stop_sampler(process) if process is not None else {'process_was_started': False}
    return result, stopped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--sample', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--proc-root', default=str(PROC))
    parser.add_argument('--interval', type=float, default=INTERVAL_SECONDS)
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(args.proc_root), sort_keys=True))
    elif args.sample:
        if not args.output or args.interval <= 0:
            raise SystemExit('--sample requires --output and a positive --interval')
        sample_loop(args.output, args.proc_root, args.interval)
    else:
        parser.error('choose --preflight or --sample')


if __name__ == '__main__':
    main()
