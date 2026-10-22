"""Review collected native files without inferring PBS terminal state or charges."""
from pathlib import Path
import datetime
import hashlib
import json
import math
import re
import statistics
import tarfile

ROOT = Path(__file__).resolve().parent
JOB = "25907753.pbs101"
COLLECTION = ROOT / "collected-files-only" / JOB
RUNS = Path("runs/25907753")
ARCHIVE_PATH = COLLECTION / "raw-text-evidence.tar.gz"


def read_bytes(relative):
    path = COLLECTION / relative
    if path.is_file():
        return path.read_bytes()
    with tarfile.open(ARCHIVE_PATH, "r:gz") as archive:
        member = archive.extractfile(str(relative).lstrip("./"))
        if member is None:
            raise FileNotFoundError(str(relative))
        return member.read()


def read_text(relative):
    return read_bytes(relative).decode("utf-8")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

# Verify the files-only collection's recorded hashes. Scheduler state is absent by design.
manifest = json.loads((COLLECTION / "evidence-sha256.json").read_text())
for relative, expected in manifest.items():
    require(hashlib.sha256(read_bytes(relative)).hexdigest() == expected,
            f"collection hash mismatch: {relative}")

payload_hashes = json.loads((ROOT / "payload-sha256.json").read_text())
for relative, expected in payload_hashes.items():
    require(sha256(ROOT / "payload" / relative) == expected,
            f"local frozen payload hash mismatch: {relative}")
for relative in payload_hashes:
    require(read_bytes(relative) == (ROOT / "payload" / relative).read_bytes(),
            f"collected payload differs from frozen payload: {relative}")

collected_validation = json.loads(read_text("INPUTS_VALIDATED.json"))
require(collected_validation.get("passed") is True, "runtime input validation did not pass")
require("CPU_HS_PAIR_PASS" in read_text("tu-cpu-SN128.o25907753"),
        "native wrapper completion marker missing")

placement = [json.loads(line) for line in read_text(RUNS / "rank-placement.jsonl").splitlines() if line.strip()]
require(sorted(row["rank"] for row in placement) == list(range(128)), "rank coverage mismatch")
require(len({row["host"] for row in placement}) == 1, "placement spans unexpected hosts")
require(all(len(row["affinity"]) == 1 for row in placement), "rank affinity is not single-CPU")
require(len({row["affinity"][0] for row in placement}) == 128, "logical CPU affinity is not unique")
require(len({tuple(row["physical_core"]) for row in placement}) == 128,
        "physical core affinity is not unique")
