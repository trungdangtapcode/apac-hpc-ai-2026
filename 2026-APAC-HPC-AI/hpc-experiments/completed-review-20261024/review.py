#!/usr/bin/env python3
"""Offline integrity and native-result replay for the 2026-10-24 PBS collection."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "collected"
SRC = ROOT.parent


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path):
    return json.loads(path.read_text())


def resource_summary(path):
    txt = path.read_text(errors="replace")
    def number(pattern):
        m = re.search(pattern, txt)
        return float(m.group(1)) if m else None
    wall = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([0-9:]+(?:\.[0-9]+)?)", txt)
    wall_seconds = None
    if wall:
        bits = wall.group(1).split(":")
        wall_seconds = sum(float(v) * (60 ** i) for i, v in enumerate(reversed(bits)))
    return {"wall_seconds": wall_seconds,
            "reported_user_seconds": number(r"User time \(seconds\): ([0-9.]+)"),
            "reported_system_seconds": number(r"System time \(seconds\): ([0-9.]+)")}


def main():
    manifest = load_json(DATA / "collection.json")
    checks = []
    for rel, expected in manifest["files"].items():
        p = DATA / rel
        assert p.is_file(), rel
        actual = {"sha256": sha256(p), "bytes": p.stat().st_size}
        assert actual == expected, (rel, actual, expected)
        checks.append(rel)

    terminal = manifest['terminal']
    assert {j: v['Exit_status'] for j,v in terminal.items()} == {'25940700.pbs101':0,'25943865.pbs101':0,'25947168.pbs101':1}
    assert all(v['job_state']=='F' and str(v['project'])=='59000042' for v in terminal.values())
    rdir = DATA / "25940700/runs/25940700"
    validator_path = SRC / "nscc-cpu-four-node-confirm-20261023/payload/validate-solve.py"
    spec = importlib.util.spec_from_file_location("validate_solve", validator_path)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    case = rdir / "case"
    replay = validator.validate(
        (case / "logFiles/simpleFoam.log").read_text(errors="replace"),
        (case / "postProcessing/solverInfo/0/solverInfo.dat").read_text(errors="replace"),
        (case / "postProcessing/wallClockTimeStatistics/0/wallClockTime.dat").read_text(errors="replace"),
        (case / "postProcessing/forceCoeffsAll/0/coefficient.dat").read_text(errors="replace"),
    )
    recorded = load_json(rdir / "native-solver-review.json")
    assert replay == recorded
    assert load_json(rdir / "native-solver-review.stdout.json") == replay

    pre = load_json(rdir / "initialized-zero-fields-before-solve.json")
    post = load_json(rdir / "initialized-zero-fields-after-solve.json")
    assert pre["files"] == post["files"]
    assert pre["rank_count"] == post["rank_count"] == 512
    assert pre["file_count"] == post["file_count"]
    source_before = load_json(rdir / "source-validation-before.json")
    source_after = load_json(rdir / "source-validation-after.json")
    assert source_before == source_after
    command_rows = load_json(rdir / "command-return-codes.json")
    assert all(x["return_code"] == 0 for x in command_rows)
    stage_checks = {}
    for name in ("10_decomposePar", "20_renumberMesh", "30_potentialFoam",
                 "40_applyBoundaryLayer"):
        log = (rdir / "logs" / (name + ".log")).read_text(errors="replace")
        stage_checks[name] = {"end_marker": bool(re.search(r"(?m)^End\s*$", log)),
                              "fatal_markers": len(re.findall(r"FOAM FATAL|FATAL ERROR|MPI_ABORT", log, re.I)),
                              "warning_lines": [x.strip() for x in log.splitlines()
                                                if "Warning" in x or "WARNING" in x]}
        assert stage_checks[name]["end_marker"] and not stage_checks[name]["fatal_markers"]
    resource_checks = {name: resource_summary(rdir / "logs" / (name + ".resource.txt"))
                       for name in ("decomposePar", "restore0Dir", "renumberMesh",
                                    "potentialFoam", "applyBoundaryLayer", "simpleFoam")}
    rankprobe = [json.loads(x) for x in (rdir / "rank-probe.jsonl").read_text().splitlines() if x]
    rank_counts = {}
    for row in rankprobe:
        host = row["host"]
        rank_counts[host] = rank_counts.get(host, 0) + 1

    rank_check = subprocess.run([sys.executable, str(SRC / 'nscc-cpu-four-node-confirm-20261023/payload/validate-rank-probe.py'), str(rdir/'rank-probe.jsonl'), '--nodefile', str(rdir/'pbs-nodefile.txt')], capture_output=True, text=True, check=True)
    assert json.loads(rank_check.stdout) == load_json(rdir/'rank-probe-validation.json')
    four = DATA / "25943865/runs/25943865"
    probe_validator = SRC / "nscc-cpu-mpi-reorder-preflight-20261023/payload/validate-probe.py"
    proc = subprocess.run([sys.executable, str(probe_validator),
                           str(four / "logs/mpi_identity.stdout.txt"),
                           str(four / "logs/mpi_candidate.stdout.txt"),
                           str(four / "pbs-nodefile.txt")], text=True, capture_output=True)
    four_result = {"return_code": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    if proc.returncode == 0:
        four_result["validator_json"] = json.loads(proc.stdout)
        four_result["replay_sysfs_scope"] = "The offline CLI reads this machine's /sys for CPU IDs; the captured mapping-validation.json produced on the allocated compute node is the authoritative placement record."
    four_result["captured_compute_node_validation"] = load_json(four / "mapping-validation.json")

    large = DATA / "25947168/runs/25947168"
    large_rc = load_json(large / "command-return-codes.json")
    stderr = (large / "logs/mpi_identity.stderr.txt").read_text(errors="replace")
    topology_errors = re.findall(r"rank (\d+) could not prove single-CPU package/core/NUMA topology", stderr)
    assert large_rc[-1]["stage"] == "mpi_identity" and large_rc[-1]["return_code"] != 0
    assert not any(x["stage"] == "mpi_candidate" for x in large_rc)
    assert not (large / "candidate").exists() or not any((large / "candidate").iterdir())

    old = load_json(SRC / "four-node-review-20261023/review.json")["runs"]["25921488.pbs101"]["native_simplefoam"]
    comparison = {}
    for key, old_key in (("average_seconds_step_native", "average_step_seconds"),
                         ("median_seconds_step", "median_seconds"),
                         ("p95_seconds_linear_interpolation", "p95_seconds_linear_interpolation"),
                         ("max_seconds_step", "max_seconds")):
        comparison[key] = {"new": replay[key], "prior": old[old_key],
                           "difference_new_minus_prior": replay[key] - old[old_key]}
    result = {
        "review_scope": "Read-only replay of the collected native artifacts; no scheduler or budget actions.",
        "terminal_scheduler_evidence": terminal,
        "collection_integrity": {"manifest_files_verified": len(checks), "passed": True},
        "confirmation_25940700": {
            "native_validator_replay_matches_recorded_json": True,
            "source_manifest_before_equals_after": True,
            "pre_solver_and_post_solver_zero_field_seals_match": True,
            "pre_seal_file_count": pre["file_count"], "rank_count": pre["rank_count"],
            "stage_checks": stage_checks,
            "stage_resource_records": resource_checks,
            "rank_probe_records": len(rankprobe), "rank_probe_host_counts": rank_counts,
            "solver": {k: replay[k] for k in ("steps", "timed_samples", "average_seconds_step_native",
                       "median_seconds_step", "p95_seconds_linear_interpolation", "max_seconds_step",
                       "max_time", "top_five_steps_descending", "iqr_outliers", "final_Cd",
                       "native_minimum_sample_count_for_2pct_95pct_target", "native_warning_below_recommended_count")},
            "comparison_to_25921488": comparison,
        },
            "four_rank_25943865": four_result,
        "placement_512_25947168": {
            "last_executed_stage": large_rc[-1], "candidate_launched": any(x["stage"] == "mpi_candidate" for x in large_rc),
            "topology_gate_error_count_in_stderr": len(topology_errors),
            "topology_gate_example_ranks": [int(x) for x in topology_errors[:8]],
            "root_cause": "unresolved: the generic probe gate reports inability to prove single-CPU package/core/NUMA topology; retained outputs do not separate which component failed for each rank",
            "wrapper": load_json(large / "batch-lifecycle.json"),
        },
        "limits": ["The two solver observations are from separate allocations and do not form a controlled code-level speedup test.",
                   "No causal explanation for timing differences is supported by these artifacts.",
                   "The 512-rank mapping candidate did not launch; no candidate placement or solver result is claimed."]
    }
    (ROOT / "review.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"manifest_files_verified": len(checks), "solver_replay": replay["average_seconds_step_native"],
                      "four_rank_validator_rc": proc.returncode,
                      "512_topology_error_count": len(topology_errors)}, indent=2))


if __name__ == "__main__":
    main()
