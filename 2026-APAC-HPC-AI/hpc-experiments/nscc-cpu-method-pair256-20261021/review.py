"""Review a two-node H/S256 run using its full native evidence."""
from pathlib import Path
import datetime
import hashlib
import json
import math
import re
import statistics
from collections import Counter


ROOT = Path(__file__).resolve().parent
review_output = ROOT / "review.json"
job = json.loads((ROOT / "submission.json").read_text())["stdout"].strip()
collected = ROOT / "collected" / job
run_id = job.split(".")[0]
run = collected / "runs" / run_id

for relative, expected in json.loads((collected / "evidence-sha256.json").read_text()).items():
    assert hashlib.sha256((collected / relative).read_bytes()).hexdigest() == expected, relative

accounting = json.loads((ROOT / "terminal-accounting.json").read_text())["jobs"][job]
assert accounting["job_state"] == "F" and accounting["Exit_status"] == 0
resources = accounting["Resource_List"]
assert resources["ncpus"] == 256 and resources["ngpus"] == 0
assert resources["select"] == "2:ncpus=128:mpiprocs=128:mem=440gb:ngpus=0"
assert resources["place"] == "scatter:excl"

for payload_file in (ROOT / "payload").iterdir():
    assert payload_file.read_bytes() == (collected / payload_file.name).read_bytes(), payload_file.name
assert json.loads((collected / "INPUTS_VALIDATED.json").read_text())["passed"] is True
assert "CPU_HS256_PAIR_PASS" in (collected / f"tu-cpu-HS256.o{run_id}").read_text()

