# I/O-only R2 completes; lower rank density is the next distinct lead

Recorded 6 November 2026, Vietnam (UTC+7). Terminal observation at 14:37 Vietnam. This entry follows actual receipt 2294997, not the failed 2294920 matrix.

## Question and controlled change

The earlier hybrid changed both default 48-rank placement and file handler, and all retained hybrid arms were slow. R2 therefore retains default placement and the initialized 48-domain source, changing only uncollated to collated I/O. Actual teammate56 socket/core+collated is a second credible control, although that contrast also changes rank count and source partition. The six-arm order is T1/O1/D1/D2/O2/T2, with 40 solver steps and 39 measured wall-clock intervals per arm. Source mesh, physics, precision and fixed iteration work are preserved. Qualified per-rank file proofs replace the stdout parser that failed the prior matrix.

## Actual observations

Slurm reports COMPLETED 0:0, 8,059 seconds, 56 allocated CPUs, iris001. All six native logs reach End and each solver returns zero. These means are independently replayed from the retained terminal snapshot's 39 intervals each; full raw-artifact review has also passed.

| Recipe | First arm (s/step) | Second arm (s/step) | Mean of both arms (s/step) |
|---|---:|---:|---:|
| Teammate56, socket/core, collated | 34.694265954 | 28.754195819 | 31.724230886 |
| Original48, default, uncollated | 31.801589263 | 28.997183983 | 30.399386623 |
| Candidate48, default, collated | 32.502180668 | 24.687984366 | 28.595082517 |

Candidate48 pooled mean is 5.935331% lower than original48 and 9.863591% lower than teammate56. However, the first paired candidate arm is 2.203008% slower than O1, while the second is 14.860752% faster than O2. This sign reversal and large within-recipe changes do not establish a robust I/O benefit. The fastest complete candidate arm, 24.687984366 s/step, does not beat the retained historical approximately 22-second measurements. Do not select the lowest arm as a stable winner or compare only against the slower control.

## Assessment, limits and decision

The corrected proof transport allowed all six native arms to finish. It resolves an engineering failure, not a speed record. There is no causal bandwidth, NUMA page placement or I/O bottleneck proof from these timings. Historical binary/source identity audits do not pin all runtime states. The terminal review verifies all 642 artifact hashes, all six exact rank-file groups, native outputs and force checks, source/payload before/after and unchanged runtime identities. Five-second whole-node procfs sampling is retained; PSI is unavailable and no per-process bandwidth or causal profile was collected. Root independently replays every native timing and all transferred hashes. Root-job Slurm MaxRSS is blank; batch-step MaxRSS is available as 139187772K and is not a sum of MPI rank RSS.

Do not repeat this unchanged I/O-only configuration merely to fill the queue. The next distinct lead is 40 MPI ranks, following two valid opposite-order 48-versus-56 comparisons with lower mean time at 48. Fewer ranks might reduce communication but increase work per rank; a further gain is a hypothesis. The already completed Scotch40 cut 2294919 preserves all 65,334,765 cells. Mandatory native initialization must pass before a matched 40-versus-48 solver test. Preparing or initializing that source is not a performance result.

## Cost and evidence

Actual allocated CPU cost is 125.362222 CPU-hours, conservatively charged 126 in the local planning ledger. The 224 CPU-hour maximum retires exactly once, leaving 1,626 consumed, zero reserved, internal stage 1,724 before the next admission. These are not known billed site SU. Iris is separate from NSCC CPU and AI accounting.

[Terminal observation](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-best-recipes40-r2-20261106/live-status-20261106-latest.json). [Actual configuration and frozen receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-best-recipes40-r2-20261106/STATUS.md). [Full reviewed result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-best-recipes40-r2-20261106/completed-2294997/RESULTS.md). The next job receipt will be added only after acceptance.
