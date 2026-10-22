# Shared CPU density and decomposition review

This review combines six newly sealed one/two-node jobs with two prior sealed Scotch controls. It reports candidate native evidence and descriptive endpoint comparisons; it does not confer accepted-result status or establish controlled speedup.

## Integrity and work checks

All 400 local evidence entries and 398 remote-file hashes for the six new runs passed; the raw archive has 399 safe file members. The unchanged two prior Scotch controls were seal-verified and native timing rows rechecked (136 local entries, 134 remote hashes). All eight PBS records show F/exit 0. Each new run has all five native stage End markers, no FOAM fatal marker, full step endpoints, fixed Ux/Uy/Uz=15, p=12, omega=8, k=8 per-step work, exact solver/WCT time and elapsed matches, finite Cd rows, and matching source inputs after the documented parameter normalizations.

Allocated CPUs and MPI processes are distinct: one-node jobs reserve 128 CPUs while using 64, 96, or 128 MPI ranks; two-node jobs reserve 256 CPUs while using 128, 192, or 256 ranks. Cell partitions and solver rank checks use MPI ranks; resource cost and utilization use allocated CPUs.

| Job | Nodes | Method | MPI ranks/node (total) | Allocated CPUs | Steps | Mean s | p95 s | Max s (Time) | Final Cd | PBS walltime | Estimated SU* | Native minimum samples (warning) | Partial preparation timer sum s |
|---|---:|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---|---:|
| 25921831.pbs101 | 1 | hierarchical | 128 (128) | 128 | 40 | 14.366263 | 14.446429 | 16.421560 (T2) | 0.4389323284 | 925 s | 32.889 | 5 (short-sample warning: no) | 98.68 |
| 25921832.pbs101 | 1 | scotch | 64 (64) | 128 | 40 | 16.018573 | 16.478274 | 18.328530 (T36) | 0.4369250633 | 1045 s | 37.156 | 7 (short-sample warning: no) | 201.08 |
| 25921833.pbs101 | 1 | scotch | 96 (96) | 128 | 40 | 14.374957 | 14.484753 | 16.304206 (T2) | 0.4403515202 | 1015 s | 36.089 | 5 (short-sample warning: no) | 205.84 |
| 25921809.pbs101 | 2 | hierarchical | 128 (256) | 256 | 80 | 7.169997 | 8.009692 | 10.075875 (T27) | 0.3368689717 | 908 s | 64.569 | 42 (short-sample warning: no) | 86.34 |
| 25921820.pbs101 | 2 | scotch | 64 (128) | 256 | 80 | 7.902555 | 8.028983 | 8.509187 (T25) | 0.3310021116 | 1072 s | 76.231 | 2 (short-sample warning: no) | 199.14 |
| 25921822.pbs101 | 2 | scotch | 96 (192) | 256 | 80 | 7.701742 | 7.887058 | 10.048262 (T11) | 0.3369553193 | 1071 s | 76.160 | 15 (short-sample warning: no) | 208.36 |
| 25921487.pbs101 | 1 | scotch | 128 (128) | 128 | 40 | 14.450757 | 14.595540 | 16.145866 (T31) | 0.4359888360 | 1081 s | 38.436 | 4 (short-sample warning: no) | 197.99 |
| 25921492.pbs101 | 2 | scotch | 128 (256) | 256 | 80 | 7.462835 | 8.327817 | 16.397209 (T12) | 0.3271298097 | 1105 s | 78.578 | 225 (short-sample warning: yes) | 242.73 |

The lowest solver Average in this eight-run table is 25921809.pbs101 (7.169997 s/step). The lowest estimated whole-allocation charge is 25921831.pbs101 (32.889 SU estimate). The partial preparation timer sum is descriptive only and is not a fastest setup/init winner. It combines decomposePar algorithm duration with three native ClockTime values and excludes decomposePar processor-mesh/field transfer and write, read/I/O, and unattributed time.

The p95 uses linear interpolation; maxima and all full time-indexed samples, per-run IQR outliers, Cd ranges, resource records, stage tails, native recommended minimum sample counts, and actual confidence-warning presence are retained in review.json. The logger’s reported minimum is a diagnostic recommendation, not a formal independent confidence interval.

## Interpretation and limits

Per-run validation failures, if any, are recorded in review.json and excluded from the comparison table and leaders. These are descriptive endpoint observations across different MPI rank densities and allocations, at prescribed 40-step one-node and 80-step two-node endpoints. Cd endpoints are at different times; the values are not an accuracy comparison. Do not infer stable matched speedup or a causal bottleneck from these runs. The observed lowest solver Average can differ from the cheapest full allocation, because cost includes allocated CPU count and all elapsed preparation and solve time.

PBS `cpupercent` is a last-sample field; whole-allocation average utilization is separately derived as CPUT / (walltime × allocated CPUs). PBS `exec_host` records allocated hosts, but not which physical cores each MPI rank used. Estimated SU is walltime × allocated CPUs × queue charge rate / 3600, not posted charge.

Frozen submission script provenance and owner identity are not established. The collected current common script has a hash and runtime flags in review.json, but may differ from submitted bytes. PBS exit 0 and native End markers do not prove each stage command returned zero because the helper can mask a nonzero native return code. Processor fields, mesh binaries/independent mesh identity, final zero-field seals, runtime environment, rank affinity mapping, hardware telemetry, and posted charge were not collected. Negative omega minima are diagnostic only and also appear in accepted controls; no fields/counters diagnose their cause.

Machine-readable measurements and complete time samples are in [review.json](review.json).
