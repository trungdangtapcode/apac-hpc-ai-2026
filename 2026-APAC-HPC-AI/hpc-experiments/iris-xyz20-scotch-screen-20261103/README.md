# Prepared measurement: Iris hierarchical xyz versus Scotch directional screen

This document describes a frozen preparation. It does not report deployment or scheduler acceptance; see `STATUS.md`.

**Prepared only. No deployment, job receipt, reservation, or new result is included.** This is a bounded, one-node solver screen after the Scotch weight-only branch. It is not a confirmatory benchmark.

## Question and evidence

Does the standard OpenFOAM hierarchical decomposition `(7 4 2), order xyz` run faster than the accepted default Scotch decomposition on the same Iris setup? This is a parameter comparison using a standard method, not a new algorithm.

The distinct direct comparison is missing. Full-length jobs 2294234 and 2294262 compared hierarchical orders, not hierarchy against Scotch, and the first arm was faster in both temporal orders. Retained xyz means were 26.9538 and 21.8239 seconds per step in separate allocations; these are observations, not evidence of an xyz advantage. Own zyx and xzy comparisons against Scotch failed to show stable gains, so this screen tests one distinct, already initialized xyz partition rather than reopening either losing result.

The separate Scotch weight branch has now also closed. Job 2294670 completed the 100:1 native cut/filter in 280 seconds: logical cross-package faces decreased 5.07289%, but maximum neighbor patches rose from 20 to 24, failing the fixed maximum increase of two. It produced no READY tree or solver result. This graph filter is only triage evidence; it neither predicts timing nor justifies more weight sweeps.

## Exact control and candidate sources

- Control: `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z/artifacts/ready-N56-scotch` with its accepted 1,040-file source manifest and 336-field seal from the reviewed own Scotch comparison.
- Candidate: `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-order-init-20261026T133526Z/initialized/order-xyz`. The frozen candidate source manifest is taken from the retained 2294262 `source-before.json`; its `source-after.json` matches exactly (1,040 regular files plus the canonical mesh symlink). The independent 2294262 source check confirms order `xyz`, factors `(7 4 2)`, and all 41 canonical input pins. Its initialized copy has 336 time-zero field seals and a retained READY marker.

This is provenance evidence from completed prior runs, not a claim that the remote source was re-hashed by this preparation session. The scheduled run must re-check each full source manifest and time-zero fields before and after measurement, then verify isolated-copy hashes and inodes.

## Run plan and gates

One exclusive Iris node, 56 MPI ranks, zero GPUs. Run `Scotch / xyz / xyz / Scotch` (ABBA); each arm performs 20 steps and retains all 19 native timing intervals. Use the same OpenFOAM v2512 double-precision build, plain default MPI launcher, uncollated I/O, original 65M mesh, physics, fixed iteration controls, and function objects. The only workload edit is setting `endTime=20` on each isolated arm copy. Partitioned meshes and initialized fields necessarily differ by decomposition.

Every arm must complete normally and pass the native `End`, version/precision/rank, 20-step and 19-timing checks, wall-clock file agreement, fixed-iteration counts, 20 finite Cd rows, actual I/O handler, resource log, source/copy/field seals and runtime-library identity checks. Keep every slow interval and inspect distributions, tails, temporal windows, solver stderr, available node snapshots and resource counters. Missing hardware counters remain uncollected.

The resource ceiling is 60 minutes / 56 allocated CPU-hours. Internal deadline 3,510 seconds, wrapper 3,540 seconds, scheduler 3,600 seconds; per-arm solver cap 720 seconds, with 810 seconds protected for each remaining arm and 120 seconds final reserve. The four protected arm windows plus reserve require 3,360 seconds, leaving 150 seconds for validation and setup. Prior job 2294640 measured about 70 seconds of initial source and canonical-input checks; source-manifest scans took 27.4 and 32.6 seconds. Each isolated copy took 11.6–15.2 seconds and its full hash verification 27.3–27.4 seconds. Stop before an arm if its full cap cannot be protected.

Based on the completed 40-step ABBA job 2294640, four 20-step arms are expected to take roughly 2,787 seconds / 43.4 allocated CPU-hours if solver work scales linearly and prior fixed setup cost repeats. This is a planning estimate, not a runtime guarantee. The 56-hour ceiling retains margin for slower arms and source verification; the job must abort rather than truncate a protected arm.

## Interpretation limit and telemetry

This is a directional screen only. The old xyz run recommended 361 native timing samples; 19 observations fall far short. Prior job 2294640 had Scotch control repeats drift **+40.64%**, candidate repeats **+13.14%**, and adjacent comparisons of **+24.44%** versus **+0.10%**. A 20-step screen cannot resolve a 10% configuration effect against that observed drift. ABBA reduces simple order confounding but one short allocation cannot establish a stable effect. No favorable pooled ratio is sufficient for promotion.

The prior job's strongest drift-associated clue was GNU-time major page faults increasing A1/B1/B2/A2 as **6,688 / 11,584 / 99,648 / 341,798**, while file-system inputs rose **4,032 / 9,032 / 189,960 / 380,304**. Aggregate CPU use remained about 55.4–55.6 cores; command maximum RSS was 2.89–3.00 GB. Outside-arm node snapshots showed about 171–175 GB available of 196.6 GB and median sampled CPU frequency of 4,000 MHz. Those snapshots are not measurements during solver intervals. The page-fault and input counters correlate with later slow arms but do not prove cache eviction, filesystem contention, memory pressure or another cause. Hardware bandwidth, sustained frequency, per-step memory pressure, page residency and helper affinity were not collected.

The wider 12-arm audit changes how that single-job pattern should be read: page faults and file-input counts do **not** consistently track time. In the reverse xzy run, a fast Scotch arm also had high GNU major-fault and input counts. See `/home/apacsc42/workspace/reports/hpc-next-directions-20261103/README.md` and `EVIDENCE.json`; do not treat 2294640's covariation as causal.

This diagnostic preparation adds a separate sampler process every five seconds during each solver arm. It reads only whole-node aggregate `/proc/meminfo`, `/proc/vmstat`, the aggregate `/proc/stat` CPU row, `/proc/cpuinfo` frequency values, and `/proc/pressure/{cpu,io,memory}` when present. Memory keys are kB; vmstat counters are raw kernel page/event counters; CPU values are aggregate scheduler ticks; pressure totals retain the kernel's microsecond unit. Optional pressure files and missing metrics are explicitly marked unavailable. No process-specific `/proc/<pid>` data, `numa_maps`, affinity changes, governor changes or cache drops are used.

Before the first solver, five read samples must each finish within 50 ms and all four required sources must parse. If a read exceeds the cost gate or a required source is missing, sampling is disabled for all arms and the reason is recorded. The sampler starts just before each solver and is stopped and reaped in a `finally` path, including launch errors/timeouts. Per-arm JSONL is capped below 2 MB and the collector validates its rows. `collection_ms` measures only the sampler's read duration; it is **not** a true estimate of observer interference. This job's timings are diagnostic, not contest-ranked timings, and whole-node counters cannot be assigned to one rank or process.

A favorable short screen would justify only a better controlled follow-up, if more authorized CPU-hours become available. It cannot establish an optimization, contest score improvement, NSCC result or Gadi prediction.
