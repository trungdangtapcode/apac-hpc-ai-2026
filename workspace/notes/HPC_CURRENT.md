# Current HPC/OpenFOAM handoff

Updated **03 November 2026, 14:00:24 Vietnam (UTC+7)**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex, schedules or automatic MFA loops.

## Live checkpoint — 4 November 2026, 20:37 Vietnam

2294735 is RUNNING on iris001, elapsed 1:02:04. Three 40-step arms have returned 0: B1 interleaved 21.842916421 s/step, A1 inherited 29.418802008, A2 inherited 33.586912671. B2 is created but no completed log/return is present. These are live, unreviewed printed means, not a complete comparison or a new best. Strong control drift reinforces the need for the final arm and full review. No extra job is admitted while this one-owned-allocation cap is occupied. The existing two-hour limit and 112 CPU-hour maximum remain unchanged.

The GitHub Pages update completed successfully; the live shared page returned HTTP 200 and its HPC investigation contains actual job 2294735. [Hosted page](https://trungdangtapcode.github.io/apac-hpc-ai-2026/#hpc).

## Actual reversed confirmation submitted — 4 November 2026

**Iris job 2294735 accepted**, one node /56 CPUs /zero GPUs /maximum 2 hours, 112 allocated CPU-hours reserved. Four 40-step BAAB arms reverse the earlier 20-step ABBA experiment while preserving the same accepted Scotch source, solver and child-only preparation policy. [Frozen bundle, receipt and dated state](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-reverse40-20261104/STATUS.md). No completed new mean yet. Internal planning ledger is 1,024 consumed +112 reserved = 1,136; previous 1,059 stage extended by 77 for this one bounded confirmation. This is not billed SU or a new owner-set budget. Preserve the one-own-allocation cap and queue position.

## Hosted diagram delivery — 4 November 2026

The owner clarified that diagram updates belong directly in the existing shared [GitHub Pages atlas](https://trungdangtapcode.github.io/apac-hpc-ai-2026/#hpc), with AI and HPC on the same page. HPC-only builds preserve the existing AI component. The latest update replaces the stale unreviewed native milestone with the qualified 1.76868% signal and source-linked completed review. [Build, browser and deployment verification](../reports/hpc-atlas-update-20261104/README.md). No new performance run was submitted during this publication.

## New reviewed native result — 4 November 2026

Iris **2294676 COMPLETED 0:0**, 2,200 seconds /56 CPUs. Preparation-child interleave yields **21.771496718 versus 22.163497501 s/step**, **1.76868% lower pooled time**, in four 20-step arms. Adjacent pairs disagree (+0.73172% /−4.20539%); this is a short directional signal, not a stable own win. All four independent native replays and identical force trajectories pass. [Full review and diagnostic limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-native20-20261103/completed-2294676/RESULTS.md).

Fresh Iris queue at **4 November 18:39:25 Vietnam** is empty. Next hypothesis is reversed-order, longer-horizon confirmation of the same preparation factor. It is proposed, not submitted; a new sealed/admitted bundle is required. Actual cost 34.2222 allocated CPU-hours, conservatively 35, reservation retired once: 1,024 consumed /0 reserved /1,059 internal stage. Not billed SU. The earlier running snapshots and unreviewed diagram node are historical and superseded by this result.

## HPC research diagram — 4 November 2026

The owner requested an HPC counterpart to the AI README map. [The 15-milestone visual journey](../reports/hpc-run-lineage-20261104/README.md) distinguishes NSCC/Iris, observations versus matched evidence, rejected branches and preparation qualification. It uses retained reviews through 3 November and makes no fresh scheduler claim. No job, budget or authentication was changed.

## HPC presentation publication — 3 November 2026, 16:44 Vietnam

The owner requested only the HPC section. The canonical team PPTX and ZIP now contain the reviewed Iris comparison and 14-versus-40-step explanation in the existing eight HPC positions (35–42). All 34 AI slide dependency bytes, AI note bodies and AI PDF pages were preserved. NSCC job 25940700 is correctly described as a completed organizer-recipe reproduction at 3.364622070 s/step; the obsolete pending-slide claim is superseded. Job scripts and measurements in both tracks are unchanged. [Current slides, PDFs, notes and checks](../submission-review/hpc-iris-slides-20261103/README.md).

This publication performed no scheduler query, submission or VPN action. Job 2294676's earlier scheduler state below remains a dated snapshot, not a live status. The native experiment is excluded from the slide results until reviewed.

## Answer to the Iris comparison question

The supplied teammate runtime recipe has a **qualified 11.2228% lower mean** than organizer/BTC in the complete 40-step Iris comparison 2294637. Our `zyx` loses 10.2150% to its own matched Scotch control; the small `xzy` gain reverses to 10.2525% slower in confirmation. Latest `xyz` 2294671 is incomplete and cannot establish a gain. No matched three-way test proves we beat the teammate. [Readable comparison, exact values and provenance](../reports/hpc-iris-comparison-20261103/README.md).

Our old **21.229593669 s/step** is a real completed Iris observation, not a stable matched win over teammate/BTC. Never compare it against another allocation's slower raw time to claim first place.

## Exact lowest-observation clarification

Lowest reviewed whole-arm means on Iris: **ours 21.051168942 s/step (2294390, 14 steps)**; **organizer 22.358237138 (2294640, 40 steps)**; **teammate 22.396949743 (2294637, 40 steps)**. Separate allocations/horizons are not a matched ranking. Our 50-step zyx value is 21.112004724, and 150-step value is 21.229593669. Calling the latter the absolute minimum across all horizons was too broad. [Exact values, attribution and source hashes](../reports/hpc-iris-comparison-20261103/BEST_RECORDED.md).

At **3 November 2026 14:29:10 Vietnam**, job 2294676 is RUNNING on iris001, elapsed 32:08. Its live unreviewed output is excluded from the minima. Preserve its position and existing maximum reservation; no new admission during this clarification.

## Reviewed preparation mechanism

**2294675 COMPLETED 0:0**, 216 seconds / 56 CPUs on iris001. Terminal state collected **13:42:51 Vietnam**, compact evidence collected later this turn. All four fresh A/B/B/A preparations, actual policies, input/copy/source-after gates, 10 collected artifact hashes and 7 frozen hashes replay. Source is 1,040 accepted regular files plus 13 pinned metadata files and the approved mesh symlink. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-numa-qualify-r2-20261103/completed-2294675/RESULTS.md).

Inherited policy twice gave approximately 0 / 9.78 GiB of additional node-wide FilePages; interleaved child policy twice gave 4.89 / 4.89 GiB across the two NUMA nodes. This qualifies the policy mechanism and consistent aggregate response. It does not attribute individual pages/files, prove a solver bottleneck or establish speed improvement. OpenFOAM did not run. Failed parser job 2294674 remains preserved; its fix was in a separate frozen R2 bundle.

## Actual native follow-up and accounting

**2294676 accepted at 3 November 13:57:02 Vietnam**, observed **RUNNING on iris001 at 13:58:42**, elapsed 1:40. Source/input gates and first fresh copy/hash passed; first actual OpenFOAM arm started at 13:58:25 with node sampling. No completed mean yet. [Receipt, startup and review route](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-native20-20261103/STATUS.md).

All four arms keep the same accepted Scotch source and native runtime. Only preparation-child policy changes in A/B/B/A order; launcher-parent policy and solver command stay fixed. Policy inside MPI ranks is not measured. 20 steps / 19 intervals are directional only. Per-arm cap 1,000 seconds, job maximum 75 minutes / 56 CPUs / zero GPUs. Source-after, runtime/payload hashes, native work and cross-arm force coefficients must pass before a performance interpretation.

Parent 2294675 used 3.36 CPU-hours, conservatively 4, and its maximum retired once. Under the authorized research execution contract, the new selected 70-hour maximum has a documented internal-stage change: **989 consumed + 70 reserved = 1059 committed**, old stage 1009 increased by 50 to 1059 for this one test. These numbers are agent-selected planning CPU-hours, not a known billed-SU balance or new owner-set allowance. Fresh admission checked an empty owned queue; the current owned allocation is occupied at the dated snapshot. No NSCC/AI transfer or automatic schedules.

## References and access boundaries

Best reviewed NSCC **3.364622070 s/step** is our organizer-recipe reproduction; organizer **3.210832548** and teammate Gadi **2.079045460** are separate references. Iris values do not forecast Gadi results. No Gadi identity/project supplied.

Latest VPN retry **3 November 00:06:30–00:06:34 Vietnam** returned gateway Authentication failed; 00:07:58 path check remained NAMESPACE_UNAVAILABLE. No new VPN attempt in this turn. [Safe VPN record](nscc-vpn-retry-20261103.md).

[Previous detailed handoff, historical](history/HPC_CURRENT-before-preparation-result-20261103.md). AI payloads, queues, budgets and submission materials remain unchanged.
