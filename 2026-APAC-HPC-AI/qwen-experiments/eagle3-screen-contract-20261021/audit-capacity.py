"""Fail closed unless a future screen logs both its declared and final scheduler capacity.

This gate reads ServerArgs plus final scheduler initialization, not requested CLI flags. It does not
certify readiness, output equality, full runtime correctness or performance.
"""
import argparse
import json
from pathlib import Path
import re

ROLES = {'prefill-0': (4, 1, 64), 'prefill-1': (4, 1, 64), 'decode-0': (8, 8, 256)}
FIELDS = ('max_running_requests', 'tp_size', 'ep_size', 'dtype',
          'mem_fraction_static', 'chunked_prefill_size', 'speculative_algorithm')


def parse(line):
    assert 'server_args=ServerArgs(' in line, 'Missing resolved ServerArgs'
    values = {}
    for key in FIELDS:
        matches = re.findall(r'(?<![\w.])' + key + r'=(None|True|False|\d+(?:\.\d+)?|\x27[^\x27]*\x27)(?=[,)])', line)
        assert len(matches) == 1, 'Missing or ambiguous resolved field: ' + key
        value = matches[0]
        if value == 'None':
            value = None
        elif value.startswith("'"):
            value = value[1:-1]
        elif value not in ('True', 'False'):
            value = float(value) if '.' in value else int(value)
        else:
            raise AssertionError('Boolean where scalar expected: ' + key)
        values[key] = value
    return values


def audit(root, mode):
    assert mode in ('control', 'candidate')
    observations = {}; failures = []
    for role, (tp, ep, capacity) in ROLES.items():
        paths = sorted(set(root.glob('task-' + role + '-*.log')) | {root / (role + '.log')})
        records = []; scheduler_records = []
        for path in paths:
            if not path.is_file():
                continue
            with path.open(errors='replace') as stream:
                for number, line in enumerate(stream, 1):
                    if 'server_args=ServerArgs(' in line:
                        records.append(dict(path=str(path), line=number, values=parse(line)))
                    if 'max_total_num_tokens=' in line and 'server_args=ServerArgs(' not in line:
                        cap = re.search(r'(?<![\w.])max_running_requests=(\d+)(?=[,\s])', line)
                        if cap:
                            scheduler_records.append(dict(path=str(path), line=number, max_running_requests=int(cap[1])))
        if not records:
            failures.append(role + ': no resolved ServerArgs log')
            continue
        unique = {json.dumps(r['values'], sort_keys=True) for r in records}
        if len(unique) != 1:
            failures.append(role + ': conflicting resolved settings')
            continue
        value = records[0]['values']; observations[role] = dict(server_args=records, final_scheduler=scheduler_records)
        if not scheduler_records:
            failures.append(role + ': no final scheduler capacity receipt')
        elif {r['max_running_requests'] for r in scheduler_records} != {capacity}:
            failures.append(role + ': final scheduler capacity differs from declaration')
        expected = dict(max_running_requests=capacity, tp_size=tp, ep_size=ep,
                        dtype='bfloat16', mem_fraction_static=.9,
                        speculative_algorithm='EAGLE3' if mode == 'candidate' else None)
        if role.startswith('prefill'):
            expected['chunked_prefill_size'] = 4096
        for key, wanted in expected.items():
            if value[key] != wanted:
                failures.append('{}: {}={} expected {}'.format(role, key, value[key], wanted))
    return dict(passed=not failures, mode=mode, observations=observations, failures=failures,
                scope='Declared and final scheduler capacity/dtype/topology log gate only; not full native execution, correctness or performance')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--mode', choices=['control', 'candidate'], required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert not args.out.exists(), 'Preserve prior audit'
    try:
        result = audit(args.run, args.mode)
    except (AssertionError, OSError, ValueError) as error:
        result = dict(passed=False, mode=args.mode, failures=[str(error)])
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=result['passed'], failures=result.get('failures', []))))
    raise SystemExit(0 if result['passed'] else 1)
