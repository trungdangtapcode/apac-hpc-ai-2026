# R2 six-arm native comparison review

**Iris 2294997 COMPLETED 0:0**, 8,059 seconds / 56 CPUs / iris001. The full six-arm 40-step matrix passed native output, rank-proof, source, payload, runtime identity and force-repeat gates. This is a valid local measurement; it is not an official contest score.

| Recipe | Arm means (s/step) | Pooled mean (s/step) | Mean of arm medians (s) |
|---|---:|---:|---:|
| teammate56 | 34.694 / 28.754 | 31.724 | 30.683 |
| original48 | 31.802 / 28.997 | 30.399 | 30.061 |
| io48 | 32.502 / 24.688 | 28.595 | 28.467 |

The pooled io48 result is 5.94% faster than original48 and 9.86% faster than teammate56 in this allocation. The paired io48/original48 contrasts point in opposite directions: D1 is 2.20% slower than O1, while D2 is 14.86% faster than O2. Recipe repeat drift is 17.12% for teammate56, 8.82% for original48 and 24.04% for io48. This strong within-allocation timing drift means the pooled result does not establish an I/O benefit or a stable winner. The fastest individual arm, D2 at 24.688 s/step, is not a repeat-confirmed record and remains slower than the historical approximately 22.4-second Iris control.

All six arms completed steps 1–40 with 39 positive solver intervals and 40 force rows, rank-specific initialization, and exact 48/56 exclusive proof files. All six native logs, sampled pre-MPI rank proofs, telemetry streams, and the 642-file transferred archive were independently replayed. Source checks passed before and after for both rank partitions; payload checks passed before and after; OpenFOAM/MPI binary and linked library identities were stable. Same-recipe force repeat and paired original48/io48 force checks passed their existing tolerance.

Inspection found 5-second whole-node procfs samples for each arm, per-command GNU-time peak RSS, runtime identity, node snapshots, and solver resource logs. The collected pressure/PSI sources are unavailable, Slurm root-job MaxRSS is blank (the batch-step row reports 139187772K), and no per-process CPU/I/O bandwidth or GPU telemetry was collected. RSS is not summed MPI memory. These data do not identify why timings drifted.

Next: close promotion of collated I/O pending independent block-balanced replication; preserve this complete but drift-confounded measurement and do not claim improvement over the historical Iris result.

Evidence: `REVIEW.json`, `ROOT_REPLAY.json`, `collection.json`, `raw-evidence.tar.gz`, and `collected/`.
