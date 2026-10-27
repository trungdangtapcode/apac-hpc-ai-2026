# Current HPC/OpenFOAM handoff

Updated **2026-10-27T05:27:17.652192+00:00**. This is HPC session `01a1508d-26b0-7dd0-9dc1-f217ce0aff40`, covering NSCC CPU and Iris CPU. AI/Qwen belongs to the other mapped session. Keep one own active or queued CPU job per cluster and combined own NSCC CPU/AI PBS cap three. No background Codex, schedules or automatic chat notifications.

## Current results

**NSCC full-run reference remains 3.364622070 seconds/step**, job 25940700, four nodes / 512 ranks / 150 steps / 149 timings. It repeats the intended default-Scotch configuration; it is not a measured placement gain or organizer-confirmed score. [Review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/RESULTS.md).

**Native placement job 26016270 passes**, F / Exit 0 in 17 seconds. Replay verifies 1,569 artifacts and all 512 main threads on their exact singleton targets through collectives and two seconds. Each host has 256 online logical CPUs, 128 physical cores, two packages and eight NUMA nodes. All targets reproduce the same allocation's baseline entry CPU by PMI/host. The mechanism no longer relies on capturing a singleton entry mask. This does not qualify Pstream, helper threads, memory locality or solver speed. [Result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-postinit-pin-20261027/completed-26016270/RESULTS.md).

**Iris zyx remains the preferred screened candidate.** Its two 30-step pairs observed 26.94% and 21.42% lower mean time than their respective xyz controls; those controls were below native sample recommendations. The 50-step extension 2294148 completed 0:0 on iris009: mean **21.112004724 seconds/step**, p95 21.248222475; later versus earlier window +0.509%. All first-30 Cd rows reproduce prior zyx. Final step-50 Cd is 0.400779301; 15 bounding-omega messages remain. Native sample recommendation zero is rounding of 0.167091137, not zero variance. No full 150-step, matched 50-step or official gain is claimed. [Review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-zyx50-20261027/completed-2294148/RESULTS.md).

## Current queue and next gate

**26019383.pbs101 is submitted**, Q/q5 at **05:25:41 UTC on 27 October**, waiting for `node_pool`. Maximum ten minutes / 512 CPUs / **85.333333 SU**. Three arms test an unchanged native control, adapter-backed control and real OpenFOAM checkMesh over an owned 8192-cell diagnostic mesh. No DrivAer solver runs. Require every init/topology/main-thread/finalize audit and the actual PMPI_Finalize return, actual utility version/F64/rank/cell proof, source/runtime hashes and all command statuses. [Receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-pstream-latepin-20261027/STATUS.md).

After completion, collect and independently replay this integration test before any full contest-solver allocation. Actual installed Pstream imports Init_thread and Finalize; local syntax checks alone do not prove the adapter ABI. If it passes, derive an identity-pin ABBA comparison on unchanged Scotch and initialized fields. The old ABBA draft uses an unqualified entry-capture shim and graph permutation and must not be deployed wholesale. Full initialized clones include processor mesh and fields; the earlier tiny 43-file source copy does not bound their cost.

## Budget and access

NSCC CPU project **59000042** is distinct from AI GPU project 59010042. Current ceiling **29,777.846 SU**, conservative commitment **4,857.2 SU**, headroom **24,920.646667 SU** after the new reservation. Older unknown maxima remain. No exact posted per-job charge is claimed. A fresh site query still carries a 25 October backend balance label; preserve that limitation. Owner's planning deadline is 30 October; site expiry metadata says 15 November.

Iris has its own **224 allocated CPU-hour envelope**, consumed allowance **219**, outstanding maximum **0**, headroom **5 CPU-hours**. SU rate and balance are unknown. This does not fit a full 150-step or another matched short pair. Keep the remainder for a justified bounded validation and continue active optimization on NSCC; do not add arbitrary shorter runs to occupy a queue. Shared Iris ledger remains `iris-scotch56-20261025/budget.json`.

CPU SSH uses the verified separate **r9** master through the existing VPN. Both nscc01 and nscc02 are valid CPU login hosts; do not require only nscc02. Preserve live VPN and old state. Iris requires forced-TTY gateway auto-jump and the verified bridge. [Access correction](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261026/REPORT.md). Never retain authentication material in research files.

## Preservation and history

Edit active sources once; explicitly capture, screen, verify, commit and push each completed checkpoint. Preserve failed arms, raw archives, hashes and reasoning. No submission materials changed. Inline archives retain recent small evidence; older external large artifacts still need separate off-host copying. Canonical mesh and initialized binary fields remain remote with reproducible stages and seals. Missing bandwidth, NUMA residency and helper-thread measurements remain unknown.

The [previous detailed handoff](history/HPC_CURRENT-before-pstream-admission-20261027.md) preserves earlier launcher, syscall-trace, failed Scotch and preparation stages. Use the [research journal](../reports/research-journey-20261019/journal/README.md) for complete questions, controlled changes, observations, corrections, costs and next decisions. Dated scheduler snapshots are historical; refresh actual queues on continuation.

## Latest owner-directed transfer plan — 2026-10-27T10:33:22.706355+00:00

The owner requested moving promising candidates to NSCC and then requested a plan. [Canonical plan and adaptive queue](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-transfer-campaign-20261027/PLAN.md): fresh native Scotch reference; full xyz/zyx hierarchy on 512 ranks with factors (16 8 4); reverse confirmation; qualified pinning and balanced/aggressive placement; combinations and independent repeats. Native Basic tests do not depend on the PMPI gate. LD_PRELOAD branches are Bonus under pinned F2 and need 1/2/4-node F3 self-proof before promotion. All new entries are planned, not submitted.

At 10:28 UTC on 27 October, both fresh scheduler queries failed before SSH because the VPN wrapper found no live session. Do not read the earlier Q snapshot above as current. Integration 26019383 was seen terminal F at 07:48, but its exit status and application replay remain unreviewed. Four other shared-account CPU jobs 26023372/26023373/26023382/26023383 were queued then, with unresolved ownership/reservations. Reconcile them before any new qsub; preserve their positions and frozen payloads.

The plan proposes an 8000-SU conditional wave, with 7253.333333 SU of listed maxima and 1536 SU in the initial native/reverse stage. This is planning only: no reservation, budget increase, authentication attempt, background schedule or new PBS receipt was created. Current posted balance and cap availability remain unknown.

## Transfer execution authorised — 2026-10-27T10:41:50.657111+00:00

The owner now explicitly requests submitting all justified ready candidates to beat the baseline. [Execution checkpoint](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-transfer-campaign-20261027/EXECUTION.md). Native S0/Hxyz/Hzyx preparation is proceeding for one four-node/512-rank/90-minute allocation, maximum 768 SU. Every arm retains 150 steps and the mandatory chain.

Two authorised VPN attempts ended with Authentication failed; the owner reported a pending DUO notification between attempts, but approval is unconfirmed. No working tunnel, current queue/credit or new PBS receipt is verified. No new reservation, credential capture, background Codex or change to AI occurred. Existing shared-account CPU jobs still require reconciliation before admission.
