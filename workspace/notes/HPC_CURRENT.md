# Current HPC/OpenFOAM handoff

Updated **6 November 2026, 02:03 Vietnam (UTC+7)**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex, schedules or automatic MFA loops.

## Live first cycle: combined recipe is slower — 6 November 2026, 02:03 Vietnam

2294920 RUNNING, elapsed 1:09:54 on iris001. Three complete 40-step /39-interval first arms: teammate56 **33.592853770**, original48 **24.781383192**, hybrid48 **34.849654258 s/step**. Hybrid is slower in this first cycle; do not promote it or claim a new absolute gain. Historical 22-second target remains open. H2 is created with no solver step yet; O2/T2 not started. Full repeats/source/runtime-after/terminal review are pending. [Dated live record](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-best-recipes40-20261105/LIVE-20261105T1901.md).

The static interface proxy improves under the balanced hybrid mapping, but this does not establish faster native timing. If the full matrix confirms a loss, close the unchanged combination. Default-mapped 48 with collated I/O is one possible later isolated-factor hypothesis; not prepared/submitted. Keep all 224 CPU-hours reserved and one-own cap occupied; no new admission or accounting retirement from partial data.

## Live direct recipe comparison — 6 November 2026, 02:01 Vietnam

2294920 RUNNING on iris001, elapsed 1:08:11. Two complete 40-step /39-interval runner-reviewed arms: teammate56 mean 33.592853770 s/step, original48 mean 24.781383192. Hybrid48 has started step 40; its completed record and all three repeats are still absent at this snapshot. Historical 22-second target remains open. No complete matrix, terminal independent/source/runtime-after or repeat-force gates yet. [Live observation](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-best-recipes40-20261105/LIVE-20261105T1901.md).

Read-only proxy verifies 48 pinned boundary files and native 976,693 interface-face total. Actual pre-MPI_Init masks + job-recorded NUMA topology show original48 rank distribution 28/20 versus hybrid48 24/24, with 100,978 versus 83,145 cross-NUMA logical faces. This is mapping/mechanism evidence, not bandwidth, page residency, a causal bottleneck or a speed prediction. No solver/policy/source change occurred. Keep all 100 frozen hashes and full 224 CPU-hour reservation; one-own cap occupied, no new admission or accounting retirement.

## Direct credible-control recipe test accepted — 6 November 2026 Vietnam

**2294920 accepted**, observed RUNNING 00:56 Vietnam on iris001, elapsed 2:20; no batch stderr at that snapshot. Six 40-step /39-interval arms: teammate56 socket/core+collated, original48 default+uncollated, hybrid48 socket/core+collated, then hybrid48/original48/teammate56 repeats. Primary outcome is absolute seconds per step against both credible controls, with every repeat/tail retained. No historical 22-second record or new gain claimed. [Exact recipe table, gates and receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-best-recipes40-20261105/STATUS.md).

All 100 hashes and root offline interfaces/native historical collated-header check pass; only runner/prep/wrapper differ from valid parent. Source/input physics/iteration counts stay fixed. Max 4h /56 allocated CPUs /zero GPUs = 224 CPU-hours reserved. With 1,396 consumed, selected internal stage 1,450→1,620 (+170), not a new owner budget or billed SU. Iris low QoS 12h cap verified; one-own cap preserved. Keep active payload and queue position.

Scotch40 cut 2294919 has passed and its cost/max reservation are reconciled; it is not READY and its optional initialization is deferred. It must not block this native experiment using valid initialized 48/56 sources. The audit confirms historical/recent same iris001/binary/48 linked-library/N56 source identities; cause of raw-time variation remains unproven. [Audit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-absolute-time-audit-20261105/README.md).

## Owner correction: credible best controls and absolute time are primary

