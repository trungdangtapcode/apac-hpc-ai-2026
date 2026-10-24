# Current HPC/OpenFOAM handoff

Updated 24 October 2026. Session 01a1508d-26b0-7dd0-9dc1-f217ce0aff40 owns HPC only. The AI worker owns its payloads and queues. English artifacts, Vietnamese chat. No background Codex, schedules or autopilot.

## Current CPU authorization — supersedes earlier 5,000-SU limit

On24October the owner explicitly authorized using the remaining CPU grant before30October. The new cumulative campaign ceiling is **29,777.846SU** (30,000grant minus retained222.154pre-campaign baseline). After the known diagnostic reconciliation, commitment **4,706.2SU**, headroom **25,071.646SU**. Unknown maxima remain. [Full decision, deadline distinction and research sequence](cpu-campaign-before-oct30-20261024.md). One active CPU allocation / combined own PBS cap3 remain; no automation or AI changes.

Job **25956623 is terminal Exit1**. All512 captured records show one-CPU affinity before MPI_Init expanding to CPUs0–255 afterward. Core/NUMA lookups were skipped, not failed. No candidate ran; launch shutdown reached its bounded timeout. Investigate a supported binding control before qualification or solver A/B. [Full collected review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/diagnostic-25956623/RESULTS.md). Later sections retain dated historical budget/queue snapshots.

## New verified native best and completed jobs

[24 October collection and independent replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/RESULTS.md) verifies 126 retained files and terminal PBS outcomes:

| Job | Result | Meaning |
|---|---|---|
| 25940700 | F / Exit 0, 18:57 allocation wall | Four-node Scotch repeat: **3.364622070 s/step**, 150 steps / 149 samples. |
| 25943865 | F / Exit 0, 7 seconds | Actual four-rank method-3 reorder and physical-slot check passed. |
| 25947168 | F / Exit 1, 9 seconds | All 512 ranks failed the combined identity topology gate. Candidate never launched. |

The repeat's mean is 8.52% lower than the previous 3.677906731 s/step, median 0.51% lower, p95 3.72% higher. The prior 35.88-second maximum did not recur; the new maximum is 5.90 seconds. This is a separate-allocation repeat with the same intended configuration, not a measured placement optimization or organizer-confirmed score. All timings remain included. Native recommended sample count 101, no short-sample warning in this repeat. Zero-time field seals match across 3,072 files; source, initialization, rank/core and numerical-work checks pass. Startup binding is not solver-time residency evidence.

## Immediate improvement

The failing C probe combined singleton affinity, physical core and NUMA reads into one message. Its exact failing subcheck is unknown. A separately versioned diagnostic was submitted once as **25956623.pbs101** under `nscc-cpu-mpi-placement512-diagnostic-20261024`: preserve the aggressive mapping and all topology acceptance gates, record affinity before/after MPI_Init and each lookup's status, then make a collective failure decision so all ranks retain diagnostics. Local synthetic MPI tests pass the singleton case and reject a two-CPU mask; they do not prove a cluster fix. Preserve the failed payload and raw logs. No solver A/B before actual qualification.

The new balanced whole-group mapping remains offline: host cut 283,819 versus original 337,324, same-host cross-NUMA 710,003 versus 710,081. These are face-count proxies, not bytes or speedup; host cell balance is worse than original. Keep both aggressive and balanced candidates. [Previous detailed reasoning](history/HPC_CURRENT-before-completed-review-20261024T0313.md), [balanced search](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/rank-placement-512-pareto-screen-20261023/RESULTS.md).

A future solver comparison must use identical method-3 identity and candidate launch flags, binding, transport, decomposition and initial fields. The successful default-launch repeat is not automatically that matched control. A single allocation with sequential arms is preferable but order effects remain; budget must permit it.

## Historical 5,000-SU budget snapshot, access and records

The owner-approved CPU campaign ceiling is **5,000 SU** on CPU project 59000042, separate from AI 59010042. [Locked reconciliation](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/budget-reconciliation.json) retires only the three now-known terminal maxima, adds a rounded 164-SU conservative allowance, preserves all shared/older unknown maxima and leaves **4,688.2 SU committed / 311.8 SU headroom** before new admission. The new 25.6-SU diagnostic reservation brings commitment to **4,713.8 SU / 286.2 SU headroom**. This is not posted billing. Check a fresh site report/rate, own CPU and AI queues under the CPU budget lock before qsub. One active CPU allocation; combined PBS cap three including holds. All three old jobs are terminal in the 03:04–03:05 UTC queries, not still queued.

VPN and CPU SSH via cpu-r3 worked on 24 October; preserve existing private state and the separate AI connection. Read-only scheduler observation showed three whole unassigned free CPU nodes, not an ETA or full eligibility proof. Scope searches to HPC; never traverse or repair Qwen runtime bind mounts.

[Learning guide](../reports/hpc-research-journey-20261023/README.md), [journal](../reports/research-journey-20261019/journal/README.md). The existing 40-slide combined submission (32 AI / 8 HPC) remains its dated 23 October snapshot; no changes or organizer upload in this review. Capture, verify, commit and push small explicit checkpoints. External historical large objects still need separate off-host backup.

**Latest owned CPU job:** 24 October 03:12:23 UTC, 25956623 Q/q5, insufficient node_pool. Both own CPU and AI PBS queues were empty immediately before admission; no older intent was resubmitted. [Receipt, frozen source and status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-mpi-placement512-diagnostic-20261024/STATUS.md). The three previous jobs are terminal.

**CPU balance clarification, 24 October 03:16:46 UTC:** live `myprojects` query displays account balance **27,730.062 SU** (30,000 grant, 2,269.938 used, zero in doubt; site report labeled 23 October 23:59:34). This can lag recent work. The **286.2 SU** figure above is internal headroom under the authorized **5,000-SU campaign**, not the site's remaining grant. The own diagnostic is now **R/q5**. No budget/ledger changes. [Explanation](cpu-su-balance-20261024.md).
