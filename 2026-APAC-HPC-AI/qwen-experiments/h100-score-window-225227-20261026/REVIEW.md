# H100 N54: separate scored activity from startup averages

The original 225227 review correctly labeled its resource averages as allocation-wide, including long idle startup and teardown. Those averages must not be read as evidence that most benchmark GPU capacity was unused. This supplement independently selects samples between the first and last profiling-request start from the 1,512 retained raw requests. It supplements the existing review without changing raw logs or the measured 2399.186728 good tokens/s.

| Role | Samples | Distinct GPUs | Mean sampled GPU activity | Mean VRAM per GPU |
|---|---:|---:|---:|---:|
|Decode|24|8|99.990%|76.170 GiB|
|Prefill 0|24|4|91.542%|74.889 GiB|
|Prefill 1|24|4|91.427%|74.885 GiB|

All 72 sampled server polls returned HTTP 200. Decode has mean 46.6667 running requests, zero sampled queue, and mean token-usage gauge 0.2354. Prefill running means are 1.2917 and 1.9167, queue means 1.0000 and 0.4167; prefill 0 has an isolated sampled queue peak of 18. These observations do not establish a particular routing or kernel cause. Node-wide CPU busy estimates are 7.04% and 7.20%; a low node average does not prove every relevant thread has spare CPU.

The earlier allocation-wide decode activity around 35% and this score-window value near 100% measure different intervals. There is no contradiction. GPU activity measures sampled time with work, not FLOPS. VRAM is allocated memory, not KV token occupancy; the token-usage gauge is rank-local. Approximately 2,015.563 GiB host memory is computed from raw KiB using the corrected unit. Missing telemetry would be recorded as missing, not zero.

This request-start envelope excludes warmup and startup but also stops before the final admitted request completes. Five-second sampling and uncalibrated host-clock skew remain limits. It is not a continuous profiler. Heavy kernel traces were not inspected. The EAGLE eight-GPU feasibility job remains a distinct architectural question, not a diagnosis derived from activity alone or a guaranteed gain.

Evidence: [reproducible audit](audit.py), [exact window, raw counts and role gauges](score-window.json), and retained raw 225227 artifacts in h100-review-225227-225228-20261026/curated-r2. No GPU allocation or SU spending was needed for this analysis.
