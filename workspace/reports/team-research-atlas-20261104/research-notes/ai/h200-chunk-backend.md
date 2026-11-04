# HPC-Ops decode with DeepGEMM/chunk8192

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Under the newer H200 prefill runner and chunk size, does HPC-Ops decode beat automatic backend selection?

## Why investigate this?

The serving setup had changed since an earlier decode test: prefill runner and chunk size were different. That can alter overlap, queues, and the operating point, so the decode decision needed a new same-load comparison. The intent was to test the backend choice under current context while monitoring first-token and streaming latency separately.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Decode backend | Automatic decode selection. | HPC-Ops decode with DeepGEMM prefill and chunk 8192 in the N58 comparison. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 job 24721 | 2,938.628 versus same-load control 2,780.403 (+5.6907%). |
| Latency | TTFT rose; ITL improved. |

## What did we learn?

- The interaction was promising at N58 and motivated independent matched confirmation.
- The score alone does not say which backend mechanism caused the change.

## Decision

Continue with a fresh control and independent repeat before treating the setting as incumbent.

## Limits and remaining questions

- This pair alone was not sufficient confirmation.
- Changed serving context means this result should not be compared causally with older N52/N54 runs.

## Sources

- [teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md)
- [research-followup-20261019-0600/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md)
