"""Compare the launcher's displayed MPI-world-rank host mapping with a fresh probe."""
import argparse
import json
import re
from pathlib import Path

RANKS = 512
DISPLAY = re.compile(r'\brank\s+(\d+)\s+is on\s+(\S+); originally was on\s+(\S+)')
MAP_PREFIX = 'MAP_JSON\t'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', required=True)
    parser.add_argument('--probe', required=True, help='MAP_JSON stdout from immediate arm probe')
    parser.add_argument('--output')
    args = parser.parse_args()
    text = Path(args.log).read_text(errors='replace')
    observed = {}
    for rank_text, host, original in DISPLAY.findall(text):
        rank = int(rank_text)
        assert rank not in observed, ('duplicate MPI display rank', rank)
        observed[rank] = (host.split('.', 1)[0], original.split('.', 1)[0])
    assert sorted(observed) == list(range(RANKS)), ('MPI rank display is incomplete', len(observed))
    expected = {}
    for line in Path(args.probe).read_text(errors='replace').splitlines():
        if MAP_PREFIX not in line:
            continue
        row = json.loads(line.split(MAP_PREFIX, 1)[1])
        rank = int(row['rank'])
        assert rank not in expected
        expected[rank] = row['processor_name'].split('.', 1)[0]
    assert sorted(expected) == list(range(RANKS)), ('probe MAP_JSON rank set', len(expected))
    mismatches = [{'rank': rank, 'expected_host': expected[rank],
                   'displayed_host': observed[rank][0]}
                  for rank in range(RANKS) if expected[rank] != observed[rank][0]]
    assert not mismatches, mismatches[:20]
    report = {'passed': True, 'rank_records': RANKS, 'world_rank_host_mismatches': 0}
    rendered = json.dumps(report, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(rendered)
    print(rendered, end='')


if __name__ == '__main__':
    main()
