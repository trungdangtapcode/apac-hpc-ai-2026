# First full one-node ASPIRE-2A CPU baseline

Prior 25905006 passes full archive/member identity and fresh official N128
hierarchical (16 4 2) cut/restore in 187 seconds. The native timing diagnostic
passes. The next question is full mandatory initialization and 40-step native
execution on the actual CPU contest platform, not speedup over Iris.

Use unmodified site v2512, double precision, exact official fixedIter, schemes,
physics and all function objects. Verify every prepared case file hash and
CUT_READY before mutation. No decomposition is repeated. Run renumberMesh,
potentialFoam -initialiseUBCs and applyBoundaryLayer -ybl 0.0450244, then fresh
40-step simpleFoam. Reject nonzero native returns, absent End/build/rank checks,
wrong step/output counts or fatal logs. Retain all slow steps and warnings.

One exclusive standard CPU node, 128 CPUs/128 MPI/440 GB/no GPUs, maximum
35 minutes; maximum 74.666667 SU. Parent CPU ledger retains 18.666667 SU for
all preceding maxima; total 93.333334 remains below the first-wave 100-SU cap.
Reserve under its CPU lock after actual project/own-queue and combined PBS
capacity checks. No AI ledger, payload, job or H100 allocation is changed.
The actual job can finish sooner; queue waiting is separate from execution.

Collect rank CPU/NUMA-mask placement, phase clocks, native stage logs, time -v,
PBS accounting, full per-step time distribution, solver iterations and Cd.
These are not bandwidth/cache/hardware-counter measurements; label missing
telemetry. The documented FI_VERBS_PREFER_XRC=0 choice stays fixed from the
native gate, not a claimed optimization. No heavy profiling inside scoring.

On success review the exact one-node baseline before planning a matched
Scotch or topology comparison; four-node/150-step scored work comes later.
No automatic retry or background Codex; preserve frozen failed payloads.
