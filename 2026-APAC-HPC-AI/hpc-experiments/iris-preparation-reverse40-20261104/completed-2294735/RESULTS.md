# Reversed 40-step confirmation: strong within-job signal, variable effect size

Reviewed 4 November 2026. Job 2294735 **COMPLETED 0:0**, 4,710 seconds on iris001 /56 CPUs. All 237 collected file hashes and frozen deployed runtime hashes verify. Independent replay of four 40-step arms passes 39 timing intervals, fixed native iteration counts, successful exits and identical force-coefficient trajectories. Every retained top-level stage status returns 0; source and payload before/after gates pass, runtime identity is stable.

| BAAB order | Mean seconds/step | Maximum seconds/step |
|---|---:|---:|
| B1 interleaved preparation |21.842916421|22.983845868|
| A1 inherited preparation |29.418802008|30.238195791|
| A2 inherited preparation |33.586912671|39.385412771|
| B2 interleaved preparation |21.881843121|24.478310904|

The pooled candidate mean is **21.862379771 s/step**, versus **31.502857339 s/step** for inherited preparation: **30.601914818% lower time within this allocation**. Both adjacent comparisons favor the candidate (−25.75185% and −34.85009%). Candidate repeat drift is +0.17821%; control drift is +14.16819%. This is stronger directional evidence than the earlier 20-step ABBA run 2294676 (−1.76868%, conflicting pair signs), but the effect size varies sharply across allocations. Do not report a universal 30.6% speedup or pool these two jobs into one causal score. No matched claim against teammate, NSCC or Gadi follows.

Only copy/hash-child policy differs; same accepted initialized Scotch source, native solver, physics, 56 ranks and five-second diagnostics. Per-rank memory policy and file residency are not measured. BAAB tests reversed order but cannot eliminate nonlinear variation. Both candidate arms are outside the slower central controls, so endpoints/time effects remain a possible confound. A further independently allocated matched trial is required before a stable improvement claim or full 150-step promotion.

Telemetry includes 184/242/277/184 whole-node samples, all required CPU/memory/vmstat sources available and no recorded sampler errors. Median reported CPU frequencies are near 3.30 GHz in each arm; this does not measure effective cycles or prove lack of throttling. Minimum available memory is about 37.9–38.6 GiB. Pressure files are unavailable, not healthy/zero. Maximum sampler read duration 5.03 ms is not measured runtime interference. No hardware bandwidth, process-attributed page residency or solver helper-affinity evidence supports a causal mechanism claim.

Actual allocated cost is **73.266667 CPU-hours**, conservatively 74 planning hours. The 112-hour maximum reservation was retired once under lock: 1,098 consumed /zero reserved /1,136 internal stage. These are planning units, not billed SU. Raw output, collection hashes, independent replay, diagnostics and the failed/qualified earlier result remain preserved.
