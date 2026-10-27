# Comparing the reported 3.39-second mean step

Recorded 2026-10-27T07:43:28.081296+00:00. The teammate value is an owner-reported rounded number. No teammate job ID, raw log or script has been supplied, so its method and validity have not been verified. This is a measurement clarification, not a new benchmark result.

## What our number means

NSCC CPU job **25940700**, four nodes and **512 MPI ranks**, completed the official 150-step case with default Scotch decomposition. Its native timer Average is **3.364622069698 seconds per step**. Recalculation from all 149 rows of `wallClockTime.dat`, Times 2 through 150, agrees. The timer excludes the first step by design; no additional slow samples are removed.

The calculation is `sum(timeStepWCT for Times 2..150) / 149`. The measured sum is **501.328688385000 seconds**. Preparation, queue time and the first step are outside this statistic. Dividing the full job or full solver duration by 150 measures something different.

The native timer is implemented in [FOwallClockTimeStatistics](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/case-recovery-20261021/case/system/FOwallClockTimeStatistics). The retained [full-run review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/RESULTS.md) documents source, fixed iteration work, numerical evidence and timing checks.

## How to interpret 3.39

If the teammate measured the same task on the same platform, rank count and sample definition, **3.39 seconds/step is only 0.754% higher than our retained mean**. Lower is better. This numerical gap does not establish a repeatable performance difference or its cause. Separate allocations can vary; the teammate configuration and samples are unknown.

The **21.112004724 seconds/step** Iris observation is a different machine and a 50-step, 56-rank experiment. Comparing it directly with a four-node NSCC observation does not demonstrate a configuration improvement.

## Evidence needed to explain the teammate result

Obtain the job ID, submitted script, native solver log and `wallClockTime.dat`. Compare actual platform/hosts, nodes/ranks/threads, official mesh and OpenFOAM build/precision, decomposition, mandatory initialization, fixed solver iterations, endpoint, included timing rows, final Cd and errors. A different decomposition can be legitimate; changed numerical work requires separate rule and accuracy assessment. No such change is assumed here.

Until those artifacts arrive, the exact reason for the teammate result and whether their averaging differs remain unknown. No teammate optimization is credited or dismissed. No scheduler state was refreshed and no jobs or reservations were changed during this clarification.

## Direct provenance of the organiser 3.21-second observation

Rechecked against both the retained original file and the public upstream source on 27 October. This is **job 25710718.pbs101**, full-chain `nosrx-scotch-4node`, dated **7 October 2026**, OpenFOAM v2512, four ASPIRE-2A CPU nodes, 128 ranks each, default Scotch, 150 steps. Its original solver log prints `Average wall-clock time per time step = 3.210832547664429`; independent recalculation of all 149 per-step samples agrees.

[Original public solver log](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/4.3-aspire2a-logs/nosrx-scotch-4node/50_simpleFoam.2026-10-07_10-11-20.log#L2419). [Official ASPIRE application notes](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/4.3%20OpenFOAM%20Application%20Notes%20-%20ASPIRE-2A.md#where-the-signal-7-comes-from) list this observation rounded to 3.211, the runtime setting and the job ID.

The relevant setting is `FI_OFI_RXM_USE_SRX=0`, an MPI/libfabric transport setting used as a workaround for shutdown faults in the documented environment. **Our 25940700 payload already uses this same setting** (`nscc-cpu-four-node-confirm-20261023/payload/pair.pbs`, line 79); discovering the organiser log does not add a new tuning switch to our configuration. The two observed means therefore do not isolate this setting's effect.

The retained organiser PBS output `nosrx-scot-n4.o25710718` records zero returns from decomposePar, renumberMesh, potentialFoam, applyBoundaryLayer and simpleFoam. That strengthens the original-log evidence, but is not a fresh terminal scheduler query. The precise cause of the timing gap to our run remains unmeasured; lower tail latency is descriptive evidence, not proof of a network or placement cause.

The official notes additionally list a 3.176–3.387 s/step range for four SRX-off Scotch runs, including solver-only reuse. Thus **3.21 is one selected full-chain reference, not the organisers' minimum or a proven hardware limit**. Reuse runs must retain their different preparation provenance.

[Our historical progress and limits](../reports/hpc-research-journey-20261023/PROGRESS_THROUGH_20261027.md) separates own results from these references.

## Correction: external reference is not our measured baseline

Recorded 2026-10-27T08:05:48.801261+00:00. The owner challenged why the organiser 3.2108 result was called a baseline after a week without exceeding it. The earlier conversational answer “yes, baseline is 3.2108” was too broad. Use **external organiser reference observation** for 3.210832548, and **our independently reviewed baseline observation** for 3.364622070. A causal optimization claim needs a fresh comparable control, preferably matched arms, rather than replacement of our measured control with somebody else's favorable run.

The organiser example is default Scotch on 512 ranks with SRX disabled, not an identified proprietary optimization. Our retained repeat already uses the same SRX setting. The available evidence does not identify the physical cause of the timing difference. Do not blame node allocation, queue, placement, network, cache or noise as though their causal contribution had been measured.

The research has produced workload validation, failed-branch findings, reproducibility evidence and placement-mechanism qualification, but **no demonstrated repeatable four-node solver-speed improvement over that organiser reference**. Prolonged mechanism diagnostics are supporting work, not evidence that the performance objective has been met. Reporting the independent 3.6779 to 3.3646 change as a tuning achievement would be incorrect; it is the same intended configuration on separate allocations, with a much smaller change in median than mean.

The performance objective remains open. A reasonable next milestone is an actually measured matched native-versus-qualified-pin solver comparison, after the integration gate is reviewed, within existing queue/budget ownership rules. Reject or revise the hypothesis if it does not produce a repeatable useful gain; do not substitute a growing diagnostic count for solver improvement. No new job, budget or payload change is authorized merely by this explanation, and no claim about a live queue is added.
