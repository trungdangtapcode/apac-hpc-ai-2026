# Fresh native cache control 27376

Reviewed 29 October 2026, Vietnam time (UTC+7). Actual job **27376 completed 0:0 in 12:39 on g1/g4**, using 16 H200. This is our fresh control, not an optimization or the organiser reference.

The independent frozen raw/runtime/KV/semantic/output gate passes at **3041.119598 good output tokens/s**, 1874/1900 good requests (98.631579%), zero errors/cancellations, 26 TTFT and zero ITL breaches, smoke 7/8 without regression and retrieval 12/12. Mean/p95 TTFT is 1119.985/1332.727 ms and request-mean ITL 14.991/15.166 ms. Full p50/p95/p99/max and hardware distributions are retained in control-review-27376.json.

All four ranks of each prefill use default RadixCache; all eight decode ranks use ChunkCache with native disable_radix_cache=True. Physical prefill KV is not disabled, original geometry signatures and both semantic P/D routes pass, and all three cache-lifecycle source guards are observed. No source/descriptor exception was widened. The control retains decode cap 256/polling 1 and all canonical requested N64 cold 4000/200 seed 2026/full 60/120/30 parameters.

The score is +0.067989% versus earlier native 27270. This is a same-setting repeat difference, not an improvement; engine random seeds and launch state vary while workload seed 2026 is fixed. It provides the prospective fresh comparator for 27378 prefill ChunkCache and 27383 conditional decode compilation.

Raw request outcomes, tail latency, role queues/inflight/KV, server polls, selected transport/traceback markers and available CPU/GPU/VRAM/power/temperature/clocks were inspected. See machine review for actual sampled values; missing heavy kernel profile, Xid/throttle reasons and hot-thread CPU are not zeros or healthy. Samples are five-second observations in the first-to-last request-start envelope, with uncalibrated host clocks and no final-drain coverage.

Only source-supported local output checks are established; official full-set model accuracy remains UNKNOWN. The pinned rules say the organisers use the same full-set checks against their own unchanged FP8 reference and require ≥99% of that score. The exact official suite/splits/command/reference score are not supplied in the retained Q1 text; model-card benchmark examples are not an authoritative fixed evaluation protocol. Do not claim the small smoke/retrieval checks or a private MMLU/GPQA subset certify that gate.

Occupancy is 3.373333 GPU-hours versus maximum 4.533334 reservation, no PBS SU. Complete raw outputs/frozen payload/telemetry/accounting are sealed in runs/27376/artifact-manifest.json. Preserve queued candidate positions and compare only complete local passes. Require >1% useful gain and acceptable tails before confirmation; otherwise close the exact setting. No default, slide or submission promotion follows from a control.
