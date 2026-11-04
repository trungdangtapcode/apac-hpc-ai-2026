# N16 quality pilot fails point threshold

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does a bounded paired pilot show that the candidate is safely above the local 99%-of-reference quality threshold?

## Why investigate this?

Before spending resources on a full evaluation, the team ran a small pilot using reference and candidate answers. A pilot can reveal gross quality regressions, but its small sample is noisy and is not a final pass. The first reference attempt failed, so only the corrected reference and candidate counts are meaningful for this comparison.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Evaluation size | No local paired quality run. | N16 pilot comparing stock FP8 reference with candidate. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Failed attempt | Reference job 28367 failed; not used as a score. |
| Corrected pilot | Reference job 28371: 104 correct; candidate job 28368: 102 correct; 98.076923% reference-score retention. |

## What did we learn?

- The pilot fell below the local 99% point threshold.
- That result justified a full fixed-set study; it did not establish final candidate quality.

## Decision

Do not claim PASS from the pilot; complete the full paired study.

## Limits and remaining questions

- Small pilot has limited precision.
- The pilot’s failed attempt must not be counted as a valid reference score.

## Sources

- [reviews/PILOT_RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/PILOT_RESULTS.md)
- [ai-quality-verification-20261103/FULL_RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-quality-verification-20261103/FULL_RESULTS.md)
