# H100 HPC-Ops decode

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

On H100, does selecting HPC-Ops for decode improve the full service relative to the existing decode backend?

## Why investigate this?

The earlier H200 result suggested HPC-Ops was worth testing as an existing decode implementation on H100, but hardware transfer was uncertain. Decode repeatedly applies the model to one next token; backend choices can shift time between streaming and first-token behavior. The H100 test therefore needs its own matched control and repeat.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Decode backend on H100 | Existing/automatic decode implementation. | HPC-Ops selected for decode only; treatment repeated against controls. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H100 matched comparison | 2,308.308 versus 2,245.534 good output tokens/s (+2.7955%). |
| Repeat/control | Repeat 2,304.083 remained above fresh control job 221275. |
| Latency tradeoff | ITL improved; TTFT rose. |

## What did we learn?

- The full-service gain repeated in the same H100 context.
- The change shifted latency metrics: higher goodput and better token spacing came with slower first-token time.

## Decision

Retain HPC-Ops decode as a supported H100 option under the tested recipe.

## Limits and remaining questions

- H100-only evidence; do not infer H200 effect.
- This is configuration-level evidence and does not isolate an individual kernel cause.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [research-followup-20261018-0900/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-0900/RESULTS.md)
- [research-followup-20261018-0917/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-0917/RESULTS.md)
