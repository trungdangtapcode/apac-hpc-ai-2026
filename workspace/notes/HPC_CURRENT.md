# Current HPC/OpenFOAM handoff

Updated 2026-10-23T18:18:38.315145+00:00. Session 01a1508d-26b0-7dd0-9dc1-f217ce0aff40 owns HPC/OpenFOAM. AI/Qwen remains with its separate worker. English artifacts, Vietnamese chat. No background Codex, autopilot or schedules.

## Live checkpoint

The whitelisted PBS check at **2026-10-23T18:15:29.209000Z** shows:

| Job | State | Purpose and interpretation |
|---|---|---|
| 25940700.pbs101 | Q/q5 |Four-node default Scotch confirmation, 512 ranks, 150 steps; insufficient node_pool. No new result. Preserve queue position. |
| 25943865.pbs101 | H/qdev |New four-rank actual MPI_COMM_WORLD reorder preflight, afterany 25940700. Expected dependency hold, not a failed probe. No runtime result. |
| 25947168.pbs101 | H/q5 |Conditional four-node/512-rank host/core/NUMA placement qualification; afterok both earlier jobs. No solver, result or mapping claim yet. |

[New receipt, frozen source and checks](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-mpi-reorder-preflight-20261023/STATUS.md). The preflight requests four CPUs, 4 GB, no GPU and 3 minutes; identity and nonidentity orders share method 3, PALS thread binding, thread controls, binary and allocation. It compiles only on the allocated node. Actual MPI_Comm_rank plus host/affinity/sysfs core identity is authoritative; PMI_RANK alone cannot prove library-level reordering. Do not change either frozen payload or resubmit either intent.

## Findings and next hypothesis

The lowest retained native four-node mean remains **3.677906731 s/step**, default Scotch 128 ranks/node, job 25921488, 149 timed samples / 150 steps. H128 is 3.819929017 s/step. These are native observations, not accepted official scores or proof of a stable gain. Old final PBS history and some submission/return/field/core evidence are missing. [Six-run review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md).

The [new timing audit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-stability-audit-20261023/RESULTS.md) inspects all 894 samples, the 13 active probe outputs per case and timer callback order. No sparse scheduled field-output event uniquely explains the spikes. Maxima occur at Time 35–130. Rounded wall-clock deltas exceed reported process ExecutionTime deltas at those events, but do not diagnose MPI, storage or CPU scheduling. All samples remain in Average; missing per-rank/hardware data are not zero.

The [new offline four-host mapping](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/rank-placement-512-screen-20261023/RESULTS.md) keeps the 512 partitions unchanged and reduces logical crossing faces **337,324 → 261,110 (−22.5937%)**. This saves 2.6038% of all 2,927,022 interface faces. Maximum per-host external-face proxy 214,160 → 140,111; hypothetical cell-total range grows 0.215%→0.702%. All groups have 128 ranks; rank 0 remains first. Root independently recomputed cuts/matrices/balance and parser guards. The boundary graph matches the sealed native decomposition totals, but was collected later and does not prove original mesh identity or historical physical placement. This is not a solver speedup. Installed Cray MPICH 8.1.15 documentation supports method 3 and custom rank files; actual behavior remains the pending cheap preflight.

**Next:** review 25940700's full source/mesh/rank/core/stage/field/timing/force and final PBS evidence, plus 25943865's C build, linked MPI library, returns, actual identity/candidate mapping and scheduler completion. A passing one-node preflight does not qualify 512 ranks/four hosts. A future larger mapping must validate the fresh adjacency against the selecting graph, verify actual MPI_COMM_WORLD placement, use an identity control and preserve all 150 steps. Check budget/capacity before new spending. Close unchanged losing branches rather than repeat them blindly.

The NUMA decomposition remains closed after its 3.4416% slowdown. Earlier N128 placement graph 4.5741% and the two-node H/S pair remain unsubmitted, lower priority; neither is a new performance result.

## Budget and access

