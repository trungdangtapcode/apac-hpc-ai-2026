# Recomputed public reference observations

These are organiser measurements, not our jobs. Reported Average matches all per-step samples; the first solver step is excluded by the case timer. Columns have seconds/step, seconds and dimensionless Cd units.

| Platform | Reference | Ranks | Steps | Average (s/step) | Cd | Max step (s) | Signal 7 in solver log |
|---|---|---:|---:|---:|---:|---:|---|
| Gadi normalsr | hierarchical-1node | 104 | 40 | 8.604779 | 0.439931770 | 8.772 | not found |
| Gadi normalsr | hierarchical-2node | 208 | 80 | 4.249190 | 0.335041277 | 4.340 | not found |
| Gadi normalsr | hierarchical-4node | 416 | 150 | 2.379600 | 0.289984638 | 2.573 | not found |
| Gadi normalsr | reuse-scotch-4node | 416 | 150 | 2.087689 | 0.291876224 | 2.218 | not found |
| Gadi normalsr | scotch-1node | 104 | 40 | 8.477926 | 0.438060067 | 8.585 | not found |
| Gadi normalsr | scotch-2node | 208 | 80 | 4.213002 | 0.339635693 | 4.272 | not found |
| Gadi normalsr | scotch-4node | 416 | 150 | 2.126043 | 0.291876082 | 6.477 | not found |
| ASPIRE-2A CPU | hierarchical-1node | 128 | 40 | 14.668759 | 0.438932328 | 15.106 | not found |
| ASPIRE-2A CPU | hierarchical-2node | 256 | 80 | 7.117703 | 0.336868972 | 7.862 | yes, after End |
| ASPIRE-2A CPU | hierarchical-4node | 512 | 150 | 3.414517 | 0.273919743 | 3.914 | yes, after End |
| ASPIRE-2A CPU | nosrx-hierarchical-4node | 512 | 150 | 3.440401 | 0.273919743 | 3.920 | not found |
| ASPIRE-2A CPU | nosrx-scotch-4node | 512 | 150 | 3.210833 | 0.283983008 | 3.340 | not found |
| ASPIRE-2A CPU | noxrc-hierarchical-4node | 512 | 150 | 3.511588 | 0.273919743 | 3.959 | not found |
| ASPIRE-2A CPU | noxrc-scotch-4node | 512 | 150 | 3.244753 | 0.283983008 | 3.728 | not found |
| ASPIRE-2A CPU | reuse-scotch-4node-1 | 512 | 150 | 3.292459 | 0.283983008 | 6.671 | yes, after End |
| ASPIRE-2A CPU | reuse-scotch-4node-2 | 512 | 150 | 3.212923 | 0.283983008 | 3.302 | yes, after End |
| ASPIRE-2A CPU | reuse-scotch-4node-3 | 512 | 150 | 3.208243 | 0.283983008 | 3.421 | yes, after End |
| ASPIRE-2A CPU | scotch-1node | 128 | 40 | 14.048605 | 0.435988836 | 14.480 | not found |
| ASPIRE-2A CPU | scotch-2node | 256 | 80 | 7.195928 | 0.327129810 | 7.982 | yes, after End |
| ASPIRE-2A CPU | scotch-4node | 512 | 150 | 3.575991 | 0.283983008 | 4.008 | yes, after End |
| ASPIRE-2A CPU | scotch-split-4node | 512 | 150 | 3.190658 | 0.283983008 | 3.266 | yes, after End |

## Partition evidence on four-node full chains

| Platform | Reference | Maximum cells above mean (%) | Unique partition faces | Maximum neighbor count | Maximum processor faces |
|---|---|---:|---:|---:|---:|
| Gadi normalsr | hierarchical-4node | 0.001 | 4107654 | 18 | 145589 |
| Gadi normalsr | scotch-4node | 1.137 | 2690403 | 49 | 24462 |
| ASPIRE-2A CPU | hierarchical-4node | 0.002 | 4306118 | 20 | 119912 |
| ASPIRE-2A CPU | nosrx-hierarchical-4node | 0.002 | 4306118 | 20 | 119912 |
| ASPIRE-2A CPU | nosrx-scotch-4node | 1.072 | 2927022 | 66 | 22214 |
| ASPIRE-2A CPU | noxrc-hierarchical-4node | 0.002 | 4306118 | 20 | 119912 |
| ASPIRE-2A CPU | noxrc-scotch-4node | 1.072 | 2927022 | 66 | 22214 |
| ASPIRE-2A CPU | scotch-4node | 1.072 | 2927022 | 66 | 22214 |
| ASPIRE-2A CPU | scotch-split-4node | 1.072 | 2927022 | 66 | 22214 |

All raw partition interfaces are reciprocal and their face sum matches the reported unique interface count. Rank-to-node mapping is not independently available, so these counts are not measured network traffic.

A completed solver with a teardown signal is retained as such, not relabelled as a clean end-to-end job. Future runs should use the documented MPI remedy, check every exit code and inspect semantic artifacts. Do not ignore arbitrary errors because End appears.
