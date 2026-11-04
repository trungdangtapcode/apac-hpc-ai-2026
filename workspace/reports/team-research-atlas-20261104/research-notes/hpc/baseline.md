# Establish an unchanged reference

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

What does an unchanged, reproducible solver reference look like before tuning?

## Why investigate this?

A performance claim needs a reference with known solver work. Full preparation ran before solver timing, avoiding a mix of setup and seconds per step. Two ordered Scotch observations were retained to expose run-to-run variation.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Reference test design | No retained unchanged reference in this comparison. | Run full preparation, then measure solver steps; retain the ordered Scotch pair in jobs 25905114 and 25907325. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Reference | 14.9220 seconds/step. |
| Ordered pair | Reported difference −0.994%, small enough to treat as noisy rather than a demonstrated gain. |

## What did we learn?

- The reference is not tuned, and the small pair difference warns that sub-percent changes need stronger repetition.

## Decision

Use the unchanged Scotch setup as a reference and require matched controls for later claims.

## Limits and remaining questions

- The two-job difference is not evidence that either order or setting improves the solver.
- This NSCC observation must not be pooled with Iris timings.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-research-journey-20261023/JOURNEY.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
