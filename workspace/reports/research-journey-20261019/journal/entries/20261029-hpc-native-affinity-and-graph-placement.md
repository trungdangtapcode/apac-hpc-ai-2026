# Actual affinity evidence selects a graph placement candidate

Recorded 29 October 2026, Vietnam time (UTC+7). These are qualification and graph-proxy results; no new solver speedup or NSCC target hit exists.

## Question and actual qualification

The reversed full pair failed to reproduce the large order advantage, and rank affinity had not been collected. Does this Iris MPI runtime bind each rank as intended, and is explicit core binding a distinct treatment? Slurm 2294358 ran a native C probe on iris025, recording 56 MPI calling-thread masks before and after MPI_Init for default, explicit fill/core and explicit span/core launch modes. It completed exit 0:0 in 11 seconds. Independent replay validated all 168 rank records, actual 56-core/two-socket/two-NUMA topology, singleton bijections, same host and exact CPU/NUMA associations; all 188 selected file hashes pass.

Default and explicit fill have identical post-MPI rank masks, so an A/B solver comparison would be a duplicate and was rejected. Span has a different even/odd rank NUMA mapping. This measures a native C MPI calling thread, not actual OpenFOAM/helper-thread affinity or page residency, and does not explain the prior timing bias. The measured runtime is Open MPI 5.0.10rc2 from the site HPC-X 2.50 module.

## Graph evidence and closed branches

A bounded read-only extraction from the owned READY initialized xyz and zyx sources retained all 56 processor-boundary hashes per order, reciprocal weighted edges and per-rank cell counts summing 65,334,765. It read about 660 KB of boundary data per order plus small owner headers. Span increases the logical cross-NUMA face proxy from 375,788 to 996,617 for xyz and 129,700 to 260,523 for zyx. Do not spend a solver allocation on unchanged span without a countervailing hypothesis. These counts are not measured traffic or bandwidth.

## New candidate and independent review

The offline deterministic Kernighan-Lin search uses separate objectives for the two decompositions, a default fallback, 32 valid balanced random starts per order (seeds 2026–2057), exactly 28 ranks per NUMA group and maximum cell load no more than 1.01 times the default maximum. It completed in 6.39 seconds CPU, below 20 seconds. An initial combined-objective output was corrected and retained as historical; different decompositions must be optimized independently.

| Source partition | Default cross-NUMA faces | Candidate | Reduction |
|---|---:|---:|---:|
|xyz|375,788|84,919|77.4024%|
|zyx|129,700|90,953|29.8743%|

Root independently recomputed candidate edge-cut sums, all 56 rank assignments, 28/28 counts and cell-load constraints from retained actual source graphs. For the selected zyx trial, candidate NUMA0 ranks are 0–23,26,28,30,36; the other 28 ranks go to NUMA1. Its cell loads 32,667,376/32,667,389 equal the default group totals. The solver partitions and physics are unchanged; only physical rank placement is proposed. Search does not prove a global optimum or a speed gain. A prior graph-based NSCC candidate lost, so a better cut is only a testable hypothesis.

## Next controlled measurement

Select zyx first, with the same initialized source, and compare identity rankfile placement with the candidate using A–B–B–A short 18-step arms. Both treatments use the same native rankfile launch mechanism. An actual native pre/post-MPI probe must establish identity equals default, candidate equals the intended OS CPU permutation, and each is a 56-core bijection before any solver starts. Logical core indexes must not be mistaken for OS CPU identifiers. A 50-minute 56-CPU request has maximum 46.666667 CPU-hours and fits the current 48-hour headroom under 505, without increasing the envelope. It is not yet submitted by this entry.

Keep all 17 timer samples and 18 Cd rows per arm, fixed iterations and full initialization provenance. This is a non-scored screen, not the prescribed 150-step NSCC result. Reverse/position evidence motivates balanced treatment order, but one short allocation cannot establish robust performance or an official score. Native mapping, source/field/runtime gates and complete output validation remain required.

## Cost, access and preservation

The probe used 0.171111 allocated CPU-hours, conservatively counted as 1; its 4.666667 maximum was retired once. Total consumed 457 / reserved 0 leaves 48 under unchanged 505. No NSCC or AI credits move. NSCC remains blocked at VPN authentication, and its independent native Scotch/xyz/zyx trial stays ready and higher priority when fresh access, queues and credit permit. No submitted payload or submission materials were changed.

[Probe findings and raw result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-mpi-affinity-20261029/RESULTS.md), [graph search](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-mpi-affinity-20261029/GRAPH_SEARCH.md) retain outcomes, source hashes, limitations and exact assignments.
