# Test NUMA-aware decomposition

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does a NUMA-aware Scotch grouping that cuts fewer partition interfaces make the native solver faster?

## Why investigate this?

A graph cut cheaply screens how many mesh faces cross a proposed grouping. But fewer logical crossings matter only if they reduce actual communication or waiting on the solver critical path, so native timing was required.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Scotch grouping | Default Scotch grouping coefficients. | Candidate NUMA-aware Scotch grouping coefficients. |
| Native test | Graph-cut proxy only. | Job 25907753 measured the candidate's native solver time as well as graph cut. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Graph proxy | Logical graph cut fell 10.63%. |
| Solver | Native time increased 3.44% in the measured pair. |

## What did we learn?

- The graph proxy improved while solver time worsened: fewer logical crossings do not guarantee a faster solve.

## Decision

Close the unchanged NUMA-coefficient performance claim; retain the proxy-versus-runtime lesson.

## Limits and remaining questions

- The native comparison was a one-node pair, not proof about a four-node contest run.
- The evidence does not identify whether communication, placement, or another factor caused the slowdown.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-research-journey-20261023/JOURNEY.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
