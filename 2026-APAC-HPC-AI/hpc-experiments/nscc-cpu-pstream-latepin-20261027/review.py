#!/usr/bin/env python3
"""Strict offline replay for retained NSCC Pstream late-pin diagnostic records."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys

RANKS = 512
HOSTS = 4
LOCAL = 128
ADAPTED_ARMS = ("with-adapter", "pstream-checkmesh")
COMMANDS = (
    "module_setup", "pstream-ldd", "checkMesh-ldd", "checkMesh-help", "compile-native-probe",
    "compile-pmpi-adapter", "adapter-ldd", "native-probe-ldd", "blockMesh",
    "decomposePar", "arm-no-adapter", "arm-with-adapter", "arm-pstream-checkmesh",
)
PREP_RESOURCES = (
    "pstream-ldd", "checkMesh-ldd", "checkMesh-help", "compile-native-probe",
    "compile-pmpi-adapter", "adapter-ldd", "native-probe-ldd", "blockMesh", "decomposePar",
)

class ReviewError(Exception):
    pass

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)

def read_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        raise ReviewError(f"cannot parse {path}: {exc}") from exc

def native_arm(run: pathlib.Path, arm: str):
    root = run / "arms" / arm / "native"
    pre_files = sorted((root / "pre").glob("rank-*.json"))
    post_files = sorted(root.glob("rank-*.json"))
    require(len(pre_files) == RANKS, f"{arm}: expected 512 entry records, got {len(pre_files)}")
    require(len(post_files) == RANKS, f"{arm}: expected 512 post-init records, got {len(post_files)}")
    pre_by_key = {}
    pmi_set = set()
    world_set = set()
    for path in pre_files:
        row = read_json(path)
        key = (row.get("host"), row.get("pmi_rank"))
        require(key[0] and isinstance(key[1], int) and 0 <= key[1] < RANKS, f"{arm}: invalid pre-init identity {path}")
        require(key not in pre_by_key, f"{arm}: duplicate pre-init host/PMI key {key}")
        require(row.get("affinity_status") == 0 and row.get("errno") == 0 and row.get("phase")=="before_mpi_init_thread" and len(row.get("cpus", [])) > 0, f"{arm}: invalid pre-init affinity {path}")
        pre_by_key[key] = row
        pmi_set.add(key[1])
    post_pmi_set=set();post_hosts=collections.Counter()
    for path in post_files:
        row = read_json(path)
        rank, pmi = row.get("rank"), row.get("pmi_rank")
        require(isinstance(rank, int) and 0 <= rank < RANKS, f"{arm}: bad world rank in {path}")
        require(isinstance(pmi, int) and 0 <= pmi < RANKS, f"{arm}: bad PMI rank in {path}")
        require(row.get("phase")=="after_mpi_init_thread" and row.get("affinity_status") == 0 and row.get("errno")==0 and len(row.get("cpus", [])) > 0,
                f"{arm}: invalid post-init record {path}")
        require(pmi not in post_pmi_set and (row.get("host"),pmi) in pre_by_key,f"{arm}: duplicate or mismatched post-init PMI identity")
        require(path.name==f"rank-{rank:04d}.json",f"{arm}: native post filename/world identity mismatch")
        post_pmi_set.add(pmi);post_hosts[row.get("host")]+=1
        world_set.add(rank)
    require(len(pmi_set) == len(world_set) == RANKS, f"{arm}: incomplete or duplicate native rank identities")
    require(len(post_pmi_set)==512 and len(post_hosts)==4 and set(post_hosts.values())=={128},f"{arm}: native host/PMI shape mismatch")
    native_log=(run/f"logs/arm-{arm}.stdout.txt").read_text()
    summaries=re.findall(r"MPI_SUMMARY_JSON (\{[^\n]+\})",native_log)
    require(len(summaries)==1,f"{arm}: missing or repeated native MPI summary")
    summary=json.loads(summaries[0]);require(summary.get("world_size")==512 and summary.get("ranks_with_capture_or_identity_errors")==0,f"{arm}: failed native MPI summary")
    return pre_by_key

def validate_adapter_arm(run: pathlib.Path, arm: str, baseline_pre: dict):
    root = run / "arms" / arm / "adapter-ranks"
    dirs = sorted(root.glob("rank-[0-9][0-9][0-9][0-9]"))
    require(len(dirs) == RANKS, f"{arm}: expected 512 isolated rank audit directories, got {len(dirs)}")
    inits, finals, maps = [], [], []
    pmi_seen, world_seen = set(), set()
    host_world = collections.Counter()
    host_local = collections.defaultdict(set)
    host_map = {}
    mapping = {"matched_by_host_and_pmi": 0, "same_singleton_target": 0, "different_or_non_singleton": 0, "missing_baseline_join": 0}
    for path in dirs:
        init = read_json(path / "init.json")
        final = read_json(path / "finalize.json")
        topo = read_json(next(iter(path.glob("host-topology-world-*.json")), path / "missing-topology.json"))
        finalize_return = read_json(path / "finalize-return.json")
        rank, pmi, host, local = init.get("world_rank"), init.get("pmi_rank"), init.get("host"), init.get("local_rank")
        require(isinstance(rank, int) and 0 <= rank < RANKS, f"{arm}: invalid world rank {path}")
        require(isinstance(pmi, int) and 0 <= pmi < RANKS, f"{arm}: invalid PMI rank {path}")
        require(host == topo.get("host") and init.get("world_rank") == topo.get("world_rank") and pmi == topo.get("pmi_rank"), f"{arm}: init/topology identity mismatch {path}")
        require(path.name == f"rank-{pmi:04d}", f"{arm}: rank workspace is not keyed by validated PMI_RANK: {path}")
        require(rank not in world_seen and pmi not in pmi_seen, f"{arm}: duplicate world or PMI rank")
        world_seen.add(rank); pmi_seen.add(pmi); host_world[host] += 1; host_local[host].add(local)
        require(init.get("world_size") == RANKS and init.get("local_size") == LOCAL and isinstance(local, int) and 0 <= local < LOCAL,
                f"{arm}: invalid world/local dimensions for rank {rank}")
        require(init.get("hook") in ("MPI_Init", "MPI_Init_thread"), f"{arm}: unexpected init hook for rank {rank}")
        req, provided = init.get("requested_thread_level"), init.get("provided_thread_level")
        require(isinstance(req, int) and isinstance(provided, int) and provided >= req, f"{arm}: invalid MPI thread levels for rank {rank}")
        require(init.get("underlying_init_rc") == 0 and init.get("init_thread_matches_hook_thread") is True and
                init.get("hook_thread_is_process_main") is True and init.get("hook_thread_tid") == init.get("process_pid") and
                init.get("repeated_or_nested_init_rejected") is False,
                f"{arm}: init hook/return audit failed for rank {rank}")
        require(init.get("topology_status") == 0 and init.get("preflight_global_error_count") == 0 and
                init.get("sched_setaffinity_status") == 0 and init.get("collective_init_error_count") == 0,
                f"{arm}: pin qualification failed at init for rank {rank}")
        target = init.get("target_cpu")
        require(isinstance(target, int) and target >= 0, f"{arm}: missing target CPU for rank {rank}")
        post = init.get("post_init_mask")
        after = init.get("after_pin_mask")
        require(init.get("before_init_status") == 0 and init.get("post_init_status") == 0 and init.get("after_pin_status") == 0,
                f"{arm}: affinity snapshot failure for rank {rank}")
        require(isinstance(post, list) and target in post, f"{arm}: target not in that rank's post-init mask {rank}")
        require(after == [target] and init.get("sched_setaffinity_errno") == 0, f"{arm}: after-pin mask is not the selected singleton for rank {rank}")
        require(init.get("physical_socket") == topo.get("selected_slots_sorted_package_core", [{}])[local].get("package") and
                init.get("physical_core") == topo.get("selected_slots_sorted_package_core", [{}])[local].get("core") and
                init.get("numa_node") == topo.get("selected_slots_sorted_package_core", [{}])[local].get("node"),
                f"{arm}: selected topology differs from local slot for rank {rank}")
        final_mask = final.get("before_pmpi_finalize_mask")
        require(final.get("hook") == "MPI_Finalize" and final.get("audit_phase") == "immediately_before_PMPI_Finalize" and
                final.get("pmpi_finalize_return_code") is None, f"{arm}: finalize audit boundary is invalid for rank {rank}")
        require(finalize_return.get("hook") == "PMPI_Finalize_return" and finalize_return.get("world_rank") == rank and
                finalize_return.get("pmi_rank") == pmi and finalize_return.get("local_rank") == local and
                finalize_return.get("host") == host and finalize_return.get("target_cpu") == target and
                finalize_return.get("process_pid") == finalize_return.get("finalize_thread_tid") and
                finalize_return.get("pmpi_finalize_return_code") == finalize_return.get("mpi_success_constant") and
                finalize_return.get("collective_finalize_error_count") == 0 and
                finalize_return.get("pre_finalize_audit_write_error_count") == 0,
                f"{arm}: actual PMPI_Finalize return audit failed for rank {rank}")
        require(final.get("world_rank") == rank and final.get("pmi_rank") == pmi and final.get("host") == host and
                final.get("local_rank") == local and final.get("local_size") == LOCAL and final.get("target_cpu") == target, f"{arm}: finalize identity/target mismatch for rank {rank}")
        require(final.get("before_pmpi_finalize_status") == 0 and final.get("finalize_thread_is_process_main") is True and
                final.get("finalize_thread_tid") == final.get("finalize_process_pid") and final_mask == [target] and final.get("target_present") is True and
                final.get("singleton_target_mask") is True and final.get("finalize_thread_matches_hook_thread") is True and
                final.get("local_error") == 0 and final.get("repeated_or_nested_init_rejected") is False and final.get("collective_finalize_error_count") == 0,
                f"{arm}: final main-thread target audit failed for rank {rank}")
        rows = topo.get("allowed_cpu_sysfs_map")
        slots = topo.get("selected_slots_sorted_package_core")
        source_allowed = topo.get("topology_source_allowed")
        require(isinstance(rows, list) and len(rows) >= LOCAL and isinstance(slots, list) and len(slots) == LOCAL,
                f"{arm}: incomplete topology map on rank {rank}")
        require(topo.get("topology_source_world_rank") is not None and len(source_allowed or []) == len(rows),
                f"{arm}: missing topology-map provenance on rank {rank}")
        cpus = [row.get("cpu") for row in rows]
        require(sorted(cpus) == source_allowed and len(cpus) == len(set(cpus)) and all(row.get("online") is True for row in rows),
                f"{arm}: topology map does not match source allowed mask on rank {rank}")
        groups = collections.defaultdict(list)
        node_by_core = {}
        for row in rows:
            require(all(isinstance(row.get(key), int) and row[key] >= 0 for key in ("cpu", "package", "core", "node")),
                    f"{arm}: invalid sysfs topology row on rank {rank}")
            key = (row["package"], row["core"])
            if key in node_by_core:
                require(node_by_core[key] == row["node"], f"{arm}: siblings disagree on NUMA node")
            node_by_core[key] = row["node"]
            groups[key].append(row["cpu"])
        expected = []
        for key in sorted(groups):
            expected.append({"cpu": min(groups[key]), "package": key[0], "core": key[1], "node": node_by_core[key]})
        require(len(groups) == LOCAL and slots == expected, f"{arm}: 128-core slot recomputation failed on rank {rank}")
        require(topo.get("post_init_allowed") == post and target in topo.get("post_init_allowed", []),
                f"{arm}: topology record's rank mask does not match init snapshot for rank {rank}")
        if host in host_map:
            require(host_map[host] == (topo.get("topology_source_world_rank"), source_allowed, rows, slots),
                    f"{arm}: host topology changed between per-rank audit records for {host}")
        else:
            host_map[host] = (topo.get("topology_source_world_rank"), source_allowed, rows, slots)
        key = (host, pmi)
        if key in baseline_pre:
            mapping["matched_by_host_and_pmi"] += 1
            entry = baseline_pre[key].get("cpus", [])
            if len(entry) == 1 and target == entry[0]: mapping["same_singleton_target"] += 1
            else: mapping["different_or_non_singleton"] += 1
        else:
            mapping["missing_baseline_join"] += 1
        inits.append(init); finals.append(final); maps.append(topo)
    require(len(world_seen) == len(pmi_seen) == RANKS and len(host_world) == HOSTS, f"{arm}: not exactly 512 ranks on four hosts")
    require(all(count == LOCAL for count in host_world.values()) and all(len(host_local[h]) == LOCAL for h in host_world),
            f"{arm}: host/local-rank cardinality is not four groups of 128")
    for host, slots in ((host, record[3]) for host, record in host_map.items()):
        require(len({(slot["package"], slot["core"]) for slot in slots}) == LOCAL, f"{arm}: host {host} lacks 128 unique physical cores")
    leaders = {row["host"]: row["world_rank"] for row in inits if row["local_rank"] == 0}
    require(all(host_map[host][0] == leaders.get(host) for host in host_map), f"{arm}: topology map source is not the shared communicator local-rank zero")
    return {"ranks": RANKS, "hosts": dict(sorted(host_world.items())), "pmi_world_identity_unique": True,
            "all_init_and_finalize_audits_pass": True, "postinit_target_containment_and_singleton_stability": True,
            "topology_map_replayed_per_rank": True, "baseline_entry_target_comparison_by_host_and_pmi": mapping}

def validate(run: pathlib.Path):
    run = run.resolve()
    worker = read_json(run / "worker-status.json")
    require(worker.get("worker_return_code") == 0, "worker did not finish successfully")
    require(worker.get("payload_unchanged_return_code") == 0 and worker.get("runtime_objects_unchanged_return_code") == 0,
            "payload or loaded runtime objects changed during run")
    for left, right, label in (("payload-sha256-before.txt", "payload-sha256-after.txt", "payload hash"),
                               ("runtime-hashes-before.txt", "runtime-hashes-after.txt", "runtime hash")):
        require((run / left).read_bytes() == (run / right).read_bytes(), f"{label} before/after mismatch")
        require((run / left).stat().st_size > 0, f"{label} evidence is empty")
    codes = {}
    for line in (run / "command-return-codes.jsonl").read_text().splitlines():
        row = json.loads(line)
        codes[row["command"]] = row["return_code"]
    for name in COMMANDS:
        require(codes.get(name) == 0, f"required command {name} did not return zero")
    require(codes.get("payload_unchanged") == 0 and codes.get("runtime_objects_unchanged") == 0, "hash integrity command failed")
    require("/mpich/8.1.15/" in (run / "logs/pstream-ldd.stdout.txt").read_text(), "Pstream did not link to Cray MPICH 8.1.15")
    require("/mpich/8.1.15/" in (run / "logs/checkMesh-ldd.stdout.txt").read_text(), "checkMesh did not link to Cray MPICH 8.1.15")
    require("/mpich/8.1.15/" in (run / "logs/adapter-ldd.stdout.txt").read_text(), "adapter did not link to Cray MPICH 8.1.15")
    exact_mpi = (run / "logs/mpi-shared-library-path.txt").read_text().strip()
    require(exact_mpi.startswith("/") and "/mpich/8.1.15/" in exact_mpi, "exact Pstream MPI link path is invalid")
    for trace in ("pstream-ldd", "adapter-ldd"):
        require(exact_mpi in (run / f"logs/{trace}.stdout.txt").read_text(), f"{trace} did not resolve to the exact Pstream MPI library")
    require("/mpich/8.1.15/" in (run / "logs/native-probe-ldd.stdout.txt").read_text(), "native probe did not link to Cray MPICH 8.1.15")
    settings = (run / "logs/selected-runtime-settings.txt").read_text()
    settings_rows = dict(line.split("=", 1) for line in settings.splitlines() if "=" in line)
    project_dir = pathlib.Path(settings_rows.get("WM_PROJECT_DIR", "/missing"))
    pstream_path = pathlib.Path((run / "logs/pstream-path.txt").read_text().strip())
    require(project_dir.is_absolute() and pstream_path.is_relative_to(project_dir), "recorded Pstream path is outside the loaded OpenFOAM project")
    for required in ("MPICH_RANK_REORDER_METHOD=0", "PALS_CPU_BIND=unset", "MPICH_RANK_ORDER=unset", "MPICH_RANK_REORDER_FILE=unset", "LD_PRELOAD=empty"):
        require(required in settings, f"missing cleared runtime setting {required}")
    phase_text = (run / "phases.tsv").read_text()
    for phase_name in ("module_setup", "blockMesh", "decomposePar", "arm-no-adapter", "arm-with-adapter", "arm-pstream-checkmesh"):
        require(phase_name in phase_text, f"missing phase evidence for {phase_name}")
    for name in PREP_RESOURCES:
        require((run / f"resources/{name}.time.txt").is_file(), f"missing resource record {name}")
    for name in ("arm-no-adapter", "arm-with-adapter", "arm-pstream-checkmesh"):
        require((run / f"resources/{name}.time.txt").is_file(), f"missing resource record {name}")
        argv = (run / f"commands/{name}.argv.txt").read_text()
        require("mpiexec" in argv and "512" in argv, f"{name}: command line lacks 512-rank mpiexec evidence")
        if name == "arm-no-adapter":
            require("rank-exec.sh" not in argv and "latepin-pmpi-adapter" not in argv, "baseline arm unexpectedly preloaded the adapter")
        elif name == "arm-with-adapter":
            require("rank-exec.sh" in argv and "latepin-pmpi-adapter.so" in argv and "mpi-init-probe" in argv, "adapter control did not target the native probe")
        else:
            require("rank-exec.sh" in argv and "latepin-pmpi-adapter.so" in argv and "checkMesh" in argv and "-parallel" in argv and "-case" in argv, "Pstream arm did not invoke parallel checkMesh through the rank adapter")
    require((run/"expected-payload-sha256.txt").read_bytes()==(run/"payload-sha256-before.txt").read_bytes(),"job-start payload did not match frozen expected manifest")
    require(codes.get("payload_matches_frozen_before")==0,"frozen payload precheck failed")
    noadapter = native_arm(run, "no-adapter")
    adapter_native = native_arm(run, "with-adapter")
    adapted = {arm: validate_adapter_arm(run, arm, noadapter) for arm in ADAPTED_ARMS}
    utility = (run / "logs/arm-pstream-checkmesh.stdout.txt").read_text(errors="replace")
    require("Mesh OK." in utility and re.search(r"\bEnd\b", utility), "parallel checkMesh output lacks complete End/Mesh OK markers")
    require('OPENFOAM=2512' in utility and 'scalar=64' in utility and re.search(r'(?m)^nProcs\s*:\s*512\s*$',utility),'checkMesh version, precision or process count mismatch')
    require(re.search(r'(?m)^\s*cells\s*:\s*8192\s*$',utility),'checkMesh global cell count is not 8192')
    require(re.search(r'(?m)^\s*nCells\s*:\s*8192\s*$',(run/'logs/blockMesh.stdout.txt').read_text()),'blockMesh cell count is not 8192')
    case_mesh = run / "diagnostic-case/processor511/constant/polyMesh"
    require(case_mesh.is_dir(), "diagnostic decomposition lacks processor511 mesh")
    return {"passed": True, "scope": "bounded PMPI initialization/finalization and Pstream checkMesh interface qualification only; no solver, contest case, score, performance, helper-thread, NIC, or full-solver benefit claim",
            "run_directory": str(run), "command_return_codes_all_required_zero": True,
            "payload_and_runtime_hashes_unchanged": True, "baseline_native_arms": 2,
            "adapter_arms": adapted, "parallel_checkMesh_end_and_mesh_ok": True,
            "diagnostic_mesh_cells": 8192, "decomposition": [8, 8, 8],
            "resources_and_phase_records_present": True}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()
    try:
        result = validate(args.run)
    except Exception as exc:
        result = {"passed": False, "error": str(exc)}
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
