# MNNVL plus FlashInfer interaction

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Which communication and attention backend choices improve the routed H200 service, alone and in combination?

## Why investigate this?

Attention and tensor-parallel collective work appeared in the serving path, so the team tested existing implementations separately and in combination. MNNVL here changes the decode collective/all-reduce path; it is not the NIXL transfer of KV between prefill and decode. The combined service must be measured because isolated component choices can interact.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Decode collective backend | Existing collective implementation in the control. | --flashinfer-allreduce-fusion-backend mnnvl on decode. |
| Decode attention backend | Existing attention implementation in the control. | --decode-attention-backend flashinfer, tested separately and in combination. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 MNNVL | 2,592.16; repeat approximately 2,592.92 good output tokens/s, about 8% above its matched N52 control. |
| Combined configuration | Later score 2,632.61; FlashInfer alone was near a tie. |

## What did we learn?

- MNNVL had a repeated positive matched-load observation in this phase.
- FlashInfer alone was not a meaningful gain; the combined result is an interaction result and not the sum of component effects.

## Decision

Keep the MNNVL direction for further matched refinement; do not attribute the combined result to FlashInfer alone.

## Limits and remaining questions

- Results apply to the tested H200 pipeline and load.
- The combined configuration does not identify a single causal component.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [serving-tuning-07/PLAN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/PLAN.md)
- [serving-tuning-10/MATCHED_REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/MATCHED_REVIEW.md)
