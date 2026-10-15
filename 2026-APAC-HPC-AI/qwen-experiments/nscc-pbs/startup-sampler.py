"""Read /proc counters for an explicit own process tree inside a PBS allocation.

No GPU access, command lines, environments, model files or unrelated processes.
Counter deltas exclude processes that exit between samples; RSS includes shared
pages, and read_bytes is not a measurement of total mmap/storage traffic.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import time


def identity(pid):
    base = Path('/proc') / str(pid)
    if base.stat().st_uid != os.getuid():
        raise PermissionError('Process belongs to another user')
    raw = (base / 'stat').read_text()
    # comm can contain whitespace and parentheses; fields after the final ')'
    # begin at stat field 3 (state).
    fields = raw[raw.rfind(')') + 2:].split()
    return base, fields


def descendants(root_pid):
    pending = [root_pid]
    seen = set()
    while pending:
        pid = pending.pop()
        if pid in seen or pid == os.getpid():
            continue
        seen.add(pid)
        try:
            base, _ = identity(pid)
            yield pid
            # Children may have been created by any thread in the process.
            for task in (base / 'task').iterdir():
                try:
                    pending.extend(int(p) for p in (task / 'children').read_text().split())
                except (OSError, ValueError):
                    pass
        except (OSError, ValueError):
            continue


def process_sample(pid):
    base, fields = identity(pid)
    row = dict(pid=pid, start_ticks=int(fields[19]), state=fields[0],
               minor_faults=int(fields[7]), major_faults=int(fields[9]),
               cpu_ticks=int(fields[11]) + int(fields[12]),
               threads=int(fields[17]), rss_bytes=int(fields[21]) * os.sysconf('SC_PAGE_SIZE'))
    try:
        io = dict(line.split(':', 1) for line in (base / 'io').read_text().splitlines())
        for name in ('read_bytes', 'write_bytes', 'rchar', 'wchar'):
            row[name] = int(io[name])
    except OSError as exc:
        row['io_unavailable'] = type(exc).__name__
    try:
        status = dict(line.split(':', 1) for line in (base / 'status').read_text().splitlines())
        for name in ('Cpus_allowed_list', 'Mems_allowed_list'):
            row[name] = status[name].strip()
        # Aggregate node placement without retaining mapped file names/paths.
        nodes = {}
        for line in (base / 'numa_maps').read_text().splitlines():
            for word in line.split():
                key, separator, value = word.partition('=')
                if separator and key.startswith('N') and key[1:].isdigit() and value.isdigit():
                    nodes[key] = nodes.get(key, 0) + int(value)
        row['numa_pages'] = nodes
    except OSError as exc:
        row['placement_unavailable'] = type(exc).__name__
    # Reject a PID that was recycled while its files were being read.
    if int(identity(pid)[1][19]) != row['start_ticks']:
        raise ProcessLookupError('PID changed during snapshot')
    return row


COUNTERS = ('minor_faults', 'major_faults', 'cpu_ticks', 'read_bytes', 'write_bytes', 'rchar', 'wchar')


def snapshot(root_pid, previous):
    rows, errors = [], []
    for pid in descendants(root_pid):
        try:
            row = process_sample(pid)
            old = previous.get((pid, row['start_ticks']))
            row['delta'] = ({key: row[key] - old[key] for key in COUNTERS
                             if key in row and key in old and row[key] >= old[key]}
                            if old else None)
            rows.append(row)
        except (OSError, ValueError, IndexError) as exc:
            errors.append(dict(pid=pid, error=type(exc).__name__))
    return dict(checked_utc=datetime.now(timezone.utc).isoformat(),
                monotonic_s=time.monotonic(), processes=rows, unavailable=errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root-pid', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--interval', type=float, default=15)
    parser.add_argument('--duration', type=float, default=1200)
    args = parser.parse_args()
    if not os.environ.get('PBS_JOBID'):
        parser.error('Run only inside an existing PBS compute allocation')
    if args.root_pid <= 1 or not 5 <= args.interval <= 60 or not 1 <= args.duration <= 1200:
        parser.error('Require root PID >1, interval 5–60s, duration 1–1200s')
    _, first = identity(args.root_pid)
    root_start = first[19]
    deadline, previous = time.monotonic() + args.duration, {}
    # Refuse to overwrite any prior evidence.
    with args.out.open('x') as output:
        output.write(json.dumps(dict(kind='metadata', job=os.environ['PBS_JOBID'],
                                     hostname=socket.gethostname(), root_pid=args.root_pid,
                                     root_start_ticks=int(root_start), clock_ticks=os.sysconf('SC_CLK_TCK'),
                                     interval_s=args.interval, max_duration_s=args.duration)) + '\n')
        while time.monotonic() < deadline:
            try:
                if identity(args.root_pid)[1][19] != root_start:
                    break
            except OSError:
                break
            row = snapshot(args.root_pid, previous)
            output.write(json.dumps(row, sort_keys=True) + '\n')
            output.flush()
            previous = {(p['pid'], p['start_ticks']): p for p in row['processes']}
            time.sleep(min(args.interval, max(0, deadline - time.monotonic())))


if __name__ == '__main__':
    main()
