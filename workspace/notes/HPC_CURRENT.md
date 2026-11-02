# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 21:35:51 Vietnam**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex, schedules or automatic MFA loops. [Earlier detailed handoff](history/HPC_CURRENT-before-scotch-package-20261102.md) is historical.

## VPN request

Latest explicit retry: **2 November 22:28:26–22:28:30 Vietnam**, exactly one attempt returned gateway Authentication failed. **22:28:38** path check: NAMESPACE_UNAVAILABLE. No SSH authentication, DUO phone delivery/approval or exact cause established. No agent cache reset/deletion or automatic retry loop. [Safe record](nscc-vpn-retry-20261102.md#further-explicitly-requested-retry--2228-vietnam). This was VPN-only; no scheduler, budget or other-track state was changed. HPC snapshots below remain dated, not live.

## Reviewed xzy result and next actual job

**2294644 COMPLETED 0:0**, 6,261 seconds / 56 CPUs, all 222 transferred files and all four 52-step / 51-interval native/source/runtime gates pass. Xzy pooled **10.25252% slower**, adjacent +1.84160%/+19.78388%, control repeat -11.75533%. Candidate native sample recommendations 69/97 exceed 51. The earlier 40-step 0.71% signal is not reproduced. **Unchanged xzy branch closed**; no more horizon extensions to chase a favorable sign. [Full result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy52-reverse-20261102/completed-2294644/RESULTS.md). Collection initially failed in the delegated worker, but a bounded root retry succeeded; this was not authentication evidence.

**Last retained 2294657 snapshot: RUNNING** on iris001, 56 CPUs, elapsed 160 seconds at **21:35:51 Vietnam**. Full eight-member mesh check passed; native Scotch decomposition is in progress. Frozen 53-file root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch2x28-init-20261102T143218Z`. Working case comes from the retained 41-pin payload; accepted default boundary graph replays 1,035,208 total/86,913 logical cross-package faces and matches all 56 accepted boundary hashes.

New native Scotch `(2 28)` / synthetic weights `(1 0.1)` matches the observed two 28-rank packages. It changes partitions, unlike the closed graph rank-permutation trial; hardware costs are not measured. Cut then apply predeclared graph/balance filters; only a passing graph and full remaining time window permit all required initialization and field/manifest seals. Rejection yields explicit no READY/no initialization, not a valid solver result. **Preparation only**, no speedup claim. [Actual payload/receipt/status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch2x28-init-20261102/STATUS.md).

## Budget and next decision

Ledger **939 consumed + 28 reserved = 967 allocated CPU-hours**, existing agent-selected stage **1,009** unchanged. Previous 6,261-second allocation cost 97.393333 actual CPU-hours, conservatively 98; original 168 maximum retired once under lock. New max 30 minutes / 28 CPU-hours / zero GPU fits the existing stage. This is not billed Iris SU, an owner numeric site quota or an NSCC/AI transfer. One owned allocation is running; preserve it and its maximum. 25 accepted owned Iris IDs: 23 completed, one prior failed/censored, one running.

After terminal collection, inspect native graph gates/source/work, actual initialization/READY state, warnings/resources and missing telemetry; reconcile actual cost once. If promising and fully initialized, separately freeze a matched default-versus-tree solver trial within a reviewed bounded stage. If rejected, close unchanged hypothesis and choose the next distinct useful trial. No blind duplicates or unsupported success claims.

No Gadi identity/project supplied; NSCC access unverified after gateway failure. No own stable scored-platform gain is established. Best reviewed NSCC 3.364622070 s/step is an organizer-recipe reproduction; organizer 3.210832548 and teammate Gadi 2.079045460 are separate references. Iris seconds/percentages cannot forecast a Gadi win. AI payloads, queues, budget and submission materials remain unchanged. [Own research history](../reports/hpc-own-research-status-20261102/README.md).
