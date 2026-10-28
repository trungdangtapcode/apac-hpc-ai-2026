# Native MPI mask qualification: 2294358

The five-minute qualification completed successfully on **iris025** in **11 seconds**, exit 0:0. Independent local replay validated all 56 rank records in each of three modes, actual 56-core/two-socket/two-NUMA topology, singleton bijections, consistent host/CPU-to-NUMA associations, and distinct fill/span ranking. All 188 retained transfer hashes passed. No solver ran.

| Mode | Post-MPI main-thread mask | Rank-to-NUMA mapping |
|---|---|---|
|A-default|56 distinct singleton CPU masks|Ranks 0–27 on NUMA 0 ; 28–55 on NUMA 1|
|B-fill, explicit core binding|Exactly the same masks as A|Exactly the same mapping as A|
|C-span, explicit core binding|56 distinct singleton CPU masks|Even ranks on NUMA 0; odd ranks on NUMA 1|

This Iris runtime already core-binds the observed MPI main threads. Running solver A versus B would duplicate the measured mapping, so that branch is closed before spending solver time. This does not establish actual OpenFOAM/helper-thread masks or explain the earlier full-run timing-order effect. NSCC's different MPI/host stack must not inherit this conclusion.

## Actual communication graph proxy

A read-only extraction from our READY initialized sources verified reciprocal processor-boundary face counts for 56 ranks and read approximately 660 KB per order. Per-rank cell counts sum to the prescribed 65,334,765. Boundary hashes, weighted edges and cell counts are retained in `processor-interface-graphs.json`.

| Hierarchy order | Default/fill cross-NUMA faces | Span cross-NUMA faces | Change |
|---|---:|---:|---:|
|xyz|375,788|996,617|+165.21%|
|zyx|129,700|260,523|+100.87%|

These are unique logical interface faces assigned across the measured CPU NUMA groups, not bytes transferred, page placement, memory bandwidth or a speed prediction. The span candidate worsens this proxy for both source partitions, so there is no present justification to benchmark that mapping unchanged.

The next low-cost question is whether a deterministic 28/28 graph bisection can reduce interface faces while controlling per-NUMA cell load and leaving each rank's partition/physics untouched. Only a real proxy improvement, valid native mapping qualification and a reviewed bounded experiment can justify another solver allocation. This is not an asserted optimization gain; an earlier graph-based NSCC candidate already demonstrated that a nicer graph can run slower.

## Cost and evidence limits

Actual allocated cost is 0.171111 CPU-hours (`56×11/3600`); the conservative local allowance is 1 CPU-hour. The 4.666667 maximum was retired once. Total Iris allowance consumed 457, reserved 0, leaving 48 under the unchanged 505-hour internal envelope. Site SU rate/balance remains unknown and no NSCC/AI credit is used.

The retained text evidence includes native C build output, source/binary hashes, actual compiler/launcher paths and versions, dynamic-library listing, topology, selected environment overrides, all 168 rank JSON records, validation output and scheduler stdout/stderr. The compiled binary is intentionally excluded. This measures the calling main thread before/after MPI_Init; solver behavior, helper threads, frequency, page residency and bandwidth remain unmeasured.
