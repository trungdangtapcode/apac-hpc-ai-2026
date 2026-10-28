#!/usr/bin/env python3
"""Build explicit Open MPI rankfiles from the actual default affinity probe."""
from __future__ import annotations

import csv
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parent
N_RANKS = 56


def read_probe(directory: pathlib.Path) -> dict[int, dict]:
    rows = {}
    for path in directory.glob("rank-*.json"):
        row = json.loads(path.read_text())
        rank = int(row["rank"])
        if rank in rows:
            raise ValueError(f"duplicate rank probe: {rank}")
        rows[rank] = row
    if set(rows) != set(range(N_RANKS)):
        raise ValueError("probe must contain each rank 0..55 exactly once")
    hosts = {r["host"] for r in rows.values()}
    if len(hosts) != 1 or any(r["size"] != N_RANKS for r in rows.values()):
        raise ValueError("probe must be a single-node 56-rank MPI job")
    for rank, row in rows.items():
        if row["pre_mpi_init_errno"] or row["post_mpi_init_errno"]:
            raise ValueError(f"rank {rank}: affinity read failed")
        if len(row["post_cpus"]) != 1 or len(row["post_numa_nodes"]) != 1:
            raise ValueError(f"rank {rank}: default rank is not bound to one CPU")
    return rows


def read_lscpu(path: pathlib.Path) -> dict[int, tuple[int, int, int]]:
    cpus = {}
    with path.open(newline="") as stream:
        for row in csv.reader(line for line in stream if not line.startswith("#")):
            if len(row) < 4:
                continue
            cpu, core, socket, node = map(int, row[:4])
            cpus[cpu] = (socket, core, node)
    if not cpus:
        raise ValueError("lscpu CSV has no CPU rows")
    return cpus


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: build_rankfiles.py DEFAULT_PROBE_DIR LSCPU_CSV OUTPUT_DIR")
    probe_dir, lscpu_csv, out = map(pathlib.Path, sys.argv[1:])
    out.mkdir(parents=True, exist_ok=False)
    default = read_probe(probe_dir)
    topo = read_lscpu(lscpu_csv)
    cpu_for_rank = {rank: int(row["post_cpus"][0]) for rank, row in default.items()}
    if len(set(cpu_for_rank.values())) != N_RANKS:
        raise ValueError("default ranks do not have distinct CPUs")
    numa_for_rank = {rank: int(row["post_numa_nodes"][0]) for rank, row in default.items()}
    group0 = [numa_for_rank[r] for r in range(28)]
    group1 = [numa_for_rank[r] for r in range(28, 56)]
    if len(set(group0)) != 1 or len(set(group1)) != 1 or group0[0] == group1[0]:
        raise ValueError("actual default ranks 0..27 and 28..55 must occupy two distinct NUMA nodes")
    if any(cpu not in topo for cpu in cpu_for_rank.values()):
        raise ValueError("a probed CPU is absent from lscpu topology")
    if any(topo[cpu][2] != numa_for_rank[r] for r, cpu in cpu_for_rank.items()):
        raise ValueError("lscpu NUMA labels disagree with the actual default MPI probe")
    # Open MPI rankfiles use hwloc logical slot indexes, which are not safely
    # inferred from lscpu's OS package/core labels. The identity rankfile uses
    # the runtime-qualified global slot r for MPI rank r. Its probe must match
    # the actual default OS-CPU map before any solver is launched. Candidate
    # ranks target CPUs by inverting that observed runtime mapping.
    logical_slot_for_cpu = {cpu_for_rank[r]: r for r in range(N_RANKS)}
    node0, node1 = group0[0], group1[0]
    node_cpu_pool = {
        node0: sorted(cpu_for_rank[r] for r in range(28)),
        node1: sorted(cpu_for_rank[r] for r in range(28, 56)),
    }
    if any(len(v) != 28 for v in node_cpu_pool.values()):
        raise ValueError("default NUMA CPU pools must each contain 28 distinct CPUs")

    candidate = json.loads((ROOT / "candidate.json").read_text())
    if candidate["order"] != "zyx" or candidate["actual_affinity_probe_job"] != "2294358":
        raise ValueError("candidate is not the reviewed zyx graph partition")
    groups = candidate["candidate_rank_groups"]
    ranks0 = list(map(int, groups["NUMA0"]))
    ranks1 = list(map(int, groups["NUMA1"]))
    if len(ranks0) != 28 or len(ranks1) != 28 or set(ranks0) | set(ranks1) != set(range(56)) or set(ranks0) & set(ranks1):
        raise ValueError("candidate must partition all 56 ranks into two groups of 28")
    if candidate["baseline_rank_groups"] != {"NUMA0": list(range(28)), "NUMA1": list(range(28, 56))}:
        raise ValueError("candidate's stated baseline groups differ from the measured default grouping")

    assignments = {
        "identity": {r: cpu_for_rank[r] for r in range(56)},
        "candidate": {},
    }
    for group, ranks, node in (("NUMA0", ranks0, node0), ("NUMA1", ranks1, node1)):
        for rank, cpu in zip(sorted(ranks), node_cpu_pool[node]):
            assignments["candidate"][rank] = cpu

    mapping = {
        "schema_version": 1,
        "actual_default_probe": str(probe_dir),
        "lscpu_csv": str(lscpu_csv),
        "candidate_sha256": __import__("hashlib").sha256((ROOT / "candidate.json").read_bytes()).hexdigest(),
        "default_rank_cpu_numa": {str(r): {"cpu": cpu_for_rank[r], "numa": numa_for_rank[r]} for r in range(N_RANKS)},
        "numa_cpu_pools": {str(node0): node_cpu_pool[node0], str(node1): node_cpu_pool[node1]},
        "candidate_rank_groups": {"NUMA0": sorted(ranks0), "NUMA1": sorted(ranks1)},
        "actual_numa_nodes": {"NUMA0": node0, "NUMA1": node1},
        "assignments": {},
        "logical_slots": {},
    }
    hostname = next(iter(default.values()))["host"]
    for name, assignment in assignments.items():
        lines, record = [], {}
        slots = {}
        for rank in range(N_RANKS):
            cpu = assignment[rank]
            slot = rank if name == "identity" else logical_slot_for_cpu[cpu]
            lines.append(f"rank {rank}=+n0 slot={slot}")
            slots[str(rank)] = slot
            record[str(rank)] = {"cpu": cpu, "logical_slot": slot, "numa": topo[cpu][2]}
        (out / f"{name}.rankfile").write_text("\n".join(lines) + "\n")
        mapping["assignments"][name] = record
        mapping["logical_slots"][name] = slots
    mapping["relative_node_symbol"] = "+n0"
    mapping["host_seen_by_probe"] = hostname
    (out / "mapping-plan.json").write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"passed": True, "ranks": 56, "identity_same_as_default": True,
                      "candidate_groups": {"NUMA0": len(ranks0), "NUMA1": len(ranks1)},
                      "candidate_cpu_map_distinct": len(set(assignments["candidate"].values())) == 56}, sort_keys=True))


if __name__ == "__main__":
    main()
