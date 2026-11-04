#!/usr/bin/env python3
"""Record actual per-rank memory policy and affinity, then exec simpleFoam in place."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from qualification_utils import parse_numactl_show


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ('default', 'interleave-all'):
        raise SystemExit('usage: rank_exec.py default|interleave-all PROOF_DIR')
    expected, proof_dir = sys.argv[1], Path(sys.argv[2])
    rank_text = os.environ.get('OMPI_COMM_WORLD_RANK')
    if rank_text is None:
        raise RuntimeError('OMPI_COMM_WORLD_RANK is unavailable')
    rank = int(rank_text)
    shown = subprocess.run(['numactl', '--show'], check=True, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
    policy = parse_numactl_show(shown)
    actual = 'interleave-all' if policy['policy'] == 'interleave' and set(policy['interleave_nodes']) == {0, 1} else policy['policy']
    if actual != expected:
        raise RuntimeError(f'rank {rank}: expected {expected}, observed {policy}')
    affinity = sorted(os.sched_getaffinity(0))
    if not affinity:
        raise RuntimeError(f'rank {rank}: empty CPU affinity')
    proof_dir.mkdir(parents=True, exist_ok=True)
    record = {'rank': rank, 'pid': os.getpid(), 'expected_policy': expected,
              'observed_policy': policy, 'affinity_cpu_ids': affinity,
              'command_before_exec': ['simpleFoam', '-parallel']}
    target = proof_dir / f'rank-{rank:02d}.json'
    fd, temporary = tempfile.mkstemp(prefix=f'.{target.name}.', dir=proof_dir)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(record, stream, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    os.execvp('simpleFoam', ['simpleFoam', '-parallel'])


if __name__ == '__main__':
    main()
