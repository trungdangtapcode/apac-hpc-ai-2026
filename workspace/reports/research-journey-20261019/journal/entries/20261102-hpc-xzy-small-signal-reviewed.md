# Reviewed xzy BAAB: small favorable signal, confirmation required

Actual job **2294643 COMPLETED 0:0** on iris001, 56 CPUs, **5,847 seconds**. Observed **2 November 2026, 14:48:52 Vietnam**. Independent replay passes all 222 transfer-file hashes, all four complete 40-step / 39-interval native outputs, exact fixed solver iterations, source/copy/field seals and executable/library identities.

| Order | Method | Mean seconds/step | Nearest-rank p95 seconds/step |
|---|---|---:|---:|
| B1 | xzy | 32.777265111 | 39.197863824 |
| A1 | Scotch | 33.170890385 | 36.707254352 |
| A2 | Scotch | 33.586073698 | 38.773714284 |
| B2 | xzy | 33.505903444 | 40.828126956 |

The pooled xzy mean is **0.70973% lower**, with both adjacent comparisons favorable (**-1.18666% and -0.23870%**). Scotch repeats differ by +1.25165% and xzy by +2.22300%. This is a small favorable screen, **not a stable improvement or a Gadi estimate**. Its effect is smaller than the native function object's 2%-error target.

The xzy arms recommend 50 and 44 measured intervals but have only 39, and both explicitly warn that the run is too short. Scotch recommendations 22/25 are below 39. Xzy p95/maxima and step variability are higher. Every treatment has an early/late timing trend: first-ten means 35.4–36.5 versus last-ten 31.1–32.4 seconds/step. The cause remains unknown; do not infer a hardware bottleneck or trim the slower early intervals. All native rows stay included.

Same-method Cd trajectories repeat exactly. Final Cd: xzy 0.43777827225979465, Scotch 0.4369593310096111. Between-method transient Cd differs; no universal Basic tolerance is invented. Native bounding-omega lines occur 9 times in each xzy arm and 10 times in each Scotch arm, retained as actual numerical diagnostics. All reported 56-rank package/core maps match. Full stderr/native logs, GNU time, before/after CPUinfo and source/runtime checks were inspected. No fatal marker is found in the inspected streams. Sustained clocks, hardware bandwidth/cycles, NUMA pages and actual helper affinity were not collected; CPU utilization sums and command maximum RSS do not establish a cause.

**Decision:** one preregistered reverse **Scotch/xzy/xzy/Scotch** confirmation at **52 steps / 51 timings per arm**. Fifty-one exceeds the prior estimated native N=50 for a 2% target; it does not establish 0.7%-effect significance or guarantee that the next run's sample recommendation is met. Use adequate full-arm time caps and preserve warnings/failures. Do not submit another unchanged 40-step run that retains the known sampling warning, or an underbudgeted 150-step pair. The confirmation changes temporal placement and extends the horizon; all comparisons remain matched within their own identical workload.

Allocation cost is 56 × 5847 / 3600=**90.953333 CPU-hours**, conservatively 91. The original 140 maximum was retired once under lock. Current local planning **841 consumed, 0 reserved, internal stage 890**, not billed Iris SU. A distinct 52-step four-arm request uses a robust 3-hour / 168 CPU-hour maximum; any internal-stage change and reservation are a separate admission checkpoint. No new submission is claimed by this review.

[Full native result and evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy40-20261102/completed-2294643/RESULTS.md). All raw logs and tables are retained. NSCC read-only probe at 14:48:46 Vietnam returned NAMESPACE_UNAVAILABLE; no new authentication was attempted. AI/submission materials remain untouched.
