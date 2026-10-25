"""Report paired per-Time force-coefficient differences without an invented tolerance."""
import argparse
import json
import math
import statistics
from pathlib import Path

ARMS = ('A1', 'B1', 'B2', 'A2')


def read_force(path):
    header = None
    rows = []
    for line in Path(path).read_text(errors='replace').splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            names = stripped.lstrip('#').split()
            if names and names[0] == 'Time' and len(names) > 1:
                header = names
            continue
        values = [float(x) for x in stripped.split()]
        assert all(math.isfinite(x) for x in values), (path, line)
        rows.append(values)
    assert header is not None and len(rows) == 150, (path, len(rows))
    assert all(len(row) == len(header) for row in rows)
    assert [int(row[0]) for row in rows] == list(range(1, 151))
    return header, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arms-root', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root = Path(args.arms_root)
    data = {}
    for arm in ARMS:
        data[arm] = read_force(root / arm / 'case/postProcessing/forceCoeffsAll/0/coefficient.dat')
    headers = [data[arm][0] for arm in ARMS]
    assert all(header == headers[0] for header in headers)
    pairs = []
    for block, control, candidate in (('AB', 'A1', 'B1'), ('BA', 'A2', 'B2')):
        columns = {}
        for index, name in enumerate(headers[0][1:], 1):
            deltas = [data[candidate][1][t][index] - data[control][1][t][index]
                      for t in range(150)]
            max_abs = max(abs(x) for x in deltas)
            max_at = deltas.index(max_abs) + 1
            columns[name] = {'mean_candidate_minus_identity': statistics.mean(deltas),
                             'max_absolute_difference': max_abs,
                             'max_absolute_difference_time': max_at,
                             'per_time_candidate_minus_identity': deltas}
        pairs.append({'block_order': block, 'control_arm': control,
                      'candidate_arm': candidate, 'columns': columns})
    report = {'passed': True, 'row_count_per_arm': 150, 'columns': headers[0],
              'comparison': 'Descriptive per-time output differences only; no acceptance tolerance or equivalence test is set here.',
              'paired_differences': pairs}
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'paired_differences'}, indent=2))


if __name__ == '__main__':
    main()
