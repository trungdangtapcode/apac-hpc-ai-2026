# Usable split baseline

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

What repeatable service configuration can serve as a baseline for later controlled tuning?

## Why investigate this?

Once the team had a working disaggregated path, it needed a stable reference before changing backends or load. Two prefill replicas can process independent prompts while a decode worker generates their continuations. Tensor parallel (TP) spreads layer computation across GPUs; expert parallel (EP) distributes the MoE experts. A baseline makes later candidate/control comparisons interpretable.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| H200 role allocation | Earlier topology experiments and recovery paths. | Two TP4 prefill replicas feed one TP8/EP8 decode worker; subsequent full runs and controls use this as the retained split baseline. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 job 22415 | N48: 1,912.30 good output tokens/s. |
| Later controls | Near 1,911 good output tokens/s. |

## What did we learn?

- The configuration provided a usable reference point for matched tuning.
- The close later controls suggest this operating point was reproducible at that stage.

## Decision

Retain it as a matched-tuning baseline, not as a claim of globally optimal topology.

## Limits and remaining questions

- The measurements are from the historical workload and system state.
- The evidence does not exhaustively compare every possible layout.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [serving-tuning/PLAN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/PLAN.md)
