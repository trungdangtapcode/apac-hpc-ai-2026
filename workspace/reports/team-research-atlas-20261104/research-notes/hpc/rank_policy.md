# Test solver-rank interleave policy

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does in-rank NUMA interleave policy survive into the solver rank process and improve a matched native run?

## Why investigate this?

Outer-launcher policy did not propagate to observed ranks in 2294801. In-rank numactl changed the pre-exec rank probe in 2294802, which motivated one bounded native test. The solver candidate timed out before the planned four-arm comparison completed.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Policy placement | 2294801 placed numactl outside mpirun; all 56 observed ranks retained default policy. 2294802 placed numactl inside each rank; all 56 candidate ranks observed interleave before exec. | 2294803 compared default solver arm A1 with in-rank interleave candidate B1 in a 40-step ABBA plan; candidate hit the 1,500-second per-arm cap before completion. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Completed control | A1 completed 40 steps /39 timings at 24.7585569046 s/step. |
| Timed-out candidate | B1 last started step 35, with 33 completed timing intervals and partial mean 41.8464956498 s/step. This is not a full-run score; B2 and A2 never started. |
| Pre-exec and force checks | Rank policy and equal-affinity checks pass for both started arms. Force-coefficient prefix matches for 34 rows. Source-after and runtime-after gates were not reached. |
| Cost | 41.4866667 allocated CPU-hours; not billed SU. |

## What did we learn?

- The outer numactl launcher did not propagate policy to observed rank probes, while in-rank numactl did change observed pre-exec rank policy and anonymous-page placement.
- The native candidate exceeded its frozen arm cap and its partial timing mean is substantially slower; no complete comparison exists.

## Decision

Close the unchanged all-rank interleave solver trial under this envelope. Do not extend caps or repeat the capped loser. The policy diagnostics are pre-exec evidence only, not proof of OpenFOAM runtime placement.

## Limits and remaining questions

- Only 34 force-coefficient rows are matched; later correctness and source/runtime-after gates were not reached.
- No complete candidate mean, reversed pair, B2 or A2 exists. Partial timing is not a solver score.
- Pressure telemetry files were unavailable. Pre-exec rank probes do not establish memory policy or placement through the OpenFOAM runtime.

## Sources

- [Native terminal review](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-solver-rank-interleave40-20261105/completed-2294803/REVIEW.json)
- [Outer-launcher policy diagnostic](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-rank-memory-policy-20261104/completed-2294801/RESULTS.md)
- [In-rank policy diagnostic](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-rank-inprocess-policy-20261104/completed-2294802/RESULTS.md)
