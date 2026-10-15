# Prefill/decode article review and measured plan update

Reviewed 14 October 2026. The user supplied this
[Outcome School article](https://outcomeschool.com/blog/prefill-vs-decode-llm-inference-optimization).
It is useful as an overview of phase-specific optimization. Implementation
decisions below use the actual staged image, our measured requests and primary
references, rather than its illustrative utilization percentages or speedup figures.

## Completed pilot results, reviewed 15 October

| Job | Prefill change, N52 | Good tokens/s | SLA | TTFT mean ms | ITL mean ms |
|---|---|---:|---:|---:|---:|
| 23286 | Fresh cache-aware control | 2075.11 | 97.42% | 1437.63 | 16.94 |
| 23324 | One request per prefill batch | 2082.09 | 97.44% | 1412.99 | 16.96 |
| 23325 | Round-robin prefill routing | 2402.64 | 98.93% | 333.25 | 19.57 |

Both pilots completed with zero benchmark errors/cancellations. One-request
batches show only a 0.34% single-run gain and retain 34 TTFT failures. Round-robin
shows a 15.78% single-run gain, reduces TTFT failures from 34 to 16 and still has
zero ITL failures in this run. The actual router log confirms its round-robin
prefill policy; worker, decode and client files are unchanged.

The tradeoff is a much tighter ITL margin: round-robin P99 is 19.89ms and maximum
per-request mean ITL is 19.90ms. This is a strong candidate, not yet a confirmed
stable result. [Wave5](../serving-tuning-05/PLAN.md) repeats N52, compares N50,
then gates a possible N54 run. It does not assume the old cache-aware optimum
N58 transfers to the new routing policy.

[Completed per-request analysis](completed-latency-failures.json) reconciles to
the official counts; [full measurement rows](completed-measurements-2026-10-15.json)
retain the raw export paths and quality limitations.

## Finding from existing request data

The new [analysis script](../analyze-latency-failures.py) reads only the profiling
phase of the retained JSONL exports. Counts reconcile exactly with each official
AIPerf summary; warmup requests are excluded. No official metric is replaced.

| Job | Variant | Good requests | TTFT-only failure | ITL-only failure | Both |
|---|---|---:|---:|---:|---:|
| 23128 | Original chunk8192 control | 1222 | 36 | 0 | 0 |
| 23130 | Chunk4096 + dense graphs | 1289 | 34 | 0 | 0 |
| 23266 | Same configuration, repeat | 1287 | 34 | 0 | 0 |
| 23131 | Chunk16384 | 1081 | 108 | 0 | 0 |
| 23265 | FP8 KV | 1239 | 34 | 0 | 0 |
| 23272 | DeepEP | 1216 | 32 | 12 | 2 |

In both winning deployments, all 34 failing requests were submitted within
30 milliseconds of the first profiling request. In job 23266, mean TTFT is
1432.37 ms, P99 TTFT 5977.28 ms and maximum TTFT 7474.30 ms. Mean ITL is
16.93 ms and maximum per-request average ITL is 18.24 ms. This is an initial
burst/tail observation, not evidence of a sustained ITL violation.
The exact failed request IDs, timing, raw hashes and counts are saved in
[latency-failures.json](latency-failures.json).

TTFT is an end-to-end measurement: admission, router/network delays, prefill,
KV handoff and first-token delivery can contribute. Client data alone does not
identify which component causes the tail. We will retain all initial failures,
keep the official warmup/window/cache-bust settings, and test genuine serving changes.

## What changes in the plan

The ongoing N52/54/56/60 refinement remains useful for decode batching and total
goodput. Add two N52 prefill pilots, each compared with the repeated winner and
the fresh N52 control job 23286:

| Pilot | Single change | Evidence and hypothesis |
|---|---|---|
| `s4-prefill-roundrobin-n52` | Gateway `--prefill-policy round_robin` | Router 23266 inherits `cache_aware` for prefill, with absolute imbalance threshold 64. The workload is cache-busted and the burst is N52. Test whether deterministic distribution across the two prefill replicas reduces the first-burst TTFT tail. This is a hypothesis, not a demonstrated router bug. |
| `s4-prefill-single-n52` | Prefill `--prefill-max-requests 1`, chunk remains4096 | Logs frequently show two sequences packed into 4096-token prefill steps. Test whether finishing one request per step avoids small carried-over fragments and reduces TTFT tail; reduced packing may also lower throughput. |

Keep checkpoint, BF16 KV, all sixteen H200, TP4 prefill → TP8/EP8 decode,
dense decode graphs 1–64, N52, transport patch and the official client unchanged.
The primary gateway supports separate phase policies; its actual staged Python
parser and the worker parser accepted both flags in CPU validation. A parser
check is not GPU validation. Two pilots only; no combined configuration until
the separate effects are measured. At most four queued/running account jobs,
including the existing load-search jobs. Existing submitted bundles stay frozen.

Submitted on 14 October: **23324** single-request prefill batches and **23325**
round-robin prefill routing. Both are tracked by the shared controller alongside
load-search jobs 23286/23287. Their CPU validation passed; performance results
are pending. Job IDs and terminal/measurement states update in
[prefill-pilots.json](prefill-pilots.json).

Acceptance: a complete benchmark with zero errors/cancellations, SLA ≥90%, and
output research eligibility. Compare goodput, TTFT-only failure count and timing,
P95/P99 TTFT, and ITL against the same-N controls. Lower P99 alone is insufficient
if goodput falls. Any useful improvement needs an independent repeat before
selection. All eight original output cases remain; full organiser accuracy is unverified.

## Other ideas: priority and limits

- **Continuous batching and P/D separation:** already used. Splitting two phases
  permits independent tuning; it adds a transport path that must also be measured.
  [DistServe](https://arxiv.org/abs/2401.09670) motivates phase-specific parallelism
  and placement under latency constraints.
- **Chunked prefill:** already measured 4096/8192/16384. The article's argument
  about a long prefill interrupting decode on the same GPU does not directly apply
  to our separate P/D pools. Its benefit here must be explained through measured
  scheduling/batching effects. Do not assume ever-smaller chunks improve goodput.
- **Prefix caching:** not the next contest optimization, because the locked client
  explicitly cache-busts the first-turn prefix. No cached benchmark-answer reuse.
- **KV memory/paging:** already managed by the serving engine. Decode logs show
  roughly 0.1 token-pool usage in the observed workload; this is memory capacity
  usage, not GPU compute utilization or HBM bandwidth. FP8 KV used the intended
  dtype but reduced measured N52 goodput. Do not increase memory allocation merely
  to imitate an offline-inference tuning recipe.
- **Speculative decoding:** remains a later compatibility pilot. The organisers
  explicitly permit lossless verification and FP8-or-higher draft weights; no
  benchmark-specific draft training. The original algorithm can preserve the
  target distribution, but a useful speedup here requires a compatible target,
  draft, PD implementation and measured acceptance/verification costs.
  [Original paper](https://arxiv.org/abs/2211.17192),
  [SGLang implementation guidance](https://docs.sglang.io/docs/advanced_features/speculative_decoding).
  A staged small Qwen model is not proof of an accepted draft or PD compatibility.
- **MoE and batching:** the dense single-request intuition is not a bottleneck
  diagnosis for a batched MoE model. Existing traces include substantial MoE,
  attention and collective kernel time. Their summed durations are not wall-time
  fractions; do not infer that decode is purely memory-bound from a blog diagram.

## Primary sources and local evidence

- [SGLang gateway phase policies](https://docs.sglang.io/docs/advanced_features/sgl_model_gateway#prefill-decode-disaggregation)
- [SGLang tuning guidance](https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning): distinguish offline saturation advice from this latency-constrained closed-loop benchmark.
- [Exact router CLI source](inspection/router_args.py), [source hashes](inspection/manifest.json)
- [CPU payload/CLI validation](cpu-validation.json)
- [Frozen pilot definitions](prefill-pilots.json)
- [Local Qwen rules](../../1.%20Qwen3%20AI%20Task%20Rules.md)
- [Live results](../SERVING_TUNING_RESULTS.md)
