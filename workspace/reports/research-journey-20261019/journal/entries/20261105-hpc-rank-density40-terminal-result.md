# Forty-step rank-density result: promising, not yet confirmed

Iris **2294916 COMPLETED 0:0**, iris001, 56 allocated CPUs, **5,297 seconds**. All four arms complete 40 steps /39 measured intervals. Root replay and a separate read-only review agree: source and payload before/after, actual rank counts, native fixed work, time-file agreement, finite force outputs, initialized fields and runtime identity pass. All 228 collected artifact hashes verify. This is a Basic practice comparison, not an official contest score.

| Arm | MPI ranks | Mean (s/step) | p95, nearest-rank (s/step) | Maximum (s/step) |
|---|---:|---:|---:|---:|
| A1 |56|33.163697419|35.895598701|39.524833968|
| B1 |48|24.820548476|25.887768537|26.766145750|
| B2 |48|28.586746826|29.244562829|29.638132523|
| A2 |56|31.480407650|34.902362040|44.902754168|

Pooled 48-rank mean is **26.703647651 s/step** versus **32.322052535 s/step** for 56: **17.382574569% lower time**. Both adjacent comparisons favor 48 (25.157475% and 9.191942% lower). This is a useful matched signal against our 56-rank Scotch control, rather than selecting a minimum from unrelated allocations. It is not a matched comparison against the teammate recipe.

## Interpretation and numerical work

The 48-rank repeats drift **+15.1737%**, while 56-rank repeats change **−5.0757%**. The effect size therefore needs an independent reversed-order confirmation. Rank count and the required Scotch partition change together; the result does not isolate MPI overhead, cache placement or frequency as a cause. Same-partition force trajectories repeat exactly. Cross-partition maximum Cd difference is 0.004363602, retained explicitly; different decompositions can change intermediate Basic Cd, so no invented universal equality threshold is applied. Original physical inputs and fixed iterations remain pinned.

## Inspection beyond the mean

All 273/208/238/264 node samples contain required memory, vmstat and frequency data. Whole-phase median reported frequency is about 3,300 MHz in every arm; this is not a hardware-cycle profile. Minimum node MemAvailable is 37.66/40.79/40.07/40.79 GiB. Maximum sample read time is 5.064 ms. Pressure files are unavailable, not zero. GNU time reports successful resources and busy CPU totals consistent with 56/48 ranks, but maximum RSS is a process collector, not summed node memory. Initial dynamic-code library lookup misses are followed by compilation and successful solver End; no causal runtime failure is established. Per-rank communication, bandwidth, kernel profiles and solver-thread page residency were not collected.

## Cost and next decision

Actual cost is **82.397778 allocated CPU-hours**, conservatively 83. The 140-hour maximum reservation retired once, leaving **1,310 consumed /zero reserved /1,367 internal stage**. Site-billed SU is unknown; NSCC/AI accounting is separate.

The distinct follow-up is a new allocation with reversed **48 →56 →56 →48** order, the same 40-step horizon, same sources and native checks. It tests order/allocation sensitivity, not a blind duplicate or a new knob. Keep the current result qualified until that comparison is reviewed. No winner over the teammate, universal 17.38% improvement, official score or Gadi/NSCC forecast is claimed.

[Raw retained evidence and replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-20261105/completed-2294916).
