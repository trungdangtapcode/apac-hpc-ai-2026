# zyx remains stable through 50 complete steps

**Iris 2294148 completed 0:0** on iris009 in 1,224 allocated seconds, with 56 CPUs. Independent replay validates 122 retained artifacts, all frozen runtime hashes, unchanged source and isolated copy snapshots, exactly 50 steps and 49 timings, required fixed numerical iterations, every Cd row and independent wall-clock function output.

| Observation | Value |
|---|---:|
| Mean time per measured step | 21.112004724 s |
| Median | 21.062013150 s |
| p95 | 21.248222475 s |
| Maximum | 21.251439360 s |
| Population standard deviation | 0.088060289 s |
| Steps 2–30 mean, 29 intervals | 21.068213278 s |
| Steps 31–50 mean, 20 intervals | 21.175502321 s |
| Later versus earlier mean time change | +0.509246% |
| Final step-50 Cd, dimensionless | 0.400779301 |
| Retained bounding-omega messages | 15 |

The later window shows no large timing collapse within this run. It is a single zyx horizon check, not a matched 50-step speedup or full 150-step result. Earlier pairs used iris001; this run used iris009. Do not call the change from 22.29 to 21.11 seconds an optimization gain caused by the configuration. Every early Cd row through step 30 exactly reproduces the preceding zyx run, which supports repeatability of that short numerical trajectory, not official accuracy or convergence. Bounding warnings remain visible.

The native timer prints a minimum sample recommendation of zero. The retained function source computes `round((1.96 * stddev / (0.02 * mean))^2)`: the unrounded value here is 0.167091137. Zero results from rounding; it is not zero variance and does not mean no samples or repetitions are needed. All 49 observations are retained.

GNU time reports 5,550% CPU, maximum RSS 3,018,652 KiB, 382,119 major faults, 375,328 filesystem inputs and zero swaps for its observed process tree. Whole-node VM deltas are 51,338,851 page faults, 8,610 major faults and zero swap-in/out events between the snapshots. These scopes differ; they do not establish a memory bottleneck. Snapshot read/construction durations are 0.431 and 0.845 ms, outside native solver timing. Slurm batch MaxRSS is 140,963,908 KiB, not a per-rank sum. No memory bandwidth, NUMA residency, helper-thread or in-solver mask sampling was collected. Prelaunch probes show 56 distinct singleton masks only. Startup stderr retains the missing dynamic timing library message followed by successful runtime compilation and complete timing output.

Cost estimate is **19.04 allocated CPU-hours**. Retire this job's 24.266667-hour maximum once and retain a rounded 20-hour allowance. Iris consumed allowance is **219 of 224**, with **5 CPU-hours** remaining and no outstanding reservation. SU rate and posted SU charge remain unknown. A full 150-step confirmation or another matched short pair cannot fit this remainder. Keep it for a justified bounded validation if needed; do not fill the queue with arbitrary shorter solver runs. Main optimization continues on the separately funded NSCC CPU project.

Run `python3 replay.py` to verify the retained archive and manifest without accessing Iris. The archive includes the small text evidence and byte seals; initialized fields and the canonical mesh remain remote. No submission materials or official result changed.
