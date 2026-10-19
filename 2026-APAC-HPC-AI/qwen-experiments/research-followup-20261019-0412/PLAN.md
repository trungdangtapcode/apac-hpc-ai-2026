# Controlled followups after recovered H200 and H100 results

The user requested continuation on 19 October 2026. The [previous review](../research-followup-20261019-0400/RESULTS.md) establishes passing source measurements and fresh accounting. Both own queues were empty when checked. This batch has four H200 jobs and two serial H100 jobs; no background AI or automatic retry is enabled.

## H200: improve the independently repeated operating point

The source is job 24647: DeepGEMM prefill, chunk 8192, auto decode, concurrency 58. It scores 2780.483 good tokens/s, 2.2688% above fresh same-load control 24589, with 98.8453% joint SLA success, mean TTFT 784.494 ms and mean ITL 16.505 ms. Original 24544 scored 2786.696. The failed 24588 warmup remains failure evidence.

| Trial | One changed factor versus the new control | Hypothesis and stopping rule |
|---|---|---|
| s14-dg8192-control-n58 | None; independent deployment | Fresh comparison for the three candidate deployments. A failed control blocks causal gain claims. |
| s14-dg8192-n60 | Concurrency 58 to 60 | The repeated N58 point has latency headroom. Test one additional load step; throughput can saturate and latency can worsen. No automatic N62. |
| s14-dg12288-n58 | Prefill chunk 8192 to 12288 | A larger token budget may improve batching of roughly 4000-token prompts. It can instead increase graph/workspace cost and latency; there is no guarantee the new shape works. Do not change per-request context length or automatically increase chunk again. |
| s14-dg8192-hpc-decode-n58 | Decode MoE runner auto to HPC-Ops | HPC-Ops decode reduced ITL at chunk 4096, but same-load goodput gain was only 0.2117%. Test its interaction with the better prefill chunk, retaining DeepGEMM prefill. Do not assume additive gains. |

Each job requests 16 H200 GPUs for at most 17 minutes. The existing 360-second whole-client guard remains identical in every candidate and control. It does not shorten the normal benchmark, filter slow requests or repair the earlier stall. Any guard timeout is a failed attempt, with no unchanged retry. HPC-Ops preflight remains required before loading the changed decode runner.

## H100: verify the new peak and test one further load step

Source job 221341, both-phase HPC-Ops at concurrency 52 and chunk 4096, scores 2398.728 good tokens/s. Its joint SLA success is 98.7316%, TTFT 602.260 ms and ITL 18.211 ms. Source quality/runtime/protocol checks pass. Job 221346 independently supports the same serving configuration at N50 (2375.807); it does not replace a repeat at N52.

Submit an independent N52 repeat, then one N54 trial. Only concurrency changes in the latter; serving, precision, benchmark and quality scripts stay identical. Use a serial PBS dependency, at most one 16-GPU allocation running. Each requests at most 45 minutes, so the two-job reservation is **3072 SU**, not a prediction of actual spend. The fresh project balance is 36800.853 SU, with zero In Doubt. Keep the internal 51000-SU operating bound and 13000-SU buffer; these are planning choices, not organiser limits. Reconcile already charged terminal reservations before counting the new batch.

Classify the recovered both-phase H100 profile by actual kernel names while jobs wait. Summed kernel durations are diagnostic, not wall time or predicted end-to-end speedup. Do not spend H100 credit on repeating the losing auto-prefill chunk-8192 branch unchanged.

## Acceptance and preservation

Freeze and check payload hashes before submission. Every result needs terminal accounting, complete unchanged 60-second warmup / 120-second scoring / 30-second grace, the joint TTFT ≤ 3000 ms and request-mean ITL ≤ 20 ms gate on at least 90% of all requests, error/cancellation checks, intended runtime and ranks, short-output nonregression and all 12 long retrieval checks. Official accuracy at 99% of the reference score is still unverified. A completed allocation alone is not an accepted measurement.

Preserve every failure and raw artifact. Store actual returned job IDs immediately; never resubmit an uncertain submission. Compare each candidate with its declared same-platform control and repeat useful gains before promotion. No slide, official submission package, HPC task content or organiser upload changes are part of this batch. Capture this milestone into the local archive with actual commit dates.
