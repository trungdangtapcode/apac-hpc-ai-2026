# Initial split topology

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Which split prefill/decode layouts can run Qwen across the two-node H200 allocation?

## Why investigate this?

Retrospective explanation: the retained records document early topology exploration and setup repairs, but do not preserve a single pre-registered hypothesis. Prefill processes the prompt in parallel; decode generates tokens sequentially. Their resource needs differ, so the team first had to establish which layouts were feasible before comparing service performance.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Parallel layout | Several early disaggregated layouts; exact per-job differences are in the topology records. | Multiple layouts were exercised, including the later split identified as 07/09; no single layout was isolated as the winner. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 results | Job 22197: 1,297.02 good output tokens/s at N32; 22131: 1,472.73 at N32; 22200: 1,649.27 at N40; separate topology 22219: 1,666.01 at N40. |

## What did we learn?

- These runs show that multiple layouts could serve benchmark traffic.
- Because layouts and concurrency differed, the score sequence is not a controlled ranking and cannot establish that one topology caused a gain.

## Decision

Treat the runs as feasibility evidence, then use later matched controls to select a usable split.

## Limits and remaining questions

- H200 only.
- Different loads and layouts prevent causal comparison.
- The retained summary does not define every topology code; consult the cited topology table.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [qwen-experiments/TOPOLOGY_RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/TOPOLOGY_RESULTS.md)
- [qwen-experiments/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/RESULTS.md)
