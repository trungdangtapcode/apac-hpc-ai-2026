# H100 smaller-chunk pair: retain 4096

Both terminal jobs pass all local protocol, sealed payload, runtime, source/precision/transport, output and joint-SLA checks. This is one equally observed N54 comparison of the deployed chunk setting, including its exact native derived prefill graph range. The complete decode graph configuration is unchanged. Official full-set accuracy remains unverified.

| Metric | 222382: chunk 4096 | 222383: chunk 2048 |
|---|---:|---:|
| Good output tokens/s | 2396.779396 | 1770.433299 |
| Joint good / requests | 1481 / 1509 | 1111 / 1215 |
| Joint qualifying fraction | 0.981445 | 0.914403 |
| Mean TTFT, ms | 746.849 | 2039.078 |
| TTFT p99, ms | 3465.948 | 4306.295 |
| Mean ITL, ms | 18.162 | 17.122 |
| ITL p99, ms | 19.064 | 17.447 |
| TTFT / ITL breaches, requests | 22 / 6 | 104 / 0 |
| Errors / cancellations | 0 / 0 | 0 / 0 |
| Long output checks | 12 / 12 | 12 / 12 |
| Allocated walltime | 13:53 | 14:24 |
| Estimated charge, SU | 473.884444 | 491.520000 |

Chunk 2048 loses **26.1328%** goodput. Its lower ITL accompanies fewer active decode requests (47.292 to 33.600 mean sampled requests) and much worse TTFT. Prefill sampled queue means rise from 0.84/0.76 to 5.24/9.04 requests; decode sampled queues stay zero. The intervention shows this smaller deployed chunk is harmful at this setting; it does not identify a unique kernel-level cause or prove global optimality. Keep 4096, and close unchanged 2048/8192 trials instead of expanding a blind chunk grid.

## Inspection beyond score

All raw scored client records and tails/concurrency were inspected. The twelve long output checks and retained short-output baseline pass. Exact worker ServerArgs and graph-generator checks accept only chunk2048 and its native prefill graph consequences; main router remains round-robin and the official model/FP8 weights/BF16 KV/NIXL path are unchanged.

Each job has sixteen sealed post-score CPU/GPU native traces with verified rank mapping. Separate diagnostic requests succeed 376/376 and 328/328. Start-profile control returns 200; all three stop calls return 500 after bounded capture, with ASGI stacks in stop_profile_async after scoring. The existing stop-profile limitation is reported, not hidden or called error-free. Whole-log NIXL error/OOM pattern scans and complete raw logs are retained; their absence is not proof of universal health.

Matched five-second scored hardware sampling verifies sixteen unique GPU UUIDs and 24–25 samples per role. Mean prefill0/prefill1/decode GPU activity is 88.97/88.03/99.99% for control and 90.30/92.25/100.00% for candidate. Prefill VRAM means decrease from 76700/76681 MiB to 76060/76060 MiB while queueing worsens. Mean decode KV token occupancy is 0.23625/0.232 and differs from VRAM. Node CPU/memory and interface evidence is retained in the resource review. Inflight is not collected; node clocks are not calibrated; five-second samples alias short events. GPU activity does not measure FLOPS or bandwidth efficiency; IP interface bytes miss kernel-bypass RDMA; summed post-score kernels are not scored wall-time shares. Whole-run batch log distributions mix phases; use phase-scoped server gauges for scored state.

## Cost and decision

The pair costs 965.404444 SU estimated from 16 allocated GPUs at 128 SU/GPU-hour and reconciles to the published965.404 SU delta within rounding. Used 40272.495 SU, Balance 23727.505 SU, In Doubt 0; internal campaign headroom 10727.505 SU under unchanged 51000 cap and 13000 reserve. No new measurement peak. Close the exact losing setting; the next distinct question is startup cost and reproducibility while the H200 confirmation queue retains its positions.

Read PLAN.md, receipts, per-job gates/reviews/inspection/server-state/resources/runtime scans, pair-accounting.json and collect pointers for sealed raw exports, submitted payloads and profiles. Frozen payloads are unchanged. Scheduler success and local checks are separate from organiser accuracy.
