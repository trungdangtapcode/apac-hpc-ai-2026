# Full modern H200 control: valid, no new improvement

Job 26315 (S70) completed 0:0 after 10:10 on g1/g4. The independent offline audit replays the frozen manifest, actual runtime gate, raw AIPerf denominator and local output checks. N64, fixed 4000/200, seed 2026 and full 60/120/30 are verified. This modern control disables prefill CUDA graphs and caps admission at 64. It is the first observed arm of the submitted graph/admission 2x2 experiment.

| Metric | Observation |
|---|---:|
| Good output throughput | 2807.325653 tokens/s |
| AIPerf Goodput | 14.036628 requests/s |
| Joint latency success | 98.248588% |
| Profiling requests | 1770 |
| Errors / cancellations | 0 / 0 |
| Mean / p95 TTFT | 1515.921 / 2203.190 ms |
| Mean / p95 request ITL | 14.534 / 15.008 ms |
| TTFT / ITL breaches | 31 / 0 requests |
| Small output sanity / retrieval | 7/8 without regression / 12/12 |

Relative to recent exact legacy replay 26313 (2830.923547 tokens/s), this observation is 0.8336% lower. That comparison changes multiple runtime properties; it is not an isolated graph effect. Relative to old historical 3044.400475 mean it is 7.7872% lower, but the old and current measurements are not a controlled pair. Neither difference proves a cause. Do not promote this control or retry until it produces a favorable peak. Official full-set 99%-reference accuracy remains UNKNOWN.

## What was inspected beyond throughput

Raw tails, all profiling request outcomes and actual runtime/source checks pass. No selected transport error lines or Python traceback were found in the three role logs. During the first-to-last profiling request-start envelope, 71 server polls report HTTP 200. Decode has 24 samples/eight distinct GPUs: mean activity 100%, sampled VRAM 131.147 GiB/GPU, mean 46.9167 running requests, zero sampled queue and 0.12 token-usage gauge. Prefill roles have 24/23 samples on four GPUs each: activity 97.240%/95.315%, VRAM 128.917/128.918 GiB/GPU. Their mean sampled queues differ (6.0000 versus 0.1304) and running requests differ (3.0417 versus 1.7826). These observations motivate retaining the matched graph/admission comparisons; they do not prove routing or kernel causality.

Deduplicated node CPU busy estimates are 12.87% on g4 and 14.74% on g1. The inherited offline helper mislabeled host memory divided from KiB by 1024 squared as TiB. Current review keys are corrected to GiB (total 2014.874 GiB/host); raw counters and historical snapshots remain unchanged. Earlier host-memory TiB labels from that helper are historical unit mistakes, not petabyte nodes. This unit correction does not change throughput, GPU VRAM or decisions.

The envelope excludes warmup and final drain but is not an exact phase clock. Five-second sampling and uncalibrated host skew limit inference. GPU activity is not FLOPS, VRAM allocation is not KV occupancy, and a rank-local token gauge is not an aggregate cache utilization. Full post-score kernel traces are retained but their kernel contents were not inspected here; sparse telemetry is not a causal bottleneck diagnosis. Allocation cost is 2.7111 GPU-hours; no H100 SU is charged.

## Next decision

Preserve pending 26317 (breakable graph/cap 64), 26319 (breakable/native admission), 26347 (disabled/native admission) and separate corrected NIXL component 26337. After their actual results, compare graph at fixed admission and admission at fixed graph, then require a useful valid gain above the prospective 1% gate before proposing confirmation. A failed arm blocks its paired interpretation. The remaining queue contains distinct necessary controls; no blind duplicate is added just to fill a finished slot.

Evidence: [independent full audit](../h200-incumbent-recovery-20261026/review-26315.json), raw runs/26315, terminal scheduler accounting and artifact-manifest.json. Raw retained traces may be external archive objects; a Git push does not upload the sibling artifact store. No submission, slides or HPC payload changed.
