# Reproduce the organizer recipe

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can the organizer's four-node Scotch recipe be reproduced with the full prescribed work?

## Why investigate this?

The earlier rank-density results were useful observations but did not provide a strong, independently submitted reference. Repeating the organizer recipe on four nodes with 512 ranks and all 150 steps provides a clearer baseline for later work. It is a reproduction exercise, not an optimization by this team.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Reference workload | Earlier observations used varying node counts, rank counts, or run endpoints. | Job 25940700: organizer Scotch, four nodes, 512 ranks, full 150-step chain. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Job | 25940700. |
| Native average | 3.364622070 seconds/step. |

## What did we learn?

- The organizer recipe was reproduced on the intended four-node scale.
- This gives subsequent comparisons a better anchored reference.

## Decision

Retain this run as baseline reproduction, not as a team-created speedup.

## Limits and remaining questions

- It does not establish an optimization over the organizer's own reference.
- Do not compare its raw seconds with Iris or Gadi to claim a cross-platform gain.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/notes/HPC_CURRENT.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
