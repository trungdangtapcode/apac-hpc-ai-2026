# Direct H100-derived recipe check on H200

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Do H100-derived decode recipes or FA3 transfer to the H200 incumbent?

## Why investigate this?

A configuration that works on H100 may interact differently with H200 hardware and software. The correct test is direct H200 measurement against a fresh H200 control, keeping same-GPU comparisons intact. FlashAttention-3 (FA3) and the H100-derived recipe are existing options, not presumed upgrades.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| H200 control | Prior incumbent reference. | Fresh H200 control at 3,038.022907 good output tokens/s. |
| Transferred backend | H200 incumbent decode. | FA3 decode and H100-derived recipe tested at N54/N64. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| FA3 on H200 | −1.276% versus fresh control. |
| H100 recipe on H200 | N64: −10.408% versus control. |

## What did we learn?

- Neither tested transfer beat the H200 control.
- The result supports hardware-specific recipes rather than pooled GPU ranking.

## Decision

Retain the H200-specific incumbent and do not port these settings unchanged.

## Limits and remaining questions

- The conclusion applies to the tested FA3/H100 recipe versions and loads.
- It does not show those techniques are universally inferior on H200.

## Sources

- [teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md)
- [h200-h100-transfer-review-20261031/FINAL_RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/FINAL_RESULTS.md)
