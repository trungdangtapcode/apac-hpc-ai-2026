# Exact packaged entry failure and acceptance

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does the exact portable AI entry start correctly, pass the result reader, finish the benchmark, and clean up?

## Why investigate this?

A fast local recipe is not enough if the package fails at deployment. The first attempt found that the router health check could return before model registration completed. The fix changed readiness validation to wait for the model/worker state, then reran the packaged entry. This is an operational acceptance check, not a serving optimization comparison.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Readiness check | Router health response accepted before model registration was complete. | Wait for valid model registration and live worker state before proceeding. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Job 28194 | Failed before benchmark because readiness was premature. |
| Job 28197 | Accepted and completed in 611 seconds at N64; 3,051.518173 good output tokens/s. |

## What did we learn?

- The exact packaged workflow completed serving, result parsing, performance checks, and cleanup after the readiness fix.
- The accepted score is a deployment observation, not a matched optimization gain.

## Decision

Keep the readiness fix and the accepted package as the portable entry evidence.

## Limits and remaining questions

- No paired control was run in this acceptance pair.
- Acceptance does not prove an official organiser submission or quality certification.

## Sources

- [ai-final-report-20261030/REPORT.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-final-report-20261030/REPORT.md)
- [final-portable-acceptance-r2-20261102/REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/REVIEW.md)
