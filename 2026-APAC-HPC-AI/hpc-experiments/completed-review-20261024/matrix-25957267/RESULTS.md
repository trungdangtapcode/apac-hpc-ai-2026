# Binding interface controls lose; early launcher capture is needed

## Observations

Job **25957267** finishes Exit1 after24seconds. All retained text files pass manifest hash/size checks; sources remain sealed. The two no-shim controls each emit512 unique rank diagnostics with singleton masks before MPI initialization. Method0 explicit binding has487 broadened0–255 masks and25 remaining singletons. Method3 PALS environment binding has489 broadened masks and23 singletons. Neither alternative consistently retains affinity; close those unchanged controls rather than repeating them.

The first PMPI shim emits512 unique world-rank records. It restores and verifies253 ranks, but rejects259 because its own entry-time pre-init mask is already broad/truncated. The -1 restore status is a sentinel for a call not attempted on that failed precondition, not a measured sched_setaffinity error. Its source does not guess a replacement CPU. The C caller had recorded a singleton before its MPI call, so the wrapper's later saved mask is too late for some ranks; the precise internal transition remains unexplained. This is partial recovery, not a successful complete mapping. The identity command returns255 and no candidate runs.

## Decision and next controlled change

Preserve both losing interface controls and the failed shim. Derive a separate application exec wrapper that captures its actual singleton launcher CPU before starting MPI code, records it, and passes that exact CPU to an opt-in PMPI restoration hook. Verify the restored mask, every actual MPI world rank, physical core and NUMA slot; never substitute rank arithmetic or the broad entry mask for the captured CPU. Use identical launch treatment for identity and candidate. Qualify MPI_Init_thread as well as MPI_Init because installed OpenFOAM Pstream source calls MPI_Init_thread (runtime binary entry still requires an audit).

This is a new hypothesis with earlier capture provenance, not a weakened topology gate or a demonstrated fix. No solver or speedup result. [Known terminal budget reconciliation](budget-reconciliation.json) retires only this42.666667-SU maximum and adds a rounded4-SU allowance from24seconds×512cores at rate1; unknown shared costs remain. Exact posted billing is unknown.
