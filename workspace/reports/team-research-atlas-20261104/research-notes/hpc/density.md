# Sweep rank density and node count

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

How do rank density and node count relate to observed solver time?

## Why investigate this?

Rank count differs from allocated CPUs: a job can reserve a full node while using fewer ranks. Six four-node logs across 64, 96, and 128 ranks per node map the range and tails, but separate allocations cannot establish a causal winner.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Ranks per node | Earlier reviewed runs covered fewer rank-density/node combinations. | Review six four-node native logs at 64, 96, and 128 ranks per node. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Lowest listed four-node observation | Scotch-128: 3.6779 seconds/step over 150 steps. |
| Scope | Six reviewed logs; separate runs and allocations. |

## What did we learn?

- The apparent method leader changes with rank density; sample warnings and long tails must remain visible, with no prescribed samples trimmed.

## Decision

Use the sweep to select a candidate for controlled confirmation, not to claim a density or method winner.

## Limits and remaining questions

- Allocations were not fully matched; some CPU reservations differed.
- PBS terminal history and acceptance artifacts were missing, so these are not accepted official scores.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-research-journey-20261023/JOURNEY.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
