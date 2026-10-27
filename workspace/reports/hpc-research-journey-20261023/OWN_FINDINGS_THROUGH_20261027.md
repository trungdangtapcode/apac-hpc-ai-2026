# What our HPC research has actually found

Retrospective written 2026-10-27 T 10:24:55.353004+00:00. This answers the owner's request for concrete research contributions after a week. It separates our experiments from organiser recipes and performance from diagnostic qualification. It does not refresh scheduler state, modify submitted jobs, or claim an official score.

## Strongest measured new candidate: hierarchical cut order on Iris

We screened hierarchical decomposition order, selected `zyx` against `xyz`, initialized both cases with the mandatory native chain, and ran the same 56-rank numerical work in isolated cases on Iris. Changing cut order changes how the domain is partitioned; it does not reduce cells or fixed solver iterations.

| Test | xyz control mean (s/step) | zyx candidate mean (s/step) | Observed time reduction |
|---|---:|---:|---:|
| 2294099, xyz then zyx, 30 steps each | 32.592668524 | 23.811097072 | 26.9434% |
| 2294132, zyx then xyz, 30 steps each | 28.367224538 | 22.290292514 | 21.4224% |

The preferred direction survived reversing execution order. This is our measured candidate finding rather than a replay of the organiser four-node NSCC recipe. The 50-step zyx extension, job 2294148, completed with 49 retained timings averaging **21.112004724 s/step**. Its later window was 0.509% slower than its early window, and its first 30 Cd rows exactly reproduced the preceding zyx trajectory.

Limits: the control in both short pairs had fewer samples than its native recommendation. There is no matched 50 or full 150 result, no proved general 21–27% gain, no official accuracy certificate and **no measured transfer of this candidate to four-node NSCC**. The 50 extension ran on a different Iris host;22.29 to 21.11 is not a new tuning gain.

[First pair](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-screen30-20261026/completed-2294099/RESULTS.md), [reverse pair](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-reverse30-20261026/completed-2294132/RESULTS.md), [50-step horizon](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-zyx50-20261027/completed-2294148/RESULTS.md).

## A useful negative result: NUMA-aware Scotch did not win

An NSCC one-node candidate reduced logical cross-group faces by 10.6283% but increased all interface faces by 1.3423%. The actual solver pair, job 25907753, measured **13.880988254 versus 14.358714620 s/step**, so the candidate lost by 3.4416%. This prevents promoting a nicer graph as a faster solver. The unchanged branch was closed. The cause remains unknown; memory bandwidth, page residency and MPI wait were not measured.

[NUMA graph preparation](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-numa-scotch128-20261021/RESULTS.md), [native solve and interpretation](/home/apacsc42/workspace/reports/hpc-openfoam-20261021/LOG.md).

## Rank density and decomposition screening on four NSCC nodes

Six full 150-step logs compared 64,96 and 128 ranks/node with both methods.

| MPI ranks/node | Hierarchical mean (s/step) | Scotch mean (s/step) |
|---|---:|---:|
|64|4.488921327|10.309943538|
|96|4.922347604|7.146018748|
|128|3.819929017|3.677906731|

The screen favors Scotch 128 among those observations, and shows method ranking can change with density. These were separate allocations and the older jobs lack final PBS history and some acceptance artifacts. They are useful selection data, not a matched causal speedup or accepted score. An independent stronger-evidence Scotch 128 repeat gave 3.364622070 s/step; it did not introduce a new optimization or outperform organiser reference 3.210832548.

[Six-run review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md), [independent repeat](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/RESULTS.md).

## An observed placement problem and a qualified native mechanism

In job 25999546, all three tested launcher-option forms produced singleton masks before MPI initialization and masks permitting logical CPUs 0–255 afterward on all 512 ranks. Moving the binding flag did not fix that observation. This is an allowed-CPU mask, not a measurement of actual migration or a demonstrated bottleneck. The syscall diagnostic did not identify the setter.

Job 26016270 then tested explicit post-initialization main-thread pinning from actual topology and local rank. All 512 targets remained exact singletons across four audit phases, collectives and a two-second interval. Host maps validated 128 distinct physical cores per host. This qualifies a native mechanism; it has no OpenFOAM solver performance measurement and does not qualify helper threads, page placement or Pstream integration.

[Launcher diagnosis](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-launcher-order-20261026/completed-25999546/RESULTS.md), [native mechanism](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-postinit-pin-20261027/completed-26016270/RESULTS.md).

## A new offline placement candidate, still unmeasured in the solver

A balanced assignment keeps all 512 partitions and their numerical work unchanged. Its cross-host interface-face proxy falls from 337324 to 283819 (**15.8616%**), while the same-host cross-NUMA proxy changes from 710081 to 710003. Host cell balance worsens slightly. This is a reproducible graph result, not a 15.86% speedup, measured bytes or proof of better memory locality. It requires separate mechanism qualification and actual full-work solver comparison.

[Placement research and trade-offs](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261023-hpc-balanced-placement-and-queue.md).

## What has and has not been delivered

The work has produced a promising measured Iris partition-order candidate, losing numerical-work-preserving branches, a density/method screen, an observed MPI affinity-mask issue, a working native pinning mechanism and candidate graph assignments, all with linked retained evidence. It has **not** delivered a demonstrated improvement over the organiser's four-node NSCC reference. Earlier conversation compressed this into “nothing better than baseline” and omitted the real Iris findings; earlier upbeat summaries also overstated the same-configuration NSCC repeat. Both interpretations need correction.

The main unfinished delivery is turning the tested ideas into a qualified NSCC full-solver comparison. First review actual application integration, then judge a matched native-versus-pin trial; transfer a distinct Iris-derived cut-order hypothesis only with an appropriate four-node control and required numerical checks. Existing queue ownership and budget rules still apply. No new allocation is admitted by this retrospective.
