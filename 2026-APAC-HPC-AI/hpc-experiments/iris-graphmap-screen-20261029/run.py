#!/usr/bin/env python3
"""Conditional native 14-step ABBA rank-placement screen; not a scored run."""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import os
import pathlib
import re
import shutil
import socket
import statistics
import subprocess
import sys
import time

from case_checks import source_check
from review_short_output import review


KIT = pathlib.Path(__file__).resolve().parent
WORK = KIT
SOURCE = pathlib.Path("/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-order-init-20261026T133526Z/initialized/order-zyx")
ARM_ORDER = ("A1-default", "B1-graph", "B2-graph", "A2-default")
STEPS = 14
SOLVER_CAP_SECONDS = 650
CLONE_CAP_SECONDS = 150
CLONE_RESERVATION_SECONDS = 80
SOLVER_MINIMUM_WINDOW_SECONDS = 530
POST_ARM_RESERVE_SECONDS = 15
FINAL_REVIEW_RESERVE_SECONDS = 50
INTERNAL_DEADLINE_SECONDS = 2850
OUTER_TIMEOUT_SECONDS = 2970
DEADLINE = 0.0
RUN: pathlib.Path


def save(path: pathlib.Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def remaining() -> int:
    return int(DEADLINE - time.monotonic())


def phase(name: str, state: str, **extra: object) -> None:
    row = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "phase": name, "state": state, **extra}
    with (RUN / "phases.jsonl").open("a") as stream:
        stream.write(json.dumps(row, sort_keys=True) + "\n")


def bounded(label: str, args: list[str], cwd: pathlib.Path, cap: int, *, capture: pathlib.Path | None = None) -> dict:
    left = remaining() - 20
    if left <= 0:
        raise RuntimeError(f"internal deadline leaves no margin for {label}")
    limit = min(cap, left)
    started = time.monotonic()
    phase(label, "start", cap_seconds=limit)
    target = capture or RUN / f"{label}.log"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w") as stream:
        try:
            proc = subprocess.run(["timeout", "--signal=TERM", "--kill-after=8s", f"{limit}s", *args],
                                  cwd=cwd, stdout=stream, stderr=subprocess.STDOUT,
                                  timeout=limit + 15, check=False)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = 124
    row = {"label": label, "returncode": rc, "elapsed_seconds": time.monotonic() - started,
           "cap_seconds": limit, "command": list(map(str, args)), "log": str(target)}
    save(RUN / f"{label}.status.json", row)
    phase(label, "exit", returncode=rc, elapsed_seconds=row["elapsed_seconds"])
    if rc:
        raise RuntimeError(f"{label} exited {rc}; see {target}")
    return row


def shell_identity() -> dict:
    values = {}
    for name in ("SLURM_JOB_ID", "SLURM_JOB_NODELIST", "SLURM_JOB_NUM_NODES", "SLURM_NTASKS",
                 "SLURM_CPUS_ON_NODE", "SLURM_JOB_PARTITION", "SLURM_JOB_QOS"):
        values[name] = os.environ.get(name)
    values.update({"hostname": socket.getfqdn(), "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "affinity": sorted(os.sched_getaffinity(0)), "requested_walltime_seconds": 3000,
                   "internal_deadline_seconds": INTERNAL_DEADLINE_SECONDS,
                   "outer_timeout_seconds": OUTER_TIMEOUT_SECONDS,
                   "maximum_allocated_cpu_hours": 56 * 3000 / 3600,
                   "arms": list(ARM_ORDER), "solver_cap_seconds_each": SOLVER_CAP_SECONDS,
                   "clone_cap_seconds_each": CLONE_CAP_SECONDS,
                   "score_claim": False})
    if int(os.environ.get("SLURM_NTASKS", "0")) != 56 or int(os.environ.get("SLURM_JOB_NUM_NODES", "0")) != 1:
        raise RuntimeError("requires exactly one Iris node and 56 allocated tasks")
    if len(values["affinity"]) < 56:
        raise RuntimeError("batch shell is not allowed the full 56-CPU allocation")
    return values


