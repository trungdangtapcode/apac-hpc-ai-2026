# Four-node iteration-tail and output-cadence audit

## Question and prior evidence

The independent review of six four-node native runs found unusually long simpleFoam timing samples. This offline audit asks whether those samples line up with scheduled output, the beginning or end of the 150-step run, or recurring iteration clusters. It reuses every one of the 149 `wallClockTime` samples at Time 2 through 150 in each run. It adds descriptive checks only; it does not trim samples, run a significance test, or infer a cause.

The input data are the sealed [four-node review](../four-node-review-20261023/RESULTS.md), its full [machine-readable review](../four-node-review-20261023/review.json), and the corresponding [text archive](../four-node-review-20261023/collected/raw-text-evidence.tar.gz). `analyze.py` records the SHA-256 hashes of the review and archive in `audit.json`. Run it with Python 3 and the standard library:

```bash
python3 analyze.py
```

## What the case schedules

The six archived `controlDict` and active function-object files have the same relevant schedule. The main field write interval is 100,000 time steps, well beyond the 150-step run. Force coefficients, solver information, and 13 active probe objects (counted from each `controlDict` include list) explicitly write every time step; all 13 corresponding probe files are present with 150 data rows per run. The archived `minMax_U` and `minMax_p` outputs each have 150 rows in all six runs. `calc_cp` uses `writeTime`, but no matching artifact is present in the collected text archive; `wallShearStress` also uses `writeTime`, and its present output file contains only a header. Those file observations do not establish whether either function object did work in its execute callback. The wall-clock function records 149 measurements, Time 2–150.

Therefore there is no sparse, periodically scheduled file-output event that uniquely marks the slow iterations. Most measured iterations do include the same recurring per-step function-object work, so the data cannot exclude it as part of total timing. The logs do not time each function object separately.

The wall-clock function is first in the `functions` include order. Its code excludes the first callback, measures elapsed time since the previous callback, then updates its clock. The value written at Time *t* is thus an interval measurement: it includes step work and the later function-object work between callbacks, not an isolated timing of an output action at Time *t*. A same-index comparison between that row and another function object's Time *t* output is not enough to claim the output caused the delay.

## Timing pattern

Every run's maximum is in the broad interior of the solve (Time 35–130), not in the first 10 or last 10 measured iterations. IQR outliers occur in some edge windows and more frequently in the longer middle window, but the rates do not give a common start-up or shutdown pattern. Some individual runs have short consecutive outlier groups; their locations differ. IQR-outlier counts in the start/middle/end windows are: Scotch-128 1/9/1, Scotch-64 0/23/0, Scotch-96 3/28/2, hierarchical-128 0/19/0, hierarchical-96 2/27/2, and hierarchical-64 0/27/1 (window sizes 10/129/10). The most repeated outlier index is Time 75, classified as an IQR outlier in four runs, but its measured time ranges from 3.27 to 16.19 seconds across the six runs. Time 100 and 130 are outliers in three runs each. These are descriptive coincidences across different allocations, not a tested periodic effect. Only Time 100 occurs in the top-three slowest samples of more than one run (two runs).

| Job | Method / ranks per node | Average (s/step) | IQR outlier samples | Maximum (Time) | WCT / rounded ClockTime delta / ExecutionTime delta at maximum |
|---|---|---:|---:|---|---:|
| 25921488 | Scotch / 128 | 3.677907 | 11 | 35.883552 (119) | 35.88 / 36 s / 3.25 s |
| 25921517 | Scotch / 64 | 10.309944 | 23 | 72.923052 (86) | 72.92 / 72 s / 6.91 s |
| 25921518 | Scotch / 96 | 7.146019 | 33 | 31.677264 (130) | 31.68 / 31 s / 5.78 s |
| 25921692 | Hierarchical / 128 | 3.819929 | 19 | 12.925347 (129) | 12.93 / 13 s / 3.51 s |
| 25921905 | Hierarchical / 96 | 4.922348 | 31 | 38.847831 (97) | 38.85 / 39 s / 3.47 s |
| 25921906 | Hierarchical / 64 | 4.488921 | 28 | 20.984311 (35) | 20.98 / 21 s / 3.47 s |

