# Round-robin prefill routing

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can assigning new prompts across the prefill replicas more evenly reduce first-token delay?

## Why investigate this?

The workload deliberately disabled prefix reuse. The source review noted a cache-aware prefill policy with an absolute imbalance threshold of 64 while the tested burst was N52. This suggested testing deterministic distribution across the two prefill replicas to reduce the first-burst TTFT tail. It was a routing hypothesis, not proof of a router bug.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Prefill gateway policy | Inherited cache_aware policy; absolute imbalance threshold 64 in the reviewed control. | Set --prefill-policy round_robin; worker, decode and client files unchanged. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 pilot 23325 | 2,402.64 good output tokens/s versus 2,075.11 control. |
| Mean TTFT | 1,437.63 ms to 333.25 ms in the pilot. |

## What did we learn?

- The pilot observed higher goodput and much lower mean time to first token.
- It was a single treatment observation; inter-token latency approached its limit, so request-level tails remained important.

## Decision

Use the routing change as a promising lead and seek controlled follow-up rather than treating the pilot as settled.

## Limits and remaining questions

- Single pilot observation; not an independent replication.
- The exact causal contribution of routing is not established by the score difference.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [serving-tuning-04/RESEARCH.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-04/RESEARCH.md)
- [serving-tuning-05/PLAN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-05/PLAN.md)
