# Separate N60 repeat/control

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Is the automatic-decode control stable across a fresh H200 N60 run?

## Why investigate this?

A promising candidate comparison is only useful if the control itself is stable. This run deliberately repeated the incumbent automatic-decode configuration separately from the N58 treatment, providing a current reference for interpreting a later matched treatment repeat.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Decode selection | HPC-Ops candidate comparison at N58. | Automatic decode incumbent rerun at N60 as a fresh control. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 job 24732 | 2,836.531 versus original control 2,839.532 good output tokens/s. |

## What did we learn?

- The two control measurements were close, supporting control stability for this configuration.
- This is not a repeat of the HPC-Ops treatment and does not confirm its gain.

## Decision

Use the stable fresh control to interpret the separate N60 treatment repeat.

## Limits and remaining questions

- Only this automatic-decode setting is checked.
- Control stability does not prove the treatment effect or eliminate run-to-run variability.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [research-followup-20261019-0600/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md)
