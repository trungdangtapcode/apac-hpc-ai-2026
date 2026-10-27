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
