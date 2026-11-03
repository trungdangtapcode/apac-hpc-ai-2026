# Terminal review: failed four-arm screen

Job **2294671** ended `FAILED`, exit code `1:0`, after 2,202 seconds on Iris node `iris001` with 56 allocated CPUs. The retained capture contains 173 files. Independent replay verified every file's recorded size and SHA-256, the raw evidence archive SHA-256, and all 62 frozen runtime file hashes. See [REVIEW.json](REVIEW.json) and rerun its deterministic replay with `python3 replay_partial.py` from this directory.

The planned arm order was S1 Scotch, X1 hierarchical xyz, X2 hierarchical xyz, S2 Scotch. S1 and X1 completed with return code zero and pass the native output checks: 20 steps, 19 timed intervals, matching wall-time tables, fixed solver iteration counts, finite force-coefficient rows, 56 ranks on one Iris host, and successful resource logs. X2 printed all 20 step markers, 19 intervals, and an `End` marker, but its timed command returned **124 at the 720-second cap** and did not print `Finalising parallel run`. The runner then asserted on the nonzero return code and stopped. X2 is an invalid timed-out arm despite its printed mean. S2 was never started. The four-arm comparison, final runtime check, and source-after gates were not reached.

## Solver output and comparison

| Arm | Output status | Mean seconds/step | Median | Maximum | Intervals |
|---|---|---:|---:|---:|---:|
| S1 Scotch | Complete, return code 0 | 33.672468 | 34.252735 | 41.560603 | 19 |
| X1 hierarchical xyz | Complete, return code 0 | 25.585999 | 25.519302 | 26.832310 | 19 |
| X2 hierarchical xyz | Printed summary only; return code 124 at cap | 34.792585 | 34.590445 | 36.356271 | 19 printed |

X1 was **24.015% faster than the immediately preceding S1** in this one adjacent contrast. X2's printed mean is **35.983% slower than X1**; it is descriptive evidence from a failed arm, not a valid repeat or a treatment result. Comparing its printed mean with S1 would be +3.327%, also invalid as a completed-arm comparison. With no S2 and the X2 timeout, there is no pooled ABBA estimate and no reproduced xyz speedup.

Final `Cd` was 0.4416818095 for S1 and 0.4439974485 for X1 and X2. The full 20-row force-coefficient tables for X1 and X2 are exactly equal. X1's final `Cd` is 0.524% higher than S1's. This is a short diagnostic output comparison, not a scored result or a claim of physical equivalence.

For S1 and X1, the 336 restored time-zero field seals match their respective method-specific source field manifests. The two layouts are different, so their byte maps are not a direct cross-layout field-equivalence test. These seals cover time-zero inputs, not final evolved solver fields. X2 has no post-solve field-seal artifact, and the final solution fields were not retained for any arm.

The native sample recommendations were 50 measured steps for S1, 7 for X1, and 2 in X2's printed output. The valid arms each have only 19 measured intervals; the X2 recommendation does not override its timeout. S1's 41.56-second maximum also contributes to its variation. These short results do not support a stable gain claim.

## Per-arm resource records

| Arm | Wall seconds | User CPU seconds | System CPU seconds | CPU percent | Major faults | File inputs | Max RSS from `time` |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1 Scotch | 706.43 | 37,658.53 | 1,471.93 | 5,539% | 198,149 | 217,552 | 2,824,044 KiB |
| X1 hierarchical xyz | 547.96 | 28,733.32 | 1,605.43 | 5,536% | 274,581 | 246,568 | 2,865,700 KiB |
| X2 hierarchical xyz | 720.01 | 0.08 | 0.17 | 0% | 0 | 0 | 11,200 KiB |

S1 and X1 GNU `time` records show about 55 CPU equivalents against a 56-CPU allocation. This does not establish that the solver was compute-bound. X2's `time` record is the timed-out command record and reports only 0.08 user and 0.17 system CPU seconds despite its printed 20-step solver output; do not use its resource fields as solver utilization or cost evidence. Scheduler allocation/accounting does not provide per-arm billed cost here.

## Whole-node telemetry

Each arm has a five-second sampler over aggregate `/proc` counters. The memory and paging values are node-wide deltas during that arm's sample span, not rank-specific measurements. The CPU frequency statistics are per-sample medians across the 56 instantaneous CPU readings.

| Arm | Samples / seconds | `MemAvailable` min–max | `Active(anon)` max | `Cached` min–max | `pgscan_kswapd` / `pgsteal_kswapd` delta | `pgscan_file` / `pgsteal_file` delta | `numa_miss` delta | CPU median range (sample medians) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S1 Scotch | 142 / 705 | 39.58–165.61 GiB | 130.84 GiB | 6.46–36.26 GiB | 3,398 / 3,394 pages | 11,923 / 11,850 pages | 66,718,152 | 2.90–4.00 GHz; median 3.30 |
| X1 hierarchical xyz | 110 / 545 | 39.27–167.25 GiB | 132.95 GiB | 26.42–27.93 GiB | 381,719 / 381,605 pages | 397,082 / 396,965 pages | 62,042,210 | 2.90–4.00 GHz; median 3.25 |
| X2 hierarchical xyz | 145 / 720 | 38.54–165.63 GiB | 132.94 GiB | 35.53–36.24 GiB | 0 / 0 pages | 0 / 0 pages | 84,578,979 | 2.90–4.00 GHz; median 3.30 |

Across the same sample spans, whole-node major-fault deltas were 3,938 (S1), 5,944 (X1), and 1 (X2); `numa_pages_migrated` deltas were 220,368, 33,901, and 12,351. Swap-in and swap-out deltas were zero; `SwapTotal` was zero in every arm's first sample. CPU, memory, and IO PSI were unavailable in all 397 samples, not measured as zero pressure. Sample read duration medians were about 3.2–3.3 ms, with maxima 4.9–5.5 ms; that is collection duration, not an observer-interference estimate.

In one S1 five-second sample window, 3,398 kswapd pages were scanned and 3,394 stolen while available memory fell from 43.53 to 41.82 GiB. In X1, the largest sampled five-second window had 209,495 kswapd pages and 210,519 file pages scanned, while available memory fell from 53.20 to 43.29 GiB. Exact alignment of these windows to native solver steps has **not been established**: the sampler and native step clock use different start points. These are whole-arm and within-sampler observations only. The faster valid X1 arm had much more reclaim overall, so the evidence does not support a simple “more reclaim means slower” explanation. X2 showed no sampled reclaim delta but failed the return-code gate. No rank attribution or causality is established.

## Assessment and limits

The first S1-to-X1 contrast is promising only as a direction. The X2 printed mean does not reproduce it, the second control arm is absent, the 19-interval sample is short, and no full four-arm result exists. Do not treat X2 as a winning or valid losing measurement. The observed resource and telemetry differences do not identify bandwidth, memory pressure attribution, CPU bottlenecks, or a cause for the step-time variation. No Gadi or NSCC result follows from these Iris observations.

The retained evidence supports closing the **claim of a confirmed xyz improvement from this screen**. Any further comparison or cap change is a separate admission decision; this review does not submit work or alter the ledger.