The owner rejected presenting a 17–19% gain against a 32-second control as if it had beaten historical 22-second measurements. Preserve the valid 48-vs-56 matched finding, but do not label 48-default the best-known recipe. Next native comparison must replay teammate56 socket/core+collated, original48 default+uncollated, and hybrid48 socket/core+collated, twice each at 40 steps in one allocation. Report absolute means, all repeat arms/tails and credible-control contrasts; no new absolute record without measured evidence. Historical 22.39695/27.09361 teammate arms, same iris001/binary/library/N56 input identities, are retained. Cause of variation remains unproven.

Scotch40 cut 2294919 now passes all ten artifact/native/source/mesh checks in 255 seconds. It is retained but not READY. Actual 3.966667 CPU-hours, conservatively 4; 37.333333 reservation retired once: 1,396 consumed /zero reserved /stage 1,450. Do not let its optional initialization block the independent native recipe comparison using already initialized 48/56 cases. [Review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch40-cut-20261105/completed-2294919/RESULTS.md).

## Distinct Scotch40 cut accepted — 5 November 2026

**2294919 accepted**: one exclusive Iris node /56 allocated CPUs /one serial task /zero GPUs /maximum 40 minutes, 37.333333 CPU-hours reserved within unchanged 1,450 stage (1,392 consumed). All 45 frozen hashes and offline 40/39/41 cardinality gates pass. It creates exact 40-domain native mesh/case preparation only; no READY/init/solver or further gain claimed. [Receipt, hypothesis and required next gates](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch40-cut-20261105/STATUS.md). Preserve active allocation and one-own cap.

The established local finding is now repeated 48-over-56 improvement at 40 steps: 17.38% then 19.21% under opposite orders on iris001. New 40 ranks may win or lose; mandatory initialization and matched comparison remain separate later gates.

## Reverse result reviewed: same-Iris signal repeats — 5 November 2026

2294918 COMPLETED 0:0 in 5,250 seconds /56 CPUs on iris001. Root and independent reviewer pass all 228 hashes/native/source/runtime/fields/rank/force gates. Pooled 48-rank 26.159176710 versus 56-rank 32.380543978 s/step: **19.213288300% lower time**, both adjacent comparisons favorable (15.3510% /23.1110%). Opposite-order parent 2294916 showed 17.3826% lower. Between allocations, 48 means differ −2.04%, 56 means +0.18%; both on iris001. This now supports a repeatable same-Iris 40-step rank-density signal, not full-horizon/universal/teammate performance. [Detailed result, tails and telemetry limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-reverse-20261105/completed-2294918/RESULTS.md).

Actual 81.666667 allocated CPU-hours, conservatively 82; 140 maximum retired once: 1,392 consumed /zero reserved /stage 1,450. Required telemetry present; pressure unavailable and no causal bandwidth/profile evidence. Next distinct candidate is 40 versus 48 ranks; fresh Scotch40 cut being prepared, not yet submitted. No implied further gain and no change to frozen old jobs.

## Independent reverse confirmation accepted — 5 November 2026

**2294918 accepted**, observed RUNNING on iris001 at 21:30 Vietnam. Order 48/56/56/48, all 40 steps /39 intervals. It tests the 17.38% parent signal under reversal, retaining all native physics, sources, settings and caps. All 100 frozen hashes verified, only run-order/label-based statistics and job name differ from valid parent 2294916. [Receipt, limits and test provenance](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-reverse-20261105/STATUS.md). No new speed result yet; preserve active allocation and one-own cap.

Maximum 140 allocated CPU-hours reserved with 1,310 consumed: internal stage 1,367 →1,450 (+83) for this bounded request; not a new owner allowance or known site-billed SU. NSCC/AI remains separate. Parent result 17.3826% lower time is promising but 48-repeat drift 15.1737% requires this confirmation. No stable winner or teammate comparison claimed.

## Atlas source updated; hosted publication blocked

