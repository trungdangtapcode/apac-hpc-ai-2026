# Preparation policy changes the node-counter distribution

**Question.** Could preparation before a native solver run contribute to Iris timing variation? Failed solver screen 2294671 and earlier reversals did not establish a winner. CPU busy time and aggregate counters do not identify a causal bottleneck.

**Control and change.** Frozen job 2294675 compared inherited default policy against child-only interleaving during copying and hashing identical initialized Scotch input. Four fresh A/B/B/A directories, same 1,040 accepted input files plus 13 separately pinned metadata files, 56 CPUs and two memory nodes. Solver execution was deliberately outside this qualification.

**Observed result.** COMPLETED 0:0 in 216 seconds. All four policy/copy/source gates passed. Independent replay checked 10 artifacts, archive hash, 7 frozen hashes and source inventories. Inherited arms showed about 0 / 9.78 GiB of extra FilePages across nodes 0/1; interleaved arms about 4.89 / 4.89 GiB twice, with interleave_hit changes only under the treatment. Copy/hash durations were similar. [Full evidence and missing telemetry](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-numa-qualify-r2-20261103/completed-2294675/RESULTS.md).

**Interpretation.** Actual policy application and the consistent aggregate response qualify a useful controllable factor. FilePages counts the node's cached file pages, not the solver's private working arrays. The record does not locate each copied file, exclude all other node activity or show a solver gain. More balanced preparation might influence later cache reads, available local memory or allocation behavior; those remain hypotheses.

**Decision.** Prepare a separate native solver comparison with identical Scotch source/solver settings in every arm. Change only the preparation child's memory policy; record and preserve inherited solver policy. Keep 20 steps/19 intervals as a directional screen, equal monitoring and all native gates, with 1,000-second per-arm finalization-inclusive caps. If only preparation/startup changes while step time does not improve consistently, do not promote a solver-performance claim. Any favorable signal still requires longer controlled confirmation.

**Cost and admission.** Actual 3.36 allocated CPU-hours; conservative debit 4; old 9.333333 maximum retired once. Ledger 989 consumed, zero reserved under existing stage 1009. A proposed 75-minute native job needs a distinct bounded 70-hour reservation and an explicitly documented internal-stage adjustment; no submission is claimed in this entry. Billed SU remains unknown and no NSCC/AI credits are used.

**Comparison correction.** The owner specifically asked how Iris compares with teammate/BTC. [Pair-specific table](../../hpc-iris-comparison-20261103/README.md) shows teammate's qualified 11.2228% lower mean, our losing/reversed branches and the lack of a three-way ranking. The old 21.2296 observation is retained but cannot establish a cross-allocation win.

**Preservation.** Archive this complete mechanism review separately from the comparison report and next payload/receipt. Preserve failed 2294674 and all earlier native failures. No schedules or background Codex.
