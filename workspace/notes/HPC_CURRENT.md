# Current HPC/OpenFOAM handoff

Updated 2026-10-21T19:41:37.780529+00:00. This handoff belongs to the HPC session; GPU/Qwen belongs to the separate GPU chat. Follow [session ownership](SESSION_OWNERSHIP.md). Vietnamese chat only, English artifacts, no schedules or background Codex. Keep HPC_Task submission folders untouched until authorized reviewed packaging.

## Current result and next decision

**25907325.pbs101: F / exit 0**, same-node H→S pair, 128 ranks, 40 steps each. Hierarchical **14.7872238123 s/step**, Scotch **14.6402329083 s/step**: observed **0.994% reduction**, not a confirmed win. Scotch step 9 was **21.120703 s**, and the native timer asks for at least 50 samples while there are 39. All fixed-work/output/exit and unchanged-zero-field gates pass. Whole allocation **1373 s / 22 min 53 s**, estimated **48.817778 SU**. One-node screen only, no four-node score. [Full inspection and decision](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-method-pair128-20261021/RESULTS.md).

**Active: 25907688.pbs101: R** at 2026-10-21T19:40:48.044548+00:00, x1001c0s3b0n0, native NUMA-aware Scotch prep. Domains (8 16), synthetic 10:1 weights; 32 allocated CPUs / serial1 / 96 GB / no GPU / max 15 min / 8 SU. Fresh split plus complete mesh and processor-boundary graph gates, no solver claim. [Receipt and next steps](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-numa-scotch128-20261021/STATUS.md). Next collect terminal evidence and run its review.py; apply preregistered graph filter. One CPU allocation active, no blind retries or underfunded solver promotion.

## Accepted CPU baseline and new partition evidence

- **25905114: F / exit 0**, hierarchical (16 4 2), 128 ranks, x1001c2s5b1n0. Full mandatory initialization plus 40 steps. **14.9219814004 s/step**, p95 **15.074989 s/step**, Cd **0.4389323284**. Whole allocation **728 s / 12 min 8 s**, MaxRSS 121.7611 GiB, estimated 25.884444 SU. All source/native/work/output gates reviewed. [Baseline](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-solve-h128-20261021/STATUS.md).
- **25907236: F / exit 0**, native Scotch N128 preparation, **371 s / 6 min 11 s**, MaxRSS 31.9063 GiB, estimated 3.297778 SU. Complete official archive/member hashes and 65,334,765 cells verified. Maximum interface faces **42,141 vs 131,252** for hierarchical, with more neighbors and cell imbalance. No candidate solver speed claim yet. **768 control zero-time field hashes** sealed on compute. [Partition review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-scotch128-20261021/STATUS.md).
- CPU baseline placement lines interleaved; all ranks/core masks were seen but no reliable per-rank map. Pair derives an atomic JSON record per diagnostic rank. Neither establishes solver runtime migration, NUMA page placement or a bandwidth/cache/MPI bottleneck. Hardware counters and power were not collected.

## Budget and queue rules

CPU-only project **59000042**, separate from AI **59010042**. All seven recorded allocations terminal; estimates total **79.995556 SU**. Stale project amount report still shows Used 250.033 / Balance 29749.967 / In Doubt zero, delta **27.879 SU**; no individual posted charge is known. Locked reconciliation conservatively uses **81 SU consumed**, new outstanding prep maximum **8 SU**, total planning commitment **89 / 100 SU**, leaving **11 SU** unreserved. Timestamp/refresh limitations remain in the ledger evidence.

One own CPU allocation active at a time, combined own PBS jobs at most three. Check CPU queue and inspect AI only read-only for combined capacity. Parent lock/ledger: hpc-experiments/nscc-cpu-timing-probe-20261021/cpu-budget.lock and cpu-budget.json. Schema 2 checks consumed + retained outstanding + new maximum. Preserve queue positions and original requested maxima as provenance. No grant/cap increase, blind duplicates, AI changes or schedules.

## Verified access

Use **hpc-experiments/tools/nscc-cpu-ssh.sh** to reuse the authenticated CPU SSH master through the existing VPN. It uses verified CPU IP 10.103.72.110 with HostKeyAlias aspire2a.nscc.sg because namespace DNS fails. Login asp2a-login-nscc02. Run commands with bash -lc for modules/PBS. No new DUO or VPN reset needed at last successful check. Private state stays outside Git; preserve GPU access. CPU Python is 3.6.

Iris helper **hpc-experiments/tools/iris-interactive.sh** requires forced TTY with no remote command; gateway auto-jumps only interactively. Iris work root /global/exafs/users/rdmaworkshop30/apac2026/tripleu-hpc-20261021T1121. Do not touch other shared-account work or run optimized solver on login CPUs. **2293754** completed practice: 56 ranks / 40 steps, **21.9653538363 s/step**, Cd 0.4405543814. All stages pass; practice only, no score. [Iris evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/STATUS.md).

## History, rules and backup

[Full research reasoning and failures](../reports/hpc-openfoam-20261021/LOG.md), [plan](../reports/hpc-openfoam-20261021/PLAN.md), [rules](../reports/hpc-openfoam-20261021/RULES.md), [actual vs requested durations](../reports/hpc-openfoam-20261021/JOB_DURATIONS.md). Final scored performance requires four nodes / 150 steps; current results are one-node screening.

Preserve resetmodule failure 25904725, successful native timing gate 25904765, false filename-comment rejection 25904959 and successful derived mesh preparation 25905006. Ten historical October 9–10 attempts are sealed but are not accepted Basic solves. All numerical work remains fixed.

Checkpoint selected safe paths via /tmp/apac-hpc-checkpoint.py, serialized shared Git lock and path-scoped commit. Capture/verify/commit/push small milestones; do not include other worker changes. Existing archive and history stay intact. External artifact objects are not uploaded by Git. Routing uses CODEX_THREAD_ID and threads.name; old title-column lookup was incomplete. Shared CURRENT.md does not change track ownership.

## Historical queue checkpoint 2026-10-21T19:08:21.262668+00:00

Job 25907325.pbs101: Q. PBS comment: Not Running: would exceed overall limit on resource ncpus in queue qdev. This is scheduler capacity, not a running solver hang. Preserve queue position, allocation and reservation; no unchanged resubmit. The requested 29-minute walltime begins after start, not at submission.

## Native NUMA hypothesis now running

Native NUMA-aware Scotch N128: domains (8 16), weights (1 0.1), using verified diagnostic rank groups. Fresh split only, max 8 SU serial prep; terminal pair review and locked reconciliation passed before 25907688 submission. Includes reciprocal boundary-graph cross-group counts and hashes; no physical latency or speed claim. [Plan](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-numa-scotch128-20261021/PLAN.md).

HPC versus AI service units: [separate project balances](hpc-ai-service-units.md). CPU project 59000042 and AI project 59010042 do not share these balances; 100 SU is the initial HPC planning ceiling, not the 30,000-SU grant.
