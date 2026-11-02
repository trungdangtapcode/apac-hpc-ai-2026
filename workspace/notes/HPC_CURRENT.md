# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 07:35 Vietnam** (00:35 UTC). HPC fork 01a17c4b-65e6-75e0-be95-c5bea1b25502; AI separate. No background Codex or schedules.

## Actual accepted work

**2 November 2026, 10:30:45 Vietnam**: 2294640 COMPLETED 0:0, iris001, 5,050s /56 CPUs. All four native arms and 222 transfer-file hashes replay correctly. Scotch A1/A2 **22.358237138 /31.443932712 s/step**; zyx B1/B2 **27.821793339 /31.476255063**. Zyx pooled **10.21498% slower**, adjacent **+24.43644%/+0.10279%**, control repeat drift **+40.63690%**. No favorable stable method signal. Both same-method Cd repeats match; all reported launcher maps match. Last control sample recommendation 69 exceeds 39 intervals. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx 40-20261102/completed-2294640/RESULTS.md).

Conditional teammate-runtime transfer proposal is **CLOSED UNSUBMITTED/UNRESERVED** because its parent gate failed. Existing old accepted jobs are terminal; refresh the full own queue before the next admission. At this review no successor is claimed. Next distinct trial selection is in progress; do not leave this closed branch as a global stop. Earlier partial/live statements below are historical.

## Our own candidate and honest attribution

**No own stable scored-platform improvement has been demonstrated.** Best reviewed NSCC **3.364622070s/step**,25940700,4nodes/512ranks/150steps/default Scotch, is an organizer-recipe reproduction. Organizer NSCC 3.210832548 remains external. Teammate Gadi 2.079045460 and collated/socket recipe belong to the supplied package, not our invented optimization.

Our now completed comparison 2294640 used **default Scotch / standard hierarchical (7 4 2), order zyx / same / Scotch**, same 56 ranks, original 65M mesh/physics/build/fixed work, 40 steps / 39 timings per arm, common default MPI/uncollated and launcher diagnostics. Initialization and accepted processor meshes/fields differ by decomposition as intended; do not describe them as identical. Our contribution is tested parameter selection and validation, not inventing hierarchical. The older Hxyz/Scotch full 150-step pair timed out during Scotch step 143; later full 150-step zyx/xyz runs compare orders only and their apparent gain failed reversal. A complete method ABBA remains a distinct missing measurement. [Actual own-candidate receipt, sources and status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx 40-20261102/STATUS.md).

