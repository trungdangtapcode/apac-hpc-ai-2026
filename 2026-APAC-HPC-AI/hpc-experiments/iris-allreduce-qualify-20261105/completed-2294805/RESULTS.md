# Tiny-Allreduce qualification rejects forced tuned candidate

2294805 COMPLETED 0:0 in 20 seconds /56 CPUs. All 28 collected files and source/payload before/after hashes verify. Actual runtime is **Open MPI 5.0.10rc2** under HPC-X 2.50. All four ABBA launches pass 56-rank correctness, identical reported rank bindings, two payloads and two 1,000-call measured blocks per payload. Every raw distribution is replayed with the C nearest-rank p50/p95 rule. Warmup 100 calls precedes each payload; reported values are worst-rank local call durations aggregated after each timed block.

| Arm | Payload | Block 1 p50 /p95, microseconds | Block 2 p50 /p95, microseconds |
|---|---:|---:|---:|
| A1 default |8 bytes|2.478 /3.038|2.443 /2.874|
| B1 forced tuned |8 bytes|4.117 /5.285|4.088 /4.768|
| B2 forced tuned |8 bytes|4.077 /5.251|4.062 /4.719|
| A2 default |8 bytes|2.461 /2.839|2.462 /2.840|
| A1 default |64 bytes|3.374 /4.543|3.459 /4.695|
| B1 forced tuned |64 bytes|5.750 /6.648|5.785 /6.911|
| B2 forced tuned |64 bytes|5.741 /6.617|5.734 /6.851|
| A2 default |64 bytes|3.662 /4.581|3.469 /4.325|

The candidate increases median by 56.8–70.4% and p95 by 44.4–85.0% in the matched block contrasts. It fails every improvement threshold. **Close the forced-tuned candidate; do not send it to a costly native solver trial.** Source/selection/correctness evidence passed, but protocol success is not a performance win.

The candidate explicitly requests tuned recursive-doubling algorithm 3 after runtime capability inspection, with tuned/basic/libnbc/self component list and tuned priority 100. Verbose default logs show ucc priority 100 enabled among selected collective components; candidate logs show tuned priority 100. This records component selection and requested algorithm, not a per-operation native solver profile. No exact UCX data transport or OpenFOAM bottleneck is inferred from library linkage. The prior NUMA timeout remains a different hypothesis.

This experiment uses no mesh, solver iterations or GPU. A faster microbenchmark would still need native confirmation; here the negative gate avoids that expenditure. No other ready solver candidate is established by this qualification. Next research should inspect existing build/runtime choices before selecting a distinct trial, rather than sweep unchanged losing flags.

Allocated cost 0.311111 CPU-hours, conservatively 1; 4.666667 maximum retired once, leaving 1,220 consumed /zero reserved /stage 1,289. These are internal planning units, not billed SU. Full raw arrays, verbose selection logs, exact compiler/runtime output, source hashes and the offline replay are retained.
