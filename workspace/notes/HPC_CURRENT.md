# Current HPC/OpenFOAM handoff

Updated **3 November 2026, 13:48 Vietnam (UTC+7)**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex, schedules or automatic MFA loops.

## Answer to the Iris comparison question

The supplied teammate runtime recipe has a **qualified 11.2228% lower mean** than organizer/BTC in the complete 40-step Iris comparison 2294637. Our `zyx` loses 10.2150% to its own matched Scotch control; the small `xzy` gain reverses to 10.2525% slower in confirmation. Latest `xyz` 2294671 is incomplete and cannot establish a gain. No matched three-way test proves we beat the teammate. [Readable comparison, exact values and provenance](../reports/hpc-iris-comparison-20261103/README.md).

Our old **21.229593669 s/step** is a real completed Iris observation, not a stable matched win over teammate/BTC. Never compare it against another allocation's slower raw time to claim first place.

## Reviewed preparation mechanism

**2294675 COMPLETED 0:0**, 216 seconds / 56 CPUs on iris001. Terminal state collected **13:42:51 Vietnam**, compact evidence collected later this turn. All four fresh A/B/B/A preparations, actual policies, input/copy/source-after gates, 10 collected artifact hashes and 7 frozen hashes replay. Source is 1,040 accepted regular files plus 13 pinned metadata files and the approved mesh symlink. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-numa-qualify-r2-20261103/completed-2294675/RESULTS.md).

Inherited policy twice gave approximately 0 / 9.78 GiB of additional node-wide FilePages; interleaved child policy twice gave 4.89 / 4.89 GiB across the two NUMA nodes. This qualifies the policy mechanism and consistent aggregate response. It does not attribute individual pages/files, prove a solver bottleneck or establish speed improvement. OpenFOAM did not run. Failed parser job 2294674 remains preserved; its fix was in a separate frozen R2 bundle.

## Next action and accounting

A **native OpenFOAM comparison is being prepared**, all four arms using the same accepted Scotch source and solver settings. Only the copy/hash child's memory policy changes; solver policy stays inherited and is recorded. ABBA, 20 steps / 19 measured intervals, equal node sampling. Per-arm timeout increases from 720 to 1,000 seconds to include finalization; maximum one exclusive 56-CPU, zero-GPU allocation, 75 minutes. It is not submitted until a frozen root review, fresh queue, bounded stage record and definite receipt exist.

2294675 used 3.36 allocated CPU-hours, conservatively 4. Its 9.333333-hour reservation retired once. **Ledger 989 consumed + 0 reserved; existing agent-selected stage 1,009; 20 hours remain**. A 70-hour maximum native request would require a separately documented internal-stage increase of 50 to 1,059 before reservation. This is not a site SU balance or an owner-stated ceiling. Latest observed shared queue at collection was empty; check again under lock at admission. No NSCC/AI debit.

## References and access boundaries

Best reviewed NSCC **3.364622070 s/step** is our organizer-recipe reproduction; organizer **3.210832548** and teammate Gadi **2.079045460** are separate references. Iris values do not forecast Gadi results. No Gadi identity/project supplied.

Latest VPN retry **3 November 00:06:30–00:06:34 Vietnam** returned gateway Authentication failed; 00:07:58 path check remained NAMESPACE_UNAVAILABLE. No new VPN attempt in this turn. [Safe VPN record](nscc-vpn-retry-20261103.md).

[Previous detailed handoff, historical](history/HPC_CURRENT-before-preparation-result-20261103.md). AI payloads, queues, budgets and submission materials remain unchanged.
