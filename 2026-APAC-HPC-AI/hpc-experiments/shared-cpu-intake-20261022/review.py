"""Review sealed read-only intake for two shared OpenFOAM CPU runs."""
from pathlib import Path, PurePosixPath
import datetime
import hashlib
import json
import math
import re
import statistics
import tarfile


ROOT = Path(__file__).resolve().parent
COLLECTED = ROOT / "collected"
BASELINE = ROOT.parent / "nscc-cpu-baseline-headerfix-20261021" / "payload" / "case"
EXPECTED_CELLS = 65_334_765
RUNS = {
    "25921487.pbs101": {"directory": "1n-scotch-25921487", "ranks": 128, "nodes": 1, "end_time": 40},
    "25921492.pbs101": {"directory": "2n-scotch-25921492", "ranks": 256, "nodes": 2, "end_time": 80},
}
STAGES = ("10_decomposePar", "20_renumberMesh", "30_potentialFoam", "40_applyBoundaryLayer")


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_json(path):
    return json.loads(path.read_text())


def elapsed_seconds(value):
    hours, minutes, seconds = map(int, value.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def data_rows(text):
    return [line.split() for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def floats(row):
    return [float(value) for value in row]


def quantile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def normalize_source(relative, data):
    text = data.decode()
    if relative in ("controlDict", "controlDict.noWrite"):
        text = re.sub(r"(?m)^(\s*endTime\s+)[^;]+;",
                      r"\g<1><ALLOWED_END_TIME>;", text)
    if relative == "include/caseDefinition":
        for key in ("nCores", "decompositionMethod", "nHierarchical"):
            text = re.sub(r"(?m)^(\s*" + key + r"\s+)[^;]+;",
                          r"\g<1><ALLOWED_" + key.upper() + r">;", text)
    return text.encode()


def parse_solver_info(text, expected_steps):
    header = None
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") and "Ux_iters" in stripped:
            header = stripped.lstrip("#").split()
            continue
        if stripped.startswith("#") or header is None:
            continue
        fields = stripped.split()
        if len(fields) == len(header):
            rows.append(dict(zip(header, fields)))
    require(header is not None and rows, "solverInfo header/data missing")
    times = [int(float(row["Time"])) for row in rows]
    require(times == list(range(1, expected_steps + 1)),
            f"solverInfo time rows mismatch: {len(times)} rows, expected {expected_steps}")
    iteration_fields = {
        "Ux_iters": 15, "Uy_iters": 15, "Uz_iters": 15,
        "p_iters": 12, "omega_iters": 8, "k_iters": 8,
    }
    observed = {}
    for field, target in iteration_fields.items():
        values = [int(float(row[field])) for row in rows]
        require(all(value == target for value in values),
                f"solverInfo fixed-work mismatch for {field}: {sorted(set(values))}")
        observed[field] = {"iterations_each_step": target, "steps": len(values)}
    return observed


def review_run(job, metadata, files):
    cfg = RUNS[job]
    run_root = f"runs/{cfg['directory']}/"

    def get(relative):
        key = run_root + relative
        require(key in files, f"{job}: missing collected member {key}")
        return files[key]

    accounting = metadata["jobs"][job]
    require(accounting["job_state"] == "F" and accounting["Exit_status"] == 0,
            f"{job}: sanitized PBS metadata is not F/exit0")
    resources = accounting["resources_used"]
    requested = accounting["Resource_List"]
    require(resources["ncpus"] == cfg["ranks"] and resources["ngpus"] == 0,
            f"{job}: reported allocation differs from expected CPU ranks")
    require(requested["ncpus"] == cfg["ranks"] and requested["mpiprocs"] == cfg["ranks"] and
            requested["nodect"] == cfg["nodes"], f"{job}: requested topology mismatch")

    solver_names = [name for name in files if name.startswith(run_root + "logFiles/50_simpleFoam.")]
    require(len(solver_names) == 1, f"{job}: expected one collected simpleFoam log")
    solver_log = files[solver_names[0]].decode(errors="replace")
    stage_names = {stage: run_root + "logFiles/" + stage + ".log" for stage in STAGES}
    stage_names["50_simpleFoam"] = solver_names[0]
    stages = {}
    for label, name in stage_names.items():
        require(name in files, f"{job}: missing stage log {name}")
        text = files[name].decode(errors="replace")
        has_end = bool(re.search(r"^End\s*$", text, re.M))
        fatal_count = len(re.findall(r"FOAM FATAL|FATAL ERROR", text, re.I))
        script_errors = len(re.findall(r"^ERROR:", text, re.M))
        require(has_end and fatal_count == 0,
                f"{job}: {label} lacks End or contains native fatal error")
        tail_lines = [line for line in text.splitlines() if line.strip()][-6:]
        stages[label] = {
            "end_marker": has_end,
            "native_fatal_count": fatal_count,
            "script_error_marker_count": script_errors,
            "tail_lines": tail_lines,
        }

    require("OPENFOAM=2512" in solver_log and "scalar=64" in solver_log,
            f"{job}: simpleFoam build/precision mismatch")
    require(re.search(r"Arch\s*:\s*\"LSB;label=32;scalar=64\"", solver_log),
            f"{job}: no double precision architecture evidence")
    require(f"nProcs : {cfg['ranks']}" in solver_log,
            f"{job}: solver log rank count mismatch")
    end_times = [int(x) for x in re.findall(r"^SIMPLE: no convergence criteria found\. Calculations will run for (\d+) steps\.", solver_log, re.M)]
    time_steps = [int(x) for x in re.findall(r"^Time = (\d+)\s*$", solver_log, re.M)]
    require(end_times == [cfg["end_time"]], f"{job}: fixed endpoint/work declaration mismatch")
    require(time_steps == list(range(1, cfg["end_time"] + 1)),
            f"{job}: solver log does not show the full requested time sequence")

    control = get("system/controlDict").decode()
    end_match = re.search(r"(?m)^\s*endTime\s+(\d+)\s*;", control)
    require(end_match and int(end_match.group(1)) == cfg["end_time"],
            f"{job}: controlDict endTime mismatch")
    case_def = get("system/include/caseDefinition").decode()
    def dict_scalar(name):
        match = re.search(r"(?m)^\s*" + name + r"\s+([^;]+);", case_def)
        require(match, f"{job}: missing {name} in caseDefinition")
        return match.group(1).split("//")[0].strip()
    ranks = int(dict_scalar("nCores"))
    method = dict_scalar("decompositionMethod")
    shape = [int(x) for x in re.findall(r"\d+", dict_scalar("nHierarchical"))]
    require(ranks == cfg["ranks"] and method == "scotch" and len(shape) == 3,
            f"{job}: requested decomposition configuration mismatch")

    decompose = get("logFiles/10_decomposePar.log").decode(errors="replace")
    decomp_method = re.search(r"Decomposition method\s+(\w+)\s+\[(\d+)\]", decompose)
    require(decomp_method and decomp_method.group(1) == "scotch" and
            int(decomp_method.group(2)) == cfg["ranks"],
            f"{job}: native partition method/rank mismatch")
    cell_counts = [int(x) for x in re.findall(r"^    Number of cells\s*=\s*(\d+)", decompose, re.M)]
    require(len(cell_counts) == cfg["ranks"] and sum(cell_counts) == EXPECTED_CELLS,
            f"{job}: partition count/total cells mismatch")
    cell_mean = statistics.mean(cell_counts)

    solver_info = get("postProcessing/solverInfo/0/solverInfo.dat").decode(errors="replace")
    fixed_work = parse_solver_info(solver_info, cfg["end_time"])

    wct_text = get("postProcessing/wallClockTimeStatistics/0/wallClockTime.dat").decode()
    wct_rows = [floats(row) for row in data_rows(wct_text)]
    require(len(wct_rows) == cfg["end_time"] - 1 and
            [int(row[0]) for row in wct_rows] == list(range(2, cfg["end_time"] + 1)),
            f"{job}: wallClockTime.dat row/time sequence mismatch")
    step_times = [row[2] for row in wct_rows]
    solver_step_samples = []
    current_time = None
    for line in solver_log.splitlines():
        time_match = re.match(r"^Time = (\d+)\s*$", line)
        if time_match:
            current_time = int(time_match.group(1))
        duration_match = re.match(
            r"^Wall-clock time elapsed during the current time step = ([0-9.eE+-]+) s\s*$", line)
        if duration_match:
            require(current_time is not None, f"{job}: unindexed solver timestep duration")
            solver_step_samples.append((current_time, float(duration_match.group(1))))
    require(len(solver_step_samples) == len(wct_rows),
            f"{job}: solver timestep duration count differs from wallClockTime.dat")
    require([time for time, _ in solver_step_samples] == [int(row[0]) for row in wct_rows],
            f"{job}: solver timestep duration indices differ from wallClockTime.dat")
    require(all(math.isfinite(value) and value > 0 for _, value in solver_step_samples) and
            all(math.isfinite(value) and value > 0 for value in step_times),
            f"{job}: nonpositive or non-finite timestep duration")
    pairwise_differences = [abs(solver_value - row[2])
                            for (_, solver_value), row in zip(solver_step_samples, wct_rows)]
    require(max(pairwise_differences) <= 1e-9,
            f"{job}: per-step solver elapsed values differ from wallClockTime.dat")
    avg_match = re.search(r"Average wall-clock time per time step\s*=\s*([0-9.eE+-]+)", solver_log)
    measured_match = re.search(r"Number of measured time steps\s*=\s*(\d+)", solver_log)
    require(avg_match and measured_match and int(measured_match.group(1)) == len(step_times),
            f"{job}: native WCT aggregate missing or count mismatch")
    native_average = float(avg_match.group(1))
    wct_average = statistics.mean(step_times)
    require(math.isclose(native_average, wct_average, rel_tol=1e-10, abs_tol=1e-10),
            f"{job}: native average differs from wallClockTime.dat")
    p95 = quantile(step_times, 0.95)
    q1, q3 = quantile(step_times, 0.25), quantile(step_times, 0.75)
    lower_fence, upper_fence = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    max_index = max(range(len(step_times)), key=step_times.__getitem__)
    max_time = int(wct_rows[max_index][0])
    iqr_outliers = [
        {"time": int(wct_rows[index][0]), "seconds": step_times[index]}
        for index in range(len(step_times))
        if step_times[index] < lower_fence or step_times[index] > upper_fence
    ]

    force_rows = [floats(row) for row in data_rows(
        get("postProcessing/forceCoeffsAll/0/coefficient.dat").decode())]
    require(len(force_rows) == cfg["end_time"] and
            [int(row[0]) for row in force_rows] == list(range(1, cfg["end_time"] + 1)),
            f"{job}: force coefficient row/time sequence mismatch")
    require(all(math.isfinite(value) for row in force_rows for value in row),
            f"{job}: non-finite force coefficient data")
    cds = [row[1] for row in force_rows]

    # Compare the retained source case with the accepted official case. Only
    # nCores, decompositionMethod, nHierarchical, and endTime may differ.
    system_prefix = run_root + "system/"
    candidate_system = {name[len(system_prefix):]: data for name, data in files.items()
                        if name.startswith(system_prefix)}
    baseline_system = {str(path.relative_to(BASELINE / "system")): path.read_bytes()
                       for path in (BASELINE / "system").rglob("*") if path.is_file()}
    require(set(candidate_system) == set(baseline_system),
            f"{job}: source system file set differs from accepted official case")
    for relative, baseline_bytes in baseline_system.items():
        candidate_bytes = candidate_system[relative]
        require(normalize_source(relative, candidate_bytes) == normalize_source(relative, baseline_bytes),
                f"{job}: unexpected source/system change: {relative}")

    for subdir in ("0.orig", "constant"):
        prefix = run_root + subdir + "/"
        candidate = {name[len(prefix):]: data for name, data in files.items() if name.startswith(prefix)}
        baseline_dir = BASELINE / subdir
        baseline_files = {str(path.relative_to(baseline_dir)): path.read_bytes()
                          for path in baseline_dir.rglob("*") if path.is_file()}
        require(set(candidate) == set(baseline_files),
                f"{job}: {subdir} source file set differs from accepted official case")
        for relative, expected in baseline_files.items():
            require(candidate[relative] == expected,
                    f"{job}: initial/source input differs from accepted official case: {subdir}/{relative}")

    elapsed = elapsed_seconds(resources["walltime"])
    cput = elapsed_seconds(resources["cput"])
    cpu_count = int(resources["ncpus"])
    utilization = cput / (elapsed * cpu_count) * 100.0
    rate = float(requested["queue_charge_rate"])
    estimated_su = elapsed * cpu_count * rate / 3600.0
    mem = resources["mem"]
    vmem = resources["vmem"]

    log_warnings = {}
    for label, name in stage_names.items():
        text = files[name].decode(errors="replace")
        log_warnings[label] = {
            "foam_warning_lines": len(re.findall(r"FOAM Warning", text)),
            "mpich_warning_lines": len(re.findall(r"MPICH WARNING", text)),
            "dynamic_code_initial_load_misses": len(re.findall(r"Could not load .*libwallClockTimeStatistics", text)),
            "native_fatal_lines": len(re.findall(r"FOAM FATAL|FATAL ERROR", text, re.I)),
        }
    omega_bounds = re.findall(
        r"bounding omega, min:\s*([-+0-9.eE]+)\s+max:\s*([-+0-9.eE]+)\s+average:\s*([-+0-9.eE]+)",
        solver_log)
    final_solver_tail = "\n".join(solver_log.splitlines()[-12:])
    sample_warning = "smaller than the calculated one by the statistical analysis" in solver_log.lower()

    return {
        "job": job,
        "job_state_from_sanitized_metadata": accounting["job_state"],
        "exit_status_from_sanitized_metadata": accounting["Exit_status"],
        "queue": accounting["queue"],
        "project": accounting["project"],
        "exec_host": accounting["exec_host"],
        "requested": {
            "nodes": cfg["nodes"], "ranks": cfg["ranks"], "memory": requested["mem"],
            "walltime": requested["walltime"], "queue_charge_rate": rate,
        },
        "source_case_comparison": {
            "official_payload": str(BASELINE),
            "all_source_system_bytes_match_after_allowed_parameter_normalization": True,
            "allowed_changes": ["nCores", "endTime", "decompositionMethod", "nHierarchical"],
            "initial_0_orig_and_constant_files_match_exactly": True,
            "rank": ranks, "method": method, "hierarchical_factors": shape,
            "end_time": cfg["end_time"],
        },
        "stage_logs": stages,
        "native_simplefoam": {
            "build": "OpenFOAM 2512, scalar=64 (double precision)",
            "completed_time_steps": len(time_steps), "final_time": time_steps[-1],
            "fixed_iterations_per_step": fixed_work,
            "native_measured_steps": int(measured_match.group(1)),
            "native_average_step_seconds": native_average,
            "wallClockTime_rows": len(wct_rows),
            "wallClockTime_first_time": int(wct_rows[0][0]),
            "wallClockTime_last_time": int(wct_rows[-1][0]),
            "wallClockTime_average_step_seconds": wct_average,
            "wallClockTime_min_step_seconds": min(step_times),
            "wallClockTime_max_step_seconds": max(step_times),
            "wallClockTime_median_step_seconds": statistics.median(step_times),
            "wallClockTime_standard_deviation_seconds": statistics.pstdev(step_times),
            "wallClockTime_p95_step_seconds_linear_interpolation": p95,
            "wallClockTime_p95_method": "linear interpolation at position (n-1)*0.95",
            "wallClockTime_iqr_outlier_fences_seconds": [lower_fence, upper_fence],
            "wallClockTime_iqr_outlier_samples": iqr_outliers,
            "wallClockTime_max_time": max_time,
            "wallClockTime_max_step_seconds": step_times[max_index],
            "step_time_samples": [
                {
                    "time": int(row[0]),
                    "solver_log_elapsed_seconds": solver_value,
                    "wallClockTime_dat_seconds": row[2],
                    "absolute_difference_seconds": difference,
                }
                for row, (_, solver_value), difference
                in zip(wct_rows, solver_step_samples, pairwise_differences)
            ],
            "native_simplefoam_tail": final_solver_tail,
        },
        "partition": {
            "method": decomp_method.group(1), "ranks": int(decomp_method.group(2)),
            "partition_records": len(cell_counts), "total_cells": sum(cell_counts),
            "min_cells_per_rank": min(cell_counts), "max_cells_per_rank": max(cell_counts),
            "max_cell_excess_fraction": max(cell_counts) / cell_mean - 1,
        },
        "force_coefficients": {
            "rows": len(force_rows), "first_time": int(force_rows[0][0]),
            "final_time": int(force_rows[-1][0]), "final_Cd": cds[-1],
            "min_Cd": min(cds), "max_Cd": max(cds), "all_values_finite": True,
        },
        "pbs_resources_used": {
            "walltime_seconds": elapsed, "walltime": resources["walltime"],
            "cput_seconds": cput, "cput": resources["cput"],
            "ncpus": cpu_count, "ngpus": resources["ngpus"],
            "cpupercent_last_sample_raw": resources["cpupercent"],
            "derived_whole_allocation_average_cpu_utilization_percent": utilization,
            "mem": mem, "vmem": vmem,
            "estimated_SU": estimated_su,
            "SU_estimate_formula": "resources_used.walltime_seconds * ncpus * Resource_List.queue_charge_rate / 3600",
            "posted_SU_charge": None,
        },
        "log_warning_counts": log_warnings,
        "wallclock_sample_confidence_warning_present": sample_warning,
        "omega_bound_records": len(omega_bounds),
        "omega_minimum_seen": min(float(row[0]) for row in omega_bounds) if omega_bounds else None,
        "omega_final_bounds": [float(x) for x in omega_bounds[-1]] if omega_bounds else None,
        "omega_diagnostic_interpretation": "Negative bounding minima are also present in accepted controls and do not alone establish a Basic failure; no final fields or hardware counters were collected to diagnose cause.",
    }


evidence_seal = local_json(COLLECTED / "evidence-sha256.json")
for relative, expected in evidence_seal.items():
    path = COLLECTED / relative
    require(path.is_file() and digest(path.read_bytes()) == expected,
            f"local evidence seal mismatch: {relative}")

collection_metadata = local_json(COLLECTED / "collection.json")
remote_manifest = local_json(COLLECTED / "remote-file-sha256.json")
archive_path = COLLECTED / "raw-text-evidence.tar.gz"
with tarfile.open(archive_path, "r:gz") as archive:
    members = archive.getmembers()
    require(all(member.isfile() for member in members), "raw archive contains non-file members")
    names = [member.name for member in members]
    require(len(names) == len(set(names)), "raw archive contains duplicate member paths")
    for name in names:
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts,
                f"unsafe raw archive path: {name}")
    require(set(names) == set(remote_manifest) | {"remote-file-sha256.json"},
            "raw archive members differ from the remote hash manifest")
    files = {member.name: archive.extractfile(member).read() for member in members}

require(files["remote-file-sha256.json"] == (COLLECTED / "remote-file-sha256.json").read_bytes(),
        "embedded remote hash manifest differs from the sealed local copy")
for name, expected in remote_manifest.items():
    require(digest(files[name]) == expected, f"remote-file hash mismatch: {name}")

require(set(collection_metadata["jobs"]) == set(RUNS), "collection job set mismatch")
for job, cfg in RUNS.items():
    item = collection_metadata["jobs"][job]
    require(item["job_state"] == "F" and item["Exit_status"] == 0,
            f"{job}: collection metadata does not show F/exit0")
    require(item["Resource_List"]["ncpus"] == cfg["ranks"] and
            item["Resource_List"]["nodect"] == cfg["nodes"],
            f"{job}: collection metadata allocation mismatch")

run_results = {job: review_run(job, collection_metadata, files) for job in RUNS}
one = run_results["25921487.pbs101"]
two = run_results["25921492.pbs101"]
throughput_ratio = one["native_simplefoam"]["native_average_step_seconds"] / two["native_simplefoam"]["native_average_step_seconds"]

result = {
    "reviewed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "scope": "Independent read-only review of sealed shared CPU intake. This is candidate native evidence, not an accepted official score or performance result.",
    "collection": {
        "sealed_local_files": len(evidence_seal),
        "sealed_remote_files": len(remote_manifest),
        "raw_archive_members": len(files),
        "all_local_and_remote_sha256_checks_passed": True,
    },
    "runs": run_results,
    "descriptive_per_step_time_ratio_1n_over_2n": throughput_ratio,
    "limits": [
        "PBS F/exit0 and sanitized resource metadata are present, but owner identity and frozen submitted script provenance are not verified; retained script bytes may differ from submitted bytes.",
        "The two runs compare official prescribed endpoints (128 ranks/40 steps versus 256 ranks/80 steps). Their per-step ratio is an endpoint-scaling observation, not controlled same-work strong scaling or a causal speedup claim.",
        "No processor fields, mesh binaries, final zero-field seals, or per-rank affinity/physical-core mapping were collected. PBS exec_host identifies allocated host(s), but not the physical cores used by each rank. The official mesh archive identity is not independently verified from these files.",
        "Negative omega bounding diagnostics alone do not establish failure; no final fields or hardware counters are available to diagnose their cause.",
        "The scripts treat a native End marker as sufficient even if a command returned nonzero. PBS reports exit 0, but the stage helper does not preserve/check every command return code.",
        "Estimated SU is elapsed allocation walltime times CPU count times queue charge rate divided by 3600. It is not a posted or reconciled charge.",
        "Neither run is the official four-node/150-step scored workload. Cd endpoints differ in time and are not an accuracy comparison.",
    ],
}
(ROOT / "review.json").write_text(json.dumps(result, indent=2) + "\n")

lines = [
    "# Shared CPU Intake Review",
    "",
    "This is a sealed-evidence review of two completed OpenFOAM CPU jobs. The logs and outputs support useful native timing observations, but missing ownership, frozen-script, final-field, mesh-binary, and physical-placement evidence prevent treating these as fully accepted results.",
    "",
    "## Integrity and work checks",
    "",
    f"All {len(evidence_seal)} local intake files and {len(remote_manifest)} remote-file entries passed SHA256 verification; the raw archive contains {len(files)} files with no unsafe paths. Both sanitized PBS records show state F and exit status 0. Each run has End markers for decomposePar, renumberMesh, potentialFoam, applyBoundaryLayer, and simpleFoam, and no native FOAM fatal marker.",
    "",
    "Both source cases match the accepted official payload after normalizing only rank count, endTime, decomposition method, and hierarchical shape. Initial 0.orig fields and constant inputs match exactly. Native logs identify OpenFOAM 2512 double precision and Scotch with the expected partition counts.",
    "",
    "| Job | Nodes / ranks | Steps / terminal Time | Cell partitions | Cells total | Fixed work per step (Ux/Uy/Uz, p, omega, k) |",
    "|---|---:|---:|---:|---:|---|",
]
for job, data in run_results.items():
    work = data["native_simplefoam"]["fixed_iterations_per_step"]
    cfg = RUNS[job]
    lines.append(
        f"| {job} | {cfg['nodes']} / {cfg['ranks']} | {cfg['end_time']} / {cfg['end_time']} | "
        f"{data['partition']['partition_records']} | {data['partition']['total_cells']:,} | "
        f"15 / 12 / 8 / 8 (checked for every recorded step) |"
    )
lines += [
    "",
    "The per-step work is 15 iterations for each velocity component, 12 for pressure, 8 for omega, and 8 for k. SolverInfo records cover every requested step. The wallClockTime function records 39 samples for the 40-step job and 79 for the 80-step job, beginning at Time 2. Every per-step elapsed value and time index in simpleFoam matches its wallClockTime.dat row; each series' arithmetic mean also matches the solver log aggregate.",
    "",
    "## Timing and resources",
    "",
    "| Job | Native mean step time (s) | p95 (s) | WCT range (s) | Max Time / seconds | IQR outlier Times | PBS walltime | PBS CPUT | Derived whole-allocation CPU use | cpupercent last sample | mem / vmem | Estimated SU |",
    "|---|---:|---:|---:|---|---|---:|---:|---:|---:|---|---:|",
]
for job, data in run_results.items():
    t = data["native_simplefoam"]
    p = data["pbs_resources_used"]
    outlier_times = ", ".join(str(item["time"]) for item in t["wallClockTime_iqr_outlier_samples"]) or "none"
    lines.append(
        f"| {job} | {t['native_average_step_seconds']:.6f} | "
        f"{t['wallClockTime_p95_step_seconds_linear_interpolation']:.6f} | "
        f"{t['wallClockTime_min_step_seconds']:.6f}–{t['wallClockTime_max_step_seconds']:.6f} | "
        f"{t['wallClockTime_max_time']} / {t['wallClockTime_max_step_seconds']:.6f} | {outlier_times} | "
        f"{p['walltime']} | {p['cput']} | {p['derived_whole_allocation_average_cpu_utilization_percent']:.2f}% | "
        f"{p['cpupercent_last_sample_raw']} (PBS last sample) | {p['mem']} / {p['vmem']} | {p['estimated_SU']:.3f}* |"
    )
lines += [
    "",
    f"The observed per-step time ratio is {throughput_ratio:.3f} (1-node value divided by 2-node value). These are endpoint-scaling observations at the prescribed 40- and 80-step endpoints, across 128- and 256-rank allocations. They are not controlled same-work strong scaling or a causal speedup measurement. The native statistic uses the 39/79 recorded post-start samples. The 2-node timing logger estimates 225 samples for its 2% error / 95% confidence target; its 79-sample mean has low sample confidence. Keep official endpoints unchanged; any longer timing sample belongs in a separately labeled diagnostic outside ranked scoring.",
    "The reported p95 uses linear interpolation. IQR outliers use the Tukey 1.5×IQR fences; the maximum Time identifies the single largest recorded step. Full time-indexed simpleFoam and wallClockTime values are retained in review.json.",
    "",
    "The PBS `cpupercent` values are the last reported samples (11551 and 23150), not whole-allocation averages. The separate average shown above is derived from PBS CPUT divided by allocated CPUs times full PBS walltime; it includes preparation and solve stages. Memory fields retain PBS `kb` units.",
    "",
    "`*` SU is estimated as elapsed PBS walltime seconds × allocated CPUs × queue charge rate ÷ 3600, using the reported rate 1.0. This is an estimate, not a posted charge.",
    "",
    "## Output and log observations",
    "",
]
for job, data in run_results.items():
    force = data["force_coefficients"]
    lines.append(
        f"- {job}: all {force['rows']} Cd/force rows are finite; final Cd at Time {force['final_time']} is {force['final_Cd']:.10f} "
        f"(full recorded Cd range {force['min_Cd']:.10f} to {force['max_Cd']:.10f})."
    )
lines += [
    "- MPI stages repeatedly warn that `FI_VERBS_PREFER_XRC` conflicts with `FI_OFI_RXM_USE_SRX=0`, so XRC is disabled. The solver also reports that the wallClockTime dynamic library was initially absent and then builds it in the run directory.",
    "- Both decomposePar logs warn while reading `constant/README.md`. The 2-node simpleFoam log reports that 79 measured steps are below its 225-sample recommendation. These warnings did not prevent End markers, but they remain part of the native evidence.",
    "- The solver logs report negative minima in omega bounding diagnostics; final printed minima are "
    f"{one['omega_final_bounds'][0]:.6g} and {two['omega_final_bounds'][0]:.6g}. Negative omega diagnostics are also present in accepted control runs and do not by themselves establish a Basic failure. No final processor fields or hardware counters were collected to diagnose their cause.",
    "",
    "## Limits and next decision",
    "",
    "PBS exec_host records the allocated host(s) for each job. The collection lacks processor fields, mesh binaries, final zero-field hashes, and per-rank affinity/physical-core mapping. The collection notes also say current job-script bytes need not match the submitted bytes, and ownership is unverified. These records therefore support candidate native solver timing and full-work observations, but do not establish frozen payload provenance, actual per-rank placement, final-field validity, or an accepted score.",
    "",
    "The shared run scripts accept a native `End` marker without checking each command's return code. The PBS metadata reports job exit 0, yet the per-stage helper can mask a nonzero native return if `End` was also printed. Future frozen scripts should retain and check each return code explicitly.",
    "",
    "Treat the 1-node/2-node ratio as descriptive endpoint scaling only. A separate, unranked diagnostic can gather a longer timing sample if needed; preserve prescribed ranked endpoints. A controlled scaling conclusion also requires frozen input provenance and verified per-rank placement.",
    "",
    "Machine-readable details and seals are in [review.json](review.json).",
]
(ROOT / "RESULTS.md").write_text("\n".join(lines) + "\n")
print(json.dumps(result, indent=2))
