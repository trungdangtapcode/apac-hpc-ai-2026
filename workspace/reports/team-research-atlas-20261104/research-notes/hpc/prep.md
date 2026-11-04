# Test preparation memory policy

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does changing the preparation child's memory policy change where file-backed pages are observed?

## Why investigate this?

The prior native comparison was incomplete, while a preparation-stage mechanism offered a cheaper hypothesis. The test copied and hashed files under inherited versus interleaved memory policy and inspected node-wide file-page counters; it did not run OpenFOAM.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Preparation-child memory policy | Inherited parent memory policy. | Interleaved NUMA policy for child copy/hash preparation; no solver invocation. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Qualified preparation job | 2294675; four copy/hash preparations. |
| Aggregate file-page observation | Inherited arms: about 0 / 9.78 GiB across the two NUMA nodes; interleaved arms: about 4.89 / 4.89 GiB twice. |

## What did we learn?

- The policy changed aggregate page-counter distribution, providing mechanism evidence but no solver speedup.

## Decision

Use the result to justify a separately controlled native test, while keeping performance claims open.

## Limits and remaining questions

- The counters are node-wide and do not attribute every page to a particular file.
- No solver was run; the measurement cannot show improved runtime or locality during solving.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-iris-comparison-20261103/README.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
