# H200 follow-up review: jobs 26064–26068

**Review date:** 25 October 2026. The Slurm queue is currently empty for `apacsc42`; team `apacsc01` owns nodes g1/g4 at the latest live query. Historical scheduler states below are terminal and no longer live.

## Findings

The four S63 jobs produced complete, independently auditable AIPerf profiles, but Slurm marked them `FAILED 1:0` because the independent checker still required concurrency N64 and looked only for `screen/n64`. I updated no submitted payloads. The external audit script reads each frozen payload's configured N, verifies the full AIPerf input config, request-level TTFT/ITL rows and denominator, recomputes Goodput × 200, and checks output smoke and retrieval responses. It confirms the first three are valid local short screens and N72 genuinely misses the SLA. The Slurm `FAILED` state is retained as evidence of our checker bug; it does not erase the already captured benchmark data.

| Job | Load | Good output tokens/s | Joint SLA success | Mean TTFT | p95 TTFT | Mean ITL | p95 ITL | Errors / cancelled | Output / retrieval | Local screen |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 25947 control | 64 | 2,757.36 | 95.24% | 1,311.60 ms | 2,767.61 ms | 14.833 ms | 15.303 ms | 0 / 0 | 7/8 / 12/12 | Pass |
| 26065 | 66 | 2,533.33 | 94.29% | 1,815.97 ms | 3,123.49 ms | 14.386 ms | 14.980 ms | 0 / 0 | 7/8 / 12/12 | Pass; −8.12% vs control |
| 26066 | 68 | 2,465.71 | 91.36% | 1,902.49 ms | 3,271.04 ms | 14.427 ms | 15.024 ms | 0 / 0 | 7/8 / 12/12 | Pass; −10.58% |
| 26067 | 70 | 2,497.14 | 90.75% | 1,934.91 ms | 3,299.85 ms | 14.521 ms | 14.970 ms | 0 / 0 | 7/8 / 12/12 | Pass; −9.44% |
| 26068 | 72 | 2,269.48 | 82.33% | 2,044.66 ms | 3,557.81 ms | 14.538 ms | 15.009 ms | 0 / 0 | 7/8 / 12/12 | **Fail SLA** |

Goodput is measured in requests/s by AIPerf; the displayed good output token rate is Goodput × 200 output tokens. Each request counts toward the success fraction, including errors and cancellations. In these four profiles there were none. A p95 TTFT above 3,000 ms is consistent with a passing request fraction when fewer than 10% of requests breach the joint threshold.

**Decision:** close the N66–N72 concurrency-increase branch. All passing points lost to the matched short N64 control, and N72 fell below the 90% gate. Do not promote these as score gains. This matched short control is not contemporaneous, so the exact percentage deltas are screening evidence, not a full-protocol ranking comparison. The long-protocol H200 frontier remains 3,044.400475 good output tokens/s; none of these jobs replaces it. The short output sanity and retrieval checks do not establish the official 99% accuracy requirement.

## Beyond the score

Phase-bounded five-second sampling covered all 16 distinct H200 GPU UUIDs. Mean sampled GPU-active time across role/GPU samples was 64.7–67.2%; mean sampled allocation was about 129.6 GiB per GPU. Role means were about 60–65% active on prefill and 68–74% on decode. These are sampled active-time and memory values, not FLOP utilization or proof of a limiting kernel.

Host CPU-jiffy deltas were counted once per node: approximately 12.2–12.3% busy on g4 and 14.3–14.7% on g1 during each scoring window. Both nodes reported about 2.01 TiB total memory and 1.81–1.87 TiB available at the first in-window sample. These broad host counters do not identify a serving bottleneck.

Embedded server scrapes in the scoring interval returned HTTP 200 for 57–59 samples per job. The available rank-local gauge series had decode `num_queue_reqs` maximum zero, while sampled prefill rank-0 queue maxima ranged from 13 to 25 requests as N increased; the exposed decode rank-0 `num_running_reqs` maxima ranged 49–52. Prefill cache-token usage gauges peaked near 2%, and decode near 13–14%. These are sparse, rank-labelled samples, not a merged total across tensor/expert ranks; they suggest a question about prefill queueing but cannot prove causality. Scores, tails and gauges all show ITL remains well below threshold while TTFT misses grow. A separate matched prefill-side intervention would be needed before attributing the effect to prefill.

## S62r2 failure and correction

Job 26064 started all four S62 workers and confirmed role-local BF16 KV allocation, then failed before semantic route warmup and before AIPerf. The validator had an undefined reference to singular `UNKNOWN_D_HEADS_ROLE` although its role allowlist was `UNKNOWN_D_HEADS_ROLES`. Correcting the typo exposed a too-narrow whitelist: existing exception covered TP8 decode, while this candidate has two TP4 decode workers. The raw 32 before/after receipts show the same explicitly uncollected head/dtype fields and exactly 188 VRAM regions per decode rank, each with 256-byte item/page/token strides. No head count, dtype, explicit layer IDs or semantic layer order is inferred.

The corrected validator was run against all 32 retained 26064 receipts and passed with the exact TP4 role/byte/region gates. Frozen derivative S62r3 applies this validator repair and changes no serving topology. The next decision is one bounded S62r3 retry against the modern N64 control. It remains a topology screen, not a score claim; require all worker/runtime/geometry/route/output gates before interpreting its AIPerf data.

## Artifacts and limitations

- [Independent raw AIPerf and observability audit](S63-audit-results.json)
- [Reproducible audit script](audit-results.py)
- [Corrected S62r2 geometry recheck of job 26064](S62r2-26064-geometry-recheck.json)
- Immutable submitted payloads remain under each `runs/<job>/submitted-payload/` directory.
- Raw requests, logs, hardware sampling and terminal scheduler records are preserved under `qwen-experiments/runs/26064–26068/`.
- Official full-set accuracy remains unknown. These results do not prove leaderboard placement.
