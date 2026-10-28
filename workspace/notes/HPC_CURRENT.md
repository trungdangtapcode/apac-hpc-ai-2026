# Current HPC/OpenFOAM handoff

Updated from actual Iris observation 2026-10-28T08:40:30.716981+00:00: **15:40:30 on 28 October 2026, Vietnam time (UTC+7)**. Fork 01a17c4b-65e6-75e0-be95-c5bea1b25502 continues HPC parent 01a1508d-26b0-7dd0-9dc1-f217ce0aff40. AI/Qwen remains with its separate mapped worker. No background Codex, schedules or automatic chat notifications.

## Actual running job

**Iris 2294262 is RUNNING on iris005**, observed 22 seconds after start. It passed the frozen-kit gate and was in xyz source preparation; this is not yet a solver measurement. Accepted at **15:40:09 Vietnam**. One exclusive node, 56 CPU ranks, zero GPUs, maximum three hours, full **xyz then zyx** pair (150 steps and 149 native timings each). It reverses the completed full pair's serial order on a fresh node. [Actual receipt and bundle status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-reverse-20261028/STATUS.md).

Frozen runtime kit: 49 files. Remote root: `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-reverse150-20261028T083845Z`. Run records: `root/runs/2294262`; cases: `root/cases/xyz` and `root/cases/zyx`; Slurm logs: `root/kit/runs/2294262.out/.err`. Use the verified forced-TTY `tools/iris_bridge.py`. One own active Iris allocation is the cap. Preserve all shared-login other teams' jobs.

## Reviewed full-length Iris result

Parent **2294234**, iris024, completed exit 0:0 in 7,585 seconds. Full local raw replay and 129 retained-file transfer hashes pass. Both arms have 150 steps, 149 timing intervals, 150 Cd rows, fixed iterations and matching timer tables. Runtime, source/copy/initialized-field seals and command exits pass.

| Metric | zyx first | xyz second |
|---|---:|---:|
| Mean seconds per step | 21.229594 | 26.953799 |
| P95 seconds per step | 21.395847 | 31.569807 |
| Final total Cd | 0.282424 | 0.287070 |

**21.2371% lower mean time in this one Iris allocation.** Final Cd differs by **1.6185% relative to xyz**; do not claim output equivalence, a contest score or an NSCC speedup. Current reverse trial tests serial order and node repeatability. Whole-node procfs and GNU time evidence do not identify hardware bandwidth or a NUMA cause. Hardware counters, per-rank frequency and per-process NUMA maps were not collected. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-20261027/completed-2294234/RESULTS.md).

## Iris accounting

Ledger: `iris-scotch56-20261025/budget.json`, lock `budget.lock`. Parent reservation 168 was retired once; actual allocation 117.988889 CPU-hours is conservatively counted as 118. Total consumed **337**, new reserved maximum **168**, commitment **505 allocated CPU-hours**. Internal stage ceiling **505**, headroom 0. The agent transparently extended the previous internal 392 ceiling by 113 to fund this one authorized followup after using 55 released headroom. The owner authorized continuation but did not specify 505 numerically. Site SU rate and balance are unknown; no NSCC CPU or AI credits were charged. [Bounded authority](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-reverse-20261028/budget-authorisation.json). Do not add another own job or silently extend this stage.

## NSCC is separate

CPU SSH reuse immediately reported no live VPN session during this turn; no further DUO prompt was sent. Old NSCC jobs remain unknown, not absent. The native S0/Hxyz/Hzyx bundle remains **unsubmitted and unreserved**. Its native Basic measurements do not depend on optional PMPI pinning. [Ready native transfer](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-transfer-campaign-20261027/native-wave/STATUS.md).

NSCC best own reviewed full result remains **3.364622070 s/step**, 25940700, four nodes/512 ranks/default Scotch/150 steps. It reproduces the principal organizer recipe, not our verified new optimization. External organizer 3.210832548 is a separate allocation. No own NSCC configuration has yet demonstrated a matched improvement over 3.3646. Keep Iris and NSCC raw seconds separate.

Old 26019383 was seen F without exit/log replay; shared-account 26023372/26023373/26023382/26023383 were queued in that dated observation, provenance unresolved. Preserve their reservations and queue positions. Before NSCC admission query both CPU/AI queues and credit under CPU-before-AI locks: own CPU cap 1, combined PBS cap 3 including holds. CPU 59000042 and GPU 59010042 are distinct projects. Detailed dated accounting remains in the previous handoff and actual ledger.

## Next action

Query actual 2294262 progress. On completion, collect native logs, timer/force tables, source/copy/field seals, runtime identities, phases, resources and terminal scheduler record. Compare each order to 2294234 without pooling correlated steps or inferring output equivalence. Reconcile its 168 maximum once from actual terminal allocated time. Select the next distinct hypothesis from that review within current authority and caps. Do not cancel/requeue merely to show activity or block independent native work behind optional diagnostics.

The [execution contract](research-execution-contract-20261027.md) and canonical AGENTS.md remain mandatory. Capture safe explicit milestones and push promptly. Large meshes/fields remain remote; selected text evidence and rebuild provenance are backed up. No slide/submission package was changed. [New journey entry](../reports/research-journey-20261019/journal/entries/20261028-hpc-full150-result-and-reverse-submitted.md). [Previous handoff](history/HPC_CURRENT-before-reverse-full150-20261028.md).

## Best-result clarification and fresh progress — 28 October, 15:44 Vietnam

The best reviewed full NSCC measurement performed by us is 3.364622070 seconds per step (25940700), reproducing the organizer recipe. Our new full-length Iris hierarchy-order candidate is 21.229593669 seconds per step (2294234), 21.2371% below its same-allocation xyz control. The earlier 50-step Iris run 2294148 observed 21.112004724 seconds per step, but its shorter horizon is not a better full-length result. These platform and horizon categories must remain separate when answering which HPC result is best. No own NSCC tuning gain below 3.3646 is demonstrated.

Actual 2294262 remains RUNNING on iris005 at 15:44:11 Vietnam; xyz solver began 15:41:56 after source and copy checks passed. Its configured and effective cap are both 5,400 seconds. No completed new arm exists yet. One own allocation occupies the cap, so preserve it.
