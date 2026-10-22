# Current HPC/OpenFOAM handoff

Updated 2026-10-22T14:16:12.096147+00:00. This is the HPC session; GPU/Qwen remains owned by its separate worker. English artifacts, Vietnamese chat. No background Codex or schedules.

## Current access checkpoint — 22 October

VPN currently unavailable. Fresh collection of 25907753 and 25907772 stopped before SSH/PBS; current scheduler states and new results are **unknown**, not failed or completed by inference. A brief separate VPN client later exited; exact cause/lifetime is not established. Preserve private cache and all existing reservations. Owner asked whether DUO approval is available; no new authentication was initiated by the HPC worker. [Safe access evidence and next actions](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-check-20261022/REPORT.md).

Three-cut review.py and H/S256 deploy-submit.py/review.py are implemented and root-reviewed. The 80-step semantic validator accepts both immutable organizer reference logs and rejects changed fixed work. These are parser qualifications, not new timing results. H/S256 remains ready **but not submitted**, awaiting actual prep review and fresh budget/queue checks. [Pre-submission review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-method-pair256-20261021/PRE_SUBMIT_REVIEW.md).

NUMA metadata correction is dated separately; actual frozen payload/input hashes agree. [Correction](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-numa-scotch128-20261021/PROVENANCE_CORRECTION.md). All reported measurements below remain historical until a fresh review.

## Historical pipeline snapshot — verified 21 October

| Job | State | Work | Maximum reserved SU |
|---|---|---|---:|
| 25907753.pbs101 | R | One-node 40+40-step default versus NUMA Scotch pair, 128 ranks, 440 GB | 61.866667 |
| 25907772.pbs101 | H: afterok parent | Three serial two-node / N256 decompositions, 32 allocated CPUs, 96 GB | 24 |

Parent runs on x1001c7s5b1n0. Follower's Hold_Types=d is intentional: PBS dependency proof matches afterok/beforeok. Preserve queue position and frozen payloads. One own CPU allocation active at a time, combined own PBS cap three including AI. CPU dependency jobs are ordinary batch work, not background Codex. Read actual scheduler state before reporting live status.

- [Full solver pair and reviewer](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-scotch-numa-pair128-20261021/STATUS.md). Validate physical cores/NUMA grouping, all numerical work, timers, Cd, tails, zero-field hashes and terminal resource accounting. Its legacy CPU_HS_PAIR_PASS marker does not define methods; accepted role hashes define default/NUMA Scotch.
- [Three N256 cuts and dependency proof](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-three-cuts256-20261021/STATUS.md). Hierarchical (16 8 2), default Scotch, node-aware Scotch (2 128), synthetic weights 10:1. Next inspect all partition/graph gates and prepare matched two-node H/S 80-step timing. Do not assume one-node gains scale.

## Accepted evidence

- **25905114**: first native ASPIRE CPU hierarchical baseline, full init + 40 steps, **14.9219814004 s/step**, Cd **0.4389323284**, 728 s allocation, estimated 25.884444 SU. All fixed-work/output gates pass.
- **25907325**: matched H→S pair on one node, H **14.7872238123**, S **14.6402329083 s/step**, observed **0.994% saving**, not stable proof. S step 9 = **21.120703 s**, native sample confidence warning (50 needed vs 39). Cd H **0.4389323284**, S **0.4359888360**; both native work/output/hash gates pass. **1373 s**, estimated 48.817778 SU. [Detailed inspection](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-method-pair128-20261021/RESULTS.md).
- **25907688**: NUMA tree (8 16) prep passes all preregistered graph filters. Cross-group faces **332,157 vs 371,658** (−10.6283%), total faces **1,570,175 vs 1,549,377** (+1.3423%), cell max excess 1.0055%, max neighbors 32 vs 35. **385 s**, estimated 3.422222 SU. No NUMA solver gain yet. [Native result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-numa-scotch128-20261021/RESULTS.md).
- **2293754 Iris practice**: 56 MPI/40 steps, 21.9653538363 s/step, Cd 0.4405543814, full chain passes. Practice only, no score. First CPU diagnostics and all failures remain linked in the log.

These are one-node results, not the scored four-node/150-step result. Atomic diagnostic rank maps establish pre-solve core affinity and grouping, not actual NUMA page residency, solve-time migration, measured MPI waits/traffic or a bottleneck. Hardware counters, bandwidth and power were not collected. Keep all outliers in native Average.

## Current CPU budget

Owner explicitly requested expanded research/submissions after learning balances are separate. New bounded **1,000-SU cumulative CPU ceiling**; original 100-SU first wave is historical, preserved in ledger ceiling_history. [Expanded plan](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/cpu-continuation-20261021/PLAN.md).

All first eight allocations terminal: estimates **83.417778 SU**, conservative consumed **85 SU**. Outstanding maxima **85.866667 SU**, total commitment **170.866667 / 1,000 SU**. These are planning commitments, not posted charges. CPU project **59000042**, grant 30,000 SU, is separate from AI **59010042**. Stale project usage display still reports Used 250.033 / Balance 29749.967 / In Doubt 0; do not call that current actual wave usage. Individual posted billing and refresh chronology remain unresolved. [SU explanation](hpc-ai-service-units.md).

Parent lock/ledger: hpc-experiments/nscc-cpu-timing-probe-20261021/cpu-budget.lock and cpu-budget.json. Always check consumed + retained maxima + new request against current ceiling, fresh project rate/balance and combined own PBS jobs. Use tools/reconcile_cpu_budget.py only with all recorded jobs terminal/own queue empty. Preserve original requested maxima and raw failures; no blind retries or prepaid double subtraction. No AI ledger changes.

## Access and queue correction

Reuse **hpc-experiments/tools/nscc-cpu-ssh.sh**, authenticated CPU master through existing VPN, CPU IP 10.103.72.110 with HostKeyAlias aspire2a.nscc.sg. Namespace CPU DNS failed previously. CPU login asp2a-login-nscc02, Python 3.6; bash -lc restores PBS/modules. Do not reset VPN/AI master or capture authentication state.

**normal is a routing queue. qdev max per job is 128 cores and aggregate 256.** Larger 256/512-core normal requests can route elsewhere, e.g. q5 max 2048. Earlier qdev-only inference was too broad. Actual larger-job route/access remains to verify. [Verified safe queue snapshot and correction](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/cpu-continuation-20261021/QUEUE_POLICY.md).

Iris helper requires forced TTY and no remote command so gateway auto-jumps to login01. Work root /global/exafs/users/rdmaworkshop30/apac2026/tripleu-hpc-20261021T1121. Do not touch other shared-account work or run optimized solvers on login CPUs.

## Research history and backups

[Full reasoning, attempts and corrections](../reports/hpc-openfoam-20261021/LOG.md), [rules](../reports/hpc-openfoam-20261021/RULES.md), [durations](../reports/hpc-openfoam-20261021/JOB_DURATIONS.md). Iris timing/source replay, resetmodule failure, metadata-comment false rejection, all ten older CPU attempts and local errno7 transport failure remain preserved. No HPC result is invented for submission materials.

Edit active sources once; selected safe capture/verify/commit/push via /tmp/apac-hpc-checkpoint.py uses serialized shared Git lock and path-scoped commit. Never sweep GPU worker changes or rebuild the archive. External artifact objects are not uploaded by Git. End each milestone with backup; preserve the existing audit trail and actual commit dates.
