# Complete paired local answer-quality test

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

On the complete paired MMLU-Pro set, does the accepted candidate retain at least 99% of the stock FP8 reference score?

## Why investigate this?

The pilot was below the local point gate, so the team evaluated the complete 12,032-question set with fixed prompts, settings, parser, and eight paired shards. The question is score retention relative to the stock FP8 reference, not whether the candidate answers every item correctly. Identical evaluation scope makes the local ratio interpretable, while organiser certification remains separate.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Quality evaluation | Small N16 pilot. | Full paired 12,032-question MMLU-Pro evaluation of stock FP8 reference and accepted candidate across eight paired shards. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Stock FP8 reference | 9,460 / 12,032 correct = 78.623670%. |
| Candidate | 9,452 / 12,032 correct = 78.557181%. |
| Retention | 9,452 / 9,460 = 99.915433%; above the local 99% point gate. |

## What did we learn?

- The candidate scored eight fewer questions correctly than the reference.
- The measured point estimate passes the local ≥99%-of-reference criterion.

## Decision

Record this as a local full-set point-gate pass, not a BTC-certified quality PASS.

## Limits and remaining questions

- This does not establish statistical equivalence on future data.
- It is not organiser certification; acceptance and quality are distinct checks.
- The quality pilot failed the local gate; the full-set result supersedes it for the final local assessment.

## Sources

- [ai-quality-verification-20261103/FULL_RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-quality-verification-20261103/FULL_RESULTS.md)
- [ai-quality-verification-20261103/METHODOLOGY.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-quality-verification-20261103/METHODOLOGY.md)
