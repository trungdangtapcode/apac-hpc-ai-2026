# Check a new axis order and reverse it

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does a new xzy axis order improve performance, and does an initial small signal survive a longer reverse check?

## Why investigate this?

After zyx lost its direct control, xzy tested a distinct axis-order hypothesis. A 40-step screen showed only a small signal; the 52-step reverse-order check tested whether it persisted with more intervals and a control for temporal drift.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Axis order and test length | Scotch control and 40-step xzy screen. | Reverse-order xzy confirmation, 52 steps and 51 intervals per arm, job 2294644. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Initial screen | −0.71% candidate time. |
| Reverse confirmation | +10.25% candidate time; slower. |

## What did we learn?

- The initial signal reversed in the longer comparison and was not robust enough to change the recipe.

## Decision

Close the unchanged xzy speed claim and preserve both trials as a useful failed hypothesis.

## Limits and remaining questions

- The jobs were Iris practice runs, not contest scores.
- The reversal demonstrates instability, not a proven physical explanation for it.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-iris-comparison-20261103/README.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
