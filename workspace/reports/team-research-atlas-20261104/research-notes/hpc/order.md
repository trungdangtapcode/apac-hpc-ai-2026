# Test hierarchical axis order

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does changing the hierarchical mesh-axis order produce a repeatable solver advantage?

## Why investigate this?

Hierarchical decomposition assigns mesh dimensions in different orders. A promising full-size zyx observation needed a reverse-order check because allocation or time drift might favor the first arm.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Hierarchical axis order | Compare zyx and xyz layouts. | Reverse arm order in the full-length comparison, job 2294262. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| First zyx observation | 21.2296 seconds/step. |
| Reverse zyx observation | 26.6108 seconds/step; each allocation favored its first arm. |

## What did we learn?

- The low first observation is real, but the reversal undermines a stable zyx advantage. Run-to-run drift requires matched controls.

## Decision

Do not promote zyx based on its isolated minimum; preserve it as an observation and improve the comparison design.

## Limits and remaining questions

- This is Iris practice data, not a contest-platform score.
- A reversed pair indicates confounding but does not isolate its physical cause.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-own-research-status-20261102/README.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
