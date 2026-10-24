# The corrected FP8 cache screen loses

Job **25920** completed with exit 0 and independently passes its local runtime, semantic, workload, error/SLA, smoke and retrieval checks. It changes KV precision against fresh BF16 control **25863** on the same H200 platform.

| Short N64 screen | BF16 control | FP8 candidate |
|---|---:|---:|
| Good output tokens/s | 2,796.146461 | 2,697.655265 |
| Requests meeting both latency limits | 95.2830% | 95.1140% |
| Completed profiling requests | 636 | 614 |
| Profiling errors / cancellations | 0 / 0 | 0 / 0 |

The candidate is **3.52239% lower**. Both use 20 seconds warmup, 40 seconds measurement and 30 seconds grace, fixed 4,000 / 200 tokens and seed 2026. These short results are not directly comparable with the full-protocol 3,044.400475 incumbent.

The earlier **25864** failed because our inherited checker insisted on BF16. That failure supplied no performance observation. S52 corrected validation and retained serving settings. All 16 ranks now prove FP8 KV allocation, and both semantic paths pass. One failed warmup response was retained before successful semantic retries; zero errors above refers to profiling requests.

The candidate retains the known 7/8 smoke floor and passes 12/12 retrieval checks. Its KV scales are uncalibrated defaults inferred from source, not observed per-layer values. Official full-set accuracy remains **unknown**. Local diagnostics do not certify the contest's 99% requirement.

Close this unchanged FP8-KV branch: its predeclared gain-above-1% condition is false, so full confirmation is not justified. [REVIEW.json](REVIEW.json) retains exact metrics and limits. [Telemetry inspection](telemetry-inspection.json) covers bounded samples from 16 distinct GPU UUIDs. Sparse VRAM/utilization observations do not establish why FP8 was slower.

The sampled decode KV token occupancy peaked at **12% for BF16 and 6% for FP8**; decode queue length was zero at the captured instants. Prefill queue peaks were 26/22 requests for BF16 and 26/20 for FP8. These are sparse observations over warmup, measurement and grace, so they do not identify a causal bottleneck. They show no captured KV-capacity pressure at this operating point. FP8 roughly doubled token capacity while the allocator still used a similar byte budget; lower token occupancy does not mean lower allocated VRAM. See [paired server metrics](paired-server-metrics.json).
