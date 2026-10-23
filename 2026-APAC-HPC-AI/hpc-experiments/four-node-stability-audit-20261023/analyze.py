#!/usr/bin/env python3
"""Descriptive timing/function-cadence audit for the sealed six-run review."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import tarfile
from collections import Counter
from pathlib import Path

DEFAULT_REVIEW = Path(__file__).resolve().parents[1] / "four-node-review-20261023" / "review.json"
DEFAULT_ARCHIVE = Path(__file__).resolve().parents[1] / "four-node-review-20261023" / "collected" / "raw-text-evidence.tar.gz"
RUNS = ("25921488.pbs101", "25921517.pbs101", "25921518.pbs101", "25921692.pbs101", "25921905.pbs101", "25921906.pbs101")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


def inspect_schedule(archive: Path, review: dict):
    output_files = ("postProcessing/forceCoeffsAll/0/coefficient.dat",
                    "postProcessing/solverInfo/0/solverInfo.dat",
                    "postProcessing/minMax_U/0/fieldMinMax.dat",
                    "postProcessing/minMax_p/0/fieldMinMax.dat",
                    "postProcessing/wallShearStress/0/wallShearStress.dat",
                    "postProcessing/wallClockTimeStatistics/0/wallClockTime.dat")
    per_run = {}
    with tarfile.open(archive, "r:gz") as tf:
        names = set(tf.getnames())
        for job in RUNS:
            run_name = review["runs"][job]["run_directory"]
            prefix = f"runs/{run_name}/system/"
            base_path = prefix + "controlDict"
            if base_path not in names:
                raise ValueError(f"controlDict missing for {job}")
            base = tf.extractfile(base_path).read().decode("utf-8", "replace")
            wc = re.search(r"\bwriteControl\s+(\w+)\s*;", base)
            wi = re.search(r"\bwriteInterval\s+(\d+)\s*;", base)
            fn_block = re.search(r"\bfunctions\s*\{(.*?)\n\}", base, re.S)
            fn_order = re.findall(r'#include\s+"([^"]+)"', fn_block.group(1)) if fn_block else []
            active_functions = {}
            active_probe_outputs = {}
            active_probes = [rel for rel in fn_order if rel.startswith("probes/")]
            for rel in fn_order:
                config_path = prefix + rel
                if config_path not in names:
                    raise ValueError(f"active function-object definition missing for {job}: {rel}")
                text = tf.extractfile(config_path).read().decode("utf-8", "replace")
                control = re.search(r"\bwriteControl\s+(\w+)\s*;", text)
                interval = re.search(r"\bwriteInterval\s+(\d+)\s*;", text)
                active_functions[rel] = {"writeControl": control.group(1) if control else "implicit/default",
                                         "writeInterval": int(interval.group(1)) if interval else None}
                if rel.startswith("probes/"):
                    name_match = re.search(r"^\s*name\s+(\w+)\s*;", text, re.M)
                    if not name_match:
                        raise ValueError(f"active probe has no output name for {job}: {rel}")
                    obj_name = name_match.group(1)
                    active_probe_outputs[rel] = {"object_name": obj_name,
                                                 "configured_writeControl": control.group(1) if control else "implicit/default",
                                                 "configured_writeInterval": int(interval.group(1)) if interval else None}
            clock_code_path = prefix + "FOwallClockTimeStatistics"
            clock_code = tf.extractfile(clock_code_path).read().decode("utf-8", "replace") if clock_code_path in names else ""
            cumulative_log_paths = [name for name in names if name.startswith(f"runs/{run_name}/logFiles/50_simpleFoam") and name.endswith(".log")]
            if len(cumulative_log_paths) != 1:
                raise ValueError(f"expected one archived simpleFoam log for {job}, found {len(cumulative_log_paths)}")
            solver_log = tf.extractfile(cumulative_log_paths[0]).read().decode("utf-8", "replace")
            current_time = None
            cumulative = {}
            for line in solver_log.splitlines():
                tm = re.match(r"\s*Time = (\d+)\s*$", line)
                if tm:
                    current_time = int(tm.group(1))
                em = re.search(r"ExecutionTime = ([0-9.]+) s\s+ClockTime = ([0-9.]+) s", line)
                if em and current_time is not None:
                    cumulative[current_time] = {"execution_seconds": float(em.group(1)),
                                                "clock_seconds": float(em.group(2))}
            cumulative_deltas = {}
            for t in range(2, 151):
                if t not in cumulative or t - 1 not in cumulative:
                    raise ValueError(f"missing cumulative native timing at {job} Time {t}")
                cumulative_deltas[t] = {
                    "execution_delta_seconds": cumulative[t]["execution_seconds"] - cumulative[t-1]["execution_seconds"],
                    "rounded_clock_delta_seconds": cumulative[t]["clock_seconds"] - cumulative[t-1]["clock_seconds"],
                }
            observed = {}
            dynamic_outputs = list(output_files)
            for rel in active_probe_outputs:
                obj = active_probe_outputs[rel]["object_name"]
                dynamic_outputs.append(f"postProcessing/{obj}/0/cp")
            for rel in dynamic_outputs:
                path = f"runs/{run_name}/{rel}"
                if path not in names:
                    observed[rel] = {"archive_status": "absent_or_not_collected", "numeric_rows": None}
                    continue
                raw = tf.extractfile(path).read().decode("utf-8", "replace")
                row_count = sum(1 for line in raw.splitlines()
                                if re.match(r"\s*\d+\s+", line) and not line.lstrip().startswith("#"))
                observed[rel] = {"archive_status": "present", "numeric_rows": row_count}
            cp_paths = sorted(name for name in names if name.startswith(f"runs/{run_name}/")
                              and "/postProcessing/" in name
                              and ("calc_cp" in name or "/postProcessing/cp/" in name))
            observed["active_function_object_artifacts"] = {
                "calc_cp": {"archive_paths_matching_object_or_cp": cp_paths,
                            "archive_status": "absent_from_collected_text_archive" if not cp_paths else "present",
                            "numeric_rows": None if not cp_paths else "not_summarized"},
                "wallShearStress": observed["postProcessing/wallShearStress/0/wallShearStress.dat"],
            }
            if not wc or not wi:
                raise ValueError(f"global write schedule missing for {job}")
            per_run[job] = {"run_directory": run_name,
                            "global_field_write_control": wc.group(1),
                            "global_field_write_interval_steps": int(wi.group(1)),
                            "function_include_order": fn_order,
                            "active_probe_object_count_derived_from_include_order": len(active_probes),
                            "active_probe_objects": active_probe_outputs,
                            "wall_clock_implementation_checks": {
                                "uses_elapsed_time_between_callbacks": "wallClock_.elapsedTime()" in clock_code,
                                "updates_clock_each_callback": "wallClock_.update()" in clock_code,
                                "excludes_first_callback": "firstTimeStep_" in clock_code,
                            },
                            "function_write_schedules_active_only": active_functions,
                            "observed_numeric_data_rows": observed,
                            "native_cumulative_time_deltas_by_time": cumulative_deltas}
    return {
        "per_run_case_schedules_and_output_rows": per_run,
        "interpretation": "Function schedules were parsed only from active includes in each controlDict. Active probe-object count is derived from those includes, and each corresponding collected probe file is counted separately. Output archive absence is null/not collected, not zero rows. Per-step forceCoeffs, solverInfo, active probes and minMax data are supported by their configured cadence or observed per-step rows; global field writes are set to 100000 steps. calc_cp is configured writeTime but no matching artifact is present in the collected text archive; wallShearStress also uses writeTime and its present output file has zero numeric rows. Neither observation establishes whether its execute callback did work. The wall-clock function is first in the functions include order, excludes its first callback, and measures elapsed time between callbacks. Therefore a Time t sample is an interval measure, not an isolated same-Time output operation. No object-level cost is measured.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    ap.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    ap.add_argument("--output", type=Path, default=Path(__file__).with_name("audit.json"))
    args = ap.parse_args()
    review = json.loads(args.review.read_text())
    if review.get("status") != "CANDIDATE_NATIVE_EVIDENCE_ONLY":
        raise SystemExit("unexpected source review status")
    results = {}
    outlier_union = Counter()
    top3_union = Counter()
    run_values = {}
    for job in RUNS:
        r = review["runs"][job]
        n = r["native_simplefoam"]
        samples = n["step_time_samples"]
        times = [int(x["time"]) for x in samples]
        vals = [float(x["solver_log_seconds"]) for x in samples]
        if len(vals) != 149 or times != list(range(2, 151)):
            raise SystemExit(f"unexpected sample grid for {job}")
        outliers = sorted(int(x["time"]) for x in n["iqr_outliers"])
        top3 = sorted(int(x["time"]) for x in n["top_three_step_times_descending"])
        for t in outliers: outlier_union[t] += 1
        for t in top3: top3_union[t] += 1
        # Fixed phase bins: first 10 measured iterations, interior, last 10.
        phase_masks = {"start_T2_T11": lambda t: 2 <= t <= 11,
                       "middle_T12_T140": lambda t: 12 <= t <= 140,
                       "end_T141_T150": lambda t: 141 <= t <= 150}
        phases = {}
        for label, predicate in phase_masks.items():
            selected = [(t, v) for t, v in zip(times, vals) if predicate(t)]
            phases[label] = {
                "n": len(selected), "mean_seconds": mean([v for _, v in selected]),
                "median_seconds": median([v for _, v in selected]),
                "iqr_outlier_count": sum(t in set(outliers) for t, _ in selected),
                "iqr_outlier_rate": sum(t in set(outliers) for t, _ in selected) / len(selected),
            }
        outlier_set = set(outliers)
        adjacency = sum(1 for t in outlier_set if t + 1 in outlier_set)
        # Longest consecutive run of IQR outlier indices.
        groups = []
        for t in outliers:
            if not groups or t != groups[-1][-1] + 1:
                groups.append([t])
            else:
                groups[-1].append(t)
        best = max(groups, key=len) if groups else []
        results[job] = {
            "method": r["method"], "ranks_per_node": r["per_node_mpi_ranks"],
            "sample_count": len(vals), "sample_time_indices": [2, 150],
            "mean_seconds": n["average_step_seconds"], "median_seconds": n["median_seconds"],
            "p95_seconds": n["p95_seconds_linear_interpolation"],
            "max_seconds": n["max_seconds"], "max_time": n["max_time"],
            "native_minimum_sample_recommendation": n["native_minimum_sample_count_for_2pct_95pct_target"],
            "confidence_warning": n["native_sample_confidence_warning_present"],
            "iqr_fences_seconds": n["iqr_fences_seconds"], "iqr_outlier_times": outliers,
            "top_three_times": top3, "phase_summary": phases,
            "outlier_adjacent_pairs": adjacency,
            "longest_consecutive_outlier_run": best,
            "all_samples_seconds": [{"time": t, "seconds": v} for t, v in zip(times, vals)],
        }
        run_values[job] = vals
    output = {
        "analysis": "descriptive phase/cadence audit; no significance or causal tests",
        "inputs": {"review_path": str(args.review), "review_sha256": sha256(args.review),
                   "archive_path": str(args.archive), "archive_sha256": sha256(args.archive)},
        "series_definition": "all 149 native simpleFoam Average samples at Time 2..150, retained unchanged; WCT/log matches are from the source review",
        "phase_bins_descriptive": {"start_T2_T11": 10, "middle_T12_T140": 129, "end_T141_T150": 10},
        "function_schedule": inspect_schedule(args.archive, review),
        "cross_run_timing_indices": {
            "times_that_are_top3_in_multiple_runs": {str(t): c for t, c in sorted(top3_union.items()) if c > 1},
            "times_that_are_iqr_outliers_in_multiple_runs": {str(t): c for t, c in sorted(outlier_union.items()) if c > 1},
        },
        "runs": results,
        "limits": [
            "The six runs are separate allocations, not repeated matched controls; no causal inference is made.",
            "All six source loggers warn that 149 samples are below their run-specific 2%-at-95%-confidence recommendation.",
            "Per-step function output is part of the measured interval, but no object-level timing, per-rank timing, filesystem telemetry, CPU frequency, scheduler elapsed history, or physical affinity telemetry is available.",
            "IQR outlier labels and fixed phase bins are descriptive summaries, not a distribution-free stability or significance test.",
            "The job history is unavailable; native evidence does not establish final scheduler state, exit status, elapsed time, or charge.",
        ],
    }
    for job, run in results.items():
        deltas = output["function_schedule"]["per_run_case_schedules_and_output_rows"][job]["native_cumulative_time_deltas_by_time"]
        for sample in run["all_samples_seconds"]:
            sample.update(deltas[sample["time"]])
        max_sample = next(x for x in run["all_samples_seconds"] if x["time"] == run["max_time"])
        run["max_step_clock_context"] = {k: max_sample[k] for k in ("time", "seconds", "execution_delta_seconds", "rounded_clock_delta_seconds")}
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "run_count": len(results), "samples_per_run": 149,
                      "overlap_top3": output["cross_run_timing_indices"]["times_that_are_top3_in_multiple_runs"],
                      "overlap_outliers": output["cross_run_timing_indices"]["times_that_are_iqr_outliers_in_multiple_runs"]}, indent=2))

if __name__ == "__main__":
    main()
