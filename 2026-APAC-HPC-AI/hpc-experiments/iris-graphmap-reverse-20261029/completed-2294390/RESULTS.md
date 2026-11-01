# Reverse graph-placement screen: no reproduced gain

Job 2294390 completed 0:0 on iris005, 2,009 seconds, 56 CPUs. All 397 selected transfer hashes and independent native replays pass. Each arm has 14 steps / 13 intervals. This is a practice-cluster screen, not a scored run.

| Position | Treatment | Mean s/step | Median s/step | Maximum s/step |
|---|---|---:|---:|---:|
| B1 | Graph mapping | 21.051169 | 21.029651 | 21.200120 |
| A1 | Identity mapping | 23.241965 | 23.370882 | 24.395179 |
| A2 | Identity mapping | 33.239424 | 33.333679 | 34.102356 |
| B2 | Graph mapping | 38.462425 | 32.422828 | 92.360908 |

Candidate aggregate is 5.3685% slower than control in BAAB, whereas parent ABBA appeared 18.5027% faster because of a slow last control. Repeat drift is +43.0147% for control and +82.7092% for candidate. These one-allocation short cycles do not establish a robust mapping benefit. Close the unchanged graph-placement performance branch; preserve its source/mapping qualification as mechanism evidence.

Source/copy isolation, initialized fields, native fixed iteration counts, Cd and executable/library identities pass. Same-treatment Cd repeats exactly, cross-treatment differences are approximately 1e-15. Sample recommendations are 0 / 14 / 3 / 1670 versus 13 observations. CPU utilization from GNU time is command aggregate, not frequency or bandwidth. Frequency, per-rank bandwidth, NUMA page residency and solver helper affinity were not collected. Slurm stderr contains an energy-monitor socket timeout, so energy telemetry is unavailable; this did not change terminal 0:0 or the passing native output checks. No causal explanation of the timing drift is established.

Cost: 31.251111 allocated CPU-hours, conservatively charged 32 in the local planning ledger; original 46.666667 maximum retired exactly once. This is not a billed SU amount. Next useful accessible experiment should test a distinct native setting from the supplied Gadi recipe with the same initialized work and a matched control, rather than repeating this losing mapping branch.
