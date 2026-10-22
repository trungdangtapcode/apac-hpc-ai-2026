"""Gate fixed-work output and cross-check native timer samples and time function."""
from pathlib import Path
import json
import math
import re
import statistics
import sys

case = Path(sys.argv[1])
log = case / "logFiles/simpleFoam.log"
s = log.read_text()
steps = [int(x) for x in re.findall(r"^Time = (\d+)\s*$", s, re.M)]
assert steps == list(range(1, 41)), steps
for name, expected_iterations in [("Ux", 15), ("Uy", 15), ("Uz", 15),
                                  ("p", 12), ("omega", 8), ("k", 8)]:
    counts = [int(x) for x in re.findall(
        r"Solving for " + name + r",.*?No Iterations (\d+)", s
    )]
    assert counts == [expected_iterations] * 40, (name, counts)

# The native time function records WCT samples for Time=2..40 (39 samples).
# Match every log sample to the time-function file and independently recompute
# the reported mean; retain all samples and tail indices in semantic-result.
time_step = None
log_samples = []
for line in s.splitlines():
    time_match = re.match(r"^Time = (\d+)\s*$", line)
    if time_match:
        time_step = int(time_match.group(1))
    wct_match = re.match(
        r"^Wall-clock time elapsed during the current time step\s*=\s*([\deE.+-]+)\s*s\s*$",
        line,
    )
    if wct_match:
        assert time_step is not None
        log_samples.append((time_step, float(wct_match.group(1))))
expected_sample_times = list(range(2, 41))
assert [step for step, _ in log_samples] == expected_sample_times, log_samples

timer_path = case / "postProcessing/wallClockTimeStatistics/0/wallClockTime.dat"
timer_rows = []
for line in timer_path.read_text().splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    cols = [float(value) for value in line.split()]
    assert len(cols) == 3, cols
    timer_rows.append(cols)
assert [int(row[0]) for row in timer_rows] == expected_sample_times
log_values = [value for _, value in log_samples]
timer_values = [row[2] for row in timer_rows]
assert len(log_values) == len(timer_values) == 39
assert all(math.isfinite(value) and value > 0 for value in log_values + timer_values)
sample_checks = []
for (step, log_value), row in zip(log_samples, timer_rows):
    tolerance = max(1e-8, abs(row[2]) * 1e-10)
    assert abs(log_value - row[2]) <= tolerance, (step, log_value, row[2])
    sample_checks.append({"time_step": step, "log_seconds": log_value,
                          "time_function_seconds": row[2],
                          "absolute_difference_seconds": abs(log_value - row[2])})

accumulated = 0.0
accumulation_checks = []
for row in timer_rows:
    accumulated += row[2]
    tolerance = max(1e-8, abs(accumulated) * 1e-10)
    assert abs(row[1] - accumulated) <= tolerance, (row[0], row[1], accumulated)
    accumulation_checks.append({"time_step": int(row[0]), "reported_accumulated_seconds": row[1],
                                "recomputed_accumulated_seconds": accumulated})

average_match = re.search(
    r"Average wall-clock time per time step\s*=\s*([\deE.+-]+)", s
)
assert average_match, "Native average timer marker missing"
average = float(average_match.group(1))
sample_mean = statistics.mean(timer_values)
assert math.isfinite(average) and average > 0
assert abs(average - sample_mean) <= max(1e-8, abs(sample_mean) * 1e-10), (average, sample_mean)

force_path = case / "postProcessing/forceCoeffsAll/0/coefficient.dat"
force_rows = [
    [float(value) for value in line.split()]
    for line in force_path.read_text().splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]
assert [int(row[0]) for row in force_rows] == steps
assert all(math.isfinite(value) for row in force_rows for value in row)
cd = [row[1] for row in force_rows]
# A deliberately broad diagnostic sanity screen only; this is not an official
# Basic-tier accuracy tolerance and is not used for comparing arms.
cd_sanity_range = 0.3 < cd[-1] < 0.6
ranked = sorted(enumerate(timer_values, start=2), key=lambda pair: pair[1], reverse=True)
sorted_values = sorted(timer_values)
percentile = lambda q: sorted_values[math.ceil(q * len(sorted_values)) - 1]
result = {
    "passed": True,
    "steps": len(steps),
    "native_timer_samples": len(timer_values),
    "average_seconds_step": average,
    "recomputed_timer_sample_mean_seconds": sample_mean,
    "median_seconds_step": statistics.median(timer_values),
    "p95_seconds_step": percentile(0.95),
    "p99_seconds_step": percentile(0.99),
    "percentile_method": "nearest rank: sorted sample at ceil(q * n)",
    "max_seconds_step": max(timer_values),
    "slowest_five_samples": [{"time_step": step, "seconds": value}
                             for step, value in ranked[:5]],
    "log_vs_time_function_samples": sample_checks,
    "time_function_accumulation_checks": accumulation_checks,
    "force_rows": len(force_rows),
    "final_Cd_dimensionless": cd[-1],
    "broad_Cd_sanity_range": cd_sanity_range,
    "Cd_gate_scope": "Reported as a diagnostic only; not an official tolerance or pass gate.",
    "scope": "One-node ordered 40-step pair screen; no four-node score.",
}
result_path = Path(sys.argv[2]) if len(sys.argv) > 2 else case / "semantic-result.json"
result_path.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
