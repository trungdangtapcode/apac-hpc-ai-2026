#!/usr/bin/env python3
"""Small local checks for graph-rank translation, map gates and output parsing."""
from __future__ import annotations

import json
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from review_short_output import review
import run as runner


KIT = pathlib.Path(__file__).resolve().parent


def probe_row(rank: int, cpu: int, numa: int, mode: str) -> dict:
    return {"mode": mode, "rank": rank, "size": 56, "host": "iris-test",
            "pre_mpi_init_errno": 0, "pre_cpus": [cpu], "post_mpi_init_errno": 0,
            "post_cpus": [cpu], "post_numa_nodes": [numa]}


def write_probe(root: pathlib.Path, mode: str, cpu_by_rank: dict[int, int], numa_by_rank: dict[int, int]) -> pathlib.Path:
    directory = root / mode
    directory.mkdir()
    for rank in range(56):
        (directory / f"rank-{rank:03}.json").write_text(json.dumps(probe_row(rank, cpu_by_rank[rank], numa_by_rank[rank], mode)))
    return directory


def check_rankfiles(root: pathlib.Path) -> None:
    cpus = {rank: 100 + 3 * rank for rank in range(56)}
    nodes = {rank: 0 if rank < 28 else 1 for rank in range(56)}
    default = write_probe(root, "default", cpus, nodes)
    lscpu = root / "lscpu.csv"
    lscpu.write_text("# CPU,CORE,SOCKET,NODE\n" + "".join(
        f"{cpus[r]},{r % 28},{r // 28},{nodes[r]}\n" for r in range(56)))
    mapping_dir = root / "mapping"
    subprocess.run([sys.executable, str(KIT / "build_rankfiles.py"), str(default), str(lscpu), str(mapping_dir)], check=True)
    plan = json.loads((mapping_dir / "mapping-plan.json").read_text())
    identity_text = (mapping_dir / "identity.rankfile").read_text().splitlines()
    if identity_text != [f"rank {r}=+n0 slot={r}" for r in range(56)]:
        raise AssertionError("identity rankfile must use global logical slot r")
    candidate_expected = {int(rank): int(row["cpu"]) for rank, row in plan["assignments"]["candidate"].items()}
    candidate_nodes = {rank: int(plan["assignments"]["candidate"][str(rank)]["numa"]) for rank in range(56)}
    identity = write_probe(root, "identity", cpus, nodes)
    candidate = write_probe(root, "candidate", candidate_expected, candidate_nodes)
    valid = subprocess.run([sys.executable, str(KIT / "validate_rankmaps.py"), str(default), str(identity),
                            str(candidate), str(mapping_dir / "mapping-plan.json")],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if valid.returncode:
        raise AssertionError(f"valid synthetic map rejected: {valid.stderr}")
    row = json.loads(valid.stdout)
    if not row.get("passed") or not row.get("default_equals_identity_rankfile"):
        raise AssertionError("map validator did not report passing controls")
    candidate_row = json.loads((candidate / "rank-000.json").read_text())
    candidate_row["post_cpus"] = [candidate_row["post_cpus"][0] + 1]
    (candidate / "rank-000.json").write_text(json.dumps(candidate_row))
    invalid = subprocess.run([sys.executable, str(KIT / "validate_rankmaps.py"), str(default), str(identity),
                              str(candidate), str(mapping_dir / "mapping-plan.json")],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if invalid.returncode == 0:
        raise AssertionError("map validator accepted a wrong candidate CPU")


def check_output_parser(root: pathlib.Path) -> None:
    arm = root / "arm"
    arm.mkdir()
    counts = {"Ux": 15, "Uy": 15, "Uz": 15, "p": 12, "k": 8, "omega": 8}
    lines = ["Build : _test OPENFOAM=2512 version=v2512", 'Arch : "LSB;scalar=64"',
             "nProcs : 56", "    (iris-test 56)"]
    for step in range(1, 15):
        lines.append(f"Time = {step}")
        for field, count in counts.items():
            lines.append(f"Solving for {field}, Initial residual = 1, Final residual = 0.01, No Iterations {count}")
        if step > 1:
            lines.append("Wall-clock time elapsed during the current time step = 1.25")
    lines.extend(["Average wall-clock time per time step = 1.25", "End"])
    (arm / "simpleFoam.log").write_text("\n".join(lines) + "\n")
    (arm / "solver.stderr").write_text("")
    (arm / "resource-time.log").write_text("Exit status: 0\nMaximum resident set size (kbytes): 1\n")
    wall = arm / "postProcessing/wallClockTimeStatistics/0"
    wall.mkdir(parents=True)
    (wall / "wallClockTime.dat").write_text("".join(f"{step} 0 1.25\n" for step in range(2, 15)))
    cd = arm / "postProcessing/forceCoeffsAll/0"
    cd.mkdir(parents=True)
    (cd / "coefficient.dat").write_text("".join(f"{step} 0.1 0.2 0.3\n" for step in range(1, 15)))
    if review(arm)["timed_intervals"] != 13:
        raise AssertionError("native parser did not retain all 13 timing samples")
    (arm / "simpleFoam.log").write_text("\n".join(lines[:-3] + lines[-2:]) + "\n")
    try:
        review(arm)
    except (ValueError, AssertionError):
        pass
    else:
        raise AssertionError("native parser accepted a log with missing solver timing evidence")


def check_field_seals(root: pathlib.Path) -> None:
    case = root / "field-case"
    manifest = {"files": {}}
    for rank in range(56):
        for name in ("U", "p", "k", "omega", "nut", "nuTilda"):
            rel = f"processor{rank}/0/{name}"
            path = case / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            data = f"field:{rank}:{name}\n".encode()
            path.write_bytes(data)
            manifest["files"][rel] = hashlib.sha256(data).hexdigest()
    source_seal = runner.field_seal_from_manifest(case, manifest)
    clone_seal = runner.field_seal_from_manifest(case, manifest)
    post_seal = runner.field_seal_from_case_time0(case)
    if source_seal != clone_seal or source_seal != post_seal:
        raise AssertionError("pre-copy, clone, and post-solver time-zero seals must share one canonical schema")
    changed = case / "processor17/0/k"
    changed.write_bytes(changed.read_bytes() + b"changed\n")
    if runner.field_seal_from_case_time0(case) == source_seal:
        raise AssertionError("time-zero seal failed to detect an edited field")


def check_graph_boundary_provenance() -> None:
    candidate = json.loads((KIT / "candidate.json").read_text())
    graph = json.loads((KIT / "processor-interface-graphs.json").read_text())
    boundaries = graph["orders"]["zyx"]["boundary_sha256"]
    manifest = {"files": {f"processor{rank}/constant/polyMesh/boundary": boundaries[str(rank)]
                           for rank in range(56)}}
    proof = runner.verify_frozen_graph_boundaries(manifest)
    if proof["boundary_sha256"] != boundaries or proof["boundary_files"] != 56:
        raise AssertionError("candidate provenance check did not bind all source boundaries")
    manifest["files"]["processor27/constant/polyMesh/boundary"] = "0" * 64
    try:
        runner.verify_frozen_graph_boundaries(manifest)
    except ValueError:
        pass
    else:
        raise AssertionError("graph provenance gate accepted a changed processor boundary")


def check_accepted_source_gate() -> None:
    accepted = json.loads((KIT / "accepted-source-manifest.json").read_text())
    if runner.verify_accepted_source(accepted)["regular_files"] != 1040:
        raise AssertionError("reviewed 2294262 source manifest did not verify")
    altered = {"files": dict(accepted["files"]), "symlinks": dict(accepted["symlinks"])}
    altered["files"]["processor0/0/U"] = "0" * 64
    try:
        runner.verify_accepted_source(altered)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted-source gate tolerated a changed source hash")


def ready_pinned_case(path: pathlib.Path) -> None:
    shutil.copytree(KIT / "payload-case", path, symlinks=True)
    cdef = path / "system/include/caseDefinition"
    text = cdef.read_text()
    text, n = re.subn(r"(?m)^nCores .*?$", "nCores              56;", text)
    if n != 1:
        raise AssertionError("case fixture lacks one nCores line")
    text, n = re.subn(r"(?m)^nHierarchical .*?$", "nHierarchical       (7 4 2);", text)
    if n != 1:
        raise AssertionError("case fixture lacks one nHierarchical line")
    cdef.write_text(text)
    decomp = path / "system/decomposeParDict"
    text, n = re.subn(r"(?m)^([ \t]+order[ \t]+)xyz;", r"\g<1>zyx;", decomp.read_text())
    if n != 1:
        raise AssertionError("case fixture lacks one xyz order line")
    decomp.write_text(text)
    (path / "Allrun").unlink(missing_ok=True)


def check_configure(root: pathlib.Path) -> None:
    good = root / "case-good"
    ready_pinned_case(good)
    control = good / "system/controlDict"
    before = control.read_bytes()
    expected, count = re.subn(rb"(?m)^endTime[ \t]+[^;\n]+;[^\n]*$", b"endTime 14;", before)
    if count != 1:
        raise AssertionError("case fixture lacks exactly one endTime control")
    result = runner.configure(good)
    if not result["passed"] or control.read_bytes() != expected:
        raise AssertionError("endTime-only configuration failed its positive fixture")
    bad = root / "case-bad"
    ready_pinned_case(bad)
    (bad / "system/fvSolution").write_bytes(b"altered physics/iteration controls\n")
    try:
        runner.configure(bad)
    except (AssertionError, ValueError):
        pass
    else:
        raise AssertionError("configuration gate accepted a changed fvSolution")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="iris-graphmap-offline-") as name:
        root = pathlib.Path(name)
        check_rankfiles(root)
        check_output_parser(root)
        check_field_seals(root)
        check_configure(root)
        check_graph_boundary_provenance()
        check_accepted_source_gate()
    print("offline checks passed: rankfile translation and negative map, 14-step parser and missing sample, canonical field seals and mutation detection, endTime-only configuration and physics negative, graph boundary provenance, and reviewed 1,040-file source acceptance")


if __name__ == "__main__":
    main()
