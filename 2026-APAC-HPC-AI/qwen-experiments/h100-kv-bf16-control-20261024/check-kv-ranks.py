#!/usr/bin/env python3
"""Require exact per-rank KV allocation records using the configured cache dtype."""
import argparse
import re
from collections import Counter
from pathlib import Path

DTYPES = {'auto': 'torch.bfloat16', 'fp8_e4m3': 'torch.float8_e4m3fn'}
PREFILL = re.compile(
    r'^\[[^\]\r\n]+ TP(?P<tp>[0-9]+)\] KV Cache is allocated\. dtype: (?P<dtype>[^, ]+), '
    r'#tokens: (?P<tokens>[1-9][0-9]*), K size: (?P<ksize>[0-9]+(?:\.[0-9]+)?) GB, '
    r'V size: (?P<vsize>[0-9]+(?:\.[0-9]+)?) GB\s*$'
)
DECODE = re.compile(
    r'^\[[^\]\r\n]+ TP(?P<tp>[0-9]+) EP(?P<ep>[0-9]+)\] KV Cache is allocated\. dtype: (?P<dtype>[^, ]+), '
    r'#tokens: (?P<tokens>[1-9][0-9]*), K size: (?P<ksize>[0-9]+(?:\.[0-9]+)?) GB, '
    r'V size: (?P<vsize>[0-9]+(?:\.[0-9]+)?) GB\s*$'
)


def check(path: Path, worker: str, expected: str) -> list[int]:
    if expected not in DTYPES:
        raise ValueError(f'unsupported expected KV dtype {expected!r}')
    if worker.startswith('prefill-'):
        expected_ranks = set(range(4))
        pattern = PREFILL
    elif worker == 'decode-0':
        expected_ranks = set(range(8))
        pattern = DECODE
    else:
        raise ValueError(f'unknown target worker name {worker!r}')

    rank_counts = Counter()
    for number, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
        if 'KV Cache is allocated.' not in line:
            continue
        match = pattern.fullmatch(line)
        if match is None:
            raise ValueError(f'{worker}: malformed/unexpected KV allocation line {number}: {line}')
        rank = int(match['tp'])
        if rank not in expected_ranks:
            raise ValueError(f'{worker}: unexpected TP rank {rank} on line {number}')
        if match['dtype'] != DTYPES[expected]:
            raise ValueError(f'{worker}: TP{rank} dtype {match["dtype"]!r}, expected {DTYPES[expected]!r}')
        if worker == 'decode-0' and int(match['ep']) != rank:
            raise ValueError(f'{worker}: TP{rank} EP{match["ep"]} mapping mismatch')
        if float(match['ksize']) <= 0 or float(match['vsize']) <= 0:
            raise ValueError(f'{worker}: TP{rank} has nonpositive KV allocation size')
        rank_counts[rank] += 1

    duplicates = sorted(rank for rank, count in rank_counts.items() if count != 1)
    found = set(rank_counts)
    missing = sorted(expected_ranks - found)
    if duplicates or missing or found != expected_ranks:
        raise ValueError(f'{worker}: {expected} KV rank evidence incomplete/duplicated; found={sorted(found)} missing={missing} duplicate={duplicates}')
    return sorted(found)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('worker', choices=('prefill-0', 'prefill-1', 'decode-0'))
    parser.add_argument('--expected', choices=tuple(DTYPES), required=True)
    args = parser.parse_args()
    try:
        ranks = check(args.log, args.worker, args.expected)
    except Exception as error:
        raise SystemExit(f'FATAL: {error}')
    print(f'KV_RANKS_CONFIRMED worker={args.worker} dtype={DTYPES[args.expected]} ranks={",".join(map(str, ranks))}')


if __name__ == '__main__':
    main()
