# N60 HPC-Ops interaction repeat

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does the HPC-Ops decode plus revised prefill interaction reproduce at N60 against a fresh control?

## Why investigate this?

After the N58 candidate looked promising and a separate run showed the automatic control was stable, the next step was a fresh matched comparison and independent treatment repeat. The question concerns the complete serving recipe under the revised phase setup, not the intrinsic speed of one kernel.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Decode MoE runner | Automatic selection (auto). | HPC-Ops (hpc_ops); other serving settings held fixed. |
| Fixed prefill | DeepGEMM / chunk 8192. | DeepGEMM / chunk 8192, unchanged. |
| Workload and hardware | N60, fixed 4000 input /200 output tokens, 16 H200. | Same load, workload, topology, attention and transport. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Automatic decode control 24912 | 2,838.853 good output tokens/s. |
| HPC-Ops repeat 24913 | 2,989.175 good output tokens/s; +5.295% versus control. |
| Mean TTFT | 822.292 → 947.627 ms, about +125 ms. |
| Mean request ITL | 16.579 → 14.934 ms, about −1.64 ms. |
| Independent repeat | Approximately 0.033% below original HPC-Ops treatment 24738. |

## What did we learn?

- The configuration-level goodput improvement reproduced closely in this workload.
- The repeat supports the decision, while the latency tradeoff remains material.

## Decision

Retain the tested interaction for subsequent load tuning; describe it as a recipe-level result.

## Limits and remaining questions

- Cannot assign the full gain to one decode kernel or add it mechanically to earlier gains.
- Applies to the tested H200 topology, phase settings, and request workload.

## Sources

- [ai-final-report-20261030/REPORT.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-final-report-20261030/REPORT.md)
- [research-followup-20261020-0028/H200_RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0028/H200_RESULTS.md)
- [ai-final-report-20261030/MOCK_QA_EVIDENCE.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-final-report-20261030/MOCK_QA_EVIDENCE.md)