placement = [json.loads(line) for line in (run / "rank-placement.jsonl").read_text().splitlines() if line.strip()]
assert sorted(row["rank"] for row in placement) == list(range(256))
hosts = Counter(row["host"] for row in placement)
assert len(hosts) == 2 and sorted(hosts.values()) == [128, 128]
assert all(len(row["affinity"]) == 1 for row in placement)
assert len({(row["host"], tuple(row["physical_core"])) for row in placement}) == 256
for block in range(2):
    block_hosts = {row["host"] for row in placement if row["rank"] // 128 == block}
    assert len(block_hosts) == 1
assert len({row["host"] for row in placement if row["rank"] < 128}) == 1
assert len({row["host"] for row in placement if row["rank"] >= 128}) == 1
assert next(iter({row["host"] for row in placement if row["rank"] < 128})) != next(
    iter({row["host"] for row in placement if row["rank"] >= 128})
)

environment = (run / "environment.log").read_text()
assert "AMD EPYC 7713" in environment
nodefile = (run / "pbs-nodefile.txt").read_text().splitlines()
assert len(nodefile) == 256 and sorted(Counter(nodefile).values()) == [128, 128]


def check_stage(path):
    text = path.read_text()
    assert re.search(r"^End\s*$", text, re.M), path
    assert "FOAM FATAL" not in text and "died from signal" not in text, path
    assert "OPENFOAM=2512" in text and "scalar=64" in text, path
    assert re.search(r"^nProcs\s*:\s*256\s*$", text, re.M), path
    assert re.search(r"Exit status:\s*0\s*$", text, re.M), path
    return text


results = {}
for role, case_name, method in (("control", "hierarchical", "hierarchical"),
                                ("candidate", "default_scotch", "scotch")):
    for stage_name in ("renumberMesh", "potentialFoam", "applyBoundaryLayer"):
        check_stage(run / f"{role}-init" / f"{stage_name}.log")

    case = run / role
    text = check_stage(case / "logFiles" / "simpleFoam.log")
    steps = [int(value) for value in re.findall(r"^Time = (\d+)\s*$", text, re.M)]
    assert steps == list(range(1, 81))
    timed = [float(value) for value in re.findall(
        r"Wall-clock time elapsed during the current time step = ([\deE.+-]+)", text
    )]
    average = float(re.search(r"Average wall-clock time per time step\s*=\s*([\deE.+-]+)", text)[1])
    assert len(timed) == 79 and all(math.isfinite(value) and value > 0 for value in timed)
    assert abs(statistics.mean(timed) - average) < 1e-10

    wall_rows = [list(map(float, line.split())) for line in
                 (case / "postProcessing/wallClockTimeStatistics/0/wallClockTime.dat").read_text().splitlines()
                 if line.strip() and not line.startswith("#")]
    assert [int(row[0]) for row in wall_rows] == list(range(2, 81))
    assert all(abs(value - row[2]) < 1e-10 for value, row in zip(timed, wall_rows))

    force_rows = [list(map(float, line.split())) for line in
                  (case / "postProcessing/forceCoeffsAll/0/coefficient.dat").read_text().splitlines()
                  if line.strip() and not line.startswith("#")]
    assert [int(row[0]) for row in force_rows] == steps
    assert all(math.isfinite(value) for row in force_rows for value in row)
    for field, iterations in (("Ux", 15), ("Uy", 15), ("Uz", 15), ("p", 12), ("omega", 8), ("k", 8)):
        counts = [int(value) for value in re.findall(r"Solving for " + field + r",.*?No Iterations (\d+)", text)]
        assert counts == [iterations] * 80, (role, field, Counter(counts))

    semantic = json.loads((case / "semantic-result.json").read_text())
    assert semantic["passed"] and semantic["steps"] == 80
    assert semantic["average_seconds_step"] == average
    assert semantic["final_Cd_dimensionless"] == force_rows[-1][1]

    before = json.loads((run / f"{role}-before.json").read_text())
    after = json.loads((run / f"{role}-after.json").read_text())
    assert before["files"] == after["files"]

    # Compare the replayable method source delivered in the frozen prep bundle.
    source = ROOT.parent / "nscc-cpu-three-cuts256-20261021" / "payload" / "cases" / case_name / "system"
    for source_file in source.rglob("*"):
        if source_file.is_file() and source_file.name != "controlDict":
            relative = source_file.relative_to(source)
            assert (case / "system" / relative).read_bytes() == source_file.read_bytes(), relative
    control = (case / "system/controlDict").read_text()
    assert re.search(r"^startFrom\s+startTime;", control, re.M)
    assert re.search(r"^endTime\s+80;", control, re.M)
    source_function = (source / "FOwallClockTimeStatistics").read_text()
    assert [item.strip() for item in re.findall(r"#\{(.*?)#\}", source_function, re.S)] == [
        item.strip() for item in re.findall(r"#\{(.*?)#\}", control, re.S)
    ]

    results[role] = {
        "method": method,
        "steps": 80,
        "measured_steps": 79,
        "average_seconds_step": average,
        "median_seconds_step": statistics.median(timed),
        "p95_seconds_step": statistics.quantiles(timed, n=100, method="inclusive")[94],
        "min_seconds_step": min(timed),
        "max_seconds_step": max(timed),
        "final_Cd_dimensionless": force_rows[-1][1],
        "native_solver_clock_seconds": float(re.findall(r"ClockTime = ([\d.]+) s", text)[-1]),
        "omega_bounding_messages": text.count("bounding omega"),
        "timing_confidence_warning": "smaller than the calculated one" in text,
        "initial_fields_unchanged": True,
    }

hours, minutes, seconds = map(int, accounting["resources_used"]["walltime"].split(":"))
elapsed = hours * 3600 + minutes * 60 + seconds
ratio = results["control"]["average_seconds_step"] / results["candidate"]["average_seconds_step"]
output = {
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "job": job,
    "state": "NATIVE_TWO_NODE_METHOD_PAIR_PASS",
    "nodes": sorted(hosts),
    "order": ["hierarchical", "scotch"],
    "results": results,
    "observed_control_over_candidate_step_time_ratio": ratio,
    "observed_candidate_step_time_reduction_percent": 100 * (1 - 1 / ratio),
    "elapsed_seconds": elapsed,
    "estimated_base_SU": elapsed * 256 / 3600,
    "reported_resources": accounting["resources_used"],
    "posted_individual_charge": "Not individually reported",
    "placement_records": placement,
    "limitations": (
        "One ordered two-node pair, no reverse repeat; cache/order/host drift remain. "
        "No four-node/150-step score. Partition method can change floating-point order and Cd; "
        "do not impose an invented universal accuracy tolerance. The affinity probe is outside "
        "solver timing and does not measure solver migration or page placement. Hardware "
        "bandwidth/cache/MPI counters and power were not collected. GNU time wraps the PALS launcher."
    ),
}
review_output.write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps({key: value for key, value in output.items() if key != "placement_records"}, indent=2))
