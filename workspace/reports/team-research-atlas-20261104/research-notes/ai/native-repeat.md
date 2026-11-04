# Native full N64 reproduction

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does the native H200 N64 recipe still deliver its historical operating level under the current full protocol?

## Why investigate this?

A fresh native run checks whether the retained H200 configuration remains a valid reference after earlier tuning and gate changes. It is a reproduction of the recipe, not a new candidate treatment, and should remain distinct from the historical three-run N64 mean.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| H200 deployment | Historical native N64 observations. | Native full N64 configuration replayed under current gates. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Job 26766 | 3,045.501509 good output tokens/s. |

## What did we learn?

- The native run is close to the historical N64 operating region.
- It provides an individual observation in a separate series, not a new global best claim.

## Decision

Retain as a current native reference and keep it distinct from the historical mean.

## Limits and remaining questions

- It is not a matched comparison with an optimization arm.
- A single replay does not characterize all runtime drift.

## Sources

- [h200-native-chunk-review-20261028/REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h200-native-chunk-review-20261028/REVIEW.md)
- [ai-final-report-20261030/REPORT.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-final-report-20261030/REPORT.md)
