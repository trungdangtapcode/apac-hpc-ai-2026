# Separate a graph proxy from runtime

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can partition-interface counts alone explain which method will run faster?

## Why investigate this?

After the NUMA candidate's lower cut coincided with slower solver time, a graph-only comparison could help distinguish what that proxy measures from what it omits. The N256 screen compared partition interfaces without running the solver. That makes it useful for narrowing hypotheses, but not for ranking solver performance.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Partition screen | No N256 interface comparison in this test. | Compare N256 partition interfaces during preparation; do not run solver. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Job | 25907772. |
| Outcome | Preparation and interface comparison only; no solver speed ranking. |

## What did we learn?

- The graph count describes logical partition boundaries, not bytes transferred, hardware traffic, or waiting time.
- This screen is mechanism evidence for choosing what to measure next, not a speed result.

## Decision

Keep graph counts as a screening diagnostic and require native timing before promoting a decomposition.

## Limits and remaining questions

- No solver ran, so no seconds-per-step result exists.
- Logical groupings do not prove physical CPU or NUMA placement.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-research-journey-20261023/JOURNEY.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
