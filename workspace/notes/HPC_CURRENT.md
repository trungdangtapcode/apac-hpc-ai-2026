# Current HPC/OpenFOAM handoff

Updated 2026-10-27T17:33:06.657738+00:00. Vietnam time is UTC+7. This fork 01a17c4b-65e6-75e0-be95-c5bea1b25502 continues HPC parent 01a1508d-26b0-7dd0-9dc1-f217ce0aff40. AI/Qwen belongs to its separate mapped worker. No background Codex, schedules or automatic chat notifications.

## Live Iris job

**Job 2294234 is RUNNING on iris024**,verified 17:29:25 UTC 27 October / 00:29:25 Vietnam 28 October. Actual submission confirmation was 00:28:44 Vietnam. One exclusive CPU node, 56 ranks, zero GPUs, QoS low, 3-hour maximum. It runs zyx then xyz, each 150 steps with 149 native timer samples, on the same allocation. [Receipt,source and exact live progress](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-20261027/STATUS.md).

The 49-file runtime kit is sealed. Both source cases were READY, with 56 processor directories. Root review includes actual retained full 150 parser replay, source/copy/physics/iteration/force gates, zero-time latestTime checks, stable executable/library identities and all command exits. First runtime source-hash gate passed 31.46 s and zyx clone began. No new mean or speedup exists yet. A partial first arm is not a completed matched pair.

Remote root: `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-orderfull150-20261027T172755Z`. Worker results are `root/runs/2294234`, cases are `root/cases/zyx` and `root/cases/xyz`, Slurm output is `root/kit/runs/2294234.out/.err`. Use the verified forced-TTY `tools/iris_bridge.py` for access. Do not cancel/requeue just because it takes time. Preserve shared-login other teams' jobs; own names use tu-. One own queued/running Iris allocation is the cap.

## Budget

Same Iris ledger: `iris-scotch56-20261025/budget.json`, lock sibling budget.lock. Latest explicit owner instruction redirects measurements to Iris instead of waiting for DUO. Root transparently extended the original agent-defined 224-hour envelope by one bounded 168-hour request to 392 CPU-hours. **Consumed 219 + reserved 168 = 387**, headroom 5. Preserve all old jobs/history; no NSCC debit and no inferred SU rate or balance. [Rationale](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-20261027/budget-authorisation.json). Do not retire the reservation before actual terminal/resource review.

## Retained performance and meaning

NSCC best reviewed own full observation remains **3.364622070 s/step**, job 25940700, four nodes/512 ranks/default Scotch/150 steps / 149 samples. It reran the principal organiser recipe; it is not a demonstrated own optimization. Organiser external reference 3.210832548 is a separate allocation, not our matched baseline. No claimed NSCC gain exists yet.

Iris short order pairs observed 26.94% and 21.42% lower times for zyx, with limited controls; single 50-step zyx job 2294148 averaged 21.112004724 s/step. The active 150-step pair tests the missing full-length comparison. Iris raw seconds are not ranked against NSCC 3.3646 and are not the contest's scored result. [Own findings](/home/apacsc42/workspace/reports/hpc-research-journey-20261023/OWN_FINDINGS_THROUGH_20261027.md).

## NSCC remains separate and blocked

No verified live VPN; two earlier authentication attempts failed. No new VPN authentication was attempted during this Iris action. The 61-file native S0/Hxyz/Hzyx bundle is ready offline but remains **unsubmitted and unreserved**. Do not conflate it with actual Iris 2294234. [NSCC ready bundle](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-transfer-campaign-20261027/native-wave/STATUS.md).

NSCC old 26019383 was seen F at 07:48 UTC without exit/log replay. Four shared-account jobs 26023372/26023373/26023382/26023383 were queued then; their current state/provenance is unverified. CPU ceiling 29777.846 SU, dated commitment 4857.2 / headroom 24920.646667 remain dated. Query both CPU/AI queues and current credit under CPU-before-AI locks before any NSCC admission; own CPU cap 1 and combined PBS cap 3 including holds. Preserve frozen payloads and other worker work.

The post-init native probe 26016270 qualifies 512 main-thread targets, not actual solver speed or Pstream integration. LD_PRELOAD branches are Bonus under official F2 and require F3 self-proof. Native hierarchical order Basic tests do not depend on the PMPI branch.

## Next actions and preservation

Inspect actual 2294234 progress, then collect/replay both complete native outputs, all 149 samples/150 force rows, field/source/runtime hashes, terminal Slurm status and available resource/VM evidence. Missing hardware counters remain unknown. The existing small-artifact collector/replay should be derived for this exact root and full 150 layout after completion. Next choice follows the measured pair rather than an unchanged losing branch.

Capture safe explicit checkpoints, verify, commit and push promptly. The payload is backed up; large processor meshes/fields remain remote with seals/rebuild sources and are not uploaded by Git. No slide or submission-package change is made by this job.

[Prior detailed handoff and corrections](history/HPC_CURRENT-before-iris-full150-20261027T1730.md) retain the VPN chronology and older branches. [Journal](../reports/research-journey-20261019/journal/README.md) retains the full reasoning.

## First solver progress — 17:34 UTC / 00:34 Vietnam

Fresh Slurm confirms 2294234 RUNNING on iris024. Both source and clone checks returned zero; zyx solver started at 17:30:32 UTC with an effective 4192-second cap and has reached Time 9/150. This is partial progress, not a completed mean or accuracy result. xyz remains the second arm. [Retained phase snapshot](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-20261027/early-progress.json).

## Mandatory execution rule

The owner requires that this dispatch failure not need another reminder. Read [research-execution-contract-20261027.md](research-execution-contract-20261027.md) and the new canonical AGENTS.md section before continuation. If NSCC is blocked, use authorised feasible Iris work; optional pinning diagnostics must not block independent native solver tests. Actual submission requires a receipt/job ID. Keep budgets, locks, caps and disabled automation unchanged.
