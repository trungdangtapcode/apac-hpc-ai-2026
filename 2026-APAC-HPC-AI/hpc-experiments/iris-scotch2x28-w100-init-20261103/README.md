# Iris native Scotch 100:1 weight falsification

**Prepared only. This folder has no deployment, scheduler receipt, reservation, or solver measurement.** It derives a fresh native Scotch cut and runs the required initialization stages only if the unchanged predeclared graph gates pass.

## Why this single follow-up

The preceding native Iris Scotch candidate used `domains (2 28)` and `domainWeights (1 0.1)`, which OpenFOAM normalizes to synthetic integer weights 10:1. Its native cut was rejected before initialization: logical rank28 cross-package faces increased 37.7308% against the accepted default Scotch tree; total faces increased 0.233%; worst-rank faces decreased 10.354%; and maximum neighbor patches rose by three. Thus the graph hypothesis did not pass.

This one follow-up changes only the synthetic domain weights to `(1 0.01)`, normalized to 100:1 by the pinned OpenFOAM implementation. Domains remain `(2 28)`, the mesh, canonical 41 text inputs, control tree, graph grouping, and all five triage gates remain fixed. This is a bounded falsification of whether a stronger synthetic tree preference changes that graph outcome. It is not a measured socket-cost model. If this candidate also fails the unchanged graph gates, stop all further weight-only tuning for this topology.

## Method and safeguards

The job verifies the 41 canonical input pins and eight full serial mesh members, then runs native serial `decomposePar -constant` and `restore0Dir -processor` on a fresh job-specific case. A reciprocal processor-boundary parser compares the cut to the accepted default Scotch tree, whose 56 boundary hashes and native face total are rechecked. Rank groups 0–27 and 28–55 follow the observed Iris two-package, 28-core-per-package MPI map.

Initialization runs only if every unchanged research triage gate passes: cross-package faces decrease at least 5%; maximum cell count is at most 3% above mean; total interfaces rise at most 10%; worst-rank faces rise at most 10%; and worst-rank neighbor patches rise at most two. A rejected cut writes diagnostics and creates no READY tree. A passing cut must complete `renumberMesh`, `potentialFoam`, and `applyBoundaryLayer`, validate native OpenFOAM 2512/double precision and all 336 time-zero fields, recheck the shared mesh and read-only accepted control graph, then seal a separate manifest. These graph gates are not contest score thresholds or solver-performance predictions.

Resource ceiling: one exclusive Iris node, 56 CPUs, zero GPUs, 30 minutes (28 allocated CPU-hours). Internal deadline is 1,680 seconds beneath the 1,740-second wrapper and 1,800-second scheduler limit. No solver is run.

## Attribution and limits

The treatment is an ordinary native OpenFOAM Scotch configuration, not a novel partitioning algorithm. The pinned OpenFOAM v2512 source documents the weight conversion and `SCOTCH_archTleaf` selection. The specific runtime SCOTCH library’s internal labeling order is not inferred as a proven hardware placement; rank//28 is only the observed logical MPI grouping used for this graph proxy. No hardware cost, interconnect traffic, or performance claim is made.
