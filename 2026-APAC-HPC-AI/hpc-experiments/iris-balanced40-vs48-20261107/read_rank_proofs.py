#!/usr/bin/env python3
"""Validate one-file-per-rank proofs without parsing interleaved MPI stdout."""
import argparse
import json
from pathlib import Path

EXPECTED_KEYS = {'rank', 'world_size', 'hostname', 'affinity_cpu_ids'}


def validate_proof_dir(proof_dir, expected_ranks):
    proof_dir = Path(proof_dir)
    if proof_dir.is_symlink() or not proof_dir.is_dir():
        raise ValueError('proof directory missing or symlinked')
    expected_names = {'rank-%04d.json' % rank for rank in range(expected_ranks)}
    entries = list(proof_dir.iterdir())
    names = {entry.name for entry in entries}
    if names != expected_names or any(not entry.is_file() or entry.is_symlink() for entry in entries):
        raise ValueError('proof file set mismatch: expected %d exact rank files, got %d entries' %
                         (expected_ranks, len(entries)))
    records = []
    seen_ranks = set()
    hosts = set()
    masks = []
    for rank in range(expected_ranks):
        path = proof_dir / ('rank-%04d.json' % rank)
        try:
            record = json.loads(path.read_text())
        except Exception as exc:
            raise ValueError('invalid JSON in %s: %s' % (path.name, exc))
        if not isinstance(record, dict) or set(record) != EXPECTED_KEYS:
            raise ValueError('schema mismatch in ' + path.name)
        if type(record['rank']) is not int or record['rank'] < 0:
            raise ValueError('invalid rank in ' + path.name)
        if record['rank'] in seen_ranks:
            raise ValueError('duplicate rank identity: %d' % record['rank'])
        seen_ranks.add(record['rank'])
        if type(record['world_size']) is not int or record['world_size'] != expected_ranks:
            raise ValueError('world size mismatch in ' + path.name)
        if record['rank'] != rank:
            raise ValueError('filename/rank mismatch in ' + path.name)
        if not isinstance(record['hostname'], str) or not record['hostname']:
            raise ValueError('invalid hostname in ' + path.name)
        hosts.add(record['hostname'])
        cpus = record['affinity_cpu_ids']
        if not isinstance(cpus, list) or not cpus or any(type(cpu) is not int or cpu < 0 for cpu in cpus):
            raise ValueError('invalid or empty affinity mask in ' + path.name)
        if cpus != sorted(set(cpus)):
            raise ValueError('affinity mask must be sorted and unique in ' + path.name)
        masks.append(set(cpus))
        records.append(record)
    if seen_ranks != set(range(expected_ranks)):
        raise ValueError('rank identities are incomplete')
    if len(hosts) != 1:
        raise ValueError('rank proofs report multiple hostnames')
    for index, mask in enumerate(masks):
        if any(mask.intersection(other) for other in masks[index + 1:]):
            raise ValueError('rank affinity masks overlap')
    return {
        'passed': True,
        'rank_count': expected_ranks,
        'rank_ids': list(range(expected_ranks)),
        'hostnames': sorted(hosts),
        'affinity_masks_nonempty_unique_nonoverlap': True,
        'proof_files': ['rank-%04d.json' % rank for rank in range(expected_ranks)],
        'proofs': records,
        'scope': 'Launcher process OS affinity before MPI_Init; does not establish MPI-initialized application or solver-thread affinity.',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--proof-dir', required=True, type=Path)
    parser.add_argument('--expected-ranks', type=int, required=True, choices=(48, 56))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = validate_proof_dir(args.proof_dir, args.expected_ranks)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'proofs'}, indent=2))


if __name__ == '__main__':
    main()
