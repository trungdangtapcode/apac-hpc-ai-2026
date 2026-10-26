#!/usr/bin/env python3
"""One exclusive record per MPI rank; inspect, never alter, affinity."""
import json, os, pathlib, socket, sys
mode, root = sys.argv[1], pathlib.Path(sys.argv[2])
if mode == 'worker':
    rank = int(os.environ['OMPI_COMM_WORLD_RANK'])
    row = {'rank': rank, 'host': socket.getfqdn(), 'affinity_cpus': sorted(os.sched_getaffinity(0))}
    root.mkdir(parents=True, exist_ok=True)
    with (root / f'rank-{rank:02d}.json').open('x') as f:
        json.dump(row, f, sort_keys=True)
        f.write('\n')
elif mode == 'validate':
    paths = sorted(root.glob('rank-*.json'))
    assert len(paths) == 56 and {p.name for p in paths} == {f'rank-{i:02d}.json' for i in range(56)}, 'expected exactly one record for ranks 0..55'
    rows = [json.loads(p.read_text()) for p in paths]
    assert sorted(row['rank'] for row in rows) == list(range(56)), 'duplicate or missing rank'
    assert len({row['host'] for row in rows}) == 1, 'ranks span multiple hosts'
    assert all(row['affinity_cpus'] for row in rows), 'empty observed affinity mask'
    summary = {'passed': True, 'ranks': 56, 'host': rows[0]['host'], 'affinity_by_rank': rows}
    (root / 'validated-map.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'passed': True, 'ranks': 56, 'host': rows[0]['host']}))
else:
    raise SystemExit('mode must be worker or validate')
