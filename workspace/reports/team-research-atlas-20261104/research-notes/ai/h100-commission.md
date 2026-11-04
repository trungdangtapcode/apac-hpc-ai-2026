# H100 platform becomes measurable

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can the separately allocated H100/PBS platform produce a valid full benchmark baseline?

## Why investigate this?

H100 and H200 results must remain separate because they are different GPU generations and execution environments. Early H100 attempts exposed PBS launch and model-loader failures, so the first question was operational: can the platform complete the workload at all? A completed baseline is necessary before H100-side optimization claims can be evaluated.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| H100 job execution | PBS launch/loader attempts that did not complete a valid run. | A full N32 baseline completed after a long startup. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H100 job 220562.pbs111 | Approximately 1,565.16 good output tokens/s at N32. |

## What did we learn?

- The platform became measurable; earlier launch failures are not benchmark scores.
- This point starts an H100-specific series.

## Decision

Use H100 controls for H100 hypotheses and keep their evidence separate from H200.

## Limits and remaining questions

- Long startup is part of this deployment context.
- Do not pool this score with H200 or treat cross-GPU differences as a controlled optimization.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [nscc-pbs/README.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/README.md)
