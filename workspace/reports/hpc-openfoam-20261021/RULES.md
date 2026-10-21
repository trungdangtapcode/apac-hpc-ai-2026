# OpenFOAM changes: Basic, Bonus and Prohibited

Source: the pinned [task rules and F0–F5 addendum](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/2.%20OpenFOAM%20HPC%20Task%20Rules.md).
Where an earlier paragraph conflicts with its named replacement, use the addendum.

| Tier | Change | Evidence needed |
|---|---|---|
| Basic | Unmodified official openfoam.com v2512, site module or rebuild | Exact version, WM settings and build recipe |
| Basic | hierarchical or scotch, chosen rank count and method coefficients | Text dictionaries, decomposition logs |
| Basic | Required endTime 40 / 80 / 150 for 1 / 2 / 4 nodes | Complete logs at each size |
| Basic | CPU placement, affinity, SMT, MPI/UCX environment | Job script, actual mapping and environment |
| Basic | Safe double-precision compiler settings; label size 32 or 64 | Exact flags; wmake-rule patch if changed |
| Basic | Runtime OptimisationSwitches, fileHandler, hostRoots, ioRanks | Exact command/environment; unchanged numerical work |
| Basic | Split serial preparation from dependent parallel jobs | Every Allrun step retained, dependency and logs |
| Bonus | Other decomposition methods, such as multiLevel, kahip, metis | Exact method/build/input and method-only sanity-check exception below |
| Bonus | Other renumbering options or custom manual partition | Source/text settings and applicable F3 check |
| Bonus | Source/communication/layout changes, preload/wrap injection | Patch/source provenance, same-work argument, F3 check |
| Bonus | GAMG processorAgglomerator redistributing unchanged work | Matched pre-change baseline and F3 check |
| Bonus | fast-math / Ofast / other value-unsafe floating-point settings | Still double precision; F3 proof, no automatic correctness assumption |
| Prohibited | GPU acceleration, float/mixed precision | Forbidden in every tier |
| Prohibited | Mesh/physics changes, omitted layers of the preparation chain | Forbidden in every tier |
| Prohibited | fvSchemes changes or changed solver tolerances/maxIter/smoothers/coarse-grid thresholds/relaxation | Changes numerical work; forbidden in every tier |
| Prohibited | Removing function objects, reducing required solver log output, or fabricating output/timings | Forbidden in every tier |

The native scotch domains/domainWeights coefficients are distinct from choosing
method multiLevel. F1 allows coefficients of scotch; the former is therefore
our proposed Basic hypothesis, subject to exact deployed-version validation.
The latter is listed as Bonus. Do not relabel a different method as Basic by
calling both “multilevel.” No source change is planned for the initial campaign.

For Basic, Cd at the three endpoints is a sanity check, with no universal numeric
percentage gate. For a Bonus change needing F3, preserve the same method,
coefficients, ranks and node count in a pre-change baseline. Compare the three
separate 40/80/150-step endpoint Cd values, each to its own baseline. A
bit-identical coefficient.dat passes; otherwise each endpoint must be within
±0.5%. This is not a comparison to the AI 99%-reference quality rule.

F2 explicitly exempts a pure decomposition-method swap, with unmodified source
and all other files as Basic, from needing an extra baseline. That case uses
the Basic sanity check instead. This exception does not waive proof for an
additional compiler, renumbering or source change combined with the swap.

Required text deliverables: decomposition method/ranks/coefficients; full
preparation and solver steps; version/build recipe; four-node solver log with
Average plus coefficient.dat; 1/2/4-node scaling; caseDefinition, decomposeParDict
and controlDict; presentation slides. MPI profiling is strongly recommended.
Do not include mesh binaries, processor trees, solver binaries or a full install
in the submission. The research backup and official text submission are
separate artifact selections.
