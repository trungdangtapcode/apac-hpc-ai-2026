# FP8 KV and decode DeepGEMM losses

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Do FP8 KV storage or DeepGEMM decode improve the routed service without violating both latency limits?

## Why investigate this?

After routing improved the service, two plausible decode-side changes were tested separately: reducing KV representation precision and changing the decode matrix-kernel backend. KV cache stores attention state needed for future tokens; lower precision can reduce its footprint but may affect latency or quality. DeepGEMM is an existing optimized kernel library, not a team-created method. These are candidate mechanisms, not assumed wins.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| KV cache precision | BF16 KV. | FP8 KV tested on the routed pipeline at N52. |
| Decode kernel backend | Existing decode backend. | DeepGEMM decode tested separately at matched N52. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 matched-load tests | Both tested branches failed the joint SLA at N52. |

## What did we learn?

- Neither candidate met the service gate in these tests.
- A decode-only failure does not rule out using DeepGEMM in prefill, whose parallel workload differs.

## Decision

Retain BF16 KV and close these tested branches; later test phase-specific ideas only with their own controls.

## Limits and remaining questions

- The result applies to these implementations, routing, and N52 setup.
- No claim about all FP8 KV or all DeepGEMM versions.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [serving-tuning-06/PLAN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-06/PLAN.md)
