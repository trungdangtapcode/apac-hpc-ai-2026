# Decode cap64 passes but does not establish useful improvement

Reviewed 29 October 2026, Vietnam time (UTC+7). Actual **27365 completed 0:0 in 11:43 on g1/g4**, 16 H200. Source/runtime/final-scheduler/KV/two-route/local-output and full raw protocol pass. It is a valid exploratory measurement, not official model accuracy.

| Metric | Control cap256, 27270 | Candidate cap64, 27365 |
|---|---:|---:|
| Good output throughput, tokens/s | 3039.053386 | 3046.890454 |
| Joint SLA, percent of all requests | 98.527865 | 98.633736 |
| Total/good requests | 1902/1874 | 1903/1877 |
| Mean/p95 TTFT, ms | 1116.427/1312.170 | 1111.512/1326.607 |
| Mean/p95 request-mean ITL, ms | 14.995/15.169 | 14.998/15.159 |
| Errors/cancellations | 0/0 | 0/0 |
| TTFT/ITL breaches | 28/0 | 26/0 |
| Smoke/retrieval | 7/8 and 12/12 | 7/8 and 12/12 |

The single-run change is **+0.257879%**, below the prospective >1% useful-gain gate. It is only +0.045606% above the separate previous native individual 26766, too small to establish an optimization. No unchanged repeat, default or submission promotion. Keep the original baseline and close this exact cap64 sensitivity; no128sweep. Local output checks do not verify official accuracy, which remains UNKNOWN.

The exact intended change is source/runtime confirmed: requested and final TP0 scheduler cap64, with separate transfer/preallocation slots, unchanged prefill settings, graph batches 1..64, image/model/precision/KV/NIXL and full requested N64 cold 4000/200 seed 2026/60:120:30. Every native pool source guard passes. All physical KV receipts and both semantic routes pass. No descriptor exception or quality gate was broadened.

Beyond the score, 24 five-second samples show mean 49.625/max 56 running decode requests, no sampled decode queue and mean KV token usage 0.1146. Decode activity mean 95.833% versus 100% in control is explained arithmetically by one of 24 samples containing 0% on all eight GPUs, only 0.161 seconds after the first profiling request started; the remaining 23 samples have 100%. This timing sensitivity prevents interpreting the activity average as a causal efficiency improvement. It does not prove the reason for that initial idle sample. Decode sampled VRAM is 131.158 GiB/GPU; host-wide CPU estimates are 12.87% decode/12.57% prefill, not hot-thread measurements. All 72 role polls return HTTP 200 and no selected transport error/Python traceback is found. Full raw latency and sampled power/temperature/clocks/memory-activity distributions are retained in comparison.json. Missing heavy kernel profile, Xid/throttling reasons and exact generated IDs remain explicit.

Client-reported token counts may differ slightly from requested fixed lengths because AIPerf uses local text tokenization; exact per-row physical IDs are uncollected. The organiser score remains exported Goodput × 200. Do not redefine it with a token recount mean.

Allocation occupancy is3.124444 GPU-hours versus maximum 4.533334 reservation, no PBS SU; this is not a metered charge. Raw requests/exports, logs, telemetry, original frozen payload and accounting are sealed in runs/27365/artifact-manifest.json. The candidate has answered the low-upside source question without revealing a useful gain. New prefill-cache pair 27376/27378 and compile qualification 27383 are separate hypotheses already accepted; this branch closure does not stop the research loop.

Resolved engine random_seed also varies across these separate launches; workload seed 2026 stays fixed. Full raw argument differences are retained in comparison.json. The sub-1% change is not a deterministic, seed-matched or causal improvement claim.
