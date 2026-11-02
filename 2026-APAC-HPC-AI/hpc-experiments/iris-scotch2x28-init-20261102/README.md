# Iris native Scotch socket-tree cut and conditional initialization

**Reviewed payload; actual execution is tracked in STATUS.md and the scheduler receipt. No deployment, submission, reservation, or solver measurement is included.** This candidate is a fresh native Scotch decomposition of the official 65,334,765-cell case, with a graph filter before the required parallel initialization stages.

## Why this is distinct

The reviewed xzy comparison, job 2294644, failed the unchanged-branch stop rule: xzy was **10.25252% slower pooled**, with adjacent differences **+1.84160% and +19.78388%**; Scotch repeats changed **-11.75533%** and xzy repeats **+3.79146%**. Xzy native sample recommendations **69/97** both exceed the 51 measured intervals. The earlier favorable 40-step sign did not reproduce. The complete raw collection and independent review are retained in `iris-xzy52-reverse-20261102/completed-2294644/`; close this unchanged xzy speedup claim.

Iris records show two Intel CPU packages, each with 28 cores. The reviewed 56-rank Open MPI map places 28 ranks on package 0 and 28 on package 1. Therefore `(2 28)` is a topology-matched native Scotch tree hypothesis: two package-sized groups, each with 28 ranks. This differs from the earlier NSCC `(8 16)` test, which represented its eight NUMA groups at 128 ranks and cannot be transferred as Iris performance evidence.

The candidate uses `domains (2 28); domainWeights (1 0.1);`. The pinned OpenFOAM v2512 Scotch code converts these weights to an integer 10:1 hierarchy before calling `SCOTCH_archTleaf`; the values are synthetic priorities, not measured socket latency or bandwidth. `processorWeights` is intentionally absent because its nonempty path takes precedence over `domains` and `domainWeights`.

The NSCC `(8 16), (1 0.1)` cut passed its preregistered graph filter, with cross-group faces down 10.63%, total interface faces up 1.34%, worst-rank faces up 2.31%, and maximum cell excess near 1.01%. That is only a precedent for trying a native tree; it neither validates this Iris-specific geometry nor predicts its speed.

## Controlled preparation and early decision

The job starts from the pinned official case text and shared serial mesh, writes a new job-specific case root, and never changes the accepted default Scotch tree. It changes only `nCores=56`, `decompositionMethod=scotch`, and the new Scotch coefficient block. It verifies all 41 canonical source pins and all eight full mesh members, then runs native `decomposePar -constant` and `restore0Dir -processor`.

A reciprocal processor-boundary parser compares the fresh cut to the accepted 56-rank default Scotch tree. It groups ranks `0–27` and `28–55` according to the observed package mapping. Initialization proceeds only if every preregistered triage gate passes:

- Cross-package interface faces decrease by at least 5%.
- Maximum cell count is no more than 3% above the mean.
- Total unique interface faces rise by no more than 10%.
- Worst-rank interface faces rise by no more than 10%.
- Worst-rank processor-neighbor patches rise by no more than 2.

These are research filters, not contest score thresholds or accuracy gates. If any fails, the job preserves the cut, native logs, boundary hashes, and comparison, exits with an explicit `GRAPH_FILTER_REJECTED_NO_READY_NO_INITIALIZATION` state, and does not create `READY` or an initialized manifest. If all pass, it runs `renumberMesh`, `potentialFoam`, and `applyBoundaryLayer` on 56 ranks; verifies native v2512/double precision, exact commands, `End`, no fatal markers, and all 336 time-zero field seals; then creates a separate initialized manifest and `READY` record.

## Resource limit and scope

One exclusive Iris node, 56 CPUs, zero GPUs, at most 30 minutes / 28 allocated CPU-hours. The internal wall-clock deadline is 1,740 seconds. Native phases have full-stage timeout caps and refuse to start without enough remaining time; there is no solver run and no claim of Iris SU, billed usage, or solver improvement. A passing preparation only makes a later matched solver comparison eligible for separate review and admission.

OpenFOAM's competition rules list native Scotch coefficients under Basic when the v2512 source/build and all other numerical inputs remain unchanged. This bundle changes no source, solver tolerance, physical mesh, or function object. Exact submission eligibility remains a human/organizer rule check; this is a research preparation, not a contest submission package.

Root review corrections before the first freeze: use the retained 41-pin payload case rather than an unversioned shared case; call restore0Dir through the OpenFOAM RunFunctions shell function; keep the internal 1,680-second deadline beneath the 1,740-second outer wrapper; bind all 56 control boundary hashes to the accepted default manifest and replay the native total-face counts. If initialization runs, recheck the eight shared mesh members and read-only control graph before writing READY. No frozen submitted payload was altered.

The earlier xzy confirmation failed: no stable own scored-platform gain exists. This native topology-aware partition changes cells assigned to ranks, unlike the closed rank-permutation experiment. Weights remain a synthetic 10:1 assumption, not a measured hardware cost.
