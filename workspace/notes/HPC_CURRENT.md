# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 04:48 Vietnam (1 November 21:48 UTC)** from actual Iris observations. This is HPC fork 01a17c4b-65e6-75e0-be95-c5bea1b25502; AI is separate. No background Codex or schedules.

## Actual active work

**Iris 2294634 RUNNING on iris001**, accepted 04:46:50 Vietnam, 2 November. One exclusive node, 56 CPUs, zero GPUs, maximum 75 minutes. Runs **A-default / B-collated**, 40 steps / 39 timings each. Same Scotch initialization and identical socket/core MPI launch; only B adds `-fileHandler collated` from the supplied teammate recipe. At 04:48 the payload, original accepted 1,040-file source and canonical case-input checks pass; first isolated clone is being verified. No solver speed claim yet. [Receipt, frozen payload and actual status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-20261101/STATUS.md).

Remote root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-io40-20261101T214618Z`; evidence/cases `root/kit/runs/2294634`. Frozen 56 files. Preserve them. Common socket mapping is not proven equivalent to defaults: old probe used ppr:28:package/rank-by-fill, a different command. No source/tolerance/timer modification imported from ZIP.

Iris queue was empty and partition up at 21:40 UTC; one actual sbatch was admitted after fresh locked checks. Own active Iris cap 1 is now occupied. Shared rdmaworkshop30 work is not ours. Current Slurm reservation is not retired while running.

## Completed branch and honest current best

**2294390 COMPLETED 0:0**, iris005, 2,009 seconds. All 397 selected hashes and independent native checks pass. B1/A1/A2/B2 means **21.051169 / 23.241965 / 33.239424 / 38.462425 s/step**. BAAB candidate aggregate **+5.3685% slower**, versus parent ABBA's misleading -18.5027%; strong temporal drift in both cycles. **Close unchanged graph-placement branch: no reproduced gain.** Cd repeat/source/runtime gates pass. Energy sampling logged socket timeouts; hardware bandwidth, CPU frequency and solver helper affinity were not collected. [Full result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-reverse-20261029/completed-2294390/RESULTS.md).

Best own reviewed scored-platform full result stays **NSCC 3.364622070 s/step**, job 25940700, 4 nodes / 512 ranks / default Scotch / 150 steps. It is an organizer-recipe reproduction, not a demonstrated new configuration gain. External organizer NSCC 3.210832548 remains separate.

The supplied teammate Gadi logs independently replay to **2.079045460 s/step**, 4 nodes / 416 ranks / 150 steps, Cd 0.291876135. This is supplied evidence, not our rerun. Same-platform organizer Gadi reuse-Scotch is 2.087688606, a separate-run gap of 0.414%; neither cross-platform comparison nor this gap isolates a tuning gain. Missing actual fvSolution/source hashes and timer provenance remain qualified. [Package audit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/incoming-openfoam-20261101/REPORT.md).

## Accounting and access

Old 2294390 actual 31.251111 CPU-hours was conservatively counted 32 and its 46.666667-hour maximum retired exactly once. Iris ledger now **517 consumed + 70 reserved = 587 CPU-hours**, internal stage 587. Current owner instruction to improve funds only this one bounded 75-minute job; the agent transparently adds 55 to its prior 532 internal envelope. The owner did not specify 587 numerically; no site SU rate/balance is known. No NSCC/AI credit moved. [Authority](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-20261101/budget-authorisation.json). Do not silently extend again or exceed cap 1.

NSCC namespace was unavailable at 04:39 Vietnam; one bounded actual retry again returned Authentication failed. No confirmed tunnel/CPU login, queue or fresh credit; states unknown, not empty. No Gadi login was supplied to this worker. Do not repeatedly ask the owner about the captain's phone. No new NSCC deployment/reservation/submission. Existing CPU and combined PBS gates/locks still apply before recovery.

## Next action

Collect actual 2294634 terminal accounting and selected text with its `collect_completed.py`, replay with `review_completed.py`, inspect tails/Cd/native I/O headers/source/runtime/available resource evidence and all limitations, then reconcile once under the Iris lock. A positive A/B result requires matched reversal/repetition before a gain claim; native 40-step is the full one-node protocol but remains non-scored Iris data. Prefer useful native scored-platform comparisons when NSCC/Gadi access and current budget permit. A failed branch is not a global stop. Keep ready NSCC S0/Hxyz/Hzyx wave independent of optional diagnostics and query both PBS accounts before admission.

[Current journey entry](../reports/research-journey-20261019/journal/entries/20261101-hpc-iris-recovered-and-native-io-submitted.md); [historical handoff](history/HPC_CURRENT-before-io40-20261101.md). Safe milestones are explicitly captured/verified/committed/pushed; raw selected text is retained. Large external objects remain local unless separately copied off-host. Submission folders/slides and AI payloads are unchanged.

## Latest actual execution checkpoint

At **2 November 04:49:59 Vietnam**, job **2294634 is RUNNING on iris001**, elapsed 189 seconds. Payload, accepted source, canonical text inputs and isolated clone hash/inode gates pass. Native A-default solver started at 04:48:12 Vietnam and has reached **step 2/40**, with its header confirming uncollated I/O. No observed fatal marker or scheduler stderr. B-collated has not started; no completed performance result yet. Preserve the running allocation and its reservation.

## Progress checked at 2 November 04:58:10 Vietnam

Job **2294634 remains RUNNING on iris001**, 680 seconds into the allocation. Native A-default is at **step 18/40**, with no observed fatal marker or scheduler stderr. B-collated has not started; this is not a completed metric or improvement. The one-own-allocation cap remains occupied and the full 70 CPU-hour maximum stays reserved. Read-only NSCC transport at 04:58:27 Vietnam still reports namespace unavailable; no additional authentication was triggered in this checkpoint. Current NSCC/Gadi performance results are unchanged. Preserve this job and review both complete native outputs before another decision.
