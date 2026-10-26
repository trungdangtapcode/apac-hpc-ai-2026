#!/usr/bin/env python3
"""Offline gates and evidence snapshots for the native Iris N56 initialization."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

FIELDS = ("U", "p", "k", "omega", "nut", "nuTilda")
EXPECTED_CELLS = 65334765
CUT_JOB = "2294040"
FATAL = re.compile(r"FOAM FATAL|MPI_ABORT|FATAL ERROR", re.I)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(2 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_source(kit: Path, case: Path) -> dict:
    pins = json.loads((kit / "source-pins.json").read_text())["files"]
    mismatches = []
    input_hashes = {}
    for relative, expected in sorted(pins.items()):
        source = kit / "payload-case" / relative
        if not source.is_file() or source.is_symlink() or sha256(source) != expected:
            mismatches.append("kit/payload-case/" + relative)
            continue
        input_hashes[relative] = {"bytes": source.stat().st_size, "sha256": expected}

        target = case / relative
        if relative == "Allrun":
            if target.exists() or target.is_symlink():
                mismatches.append("unexpected operational Allrun")
        elif relative == "system/include/caseDefinition":
            original_text = source.read_text()
            expected_text = re.sub(r"(?m)^nCores .*", "nCores              56;", original_text)
            expected_text = re.sub(r"(?m)^nHierarchical .*", "nHierarchical       (7 4 2);", expected_text)
            expected_text = re.sub(r"(?m)^decompositionMethod .*", "decompositionMethod scotch;", expected_text)
            expected_text = re.sub(
                r"(?m)(^nHierarchical )",
                lambda match: "// Not the scotch cut. Required so decomposeParDict $nHierarchical expands.\n" + match.group(1),
                expected_text)
            if not target.is_file() or target.is_symlink() or target.read_bytes() != expected_text.encode():
                mismatches.append(relative + " differs from exact organizer 13.1 operational edits")
        elif relative == "system/controlDict":
            expected_operational = kit / "payload-case/system/controlDict.noWrite"
            if not target.is_file() or target.is_symlink() or sha256(target) != sha256(expected_operational):
                mismatches.append(relative + " differs from pinned controlDict.noWrite")
        elif relative == "system/fvSolution":
            expected_operational = kit / "payload-case/system/fvSolution.fixedIter"
            if not target.is_file() or target.is_symlink() or sha256(target) != sha256(expected_operational):
                mismatches.append(relative + " differs from pinned fvSolution.fixedIter")
        else:
            if not target.is_file() or target.is_symlink() or sha256(target) != expected:
                mismatches.append(relative)
    if len(pins) != 41 or mismatches:
        raise ValueError("owned case source gate failed: " + ", ".join(mismatches or [f"expected 41 source pins, got {len(pins)}"]))
    return {"passed": True, "pinned_files": len(pins), "input_hashes": input_hashes,
            "operational_changes": ["Allrun absent", "caseDefinition N=56/scotch/(7 4 2)",
                                    "controlDict equals pinned noWrite variant", "fvSolution equals pinned fixedIter variant"]}


def gate_cut(cut_root: Path, accounting_path: Path) -> dict:
    validation_path = cut_root / "runs/2294040-cut-validation.json"
    validation = json.loads(validation_path.read_text())
    if not (validation.get("passed") is True and validation.get("ranks") == 56
            and validation.get("mesh_cells") == EXPECTED_CELLS
            and validation.get("method") == "scotch"
            and validation.get("restored_zero_fields") == 336):
        raise ValueError("2294040 native cut-validation gate failed")
    cut_log = (cut_root / "runs/2294040.out").read_text(errors="replace")
    if "TRIPLEU_IRIS_SCOTCH56_CUT_NATIVE_PASS" not in cut_log:
        raise ValueError("2294040 cut stdout lacks native pass marker")
    source_after = json.loads((cut_root / "runs/2294040-source-after.json").read_text())
    if source_after.get("passed") is not True or source_after.get("all_source_hashes_match") is not True:
        raise ValueError("2294040 source-after gate failed")
    accounting = accounting_path.read_text(errors="replace")
    rows = [line.strip().split("|") for line in accounting.splitlines() if line.strip()]
    root_rows = [row for row in rows if row and row[0] == CUT_JOB]
    if len(root_rows) != 1 or len(root_rows[0]) < 5:
        raise ValueError("sacct output lacks exactly one root row for job 2294040")
    row = root_rows[0]
    if row[1] != "COMPLETED" or row[2] != "0:0" or row[4] != "56":
        raise ValueError("2294040 accounting must be COMPLETED, exit 0:0, allocated 56 CPUs")
    return {"passed": True, "job_id": CUT_JOB, "state": row[1], "exit_code": row[2],
            "elapsed": row[3], "allocated_cpus": int(row[4]),
            "cut_validation": str(validation_path), "mesh_cells": validation["mesh_cells"],
            "restored_zero_fields": validation["restored_zero_fields"]}


def field_snapshot(case: Path) -> dict:
    directories = {p.name for p in case.glob("processor*") if p.is_dir() and not p.is_symlink()}
    expected = {f"processor{i}" for i in range(56)}
    if directories != expected:
        raise ValueError(f"expected exactly processor0..processor55, found {len(directories)} directories")
    fields = {}
    for rank in range(56):
        for field in FIELDS:
            path = case / f"processor{rank}" / "0" / field
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"missing or symlinked time-zero field: {path}")
            fields[f"processor{rank}/0/{field}"] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    if len(fields) != 336:
        raise ValueError(f"expected 336 time-zero field seals, got {len(fields)}")
    return {"passed": True, "scope": "Byte seals of restored time-zero fields; initialization may legitimately change them.",
            "field_count": len(fields), "fields": fields}


def check_probe(run_dir: Path, job_id: str) -> dict:
    probe_path = run_dir / f"{job_id}-mpi-hostnames.log"
    probe = probe_path.read_text(errors="replace")
    observations = []
    for line in probe.splitlines():
        match = re.match(r"^INIT_PROBE\t(\d+)\t([^\s]+)\s*$", line)
        if match:
            observations.append((int(match.group(1)), match.group(2)))
    observed_ranks = [rank for rank, _ in observations]
    hosts = {host for _, host in observations}
    if len(observations) != 56 or set(observed_ranks) != set(range(56)) or len(hosts) != 1:
        raise ValueError(f"MPI hostname probe must show each rank 0..55 exactly once on one node; found {len(observations)} records")
    if "INIT_PROBE_RETURN_CODE=0" not in probe:
        raise ValueError("MPI hostname probe did not return successfully")
    return {"passed": True, "ranks": len(observations), "hosts": sorted(hosts)}


def check_stage_logs(run_dir: Path, job_id: str) -> dict:
    stages = ("renumberMesh", "potentialFoam", "applyBoundaryLayer")
    summaries = {}
    for stage in stages:
        path = run_dir / f"{job_id}-{stage}.log"
        text = path.read_text(errors="replace")
        if "INIT_STAGE_RETURN_CODE=0" not in text:
            raise ValueError(f"{stage}: success sentinel missing")
        if not re.search(r"(?m)^\s*End\s*$", text):
            raise ValueError(f"{stage}: native End marker missing")
        if FATAL.search(text) or re.search(r"died from signal", text, re.I):
            raise ValueError(f"{stage}: fatal marker found")
        if "OPENFOAM=2512" not in text or "scalar=64" not in text:
            raise ValueError(f"{stage}: expected native OpenFOAM 2512 and scalar=64 log metadata")
        if not re.search(r"(?m)^nProcs\s*:\s*56\s*$", text):
            raise ValueError(f"{stage}: log does not report exactly 56 OpenFOAM processes")
        flags = {
            "renumberMesh": r"Exec\s*:\s*renumberMesh\s+-constant\s+-overwrite\s+-parallel\s*$",
            "potentialFoam": r"Exec\s*:\s*potentialFoam\s+-initialiseUBCs\s+-parallel\s*$",
            "applyBoundaryLayer": r"Exec\s*:\s*applyBoundaryLayer\s+-ybl\s+0\.0450244\s+-parallel\s*$",
        }[stage]
        if not re.search(r"(?m)^.*" + flags, text):
            raise ValueError(f"{stage}: actual command and organizer arguments not found in log")
        summaries[stage] = {"log": str(path), "end_marker": True, "openfoam": 2512,
                            "scalar_bits": 64, "nprocs": 56, "fatal_markers": 0}
    probe = check_probe(run_dir, job_id)
    return {"passed": True, "stages": summaries, "mpi_probe": probe}

def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    gate = sub.add_parser("cut-gate")
    gate.add_argument("--cut-root", type=Path, required=True)
    gate.add_argument("--accounting", type=Path, required=True)
    source = sub.add_parser("source")
    source.add_argument("--kit", type=Path, required=True)
    source.add_argument("--case", type=Path, required=True)
    source.add_argument("--output", type=Path)
    fields = sub.add_parser("fields")
    fields.add_argument("--case", type=Path, required=True)
    fields.add_argument("--output", type=Path, required=True)
    probe = sub.add_parser("probe")
    probe.add_argument("--run-dir", type=Path, required=True)
    probe.add_argument("--job-id", required=True)
    logs = sub.add_parser("logs")
    logs.add_argument("--run-dir", type=Path, required=True)
    logs.add_argument("--job-id", required=True)
    args = parser.parse_args()
    if args.command == "cut-gate":
        result = gate_cut(args.cut_root, args.accounting)
    elif args.command == "source":
        result = check_source(args.kit, args.case)
        if args.output:
            args.output.write_text(json.dumps(result, indent=2) + "\n")
    elif args.command == "fields":
        result = field_snapshot(args.case)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    elif args.command == "probe":
        result = check_probe(args.run_dir, args.job_id)
    else:
        result = check_stage_logs(args.run_dir, args.job_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
