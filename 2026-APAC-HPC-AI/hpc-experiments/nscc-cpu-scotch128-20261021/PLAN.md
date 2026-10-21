# Native Scotch N128 and a matched CPU method screen

## Question and prior evidence

Our accepted hierarchical (16 4 2) one-node baseline, job 25905114.pbs101, achieved 14.9219814004 s/step, Cd 0.4389323284, exit 0. Public one-node Scotch is 14.048605 versus hierarchical 14.668759 s/step, but those runs do not establish a matched gain. Public four-node results also warn that a one-node winner may lose at scale. Pinned reference analysis is in ../reference-analysis-20261021/RESULTS.md.

Hypothesis: native graph partitioning can improve this one-node fixed-work solve through a different partition/communication balance. More neighbors or cell imbalance can erase the benefit. Interface counts alone do not establish a causal bottleneck on one node.

## Exact preparation and control

Only decompositionMethod changes from hierarchical to native default Scotch; ranks remain 128. All physical inputs, double precision, fixedIter solvers, function objects and 40-step control match the accepted payload. The old split and runs are never modified. This new root creates a fresh split, restores all initial fields, verifies the complete official archive and each reused unpacked mesh member, and checks native End/DP/rank/cell counts. It also hashes initialized control zero-time fields on allocated compute CPUs for later read-only reuse. The existing control fields came from the accepted mandatory initialization; repeating that initialization in place would invalidate reuse provenance.

Preparation requests one CPU node, 32 CPUs / one serial process / 96 GB, no GPUs, maximum 15 minutes (8 SU). Native Scotch may require more memory or time than hierarchical; an unchanged OOM/timeout retry is not authorized. No solver score is claimed from preparation. Check partition balance, interface faces, neighbors and all logs after completion.

## Conditional same-node comparison

Only after reviewed preparation, derive a separate frozen pair payload: one exclusive node / 128 ranks, candidate mandatory initialization once, then fresh hierarchical and Scotch 40-step solves on the same node. Keep native runtime, rank policy and FI_VERBS_PREFER_XRC=0 identical. Probe placement with atomic per-rank records outside solver timing. Hash reused initial fields before/after each solve. Fresh run directories isolate logs, timers and function outputs. Order H then S is a first screen, not a repeated causal estimate; disclose order, cache and drift limitations. No four-node contest score is implied. Retain per-step distribution, Cd, all fixed iterations, errors, resources and missing telemetry.

The unchanged 100-SU wave ceiling now includes a conservative 29-SU consumed ceiling (all five completed allocations total 27.880 estimated SU; server amount delta 27.879). New preparation maximum 8 plus a conditional 29-minute pair maximum 61.866667 totals 98.866667 SU. Recheck accounting/own queue under the CPU budget lock before each submission. One CPU allocation active at a time, combined own PBS jobs at most three. No AI budget or job changes. Do not silently increase walltime, memory, core count, node count or the 100-SU planning ceiling.

The acceptance gate is successful native exit and exact numerical work/outputs, not merely job completion. Report actual results even if Scotch loses. Advance to scale only after evidence and a separately budgeted plan; a reverse-order repeat may need further authorization if it cannot fit the remaining first-wave allowance.
