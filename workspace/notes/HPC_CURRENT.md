# Current HPC/OpenFOAM handoff

Updated **3 November 2026, 11:32 Vietnam (UTC+7)**. This is the HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI remains separate. No background Codex, schedules or automatic MFA loops.

## Current result: no stable Iris gain

Job **2294671 FAILED 1:0**, 2,202 seconds / 56 allocated CPUs on iris001. The terminal snapshot was collected on 3 November; earlier running snapshots are historical. The first Scotch arm completed at **33.672468410 s/step** and the first xyz arm at **25.585999316 s/step**. The second xyz arm printed 20 steps / 19 timing intervals and **34.792584778 s/step**, but its command exited **124** at the 720-second per-arm cap. It is a failed arm, not a valid completed benchmark. The final Scotch arm never started. The root-set cap was too tight for successful finalization. There is no complete ABBA comparison and no new winner.

All **173 terminal artifacts** were transferred with byte/hash verification. The retained remote runtime still matches its frozen payload. Per-run source-after and final gates were not reached. Independent partial-run review is complete; preserve the failed raw evidence. [Full reviewed findings](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xyz20-scotch-screen-20261103/completed-2294671/RESULTS.md). [Terminal collection](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xyz20-scotch-screen-20261103/completed-2294671/collection.json).

The collector now tolerates an unstarted arm. Two bounded read-only transfers failed at pre-frame transport limits; a later transfer succeeded. A local shell reproduction and a remote 100,000-byte synthetic reply passed, so the proposed prompt-prefix explanation is **unconfirmed**. No bridge protocol change, credential reset or authentication claim was made.

## Next measurement and accounting

The ten-minute **preparation-only NUMA diagnostic** was accepted as **2294674 at 11:31:21 Vietnam**, then failed after one allocated second before any copying: the parser missed numactl’s actual `interleavemask` key. This is our parser defect, not unsupported policy. Its frozen payload and raw error are preserved. A derived corrected retry is being prepared. Intended one-node / 56-CPU / zero-GPU experiment: compare inherited memory policy with child-only interleaving during fresh case copy/hash in A/B/B/A order. This checks whether preparation changes whole-node memory counters; it runs no solver and cannot establish a speed improvement. Root code review and offline checks pass. Compute-side source/copy inventory and actual child policy remain runtime gates. [Mechanism rationale](../reports/hpc-next-directions-20261103/MECHANISMS.md).

The terminal cost was reconciled once from sacct: **34.253333 allocated CPU-hours**, rounded conservatively to **35**. After the diagnostic parser failure adds one conservative CPU-hour, ledger now **985 consumed + 0 reserved**, unchanged agent-selected stage **1,009**; **24 CPU-hours** remain. These are local planning CPU-hours, not billed SU. Fresh queue, frozen payload and locked admission still required before submitting the new maximum 9.333333 CPU-hour diagnostic.

## Reference and access boundaries

No own stable scored-platform gain is established. Best reviewed NSCC **3.364622070 s/step** is our organizer-recipe reproduction; organizer **3.210832548** and teammate Gadi **2.079045460** are separate references. Iris results cannot forecast a Gadi win. Own historical Iris **21.229593669 s/step** is an observed run whose advantage was not stable under reversal.

Latest VPN retry **3 November 00:06:30–00:06:34 Vietnam** returned gateway Authentication failed; 00:07:58 path check remained NAMESPACE_UNAVAILABLE. No new VPN attempt in this status turn. No Gadi identity/project supplied. [Safe VPN record](nscc-vpn-retry-20261103.md).

Unchanged xzy, graph-placement, collated-I/O and topology-weight-only branches are closed after contradictory or negative checks. [Earlier detailed handoff, explicitly historical](history/HPC_CURRENT-before-xyz20-terminal-20261103.md). AI payloads, queues, budgets and submission materials remain unchanged.