The reviewed eighteenth HPC milestone and numerical metric cards pass local browser and AI-preservation checks and are pushed. GitHub workflow 42046513133 failed before any build step: account locked due to a billing issue; deploy skipped. Live-byte verification still finds the previous 17-milestone page. [Exact receipt and source/live hashes](../reports/hpc-rank-density-atlas-20261105/publication-blocked.json). Do not claim the new result is live. No account/payment change or blind rerun attempted. This does not affect Iris job 2294918 or its allocated budget.

## Complete forty-step result reviewed — 5 November 2026

2294916 COMPLETED 0:0 in 5,297 seconds /56 CPUs on iris001. All four 40-step native replays, 228 transferred hashes, source/payload/runtime before/after, rank and same-partition force-repeat gates pass both root and independent review. 48-rank pooled 26.703647651 versus 56-rank 32.322052535 s/step: **17.382574569% lower**, with both adjacent contrasts favorable (25.157475% /9.191942%). Candidate repeats drift +15.1737%; this is a promising within-allocation signal, not a confirmed universal win or teammate comparison. [Full result and telemetry limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-20261105/completed-2294916/RESULTS.md).

Actual 82.397778 allocated CPU-hours, conservatively 83; 140 maximum retired once: 1,310 consumed /zero reserved /stage 1,367. Pressure data unavailable; required memory/vmstat/frequency samples present. No bandwidth or causal bottleneck claim. Next distinct ready work is reverse BAAB40 confirmation in a new allocation; being prepared, not submitted yet. Preserve all old raw results and do not promote the selected 14-step graph arm.

## Live forty-step comparison — 5 November 2026, 17:06 Vietnam

2294916 RUNNING on iris001, elapsed 56:52. Two complete forty-step arms: A1-56 mean 33.163697419 s/step; B1-48 mean 24.820548476 s/step, first candidate contrast 25.157475% lower. B2-48 at 26/40, final A2-56 not started. Runner per-arm native gates passed for the first two; independent terminal/source/runtime-after review is pending. No stable gain or winner claim yet. [Preserved live checkpoint](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-20261105/LIVE-20261105T1006.md).

All 100 local frozen hashes match deployment. Preserve the accepted allocation and full 140 CPU-hour maximum reservation under the one-own-allocation cap; no new submission during this live checkpoint. No reservation retired or extra spending authorised by these partial means.

## Full forty-step rank-density comparison accepted — 5 November 2026

**Iris 2294916 accepted**: A1-56 /B1-48 /B2-48 /A2-56, all forty steps /39 intervals. Same original physical problem and native Basic settings; partition and rank count differ. Maximum 2.5 hours /56 allocated CPUs /zero GPUs, 140 allocated CPU-hours reserved. With 1,227 consumed, the selected bounded internal stage extends from 1,289 to 1,367 (+78); this is not a new owner budget or known billed SU. Fresh queue and all 100 frozen hashes verified before admission. [Exact receipt, gates and limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-20261105/STATUS.md). Preserve the accepted allocation and one-own cap. No new solver result yet.

The 14-step 21.0512 observation belonged to the old graph-placement branch; its complete reversed screen lost 5.3685%. It was never a Scotch48 trial or a stable winner. The new equal-horizon trial is a distinct hypothesis, not evidence that the old selected minimum beats organizer/teammate.

## Scotch48 READY reviewed; forty-step comparison being prepared

2294915 COMPLETED 0:0 in 111 seconds /56 CPUs on iris001. All three required native initialization stages, 48-rank probe, 288 field inventories, source/payload checks and 26 transferred hashes replay. READY and new 896-core-file +13-ancillary-file manifests are preserved. [Full result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch48-init-20261105/completed-2294915/RESULTS.md). Actual cost 1.726667 allocated CPU-hours, conservatively 2; maximum retired once: 1,227 consumed /zero reserved /stage 1,289.

The selected 21.051168942 s/step graph arm was a 14-step screen, not a best-configuration ranking. In the full reversed BAAB comparison 2294390, graph arms were 21.051169 and 38.462425 versus identity controls 23.241965 and 33.239424 s/step. The pooled graph candidate was 5.3685% slower, so that unchanged performance branch was closed before longer confirmation. Displaying only its lowest arm beside 40-step organizer or teammate results can mislead; no matched win is established. Raw results remain intact.

