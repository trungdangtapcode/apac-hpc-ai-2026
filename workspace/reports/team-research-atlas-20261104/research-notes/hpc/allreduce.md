# Qualify tiny Allreduce before a solver trial

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can a different tiny-message collective configuration reduce latency enough to justify a native test?

## Why investigate this?

The previous NUMA solver trial timed out. A distinct cheap probe tests MPI configuration before spending another solver allocation; the timeout itself does not identify MPI as a bottleneck.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Configuration | Current default Open MPI collective selection. | Forced tuned/basic/libnbc/self list, tuned priority 100, dynamic rules enabled and Allreduce algorithm 3. |
| Work held fixed | 56 ranks, 8/64-byte SUM, 100 warmups, two 1000-call blocks per launch. | Same C binary and work in ABBA order, identical reported CPU binding; raw distributions retained. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Protocol | 2294805 COMPLETED 0:0 in 20 s; correctness, source hashes, binding and raw quantile replay pass. |
| 8B block 1 A1/B1 p50 | 2.478 us versus 4.117 us; candidate is 66.14% slower in that matched block. |
| All matched blocks | Candidate median 57–70% higher and p95 44–85% higher; no qualifying benefit. |
| Actual runtime | Open MPI 5.0.10rc2. Verbose default includes ucc priority 100 enabled; candidate tuned priority 100 enabled. |

## What did we learn?

- The strict improvement gate fails in every matched block, so a costly native follow-up is not justified for this candidate.
- The default collective stack is faster than this forced configuration on this tiny-message test; this does not establish a global optimum or OpenFOAM bottleneck.

## Decision

Close this forced-tuned candidate and retain default MPI for now. Inspect existing optimized build/runtime choices before selecting a distinct next trial; do not sweep losing flags blindly.

## Limits and remaining questions

- Microseconds per tiny collective call are not seconds per CFD step or a solver speedup.
- Component-selection logs are not a per-operation native profile; no exact active UCX transport is inferred from linkage.

## Sources

- [Complete qualification review](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-allreduce-qualify-20261105/completed-2294805/RESULTS.md)
- [Raw metric/replay record](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-allreduce-qualify-20261105/completed-2294805/REVIEW.json)
- [Official component selection documentation](https://docs.open-mpi.org/en/v5.0.x/tuning-apps/collectives/components.html)
- [Official tuned controls](https://docs.open-mpi.org/en/v5.0.x/tuning-apps/collectives/tuned.html)
