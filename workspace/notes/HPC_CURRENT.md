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

Ledger `iris-scotch56-20261025/budget.json`, lock `budget.lock`: consumed 456, reserved 0, headroom 49 under unchanged 505 CPU-hour internal ceiling. 2294262 used 118.766667 CPU-hours; conservatively counted 119 and retired its 168 maximum once. No site SU rate/balance is known, and no NSCC/AI credits were moved. Fresh queue must be checked before any new submission; cap one own queued/running allocation, own prefix tu-. Shared rdmaworkshop30 jobs belong to other users; preserve them.

Prepare a bounded five-minute / 56 CPU native MPI mask qualification, max 4.666667 CPU-hours, within that 49-hour headroom. Default, explicit core binding and fill/span rank order are tested before and after MPI_Init. It collects a missing mechanism, not a solver performance result or an inferred NUMA fix. Do not deploy or call it submitted without sealed review, fresh queue, reservation and definite job ID. Only a qualified distinct mapping can motivate a later short balanced performance screen. The independent NSCC native trial remains higher priority when accessible.

## NSCC objective and blocker

Best own reviewed full NSCC measurement remains **3.364622070 s/step**, job 25940700, 4 nodes / 512 ranks / default Scotch / 150 steps. It reproduces the organizer recipe, not a new optimization. External organizer 3.210832548 is a separate observation. No new own configuration has demonstrated a matched improvement below 3.3646. Never compare Iris raw seconds as NSCC scores.

A fresh bounded retry at 19:03 UTC 28 October / 02:03 Vietnam 29 October returned Authentication failed. The latest transport check has no live namespace; no current NSCC queue/credit/new job is claimed. Captain holds DUO; do not repeatedly ask the owner about that phone. Correct health gate requires tunnel IPv4 plus reachable SSH service, then successful host-key-verified SSH; enter-true alone was a corrected false positive. Preserve private caches; no repeated indefinite MFA loop.

The native 61-file S0/Hxyz/Hzyx bundle remains ready but unsubmitted/unreserved. It requests 4 exclusive nodes, 512 ranks, 90 minutes, max 768 SU at the historically verified rate; fresh credit/rate/queues and commitments gate admission. It does not depend on PMPI diagnostics. Before qsub inspect CPU and AI queues under CPU-before-AI locks, own CPU cap 1, combined PBS cap 3 including holds. CPU project 59000042 is separate from AI 59010042. Old 26019383 and shared 26023372/373/382/383 still need safe terminal/provenance/resource review; preserve unknown reservations and do not cancel/duplicate them.

## Preservation and execution

Use [execution contract](research-execution-contract-20261027.md), [target criteria](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-transfer-campaign-20261027/TARGET_3_3646.md) and actual scheduler state. Capture, screen, verify, commit and push small explicit milestones. Large meshes/fields remain remote; selected raw evidence is retained. No submission material or AI payload was changed. [Previous full handoff](history/HPC_CURRENT-before-reverse-review-20261029.md).
