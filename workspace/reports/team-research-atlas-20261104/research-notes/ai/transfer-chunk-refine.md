# Refine transferred recipe chunk

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can chunk-size refinement recover performance when the H100-derived HPC-Ops prefill runner is used on H200?

## Why investigate this?

The prior H100 recipe transferred poorly to H200, but the runner and chunk size can interact. Rather than reject every component, this branch held the HPC-Ops prefill runner and changed chunk size, then compared its best point with the incumbent. This isolates the chunk refinement within that transferred recipe, while still requiring a direct incumbent comparison.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Prefill chunk on transferred runner | HPC-Ops prefill with chunk 4096. | Chunks 6144 and 8192 tested on H200. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 results | Chunk 6144: 2,821.885; chunk 8192: 2,900.607 good output tokens/s. |
| Incumbent comparison | Chunk 8192 remained 4.523% below the incumbent. |

## What did we learn?

- Chunk 8192 recovered performance relative to 4096 within this transferred branch.
- Recovery did not make the recipe competitive with the retained H200 incumbent.

## Decision

Do not promote the transferred runner; retain the H200-specific recipe.

## Limits and remaining questions

- The result is a branch-level comparison, not evidence that chunk 8192 is globally best.
- Different controls and recipe settings prohibit combining these values with unrelated series.

## Sources

- [teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md)
- [h200-hpc-chunk-transfer-20261031/PLAN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/PLAN.md)
- [h200-hpc-chunk-transfer-20261031/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/RESULTS.md)
