# Sparse decode graph experiment

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can reducing decode graph buckets lower memory use and improve service goodput?

## Why investigate this?

The hypothesis was that fewer captured graph variants might reduce memory pressure. Graph capture prepares reusable GPU execution paths; however, a memory proxy is not itself the competition metric. The full run tests whether the reduced footprint translates into qualifying-request throughput.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Decode graph batch buckets | Dense list 1–64 (64 captures). | [1, 2, 4, 8, 16, 32, 48, 50, 52, 54, 56, 64] (12 captures). Maximum 64 retained. |
| Compilation | torch.compile disabled. | Still disabled; this is a graph-bucket trial, not a compile speedup. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 job 27510 | 3,029.861122 good output tokens/s, −0.370208%. |
| Memory per rank | 1.15 GB to 0.36 GB. |
| Logged capture memory per rank | 1.15 → 0.36 GB; native capture log label, not total sampled VRAM. |
| Logged capture time | 101.46–101.49 → 95.98–96.05 seconds. |

## What did we learn?

- The memory measure fell substantially, but goodput did not improve.
- Lower memory use alone was not sufficient to justify a slower measured service.

## Decision

Close the sparse-graph candidate under the current objective.

## Limits and remaining questions

- Memory figures are the recorded graph-related measure, not total GPU VRAM.
- No evidence that graph memory constrained this deployment.

## Sources

- [ai-final-report-20261030/REPORT.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-final-report-20261030/REPORT.md)
- [h200-sparse-decode-compile-20261029/RESULTS-27510.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h200-sparse-decode-compile-20261029/RESULTS-27510.md)
- [h200-sparse-decode-compile-20261029/PLAN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h200-sparse-decode-compile-20261029/PLAN.md)
