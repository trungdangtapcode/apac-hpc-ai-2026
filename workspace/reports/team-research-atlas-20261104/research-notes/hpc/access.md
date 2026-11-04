# Learn the actual cluster route

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Can we reach Iris through its actual login route and run the native OpenFOAM workload?

## Why investigate this?

A remote-command SSH attempt stayed on the gateway and was mistaken for Iris unavailability. The correct route is an interactive forced-TTY jump with no remote command, followed by commands at the Iris prompt. Access, scheduler reachability, and a successful solve are separate checks.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Iris workload validation | No runtime intervention; no full-mesh practice result in this milestone. | Use the interactive Iris route and run the full-mesh practice chain through a 40-step solver test. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Full-mesh practice | Job 2293754; 21.9654 seconds/step over 40 steps. |
| Platform | Iris practice CPU nodes; not an official contest score. |

## What did we learn?

- The interactive route and native MPI chain worked.

## Decision

Keep the access correction and full-chain practice as a prerequisite for later Iris experiments, not as a performance improvement.

## Limits and remaining questions

- This was practice on Iris, not the official four-node ASPIRE evaluation.
- The result is not directly rankable against NSCC or another platform.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-research-journey-20261023/JOURNEY.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
