# Current HPC/OpenFOAM handoff

Updated **3 November 2026, 11:34:15 Vietnam (UTC+7)**. This is the HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI remains separate. No background Codex, schedules or automatic MFA loops.

## Current result: no stable Iris gain

Job **2294671 FAILED 1:0**, 2,202 seconds / 56 allocated CPUs on iris001. The terminal snapshot was collected on 3 November; earlier running snapshots are historical. The first Scotch arm completed at **33.672468410 s/step** and the first xyz arm at **25.585999316 s/step**. The second xyz arm printed 20 steps / 19 timing intervals and **34.792584778 s/step**, but its command exited **124** at the 720-second per-arm cap. It is a failed arm, not a valid completed benchmark. The final Scotch arm never started. The root-set cap was too tight for successful finalization. There is no complete ABBA comparison and no new winner.

All **173 terminal artifacts** were transferred with byte/hash verification. The retained remote runtime still matches its frozen payload. Per-run source-after and final gates were not reached. Independent partial-run review is complete; preserve the failed raw evidence. [Full reviewed findings](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xyz20-scotch-screen-20261103/completed-2294671/RESULTS.md). [Terminal collection](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xyz20-scotch-screen-20261103/completed-2294671/collection.json).

The collector now tolerates an unstarted arm. Two bounded read-only transfers failed at pre-frame transport limits; a later transfer succeeded. A local shell reproduction and a remote 100,000-byte synthetic reply passed, so the proposed prompt-prefix explanation is **unconfirmed**. No bridge protocol change, credential reset or authentication claim was made.

## Actual follow-up and accounting

Initial preparation diagnostic **2294674** was accepted at 11:31:21 Vietnam and failed after one second before copying: our parser missed numactl's actual `interleavemask` key. Raw evidence and the original frozen payload are preserved. It is not evidence that interleaving is unsupported. Its 9.333333 CPU-hour maximum was retired and one conservative CPU-hour charged.

**Corrected job 2294675 accepted at 3 November 11:33:56 Vietnam**, **RUNNING on iris001 at 11:34:15**, elapsed 19 seconds. Exact observed output is covered by a regression fixture. The only runtime changes are the parser spelling and distinct job name. [Accepted R2 and next gates](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-numa-qualify-r2-20261103/STATUS.md).

This is a ten-minute, one-node, 56-CPU, zero-GPU **preparation-only NUMA diagnostic**. Four fresh copy/hash arms compare inherited and child-only interleaved memory policy in A/B/B/A order. It runs no solver and cannot establish a speed improvement. Exact source/copy inventory, actual distinct child policies, source-after seal and completed arms are runtime gates. The original 1,040 inputs and separately reviewed 13 ancillary files are both pinned. [Mechanism rationale](../reports/hpc-next-directions-20261103/MECHANISMS.md).

2294671 cost **34.253333 allocated CPU-hours**, conservatively 35; 2294674 cost **0.015556**, conservatively 1. Both maxima retired once. Ledger now **985 consumed + 9.333333 reserved**, unchanged agent-selected stage **1,009**, leaving **14.666667 unreserved CPU-hours**. These are local planning CPU-hours, not billed SU. The current owned allocation cap is occupied at the dated snapshot. Preserve this job; collect and reconcile once terminal before any further admission. No NSCC/AI transfer.

## Reference and access boundaries

No own stable scored-platform gain is established. Best reviewed NSCC **3.364622070 s/step** is our organizer-recipe reproduction; organizer **3.210832548** and teammate Gadi **2.079045460** are separate references. Iris results cannot forecast a Gadi win. Own historical Iris **21.229593669 s/step** is an observed run whose advantage was not stable under reversal.

Latest VPN retry **3 November 00:06:30–00:06:34 Vietnam** returned gateway Authentication failed; 00:07:58 path check remained NAMESPACE_UNAVAILABLE. No new VPN attempt in this status turn. No Gadi identity/project supplied. [Safe VPN record](nscc-vpn-retry-20261103.md).

Unchanged xzy, graph-placement, collated-I/O and topology-weight-only branches are closed after contradictory or negative checks. [Earlier detailed handoff, explicitly historical](history/HPC_CURRENT-before-xyz20-terminal-20261103.md). AI payloads, queues, budgets and submission materials remain unchanged.
