# H100 load/chunk frontier

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

How do H100 prefill chunk size and client load interact under complete latency gates?

## Why investigate this?

The H100 recipe had shown a higher operating point at N54, but tuning must consider whether chunk changes preserve joint TTFT/ITL eligibility and useful throughput. The test explored a bounded chunk/load frontier using full runs, rather than assuming that smaller chunks are always more responsive.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| H100 prefill chunk | Control chunk setting at N54. | Chunk 2048 and 8192/later chunk branches tested with full-run latency gates. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H100 N54 control job 222281 | 2,401.578 good output tokens/s. |
| Chunk 2048 | Approximately 26.13% lower. |
| Chunk 8192/later branches | No useful gain established. |

## What did we learn?

- A smaller chunk was substantially worse in this context.
- The tested chunk sweep did not produce a promoted H100 improvement.

## Decision

Keep the existing H100 recipe and close these chunk branches unless a new hypothesis changes conditions.

## Limits and remaining questions

- H100 evidence only.
- A bounded sweep does not prove all chunk values are inferior.

## Sources

- [h100-prefill-hpc-chunk-interaction-20261020/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h100-prefill-hpc-chunk-interaction-20261020/RESULTS.md)
- [h100-hpc-smallchunk-20261020/PAIR_REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h100-hpc-smallchunk-20261020/PAIR_REVIEW.md)
