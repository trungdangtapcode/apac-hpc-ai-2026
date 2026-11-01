# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 05:38 Vietnam** (1 November 22:38 UTC) from actual scheduler/results. HPC fork 01a17c4b-65e6-75e0-be95-c5bea1b25502; AI ownership is separate. No background Codex or schedules.

## Actual active job

**Iris 2294635 RUNNING on iris001**, accepted 05:37:29 Vietnam on 2 November. One exclusive node, 56 CPUs, zero GPUs, maximum 75 minutes. **B-collated then A-default**, 40 steps / 39 timings each, same accepted Scotch 56-rank initialization and common --map-by socket --bind-to core. Only B uses `-fileHandler collated`. Frozen 56-file derived kit preserves physics/fixedIter/original function objects; new /proc/cpuinfo snapshots are before/after solver only. Payload/source/canonical-input gates pass; first isolated copy is underway. **No new solver result yet.** [Actual receipt and status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-reverse-20261101/STATUS.md).

Remote root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-io40r-20261101T223647Z`; evidence/cases root/kit/runs/2294635. One own Iris allocation cap is occupied; shared-account jobs are not ours. Preserve frozen payload, queue position and full reservation.

## New reviewed result and interpretation

**Parent 2294634 COMPLETED 0:0**, iris001, 2,738 seconds. All 116 selected transfer hashes and independent native 40-step replays pass. A-default first **31.600735680 s/step**; B-collated second **29.681757101 s/step**: observed **6.0726% lower mean**, NOT confirmed optimization. A/B medians 31.271388431/28.687821001; maxima 35.908385101/51.401735539. All 40 Cd rows match exactly; final Cd 0.436959331. Source/field/inode/runtime and actual I/O headers pass.

B timing first 10 mean 34.407829191 and last 10 mean 26.818858285 s shows a strong downward trend. Native sample recommendations 15/192 versus 39 observations. Keep all samples. GNU time selected counters and procfs snapshots inspected; no actual solver helper-affinity, hardware bandwidth or sustained CPU-frequency evidence. No causal bottleneck conclusion or NSCC/Gadi speedup claim. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-20261101/completed-2294634/RESULTS.md). New B/A ordering tests temporal confounding; both jobs use iris001 but node identity does not remove time effects.

The older graph-placement branch is closed: 2294390 BAAB aggregate 5.3685% slower versus parent ABBA's unconfirmed 18.5027% faster. Do not repeat/promote unchanged graph mapping. [Review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-reverse-20261029/completed-2294390/RESULTS.md).

## Scored-platform best and next prepared hypothesis

Our best reviewed full NSCC result remains **3.364622070 s/step**, job 25940700, 4 nodes / 512 ranks / 150 steps / default Scotch, a baseline reproduction. Organizer NSCC 3.210832548 is separate. Teammate ZIP Gadi 2.079045460 is internally consistent supplied evidence, not our rerun. Gadi organizer reuse-Scotch 2.087688606 is a separate-job reference; neither platform gap establishes a tuning gain. Source/timer provenance qualifications remain in the [audit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/incoming-openfoam-20261101/REPORT.md).

A distinct **default MPI placement vs exact teammate socket/core mapping** four-arm 40-step ABBA kit is prepared in iris-placement40-20261101, statically peer-reviewed, **deferred/not deployed/not submitted/not reserved**. Old probe 2294358 tested ppr:28:package fill/span, not exact --map-by socket; no mapping equivalence claim. This hypothesis waits for the I/O confirmation, with new root/financial/site review required before activation. Do not treat preparation as a job.

## Cost, access and next execution

Old 2294634 actual 42.591111 CPU-hours conservatively counted 43; its 70-hour maximum retired once. Iris now **560 consumed + 70 reserved = 630 CPU-hours**, agent-selected internal stage 630. Latest Continue applied to only this bounded 70-hour confirmation; internal stage 587→630 is a transparent 43-hour extension, not owner numerical or site balance. No SU rate/balance known; no NSCC/AI credit moved. [Authority](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-reverse-20261101/budget-authorisation.json). Preserve cap 1 and do not silently extend again.

Read-only NSCC transport at 05:29:43 Vietnam still showed namespace unavailable; no new authentication this turn. Last actual bounded retry returned Authentication failed. Queues/credit/old PBS commitments unknown, not empty. No Gadi SSH identity was supplied. Prefer national-supercomputer measurement if already-authorized access returns, after fresh CPU/AI queue, credit and old-commitment checks under the existing locks. Ready NSCC native S0/Hxyz/Hzyx does not depend on optional diagnostics.

On 2294635 terminal, collect selected text, replay native outputs, jointly inspect A/B and B/A per-arm trends/tails/Cd/resources/runtime and warnings, then reconcile once under iris-scotch56 budget.lock. A favorable pooled mean is insufficient against inconsistent within-pair effects or nonlinear drift. Proceed to a justified distinct trial within gates, not blind repeats. Submission materials/AI payloads remain unchanged. Safe milestone commits are explicit; external large objects still require separate off-host backup.

[Current journal](../reports/research-journey-20261019/journal/entries/20261101-hpc-collated-signal-and-reverse-submitted.md); [historical handoff](history/HPC_CURRENT-before-io40-reversal-20261101.md).
