# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 07:16 Vietnam** (00:16 UTC). HPC fork 01a17c4b-65e6-75e0-be95-c5bea1b25502; AI separate. No background Codex or schedules.

## Actual accepted work

| Job | Observed state | What it measures |
|---|---|---|
| **2294637** | RUNNING on iris001, elapsed 1:04:47 | Organizer vs teammate runtime, four 40-step arms |
| **2294640** | PENDING / Dependency, AllocCPUS 0 | Our hierarchical zyx vs default Scotch, four 40-step arms |

New 2294640 receipt **00:15:46.990918 UTC / 07:15:46 Vietnam**, dependency **afterany:2294637(unfulfilled)** verified at 07:16:45. No second allocation. Slurm will schedule the queued job after predecessor termination. Preserve both jobs and full maxima; no arbitrary additional own wave.

2294637 now has **3/4 completed arms**: organizer A1 **25.581958377**, teammate B1 **22.396949743**, teammate B2 **27.093606214 s/step**. Last organizer A2 at **15/40**. This is runtime-reviewed partial data, not terminal independent replay or a recipe winner. The same candidate's repeated means differ materially; A2 and full raw review remain required. [Direct-comparison kit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-recipes40-20261101/STATUS.md).

## Our own candidate and honest attribution

**No own stable scored-platform improvement has been demonstrated.** Best reviewed NSCC **3.364622070s/step**,25940700,4nodes/512ranks/150steps/default Scotch, is an organizer-recipe reproduction. Organizer NSCC 3.210832548 remains external. Teammate Gadi 2.079045460 and collated/socket recipe belong to the supplied package, not our invented optimization.

Our distinct pending comparison 2294640 uses **default Scotch / standard hierarchical (7 4 2), order zyx / same / Scotch**, same 56 ranks, original 65M mesh/physics/build/fixed work, 40 steps / 39 timings per arm, common default MPI/uncollated and launcher diagnostics. Initialization and accepted processor meshes/fields differ by decomposition as intended; do not describe them as identical. Our contribution is tested parameter selection and validation, not inventing hierarchical. The older Hxyz/Scotch full 150-step pair timed out during Scotch step 143; later full 150-step zyx/xyz runs compare orders only and their apparent gain failed reversal. A complete method ABBA remains a distinct missing measurement. [Actual own-candidate receipt, sources and status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx40-20261102/STATUS.md).

New root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-own-zyx40-20261102T001225Z`, evidence root/kit/runs/2294640. Frozen 58 files. Control source is ready-N56-scotch; candidate is **initialized/order-zyx**, accepted by the reviewed 1040-file graph/full-work source record. Never substitute the old original Hxyz path from inherited source-observations.json; only its S entry is consumed. Candidate uses case_checks.source_check(...,'zyx') and its own accepted-zyx-source-manifest. Both canonical 41-pin preflights passed live; heavy source/copy/field hashes are inside compute. README and SOURCE_PROVENANCE explain the separate sources.

## Other branch outcomes

- Own NSCC NUMA-tree Scotch native pair 25907753: candidate 3.4416% slower despite lower face proxy; scheduler history/billing unknown, old maximum retained. Not a four-node improvement.
- Own hierarchy-order apparent gain flipped under full reversal; no stable order claim.
- Own graph placement 2294366/2294390: reverse does not confirm favorable aggregate; closed.
- Supplied collated I/O 2294634/2294635: -6.0726% then +9.3497%; pooled +0.159963% is descriptive, not causal. All Cd rows equal; no reproduced gain.
- Standalone exact socket-map proposal closed unsubmitted because first A1/B1 launcher rank/package/core maps are identical. This is not proof of all worker behavior or Gadi equivalence.

Keep failures and provenance; do not relabel reference configs, borrowed flags or diagnostic qualifications as our validated optimization.

## Cost and next action

Ledger **593 consumed + 280 reserved = 873 CPU-hours**, internal stage 873; current and successor each reserve 140. The owner continues active research and now asks specifically about own configurations. This single bounded native 40-step ABBA adds 103 to the previous agent-selected 770 envelope, not an owner numerical/site grant. No NSCC/AI debit or site SU balance claim. New admission allows only exact 2294637 predecessor plus one afterany successor under the existing lock; one active own CPU allocation stays the policy. No further own jobs until these are reviewed; preserve queue position. [Authority](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx40-20261102/budget-authorisation.json).

Let 2294637 finish A2, collect once/replay all four raw outputs/Cd/source/runtime/maps/trends/warnings/telemetry and reconcile the 140-hour maximum once. Then preserve active/pending 2294640, which applies its own input gates regardless of predecessor outcome. On its completion, run its two-source collector/reviewer, compare both adjacent directions and repeat controls, Cd/sanity by method and all limitations, then reconcile its 140-hour maximum once. A successful Iris 40-step screen is not an NSCC/Gadi four-node 150-step score. Do not pool raw cross-allocation seconds as a direct three-way ranking.

NSCC last read-only transport unavailable, no new authentication or credit/queue proof; no Gadi identity supplied. National native trials remain conditional on authorized access and fresh financial/shared queue checks. Submission folders/slide bytes and AI work unchanged. Safe snapshots/commits/pushes are explicit; external binary objects still need independent off-host copy.

[Own research answer](../reports/hpc-own-research-status-20261102/README.md); [new journal](../reports/research-journey-20261019/journal/entries/20261102-hpc-own-candidate-matched-method-test-submitted.md); [historical handoff](history/HPC_CURRENT-before-own-candidate-20261102.md).

## Gadi transfer question — 2 November

The owner asked whether moving to Gadi could improve results. Lower absolute seconds than the NSCC 3.3646 baseline is plausible because official Gadi Scotch references are already around 2.088–2.126 s/step, but this is a baseline target/inference, not a measured forecast of our candidate. The published Gadi hierarchy reference is about 2.380 s/step, so our zyx candidate has no established transfer advantage or demonstrated ability to beat teammate 2.079. Normalize rank/factors and compare against Gadi's own matched controls; a platform switch alone does not establish an optimization or higher score. No Gadi identity/project budget was supplied and no job was submitted. [Source-linked outlook](gadi-transfer-outlook-20261102.md). Existing Iris jobs remain untouched.