def runtime_snapshot(label: str) -> dict:
    tools = {}
    for name in ("simpleFoam", "mpirun"):
        found = shutil.which(name)
        if not found:
            raise RuntimeError(f"{name} is not available after module load")
        resolved = pathlib.Path(found).resolve()
        tools[name] = {"path": found, "resolved_path": str(resolved),
                       "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest()}
    ldd = subprocess.run(["ldd", tools["simpleFoam"]["resolved_path"]], text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    libraries = {}
    for line in ldd.stdout.splitlines():
        match = re.search(r"=>\s+(/\S+)", line) or re.match(r"\s*(/\S+)\s+\(", line)
        if not match:
            continue
        path = pathlib.Path(match.group(1)).resolve()
        if path.is_file():
            libraries[str(path)] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                    "bytes": path.stat().st_size}
    if not libraries or "not found" in ldd.stdout:
        raise RuntimeError("native simpleFoam has unresolved runtime libraries")
    result = {"label": label, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "tools": tools, "libraries": libraries, "ldd_simpleFoam": ldd.stdout}
    save(RUN / f"runtime-{label}.json", result)
    return result


def field_seal_from_manifest(root: pathlib.Path, manifest: dict) -> dict:
    fields = {}
    hashes = manifest["files"]
    for rank in range(56):
        for name in ("U", "p", "k", "omega", "nut", "nuTilda"):
            rel = f"processor{rank}/0/{name}"
            path = root / rel
            if rel not in hashes or not path.is_file() or path.is_symlink():
                raise ValueError(f"missing regular source field {rel}")
            fields[rel] = {"bytes": path.stat().st_size, "sha256": hashes[rel]}
    if len(fields) != 336:
        raise ValueError("source manifest did not seal all 336 initialized rank fields")
    return {"passed": True, "scope": "336 initialized time-zero field bytes and SHA256 hashes",
            "field_count": len(fields), "fields": fields}


def field_seal_from_case_time0(root: pathlib.Path) -> dict:
    fields = {}
    for rank in range(56):
        for name in ("U", "p", "k", "omega", "nut", "nuTilda"):
            rel = f"processor{rank}/0/{name}"
            path = root / rel
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"missing regular time-zero field after solver: {rel}")
            h = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(2 * 1024 * 1024), b""):
                    h.update(block)
            fields[rel] = {"bytes": path.stat().st_size, "sha256": h.hexdigest()}
    return {"passed": True, "scope": "336 initialized time-zero field bytes and SHA256 hashes",
            "field_count": len(fields), "fields": fields}


def verify_frozen_graph_boundaries(manifest: dict) -> dict:
    candidate = json.loads((KIT / "candidate.json").read_text())
    processor_graph = (KIT / "processor-interface-graphs.json").read_bytes()
    graph_search = (KIT / "graph-search.json").read_bytes()
    if hashlib.sha256(processor_graph).hexdigest() != candidate["source_processor_graph_sha256"]:
        raise ValueError("local processor-interface graph differs from the hash frozen into candidate.json")
    if hashlib.sha256(graph_search).hexdigest() != candidate["source_graph_search_sha256"]:
        raise ValueError("local graph-search result differs from the hash frozen into candidate.json")
    graph = json.loads(processor_graph)
    expected = graph["orders"]["zyx"]["boundary_sha256"]
    if set(expected) != {str(r) for r in range(56)}:
        raise ValueError("frozen zyx graph must pin all 56 processor boundary hashes")
    actual = {}
    for rank in range(56):
        rel = f"processor{rank}/constant/polyMesh/boundary"
        if rel not in manifest["files"]:
            raise ValueError(f"source inventory does not contain graph boundary file {rel}")
        actual[str(rank)] = manifest["files"][rel]
    if actual != expected:
        mismatches = [rank for rank in expected if actual.get(rank) != expected[rank]]
        raise ValueError(f"initialized zyx source does not match all frozen graph boundary hashes: {mismatches}")
    return {"passed": True, "boundary_files": 56, "order": "zyx",
            "processor_graph_sha256": candidate["source_processor_graph_sha256"],
            "graph_search_sha256": candidate["source_graph_search_sha256"],
            "boundary_sha256": actual}


def verify_accepted_source(manifest: dict) -> dict:
    path = KIT / "accepted-source-manifest.json"
    raw = path.read_bytes()
    accepted = json.loads(raw)
    if set(accepted) != {"files", "symlinks"} or manifest != accepted:
        raise ValueError("current initialized zyx inventory differs from the reviewed accepted-source manifest")
    if len(accepted["files"]) != 1040:
        raise ValueError(f"accepted source baseline expected 1,040 regular files, found {len(accepted['files'])}")
    return {"passed": True, "source_parent_job": "2294262", "regular_files": len(accepted["files"]),
            "symlinks": len(accepted["symlinks"]), "accepted_manifest_sha256": hashlib.sha256(raw).hexdigest(),
            "scope": "exact files and symlink targets over system, constant, and processorN/(0|constant) roots"}


