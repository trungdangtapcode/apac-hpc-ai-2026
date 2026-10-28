#!/usr/bin/env python3
"""Native output gates for the explicitly non-scored 14-step placement screen."""
from __future__ import annotations

import json
import math
import pathlib
import re
import statistics


STEPS = 14
EXPECTED_ITERATIONS = {"Ux": 15, "Uy": 15, "Uz": 15, "p": 12, "k": 8, "omega": 8}
FATAL = re.compile(r"FOAM FATAL|FOAM ERROR|MPI_ABORT|died from signal|\bSIGFPE\b|floating point exception occurred|core dumped", re.I)


def review(arm: pathlib.Path) -> dict:
    log = (arm / "simpleFoam.log").read_text(errors="replace")
    stderr = (arm / "solver.stderr").read_text(errors="replace")
    resource = (arm / "resource-time.log").read_text(errors="replace")
    if "OPENFOAM=2512" not in log or "scalar=64" not in log:
        raise ValueError("native solver log lacks OpenFOAM 2512 / scalar=64 identity")
    if FATAL.search(log + "\n" + stderr + "\n" + resource) or not re.search(r"(?m)^End\s*$", log):
        raise ValueError("native solver error/fatal marker or missing End")
    if not re.search(r"(?m)^nProcs\s*:\s*56\s*$", log) or not re.search(r"\(iris\S+\s+56\)", log):
        raise ValueError("solver log does not confirm 56 ranks on one Iris host")
    times = [int(x) for x in re.findall(r"^Time = (\d+)\s*$", log, re.M)]
    if times != list(range(1, STEPS + 1)):
        raise ValueError(f"expected native steps 1..{STEPS}, got {times}")
    timings = [float(x) for x in re.findall(r"Wall-clock time elapsed during the current time step = ([\deE.+-]+)", log)]
    if len(timings) != STEPS - 1 or not all(math.isfinite(x) and x > 0 for x in timings):
        raise ValueError(f"expected {STEPS - 1} finite, positive native timings for steps 2..{STEPS}")
    average = re.search(r"Average wall-clock time per time step\s*=\s*([\deE.+-]+)", log)
    if not average or abs(statistics.mean(timings) - float(average[1])) >= 1e-9:
        raise ValueError("reported average does not match the 17 native timing samples")
    counts: dict[str, list[int]] = {}
    for field, count in re.findall(r"Solving for (\w+),.*?No Iterations (\d+)", log):
        counts.setdefault(field, []).append(int(count))
    if counts != {field: [count] * STEPS for field, count in EXPECTED_ITERATIONS.items()}:
        raise ValueError("fixed-iteration solver counts changed or are incomplete")
    wall_path = arm / "postProcessing/wallClockTimeStatistics/0/wallClockTime.dat"
    wall = [list(map(float, line.split())) for line in wall_path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]
    if [int(row[0]) for row in wall] != list(range(2, STEPS + 1)):
        raise ValueError(f"wall-clock function object must contain steps 2..{STEPS}")
    if any(not math.isfinite(value) for row in wall for value in row):
        raise ValueError("wall-clock function object contains non-finite values")
    if any(abs(timing - row[2]) >= 1e-8 for timing, row in zip(timings, wall)):
        raise ValueError("function-object wall times differ from the native solver log")
    cd_path = arm / "postProcessing/forceCoeffsAll/0/coefficient.dat"
    cdrows = [list(map(float, line.split())) for line in cd_path.read_text().splitlines()
              if line.strip() and not line.lstrip().startswith("#")]
    if len(cdrows) != STEPS or [int(row[0]) for row in cdrows] != times:
        raise ValueError(f"force-coefficient file must contain one row per step 1..{STEPS}")
    if any(not math.isfinite(value) for row in cdrows for value in row):
        raise ValueError("force-coefficient output contains non-finite values")
    if "Exit status: 0" not in resource or "Maximum resident set size (kbytes):" not in resource:
        raise ValueError("GNU time did not record a successful exit and peak RSS")
    return {"passed": True, "steps": STEPS, "timed_intervals": len(timings),
            "mean_seconds_per_step": statistics.mean(timings),
            "median_seconds_per_step": statistics.median(timings),
            "p95_seconds_per_step": sorted(timings)[math.ceil(0.95 * len(timings)) - 1],
            "maximum_seconds_per_step": max(timings), "timings_seconds": timings,
            "Cd_rows": len(cdrows), "Cd_by_step": cdrows,
            "fixed_iterations_each_step": EXPECTED_ITERATIONS,
            "gnu_time_exit_zero": True}


if __name__ == "__main__":
    import sys
    result = review(pathlib.Path(sys.argv[1]))
    print(json.dumps(result, indent=2, sort_keys=True))
