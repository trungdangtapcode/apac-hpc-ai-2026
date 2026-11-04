# Heterogeneous TP8 warmup failure

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Why did a heterogeneous tensor-parallel prefill/decode pair fail before it could be scored?

## Why investigate this?

The model workers could load, but the two roles still had to establish a usable request path and pass a warmup request. Investigating this boundary mattered because a model that is resident on GPUs is not yet a working inference service. The retained evidence localizes the failure to the pair setup/transfer path; the specific underlying cause was not measured.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Worker state | Workers loaded and reported ready. | The prefill/decode pair did not complete warmup within the job window. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Job 22271 | Warmup timeout; AIPerf scoring did not begin; no performance score. |

## What did we learn?

- This was a setup failure before scored serving, not a low-throughput benchmark result.
- It motivated source inspection of the KV-transfer descriptor path; that is a research lead, not proof that descriptors caused the timeout.

## Decision

Inspect the handoff path and preserve the failed run as a distinct failure class.

## Limits and remaining questions

- No successful control score exists for this exact attempt.
- No phase timer or direct causal diagnosis was retained.

## Sources

- [teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md)
- [qwen-experiments/TOPOLOGY_REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/TOPOLOGY_REVIEW.md)
