"""Gate default and candidate MPI placement probes outside solver timing."""
import json
import sys
from pathlib import Path

mode, probe_path = sys.argv[1:3]
rows = [json.loads(line) for line in Path(probe_path).read_text().splitlines() if line.strip()]
assert len(rows) == 128
assert sorted(row["rank"] for row in rows) == list(range(128))
assert len({row["host"] for row in rows}) == 1, "Ranks span multiple hosts"
assert all(len(row["affinity"]) == 1 for row in rows), "Each rank must have one CPU"
assert len({row["affinity"][0] for row in rows}) == 128, "CPU overlap"
assert len({tuple(row["physical_core"]) for row in rows}) == 128, "Physical-core overlap"
assert all(len(row["numa_nodes"]) == 1 for row in rows), "Ambiguous NUMA membership"

if mode == "default":
    nodes_by_block = []
    for block in range(8):
        group = [row for row in rows if row["rank"] // 16 == block]
        assert len(group) == 16
        nodes = {tuple(row["numa_nodes"]) for row in group}
        assert len(nodes) == 1, "A contiguous 16-rank block spans NUMA groups"
        nodes_by_block.append(next(iter(nodes)))
    assert len(set(nodes_by_block)) == 8, "Blocks must map to eight distinct NUMA nodes"
elif mode == "candidate":
    expected = json.loads(Path(sys.argv[3]).read_text())
    assert len(expected["expected_rank_mapping"]) == 128
    by_rank = {row["rank"]: row for row in rows}
    for target in expected["expected_rank_mapping"]:
        row = by_rank[target["rank"]]
        assert row["affinity"] == [target["cpu"]], (target, row)
        assert row["numa_nodes"] == [target["numa_node"]], (target, row)
    assert next(iter({row["host"] for row in rows})) == expected["allocation_host_in_probe"]
else:
    raise AssertionError("mode must be default or candidate")
print(json.dumps({"passed": True, "mode": mode, "ranks": len(rows),
                  "host": rows[0]["host"], "unique_physical_cores": 128,
                  "scope": "Startup diagnostic only; not solver-time affinity or page-residency evidence."},
                 indent=2))
