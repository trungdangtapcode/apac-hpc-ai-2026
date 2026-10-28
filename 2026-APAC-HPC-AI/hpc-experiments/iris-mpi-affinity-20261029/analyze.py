#!/usr/bin/env python3
"""Validate a completed MPI affinity probe without contacting a scheduler."""
import collections
import json
import pathlib
import sys


def fail(message):
    raise SystemExit(f"validation failed: {message}")


root = pathlib.Path(sys.argv[1])
try:
    allocated = set(json.loads((root / "allocated-cpus.json").read_text()))
except Exception as exc:
    fail(f"cannot read allocated CPU set: {exc}")
if len(allocated) != 56:
    fail(f"allocation CPU set has {len(allocated)} CPUs, expected 56")

topology = {}
for line in (root / "lscpu.csv").read_text().splitlines():
    if not line or line.startswith("#"):
        continue
    fields = line.split(",")
    if len(fields) < 4:
        fail(f"malformed lscpu row: {line}")
    cpu, core, socket, node = fields[:4]
    if node == "" or node == "-":
        fail("lscpu did not report NUMA nodes")
    topology[int(cpu)] = {"core": int(core), "socket": int(socket), "node": int(node)}
if set(topology) != allocated:
    fail("allocated CPU IDs do not exactly match the visible node topology")
if len({v["socket"] for v in topology.values()}) != 2:
    fail("expected exactly two CPU sockets")
if len({v["node"] for v in topology.values()}) != 2:
    fail("expected exactly two NUMA nodes")
if len({(v["socket"], v["core"]) for v in topology.values()}) != 56:
    fail("expected 56 distinct physical cores (SMT off)")

records = {}
all_hosts = set()
for mode in ("A-default", "B-fill", "C-span"):
    directory = root / mode
    files = sorted(directory.glob("rank-*.json"))
    if len(files) != 56:
        fail(f"{mode}: found {len(files)} rank records, expected 56")
    rows = {}
    for path in files:
        row = json.loads(path.read_text())
        rank = row["rank"]
        if rank in rows or row["size"] != 56 or row["mode"] != mode:
            fail(f"{mode}: duplicate rank or inconsistent mode/size")
        if row["pre_mpi_init_errno"] or row["post_mpi_init_errno"]:
            fail(f"{mode} rank {rank}: sched_getaffinity failed")
        pre, post = set(row["pre_cpus"]), set(row["post_cpus"])
        if not pre or not post or not pre <= allocated or not post <= allocated:
            fail(f"{mode} rank {rank}: invalid affinity mask")
        if len(row["post_numa_nodes"]) != len(row["post_cpus"]):
            fail(f"{mode} rank {rank}: NUMA mask length mismatch")
        if -1 in row["post_numa_nodes"]:
            fail(f"{mode} rank {rank}: could not map post-init CPUs to NUMA nodes")
        rows[rank] = row
    if set(rows) != set(range(56)) or len({r["host"] for r in rows.values()}) != 1:
        fail(f"{mode}: ranks are incomplete or span multiple hosts")
    all_hosts.update(r["host"] for r in rows.values())
    for rank, row in rows.items():
        for cpu, node in zip(row["post_cpus"], row["post_numa_nodes"]):
            if topology[cpu]["node"] != node:
                fail(f"{mode} rank {rank}: sysfs NUMA mapping disagrees with lscpu topology")
    records[mode] = rows
if len(all_hosts) != 1:
    fail("modes ran on different hosts")

def checked_singleton_bijection(mode):
    mapping = {}
    for rank, row in records[mode].items():
        mask = row["post_cpus"]
        if len(mask) != 1:
            fail(f"{mode} rank {rank}: post-MPI mask is not a singleton")
        mapping[rank] = mask[0]
    if set(mapping.values()) != allocated or len(set(mapping.values())) != 56:
        fail(f"{mode}: post-MPI masks are not a bijection over all 56 CPUs")
    return mapping

bmap = checked_singleton_bijection("B-fill")
cmap = checked_singleton_bijection("C-span")
if bmap == cmap:
    fail("B-fill and C-span produced identical rank-to-CPU mappings")

def summarize(mode):
    rows = records[mode]
    rank_nodes = [topology[rows[r]["post_cpus"][0]]["node"]
                  if len(rows[r]["post_cpus"]) == 1 else None for r in range(56)]
    return {
        "rank_post_cpu": {str(r): rows[r]["post_cpus"] for r in range(56)},
        "rank_post_numa_node": {str(r): rows[r]["post_numa_nodes"] for r in range(56)},
        "singleton_rank_numa_counts": dict(collections.Counter(n for n in rank_nodes if n is not None)),
    }

amap = {r: records["A-default"][r]["post_cpus"] for r in range(56)}
report = {
    "validation": "PASS",
    "scope": "main-thread sched_getaffinity immediately before and after MPI_Init only",
    "topology": {"cpu_count": len(allocated), "sockets": 2, "numa_nodes": 2,
                 "distinct_socket_core_pairs": 56, "smt_threads_per_core": 1},
    "all_ranks_one_host": True,
    "A_default_vs_B_fill_rank_masks": "identical" if all(amap[r] == [bmap[r]] for r in range(56)) else "different",
    "B_fill_vs_C_span_rank_mapping": "distinct",
    "modes": {name: summarize(name) for name in records},
    "limitations": [
        "This measures affinity masks only; it does not run a solver or measure performance.",
        "It does not observe helper-thread masks, NUMA page residency, memory bandwidth, or causality.",
    ],
}
print(json.dumps(report, indent=2, sort_keys=True))