The distinct 48-versus-56 rank-density comparison will use 40 steps /39 measured intervals per arm, in one 56/48/48/56 allocation. This is not a complete official simulation or a revival of the rejected graph branch. It is being prepared; no new job acceptance or speed result is claimed here.

## Scotch48 initialization accepted — 5 November 2026

**2294915 accepted**: mandatory renumberMesh → potentialFoam → applyBoundaryLayer at 48 MPI ranks, one exclusive 56-CPU Iris node, zero GPUs, at most 20 minutes. The 18.666667 allocated CPU-hour maximum is reserved with 1,225 consumed under unchanged 1,289 internal stage. All 44 frozen payload hashes, exact cut gates and offline acceptance/rejection checks pass. [Receipt, limits and pending terminal review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch48-init-20261105/STATUS.md). No assumed socket map, solver score or initialization success yet. Preserve the active allocation and one-own cap.

## Scotch48 cut reviewed — 5 November 2026, 15:23 Vietnam

2294914 COMPLETED 0:0 in 264 seconds /56 CPUs on iris001. Exact 48-domain and 65,334,765-cell gates pass, with 288 restored initial fields; maximum domain/mean cell ratio 1.010184. Ten transferred files, full official serial mesh identity, source before/after and native logs verify. This is not a solver or READY result. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch48-cut-20261105/completed-2294914/RESULTS.md).

Actual cost 4.106667 allocated CPU-hours, conservatively 5. Retired 37.333333 reservation once: 1,225 consumed /zero reserved /unchanged 1,289 internal stage. Mandatory native initialization is being prepared; no acceptance implied yet. No new faster solver configuration is established.

## Distinct rank-density preparation accepted — 5 November 2026

Iris **2294914 accepted**: fresh Scotch48 cut and restored fields only, not READY or a solver score. Maximum 40 minutes /56 allocated CPUs /zero GPUs, 37.333333 allocated CPU-hours reserved within unchanged 1,289 internal stage (1,220 consumed). All 45 payload hashes and local 48/47/49-domain tests pass. [Frozen payload, actual receipt and required later gates](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch48-cut-20261105/STATUS.md). This distinct 48-versus-56-rank question replaces unchanged losing flags; native initialization and matched solver comparison remain unsubmitted. Preserve one-own-allocation cap.

Fresh Iris queue was empty at 14:29 Vietnam before admission; read-only NSCC path at 14:30 remained NAMESPACE_UNAVAILABLE, SSH authentication untested, no MFA attempt. No new faster solver result. Hosted 17-milestone atlas was verified live previously; this preparation is not a numeric performance result.

## MPI qualification closed; build rules inspected

2294805 COMPLETED 0:0 in 20 seconds /56 CPUs, all four correctness/binding/quantile-replay gates pass. Forced tuned candidate increases median latency by 56.8–70.4% and p95 by 44.4–85.0% in matched blocks; no native solver follow-up is warranted for that candidate. Actual runtime is Open MPI 5.0.10rc2; default verbose output includes ucc priority 100, candidate tuned priority 100. This is component evidence, not a per-operation OpenFOAM profile or proof of a bottleneck. [All raw samples and result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-allreduce-qualify-20261105/completed-2294805/RESULTS.md).

20 seconds costs 0.311111 allocated CPU-hours, conservatively 1; maximum 4.666667 retired once, leaving 1,220 consumed /zero reserved /stage 1,289. Compiler-rule inspection also found -O3 and -march=cascadelake; that does not prove binary build flags, but removes the assumption that a generic unoptimized build can simply be replaced. [Read-only provenance](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-build-flags-review-20261105/README.md). No newly qualified faster solver configuration exists from these branches; do not fill the queue with unchanged losing flags.

