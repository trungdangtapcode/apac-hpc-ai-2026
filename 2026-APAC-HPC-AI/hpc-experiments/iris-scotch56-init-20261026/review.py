#!/usr/bin/env python3
"""Offline acceptance and rejection checks for the Iris initialization gates."""
from __future__ import annotations
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("verify_init", HERE / "verify-init.py")
verify_init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_init)


def expect_reject(label, function):
    try:
        function()
    except (AssertionError, OSError, ValueError, KeyError):
        return
    raise AssertionError(label + " was incorrectly accepted")


def main():
    with tempfile.TemporaryDirectory(prefix="iris-init-review-") as temp:
        root = Path(temp)
        kit = root / "init-kit"
        case = root / "artifacts/ready-N56-scotch"
        runs = root / "runs"
        kit.mkdir()
        runs.mkdir(parents=True)
        shutil.copytree(HERE / "payload-case", kit / "payload-case")
        shutil.copy2(HERE / "source-pins.json", kit / "source-pins.json")

        # Simulate the documented, expected cut-time operations on an owned working copy.
        shutil.copytree(kit / "payload-case", case)
        (case / "Allrun").unlink()
        shutil.copy2(case / "system/controlDict.noWrite", case / "system/controlDict")
        shutil.copy2(case / "system/fvSolution.fixedIter", case / "system/fvSolution")
        config = case / "system/include/caseDefinition"
        text = config.read_text()
        import re
        text = re.sub(r"(?m)^nCores .*", "nCores              56;", text)
        text = re.sub(r"(?m)^nHierarchical .*", "nHierarchical       (7 4 2);", text)
        text = re.sub(r"(?m)^decompositionMethod .*", "decompositionMethod scotch;", text)
        text = re.sub(r"(?m)(^nHierarchical )", lambda match: "// Not the scotch cut. Required so decomposeParDict $nHierarchical expands.\n" + match.group(1), text)
        config.write_text(text)
        assert verify_init.check_source(kit, case)["passed"]
        (case / "constant/transportProperties").write_text("tampered\n")
        expect_reject("tampered source", lambda: verify_init.check_source(kit, case))
        shutil.copy2(kit / "payload-case/constant/transportProperties", case / "constant/transportProperties")

        # Exact 56-rank directory and 336-field inventory; changed post-init bytes are valid evidence.
        for rank in range(56):
            rank_dir = case / f"processor{rank}/0"
            rank_dir.mkdir(parents=True)
            for field in verify_init.FIELDS:
                (rank_dir / field).write_text(f"rank={rank} field={field} initial\n")
        before = verify_init.field_snapshot(case)
        (case / "processor0/0/U").write_text("post-initialization value\n")
        after = verify_init.field_snapshot(case)
        assert before["field_count"] == after["field_count"] == 336
        assert before["fields"]["processor0/0/U"]["sha256"] != after["fields"]["processor0/0/U"]["sha256"]
        shutil.rmtree(case / "processor55")
        expect_reject("missing processor rank", lambda: verify_init.field_snapshot(case))

        # Native completion gate accepts only passed evidence and completed root accounting.
        cut = root / "cut"
        (cut / "runs").mkdir(parents=True)
        validation = {"passed": True, "ranks": 56, "mesh_cells": verify_init.EXPECTED_CELLS,
                      "method": "scotch", "restored_zero_fields": 336}
        (cut / "runs/2294040-cut-validation.json").write_text(json.dumps(validation))
        (cut / "runs/2294040.out").write_text("TRIPLEU_IRIS_SCOTCH56_CUT_NATIVE_PASS\n")
        (cut / "runs/2294040-source-after.json").write_text(json.dumps({"passed": True, "all_source_hashes_match": True}))
        accounting = root / "accounting.txt"
        accounting.write_text("2294040|COMPLETED|0:0|00:04:27|56|iris005|\n2294040.batch|COMPLETED|0:0|00:04:27|56|iris005|32781460K\n")
        assert verify_init.gate_cut(cut, accounting)["passed"]
        accounting.write_text("2294040|FAILED|1:0|00:04:27|56|iris005|\n")
        expect_reject("failed cut accounting", lambda: verify_init.gate_cut(cut, accounting))
        accounting.write_text("2294040|COMPLETED|0:0|00:04:27|56|iris005|\n")
        validation["passed"] = False
        (cut / "runs/2294040-cut-validation.json").write_text(json.dumps(validation))
        expect_reject("failed native cut validation", lambda: verify_init.gate_cut(cut, accounting))

        # MPI gate requires every rank exactly once on the same allocated node.
        probe = runs / "job-mpi-hostnames.log"
        probe.write_text("".join(f"INIT_PROBE\t{rank}\tiris005\n" for rank in range(56)) + "INIT_PROBE_RETURN_CODE=0\n")
        assert verify_init.check_probe(runs, "job")["passed"]
        probe.write_text("".join(f"INIT_PROBE\t{rank}\tiris005\n" for rank in range(55)) + "INIT_PROBE_RETURN_CODE=0\n")
        expect_reject("incomplete MPI rank set", lambda: verify_init.check_probe(runs, "job"))
        probe.write_text("".join(f"INIT_PROBE\t{rank}\tiris005\n" for rank in range(56)) + "INIT_PROBE\t0\tiris005\nINIT_PROBE_RETURN_CODE=0\n")
        expect_reject("duplicate MPI rank", lambda: verify_init.check_probe(runs, "job"))

        # Each mandatory native stage needs its own End, return sentinel, and no fatal marker.
        probe.write_text("".join(f"INIT_PROBE\t{rank}\tiris005\n" for rank in range(56)) + "INIT_PROBE_RETURN_CODE=0\n")
        stage_commands = {
            "renumberMesh": "Exec   : renumberMesh -constant -overwrite -parallel",
            "potentialFoam": "Exec   : potentialFoam -initialiseUBCs -parallel",
            "applyBoundaryLayer": "Exec   : applyBoundaryLayer -ybl 0.0450244 -parallel",
        }
        for stage, command in stage_commands.items():
            (runs / f"job-{stage}.log").write_text(
                "OPENFOAM=2512\nscalar=64\nnProcs : 56\n" + command + "\nEnd\nINIT_STAGE_RETURN_CODE=0\n")
        assert verify_init.check_stage_logs(runs, "job")["passed"]
        (runs / "job-potentialFoam.log").write_text("FOAM FATAL ERROR\nEnd\nINIT_STAGE_RETURN_CODE=0\n")
        expect_reject("fatal native stage log", lambda: verify_init.check_stage_logs(runs, "job"))

    print("offline initialization review: PASS (acceptance and rejection gates exercised)")


if __name__ == "__main__":
    main()