def run_probe(name: str, extra: list[str]) -> None:
    out = RUN / "probes" / name
    out.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env["PROBE_OUT"] = str(out)
    cmd = ["timeout", "--signal=TERM", "--kill-after=5s", "35s", "mpirun", "-np", "56", *extra,
           str(RUN / "affinity_probe"), name]
    started = time.monotonic()
    with (out / "mpirun.log").open("w") as stream:
        proc = subprocess.run(cmd, cwd=KIT, env=env, stdout=stream, stderr=subprocess.STDOUT,
                              timeout=50, check=False)
    save(out / "launch.json", {"command": cmd, "returncode": proc.returncode,
                                "elapsed_seconds": time.monotonic() - started})
    if proc.returncode:
        raise RuntimeError(f"native {name} affinity probe failed: {proc.returncode}")


def configure(case: pathlib.Path) -> dict:
    path = case / "system/controlDict"
    original = path.read_bytes()
    check = source_check(case, "zyx")
    text, count = re.subn(rb"(?m)^endTime[ \t]+[^;\n]+;[^\n]*$", f"endTime {STEPS};".encode(), original)
    if count != 1:
        raise ValueError("expected exactly one controlDict endTime line")
    path.write_bytes(text)
    now = path.read_bytes()
    if now != text or re.search(rb"(?m)^endTime\s+" + str(STEPS).encode() + rb"\s*;", now) is None:
        raise ValueError(f"endTime {STEPS} edit did not persist exactly")
    if b"startFrom         latestTime;" not in now:
        raise ValueError("screen must start from the frozen initialized latestTime")
    return {"passed": True, "order": "zyx", "ranks": 56, "hierarchy_factors": [7, 4, 2],
            "steps": STEPS, "only_allowed_control_edit": "system/controlDict:endTime", "source_check": check,
            "physics_and_function_objects": "retained byte-identically from the frozen initialized source"}


def arm_gate(index: int, *, after_clone: bool = False) -> None:
    count = len(ARM_ORDER) - index
    if after_clone:
        reserve = SOLVER_MINIMUM_WINDOW_SECONDS + POST_ARM_RESERVE_SECONDS + (count - 1) * (
            CLONE_RESERVATION_SECONDS + SOLVER_MINIMUM_WINDOW_SECONDS + POST_ARM_RESERVE_SECONDS) + FINAL_REVIEW_RESERVE_SECONDS
    else:
        reserve = count * (CLONE_RESERVATION_SECONDS + SOLVER_MINIMUM_WINDOW_SECONDS + POST_ARM_RESERVE_SECONDS) + FINAL_REVIEW_RESERVE_SECONDS
    if remaining() < reserve:
        raise RuntimeError(f"stop before arm {ARM_ORDER[index]}: remaining {remaining()}s < protected complete-screen reserve {reserve}s")


def run_arm(index: int, rankfile_name: str) -> dict:
    label = ARM_ORDER[index]
    arm = RUN / "arms" / label
    if arm.exists():
        raise FileExistsError(arm)
    arm.parent.mkdir(parents=True, exist_ok=True)
    arm_gate(index)
    clone_started = time.monotonic()
    bounded(label + "-copy", ["python3", "-c", "import shutil,sys; shutil.copytree(sys.argv[1],sys.argv[2],symlinks=True)",
                                   str(SOURCE), str(arm)], KIT, CLONE_CAP_SECONDS)
    clone_time = time.monotonic() - clone_started
    verify_log = arm / "copy-verification.json"
    bounded(label + "-copy-check", ["python3", KIT / "seal_tree.py", "verify-copy", SOURCE, arm,
                                          RUN / "source-tree-before.json", verify_log], KIT, 90)
    copy_manifest = json.loads(verify_log.read_text())["manifest"]
    field_seal = field_seal_from_manifest(arm, copy_manifest)
    if field_seal != json.loads((RUN / "source-field-seal.json").read_text()):
        raise ValueError(f"{label}: initialized field bytes differ from the frozen source")
    save(arm / "initialized-fields-seal.json", field_seal)
    validation = configure(arm)
    save(arm / "source-and-control-validation.json", validation)
    arm_gate(index, after_clone=True)
    mapfile = RUN / "mapping" / f"{rankfile_name}.rankfile"
    command = ["/usr/bin/time", "-v", "-o", str(arm / "resource-time.log"),
               "timeout", "--signal=TERM", "--kill-after=10s", f"{SOLVER_CAP_SECONDS}s",
               "mpirun", "-np", "56", "--map-by", f"rankfile:file={mapfile}", "--bind-to", "core",
               "--", "simpleFoam", "-parallel"]
    command_record = {"command": list(map(str, command)), "rankfile": str(mapfile), "rankfile_sha256": hashlib.sha256(mapfile.read_bytes()).hexdigest(),
                      "launcher_policy": "identical explicit rankfile + bind-to core for all four solver arms",
                      "control_or_candidate": rankfile_name, "solver_cap_seconds": SOLVER_CAP_SECONDS}
    save(arm / "launch.json", command_record)
    started = time.monotonic()
    with (arm / "simpleFoam.log").open("w") as stdout, (arm / "solver.stderr").open("w") as stderr:
        try:
            proc = subprocess.run(command, cwd=arm, stdout=stdout, stderr=stderr,
                                  timeout=SOLVER_CAP_SECONDS + 25, check=False)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = 124
    elapsed = time.monotonic() - started
    save(arm / "solver-return-code.json", {"returncode": rc, "elapsed_seconds": elapsed,
                                           "cap_seconds": SOLVER_CAP_SECONDS, "clone_seconds": clone_time})
    if rc != 0:
        raise RuntimeError(f"{label}: solver did not complete cleanly, rc={rc}")
    record = review(arm)
    post_field_seal = field_seal_from_case_time0(arm)
    if post_field_seal != json.loads((RUN / "source-field-seal.json").read_text()):
        raise ValueError(f"{label}: native solver modified one or more sealed time-zero field files")
    save(arm / "post-solver-time0-field-seal.json", post_field_seal)
    record.update({"arm": label, "mapping": rankfile_name, "solver_elapsed_seconds": elapsed,
                   "clone_elapsed_seconds": clone_time, "returncode": rc})
    save(arm / "review.json", record)
    phase(label, "reviewed", mean_seconds_per_step=record["mean_seconds_per_step"],
          solver_elapsed_seconds=elapsed)
    return record


