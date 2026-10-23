# Current HPC/OpenFOAM handoff

Updated 2026-10-23T19:09:09.900891+00:00. Session 01a1508d-26b0-7dd0-9dc1-f217ce0aff40 owns HPC/OpenFOAM; AI/Qwen stays with its separate worker. English artifacts, Vietnamese chat. No background Codex, autopilot or schedules.

## Actual queue and immediate priority

The read-only PBS snapshot at **23 October 18:54:23 UTC** shows:

| Job | State | Purpose |
|---|---|---|
| 25940700.pbs101 | Q/q5, insufficient node_pool |Independent four-node default Scotch confirmation, 512 ranks, 150 steps. No new result. |
| 25943865.pbs101 | H/qdev, afterany 25940700 |Three-minute four-rank actual MPI-world reorder preflight. No runtime result. |
| 25947168.pbs101 | H/q5, afterok both earlier jobs |Three-minute 512-rank/four-host physical core/NUMA mapping qualification, 32 GB/node. No solver. |

Preserve all three intents, payloads and queue positions. The combined PBS cap 3 is full in the recorded admission; holds count. One active CPU allocation is maintained by dependencies. Check both CPU and AI queues before any later admission. [512-rank receipt/source/status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-mpi-placement512-preflight-20261023/STATUS.md), [four-rank source/status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-mpi-reorder-preflight-20261023/STATUS.md).

[The scheduler audit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/queue-readiness-20261023/README.md) found 182 pool nodes marked free but none with all 128 CPUs unassigned, despite 7,528 free CPU slots spread across fragments. This supports the lack of four whole 128-core chunks, not a scheduler fault or ETA. Do not equate separate aggregate zero-CPU/down counts; their identity was not established. No cancellation, qalter, extra job or new reservation occurred in this continuation.

## Measurements and proxy candidates

The lowest retained native four-node mean stays **3.677906731 s/step**, Scotch 128 ranks/node, job 25921488, 149 timed samples from 150 steps. H128 is 3.819929017 s/step. Missing old terminal PBS and submitted-payload evidence prevents us claiming an accepted score; these are native observations. [Six-run review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md). The [894-sample audit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-stability-audit-20261023/RESULTS.md) found no sparse output event uniquely explaining the slow steps; master-process CPU/wall deltas do not diagnose a hardware or MPI cause.

All mappings below use the same 512-rank graph. Face counts are logical proxies, not bytes, traffic or speedup:

| Mapping | Cross-host faces | Same-host cross-NUMA faces | Host cell range / mean |
|---|---:|---:|---:|
| Original contiguous control | 337,324 | 710,081 | 0.215% |
| Aggressive two-level | 261,110 | 732,712 | 0.702% |
| New balanced whole-group option | 283,819 | 710,003 | 0.627% |

The [new balanced screen](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/rank-placement-512-pareto-screen-20261023/RESULTS.md) holds all 32 refined 16-rank groups intact and moves eight whole groups per host. Fixed intergroup faces 993,822 imply a feasible host-cut interval 283,741–337,324 to avoid either original face-category regression. Seed 2026 / 500,000 proposals found 283,819 / 710,003; root full-edge checks and isolated replay reproduce the exact mapping. Its host reduction is 15.8616%; the NUMA difference is only 78 faces (0.010985%). This is not improvement on every metric: cell balance remains worse than original, and the aggressive option has a lower host cut. Retain both, not a newly declared runtime winner. [Figure](../reports/hpc-research-journey-20261023/figures/placement-options.png).

The queued 512-rank probe is frozen with the older aggressive mapping. Do not retarget it to the balanced input. A pass qualifies that exact allocation/mapping; the new balanced option remains unsubmitted. Both require fresh adjacency identity and actual MPI_COMM_WORLD host/core/NUMA proof before any future full run. Eight domains per host is still an unverified four-node topology assumption, and page residency/solver-time affinity are not measured.

## Next decision, budget and access

Review 25940700's complete source/mesh/rank/core/stage/field/timer/force checks and final PBS resources/exit, then the two preflights' actual MPI mapping and command returns. A later full comparison must hold method 3, thread binding, transport and all numerical work constant between identity-control and candidate. The current default-launch confirmation is not automatically a matched control for additional runtime flags. Preserve all 150 steps and 149 samples. Do not spend on tiny improvements to the 78-face proxy boundary before runtime evidence, or launch both candidates merely to fill queues.

The owner-approved CPU campaign ceiling remains **5,000 SU** on project 59000042, separate from AI 59010042. The unchanged ledger has **4,897.533333 SU** committed including consumed allowance and all maxima; **102.466667 SU** remains. Unknown shared maxima 2,389.333333 SU and older own unknown costs remain, with deliberate possible double counting. Four-rank reservation 6.4 SU is conservative versus its nominal 0.2 SU request; the 512-rank reservation is 25.6 SU. These are not posted charges. Fresh locked budget/rate/balance and combined-cap checks are required before further spending; the site's larger grant does not increase this ceiling.

VPN/CPU SSH work through cpu-r3 at the latest checks. Preserve healthy existing sessions and private state; do not reset the separate AI connection. No credentials/session material is retained in research files. Scope HPC discovery to hpc-experiments; unrelated Qwen runtime bind mounts may deny traversal and must not be repaired or swept into this work.

## Learning, presentation and archive

[Learning guide](../reports/hpc-research-journey-20261023/README.md), [whole journey](../reports/hpc-research-journey-20261023/JOURNEY.md), [short presenter script](../reports/hpc-research-journey-20261023/TALK_TRACK.md), [new reasoning entry](../reports/research-journey-20261019/journal/entries/20261023-hpc-balanced-placement-and-queue.md). The prepared submission package remains 40 slides, 32 AI / 8 HPC; no unmeasured proxy is promoted into a solver result or organizer upload. [Delivery](../submission-review/hpc-update-20261023/README.md).

The [previous handoff](history/HPC_CURRENT-before-balanced-placement-20261023T1910.md) is historical. Capture safe source/data/reviews in small commits and push to the authorized private origin; large external historical artifacts still need their off-host copy.

**Latest verified queue:** 2026-10-23T19:24:06.430522Z still 25940700 Q/q5 (node_pool), 25943865 H/qdev and 25947168 H/q5 on their original dependencies. No new solver/MPI result or spending change. Keep the existing queue positions; further proxy polishing is lower priority than the queued runtime evidence. [Latest raw state](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/queue-readiness-20261023/jobs-20261023T1924.json). The older node-capacity histogram remains a dated 19:12 snapshot.