## Distinct MPI qualification accepted

New **2294805 accepted** at 2026-11-04T18:34:01.882318Z: tiny MPI_Allreduce correctness/latency/component qualification, not OpenFOAM solve. Maximum 5 minutes /56 CPUs /zero GPU, 4.666667 CPU-hours reserved within unchanged 1,289 internal stage (1,219 consumed). Exact runtime/component evidence and repeated >=10% median/p95 gates must pass before any solver follow-up. [Actual receipt and limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-allreduce-qualify-20261105/STATUS.md). This does not attribute 2294803's timeout to MPI.


## Native solver-rank trial stopped — 5 November 2026, 01:21 Vietnam

2294803 FAILED 1:0, 2,667 seconds. A1 completes 40 steps, mean 24.758556905 s/step. B1 interleave times out 124 at 1,500 seconds, last started 35 with 33 measured intervals averaging 41.846495650 s/step diagnostically. B2/A2 not started. Full candidate/four-arm score is unavailable; close this unchanged interleave-all solver candidate under its envelope rather than raising the cap. Both 56-rank pre-exec policy/affinity proofs pass and 34 force-prefix rows match; post-source/runtime gates were not reached. [Terminal review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-solver-rank-interleave40-20261105/completed-2294803/RESULTS.md).

Cost 41.486667 allocated CPU-hours, conservatively 42, 112 reservation retired once: 1,219 consumed /zero reserved /stage 1,289. Native correctness and terminal success are separate; the failed candidate is not a valid complete benchmark. A new low-cost MPI-collective qualification is being prepared from runtime evidence; no MPI bottleneck is established by this timeout.

## Live checkpoint — 5 November 2026, 01:02 Vietnam

2294803 RUNNING on iris001, elapsed 25:37 at 01:02:01 Vietnam. At01:02:29 the first default-policy arm completed 40 steps with printed mean 24.758556905 s/step, exit 0 and all 56 pre-exec policy/affinity proof gates passing. Candidate B1 was at step 9/40 with 56 pre-exec records; no completed candidate mean. B2/A2 had not started. Preserve the active allocation, frozen payload and 112-hour reservation; no new admission while cap is occupied. Live arm output is not a terminal four-arm score.

