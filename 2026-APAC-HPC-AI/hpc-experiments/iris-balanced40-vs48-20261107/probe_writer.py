#!/usr/bin/env python3
"""Write one pre-MPI_Init launcher-rank affinity proof to an exclusive file."""
import argparse
import json
import os
from pathlib import Path
import socket


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--proof-dir', required=True, type=Path)
    args = parser.parse_args()
    rank = int(os.environ['OMPI_COMM_WORLD_RANK'])
    world_size = int(os.environ['OMPI_COMM_WORLD_SIZE'])
    proof_dir = args.proof_dir
    if proof_dir.is_symlink() or not proof_dir.is_dir():
        raise RuntimeError('proof directory must exist and must not be a symlink')
    proof = {
        'rank': rank,
        'world_size': world_size,
        'hostname': socket.gethostname(),
        'affinity_cpu_ids': sorted(os.sched_getaffinity(0)),
    }
    path = proof_dir / ('rank-%04d.json' % rank)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(json.dumps(proof, sort_keys=True, separators=(',', ':')) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


if __name__ == '__main__':
    main()
