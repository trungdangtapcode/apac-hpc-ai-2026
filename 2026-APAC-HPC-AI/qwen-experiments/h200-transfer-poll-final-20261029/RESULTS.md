# H200 decode transfer polling interval: final results

**Reviewed:** 2026-10-29 (UTC)  
**Scope:** Full N=64 native Qwen serving runs on 16 H200 GPUs. Jobs 27270, 27272, and 27274 vary only the decode-side transfer completion polling interval: 1, 2, and 4. Prefill polling stays at 1.

## Result

| Decode poll interval | Job | Goodput (requests/s) | Good output tokens/s | Change vs interval 1 | Good-request fraction | TTFT p95 / p99 (ms) | ITL p95 / p99 (ms) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 27270 | 15.1953 | 3039.053 | baseline | 98.5279% | 1312 / 3531 | 15.169 / 15.766 |
| 2 | 27272 | 15.1414 | 3028.280 | −0.3545% | 98.6258% | 1422 / 3492 | 15.224 / 16.111 |
| 4 | 27274 | 15.0835 | 3016.700 | −0.7355% | 98.6222% | 1356 / 3494 | 15.342 / 15.965 |

All three pass the local joint SLA: at least 90% of requests must have TTFT ≤3,000 ms and mean ITL ≤20 ms. The three runs had 28, 26, and 26 TTFT breaches respectively, no ITL breaches, and zero request errors or cancellations. Each run still has a TTFT p99 above 3,000 ms; the contest gate is based on the good-request fraction, not a p99 limit.

The measured scores decline as the decode polling interval rises, but the full spread is below the study's predeclared 1% useful-gain threshold. Latency tails do not move monotonically. Keep interval 1 as the best observed setting, close the interval 2 and 4 arms, and do not spend another run widening this polling sweep. One run per setting cannot establish that the small score differences are caused by the interval.

## Controlled configuration and execution

The official workload settings were N=64 closed-loop clients, synthetic input 4,000 tokens (standard deviation 0), output 200 tokens (standard deviation 0), seed 2026, 60-second warmup, 120-second measured phase, 30-second grace, cold prefixes, and the same 16-GPU topology (two P4 prefill workers and one TP8/EP8 decode worker). The same pinned SGLang and AIPerf images were used. Frozen payload hashes passed for each reviewed run.

Actual worker `ServerArgs` confirm that only `disaggregation_decode_polling_interval` changes in the decode worker (1/2/4); all compared prefill worker arguments match. All three roles reported the native polling-source guard and NIXL patch hash. The runtime scan found no selected transport error or traceback in the prefill/decode worker logs. All 72 sampled server-metrics polls returned HTTP 200. The worker logs contain non-fatal `Invalid HTTP request received` warnings during probe windows; their origin is unassigned.

## Runtime and hardware observations

During the 24 five-second samples per role inside the scored-request envelope, decode reported 49.875 mean and 54 maximum running requests, zero queued requests, and mean KV token usage 0.1192 (about 11.9%). Prefill queues were sampled, with mean queue sizes 1.08 and 0.96 and maxima of 22; these sparse samples do not establish a sustained prefill bottleneck.

Mean GPU active time was 100% across the eight decode GPUs and 96.1–97.1% across the two four-GPU prefill roles. Mean sampled VRAM was about 131.06 GiB per decode GPU and 130.21 GiB per prefill GPU. Decode GPU mean power was 469.8 W; observed maximum temperature was 68°C. Prefill mean power was 684.9–688.0 W, with maximum sampled temperature 75–76°C. Host-wide estimated CPU busy time was 12.84% on decode host g4 and 12.56% on prefill host g1; these are node-wide estimates, not worker process usage.

The samples cover the first-to-last profiling-request start envelope, not warmup or final drain. Five-second GPU utilization means time with kernel activity; it does not measure FLOPS or memory bandwidth. Xid/throttling reasons, hot-thread CPU data, and a heavy kernel profile were not collected. The logs and summaries therefore support no causal hardware bottleneck claim.

## Output and token accounting

The local sanity suite passed 7 of 8 cases, with no regression against its frozen reference; the same reverse-string case failed in all three arms. Retrieval passed 12/12, and each run passed both recorded semantic P/D routes. These checks do not establish official model accuracy. The MMLU-Pro/GPQA accuracy result remains **UNKNOWN**; the retained strict reference comparison 25862 failed.

The official performance unit remains `AIPerf Goodput (requests/s) × 200 fixed output tokens/request`. AIPerf's pinned client-side text-tokenization path reports a small number of output lengths as 199 and input lengths as 3,986/3,987. For job 27274, it reports 1,884 outputs at 200 and 3 at 199. Actual generated token IDs and authoritative per-request server usage were not retained, so the precise reason for those local counts remains unknown. They do not change the organizer's fixed 200-token score multiplier.

## Resource cost and retained evidence

| Job | Slurm elapsed | Allocated GPU-hours | Maximum reserved GPU-hours |
|---:|---:|---:|---:|
| 27270 | 11:30 | 3.0667 | 4.5333 |
| 27272 | 11:45 | 3.1333 | 4.5333 |
| 27274 | 11:34 | 3.0844 | 4.5333 |
| **Total** | — | **9.2844** | **13.6000** |

GPU-hours are 16 allocated H200 GPUs multiplied by Slurm elapsed time; they are not energy, PBS SU, or a measure of exclusive GPU busy time. The terminal accounting for 27274 and hashes for its 140 regular run/output files are sealed at `runs/27274/scheduler-accounting.psv` and `runs/27274/artifact-manifest.json`. The frozen submitted payload was not modified. Existing detailed per-run reviews remain under `h200-full-load-review-20261026/`; the machine-readable bracket and reproducible review script are `comparison.json` and `review_bracket.py` here.

## Next step

Keep interval 1 in the matched serving baseline. Review the already admitted, distinct decode-cap-64 full-run candidate when it completes; do not submit a duplicate polling sweep. Do not claim a new best or official accuracy from this bracket.


## Root review clarification: engine seed is not workload seed

The configured experiment changes only transfer polling. Actual resolved engine random_seed also varies across workers/runs and was excluded from the intended-setting comparison, along with permitted launch fields. The raw full differences are now retained in comparison.json. AIPerf workload seed remains 2026. Do not call this deterministic or fully seed-matched execution, or attribute sub-1% differences causally to the polling flag. This strengthens the decision to close the unchanged sweep without promotion.
