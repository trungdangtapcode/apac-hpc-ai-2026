# Graph-derived rank placement submitted as Iris 2294366

Recorded 29 October 2026, Vietnam time (UTC+7). Slurm accepted the new experiment at **2026-10-29T03:04:59.323155+07:00**.

## Question and prior evidence

The first full hierarchy pair suggested a large zyx advantage, but reversing the serial order flipped the result. Therefore the 21% gain was not reproduced. Native affinity job 2294358 showed default and explicit fill rank masks are identical; a default-versus-fill comparison was rejected before solver spending. Span worsened measured logical face proxies and was also rejected. These losing findings remain retained.

A deterministic graph bisection on actual reciprocal processor-boundary face counts selected a distinct zyx rank assignment: 129,700 to 90,953 unique cross-NUMA faces (29.8743% fewer), with 28 ranks per NUMA group and unchanged group cell totals. This is a testable communication proxy, not an expected runtime improvement. A previous NSCC graph candidate lost, so proxy quality alone cannot establish success.

## Controlled change and frozen work

The new job compares **identity rankfile A** with **candidate graph rankfile B** in **A–B–B–A** order, using the same native Open MPI rankfile launch method. Every rank retains its mesh partition and numerical work. Each arm uses a separate verified copy of the same READY initialized zyx case, factors (7 4 2), OpenFOAM v2512 FP64 and fixed iterations. Only physical CPU assignment differs between treatments. The run-control change to 14 steps is identical across all arms; all 13 native timing intervals and all 14 force rows must be preserved.

The initial 18-step draft would have exceeded its old timeout: retained zyx prefixes projected 419–649 seconds for 18 steps. The final plan was changed before submission to 14 steps, whose retained projections are 335–524 seconds. The per-solver cap is 650 seconds. The shared deadline is 2,850 seconds, outer timeout 2,970 and Slurm maximum 3,000 seconds. Minimum planning windows preserve complete fixed work; overload or insufficient time can fail the screen, never manufacture completion by truncation.

## Qualification and review

The 57-file runtime is frozen. Its accepted 1,040-file source manifest is exactly the reviewed full-run source inventory, not merely a new hash of mutable current files. The source and all 56 boundary hashes must match before the actual native MPI gate. That gate checks identity against the actual default OS CPU masks, candidate against the intended permutation, and bijections over all 56 cores. Logical rankfile core slots are not treated as OS CPU identifiers.

Root independently reran the source/configuration, canonical field-seal, mapping and output fixtures, including negative cases. A real retained native prefix passed the 14-step parser with all slow samples included. Actual runtime success is pending. Final review must inspect native errors, all timing tails and force rows, copy/source/field/runtime identities, resource logs and terminal accounting. No hardware bandwidth, frequency, page-residency or helper-thread evidence is claimed; a C MPI affinity probe does not establish OpenFOAM helper-thread affinity.

## Actual admission and cost

**Job 2294366** has a definite Slurm receipt and reservation. One exclusive Iris node, 56 CPU ranks, zero GPUs, maximum 50 minutes. Consumed allowance 457 plus maximum reservation 46.666667 equals 503.666667 CPU-hours under the unchanged 505-hour internal ceiling, leaving 1.333333 headroom. No NSCC/AI credit moved and no site SU balance is inferred. Parent probe 2294358 used 11 seconds, conservatively charged one CPU-hour and reconciled once.

NSCC transport was still unavailable at the latest read-only check. Its native Scotch/xyz/zyx trial remains higher priority when current access, queues, credit and old-job reconciliation permit it. The goal below 3.364622070 seconds per step on NSCC remains unmet; this short Iris job is not a scored substitute.

## Decision after completion

Do not decide from the first arm. Review all four arms and per-treatment repeats, preserve every sample and Cd difference, and state time/order limits. A favorable screening result needs a separate full-length confirmation; a failed or unchanged loss remains data and does not justify blind duplicates. Reconcile the maximum reservation once using terminal elapsed time and retain the exact payload. Preserve queue position and the one-own-active-Iris cap.

[Actual bundle and receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-screen-20261029/STATUS.md), [source graph and prior native qualification](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-mpi-affinity-20261029/RESULTS.md) and the raw journals preserve the complete reasoning. No submission package or other track was changed.
