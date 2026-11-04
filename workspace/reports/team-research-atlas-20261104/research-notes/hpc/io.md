# Isolate a supplied runtime setting

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does the supplied collated-I/O setting itself improve native solver time?

## Why investigate this?

A borrowed runtime recipe bundled settings, so an apparent gain could not be assigned to I/O. The test isolated collated versus uncollated I/O and reversed the order to check whether the direction persisted.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| I/O setting | Uncollated I/O. | Collated I/O tested against the uncollated setting with a reverse-order check. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Initial apparent change | −6.07% time. |
| Reverse check | +9.35% time; the apparent advantage reversed. |

## What did we learn?

- The I/O claim reversed under the order check; one favorable arm cannot establish a gain.

## Decision

Close the standalone collated-I/O speed claim; retain it as evidence that order control matters.

## Limits and remaining questions

- The result is an Iris practice comparison, not a general statement about collated I/O.
- It does not identify a specific I/O bottleneck or runtime cause.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-own-research-status-20261102/README.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
