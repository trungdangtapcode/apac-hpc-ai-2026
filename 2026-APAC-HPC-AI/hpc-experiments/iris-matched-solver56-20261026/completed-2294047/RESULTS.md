# Iris comparison failed; retain the complete hierarchical reference

Job **2294047** ended FAILED / 124:0 after 2:04:02. This is not a successful completed pair. Hierarchical finished all 150 steps and 149 timed intervals. Scotch reached its 3,900-second per-solver limit during step 143; only steps 1–142 and 141 timed intervals completed. Its final End marker, full mean and post-run source hash are absent. The Slurm 2.5-hour limit was not reached.

| Measurement | Hierarchical | Scotch |
|---|---:|---:|
| Complete solver steps | 150 | 142 |
| Complete timed intervals | 149 | 141 |
| Full native mean, seconds/step | 21.8703015244 | unavailable |
| Mean on equal intervals 2–142, seconds/step | 21.8653891659 | 27.1272501866 |

Scotch took 24.06% longer on the matched prefix. That is an exploratory censored comparison, not the intended complete 150-step result. Preserve its failure and close this unchanged Scotch configuration on Iris. Fewer interface faces did not predict a better measured runtime. The data do not identify a causal kernel or memory bottleneck.

The H arm passes native 2512/scalar64/56-rank, 150-step, 149-timing, independent wall-clock series, finite Cd, exact fixed linear-iteration and source/copy checks. Its median is 21.806776234 seconds, p95 23.015001746 seconds and maximum 24.954151035 seconds. Final Cd is 0.2870700944, dimensionless. There are 116 bounding-omega messages; they remain in the raw log. These messages and finite output are not an organizer accuracy certification. The source dictionaries and all independent-copy hashes were retained.

The 216 archived artifacts match their byte counts and hashes. Slurm reports batch MaxRSS 142,664,880 KiB. Scheduler resource reports and per-arm GNU time observations are not memory-bandwidth, NUMA-traffic or per-kernel telemetry. No such hardware counters were collected.

A provenance limit applies to the old H input: its 21 October cut did not retain a full serial-mesh checksum at creation. Current dictionaries and all source partition files are hashed, but a shared serial-mesh pathname does not prove old byte identity. Add a fresh xyz control to future split-order tests with full canonical checks for every new case. This also limits the old static H/Scotch face-count comparison.

The whole allocation estimates 115.764444 CPU-hours. Retire its 140-hour maximum once and retain a rounded 116-hour planning allowance. The Iris branch now has 123 consumed planning hours, zero outstanding before the next admission and a 224-hour envelope. No Iris SU charge is inferred.

Replay with `python3 review.py`. The complete pair remains invalid even though the independently checked H arm is useful as a 150-step practice reference. Keep Iris and NSCC measurements separate.
