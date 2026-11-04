# Port teammate settings fairly

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Do the supplied teammate runtime settings show a favorable signal when ported to Iris under a matched comparison?

## Why investigate this?

The teammate supplied socket/core MPI mapping and collated I/O. A same-Iris comparison against organizer settings tests that recipe locally with Scotch input and solver work fixed, but cannot recreate the full Gadi environment.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Runtime recipe | Organizer default MPI mapping and uncollated I/O. | Teammate-supplied socket/core mapping and collated I/O, with the same initialized Scotch source. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Matched means | 24.7453 vs 27.8735 seconds/step; candidate time −11.2228%. |
| Repeat variability | About 18–21% drift; all four reported rank/core maps and force-coefficient trajectories matched. |

## What did we learn?

- This is a qualified favorable short-run signal for a teammate-supplied recipe, not proof of which setting caused it.

## Decision

Report the signal with attribution and uncertainty; do not claim this team's own optimization or a definitive win.

## Limits and remaining questions

- Observed repeats were shorter than organizer sampling recommendations.
- There is no matched three-way trial proving superiority over all alternatives, and Iris is not Gadi.

## Sources

- [Milestone source](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-iris-comparison-20261103/README.md)
- [Curated lineage overview](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/hpc-run-lineage-20261104/README.md)
