# Four-node graph-aware rank placement: read-only candidate screen

## Question and prior evidence

The native four-node leader is default Scotch with 512 ranks, 128 per node, at 3.677906731 s/step. Its independent frozen confirmation 25940700 remains queued. A prior one-node NUMA decomposition changed partitions and lost 3.44%; that unchanged branch stays closed. A separate one-node placement graph reduced a logical cut 4.57% but is unmeasured. Neither is proof of a four-node improvement.

This screen instead asks whether the **unchanged 512-way partition** can be assigned to four logical host groups of 128 ranks with fewer interface faces crossing hosts than a contiguous-rank layout. Only an assignment/permutation is changed offline. Processor directories, mesh, fields and solver configuration stay untouched. All graph arithmetic runs on this login workspace, not NSCC compute nodes; remote access reads bounded existing ASCII boundary metadata only.

## Inputs and provenance gates

Collect exactly 512 processor boundary dictionaries from the retained old Scotch run, bounded to 8 MB. Verify strict ASCII decoding, stable file size/mtime during each read, per-member SHA256 and equality of the current decomposePar log with the earlier sealed native intake. Boundary dictionaries can be text despite a global `format binary` header; two initial collection attempts rejected that valid representation and are recorded separately. No binary mesh, fields, authentication state or full environment is copied.

These boundary files were not sealed at original submission time. A matching native decomposition log strengthens provenance but does not prove complete mesh identity, frozen submission or the actual historical rank-to-host mapping. Build a graph only after validating all 512 local rank IDs and reciprocal processor patches with equal face counts. Cross-check native cell totals and available interface totals. Keep the raw text and every hash.

## Search and decision

Use four balanced groups of 128 ranks and the contiguous `rank//128` assignment as a declared logical control. Minimize the sum of unique interface-face weights crossing groups with deterministic, bounded local search. Record the starting objective, every accepted improvement, final assignment, full permutation, seed, search limit, validation and elapsed local CPU time. Verify swap deltas against full recomputation and reject duplicate/missing ranks or unbalanced groups. This heuristic proves no global optimum.

A smaller graph cut is only a selection proxy: it measures neither bytes nor MPI wait, NUMA locality, load balance or solver speed. Keep rank 0 in the first physical slot when rendering any future ordering file. HPE documents `MPICH_RANK_REORDER_METHOD=3` and a custom rank-order file, but deployed-version compatibility and actual MPI_COMM_WORLD-to-host/core placement must be independently validated. A Python probe that reads PMI environment rank IDs is insufficient for a library-level reorder.

No qsub, budget reservation, frozen-payload modification or result claim is authorized by this screen. Keep 25940700's queue position. A future runtime candidate must await its review, fresh budget/capacity checks and demonstrated launcher compatibility; apply the same reorder mechanism with an identity control and candidate mapping to all mandatory MPI stages. Preserve original numerical work and all 150 steps. Close an unhelpful mapping rather than launch a blind test.

## References

- [Native comparison](../four-node-review-20261023/RESULTS.md).
- [Prior one-node placement screen](../rank-placement-screen-20261022/PLAN.md).
- [HPE Cray MPI 24.03 rank-reordering documentation](https://h41374.www4.hpe.com/docs/24.03/mpt/mpich/intro_mpi.html#general-mpi-environment-variables), reviewed 23 October 2026. It documents custom MPI rank ordering; this is not verification of the installed cluster version or runtime binding.
