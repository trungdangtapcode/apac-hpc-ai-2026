# First 65M Iris baseline: decomposition passed

Job **2293752: COMPLETED / exit 0:0**, 161 seconds on iris031, one whole
56-CPU node, one serial task. All sealed evidence hashes pass. The native
v2512/scalar64 decomposePar log ends cleanly; exactly 56 processor directories
and 65,334,765 total cells are verified. All six expected initial fields are
present for every processor. fvSolution.fixedIter, controlDict.noWrite and
method coefficients match the frozen inputs; only the planned rank/factors
change. Both stage output markers and empty batch stderr pass.

Per-rank cells range 1,166,692–1,166,694; cell max/mean excess is 0.000151527%.
Worst partition has 93,343 interface faces and maximum neighbor count is 14.
The sum of per-rank interface faces, 2,653,432, counts both sides of 1,326,716
unique cuts. One node does not establish off-node traffic or communication cost.
The first parser rejected 57 face entries because it included the global summary;
review-cut.py now explicitly separates per-rank and global records and checks
their factor of two. That rejection was a review correction, not a failed job.

Scheduler batch MaxRSS is 32,011,392 KiB (30.5284 GiB); TotalCPU is 157.720 s.
These are available accounting measurements, not a memory-bandwidth, NUMA or
hardware-counter profile. Billed Iris SU remains unknown. No solver Average
(seconds/step), Cd or complete initialization is established yet.

Next run the already frozen 03.2-init script: one node, 56 ranks, maximum
20 minutes, all three mandatory stages. Review it before 40-step simpleFoam.
No national/GPU allocation or submission artifact is changed.

Reproduce the evidence review with python3 review-cut.py. The initial failed
pre-submit hash guard and binary-header inspection mistake are historical in
PLAN.md and the research journal; neither produced an extra job.

## Mandatory initialization submitted

2293753 accepted at 2026-10-21T12:02:36.204357+00:00; retained queue shows
RUNNING on iris031. One whole node, 56 MPI ranks, maximum 1200 seconds.
The frozen script and completed predecessor are checked before sbatch; the
shared-account queue was empty. Receipt and live job fields are retained in
init-submission.json. No simpleFoam job or extra national CPU/GPU reservation.
Review clean terminal status, renumberMesh, potentialFoam, applyBoundaryLayer
and READY identity before submitting the 40-step solver. No completed init
or new numerical/performance result is claimed at this checkpoint.

## Mandatory initialization reviewed

2293753 is COMPLETED / exit 0:0 in 103 seconds, one iris031 node/56 MPI ranks.
Sealed native logs show every required flag and clean End for renumberMesh,
potentialFoam and applyBoundaryLayer; wall clocks are 9/71/8 seconds. READY
and immutable dictionaries agree with the accepted N56 hierarchical (7 4 2)
split. Scheduler batch MaxRSS is 85.6927 GiB; TotalCPU is 01:29:32. No CPU
bandwidth/NUMA/network profile or billed SU is collected. Potential continuity
error is 0.00023976694199 and interpolated velocity error 0.00009469633924;
these are initialization diagnostics, not final simpleFoam convergence or Cd.
Default renumbering reduces printed matrix band 1,151,806 to 44,025, and
profile 1,297,348,083,601 to 755,856,599,687. This is the mandatory default
operation, not an invented optimization or measured solver speedup.

All complete-chain preparation gates now pass; promote to the unchanged
40-step solver payload. Reproduce the review with python3 review-init.py.
The long gap between jobs was time without an active Codex turn; no background
agent was enabled. No solver result yet at this review checkpoint.
