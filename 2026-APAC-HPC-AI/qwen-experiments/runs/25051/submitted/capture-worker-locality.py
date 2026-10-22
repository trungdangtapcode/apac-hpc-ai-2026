"""Bounded, read-only capture of one owned worker tree before benchmark warmup.

Run inside the worker's existing container. Never read process environments or
command lines. GPU process rows are retained only when their PID matches an
owned descendant, allowing for the namespace PID list in /proc/PID/status.
"""
import argparse
import csv
import datetime
import io
import json
import os
from pathlib import Path
import subprocess
import time


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def expand(value):
    result = set()
    for part in value.split(','):
        if not part:
            continue
        bounds = [int(x) for x in part.split('-')]
        result.update(range(bounds[0], bounds[-1] + 1))
    return result


def status(pid, root=Path('/proc')):
    path = root / str(pid)
    if path.stat().st_uid != os.getuid():
        raise PermissionError('Process belongs to another user')
    data = dict(line.split(':', 1) for line in (path / 'status').read_text().splitlines() if ':' in line)
    raw = (path / 'stat').read_text().rsplit(')', 1)[1].split()
    return dict(pid=int(pid), parent_pid=int(raw[1]), name=data['Name'].strip(),
                namespace_pids=[int(x) for x in data.get('NSpid', str(pid)).split()],
                allowed_cpus=sorted(expand(data['Cpus_allowed_list'].strip())),
                start_ticks=int(raw[19]), cpu_ticks=int(raw[11]) + int(raw[12]))


def owned_tree(root_pid, proc=Path('/proc'), excluded=()):
    records = {}
    errors = 0
    for path in proc.iterdir():
        if not path.name.isdigit():
            continue
        try:
            if path.stat().st_uid != os.getuid():
                continue
            records[int(path.name)] = status(path.name, proc)
        except (OSError, ValueError, KeyError, IndexError):
            errors += 1
    selected = {root_pid}
    while True:
        additions = {pid for pid, row in records.items()
                     if row['parent_pid'] in selected and pid not in selected and pid not in excluded}
        if not additions:
            break
        selected.update(additions)
    rows = [records[pid] for pid in sorted(selected) if pid in records and pid not in excluded]
    if len(rows) > 256:
        raise RuntimeError('Owned process capture exceeds the bounded 256-process limit')
    return rows, errors


def match_gpu_rows(processes, gpu_rows):
    matched, ambiguous = [], 0
    for row in gpu_rows:
        pid, uuid, memory = (x.strip() for x in row)
        candidates = [p['pid'] for p in processes if int(pid) in {p['pid'], *p['namespace_pids']}]
        if len(candidates) == 1:
            matched.append(dict(process_pid=candidates[0], nvml_pid=int(pid), gpu_uuid=uuid,
                                used_gpu_memory_mib=memory))
        elif len(candidates) > 1:
            ambiguous += 1
    return matched, ambiguous


def smi(fields, query):
    cmd = ['nvidia-smi', '--query-' + query + '=' + fields, '--format=csv,noheader,nounits']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
    if result.returncode:
        raise RuntimeError('nvidia-smi failed, returncode=' + str(result.returncode))
    return list(csv.reader(io.StringIO(result.stdout)))


def snapshot(root_pid):
    processes, races = owned_tree(root_pid, excluded={os.getpid()})
    devices = []
    for ordinal, uuid, pci in smi('index,uuid,pci.bus_id', 'gpu'):
        pci = pci.strip().lower()
        pci = pci[-12:]
        base = Path('/sys/bus/pci/devices') / pci
        device = dict(nvml_visible_index=ordinal.strip(), uuid=uuid.strip(), pci=pci)
        for key in ('numa_node', 'local_cpulist'):
            try:
                device[key] = (base / key).read_text().strip()
            except OSError:
                device[key] = None
        devices.append(device)
    gpu_rows, ambiguous = match_gpu_rows(processes, smi('pid,gpu_uuid,used_gpu_memory', 'compute-apps'))
    thread_count = 0
    for process in processes:
        mask_groups = {}
        for thread in sorted((Path('/proc') / str(process['pid']) / 'task').iterdir()):
            if thread_count >= 4096:
                break
            try:
                text = (thread / 'status').read_text()
                mask = next(line.split(':', 1)[1].strip() for line in text.splitlines()
                            if line.startswith('Cpus_allowed_list:'))
                mask_groups[mask] = mask_groups.get(mask, 0) + 1
                thread_count += 1
            except (OSError, StopIteration):
                races += 1
        process['thread_mask_counts'] = mask_groups
        process['gpu_locality'] = []
        for gpu in gpu_rows:
            if gpu['process_pid'] != process['pid']:
                continue
            device = next((d for d in devices if d['uuid'] == gpu['gpu_uuid']), None)
            local = device and device.get('local_cpulist')
            process['gpu_locality'].append(dict(gpu_uuid=gpu['gpu_uuid'],
                gpu_numa_node=device.get('numa_node') if device else None,
                allowed_local_cpu_intersection=sorted(set(process['allowed_cpus']) & expand(local)) if local else None))
    return dict(captured_utc=now(), processes=processes, visible_devices=devices,
                matched_gpu_processes=gpu_rows, ambiguous_gpu_pid_matches=ambiguous,
                thread_count=thread_count, thread_capture_truncated=thread_count >= 4096,
                proc_races=races, scored_cpu_demand_collected=False,
                memory_placement_collected=False,
                ordinal_warning='NVML visible index and CUDA ordinal are not assumed interchangeable.')


def save(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=int)
    parser.add_argument('--role', required=True)
    parser.add_argument('--artifact', required=True, type=Path)
    parser.add_argument('--timeout', type=float, default=700)
    args = parser.parse_args()
    folder = args.artifact / 'worker-locality'
    folder.mkdir(exist_ok=True)
    result = dict(role=args.role, hostname=os.uname().nodename, root_pid=args.root,
                  observer_pid=os.getpid(), started_utc=now(), state='WAITING_FOR_CAPTURE',
                  reads_process_environments=False, reads_command_lines=False)
    try:
        launch = status(args.root)
        result['launch'] = launch
        save(folder / (args.role + '.launch.json'), result)
        deadline = time.monotonic() + args.timeout
        while not (folder / 'request.json').exists():
            if time.monotonic() >= deadline:
                raise TimeoutError('No pre-score capture request before deadline')
            if status(args.root)['start_ticks'] != launch['start_ticks']:
                raise RuntimeError('Worker root PID changed generation')
            time.sleep(1)
        capture_started = time.monotonic()
        result['snapshot'] = snapshot(args.root)
        result['snapshot_duration_s'] = time.monotonic() - capture_started
        result['state'] = 'CAPTURE_COMPLETE'
    except Exception as error:
        result.update(state='CAPTURE_INCOMPLETE', error_type=type(error).__name__, error=str(error))
    result['finished_utc'] = now()
    save(folder / (args.role + '.ready.json'), result)


if __name__ == '__main__':
    main()
