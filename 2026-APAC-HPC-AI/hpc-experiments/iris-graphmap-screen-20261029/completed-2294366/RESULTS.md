# Graph-placement ABBA screening result: 2294366

Job **2294366** completed on **iris009**, exit **0:0**, elapsed **1,758 seconds** with 56 CPUs. All 397 retained text-evidence hashes and all native output gates pass independent local replay. Each arm completed 14 steps and retained all 13 timing samples and 14 force rows. The accepted 1,040-file source, graph boundaries, actual native CPU mapping, isolated copies, time-zero fields and runtime library identities passed.

| Order | Treatment | Mean (s/step) | Median | P95 | Maximum |
|---|---|---:|---:|---:|---:|
| 1 | A1 identity | 21.095162 | 21.068308 | 21.271978 | 21.271978 |
| 2 | B1 graph | 21.136731 | 21.102479 | 21.318657 | 21.318657 |
| 3 | B2 graph | 22.841273 | 22.984352 | 23.716446 | 23.716446 |
| 4 | A2 identity | 32.867341 | 28.030309 | 69.166915 | 69.166915 |

The candidate average is 21.989002 seconds per step versus control 26.981251, an **18.5027% lower aggregate mean** in this short screen. This is **not a confirmed tuning gain**: adjacent first A/B means differ by only +0.1971% (candidate slightly slower), while the last baseline is 55.8051% slower than its first repeat. Candidate repeats differ by 8.0644%. The final baseline also contains a large tail, which remains in the mean. Do not trim it or call the aggregate a robust improvement.

A–B–B–A balances a linear time trend but does not identify the cause or remove arbitrary nonlinear variability. Reverse the treatment positions to **B–A–A–B** with otherwise identical work before promoting this result. That is a distinct confirmation of ordering, not an unchanged duplicate.

Control Cd trajectories repeat exactly, and candidate trajectories repeat exactly. The maximum absolute total-Cd difference between first A/B is 1.11e-15; final relative difference is about -1e-13 percent. Preserve those numerical rows rather than claiming bit-identical outputs. These data do not substitute for official full-length acceptance.

Command-level resource counters and phases were inspected and retained. CPU frequency, hardware memory bandwidth, per-process NUMA page residency and actual solver helper-thread affinity were not collected. A native preflight MPI mask check is not an observation of every OpenFOAM thread. The native minimum-sample recommendations were 0 / 0 / 11 / 1,258 for A1 / B1 / B2 / A2, versus 13 actual samples each. The last baseline does not meet that within-run recommendation; zero in the first rows is not zero uncertainty. All slow steps remain included. These serial samples are not independent run-level confidence.

Actual allocation arithmetic is **27.346667 CPU-hours**, conservatively counted as **28**. The maximum 46.666667 reservation was retired once; total Iris allowance consumed is 485, reserved 0, leaving 20 under the prior 505-hour internal envelope. These are planning CPU-hours, not a site SU bill. NSCC/AI credits were unchanged.

This is a non-scored Iris result, not 150 steps, not an NSCC score, and not evidence that the NSCC target below 3.364622070 seconds per step has been achieved. The selected 397 text artifacts, manifests and rebuild sources are retained; processor meshes, binary fields and compiled probe binaries are excluded from Git.
