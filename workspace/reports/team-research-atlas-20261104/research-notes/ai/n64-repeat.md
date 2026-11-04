# Independent N64 repeat

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does the full N64 H200 result reproduce on an independent run?

## Why investigate this?

The first N62-to-N64 comparison was only just above the useful-gain threshold. A repeat checks whether N64’s score is stable rather than a single favorable sample. Keeping the same operating recipe makes the repeat evidence about repeatability, not a new optimization.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Concurrency/configuration | First full N64 treatment. | Independent full N64 repeat with same retained recipe. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 repeat 25373 | 3,044.075 good output tokens/s; −0.013634% versus first N64. |
| Historical mean | Three-run retained mean 3,044.400475. |

## What did we learn?

- The independent result closely matched the first N64 score.
- This supports N64 as a stable operating point for later comparisons.

## Decision

Retain N64 and use the repeated mean as a historical reference series.

## Limits and remaining questions

- This repeat confirms consistency, not a universal optimum.
- The mean refers to its specified historical run set, not every later control.

## Sources

- [teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md)
- [research-review-25373-20261022/REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-review-25373-20261022/REVIEW.md)
