# N64 versus N68 stop

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does increasing the revised H200 client load from N64 to N68 yield enough additional goodput to justify its latency cost?

## Why investigate this?

With N64 replicated, a small increase in in-flight requests tested whether more overlap could raise useful throughput. The tradeoff is that more outstanding requests may wait longer before prefill begins. Full N64/N68 runs allow both the goodput increment and TTFT shift to be considered together.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Client concurrency | N64 retained operating point. | N68 full-run comparison, alongside a fresh N64 run. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Goodput change | N68 improved only +0.083056%. |
| Mean TTFT | Rose approximately 1,113.6 to 1,347.1 ms. |

## What did we learn?

- The throughput change was far below the 1% usefulness threshold.
- The higher load also worsened mean first-token delay.

## Decision

Retain N64 and close N68 for this recipe.

## Limits and remaining questions

- This does not establish that higher concurrency is always harmful.
- The evidence is specific to the measured workload and deployment.

## Sources

- [teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md)
- [research-review-25487-25488-20261023/REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-review-25487-25488-20261023/REVIEW.md)
