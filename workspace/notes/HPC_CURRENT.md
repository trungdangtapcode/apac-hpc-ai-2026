# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 06:38 Vietnam** from actual scheduler observations at 06:31:42 and live launcher prefix at 06:34:43. HPC fork 01a17c4b-65e6-75e0-be95-c5bea1b25502; AI is separate. No background Codex or schedules.

## Active comparison

**2294637 RUNNING on iris001**, one exclusive node, 56 ranks, zero GPUs, max 2.5 hours. Owner-requested same-Iris comparison: **organizer / teammate / teammate / organizer**, each 40 steps / 39 timings on identical accepted initialized Scotch source and v2512 DP runtime. A is default MPI/uncollated; B is socket/core flags/collated. Shared initialization controls inputs rather than repeating teammate prep placement.

A1 organizer completed 40 steps at runtime-reviewed **25.581958377 s/step**. At06:34:43 B1 teammate is at step 5/40; B2/A2 are pending inside the same allocation. No final winner or independently terminal four-arm result. [Live status/source kit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-recipes40-20261101/STATUS.md). Remote root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-recipes40-20261101T230311Z`, evidence root/kit/runs/2294637. Preserve frozen 57 files and full 140-hour reservation.

Actual A1/B1 launcher reports show **identical rank/package/logical-core maps for all 56 ranks**; I/O headers differ as intended. This does not establish actual solver helper-thread affinity, page locality or Gadi behavior. The separate mapping-only ABBA proposal is now **closed unsubmitted/unreserved** due to no observed distinct placement; do not waste an allocation repeating it unchanged. [Map evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-recipes40-20261101/launcher-map-review.json). Review later arms too before generalizing.

## New completed reversal: no confirmed I/O gain

**2294635 COMPLETED 0:0**, iris001, 2,069 seconds. All 116 hashes and independent native 40-step replays pass. Collated-first **23.435621344 s/step**, default-second **21.431810307 s/step**: collated **9.3497% slower**, reversing parent 2294634's 6.0726% favorable result. Later arm wins in both orders. Pooling two allocations gives collated 0.159963% higher mean, not a causal result. **Close isolated-I/O speedup claim.** All four 40-row Cd trajectories are exactly equal; source/copy/field/runtime integrity passes. [Complete review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-reverse-20261101/completed-2294635/RESULTS.md).

Inspection covers timing trends/tails, native sample recommendations, resources, stderr and endpoint CPUinfo snapshots. Collated reports higher command maximum RSS in both allocations, not summed node memory. Endpoint MHz values are outside measured solver intervals and cannot establish sustained frequency or explain drift. Hardware cycles/bandwidth, actual solver helper-affinity and NUMA page residency were not collected. No native fatal marker or scheduler stderr observed.

## Accounting and access

2294635 actual 32.184444 CPU-hours conservatively counted 33, original 70-hour maximum retired once. Ledger **593 consumed + 140 reserved = 733 CPU-hours**, internal stage 770, headroom 37. Only current 2294637 remains unretired; do not retire its 140-hour maximum while running. No site SU rate/balance known; Iris is separate from NSCC/AI.

The afterany:2294635 dependency actually cleared and launched 2294637 automatically after predecessor completion. One active own CPU allocation remains the policy. A narrow dependent successor was allowed by the authoritative active-allocation policy, correcting older helpers' blanket queued-entry rejection; no arbitrary queue wave or new concurrent allocation is authorized. No further distinct ready trial is justified while current four-arm result is incomplete; do not queue the closed mapping duplicate.

NSCC read-only transport at 06:31:35 Vietnam still showed namespace unavailable; no authentication retriggered. NSCC queue/credit/old commitments unknown, no Gadi identity supplied. No new national-supercomputer deployment or debit. Best reviewed NSCC remains baseline reproduction **3.364622070 s/step**, job 25940700; organizer NSCC 3.210832548 separate. Teammate Gadi 2.079045460 remains supplied evidence, not our rerun or a cross-platform gain. Other-track payloads and submission materials remain unchanged.

## Next action

Let 2294637 finish all four independent native arms; collect once and replay with its collector/reviewer, inspect map reports for all arms, work/Cd/source/runtime invariants, raw trends/tails, adjacent effects, control repeat and available telemetry, then reconcile maximum 140-hour reservation once. A one-arm lead or pooled favorable mean alone cannot establish a winner. Select new distinct hypotheses from complete evidence and accessible authorized clusters, preserving budgets/caps and queue positions. [Current journal](../reports/research-journey-20261019/journal/entries/20261101-hpc-io-reversal-no-gain-and-direct-comparison-running.md); [historical handoff](history/HPC_CURRENT-before-reverse-io-review-20261101.md).
