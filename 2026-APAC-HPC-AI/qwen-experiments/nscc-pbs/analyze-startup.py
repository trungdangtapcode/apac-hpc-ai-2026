"""Offline analysis of one startup-sampler JSONL; never accesses /proc or GPUs."""
import argparse
import hashlib
import json
import math
from pathlib import Path

COUNTERS = ('cpu_ticks', 'minor_faults', 'major_faults', 'read_bytes',
            'write_bytes', 'rchar', 'wchar')


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def analyze(raw):
    lines = raw.splitlines(keepends=True)
    incomplete_tail = bool(lines and not lines[-1].endswith(b'\n'))
    if incomplete_tail:
        lines.pop()  # A live writer may still be appending this record.
    records = [json.loads(line) for line in lines]
    if not records or records[0].get('kind') != 'metadata':
        raise ValueError('First complete record must be sampler metadata')
    metadata = records[0]
    hz = metadata.get('clock_ticks')
    interval = metadata.get('interval_s')
    if not finite_number(hz) or hz <= 0 or not finite_number(interval) or interval <= 0:
        raise ValueError('Require positive clock_ticks and interval_s')
    previous, last_time, intervals, snapshots = {}, None, [], 0
    for record in records[1:]:
        current_time = record.get('monotonic_s')
        if not finite_number(current_time) or (last_time is not None and current_time <= last_time):
            raise ValueError('Sample monotonic times must be finite and strictly increasing')
        current = {}
        for process in record['processes']:
            key = (process['pid'], process['start_ticks'])
            if key in current:
                raise ValueError('Duplicate process identity in sample')
            current[key] = process
        if last_time is not None:
            elapsed = current_time - last_time
            common = current.keys() & previous.keys()
            totals = dict.fromkeys(COUNTERS, 0)
            coverage = dict.fromkeys(COUNTERS, 0)
            resets = []
            for key in sorted(common):
                for counter in COUNTERS:
                    old, new = previous[key].get(counter), current[key].get(counter)
                    if old is None or new is None:
                        continue
                    if not finite_number(old) or not finite_number(new) or min(old, new) < 0:
                        raise ValueError('Counters must be finite nonnegative numbers')
                    if new < old:
                        resets.append({'pid': key[0], 'start_ticks': key[1], 'counter': counter})
                        continue
                    totals[counter] += new - old
                    coverage[counter] += 1
            # Zero is meaningful only when at least one matching identity had
            # both counters. Missing coverage stays null rather than becoming 0.
            totals = {key: value if coverage[key] else None for key, value in totals.items()}
            intervals.append({
                'end_utc': record['checked_utc'], 'elapsed_s': elapsed,
                'sample_gap': elapsed > interval * 1.5,
                'matched_processes': len(common),
                'new_identities': len(current.keys() - previous.keys()),
                'disappeared_identities': len(previous.keys() - current.keys()),
                'counter_coverage_processes': coverage, 'counter_resets': resets,
                'observed_counter_deltas': totals,
                'observed_cpu_cores': totals['cpu_ticks'] / hz / elapsed
                    if totals['cpu_ticks'] is not None else None,
                'observed_read_bytes_s': totals['read_bytes'] / elapsed
                    if totals['read_bytes'] is not None else None,
                'process_read_errors': len(record.get('unavailable', [])),
            })
        previous, last_time = current, current_time
        snapshots += 1
    return {
        'source_sha256': hashlib.sha256(raw).hexdigest(), 'metadata': metadata,
        'complete_samples': snapshots, 'ignored_incomplete_tail': incomplete_tail,
        'intervals': intervals, 'gpu_executed_by_analyzer': False,
        'interpretation': 'Observed deltas cover only identities present at both adjacent samples. '
            'New/exited processes, read errors, counter resets and sample gaps limit coverage. '
            'CPU cores are sampled CPU-seconds/wall-second, not utilization of allocated CPUs. '
            'read_bytes is not total mmap or network filesystem traffic. '
            'No memory totals or causal bottleneck classification are inferred.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.input.read_bytes())
    with args.out.open('x') as output:
        json.dump(result, output, indent=2, allow_nan=False)
        output.write('\n')
    print(json.dumps({'output': str(args.out), 'samples': result['complete_samples'],
                      'intervals': len(result['intervals']),
                      'ignored_incomplete_tail': result['ignored_incomplete_tail']}))


if __name__ == '__main__':
    main()
