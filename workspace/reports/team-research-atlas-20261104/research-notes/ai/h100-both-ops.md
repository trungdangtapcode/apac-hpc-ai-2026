# H100 both-phase HPC-Ops

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does applying HPC-Ops to prefill as well as decode improve H100 throughput, and where does added load stop helping?

## Why investigate this?

After a repeated decode-only result, the next bounded question was whether the same existing library helped the prompt-processing phase too. Prefill operates on many prompt tokens at once, so its behavior can differ from sequential decode. Subsequent N54/N56 trials examined whether increasing client concurrency yielded additional useful goodput.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| H100 backend coverage | HPC-Ops selected for decode. | HPC-Ops added to prefill while retaining the decode path; load refined with repeats. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Initial comparison | 2,371.961 versus 2,308.979 control. |
| N54 full runs | 2,430.891 and repeat 2,418.588 good output tokens/s. |
| N56 | No further gain established. |

## What did we learn?

- The all-phase recipe improved the observed H100 operating point in later N54 trials.
- N56 did not justify pushing the load higher.

## Decision

Keep the measured H100 recipe/load as a platform-specific candidate; stop increasing concurrency without useful evidence.

## Limits and remaining questions

- The observations are H100-specific.
- The contribution of prefill HPC-Ops versus interaction with decode/load was not fully isolated.

## Sources

- [journal/JOURNEY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/research-journey-20261019/journal/JOURNEY.md)
- [research-followup-20261018-1323/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1323/RESULTS.md)
- [status-review-20261019-1111/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1111/RESULTS.md)
