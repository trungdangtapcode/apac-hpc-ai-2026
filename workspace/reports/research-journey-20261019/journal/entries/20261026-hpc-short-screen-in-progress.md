# 26 October: xyz completes while the matched zyx screen continues

**Question and control.** Iris job 2294099 tests whether changing hierarchical decomposition order from xyz to zyx reduces solver time. The fresh source, 56 ranks, node, 30 solver steps and fixed per-step iteration counts are held constant. Earlier cut checks found fewer interface faces for zyx; those counts alone are not evidence of a solver gain. The full setup and receipt are retained in [the screen bundle](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-screen30-20261026/README.md).

**Actual progress.** At approximately 14:33 UTC, Slurm reported RUNNING on iris001, elapsed 1,433 seconds. The coordinator had accepted xyz and written its partial result. zyx had entered step 7; no final comparison existed. The xyz return code was zero and batch stderr was empty in this snapshot. These observations do not replace an independent terminal replay of all source, copy and numerical checks.

| xyz observation | Value |
|---|---:|
| Solver steps / measured intervals | 30 / 29 |
| Mean time per step | 32.592668524 s |
| Median time per step | 31.978769372 s |
| 95th percentile time per step | 33.104158664 s |
| Maximum time per step | 48.177250648 s |
| Final drag coefficient Cd, dimensionless | 0.441369407 |
| Native recommended minimum measured samples | 82 |

**Assessment and limits.** The native statistics explicitly warn that 29 intervals are below the calculated minimum of 82 for its stated 2% error at 95% confidence. Retain the 48.18-second slow interval. Do not promote an eventual short-screen difference as a confirmed full-length improvement. Early zyx intervals around 24 seconds are incomplete observations, not its mean. The earlier 150-step Iris reference used another allocation and a longer run; its 21.87-second mean is not a matched baseline for this short fresh-control result. No hardware bottleneck has been established. There is no new qualified best result.

**Other cluster.** A fresh PBS query still reports NSCC CPU job 26004608.pbs101 queued in q5 with `Insufficient amount of resource: node_pool`. It has not executed the syscall diagnostic. Retain its queue position and its full maximum reservation. NSCC's verified solver reference remains job 25940700 at 3.364622070 seconds per step; do not compare its hardware directly with Iris.

**Next decision.** Both clusters already have their one authorized own allocation or queued request, so no additional allocation was submitted at this checkpoint. Collect both Iris arms and replay their evidence after termination. Reconcile only known terminal usage, then choose a budgeted longer confirmation only if the gain and uncertainty justify it. The insufficient-sample warning may require a revised confirmation design; a single full-length candidate on a different allocation does not independently resolve the matched control or fixed-order limitation. Inspect the NSCC trace before proposing any affinity repair. No reservation, budget ceiling, background schedule or submission material changed.

**Evidence and preservation.** The [Iris snapshot](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-screen30-20261026/live-status-1433.json) retains actual queue/accounting responses, partial timings and native log tails. The [filtered PBS snapshot](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-affinity-strace-20261026/live-status-1434.json) retains resource requests and queue reason without the runtime environment. These are dated in-progress snapshots, not completed-run archives. Capture and push this bounded status and interpretation separately from the eventual result review.
