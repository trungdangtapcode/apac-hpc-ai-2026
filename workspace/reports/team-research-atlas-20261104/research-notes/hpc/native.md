# Ask whether that mechanism helps the solver

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does the preparation memory-policy change affect native OpenFOAM solver time when all solver inputs and settings stay fixed?

## Why investigate this?

The copy/hash test changed preparation counters, but practical value depends on solver behavior. The follow-up holds Scotch input and solver settings constant while changing only preparation-child policy; its receipt is not a result.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Native follow-up | Preparation-child policy varied; native solver effect not yet tested. | Job 2294676 accepted a 20-step test with the same Scotch source and solver settings, changing only preparation-child policy. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Job | 2294676; accepted 20-step native test. |
| Review state | Completion result had not been reviewed in the 4 November curated map. |

## What did we learn?

- The receipt establishes scheduler acceptance only; no performance conclusion is available until completed output is reviewed.

## Decision

Keep this milestone explicitly unreviewed; inspect the terminal result before deciding whether the mechanism matters to solver time.

## Limits and remaining questions

- Do not infer that the job completed or improved performance from acceptance.
- The 15-milestone map is curated, not a complete allocation census, and this record's state is only as current as its dated evidence review.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-native20-20261103/STATUS.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
