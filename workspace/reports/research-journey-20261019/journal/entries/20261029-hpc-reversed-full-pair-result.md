# Full reverse-order result rejects the large order-gain claim

Reviewed 29 October 2026, Vietnam time (UTC+7). The actual completed job ran on 28 October. HPC only; AI state is unchanged.

## Question and exact change

Would zyx keep its full-length advantage when executed second, after xyz? Job 2294262 used a fresh exclusive Iris allocation on iris005, with the same 56ranks, hierarchy (7 4 2), FP64 OpenFOAM v2512, fixed iterations, initialized sources and 150 steps per arm. The only experimental ordering change was xyz first, then zyx. Parent 2294234 used the opposite order on iris024. Submitted payloads were preserved.

## Reviewed evidence

Slurm confirms COMPLETED 0:0, elapsed 7,635 seconds at 56 CPUs. All 129 retained selected file hashes passed. Independent native replay reproduced all 149 timings and 150 total Cd rows per arm exactly. Sources, isolated copies, initialized-field seals, frozen 49-file kit, executable/library identities, fixed iterations and all 10 recorded phase commands pass.

| Allocation | First arm mean (s/step) | Second arm mean (s/step) |
|---|---|---|
| 2294234, iris024| zyx 21.229594| xyz 26.953799|
| 2294262, iris005| xyz 21.823904| zyx 26.610796|

zyx was 21.2371% faster in the first pair but 21.9342% slower in the reverse pair. The first arm was faster in both allocations. This does not reproduce a robust 21% configuration gain. Different nodes and serial ordering remain confounded; neither thermal throttling, memory bandwidth nor NUMA is established as the cause.

Both same-order total Cd trajectories match their respective parent trajectories exactly. Across different orders, final Cd differs by 1.61846%; preserve that output qualification. New xyz P95 is 21.743313s and maximum 70.992053s at Time 3; zyx P95 is 35.1638s and maximum 70.257s at Time 48. Both native sampling recommendations exceed 149 (361/354), so the retained full sample count does not satisfy that native within-run recommendation. Do not trim slow steps or promote these correlated samples as independent allocation repetitions.

## Available resource inspection

Both nodes report Xeon Platinum 8280, 56 cores, two sockets/two NUMA domains and SMT disabled. On the new node, before first/second solve MemAvailable was approximately 180.6 / 179.5 GB and swap 0. Free memory fell while cache grew; these snapshots do not show memory exhaustion. Whole-node page-fault deltas are not per-process attribution. Command-level CPU/RSS and source/copy phases were reviewed. Actual post-MPI rank masks, per-rank frequency, memory bandwidth and NUMA page residency were not collected. No hardware-cause claim follows.

## Decision and next measurement

Keep native NSCC Scotch/xyz/zyx first when access permits: the goal remains below 3.364622070s/step on NSCC, which has not been achieved by a new candidate. A fresh bounded VPN retry on 28 October UTC again returned Authentication failed; no usable SSH/PBS access, current NSCC credit or new submission exists.

Do not repeat the unchanged full Iris order pair to fill the queue. A small, bounded native MPI affinity qualification can collect the missing pre/post-MPI_Init main-thread masks for default launch, explicit core binding and rank order. It must verify a real mechanism difference before any placement performance screen, must not claim a solver improvement, and must not block independent NSCC native work. It uses only remaining Iris planning headroom; no CPU budget extension is authorized by this record.

## Cost and preservation

The allocation used 118.766667 CPU-hours by terminal elapsed arithmetic. Retire the 168-hour maximum exactly once and conservatively count 119 CPU-hours. Total Iris consumption is 456, reserved 0, leaving 49 under the unchanged 505-hour internal ceiling. These are local planning CPU-hours, not billed SU or a site credit balance. No NSCC or AI credit moved.

[Full result and raw evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-reverse-20261028/completed-2294262/RESULTS.md) retain both the failed hypothesis and numerical outputs. The earlier 21.24% report is a historical single-allocation observation, not the present validated tuning conclusion.
