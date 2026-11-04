# H100 repeated frontier remains separate

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

What repeatable full-run range does the H100 recipe achieve, and should it be compared directly with H200?

## Why investigate this?

Multiple complete H100 observations are useful for understanding that platform’s own variation. Since H100 and H200 differ in hardware and possibly runtime conditions, the fair use is to maintain separate series rather than rank their raw scores as if they were matched experiments.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Platform series | Single H100 commissioning point. | Three full H100 runs reviewed as a separate repeated series. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H100 goodput | 2,433.020 / 2,395.311 / 2,406.802 tokens/s. |

## What did we learn?

- The three H100 measurements define an observed range for that recipe.
- They are not H200 controls and do not estimate an H200 treatment effect.

## Decision

Keep H100 and H200 charts and conclusions separate; use same-platform matched comparisons.

## Limits and remaining questions

- Run-to-run differences remain visible.
- No cross-hardware normalization or causal comparison is provided.

## Sources

- [research-followup-20261020-h100-restored/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md)
- [ai-final-report-20261030/REPORT.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-final-report-20261030/REPORT.md)
