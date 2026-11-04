# H100 prefill alternatives lose

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Do alternative H100 prefill chunking or dense FlashInfer attention improve the current H100 recipe?

## Why investigate this?

Once the H100 baseline recipe existed, chunk size and attention implementation were plausible controls on prompt processing. Smaller chunks can change scheduling and memory behavior; FlashInfer is an existing attention implementation. The decision criterion was complete-service performance under matched conditions, not whether a branch passed basic validity checks.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Prefill chunk size | H100 control chunk setting. | Chunk 6144 tested. |
| Prefill attention | Existing attention path. | Dense FlashInfer prefill tested. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H100 chunk 6144 | 2,411.995 versus 2,413.802 control. |
| H100 dense FlashInfer | 2,227.031 good output tokens/s, −7.74% versus control. |

## What did we learn?

- Chunk 6144 was effectively a tie/slight loss, not an improvement.
- Dense FlashInfer materially reduced the measured score in this tested recipe.
- Passing run gates only establishes valid execution, not benefit.

## Decision

Do not promote either tested branch on H100.

## Limits and remaining questions

- These are specific H100 implementation/settings, not universal library rankings.
- No kernel-level causal profiling is implied.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [research-followup-20261019-1418/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1418/RESULTS.md)
- [research-followup-20261019-1418/ATTENTION_RESULT.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1418/ATTENTION_RESULT.md)
