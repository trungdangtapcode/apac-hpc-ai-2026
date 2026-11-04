# Compare our partition with Scotch

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does our hierarchical zyx partition beat a matched organizer Scotch control on Iris?

## Why investigate this?

Earlier zyx minima came from different allocations and could not be ranked fairly. This trial placed Scotch and our candidate in one allocation with the same mesh, rank count, solver work, and default runtime; it tests the candidate against a direct control.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Partition method | Organizer default Scotch partition. | Team hierarchical (7,4,2) partition with zyx order. |
| Matched trial | No same-allocation control/candidate pair. | Four-arm Scotch/zyx/zyx/Scotch comparison in job 2294640. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Matched means | Scotch 26.9011 vs zyx 29.6490 seconds/step. |
| Candidate time change | +10.2150% slower. |

## What did we learn?

- The matched candidate lost despite the earlier low observation, closing the claim that zyx is better on this Iris setup.

## Decision

Keep Scotch as the control and stop promoting zyx on the basis of isolated minima.

## Limits and remaining questions

- The result is specific to this Iris one-node, 56-rank practice workload.
- It does not establish the cause of zyx's slowdown or predict a different platform.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-iris-comparison-20261103/README.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