CPU project 59000042 is separate from AI 59010042. The owner-approved cumulative ceiling remains **5,000 SU**. After the two preflight reservations (6.4 + 25.6 SU), consumed allowance plus all maxima is **4,897.533333 SU**, leaving **102.466667 SU**. Shared unknown maxima 2,389.333333 SU and older own unknown costs are retained, with deliberate possible double counting. The four-rank request's nominal maximum 0.2 SU is not its conservative reservation or a posted charge. [Locked checks](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/cpu-continuation-20261023/checkpoint-20261023T1537/budget-check.json) precede the new receipt; the ledger and post-submit summary record the later reservation.

Last queried project report: Used 2,269.938 / Balance 27,730.062 / In Doubt 0, with the report's own dated refresh. The detailed 21–23 October estimate 579.91 SU carries an explicit incomplete/inaccurate disclaimer and no per-job records; it cannot retire old unknown maxima. One active CPU allocation and combined PBS cap 3 remain. The dependent preflight guarantees no overlap with the existing parent. The earlier four-rank pre-submit CPU queue had only the parent. The later 512-rank pre-submit CPU queue had those two prerequisite jobs and the read-only AI PBS queue was empty; the admitted combined count is three. Do not infer a fresh queue from this dated snapshot.

VPN and CPU SSH are functional through the cpu-r3 helper at the last live check. Preserve existing tunnel, private caches and AI connection. The failed 14:55 authentication and successful 15:04:45 recovery are [recorded](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261023T1504/REPORT.md); their cause/phone-side approval/exact lifetime were not established. No authentication/session state is archived.

## Presentation, learning and preservation

The authorized [submission update](../submission-review/hpc-update-20261023/README.md) remains 40 slides: 32 preserved AI plus 8 HPC (20%). It contains reviewed CPU scripts and native logs, with a dated 15:06 slide snapshot. No new unmeasured graph gain is inserted as a solver result; no organizer upload occurred. [Learning guide](../reports/hpc-research-journey-20261023/README.md), [whole journey](../reports/hpc-research-journey-20261023/JOURNEY.md), [3–4 minute presenter section](../reports/hpc-research-journey-20261023/TALK_TRACK.md) and [new research entry](../reports/research-journey-20261019/journal/entries/20261023-hpc-four-node-placement.md) explain the reasoning.

The [preceding handoff](history/HPC_CURRENT-before-four-node-placement-20261023T1553.md) is historical. Small explicit safe checkpoints preserve raw failures, all measurements, hypotheses and receipts. GitHub holds Git files/manifests; external large objects still need an off-host copy.

**Later queue observation:** 2026-10-23T17:49:37.514429Z still parent Q/q5 and preflight H/qdev, unchanged dependencies and no runtime result. A separate offline check of within-host logical NUMA trade-offs is in progress; no new spending has been authorized or made for it.

**Within-host refinement:** [New report](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/rank-placement-512-numa-screen-20261023/RESULTS.md) keeps the four host memberships and 261,110 crossing faces unchanged. Same-host cross-NUMA faces improve 1,097,554 → 732,712 (−33.24%); the original contiguous control was 710,081, so the refined proxy is still 3.19% worse on this category. All 512 ranks and 4 × 128 / 32 × 16 group sizes pass independent checks. Eight domains per host remain a logical assumption, not observed four-node topology. [Learning figure](../reports/hpc-research-journey-20261023/figures/placement-tradeoff.png). Conditional 512-rank qualification **25947168** is now H/q5 with afterok prerequisites on both existing jobs; its maximum 25.6 SU is reserved. [Receipt and qualification limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-mpi-placement512-preflight-20261023/STATUS.md).

**Admission at the latest checkpoint:** all three combined PBS slots are occupied by these CPU jobs; the read-only AI PBS queue was empty immediately before the new submission. Holds count toward the cap. No further qsub until a fresh combined count permits it. This does not change AI ownership, payloads or its separate budget. The refined mapping is the preferred graph candidate, conditional on actual qualification; no full solver test or performance gain is inferred.
