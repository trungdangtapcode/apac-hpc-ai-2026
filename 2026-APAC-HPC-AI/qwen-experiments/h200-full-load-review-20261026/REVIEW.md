# Full native N62/N66 bracket closes without a gain

| Job | Client N | Good tokens/s | Joint SLA | Mean / p95 TTFT (ms) | Mean / p95 ITL (ms) |
|---|---:|---:|---:|---:|---:|
|26436|62|2823.776622|98.531073%|1352.48 / 2001.41|14.647 / 15.347|
|26319 control|64|2827.996286|98.424311%|1471.40 / 2222.67|14.659 / 15.287|
|26438|66|2826.104466|98.320269%|1593.12 / 2466.54|14.670 / 15.335|

Both new runs independently pass the complete fixed-workload raw denominator, actual source/runtime, native KV geometry, two semantic routes, local smoke 7/8 without regression and retrieval 12/12. Both have zero profiling errors/cancellations. Full 60/120/30, fixed 4000/200, seed 2026 and cold prefixes remain. Official full-set accuracy stays UNKNOWN. We parameterized only the offline review's configured-N paths; the submitted gates already read configured concurrency.

N62 is -0.149211% and N66 -0.066896% versus contemporary full N64. Lower load improves TTFT but not goodput; higher load worsens TTFT without a useful gain. The three-point score span is only about 0.15%, below the prospective >1% useful-gain gate. Preserve both lower observations and close this immediate concurrency branch. One run per load does not prove a global optimum or a causal bottleneck. No N68 widening or unchanged confirmation is justified.

The independent JSON retains inspection beyond scores: actual transport/traceback scans, raw breach counts, phase-admission-envelope per-role running/queue/token gauges, sparse hardware samples and deduplicated host CPU/memory observations. N66 decode mean running requests is 46.7917 with no sampled queue; prefill mean queues differ, 8.4167 versus 0.7083. These are observations, not proof of a routing defect. GPU activity is not FLOPS and VRAM is not KV occupancy. Host memory units are corrected GiB. Missing observations are not zeros; sparse five-second sampling and uncalibrated host skew limit inference. Heavy profiles were disabled.

Slurm records both COMPLETED 0:0 in 10:33 and 11:25, approximately 2.8133 and 3.0444 allocated GPU-hours; no PBS SU. Raw artifacts are terminal-sealed and their manifest hashes preserved. Large archived objects require an off-host copy beyond Git push.

Next distinct question: jobs 26473 and 26475 test prompt chunk 6144 and 4096 under the same recovered full N64 runtime. All original local/quality/runtime gates remain. The separate plan retains earlier small gains under old N56 and requires a useful valid >1% result before confirmation. No new-best, official score, slide or packaged submission claim follows from this bracket.

Evidence: review-26436.json, review-26438.json, reusable review-full.py, seal.py, immutable submitted payloads and original raw AIPerf files in runs/26436 and runs/26438.