def main() -> None:
    global DEADLINE, RUN
    started = time.monotonic()
    DEADLINE = started + INTERNAL_DEADLINE_SECONDS
    job = os.environ["SLURM_JOB_ID"]
    RUN = WORK / "runs" / job
    RUN.mkdir(parents=True, exist_ok=False)
    intent = shell_identity()
    intent.update({"job_id": job, "utc_start": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "source": str(SOURCE), "candidate": json.loads((KIT / "candidate.json").read_text()),
                   "comparison_design": f"ABBA, each arm {STEPS} solver steps and {STEPS - 1} timed intervals",
                   "interpretation_limit": "single short allocation; non-scored; no 150-step result or causal claim",
                   "accepted_source_manifest_sha256": hashlib.sha256((KIT / "accepted-source-manifest.json").read_bytes()).hexdigest()})
    save(RUN / "run-intent.json", intent)

    # Full initialized source content is sealed once before and once after the
    # complete ABBA sequence. Each private clone is checked against that seal.
    bounded("payload-hash-before", ["sha256sum", "-c", "payload-sha256.txt"], KIT, 40)
    if not (SOURCE / "READY").is_file():
        raise RuntimeError("initialized zyx source does not have its READY marker")
    bounded("source-tree-seal", ["python3", KIT / "seal_tree.py", "inventory", SOURCE,
                                        RUN / "source-tree-before.json"], KIT, 80)
    source_manifest = json.loads((RUN / "source-tree-before.json").read_text())
    accepted_source_check = verify_accepted_source(source_manifest)
    save(RUN / "accepted-source-validation.json", accepted_source_check)
    boundary_validation = verify_frozen_graph_boundaries(source_manifest)
    save(RUN / "graph-boundary-validation.json", boundary_validation)
    field_seal = field_seal_from_manifest(SOURCE, source_manifest)
    save(RUN / "source-field-seal.json", field_seal)
    save(RUN / "runtime-allocation.json", {"shell": intent, "lscpu_command": "lscpu -p=CPU,CORE,SOCKET,NODE"})
    bounded("lscpu", ["lscpu", "-p=CPU,CORE,SOCKET,NODE"], KIT, 20,
            capture=RUN / "lscpu.csv")

    runtime_before = runtime_snapshot("before")
    bounded("probe-build", ["mpicc", "-O2", "-Wall", "-Wextra", "-Werror", KIT / "affinity_probe.c",
                                  "-o", RUN / "affinity_probe"], KIT, 45)
    bounded("probe-binary-ldd", ["ldd", RUN / "affinity_probe"], KIT, 20)
    save(RUN / "probe-binary.json", {"source_sha256": hashlib.sha256((KIT / "affinity_probe.c").read_bytes()).hexdigest(),
                                     "binary_sha256": hashlib.sha256((RUN / "affinity_probe").read_bytes()).hexdigest()})
    run_probe("default", [])
    bounded("rankfile-build", ["python3", KIT / "build_rankfiles.py", RUN / "probes/default",
                                     RUN / "lscpu.csv", RUN / "mapping"], KIT, 30)
    run_probe("identity", ["--map-by", f"rankfile:file={RUN / 'mapping/identity.rankfile'}", "--bind-to", "core"])
    run_probe("candidate", ["--map-by", f"rankfile:file={RUN / 'mapping/candidate.rankfile'}", "--bind-to", "core"])
    bounded("rankmap-validation", ["python3", KIT / "validate_rankmaps.py", RUN / "probes/default",
                                         RUN / "probes/identity", RUN / "probes/candidate",
                                         RUN / "mapping/mapping-plan.json"], KIT, 30,
            capture=RUN / "rankmap-validation.json")
    if not json.loads((RUN / "rankmap-validation.json").read_text()).get("passed"):
        raise ValueError("native rank map gate did not pass")

    # Evidence-based minimum solver/copy windows for every remaining arm are
    # protected before each arm starts. Per-arm timeout remains a hard failure,
    # not permission to accept partial output.
    results = []
    for index, label in enumerate(ARM_ORDER):
        result = run_arm(index, "identity" if "default" in label else "candidate")
        results.append(result)
        save(RUN / "partial-results.json", {"arms": results, "completed_arms": [r["arm"] for r in results],
                                            "matched_comparison_complete": False})

    runtime_after = runtime_snapshot("after")
    runtime_same = runtime_before["tools"] == runtime_after["tools"] and runtime_before["libraries"] == runtime_after["libraries"]
    if not runtime_same:
        raise ValueError("solver executable/shared-library identity changed during the short ABBA screen")
    bounded("source-tree-unchanged", ["python3", KIT / "seal_tree.py", "compare", SOURCE,
                                               RUN / "source-tree-before.json", RUN / "source-tree-after.json"], KIT, 80)
    source_after_record = json.loads((RUN / "source-tree-after.json").read_text())
    source_fields_after = field_seal_from_manifest(SOURCE, source_after_record["manifest"])
    if source_fields_after != field_seal:
        raise ValueError("initialized source fields changed during the run")
    bounded("payload-hash-after", ["sha256sum", "-c", "payload-sha256.txt"], KIT, 40)
    control = [r for r in results if r["mapping"] == "identity"]
    candidate = [r for r in results if r["mapping"] == "candidate"]
    control_mean = statistics.mean(r["mean_seconds_per_step"] for r in control)
    candidate_mean = statistics.mean(r["mean_seconds_per_step"] for r in candidate)
    all_cd_equal = all(r["Cd_by_step"] == results[0]["Cd_by_step"] for r in results[1:])
    comparison = {"passed": True, "scored_result": False, "job_id": job, "hostname": socket.getfqdn(),
                  "arms": results, "control_mean_seconds_per_step": control_mean,
                  "candidate_mean_seconds_per_step": candidate_mean,
                  "candidate_vs_control_percent": 100.0 * (candidate_mean / control_mean - 1.0),
                  "control_arm_means_seconds_per_step": [r["mean_seconds_per_step"] for r in control],
                  "candidate_arm_means_seconds_per_step": [r["mean_seconds_per_step"] for r in candidate],
                  "Cd_trajectories_exactly_equal": all_cd_equal,
                  "runtime_identity_stable": runtime_same, "source_tree_unchanged": True,
                  "source_initialization_field_seal_unchanged": True, "rank_mapping_preflight": "exact native post-MPI CPU/NUMA masks passed",
                  "limitations": [f"{STEPS} solver steps per arm; {STEPS - 1} timed intervals per arm; no full 150-step result.",
                                  "One allocation and one ABBA cycle are a screening signal, not independent confirmation.",
                                  "The graph cut is a face-count proxy, not measured memory traffic.",
                                  "A favorable short result must be confirmed by a separately reviewed full run."]}
    save(RUN / "comparison.json", comparison)
    save(RUN / "final-status.json", {"passed": True, "completed_arms": list(ARM_ORDER),
                                     "scored_result": False, "terminal": "IRIS_GRAPHMAP_ABBA14_REVIEWED"})
    print("IRIS_GRAPHMAP_ABBA14_REVIEWED_NON_SCORED")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Preserve a concise terminal record but keep the job nonzero so that
        # incomplete native evidence cannot be mistaken for a measurement.
        message = {"passed": False, "exception_type": type(exc).__name__, "message": str(exc),
                   "utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        try:
            if "RUN" in globals() and RUN.exists():
                save(RUN / "terminal-error.json", message)
        finally:
            print(json.dumps(message, sort_keys=True), file=sys.stderr)
        raise
