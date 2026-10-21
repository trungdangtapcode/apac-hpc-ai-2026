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
