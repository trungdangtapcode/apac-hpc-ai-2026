# Cold-prefill cache implementation pair: sub-1% result

Recorded 2026-10-29T22:52:15.630166+07:00, Vietnam time (UTC+7). This is a contemporary review of completed jobs, not a reconstructed original measurement.

The question was whether the cold fixed-input workload pays useful Python prefix-tree bookkeeping cost. Source review showed that disabling radix caching selects ChunkCache, while physical active-request KV and successful-transfer release remain necessary. The prospective pair changed only prefill disable_radix_cache from false to true; decode cap 256, polling interval 1, model/FP8 weights, BF16 KV, topology, full N64 workload and all original gates remained fixed.

Actual full control 27376 completed 0:0 in 12:39 on g1/g4, scoring 3041.119598 good output tokens/s. Actual candidate 27378 completed 0:0 in 11:41 on the same node pair and scored 3048.446289, a +0.240921% difference. Both use 16 H200. Good requests are 1874/1900 and 1879/1905 respectively; zero errors/cancellations, 26 TTFT breaches and zero ITL breaches in each. Both pass local smoke 7/8 without regression, retrieval 12/12, all-rank runtime cache/source/KV checks and both semantic routes. Official accuracy remains UNKNOWN.

Control versus candidate mean/p95 TTFT is 1119.985/1332.727 versus 1102.185/1380.071 ms. Mean/p95 request-mean ITL is 14.991/15.166 versus 15.028/15.226 ms. The candidate has a larger single-run score and lower average TTFT, but slightly worse tails/ITL. Generated engine seeds vary while workload seed remains 2026. One run per arm and a sub-1% difference do not establish useful improvement.

Inspection covers raw request and latency distributions, resolved flags and actual all-rank classes, transport/traceback markers, per-role queue/running/KV state, CPU and available GPU VRAM/power/temperature/clocks samples. Candidate decode shows 100% sampled activity, mean 50.708 running requests, maximum 56, zero sampled queue and mean token occupancy 0.1196. All 72 server polls return HTTP 200. Sparse five-second request-start-envelope samples do not prove a causal bottleneck; final drain, host clock calibration, heavy kernel profiles, hot CPU threads and Xid/throttle reasons are absent.

Observed occupancy is 3.373333 and 3.115556 GPU-hours, 6.488889 total; no PBS SU. Candidate raw artifacts, frozen payload and accounting are sealed. The complete machine review, runtime differences, p50/p95/p99/max, hardware distributions and interpretation are in [the pair result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-cold-prefill-cache-study-20261029/RESULTS.md) and its comparison.json.

Decision: close the unchanged ChunkCache treatment, retain the native default, and do not repeat or combine it with cap64 based on this small score movement. C++ radix caching is a distinct implementation hypothesis that preserves prefix caching; its full candidate remains blocked on actual CPU prerequisite 27387. Actual decode compile 27383 retains its queue position. Sparse graph/compile source preparation is under investigation to reduce compile-startup work; no sparse trial has been admitted. No presentation, submission or HPC payload was changed.

This review and terminal evidence receive their own scoped screened checkpoint. Git recovery metadata does not upload sibling large artifact bytes.