The native cumulative `ClockTime` deltas track the long wall-clock events closely, while `ExecutionTime` deltas at those same points are about 3.25–6.91 seconds. `ClockTime` is reported only to whole seconds and `ExecutionTime` to hundredths; they are not per-rank instrumentation. This difference is compatible with elapsed time not spent executing on the reporting process, but it does not distinguish MPI waiting, filesystem delays, operating-system scheduling, rank imbalance, or another cause. It is not evidence that the fabric or any node was unhealthy.

The job's logger recommended 943–8,329 samples for its stated 2%-at-95%-confidence target; each run supplied 149 and emitted the corresponding warning. The task endpoint is still fixed at 150 steps. This audit does not recommend extending the ranked endpoint or dropping outliers.

## Assessment and next hypothesis

The retained case setup does not support a hypothesis that rare slow steps are caused by a sparse, periodic function-output event: the main field-write interval is outside the run, while several function objects operate each step. The extreme values are not concentrated at run start or finish. Some outlier indices recur, including Time 75, but their size is not consistent across runs and the timing callback spans work across adjacent function-object phases. No causal interpretation is justified.

A defensible next **stability** hypothesis is narrower: under an unchanged four-node Scotch-128/512-rank, 150-step setup, the long wall-time tail may recur across independent allocations even when the slow iteration index changes. The root's 23 October 15:26:36 UTC snapshot records job 25940700 as Q/q5 for that confirmation; it is not a result, and this offline audit does not inspect or alter live scheduler state. After its retained logs become available, compare every sample, median, p95, maximum, and `ExecutionTime`/`ClockTime` context with the sealed Scotch-128 run. Treat two allocations as a stability screen, not enough replications for a general variance estimate.

If another stability experiment is later justified and separately authorized, retain the exact source, 150-step endpoint, function objects, and rank layout. Add bounded per-rank timing and system measurements only after validating their overhead separately; aggregate master-process timing cannot identify which rank or service delayed a step. Stop this branch if timing tails do not recur or if the required instrumentation cannot be collected without changing the ranked workload. The six native records lack final PBS history, so this audit makes no terminal elapsed-time or cost claim and requests no new allocation.

## Beginner explanation

The solver reports one elapsed duration per iteration. OpenFOAM also runs several measurement and output functions during the loop. Because those functions run on every step, a slow step's duration includes more than the equation solves alone. The custom stopwatch is called before the other configured functions and measures from one call to the next, so its time label is not a stopwatch dedicated to one file write. The long samples occur at different points in the six runs; a few indices repeat, but their durations vary. We can say the tail is real in the retained logs and warrants a same-configuration repeat. We cannot say which hardware or software component caused it.

## Reproducibility and limits

`audit.json` contains the original 894 measured samples with their time indices and seconds, each run's IQR labels, phase summaries, repeated-index counts, only the active function-object schedule, the row counts for each active probe output across all six runs, presence-versus-absence status for selected other output files, and native cumulative timing deltas parsed from the six solver logs. `analyze.py` validates each series has exactly Times 2–150 and expects one solver log per run. Inputs remain unchanged.

The six runs are separate allocations with different methods and rank densities, not matched repeats. The `wallClockTime` measurements are the timer's intervals, and the native `ExecutionTime`/`ClockTime` values are rounded cumulative log fields. No per-function timing, per-rank step duration, physical affinity map, page residency, filesystem telemetry, CPU-frequency trace, MPI-wait breakdown, PBS terminal state, allocation elapsed time, or posted charge is available. IQR labels and phase bins are descriptive summaries, not confidence intervals or causal tests. The official rules require retaining function objects and fixed solver work; this report proposes no change to either.

Sources: [pinned OpenFOAM rules, F1 fixed work and function-object requirement](../upstream-20261021/sources/2.%20OpenFOAM%20HPC%20Task%20Rules.md), [sealed native evidence review](../four-node-review-20261023/RESULTS.md), and its [collection provenance](../four-node-review-20261023/COLLECTION.md).