New root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-own-zyx 40-20261102T001225Z`, evidence root/kit/runs/2294640. Frozen 58 files. Control source is ready-N56-scotch; candidate is **initialized/order-zyx**, accepted by the reviewed 1040-file graph/full-work source record. Never substitute the old original Hxyz path from inherited source-observations.json; only its S entry is consumed. Candidate uses case_checks.source_check(...,'zyx') and its own accepted-zyx-source-manifest. Both canonical 41-pin preflights passed live; heavy source/copy/field hashes are inside compute. README and SOURCE_PROVENANCE explain the separate sources.

## Other branch outcomes

- Own NSCC NUMA-tree Scotch native pair 25907753: candidate 3.4416% slower despite lower face proxy; scheduler history/billing unknown, old maximum retained. Not a four-node improvement.
- Own hierarchy-order apparent gain flipped under full reversal; no stable order claim.
- Own graph placement 2294366/2294390: reverse does not confirm favorable aggregate; closed.
- Supplied collated I/O 2294634/2294635: -6.0726% then +9.3497%; pooled +0.159963% is descriptive, not causal. All Cd rows equal; no reproduced gain.
- Standalone exact socket-map proposal closed unsubmitted because first A1/B1 launcher rank/package/core maps are identical. This is not proof of all worker behavior or Gadi equivalence.

Keep failures and provenance; do not relabel reference configs, borrowed flags or diagnostic qualifications as our validated optimization.

## Cost and next action

Ledger **745 consumed + 0 reserved = 745 CPU-hours**, internal stage 873, remaining 128. Completed 2294637 used 72.628889 actual allocated CPU-hours, conservatively 73; its original 140 maximum was retired once under lock. Completed 2294640 used 78.555556 allocated CPU-hours, conservatively 79; its 140 maximum is retired once. The owner continues active research and now asks specifically about own configurations. This single bounded native 40-step ABBA adds 103 to the previous agent-selected 770 envelope, not an owner numerical/site grant. No NSCC/AI debit or site SU balance claim. New admission allows only exact 2294637 predecessor plus one afterany successor under the existing lock; one active own CPU allocation stays the policy. No further own jobs until these are reviewed; preserve queue position. [Authority](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx 40-20261102/budget-authorisation.json).

2294637 is now collected, independently replayed, inspected and reconciled; earlier partial statuses are historical. Preserve running 2294640. On its completion, run its two-source collector/reviewer, compare both adjacent directions and repeat controls, Cd/sanity by method and all limitations, then reconcile its 140-hour maximum once. A successful Iris 40-step screen is not an NSCC/Gadi four-node 150-step score. Do not pool raw cross-allocation seconds as a direct three-way ranking. No new admission while the owned method trial runs; review it before selecting a distinct next test.

NSCC last read-only transport unavailable, no new authentication or credit/queue proof; no Gadi identity supplied. National native trials remain conditional on authorized access and fresh financial/shared queue checks. Submission folders/slide bytes and AI work unchanged. Safe snapshots/commits/pushes are explicit; external binary objects still need independent off-host copy.

[Own research answer](../reports/hpc-own-research-status-20261102/README.md); [new journal](../reports/research-journey-20261019/journal/entries/20261102-hpc-own-candidate-matched-method-test-submitted.md); [historical handoff](history/HPC_CURRENT-before-own-candidate-20261102.md).

## Gadi transfer question — 2 November

The owner asked whether moving to Gadi could improve results. Lower absolute seconds than the NSCC 3.3646 baseline is plausible because official Gadi Scotch references are already around 2.088–2.126 s/step, but this is a baseline target/inference, not a measured forecast of our candidate. The published Gadi hierarchy reference is about 2.380 s/step, so our zyx candidate has no established transfer advantage or demonstrated ability to beat teammate 2.079. Normalize rank/factors and compare against Gadi's own matched controls; a platform switch alone does not establish an optimization or higher score. No Gadi identity/project budget was supplied and no job was submitted. [Source-linked outlook](gadi-transfer-outlook-20261102.md). Existing Iris jobs remain untouched.


## Does Iris beat teammate and organizer?

Iris is the test platform, not a third configuration. Our own hierarchical candidate has no measured result yet. The completed same-Iris comparison currently favors the supplied teammate runtime over organizer by about 11.2% in this short allocation, with the drift/sampling limitations above. This does not show that our candidate beats either recipe, or that Iris beats Gadi/NSCC hardware.


## Audited number of Iris jobs

At **2 November 07:38:24 Vietnam**, 21 distinct accepted job IDs from this worker's retained Iris receipts all match fresh sacct: **19 COMPLETED 0:0, one FAILED 124:0, one RUNNING**. Purpose: 13 full-size solver benchmark jobs (11 completed, one censored failure, one running), six decomposition/initialization, two toy/MPI diagnostic. Multiple arms may share an allocation; jobs are not distinct configurations or proven gains. Other workers and test-only IDs excluded. [Receipt-bound count and retrospective assessment](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-job-count-audit-20261102/README.md). Earlier “no result yet” statements refer to the new own-method comparison, not an absence of historical runs.


## Sub-22 Iris results exist

Historical completed full-size runs include 2294234/zyx **21.229593669 s/step** and 2294262/xyz **21.823903674** (both 150/149), plus 2294635/Scotch uncollated **21.431810307** and 2293754/hierarchical **21.965353836** (40/39). No stable speedup is different from no sub-22 result: zyx reversed to 26.6108, and cross-allocation seconds are not a matched win. [Values and provenance](../reports/hpc-own-research-status-20261102/README.md#did-any-iris-run-finish-below-22-seconds-per-step).


## Continuing improvement — 2 November 07:47 Vietnam

Actual 2294640 remains RUNNING on iris001, elapsed 17:21, first Scotch arm at native step 40 with no End marker/final arm result yet. Preserved maximum and queue. Prepared a conditional **zyx versus Scotch under the common teammate socket/core + collated runtime**, BAAB order, same two accepted sources and fixed work. Syntax, exact commands, label-based ratio fixture, source lineage and bounded read-only peer review pass. Tail/Cd diagnostic summaries added. This is **PREPARED ONLY**, not deployed/submitted/reserved; maximum if later admitted is 140 CPU-hours. Current parent must first pass complete stable review; otherwise do not spend on this transfer hypothesis. Existing own allocation and missing parent eligibility prevent another ready admission now. NSCC read-only transport at 07:46:38 returned NAMESPACE_UNAVAILABLE; no auth attempt. No Gadi credentials or numeric forecast; sub-22 Iris is motivation for a controlled test, not evidence of beating teammate Gadi 2.079. [Payload](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-zyx-teammate-runtime40-20261102/README.md); [reasoning](../reports/research-journey-20261019/journal/entries/20261102-hpc-conditional-teammate-runtime-transfer-prepared.md).
