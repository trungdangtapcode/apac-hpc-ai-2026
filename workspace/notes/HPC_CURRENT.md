# Current HPC/OpenFOAM handoff

Updated 2026-10-21T19:07:46.983112+00:00. This handoff belongs to the HPC session; GPU/Qwen belongs to the separate GPU chat. Follow [session ownership](SESSION_OWNERSHIP.md). Vietnamese chat only, English artifacts, no schedules or background Codex. Keep HPC_Task submission folders untouched until authorized reviewed packaging.

## Active experiment

**25907325.pbs101: Q** at 2026-10-21T19:06:52.767507+00:00, qdev, ASPIRE-2A CPU project **59000042**. One exclusive CPU node / 128 MPI / 440 GB / no GPU, maximum **29 minutes after starting**. Candidate mandatory initialization, then hierarchical and default Scotch 40-step solves on the same node. Queue waiting is separate.

[Exact plan, receipt, gates and limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-method-pair128-20261021/STATUS.md). Next collect and review terminal evidence using tools/collect_cpu_probe.py and the experiment review.py. Never overwrite collected terminal evidence. Inspect both averages/tails/Cd, fixed iterations, errors, phase costs, placement and unchanged zero-time fields. One ordered pair is not repeated proof or a four-node score. Do not modify submitted payloads or rerun unchanged.

## Accepted CPU baseline and new partition evidence

- **25905114: F / exit 0**, hierarchical (16 4 2), 128 ranks, x1001c2s5b1n0. Full mandatory initialization plus 40 steps. **14.9219814004 s/step**, p95 **15.074989 s/step**, Cd **0.4389323284**. Whole allocation **728 s / 12 min 8 s**, MaxRSS 121.7611 GiB, estimated 25.884444 SU. All source/native/work/output gates reviewed. [Baseline](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-solve-h128-20261021/STATUS.md).
- **25907236: F / exit 0**, native Scotch N128 preparation, **371 s / 6 min 11 s**, MaxRSS 31.9063 GiB, estimated 3.297778 SU. Complete official archive/member hashes and 65,334,765 cells verified. Maximum interface faces **42,141 vs 131,252** for hierarchical, with more neighbors and cell imbalance. No candidate solver speed claim yet. **768 control zero-time field hashes** sealed on compute. [Partition review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-scotch128-20261021/STATUS.md).
- CPU baseline placement lines interleaved; all ranks/core masks were seen but no reliable per-rank map. Pair derives an atomic JSON record per diagnostic rank. Neither establishes solver runtime migration, NUMA page placement or a bandwidth/cache/MPI bottleneck. Hardware counters and power were not collected.

## Budget and queue rules

CPU-only project **59000042** is separate from AI **59010042**. Latest amount report Used **250.033**, Balance **29749.967**, In Doubt **0 SU**. Site report timestamp is inconsistent; individual charges are not known. First five terminal allocations estimate **27.880 SU**, consistent with amount delta **27.879 SU**; conservative consumed ceiling **29 SU**. Scotch prep's terminal 8-SU maximum remains retained pending reconciliation.

Current total planning commitment **98.866667 / 100 SU** includes the active pair maximum **61.866667 SU**. Do not raise the cap or infer spend authority from the 30,000-SU grant. One own CPU allocation active at a time; combined own PBS jobs at most three. Check the actual CPU queue and inspect AI only read-only for combined capacity. Parent lock/ledger: hpc-experiments/nscc-cpu-timing-probe-20261021/cpu-budget.lock and cpu-budget.json. Schema 2 enforces consumed ceiling + outstanding retained reservations + new maximum. Preserve pending positions; no blind duplicate/retry. Reconcile actual terminal usage before planning further work; further repetitions may not fit this wave.

## Verified access

Use **hpc-experiments/tools/nscc-cpu-ssh.sh** to reuse the authenticated CPU SSH master through the existing VPN. It uses verified CPU IP 10.103.72.110 with HostKeyAlias aspire2a.nscc.sg because namespace DNS fails. Login asp2a-login-nscc02. Run commands with bash -lc for modules/PBS. No new DUO or VPN reset needed at last successful check. Private state stays outside Git; preserve GPU access. CPU Python is 3.6.

Iris helper **hpc-experiments/tools/iris-interactive.sh** requires forced TTY with no remote command; gateway auto-jumps only interactively. Iris work root /global/exafs/users/rdmaworkshop30/apac2026/tripleu-hpc-20261021T1121. Do not touch other shared-account work or run optimized solver on login CPUs. **2293754** completed practice: 56 ranks / 40 steps, **21.9653538363 s/step**, Cd 0.4405543814. All stages pass; practice only, no score. [Iris evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/STATUS.md).

## History, rules and backup

[Full research reasoning and failures](../reports/hpc-openfoam-20261021/LOG.md), [plan](../reports/hpc-openfoam-20261021/PLAN.md), [rules](../reports/hpc-openfoam-20261021/RULES.md), [actual vs requested durations](../reports/hpc-openfoam-20261021/JOB_DURATIONS.md). Final scored performance requires four nodes / 150 steps; current results are one-node screening.

Preserve resetmodule failure 25904725, successful native timing gate 25904765, false filename-comment rejection 25904959 and successful derived mesh preparation 25905006. Ten historical October 9–10 attempts are sealed but are not accepted Basic solves. All numerical work remains fixed.

Checkpoint selected safe paths via /tmp/apac-hpc-checkpoint.py, serialized shared Git lock and path-scoped commit. Capture/verify/commit/push small milestones; do not include other worker changes. Existing archive and history stay intact. External artifact objects are not uploaded by Git. Routing uses CODEX_THREAD_ID and threads.name; old title-column lookup was incomplete. Shared CURRENT.md does not change track ownership.
