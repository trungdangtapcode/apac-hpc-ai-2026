# Cold-prefill cache pair: no useful measured gain

Reviewed 29 October 2026, Vietnam time (UTC+7). Both full H200 jobs passed the independent frozen workload, runtime, KV, semantic and local output checks. The prefill ChunkCache candidate scored **3048.446289 good output tokens/s**, **+0.240921%** against fresh native control. This is below the prospective 1% useful-gain gate; close this exact arm without changing the default or submission.

| Measurement | Native control 27376 | Prefill ChunkCache 27378 |
|---|---:|---:|
| Good output tokens/s | 3041.119598 | 3048.446289 |
| Good requests / all requests | 1874 / 1900 | 1879 / 1905 |
| Good fraction | 98.631579% | 98.635171% |
| Errors / cancellations | 0 / 0 | 0 / 0 |
| TTFT breaches / ITL breaches | 26 / 0 | 26 / 0 |
| TTFT mean / p95, ms | 1119.985 / 1332.727 | 1102.185 / 1380.071 |
| Request-mean ITL mean / p95, ms | 14.991 / 15.166 | 15.028 / 15.226 |
| Smoke / retrieval | 7/8, no regression / 12/12 | 7/8, no regression / 12/12 |
| Scheduler | COMPLETED 0:0, 12:39 | COMPLETED 0:0, 11:41 |
| Allocation occupancy, GPU-hours | 3.373333 | 3.115556 |

The hypothesis was that cold inputs gain little from reusable prefix-tree lookup, so removing that bookkeeping might help. Only prefill disable_radix_cache changed from false to true. Actual all-rank classes changed from Python RadixCache to ChunkCache on both TP4 prefill roles, while the TP8 decode role retained ChunkCache, cap 256 and polling interval 1. The machine review checks complete resolved ServerArgs: only this intended setting and generated engine random seeds differ. Workload seed remains 2026. Physical prefill KV, source/lifecycle bindings, both semantic routes and original FP8/BF16 geometry all pass. Prefix lookup removal does not mean disabling active-request KV storage.

The score moved by only +0.240921%. TTFT mean improved, but p95 increased by 3.552% and mean ITL increased by 0.244%. One run per setting cannot separate small treatment effects from launch/seed variation. The candidate's larger single-run score is not a confirmed useful improvement or a new global optimum.

Beyond the score, inspected raw request outcomes and p50/p95/p99/max latency, actual cache/flags, all semantic and output checks, selected traceback/transport markers, per-role server samples and available GPU/host measurements. Candidate decode has 24 samples, 100% sampled GPU activity, mean 50.708 running requests, maximum 56, zero sampled queue and mean token occupancy 0.1196. Both prefill roles average 2.917 running requests with maxima 3/4 and sampled queue maxima 3. All 72 server polls return HTTP 200. Per-role VRAM/power/temperature/clocks distributions and source/runtime evidence are in comparison.json. Five-second sparse observations do not establish GPU saturation as a causal bottleneck, nor does a zero sampled queue prove it was always empty. Missing heavy kernel profile, CPU hot threads and Xid/throttle reasons are not zero/healthy. Profiling request-start envelopes omit final drain and clocks are not calibrated.

Cost is 6.488889 observed GPU-hours for both jobs, within their 9.066667 GPU-hour combined maximum; zero PBS SU. Complete terminal candidate artifacts, frozen payload and scheduler accounting are sealed in runs/27378/artifact-manifest.json; control seal already exists. Official full-set model accuracy remains UNKNOWN. Local smoke/retrieval cannot certify the organiser's at-least-99%-of-reference condition.

Next: preserve these losing results, close this unchanged setting, and review the distinct C++ cache prerequisite and conditional decode compile. The C++ branch retains prefix caching and changes its implementation, so it is a separate hypothesis. No blind ChunkCache rerun or cap64 combination follows from this sub-1% point result.
