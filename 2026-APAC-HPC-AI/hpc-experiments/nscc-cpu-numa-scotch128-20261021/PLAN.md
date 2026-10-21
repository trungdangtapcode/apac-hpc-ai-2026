# NUMA-aware native Scotch partition screen

## Question and prior observations

The accepted one-node hierarchical run is 14.921981 s/step. Default Scotch reduces maximum processor interface faces from 131,252 to 42,141 and unique interface faces from 2,109,346 to 1,549,377, but increases maximum neighbor count from 16 to 35 and cell imbalance to 1.178%. The same-node H→S pair 25907325 is still running when this hypothesis is written; its control completed provisionally at 14.787224 s/step. No final candidate speedup is assumed.

The pair's separate atomic affinity probe verifies rank=CPU 0–127 on EPYC 7713, eight NUMA nodes, and each contiguous block of 16 ranks maps to one NUMA CPU set. This observation makes a native topology-aware partition hypothesis testable. It does not measure actual memory page placement, MPI traffic or a NUMA bottleneck. The summary confirms two sockets but does not individually map CPUs to sockets, so do not add an unverified socket tier.

## Hypothesis and exact change

Native Scotch can use a tree architecture rather than treating all 128 destinations as equally distant. Add only:

```
scotchCoeffs
{
    domains       (8 16);
    domainWeights (1 0.1);
}
```

This describes eight groups of sixteen ranks. The source normalizes weights to integers (10,1). The 10:1 ratio is a deliberately contrasting synthetic partition objective, not a measured hardware latency or bandwidth ratio. It may worsen total cuts, fan-out, balance or solve time. No processorWeights field is present because its nonempty branch overrides the tree. Do not invent speedups or interpret the weights as actual costs.

Control is reviewed native default Scotch N128, same official archive, rank count, fixed physics/solvers and original function objects. Candidate uses a fresh split/root, never mutates either accepted tree or the active pair. Keep v2512 and double precision. Preparation does not perform or claim a solver result.

## Low-cost screen and decision

After the active pair is terminal, collect and review its full result and reconcile CPU costs under the ledger lock. Only submit this serial preparation if the existing 100-SU wave ceiling and queue caps can cover its entire 8-SU maximum. Request 32 CPU cores, one serial task, 96 GB, no GPU, at most 15 minutes. Check the native tree branch executes, full mesh identity, 128 partitions/65,334,765 cells, all restored fields, successful exit/End, cell balance and processor neighbors/interfaces. Compare both total and cross-NUMA interface faces using actual processor boundary neighbor graphs and the verified logical rank-group map. Label physical grouping conditional on a future matching placement probe.

A cut-only result is a cheap hypothesis filter, not a speed estimate. Close or revise a branch with no cross-group cut reduction or a large imbalance/interface penalty. Promote a candidate to a separately budgeted solve only after these checks; do not increase the 100-SU cap or submit an underfunded solve. No spending while the prior allocation is active. No blind duplicates, AI jobs, schedules or submission-material changes.

## Evidence and primary reference

- placement-analysis.json links the actual 128 atomic records and compute-node topology; original live evidence stays in ../nscc-cpu-method-pair128-20261021.
- Pinned OpenFOAM v2512 source revision 87ed40d256d22ea38fcc648dfc82a22162427b18, scotchDecomp.C, SHA256 0f78fb20a662d44b4e59fde6aa47292f20cab5e7364c4ddea4adcc3a67065018. Local source and manifest are in ../source-review-20261021. The processorWeights precedence, domains/weights normalization and SCOTCH_archTleaf call were read directly.
- [Exact primary source](https://gitlab.com/openfoam/core/openfoam/-/blob/87ed40d256d22ea38fcc648dfc82a22162427b18/src/parallel/decompose/scotchDecomp/scotchDecomp.C).

No new native execution or improvement is claimed by this static review.
