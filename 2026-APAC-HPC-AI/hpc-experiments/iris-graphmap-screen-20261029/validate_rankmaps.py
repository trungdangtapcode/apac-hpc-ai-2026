#!/usr/bin/env python3
"""Require exact native post-MPI affinity for default, control and candidate."""
from __future__ import annotations

import json
import pathlib
import sys


def load_probe(path: pathlib.Path) -> dict[int, dict]:
    rows = {}
    for item in path.glob("rank-*.json"):
        row = json.loads(item.read_text())
        rank = int(row["rank"])
        if rank in rows:
            raise ValueError(f"{path}: duplicate rank {rank}")
        rows[rank] = row
    if set(rows) != set(range(56)):
        raise ValueError(f"{path}: need exactly ranks 0..55")
    if len({r["host"] for r in rows.values()}) != 1:
        raise ValueError(f"{path}: ranks span more than one host")
    for rank, row in rows.items():
        if row["size"] != 56 or row["pre_mpi_init_errno"] or row["post_mpi_init_errno"]:
            raise ValueError(f"{path}: invalid native probe record at rank {rank}")
        if len(row["post_cpus"]) != 1 or len(row["post_numa_nodes"]) != 1:
            raise ValueError(f"{path}: rank {rank} is not on one CPU and one NUMA node")
    return rows


def cpu_map(rows: dict[int, dict]) -> dict[int, tuple[int, int]]:
    return {r: (int(row["post_cpus"][0]), int(row["post_numa_nodes"][0])) for r, row in rows.items()}


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit("usage: validate_rankmaps.py DEFAULT IDENTITY CANDIDATE MAPPING_PLAN")
    default = cpu_map(load_probe(pathlib.Path(sys.argv[1])))
    identity = cpu_map(load_probe(pathlib.Path(sys.argv[2])))
    candidate = cpu_map(load_probe(pathlib.Path(sys.argv[3])))
    plan = json.loads(pathlib.Path(sys.argv[4]).read_text())
    expected_id = {int(r): (int(v["cpu"]), int(v["numa"])) for r, v in plan["assignments"]["identity"].items()}
    expected_candidate = {int(r): (int(v["cpu"]), int(v["numa"])) for r, v in plan["assignments"]["candidate"].items()}
    if identity != default or identity != expected_id:
        raise ValueError("identity rankfile is not an exact match for Open MPI default rank-to-CPU/NUMA masks")
    if candidate != expected_candidate:
        mismatches = {r: {"expected": expected_candidate[r], "actual": candidate[r]}
                      for r in range(56) if candidate[r] != expected_candidate[r]}
        raise ValueError(f"candidate rankfile did not create the exact planned CPU map: {mismatches}")
    g = plan["candidate_rank_groups"]
    node0 = int(plan["actual_numa_nodes"]["NUMA0"])
    node1 = int(plan["actual_numa_nodes"]["NUMA1"])
    if any(candidate[r][1] != node0 for r in g["NUMA0"]):
        raise ValueError("candidate NUMA0 graph group did not map wholly to the measured NUMA0 CPU pool")
    if any(candidate[r][1] != node1 for r in g["NUMA1"]):
        raise ValueError("candidate NUMA1 graph group did not map wholly to the measured NUMA1 CPU pool")
    print(json.dumps({"passed": True, "ranks": 56, "default_equals_identity_rankfile": True,
                      "candidate_exact_os_cpu_map": True, "candidate_exact_numa_groups": True,
                      "default_cpu_map": {str(r): default[r][0] for r in range(56)},
                      "candidate_cpu_map": {str(r): candidate[r][0] for r in range(56)}},
                     sort_keys=True))


if __name__ == "__main__":
    main()
