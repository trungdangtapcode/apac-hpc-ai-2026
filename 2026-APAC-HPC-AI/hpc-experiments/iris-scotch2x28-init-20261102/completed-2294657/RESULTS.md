# Native 10:1 Scotch package-tree cut rejected before initialization

Job **2294657 completed 0:0**, iris001, 56 CPUs, **278 seconds**. Terminal observation **3 November 2026, 00:05:39 Vietnam**. Collection preserves 168 small text/native/config/boundary artifacts; all transfer hashes pass. Offline replay reproduces the original 65,334,765 cells, 56 partitions, all 112 boundary files/reciprocal edges, native total-face summaries and all 56 accepted control-boundary hashes. Canonical mesh check covers eight full source members; working system dictionaries match exact allowed source transforms. Restored 336-field presence was validated by the frozen native validator on compute. Binary processor fields/mesh are not retained and no offline full-field byte recovery is claimed.

| Graph quantity | Default Scotch | Native tree 10:1 | Change |
|---|---:|---:|---:|
| Logical cross-package faces |86,913|119,706|**+37.7308%**|
| Total interfaces |1,035,208|1,037,620|+0.2330%|
| Worst-rank faces |68,534|61,438|-10.3540%|
| Maximum neighbor patches |20|23|+3|

The preregistered cross-package reduction and fanout gates fail. The job explicitly stopped with **GRAPH_FILTER_REJECTED_NO_READY_NO_INITIALIZATION**. No renumberMesh, potentialFoam, applyBoundaryLayer, READY or solver measurement exists. This is a successful native cut and negative triage outcome, not a successful benchmark or speedup. Preserve the losing graph and raw output; do not relax its thresholds afterward.

A bounded source review confirms the pinned OpenFOAM wrapper normalizes weights to 10/1 and selects SCOTCH_archTleaf unless processorWeights takes precedence. It does not reverse the supplied weight vector; there is no demonstrated cost-order inversion. Observed MPI ranks form two 28-rank package groups, but exact deployed SCOTCH labeling was not traced. Face counts are logical graph proxies, not measured traffic or hardware costs. The optional remote alternative-bucket recount timed out and added no evidence.

**Next decision:** one targeted falsification may hold domains `(2 28)` fixed and strengthen only synthetic weights to `(1 0.01)` / 100:1, with all graph gates unchanged. This tests whether stronger separation changes the graph; it does not predict a gain. If that candidate also rejects, close further weight-only tuning for this topology. All required initialization and a later separately admitted native solver comparison are still necessary before any performance claim.

Allocated cost **56 × 278 / 3600=4.324444 CPU-hours**, conservatively 5. Retired the original 28 maximum once under lock. Local planning **944 consumed, 0 reserved, stage 1,009**. Another 28-hour maximum fits this existing stage; no increase, billed-SU claim or NSCC/AI transfer. No new job is claimed by this result.

[Offline replay](replay.py), [structured review](REVIEW.json), [collection/scheduler evidence](collection.json). Data below collected/ support the exact negative outcome. Frozen past payloads and other-track/submission materials are unchanged.
