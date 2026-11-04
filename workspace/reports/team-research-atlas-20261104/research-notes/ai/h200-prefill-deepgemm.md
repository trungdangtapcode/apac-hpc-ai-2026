# DeepGEMM specifically in prefill

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can DeepGEMM help prefill on H200 even though its tested decode use failed the service gate?

## Why investigate this?

Prefill processes many prompt tokens together, unlike sequential decode; kernels that lose in decode may still fit the larger matrix operations in prefill. The team therefore changed only the prefill backend and held decode and workload fixed. This phase-specific experiment tests a concrete reason for revisiting a library rather than repeating the failed decode setup.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| H200 prefill backend | Existing prefill backend with decode held fixed. | Select DeepGEMM as the prefill MoE runner (--moe-runner-backend deep_gemm) while keeping decode and the workload fixed; repeat the treatment independently. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 job 24291 | 2,715.842 good output tokens/s. |
| Fresh control 24320 | Matched reference for comparison. |
| Independent repeat 24327 | 2,716.787; treatment was +1.7401% versus the fresh control. |
| Hardware transfer | H100 did not reproduce this result. |

## What did we learn?

- Phase matters: a decode failure did not predict the prefill result.
- The repeated H200 measurement supported retaining DeepGEMM for prefill in that recipe.

## Decision

Retain DeepGEMM for H200 prefill only under the measured setup; evaluate H100 separately.

## Limits and remaining questions

- H200 result does not transfer automatically to H100.
- The gain is for a full configuration comparison, not a measured kernel-only speedup.

## Sources

- [teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md)
- [research-followup-20261017-1830/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261017-1830/RESULTS.md)
- [research-followup-20261017-2335/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261017-2335/RESULTS.md)