The GitHub Pages correction is now verified live (HTTP 200): latest numeric result 2294800 is +6.09738% slower and the preparation-only branch is closed. [Hosted HPC](https://trungdangtapcode.github.io/apac-hpc-ai-2026/#hpc). [Served-content receipt](../reports/hpc-repeat-result-update-20261105/published-verification.json). Earlier queued-publication records are historical and superseded.

## New native factor accepted — 5 November 2026 Vietnam

**2294803 accepted** at 2026-11-04T17:36:24.887079Z. Four 40-step ABBA arms test solver-rank default versus in-rank interleave policy with preparation always inherited, qualified by actual rank/page probe 2294802. Per-rank policy/affinity proof is collected immediately before solver exec, not assumed during its whole runtime. [Frozen 64-file payload, receipt and state](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-solver-rank-interleave40-20261105/STATUS.md). No new speed result yet. Maximum 2 hours /56 CPUs /zero GPUs, 112 CPU-hours reserved; internal ledger 1,177 consumed /112 reserved /stage 1,289. This bounded 79 internal-stage extension is separate from any owner limit or site/billed SU. Preserve one-own-allocation cap.

The earlier copy/hash-only gain is rejected by 2294800 (+6.09738% slower); its web correction is committed but GitHub Pages workflow 41877557587 remained queued waiting for a runner at the last check. Do not claim live publication of the new losing result before served-byte verification. Source and raw evidence are backed up.

## New mechanism qualified — 5 November 2026 Vietnam

Outer-launcher 2294801 and in-rank 2294802 both COMPLETED 0:0 in 2 seconds /56 CPUs. Outer form leaves all ranks default with single-node anonymous 8 MiB mappings. In-rank form changes all 56 to interleave and both-node residency, with identical reported CPU affinity. [Actual rank/page records and limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-inprocess-policy-20261104/completed-2294802/RESULTS.md). This qualifies command placement, not faster OpenFOAM or policy throughout solver execution.

Both small maximum reservations retired once from accounting: total 2 conservative planning hours; consumed 1,177 /zero reserved /stage 1,210. Site SU remains unknown. A distinct actual solver-rank-policy trial is being prepared, keeping preparation inherited; no native job acceptance or score is implied yet. The old preparation-child-only performance claim remains closed.

## Distinct rank-policy qualification accepted

New diagnostic **2294801 accepted** at 2026-11-04T17:22:17.718827Z: 56 MPI ranks, inherited versus launcher interleave policy, anonymous 8 MiB first-touch pages per rank. Maximum 5 minutes /56 CPUs /zero GPUs; 4.666667 planning CPU-hours reserved within the unchanged 1,210-hour stage. No solver/score or improvement claim. [Receipt, frozen code and limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-memory-policy-20261104/STATUS.md). This does not reopen the rejected preparation-child-only speed claim.

## Independent repeat reviewed — 5 November 2026 Vietnam

2294800 COMPLETED 0:0 in 4,925 seconds /56 CPUs. Four 40-step native replays and source/runtime/policy/force gates pass, but interleaved preparation is **29.004833605 versus 27.337934579 s/step**, **6.09738% slower**. Pairs disagree (+18.26064% /−3.96822%). The prior 30.60% BAAB gain does not reproduce under same-horizon ABBA; close the unchanged preparation-child-only performance branch. [Full result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-repeat40-20261104/completed-2294800/RESULTS.md).

Reservation retired once: 76.611111 allocated CPU-hours, conservatively 77. Internal ledger 1,175 consumed /zero reserved /stage 1,210; site SU remains unknown. A distinct small qualification of actual MPI-rank policy and first-touch anonymous pages is being prepared; no speed result or new admission is implied until receipt. The hosted numeric result will retain each job separately and show the latest failed confirmation rather than promoting the older favorable allocation.

## Continued execution — fresh same-horizon repeat

Owner asked to continue research rather than stop after review/diagram. New Iris **2294800 accepted** at 2026-11-04T15:07:28.254678Z. Same 40-step horizon and runtime/source/policy checks as 2294735, ABBA rather than BAAB. [Actual receipt and frozen payload](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-repeat40-20261104/STATUS.md). Maximum 2 hours /56 CPUs /zero GPUs; 112 planning CPU-hours reserved. Ledger is 1,098 consumed +112 reserved = 1,210 internal stage; actual site SU unknown. No new performance result yet; preserve queue position and one-own cap.

The owner additionally requires numerical Result schemas on the shared website, matching AI's metric-based presentation. HPC Result must show named numeric metrics, units, run/horizon context and missing-data states. Assessments belong separately. Do not turn remarks into a numeric score or treat graph-only evidence as solver performance.

## Completed confirmation reviewed — 4 November 2026

2294735 COMPLETED 0:0 in 4,710 seconds, 56 CPUs. Independent native replay and all source/runtime/payload/force gates pass. Candidate pooled 21.862379771 versus control 31.502857339 s/step: 30.601914818% lower within this 40-step BAAB job. Both adjacent comparisons favor candidate; candidate repeat drift +0.17821%, control +14.16819%. Effect size differs sharply from the earlier 1.77% screen; retain as a strong within-allocation signal, not a universal speedup. [Full result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-reverse40-20261104/completed-2294735/RESULTS.md).

Cost 73.266667 allocated CPU-hours, conservatively 74; 112-hour reservation retired once: 1,098 consumed /zero reserved /1,136 internal stage. Not billed SU. Historical running snapshots below are superseded. The owner requested a top-to-bottom dated diagram like AI; both the hosted atlas and reproducible static map are updated from the reviewed results. No new job was submitted during this diagram revision.

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
