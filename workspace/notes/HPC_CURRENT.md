# Current HPC/OpenFOAM handoff

Updated **03 November 2026, 14:00:24 Vietnam (UTC+7)**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex, schedules or automatic MFA loops.

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
