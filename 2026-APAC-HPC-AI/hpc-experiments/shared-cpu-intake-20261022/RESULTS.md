# Shared CPU Intake Review

This is a sealed-evidence review of two completed OpenFOAM CPU jobs. The logs and outputs support useful native timing observations, but missing ownership, frozen-script, final-field, mesh-binary, and physical-placement evidence prevent treating these as fully accepted results.

## Integrity and work checks

All 136 local intake files and 134 remote-file entries passed SHA256 verification; the raw archive contains 135 files with no unsafe paths. Both sanitized PBS records show state F and exit status 0. Each run has End markers for decomposePar, renumberMesh, potentialFoam, applyBoundaryLayer, and simpleFoam, and no native FOAM fatal marker.

Both source cases match the accepted official payload after normalizing only rank count, endTime, decomposition method, and hierarchical shape. Initial 0.orig fields and constant inputs match exactly. Native logs identify OpenFOAM 2512 double precision and Scotch with the expected partition counts.

| Job | Nodes / ranks | Steps / terminal Time | Cell partitions | Cells total | Fixed work per step (Ux/Uy/Uz, p, omega, k) |
|---|---:|---:|---:|---:|---|
| 25921487.pbs101 | 1 / 128 | 40 / 40 | 128 | 65,334,765 | 15 / 12 / 8 / 8 (checked for every recorded step) |
| 25921492.pbs101 | 2 / 256 | 80 / 80 | 256 | 65,334,765 | 15 / 12 / 8 / 8 (checked for every recorded step) |

The per-step work is 15 iterations for each velocity component, 12 for pressure, 8 for omega, and 8 for k. SolverInfo records cover every requested step. The wallClockTime function records 39 samples for the 40-step job and 79 for the 80-step job, beginning at Time 2. Every per-step elapsed value and time index in simpleFoam matches its wallClockTime.dat row; each series' arithmetic mean also matches the solver log aggregate.

## Timing and resources

| Job | Native mean step time (s) | p95 (s) | WCT range (s) | Max Time / seconds | IQR outlier Times | PBS walltime | PBS CPUT | Derived whole-allocation CPU use | cpupercent last sample | mem / vmem | Estimated SU |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|---|---:|
| 25921487.pbs101 | 14.450757 | 14.595540 | 14.269316–16.145866 | 31 / 16.145866 | 31 | 00:18:01 | 25:31:43 | 66.42% | 11551 (PBS last sample) | 128736360kb / 260213940kb | 38.436* |
| 25921492.pbs101 | 7.462835 | 8.327817 | 7.044165–16.397209 | 12 / 16.397209 | 2, 12, 17, 19, 21, 26, 41, 51, 55, 59, 69 | 00:18:25 | 49:52:58 | 63.48% | 23150 (PBS last sample) | 150124848kb / 207278184kb | 78.578* |

The observed per-step time ratio is 1.936 (1-node value divided by 2-node value). These are endpoint-scaling observations at the prescribed 40- and 80-step endpoints, across 128- and 256-rank allocations. They are not controlled same-work strong scaling or a causal speedup measurement. The native statistic uses the 39/79 recorded post-start samples. The 2-node timing logger estimates 225 samples for its 2% error / 95% confidence target; its 79-sample mean has low sample confidence. Keep official endpoints unchanged; any longer timing sample belongs in a separately labeled diagnostic outside ranked scoring.
The reported p95 uses linear interpolation. IQR outliers use the Tukey 1.5×IQR fences; the maximum Time identifies the single largest recorded step. Full time-indexed simpleFoam and wallClockTime values are retained in review.json.

The PBS `cpupercent` values are the last reported samples (11551 and 23150), not whole-allocation averages. The separate average shown above is derived from PBS CPUT divided by allocated CPUs times full PBS walltime; it includes preparation and solve stages. Memory fields retain PBS `kb` units.

`*` SU is estimated as elapsed PBS walltime seconds × allocated CPUs × queue charge rate ÷ 3600, using the reported rate 1.0. This is an estimate, not a posted charge.

## Output and log observations

- 25921487.pbs101: all 40 Cd/force rows are finite; final Cd at Time 40 is 0.4359888360 (full recorded Cd range 0.3181068859 to 1.1881838148).
- 25921492.pbs101: all 80 Cd/force rows are finite; final Cd at Time 80 is 0.3271298097 (full recorded Cd range 0.3193513140 to 1.1996658820).
- MPI stages repeatedly warn that `FI_VERBS_PREFER_XRC` conflicts with `FI_OFI_RXM_USE_SRX=0`, so XRC is disabled. The solver also reports that the wallClockTime dynamic library was initially absent and then builds it in the run directory.
- Both decomposePar logs warn while reading `constant/README.md`. The 2-node simpleFoam log reports that 79 measured steps are below its 225-sample recommendation. These warnings did not prevent End markers, but they remain part of the native evidence.
- The solver logs report negative minima in omega bounding diagnostics; final printed minima are -3729.55 and -17209.4. Negative omega diagnostics are also present in accepted control runs and do not by themselves establish a Basic failure. No final processor fields or hardware counters were collected to diagnose their cause.

## Limits and next decision

PBS exec_host records the allocated host(s) for each job. The collection lacks processor fields, mesh binaries, final zero-field hashes, and per-rank affinity/physical-core mapping. The collection notes also say current job-script bytes need not match the submitted bytes, and ownership is unverified. These records therefore support candidate native solver timing and full-work observations, but do not establish frozen payload provenance, actual per-rank placement, final-field validity, or an accepted score.

The shared run scripts accept a native `End` marker without checking each command's return code. The PBS metadata reports job exit 0, yet the per-stage helper can mask a nonzero native return if `End` was also printed. Future frozen scripts should retain and check each return code explicitly.

Treat the 1-node/2-node ratio as descriptive endpoint scaling only. A separate, unranked diagnostic can gather a longer timing sample if needed; preserve prescribed ranked endpoints. A controlled scaling conclusion also requires frozen input provenance and verified per-rank placement.

Machine-readable details and seals are in [review.json](review.json).
