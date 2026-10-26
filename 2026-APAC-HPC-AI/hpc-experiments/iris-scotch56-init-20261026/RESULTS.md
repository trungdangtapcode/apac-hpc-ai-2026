# Iris Scotch initialization completed

Job **2294046** completed 0:0 on iris009 in **100 seconds**. All three mandatory utilities pass the native OpenFOAM 2512, scalar64, 56-process, exact-command, End and no-fatal-error gates: renumberMesh, potentialFoam and applyBoundaryLayer. The startup probe contains exactly one observation for each of 56 ranks, all on the same node.

The collected 26 artifacts (300,267 bytes) match their transfer hashes and lengths. All 44 kit files and 41 original case input pins pass before and after. Both snapshots contain all 336 zero-time fields. Exactly 56 field files changed during mandatory initialization; changed initialized fields are expected and were not required to equal the uninitialized bytes. READY was created only after the native and source checks passed. Original group input and the frozen cut payload were preserved.

The estimated whole-node allocation is 1.555556 allocated CPU-hours. Its 18.666667-hour maximum is retired once and replaced by a rounded two-hour planning allowance. The branch now retains seven consumed planning CPU-hours for cut plus initialization, zero outstanding reservations before the next admission, and a 224-hour envelope. No Iris SU charge or rate is inferred; NSCC is separate.

Slurm reports batch MaxRSS 89,115,912 KiB. GNU time reports separate per-stage maxima of 1,139,364 / 2,059,196 / 1,228,564 KiB. These are different collectors and are not a common aggregate-memory measurement or memory-bandwidth diagnosis. Stage resources, the host CPU description and Open MPI binding output are retained. No hardware performance counters were collected.

This is still not a solver timing or Cd result. The next controlled test should run initialized hierarchical and Scotch cases on the same Iris allocation with 56 ranks, fixed iterations and 150 steps each. Preserve source artifacts, copy fields independently, retain all 149 timings per arm and report order effects. A lower interface-face count is a hypothesis, not the measured answer.

Replay with `python3 review-completed.py`. See completed-review.json, collected/ and completed-2294046.json.
