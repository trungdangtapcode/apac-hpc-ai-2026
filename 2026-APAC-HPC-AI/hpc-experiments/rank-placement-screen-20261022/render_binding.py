"""Render a PALS CPU-list argument from a graph mapping and a rank probe.

This never launches MPI or changes affinity. A historical probe is useful only
for offline qualification; an actual experiment needs a fresh allocation probe
and a second probe with the generated binding before every mandatory stage.
"""
import argparse
import hashlib
import json
from pathlib import Path


def render(screen, rows):
    assert screen["unchanged_graph_invariants"]["ranks"] == 128
    assert sorted(row["rank"] for row in rows) == list(range(128))
    hosts = {row["host"] for row in rows}
    assert len(hosts) == 1, "This mapping is for one node only"
    assert all(len(row["affinity"]) == 1 and len(row["numa_nodes"]) == 1 for row in rows)
    assert len({tuple(row["physical_core"]) for row in rows}) == 128, "SMT/core overlap"
    assert len({row["affinity"][0] for row in rows}) == 128
    numa_ids = sorted({row["numa_nodes"][0] for row in rows})
    assert len(numa_ids) == 8
    cpus = {node: sorted(row["affinity"][0] for row in rows if row["numa_nodes"] == [node])
            for node in numa_ids}
    assert all(len(values) == 16 for values in cpus.values())
    baseline_groups = [{row["numa_nodes"][0] for row in rows if row["rank"] // 16 == group}
                       for group in range(8)]
    assert all(len(group) == 1 for group in baseline_groups)
    assert len({next(iter(group)) for group in baseline_groups}) == 8, "Baseline grouping changed; recompute the graph control first"
    group_members = screen["candidate"]["logical_group_members"]
    assert len(group_members) == 8 and all(len(group) == 16 for group in group_members)
    assert sorted(rank for group in group_members for rank in group) == list(range(128))
    binding = [None] * 128
    expected = []
    for group, members in enumerate(group_members):
        node = numa_ids[group]
        for rank, cpu in zip(sorted(members), cpus[node]):
            assert screen["candidate"]["rank_to_logical_group"][rank] == group
            binding[rank] = cpu
            expected.append({"rank": rank, "cpu": cpu, "numa_node": node})
    assert sorted(binding) == sorted(row["affinity"][0] for row in rows)
    return {"allocation_host_in_probe": next(iter(hosts)),
            "pals_cpu_bind_argument": "list:" + ":".join(map(str, binding)),
            "expected_rank_mapping": sorted(expected, key=lambda row: row["rank"]),
            "scope": "Rendered only. CPU IDs belong exclusively to the supplied probe; no runtime execution or fresh-allocation assertion.",
            "required_runtime_gates": [
                "Use a fresh unbound rank probe from the actual exclusive one-node allocation.",
                "Probe the generated binding on that allocation; check host, physical cores, NUMA groups and rank coverage.",
                "Apply the same binding to renumberMesh, potentialFoam, applyBoundaryLayer and simpleFoam in the candidate arm.",
                "Keep the original control binding; restore original fields and repeat full mandatory initialization for both arms.",
                "A startup binding probe does not establish page residency or solver-time migration."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("screen", type=Path)
    parser.add_argument("rank_probe", type=Path)
    args = parser.parse_args()
    source = args.screen.read_bytes()
    probe = args.rank_probe.read_bytes()
    result = render(json.loads(source), [json.loads(line) for line in probe.splitlines() if line.strip()])
    result["screen_sha256"] = hashlib.sha256(source).hexdigest()
    result["probe_sha256"] = hashlib.sha256(probe).hexdigest()
    print(json.dumps(result, indent=2))
