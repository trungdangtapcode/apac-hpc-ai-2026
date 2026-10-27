# zyx remains faster after reversing the short-run order

**Iris 2294132 completed 0:0**, 1,870 allocated seconds on iris001, 56 CPUs. Independent replay verifies **235 retained artifacts**, the frozen 49 runtime files, both isolated copies and unchanged sources, exact fixed numerical iterations, 30 steps / 29 native timings, all Cd rows and complete wall-clock output. No official score is claimed.

| Metric | zyx, first | xyz, second |
|---|---:|---:|
| Mean seconds per step | 22.290292514 | 28.367224538 |
| Median seconds per step | 22.348601405 | 27.715990749 |
| p95 seconds per step | 23.260834934 | 30.640599892 |
| Maximum seconds per step | 23.969119154 | 43.251220575 |
| Final step-30 Cd, dimensionless | 0.437604579 | 0.441369407 |
| Native recommended minimum measured samples | 8 | 111 |
| Actual measured samples | 29 | 29 |
| GNU time major page faults | 382,200 | 124,805 |
| GNU time filesystem inputs | 382,464 | 157,736 |
| GNU time CPU percentage | 5,531% | 5,548% |
| Whole-node pgmajfault delta between snapshots | 8,715 | 4,677 |
| Whole-node pswpin / pswpout delta | 0 / 0 | 0 / 0 |

zyx took **21.4224% less time** in this reverse-order pair. The preceding xyz-then-zyx pair observed a 26.9434% reduction. The direction therefore survives swapping the first and second positions. This weakens a simple explanation that only the second run benefits, and supports retaining zyx as the preferred screened candidate. It does not establish a general speedup, an official score or an equal-sample full 150-step result. The xyz control is again below its native recommended sample count. Preserve its 43.25-second slow interval.

The page-fault pattern also reverses: zyx now has more GNU time major faults and filesystem inputs yet remains faster. The earlier association between fewer faults and lower runtime does not provide a sufficient causal explanation. Whole-node vmstat deltas have a different collection window and scope from process-tree GNU time counters; do not equate or sum them. Four procfs read/metadata construction durations range from 0.294 to 0.569 milliseconds, outside native solver timing. This does not measure all write cost or certify zero monitoring impact. No hardware bandwidth, NUMA residency, kernel profile or in-solver CPU-mask telemetry was collected.

Prelaunch probes observe 56 distinct singleton masks; this does not prove post-MPI solver binding. Both native stderr streams retain the initial missing dynamic timing library message, followed by successful runtime compilation and all 29 timing outputs. Fixed work remains Ux/Uy/Uz 15, p 12, k/omega 8 per step. Each decomposition's final Cd exactly repeats its earlier step-30 result. This supports reproducibility of the short numerical trajectory, not official accuracy or convergence at step 150.

The allocation cost estimate is **29.088889 CPU-hours**; retire only its 42-hour maximum and retain a rounded 30-hour allowance. Iris cumulative consumed allowance is **199 of 224**, leaving **25 CPU-hours** before another reservation. SU rate and actual posted SU charge remain unknown. Full 150-step confirmation does not fit this remainder at the measured rate.

Next: a single zyx 50-step horizon extension can fit a 26-minute maximum (24.266667 CPU-hours). It asks whether native throughput and transient numerical work persist beyond step 30. It must keep all source, work and output gates, report the initial and later windows without dropping timings, and remain explicitly unmatched at 50 steps. It cannot close the missing full-length control or official accuracy gates. No budget increase is inferred.

Recovery: `raw-evidence.tar.gz`, `collection.json`, `replay.py` and `review.json` retain and verify the exact small records. Large mesh and initialized fields remain remote with seals and reproducible staging; Git contains the retained text evidence, not those large binary trees.
