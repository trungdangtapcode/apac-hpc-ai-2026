#!/usr/bin/env python3
"""Independently replay retained output, transfer hashes, and telemetry for job 2294671.

This capture is terminal but incomplete as a four-arm comparison: X2 reached the
20-step output summary but its 720-second command returned 124; S2 was never run.
The script deliberately keeps that failed-arm state instead of upgrading the
printed X2 timing into a valid completed measurement.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
sys.path.insert(0, str(EXPERIMENT))

from native_output import review_native_output  # noqa: E402
from sampler import validate_sample_file  # noqa: E402


COLLECTION = json.loads((HERE / "collection.json").read_text())
COLLECTED = HERE / "collected"
JOB = str(COLLECTION["job_id"])
RUN = COLLECTED / "runs" / JOB
EXPECTED_COMMAND = [
    "mpirun", "-np", "56", "--report-bindings", "--display-map", "--",
    "simpleFoam", "-parallel",
]
EXPECTED_ITERS = {"Ux": 15, "Uy": 15, "Uz": 15, "p": 12, "k": 8, "omega": 8}
ARM_ORDER = ["S1-scotch", "X1-hierarchical-xyz", "X2-hierarchical-xyz", "S2-scotch"]
SOLVER_ARMS = ARM_ORDER[:3]
FATAL_PATTERN = re.compile(
    r"FOAM FATAL|FOAM ERROR|MPI_ABORT|died from signal|\bSIGFPE\b|"
    r"floating point exception occurred|core dumped",
    re.IGNORECASE,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(2 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_resource(path: Path) -> dict:
    text = path.read_text(errors="replace")
    values = {}
    for key in (
        "User time (seconds)", "System time (seconds)",
        "Percent of CPU this job got", "Elapsed (wall clock) time (h:mm:ss or m:ss)",
        "Maximum resident set size (kbytes)", "Major (requiring I/O) page faults",
        "Minor (reclaiming a frame) page faults", "Voluntary context switches",
        "Involuntary context switches", "Swaps", "File system inputs",
        "File system outputs", "Exit status",
    ):
        match = re.search(r"^\s*" + re.escape(key) + r":\s*(.+)$", text, re.MULTILINE)
        if match:
            values[key] = match.group(1).strip()
    return {"raw_fields": values, "text_bytes": len(text.encode())}


def parse_partial_native_output(arm_dir: Path) -> dict:
    """Apply the native-output gates while retaining a nonzero command status."""
    log = (arm_dir / "simpleFoam.log").read_text(errors="replace")
    resources = (arm_dir / "resource-time.log").read_text(errors="replace")
    assert "OPENFOAM=2512" in log and "scalar=64" in log
    assert re.search(r"^End\s*$", log, re.MULTILINE), "native End marker absent"
    assert not FATAL_PATTERN.search(log + "\n" + resources), "native fatal marker found"
    assert re.search(r"^nProcs\s*:\s*56\s*$", log, re.MULTILINE)
    host_rows = re.findall(r"\((iris\S+)\s+56\)", log)
    assert host_rows, "native log host/rank line missing"
    steps = [int(value) for value in re.findall(r"^Time = (\d+)\s*$", log, re.MULTILINE)]
    assert steps == list(range(1, 21)), "expected printed steps 1..20"
    timings = [float(value) for value in re.findall(
        r"Wall-clock time elapsed during the current time step = ([\deE.+-]+)", log
    )]
    assert len(timings) == 19 and all(math.isfinite(value) and value > 0 for value in timings)
    average = re.search(r"Average wall-clock time per time step\s*=\s*([\deE.+-]+)", log)
    assert average and abs(statistics.mean(timings) - float(average.group(1))) < 1e-9
    wall_path = arm_dir / "postProcessing/wallClockTimeStatistics/0/wallClockTime.dat"
    wall_rows = [list(map(float, line.split())) for line in wall_path.read_text().splitlines()
                 if line.strip() and not line.lstrip().startswith("#")]
    assert [int(row[0]) for row in wall_rows] == list(range(2, 21))
    assert len(wall_rows) == 19 and all(math.isfinite(value) for row in wall_rows for value in row)
    assert all(abs(step_time - wall_row[2]) < 1e-8 for step_time, wall_row in zip(timings, wall_rows))
    counts = {}
    for field, count in re.findall(r"Solving for (\w+),.*?No Iterations (\d+)", log):
        counts.setdefault(field, []).append(int(count))
    assert set(counts) == set(EXPECTED_ITERS)
    assert all(values == [EXPECTED_ITERS[field]] * 20 for field, values in counts.items())
    coeff_path = arm_dir / "postProcessing/forceCoeffsAll/0/coefficient.dat"
    coeff_rows = [list(map(float, line.split())) for line in coeff_path.read_text().splitlines()
                  if line.strip() and not line.lstrip().startswith("#")]
    assert len(coeff_rows) == 20 and [int(row[0]) for row in coeff_rows] == steps
    assert all(math.isfinite(value) for row in coeff_rows for value in row)
    # A return code of 124 means GNU time cannot validate solver resource usage;
    # the printed native rows above remain inspectable but are not a valid arm.
    return {
        "printed_native_structure_passed": True,
        "native_End_observed": True,
        "finalising_parallel_run_observed": bool(re.search(r"^Finalising parallel run\s*$", log, re.MULTILINE)),
        "steps_printed": len(steps),
        "intervals_printed": len(timings),
        "timings_seconds": timings,
        "mean_s_step": statistics.mean(timings),
        "median_s_step": statistics.median(timings),
        "maximum_s_step": max(timings),
        "native_average_matches_rows": True,
        "wall_time_table_matches_log": True,
        "fixed_iterations_match": counts,
        "force_coefficient_rows": coeff_rows,
        "host": host_rows[-1],
        "recommended_samples": re.findall(
            r"Minimum number of measured time steps[^\n]*", log
        ),
    }


def telemetry_summary(arm_dir: Path) -> dict:
    sample_path = arm_dir / "telemetry-samples.jsonl"
    validation = validate_sample_file(sample_path, optional=False)
    raw = sample_path.read_bytes()
    lines = raw.splitlines()
    # Ignore only a final unterminated JSONL record; preserve and report its count.
    dropped = 0
    if raw and not raw.endswith(b"\n"):
        lines = lines[:-1]
        dropped = 1
    samples = [json.loads(line) for line in lines if line.strip()]
    assert samples, f"no complete telemetry samples in {sample_path}"
    status_path = arm_dir / "telemetry-status.json"
    status = json.loads(status_path.read_text())
    assert status["sample_count"] == validation["sample_count"] == len(samples)
    start, end = samples[0], samples[-1]
    duration = end["timestamp_monotonic_seconds"] - start["timestamp_monotonic_seconds"]
    assert duration > 0

    def mem_range(key: str) -> dict:
        values = [sample["meminfo_kb"][key] / (1024 ** 2)
                  for sample in samples if key in sample.get("meminfo_kb", {})]
        return {"minimum_GiB": min(values), "maximum_GiB": max(values),
                "first_GiB": values[0], "last_GiB": values[-1]}

    counters_start = start["vmstat_pages_or_events"]
    counters_end = end["vmstat_pages_or_events"]
    selected = (
        "pgmajfault", "pgscan_direct", "pgscan_kswapd", "pgscan_file",
        "pgsteal_direct", "pgsteal_kswapd", "pgsteal_file", "numa_miss",
        "numa_pages_migrated", "pswpin", "pswpout",
    )
    deltas = {key: counters_end[key] - counters_start[key]
              for key in selected if key in counters_start and key in counters_end}
    frequencies = [sample["cpuinfo_frequency"]["median_mhz"] for sample in samples
                   if sample.get("cpuinfo_frequency", {}).get("median_mhz") is not None]
    assert frequencies
    pressure = {name: sum(bool(sample.get("pressure", {}).get(name, {}).get("available"))
                          for sample in samples) for name in ("cpu", "io", "memory")}
    collection_ms = [float(sample["collection_ms"]) for sample in samples]
    schedule_lag = [float(sample.get("schedule_lag_ms", 0.0)) for sample in samples]
    return {
        "scope": "Whole-node aggregate procfs; not per-process attribution or bandwidth.",
        "interval_seconds": status.get("interval_seconds"),
        "samples": len(samples),
        "trailing_incomplete_lines_ignored": dropped,
        "sample_bytes": validation["bytes"],
        "duration_seconds": duration,
        "utc_start": start["timestamp_utc"],
        "utc_end": end["timestamp_utc"],
        "memory": {key: mem_range(key) for key in
                   ("MemAvailable", "Active(anon)", "Cached", "Inactive(file)")
                   if key in start.get("meminfo_kb", {}) and key in end.get("meminfo_kb", {})},
        "counter_deltas": deltas,
        "counter_rates_per_second": {key: value / duration for key, value in deltas.items()},
        "swap_total_GiB_first": start["meminfo_kb"].get("SwapTotal", 0) / (1024 ** 2),
        "pressure_available_sample_counts": pressure,
        "cpu_frequency_sample_median_MHz": {
            "minimum": min(frequencies), "median": statistics.median(frequencies),
            "maximum": max(frequencies),
            "samples_at_3300MHz_approx": sum(abs(value - 3300.0) < 2.0 for value in frequencies),
            "sample_count": len(frequencies),
            "scope": "Each sample is a cross-CPU median of instantaneous /proc/cpuinfo readings.",
        },
        "per_cpu_frequency_readings_MHz": {
            "minimum": min(sample["cpuinfo_frequency"]["minimum_mhz"] for sample in samples),
            "maximum": max(sample["cpuinfo_frequency"]["maximum_mhz"] for sample in samples),
            "scope": "Instantaneous host readings across the 56 CPU entries; not sustained rank clocks.",
        },
        "sample_collection_ms": {
            "median": statistics.median(collection_ms), "maximum": max(collection_ms),
            "max_schedule_lag": max(schedule_lag),
            "interpretation": "Read duration only; not an estimate of observer interference.",
        },
        "sampler_stop": status.get("stop"),
    }


def main() -> dict:
    assert JOB == "2294671"
    scheduler = COLLECTION["scheduler"]
    assert scheduler["State"] == "FAILED" and scheduler["ExitCode"] == "1:0"
    assert scheduler["ElapsedRaw"] == "2202" and scheduler["AllocCPUS"] == "56"

    verified_files = []
    for relative, metadata in COLLECTION["files"].items():
        path = COLLECTED / relative
        data = path.read_bytes()
        assert len(data) == metadata["bytes"], f"size mismatch: {relative}"
        assert sha256_bytes(data) == metadata["sha256"], f"SHA-256 mismatch: {relative}"
        verified_files.append(relative)
    assert len(verified_files) == 173
    archive = HERE / "raw-evidence.tar.gz"
    assert archive.stat().st_size == COLLECTION["archive_bytes"]
    assert sha256_file(archive) == COLLECTION["archive_sha256"]

    frozen_runtime_matches = []
    for relative, expected_hash in COLLECTION["frozen_runtime_hashes"].items():
        path = EXPERIMENT / relative
        assert path.is_file(), f"frozen runtime file missing: {relative}"
        assert sha256_file(path) == expected_hash, f"frozen runtime hash mismatch: {relative}"
        frozen_runtime_matches.append(relative)
    assert len(frozen_runtime_matches) == 62

    phases = [json.loads(line) for line in (RUN / "phases.jsonl").read_text().splitlines() if line.strip()]
    solver_exits = {row["phase"]: row for row in phases if row.get("state") == "solver-exit"}
    assert solver_exits["S1-scotch"]["returncode"] == 0
    assert solver_exits["X1-hierarchical-xyz"]["returncode"] == 0
    assert solver_exits["X2-hierarchical-xyz"]["returncode"] == 124
    assert "S2-scotch" not in solver_exits

    accepted = {
        "scotch": json.loads((EXPERIMENT / "accepted-source-manifest.json").read_text()),
        "xyz": json.loads((EXPERIMENT / "accepted-xyz-source-manifest.json").read_text()),
    }
    source_fields = {
        "scotch": json.loads((RUN / "scotch-source-fields.json").read_text()),
        "xyz": json.loads((RUN / "xyz-source-fields.json").read_text()),
    }
    for key in ("scotch", "xyz"):
        before = json.loads((RUN / f"{key}-source-before.json").read_text())
        assert before["manifest"] == accepted[key]
        assert source_fields[key]["field_count"] == 336

    arms = []
    arm_data = {}
    for label in SOLVER_ARMS:
        arm_dir = RUN / "arms" / label
        method = "xyz" if label.startswith("X") else "scotch"
        command = json.loads((arm_dir / "command.json").read_text())["command"]
        assert command == EXPECTED_COMMAND
        return_code = json.loads((arm_dir / "return-code.json").read_text())
        resource = parse_resource(arm_dir / "resource-time.log")
        telemetry = telemetry_summary(arm_dir)
        if label in ("S1-scotch", "X1-hierarchical-xyz"):
            log, timings, coeff_rows, iterations = review_native_output(arm_dir)
            recommended_samples = re.findall(
                r"Minimum number of measured time steps[^\n]*", log
            )
            assert return_code["returncode"] == 0
            assert resource["raw_fields"].get("Exit status") == "0"
            output_validity = "complete_native_output_and_zero_return_code"
        else:
            native = parse_partial_native_output(arm_dir)
            timings = native["timings_seconds"]
            coeff_rows = native["force_coefficient_rows"]
            iterations = native["fixed_iterations_match"]
            recommended_samples = native["recommended_samples"]
            assert return_code["returncode"] == 124
            assert resource["raw_fields"].get("Exit status") == "124"
            output_validity = "20_steps_and_19_intervals_printed_but_invalid_timeout_return_124"
        arm_data[label] = {"timings_seconds": timings, "coefficient_rows": coeff_rows,
                           "iterations": iterations, "resource": resource,
                           "return_code": return_code, "telemetry": telemetry,
                           "output_validity": output_validity}

        copy = json.loads((RUN / f"{label}-copy.json").read_text())
        assert copy.get("passed") and copy.get("no_source_inodes_reused")
        assert copy["manifest"] == accepted[method]
        postsolve_path = arm_dir / "postsolve-fields.json"
        postsolve = None
        if postsolve_path.is_file():
            postsolve = json.loads(postsolve_path.read_text())
            assert postsolve.get("passed") and postsolve["field_count"] == 336
            assert postsolve["fields"] == source_fields[method]["fields"]
        if label in ("S1-scotch", "X1-hierarchical-xyz"):
            assert postsolve is not None
        else:
            assert postsolve is None
        arms.append({
            "arm": label,
            "method": method,
            "steps_printed": 20,
            "intervals_printed": 19,
            "mean_s_step": statistics.mean(timings),
            "median_s_step": statistics.median(timings),
            "maximum_s_step": max(timings),
            "returncode": return_code["returncode"],
            "elapsed_seconds_reported": return_code["elapsed_seconds"],
            "classification": output_validity,
            "resource_time": resource["raw_fields"],
            "native_iteration_counts": iterations,
            "native_recommended_samples": recommended_samples,
            "input_copy_gate_passed": copy["passed"],
            "restored_time_zero_field_seals_match_method_source": postsolve is not None,
            "field_seal_scope": (postsolve or {}).get("scope"),
            "telemetry": telemetry,
        })

    partial = json.loads((RUN / "partial-results.json").read_text())
    partial_arms = {arm["arm"]: arm for arm in partial["arms"]}
    assert set(partial_arms) == {"S1-scotch", "X1-hierarchical-xyz"}
    for label in partial_arms:
        observed = partial_arms[label]
        replayed = arm_data[label]
        assert observed["timings_seconds"] == replayed["timings_seconds"]
        assert observed["Cd_by_step"] == replayed["coefficient_rows"]
        assert abs(observed["mean_s_step"] - statistics.mean(replayed["timings_seconds"])) < 1e-12

    s1, x1, x2 = (arm_data[label] for label in SOLVER_ARMS)
    x2_vs_x1_pct = 100.0 * (statistics.mean(x2["timings_seconds"]) /
                            statistics.mean(x1["timings_seconds"]) - 1.0)
    x1_vs_s1_pct = 100.0 * (statistics.mean(x1["timings_seconds"]) /
                            statistics.mean(s1["timings_seconds"]) - 1.0)
    x2_vs_s1_pct = 100.0 * (statistics.mean(x2["timings_seconds"]) /
                            statistics.mean(s1["timings_seconds"]) - 1.0)
    x1_x2_coefficients_identical = x1["coefficient_rows"] == x2["coefficient_rows"]
    assert x1_x2_coefficients_identical
    final_cd = {label: data["coefficient_rows"][-1][1]
                for label, data in zip(SOLVER_ARMS, (s1, x1, x2))}
    source_after_present = any((RUN / f"{method}-source-after.json").exists()
                               for method in ("scotch", "xyz"))
    runtime_after_present = (RUN / "runtime-after.json").exists()
    assert not source_after_present and not runtime_after_present

    result = {
        "reviewed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "job_id": JOB,
        "scheduler": scheduler,
        "all_transfer_hashes_verified": True,
        "transfer_file_count": len(verified_files),
        "frozen_runtime_hashes_verified": len(frozen_runtime_matches),
        "raw_evidence_archive_sha256_verified": True,
        "planned_order": ARM_ORDER,
        "observed_solver_order": SOLVER_ARMS,
        "arms": arms,
        "comparisons": {
            "first_adjacent_X1_vs_S1_percent": x1_vs_s1_pct,
            "X2_vs_X1_percent": x2_vs_x1_pct,
            "X2_vs_S1_percent_descriptive_only_invalid_X2": x2_vs_s1_pct,
            "X1_and_X2_force_coefficient_rows_exactly_equal": x1_x2_coefficients_identical,
            "final_Cd": final_cd,
            "final_Cd_X1_minus_S1": final_cd["X1-hierarchical-xyz"] - final_cd["S1-scotch"],
            "final_Cd_X1_minus_S1_percent": 100.0 * (final_cd["X1-hierarchical-xyz"] /
                                                       final_cd["S1-scotch"] - 1.0),
            "valid_pooled_ABBA_comparison": False,
        },
        "gate_status": {
            "S1_native_output_and_return_code": "passed",
            "X1_native_output_and_return_code": "passed",
            "X2_printed_output_structure": "20 steps, 19 intervals, End marker; timeout return code 124 invalidates arm",
            "S2": "not run",
            "source_before_manifests": "passed for Scotch and xyz",
            "time_zero_field_seals": "336 seals per successful arm match that arm's method-specific source manifest",
            "source_after_gates": "not reached",
            "runtime_after_gate": "not reached",
            "complete_four_arm_review": False,
        },
        "limits": [
            "The first S1-to-X1 adjacent contrast is a short directional screen only; it is not a confirmed speedup.",
            "X2 printed 20 steps and 19 timing intervals, but the command returned 124 at its 720-second cap; its timing is not a valid completed arm or a win.",
            "S2 was never run, so there is no complete counterbalanced four-arm comparison or pooled treatment effect.",
            "Time-zero field seals validate each method's restored input layout; final solver fields were not captured for a cross-layout equality test.",
            "The sampler records whole-node aggregate counters and instantaneous cross-CPU frequency medians; it provides no per-process attribution or bandwidth measurement.",
            "CPU time and scheduler accounting describe the captured commands/job; they do not by themselves establish a bottleneck or a billed cost.",
        ],
    }
    (HERE / "REVIEW.json").write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")
    print(json.dumps({
        "job_id": JOB,
        "verified_files": len(verified_files),
        "S1_mean_s_step": arms[0]["mean_s_step"],
        "X1_mean_s_step": arms[1]["mean_s_step"],
        "X2_printed_mean_s_step_invalid_timeout": arms[2]["mean_s_step"],
        "X2_vs_X1_percent_invalid": x2_vs_x1_pct,
        "complete_ABBA_review": False,
    }, indent=2))
    return result


if __name__ == "__main__":
    main()
