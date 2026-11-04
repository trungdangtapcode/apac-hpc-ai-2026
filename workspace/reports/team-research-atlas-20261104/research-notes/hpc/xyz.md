# Revisit native xyz with a control

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can a controlled native comparison establish whether our xyz decomposition is better than Scotch?

## Why investigate this?

Earlier axis-order tests had not established a win, so xyz was revisited in a controlled multi-arm screen. A valid comparison needs both candidate and control to finish; a fast partial arm cannot substitute for a timed-out arm.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Screen design | No complete matched xyz comparison. | 20-step four-arm Scotch/xyz screen in job 2294671; planned comparison remained incomplete after timeout. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Job | 2294671; second xyz arm timed out at 720 seconds. |
| Observed fragments | Scotch 33.6725; first xyz 25.5860; second xyz printed 34.7926 before timeout; final Scotch absent. |

## What did we learn?

- The planned comparison did not finish, so its fragments support neither a valid win nor a complete solver loss.

## Decision

Mark the comparison incomplete and do not promote xyz from its partial timing.

## Limits and remaining questions

- No complete paired estimate or valid repeat exists.
- A timeout is a terminal experiment failure, not a performance measurement.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-iris-comparison-20261103/README.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