groups = [
    {tuple(row["numa_nodes"]) for row in placement if row["rank"] // 16 == group}
    for group in range(8)
]
require(all(len(group) == 1 and len(next(iter(group))) == 1 for group in groups),
        "rank block does not map to one NUMA node")
numa_nodes = [next(iter(group)) for group in groups]
require(len(set(numa_nodes)) == 8, "NUMA rank blocks are not distinct")
environment = read_text(RUNS / "environment.log")
require("AMD EPYC 7713" in environment, "expected CPU model missing")


def stage(relative, expected_ranks=128):
    text = read_text(relative)
    require(re.search(r"^End\s*$", text, re.M) is not None, f"OpenFOAM End missing: {relative}")
    require("FOAM FATAL" not in text and "died from signal" not in text,
            f"fatal/signal marker in {relative}")
    require("OPENFOAM=2512" in text and "scalar=64" in text,
            f"version/precision mismatch in {relative}")
    require(re.search(rf"^nProcs\s*:\s*{expected_ranks}\s*$", text, re.M) is not None,
            f"rank count mismatch in {relative}")
    require(re.search(r"Exit status:\s*0\s*$", text, re.M) is not None,
            f"GNU time did not record exit status 0: {relative}")
    return text


for name in ("renumberMesh", "potentialFoam", "applyBoundaryLayer"):
    stage(RUNS / "candidate-init" / f"{name}.log")

sources = {
    "control": ROOT.parent / "nscc-cpu-scotch128-20261021" / "payload" / "case" / "system",
    "candidate": ROOT.parent / "nscc-cpu-numa-scotch128-20261021" / "payload" / "case" / "system",
}
results = {}
for role, method in (("control", "default_scotch"), ("candidate", "numa_scotch")):
    base = RUNS / role
    log_path = base / "logFiles/simpleFoam.log"
    text = stage(log_path)
    steps = [int(value) for value in re.findall(r"^Time = (\d+)\s*$", text, re.M)]
    require(steps == list(range(1, 41)), f"fixed steps mismatch: {role}")
    samples = [float(value) for value in re.findall(
        r"Wall-clock time elapsed during the current time step = ([\deE.+-]+)", text)]
    average = float(re.search(
        r"Average wall-clock time per time step\s*=\s*([\deE.+-]+)", text)[1])
    require(len(samples) == 39 and all(math.isfinite(value) and value > 0 for value in samples),
            f"timing samples invalid: {role}")
    require(math.isfinite(average) and abs(statistics.mean(samples) - average) < 1e-10,
            f"native average does not match samples: {role}")
    wall_rows = [list(map(float, line.split())) for line in read_text(
        base / "postProcessing/wallClockTimeStatistics/0/wallClockTime.dat").splitlines()
        if line.strip() and not line.startswith("#")]
    require([int(row[0]) for row in wall_rows] == list(range(2, 41)),
            f"native timer row coverage mismatch: {role}")
    require(all(abs(sample - row[2]) < 1e-10 for sample, row in zip(samples, wall_rows)),
            f"native timer and solver samples differ: {role}")
    forces = [list(map(float, line.split())) for line in read_text(
        base / "postProcessing/forceCoeffsAll/0/coefficient.dat").splitlines()
        if line.strip() and not line.startswith("#")]
    require([int(row[0]) for row in forces] == steps and
            all(math.isfinite(value) for row in forces for value in row),
            f"force coefficient rows invalid: {role}")
    for field, iterations in (("Ux", 15), ("Uy", 15), ("Uz", 15),
                              ("p", 12), ("omega", 8), ("k", 8)):
        values = [int(value) for value in re.findall(
            rf"Solving for {field},.*?No Iterations (\d+)", text)]
        require(values == [iterations] * 40, f"fixed solver work mismatch: {role}/{field}")
    semantic = json.loads(read_text(base / "semantic-result.json"))
    require(semantic.get("passed") is True and semantic.get("average_seconds_step") == average and
            semantic.get("final_Cd_dimensionless") == forces[-1][1],
            f"semantic result mismatch: {role}")
    before_path = RUNS / f"{role}-before.json"
    after_path = RUNS / f"{role}-after.json"
    before = json.loads(read_text(before_path))
    after = json.loads(read_text(after_path))
    require(before["files"] == after["files"], f"zero-time fields changed: {role}")
    source = sources[role]
    require(source.exists(), f"pinned source system missing: {source}")
    source_files = {path.relative_to(source).as_posix() for path in source.rglob("*") if path.is_file()}
    runtime_prefix = f"{(base / 'system').as_posix()}/"
    runtime_files = {
        name[len(runtime_prefix):] for name in manifest
        if name.startswith(runtime_prefix)
    }
    require(runtime_files == source_files, f"runtime system file set differs: {role}")
    for relative in source_files:
        if relative == "controlDict":
            continue
        actual = read_bytes(base / "system" / relative)
        require(actual == (source / relative).read_bytes(),
                f"runtime system input differs: {role}/{relative}")
    runtime_control = read_text(base / "system/controlDict")
    require(re.search(r"^startFrom\s+startTime;", runtime_control, re.M) is not None and
            re.search(r"^endTime\s+40;", runtime_control, re.M) is not None,
            f"runtime controlDict time bounds mismatch: {role}")
    timing_source = (source / "FOwallClockTimeStatistics").read_text()
    require([value.strip() for value in re.findall(r"#\{(.*?)#\}", timing_source, re.S)] ==
            [value.strip() for value in re.findall(r"#\{(.*?)#\}", runtime_control, re.S)],
            f"native timing function object differs: {role}")
    results[role] = {
        "method": method,
        "steps": 40,
        "measured_steps": 39,
        "average_seconds_step": average,
        "median_seconds_step": statistics.median(samples),
        "p95_seconds_step": statistics.quantiles(samples, n=100, method="inclusive")[94],
        "min_seconds_step": min(samples),
        "max_seconds_step": max(samples),
        "final_Cd_dimensionless": forces[-1][1],
        "native_solver_clock_seconds": float(re.findall(r"ClockTime = ([\d.]+) s", text)[-1]),
        "omega_bounding_messages": text.count("bounding omega"),
        "timing_confidence_warning": "smaller than the calculated one" in text,
        "initial_fields_unchanged": True,
        "field_seal_file_count": len(before["files"]),
        "field_seal_before_json_sha256": hashlib.sha256(read_bytes(before_path)).hexdigest(),
        "field_seal_after_json_sha256": hashlib.sha256(read_bytes(after_path)).hexdigest(),
        "timing_samples_by_step_seconds": [
            {"step": index + 2, "seconds": value} for index, value in enumerate(samples)
        ],
        "samples_above_inclusive_p95_seconds": [
            {"step": index + 2, "seconds": value}
            for index, value in enumerate(samples)
            if value > statistics.quantiles(samples, n=100, method="inclusive")[94]
        ],
        "exact_solver_warning_lines": [
            line for line in text.splitlines()
            if re.search(r"warning|bounding omega|FOAM FATAL|died from signal", line, re.I)
        ],
    }

ratio = results["control"]["average_seconds_step"] / results["candidate"]["average_seconds_step"]
submission = json.loads((ROOT / "submission.json").read_text())
out = {
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "job": JOB,
    "state": "NATIVE_PAIR_EVIDENCE_PASS_SCHEDULER_HISTORY_UNAVAILABLE",
    "scheduler_terminal_state": "UNVERIFIED: PBS history unavailable; no terminal accounting used",
    "native_wrapper_completion_marker_observed": True,
    "submitted_maximum_SU_reserved": submission["maximum_SU"],
    "submitted_maximum_SU_reserved_is_not_actual_charge": True,
    "node": next(iter({row["host"] for row in placement})),
    "order": ["default_scotch", "numa_scotch"],
    "results": results,
    "observed_control_over_candidate_step_time_ratio": ratio,
    "observed_candidate_step_time_reduction_percent": 100 * (1 - 1 / ratio),
    "placement_records": placement,
    "limitations": [
        "Native files pass source, stage exit, fixed-work, timing, force, zero-field, and rank placement checks.",
        "PBS terminal state and exact batch elapsed time are unavailable and remain unverified.",
        "No exact batch elapsed time, actual SU usage, posted individual charge, or terminal resource accounting is inferred.",
        "One ordered pair has no reverse repeat; cache, order, and host effects remain.",
        "Affinity probe is outside solver timing and does not establish page residency or solver-time migration.",
        "Hardware bandwidth/cache/MPI counters and power were not collected; GNU time wraps the PALS launcher.",
        "This is not the four-node/150-step score.",
    ],
}
(ROOT / "review-files-only.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({key: value for key, value in out.items() if key != "placement_records"}, indent=2))
