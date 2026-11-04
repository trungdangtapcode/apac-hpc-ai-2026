# Move communicating ranks closer

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can moving communicating MPI ranks closer in the node reduce solver time?

## Why investigate this?

The graph mapping sought fewer logical crossings between NUMA groups without changing the mesh partition: ranks keep their work while runtime placement changes. A reverse cycle tested whether an earlier short ABBA signal was order-dependent.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Rank-to-core mapping | Default runtime mapping of rank IDs to CPU cores. | Graph-informed rank-to-core mapping; reverse-order native comparison while keeping the partition fixed. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Lowest arm | 21.0512 seconds/step in a 14-step observation. |
| Reversed pooled comparison | Candidate was 5.37% slower. |

## What did we learn?

- The short minimum did not survive reversal; the graph objective does not measure physical traffic or solver critical-path time.

## Decision

Close the unchanged graph-placement speed claim; do not present the 14-step minimum as a winner.

## Limits and remaining questions

- The 21.0512 value is a 14-step arm, not a matched win.
- No measured hardware counter establishes why the candidate was slower.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-reverse-20261029/completed-2294390/RESULTS.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
