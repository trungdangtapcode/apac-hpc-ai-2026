# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 04:48 Vietnam (1 November 21:48 UTC)** from actual Iris observations. This is HPC fork 01a17c4b-65e6-75e0-be95-c5bea1b25502; AI is separate. No background Codex or schedules.

## Actual active work

**Iris 2294634 RUNNING on iris001**, accepted 04:46:50 Vietnam, 2 November. One exclusive node, 56 CPUs, zero GPUs, maximum75min. Runs **A-default / B-collated**, 40 steps / 39 timings each. Same Scotch initialization and identical socket/core MPI launch; only B adds `-fileHandler collated` from the supplied teammate recipe. At 04:48 the payload, original accepted 1,040-file source and canonical case-input checks pass; first isolated clone is being verified. No solver speed claim yet. [Receipt, frozen payload and actual status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-20261101/STATUS.md).

Remote root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-io40-20261101T214618Z`; evidence/cases `root/kit/runs/2294634`. Frozen 56 files. Preserve them. Common socket mapping is not proven equivalent to defaults: old probe used ppr:28:package/rank-by-fill, a different command. No source/tolerance/timer modification imported from ZIP.

Iris queue was empty and partition up at21:40UTC; one actual sbatch was admitted after fresh locked checks. Own active Iris cap1 is now occupied. Shared rdmaworkshop30 work is not ours. Current Slurm reservation is not retired while running.

## Completed branch and honest current best

**2294390 COMPLETED 0:0**, iris005,2,009s. All397 selected hashes and independent native checks pass. B1/A1/A2/B2 means **21.051169 / 23.241965 / 33.239424 / 38.462425 s/step**. BAAB candidate aggregate **+5.3685% slower**, versus parent ABBA's misleading -18.5027%; strong temporal drift in both cycles. **Close unchanged graph-placement branch: no reproduced gain.** Cd repeat/source/runtime gates pass. Energy sampling logged socket timeouts; hardware bandwidth, CPU frequency and solver helper affinity were not collected. [Full result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-reverse-20261029/completed-2294390/RESULTS.md).

Best own reviewed scored-platform full result stays **NSCC3.364622070 s/step**,25940700,4nodes/512ranks/defaultScotch/150steps. It is an organizer-recipe reproduction, not a demonstrated new configuration gain. External organizerNSCC3.210832548 remains separate.

The supplied teammate Gadi logs independently replay to **2.079045460 s/step**,4nodes/416ranks/150steps,Cd0.291876135. This is supplied evidence, not our rerun. Same-platform organizer Gadi reuse-Scotch is2.087688606, a separate-run gap of0.414%; neither cross-platform comparison nor this gap isolates a tuning gain. Missing actual fvSolution/source hashes and timer provenance remain qualified. [Package audit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/incoming-openfoam-20261101/REPORT.md).

## Accounting and access

Old2294390 actual31.251111CPUh was conservatively counted32 and its46.666667maximum retired exactly once. Iris ledger now **517 consumed +70 reserved =587 CPUh**, internal stage587. Current owner instruction to improve funds only this one bounded75min job; the agent transparently adds55 to its prior532 internal envelope. The owner did not specify587 numerically; no site SU rate/balance is known. No NSCC/AI credit moved. [Authority](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-20261101/budget-authorisation.json). Do not silently extend again or exceed cap1.

NSCC namespace was unavailable at04:39Vietnam; one bounded actual retry again returned Authentication failed. No confirmed tunnel/CPU login, queue or fresh credit; states unknown, not empty. No Gadi login was supplied to this worker. Do not repeatedly ask the owner about the captain's phone. No new NSCC deployment/reservation/submission. Existing CPU and combined PBS gates/locks still apply before recovery.

## Next action

Collect actual2294634 terminal accounting and selected text with its `collect_completed.py`, replay with `review_completed.py`, inspect tails/Cd/native I/O headers/source/runtime/available resource evidence and all limitations, then reconcile once under the Iris lock. A positive A/B result requires matched reversal/repetition before a gain claim; native40 is the full one-node protocol but remains non-scored Iris data. Prefer useful native scored-platform comparisons when NSCC/Gadi access and current budget permit. A failed branch is not a global stop. Keep ready NSCC S0/Hxyz/Hzyx wave independent of optional diagnostics and query both PBS accounts before admission.

[Current journey entry](../reports/research-journey-20261019/journal/entries/20261101-hpc-iris-recovered-and-native-io-submitted.md); [historical handoff](history/HPC_CURRENT-before-io40-20261101.md). Safe milestones are explicitly captured/verified/committed/pushed; raw selected text is retained. Large external objects remain local unless separately copied off-host. Submission folders/slides and AI payloads are unchanged.
