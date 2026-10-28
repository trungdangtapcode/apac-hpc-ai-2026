# Reversed Iris full-run pair: job 2294262

## Finding

The full reverse-order run does **not** reproduce the earlier apparent zyx advantage. In job2294262 on `iris005`, `xyz` ran first and averaged **21.823904 seconds per step**. `zyx` ran second and averaged **26.610796 seconds per step**, 21.9342% slower in this allocation.

| Full 150-step pair | First arm | First mean (s/step) | Second arm | Second mean (s/step) | First vs second |
|---|---|---:|---|---:|---:|
|2294234, `iris024`|zyx|21.229594|xyz|26.953799|zyx 21.2371% faster|
|2294262, `iris005`|xyz|21.823904|zyx|26.610796|xyz 21.9342% faster|

The **first arm was faster in both allocations**. For xyz, first on2294262 averaged **19.0322% less** than second on2294234; for zyx, second on2294262 averaged **25.3476% more** than first on2294234. Equal-weight cross-allocation means are 23.920195 seconds for zyx and24.388851 for xyz, a descriptive1.922% difference. This is only two allocations, with node and execution order changed together; it is not a causal estimate of either a hierarchy-order effect or a general position effect. The earlier21.2371% zyx speedup claim is not repeatable from these observations. The cause remains unknown.

No own NSCC performance gain is established by this Iris result. The direct next performance trial for the target **3.364622070 seconds per step on NSCC** is the prepared same-allocation native `Scotch / xyz / zyx` run, after admission becomes feasible.

## What was compared

Both allocations used one exclusive node,56 CPU ranks,zero GPUs, the same Xeon Platinum8280 model and the same hierarchy factors `(7 4 2)`. Each arm used the same FP64 source case, native OpenFOAM v2512 executable and library set, fixed iterations (`Ux/Uy/Uz=15`, `p=12`, `k/omega=8`) and150 solver steps. Each job changed only the order of the two hierarchical arms. Case validation permits only `controlDict:endTime` to be set to150.

Job2294262 completed `COMPLETED`, exit `0:0`, elapsed7,635 seconds on iris005. The frozen49-file runtime kit hashes match deployment; runtime executable and shared-library identity stayed stable. All10 recorded phase commands returned zero. Both arms have `End`,150 steps,149 positive native timer intervals,150 finite force-coefficient rows, expected iterations, source/copy checks, unchanged source trees and identical initialized/copy/post-solver field seals.

Root-side re-review independently replayed both raw native logs and found all149 timing values and all150 total-Cd rows per arm exactly equal to the saved comparison summary. The129-file transfer (125 main archive files plus four native function-object tables) passed per-file byte-count and SHA256 checks; no mesh or binary fields were transferred.

## Means, tails and outputs

| Order in job2294262 | Mean (s/step) | Median | P95 | P99 | Maximum (step) | 2%/95% sample recommendation |
|---|---:|---:|---:|---:|---:|---:|
|xyz, first|21.823904|21.380754|21.743313|30.538132|70.992053 (3)|361|
|zyx, second|26.610796|24.274069|35.163775|36.045696|70.257417 (48)|354|

All149 timed intervals remain in each mean, including the two approximately71-second outliers. The native within-run sample-count recommendation exceeds149 for both arms. Per-step samples are correlated, so they are not independent allocation repetitions or a confidence interval for a stable order effect.

In both allocations, each hierarchy order's complete150-row total-Cd trajectory exactly matches that same order in the other allocation. Across orders, the final values remain `xyz=0.287070094` and `zyx=0.282423983`; the final difference is1.6185% relative to xyz. The maximum absolute per-step cross-order difference is0.04104031. This is a descriptive output difference. It does not prove full-field equivalence or impose a new task tolerance.

## Resource and observability review

GNU `time` around each `mpirun` reported:

| Job/order | Solver wall | User CPU | System CPU | CPU use | Max RSS | Major page faults | Swaps |
|---|---:|---:|---:|---:|---:|---:|---:|
|2294234 zyx|3,223.76s|177,231.22s|1,958.68s|5,558%|2,964,632KB|113,325|0|
|2294234 xyz|4,075.94s|223,562.59s|3,185.50s|5,563%|3,009,304KB|85,987|0|
|2294262 xyz|3,311.54s|181,437.16s|2,550.52s|5,556%|2,880,748KB|179,751|0|
|2294262 zyx|4,037.61s|221,934.20s|2,571.00s|5,560%|3,017,996KB|267,424|0|

Max RSS and page-fault counts belong to the command-level `mpirun` process tree; they are not per-rank profiles. Before/after whole-node `/proc` counters were recorded. Before xyz: MemFree158.5GB, MemAvailable180.6GB, Cached28.0GB; before zyx: MemFree138.4GB, MemAvailable179.5GB, Cached46.8GB. Swap is absent/zero on this node. The two before-snapshots show substantial available memory; they do not support a memory-exhaustion claim. Whole-node `pgmajfault` advanced by about5.2k over xyz and7.4k over zyx; file refault counter ended at190 for the second arm versus0 before the first. These aggregate counters do not identify which process or MPI rank caused the events. Memory bandwidth counters, per-process NUMA maps and per-rank frequency traces were not collected.

The saved CPU inventory for both nodes reports Intel Xeon Platinum8280,56 physical cores,2 sockets,2 NUMA nodes and SMT off. Node0 contains even-numbered CPUs and node1 odd-numbered CPUs. It is not an affinity map: rank-specific placement was not sampled. Similar CPU models do not establish equal clocks or identical physical conditions. No evidence collected here selects memory interleave, core pinning or a particular MPI mapping as the cause; no such cause is claimed.

## Assessment and next decision

The crossed full runs reverse which decomposition is faster when its position changes. Both runs passed their numerical and execution gates, and the same order reproduces the same Cd rows, but the performance effect is not isolated from node and serial position. Treat the earlier Iris result as an allocation-specific observation. Do not use it as a robust Iris gain or predict an NSCC speedup.

Given the user's NSCC target, prioritize the actual NSCC-native first wave (`Scotch`, hierarchical `xyz`, hierarchical `zyx`) when VPN, current CPU and AI PBS queues, job provenance and current project credit all pass the admission gates. That trial directly measures the target platform. It needs no PMPI adapter. Until NSCC is accessible, no extra Iris placement trial is supported by this pair alone. Preserve both complete results and all outliers.

## Evidence

- `REVIEW.json`: structured full re-review and limitations.
- `collection.json`, `collected-addendum/collection.json`: scheduler records and transfer-file hashes.
- `raw-evidence.tar.gz`, `collected/`, and `collected-addendum/raw-evidence.tar.gz`:129 selected safe text/provenance/resource files and all four native timer/force tables; no mesh or binary fields.
- `../arm-status-20261028T0938.json`: interim completed-arm summary (superseded by this final review).
- `../submission-receipt.json`: actual job acceptance. The49 frozen runtime files remain unchanged.
