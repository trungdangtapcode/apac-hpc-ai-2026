# N62 to N64 matched load

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does increasing client concurrency from N62 to N64 raise useful H200 goodput while retaining the full gate?

## Why investigate this?

After selecting the H200 phase recipe, the team needed to find the useful request-load operating point. Closed-loop concurrency means the client keeps up to N requests in flight; raising N can improve GPU overlap but can also add queueing and first-token delay. This paired full-run comparison tests the tradeoff directly.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Client concurrency | N62 requests in flight. | N64 requests in flight on the revised recipe. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 full runs | N62: 3,011.875; N64: 3,044.490 good output tokens/s (+1.082867%). |
| SLA | N64 met the full joint gate. |

## What did we learn?

- N64 crossed the team’s 1% useful-gain threshold in this comparison.
- The result justified replication, not certainty from one pair.

## Decision

Repeat N64 independently before retaining it as the operating point.

## Limits and remaining questions

- The comparison supports this recipe and workload only.
- Goodput is the qualifying-request rate converted to 200 output tokens per request; it is not raw GPU token throughput.

## Sources

- [teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md)
- [research-review-25365-20261022/REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-review-25365-20261022/REVIEW.md)
- [research-review-25366-20261022/REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/REVIEW.md)
