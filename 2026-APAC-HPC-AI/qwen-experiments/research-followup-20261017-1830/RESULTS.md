# Where the remaining latency failures occur

All counts below come from scored profiling requests in the raw AIPerf journals and reconcile with their official exports. Warmup traffic is excluded from the score. No request is removed and no benchmark threshold is changed.

| Job / platform | N | Requests | TTFT-only misses | ITL-only misses | TTFT-miss request starts after phase start |
|---|---:|---:|---:|---:|---|
| 24291 / H200 | 56 | 1694 | 20 | 0 | 0.0075–0.0246 s |
| 24320 / H200 | 56 | 1667 | 20 | 0 | 0.0148–0.0281 s |
| 24236 / H200 | 58 | 1670 | 22 | 0 | 0.0018–0.0297 s |
| 221151.pbs111 / H100 | 50 | 1400 | 19 | 3 | 0.0029–0.0130 s |

## Findings

In all four runs, every TTFT failure belongs to the initial simultaneous request burst. These requests start within roughly 30 milliseconds of the first scored request. All H200 request mean ITLs pass the 20 ms limit, including those whose TTFT fails. The H100 control also has three ITL-only misses, whose exact timing is retained in burst-analysis.json.

The initial first-second request counts match N: 56, 56, 58 and 50. No recorded warmup request overlaps the first profiling request in these journals. This rejects the proposed explanation of outstanding warmup traffic doubling decode load for these observations. It does not exclude hidden server state or prove a unique queueing cause.

The pattern is consistent with a cold arrival burst waiting for prompt processing, routing or KV delivery. It is not evidence that steady-state decode ITL is currently failing on H200. Worker-level aligned tracing would be needed to attribute the wait to one component.

## How large is this opportunity?

| Job | Observed good tokens/s | If all requests passed at the same observed total rate | Relative headroom |
|---|---:|---:|---:|
| 24291 | 2715.842 | 2748.290 | 1.195% |
| 24320 | 2670.321 | 2702.748 | 1.214% |
| 24236 | 2667.966 | 2703.582 | 1.335% |
| 221151.pbs111 | 2231.429 | 2267.054 | 1.597% |

This arithmetic holds total request throughput fixed. It is not a prediction that a configuration change can remove every miss, and faster total service could change both numerator and duration. For the latest H200 candidate, eliminating all existing misses at unchanged total throughput offers only about 1.2%; a larger gain requires improved total service as well.

## Next conditional candidate

A larger prefill chunk with the new DeepGEMM runner is a bounded hypothesis: larger prompt batches may change MoE kernel efficiency. The old auto-runner chunk8192 trial lost versus chunk4096, so do not claim an existing improvement or repeat it unchanged. Prepare DeepGEMM plus chunk8192 at N56, changing only chunk size versus the DeepGEMM candidate. First review the pending independent N56 confirmation and graph ablation; submit only when a queue slot opens and the results still justify it. One bounded test, full protocol and quality gates, then close the branch on no useful gain.

Do not drop initial requests, delay traffic based on benchmark phase, alter the official seed or warmup, or redefine the score. Generic service improvements must handle burst arrivals while retaining the same benchmark and output checks.

## Reproduction

- Run analyze-burst.py after the saved tail-analysis.json is available.
- burst-analysis.json contains source paths, raw hashes, timing bins and exact counterfactual arithmetic.
- The parent analysis is ../analyze-latency-failures.py; its raw counts reconcile with the benchmark exports.
