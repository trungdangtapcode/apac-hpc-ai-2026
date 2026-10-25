"""Require repeated identity launches to preserve the same world-rank slot map."""
import argparse
import json
from pathlib import Path

PREFIX = 'MAP_JSON\t'


def read(path):
    rows = {}
    for line in Path(path).read_text(errors='replace').splitlines():
        if PREFIX not in line:
            continue
        row = json.loads(line.split(PREFIX, 1)[1])
        rank = int(row['rank'])
        assert rank not in rows
        rows[rank] = (row['processor_name'], row['affinity_cpus'],
                      row['physical_package_id'], row['physical_core_id'], row['numa_node'])
    assert sorted(rows) == list(range(512)), (path, len(rows))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('reference')
    parser.add_argument('observed')
    parser.add_argument('--output')
    args = parser.parse_args()
    left, right = read(args.reference), read(args.observed)
    diffs = [rank for rank in range(512) if left[rank] != right[rank]]
    assert not diffs, ('rank slots changed since qualification probe', diffs[:20])
    report = {'passed': True, 'rank_count': 512, 'different_world_rank_slots': 0}
    text = json.dumps(report, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
