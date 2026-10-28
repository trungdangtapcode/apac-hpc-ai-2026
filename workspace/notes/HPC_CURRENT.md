# Current HPC/OpenFOAM handoff

Updated 2026-10-28T19:35:42.335823+00:00 / **02:35 on 29 October 2026 Vietnam (UTC+7)**. Fork 01a17c4b-65e6-75e0-be95-c5bea1b25502 continues HPC parent 01a1508d-26b0-7dd0-9dc1-f217ce0aff40. AI/Qwen remains separate. No background Codex, schedules or automatic chat notifications.

## Latest full Iris result

**2294262 completed 0:0 on iris005**, elapsed 7,635 seconds, 56 CPUs. Both 150-step arms and 149 timings / 150 Cd rows independently replay exactly; all 129 selected transfer hashes, source/copy/field seals, frozen runtime/library IDs and command exits pass. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-reverse-20261028/completed-2294262/RESULTS.md).

| Allocation | First arm (s/step) | Second arm (s/step) |
|---|---|---|
| 2294234, iris024| zyx 21.229594| xyz 26.953799|
| 2294262, iris005| xyz 21.823904| zyx 26.610796|

**The earlier 21.24% hierarchy advantage failed reverse-order confirmation.** In the new pair zyx is 21.9342% slower. First-arm performance was better in both allocations; cause is confounded with node/order/time. Same-order total Cd trajectories repeat exactly, but cross-order final Cd still differs 1.61846%. Never claim stable 21% tuning, NSCC improvement or numerical equivalence. New native sample recommendations 361 / 354 exceed 149; all samples remain included. No snapshots show memory exhaustion, but hardware bandwidth, frequency traces, post-MPI rank affinity and NUMA page residency were not measured. [Detailed new journal entry](../reports/research-journey-20261019/journal/entries/20261029-hpc-reversed-full-pair-result.md).

## Iris accounting and next action

Ledger `iris-scotch56-20261025/budget.json`, lock `budget.lock`: consumed 457, reserved 0, headroom 48 under unchanged 505 CPU-hour internal ceiling. 2294262 used 118.766667 CPU-hours; conservatively counted 119 and retired its 168 maximum once. No site SU rate/balance is known, and no NSCC/AI credits were moved. Fresh queue must be checked before any new submission; cap one own queued/running allocation, own prefix tu-. Shared rdmaworkshop30 jobs belong to other users; preserve them.

**2294358 completed 0:0 in 11 seconds on iris025.** It independently qualifies default and explicit fill as exactly the same 56 singleton post-MPI main-thread masks, with ranks 0–27/28–55 on the two NUMA domains. Span is a distinct even/odd ranking. Do not run default versus explicit fill as a solver comparison. All 188 retained file hashes and local validator replay pass. Actual 0.171111 CPU-hours is conservatively charged 1 and its 4.666667 maximum retired once. [Probe result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-mpi-affinity-20261029/RESULTS.md).

Read-only processor graphs preserve 56 boundary hashes/reciprocal edges and all 65,334,765 cells. Span worsens cross-NUMA logical face proxies: xyz 375788→996617; zyx 129700→260523. Close unchanged span rather than blindly spending solver time. A bounded offline balanced graph search is examining a distinct rank assignment; no solver trial is justified until it has a real proxy change and native mapping qualification. These proxies do not identify a measured bandwidth/NUMA cause. Independent NSCC native trials remain first when accessible.

## NSCC objective and blocker

Best own reviewed full NSCC measurement remains **3.364622070 s/step**, job 25940700, 4 nodes / 512 ranks / default Scotch / 150 steps. It reproduces the organizer recipe, not a new optimization. External organizer 3.210832548 is a separate observation. No new own configuration has demonstrated a matched improvement below 3.3646. Never compare Iris raw seconds as NSCC scores.

A fresh bounded retry at 19:03 UTC 28 October / 02:03 Vietnam 29 October returned Authentication failed. The latest transport check has no live namespace; no current NSCC queue/credit/new job is claimed. Captain holds DUO; do not repeatedly ask the owner about that phone. Correct health gate requires tunnel IPv4 plus reachable SSH service, then successful host-key-verified SSH; enter-true alone was a corrected false positive. Preserve private caches; no repeated indefinite MFA loop.

The native 61-file S0/Hxyz/Hzyx bundle remains ready but unsubmitted/unreserved. It requests 4 exclusive nodes, 512 ranks, 90 minutes, max 768 SU at the historically verified rate; fresh credit/rate/queues and commitments gate admission. It does not depend on PMPI diagnostics. Before qsub inspect CPU and AI queues under CPU-before-AI locks, own CPU cap 1, combined PBS cap 3 including holds. CPU project 59000042 is separate from AI 59010042. Old 26019383 and shared 26023372/373/382/383 still need safe terminal/provenance/resource review; preserve unknown reservations and do not cancel/duplicate them.

## Preservation and execution

Use [execution contract](research-execution-contract-20261027.md), [target criteria](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-transfer-campaign-20261027/TARGET_3_3646.md) and actual scheduler state. Capture, screen, verify, commit and push small explicit milestones. Large meshes/fields remain remote; selected raw evidence is retained. No submission material or AI payload was changed. [Previous full handoff](history/HPC_CURRENT-before-reverse-review-20261029.md).

## Actual bounded qualification submission — 29 October, 02:41 Vietnam

Slurm accepted **2294358** at 02:41:16 Vietnam, five-minute / 56 CPU / zero GPU maximum. A 4.666667 CPU-hour reservation is recorded under the existing 505 ceiling; consumed 456 plus reserved 4.666667 leaves 44.333333 headroom. The frozen five-file source observes pre/post-MPI_Init main-thread masks for default, explicit core fill and core span ranking. No solver runs here and no performance result is implied. [Receipt and status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-mpi-affinity-20261029/STATUS.md). Query actual state and collect text evidence before deciding whether any distinct solver placement test is supported. NSCC access remains blocked; preserve its independent native trial readiness.
