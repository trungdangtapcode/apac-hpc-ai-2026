#!/usr/bin/env python3
"""Offline syntax, source-integrity, and synthetic proof protocol tests."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / 'payload-sha256.json').read_text())['files']
sys.path.insert(0, str(ROOT))
from read_rank_proofs import validate_proof_dir


def check(condition, label):
    print(('PASS ' if condition else 'FAIL ') + label)
    if not condition:
        raise SystemExit(1)


def write_set(directory, count, world_size=None, mutate=None):
    directory.mkdir()
    world_size = count if world_size is None else world_size
    for rank in range(count):
        record = {'rank': rank, 'world_size': world_size, 'hostname': 'iris-synthetic',
                  'affinity_cpu_ids': [rank]}
        if mutate:
            mutate(rank, record)
        (directory / ('rank-%04d.json' % rank)).write_text(json.dumps(record) + '\n')

check(all((ROOT / name).is_file() and hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
          for name, digest in MANIFEST.items()), 'all frozen operational source hashes match')
for name in ('probe_writer.py', 'read_rank_proofs.py', 'run_probes.py'):
    result = subprocess.run([sys.executable, '-m', 'py_compile', str(ROOT / name)], capture_output=True)
    check(result.returncode == 0, 'Python syntax ' + name)
result = subprocess.run(['bash', '-n', str(ROOT / 'job.sbatch')], capture_output=True)
check(result.returncode == 0, 'Slurm shell syntax')

with tempfile.TemporaryDirectory(prefix='iris-rank-proof-check-') as temp:
    base = Path(temp)
    for count in (48, 56):
        directory = base / ('valid%d' % count)
        write_set(directory, count)
        check(validate_proof_dir(directory, count)['passed'], 'valid %d-rank proof set' % count)
    for count, label in ((47, 'reject 47 ranks when 48 expected'), (49, 'reject 49 ranks when 48 expected')):
        directory = base / label.replace(' ', '-')
        write_set(directory, count)
        try:
            validate_proof_dir(directory, 48)
            accepted = True
        except ValueError:
            accepted = False
        check(not accepted, label)
    cases = []
    d = base / 'missing'; write_set(d, 48); (d / 'rank-0047.json').unlink(); cases.append((d, 'reject missing rank file'))
    d = base / 'corrupt'; write_set(d, 48); (d / 'rank-0021.json').write_text('{bad json'); cases.append((d, 'reject corrupt JSON'))
    d = base / 'world'; write_set(d, 48, world_size=47); cases.append((d, 'reject world-size mismatch'))
    def duplicate(rank, record):
        if rank == 1: record['rank'] = 0
    d = base / 'duplicate'; write_set(d, 48, mutate=duplicate); cases.append((d, 'reject duplicate rank identity'))
    def overlap(rank, record):
        if rank == 1: record['affinity_cpu_ids'] = [0]
    d = base / 'overlap'; write_set(d, 48, mutate=overlap); cases.append((d, 'reject overlapping affinity masks'))
    for directory, label in cases:
        try:
            validate_proof_dir(directory, 48)
            accepted = True
        except ValueError:
            accepted = False
        check(not accepted, label)
