# H100-to-H200 verification: retain the existing H200 recipe

All four trials completed 0:0 and independently passed their full local raw
workload, source/runtime, physical KV, two semantic P/D paths and output gates.
They ran on **the same 16 H200, nodes g1/g4**. The H100-selected recipe did not
beat the current H200 recipe in this bounded verification wave.

| Job | Configuration on H200 | Concurrency | Good output tokens/s | Joint SLA fraction |
|---|---|---:|---:|---:|
| **27777** | DeepGEMM prefill/chunk 8192, FlashInfer decode |64| **3038.022907** |98.630137%|
| 27779 | Same recipe, FA3 decode |64|2999.245473|98.507463%|
| 27781 | H100 recipe: HPC-Ops both phases, chunk 4096 |54|2738.940099|98.944282%|
| 27783 | Same H100 recipe |64|2721.815800|98.369249%|

At the same N64 on H200, FA3 decode loses 1.276404% and the transferred H100
recipe loses 10.408319% versus fresh control 27777. The fourth result is not a
failed job or a partial score: the independently checked raw denominator is
1717 requests, with 1689 good, 28 TTFT breaches, zero ITL breaches and zero scored
errors/cancellations. All four retain smoke 7/8 without regression and retrieval
12/12. Full official model accuracy remains UNKNOWN, not certified 99% of the
organiser's reference. Official score is exported Goodput (req/s) times 200.

## What the fourth measurement resolves

27781 at N54 could not isolate a recipe effect against the N64 control. 27783
provides that same-load N64 comparison. It changes both prefill MoE runner and
chunk size as a package; it does not quantify either contribution separately.
Both use two TP4/EP1 prefills, one TP8/EP8 decoder, HPC-Ops decode, MNNVL, round-robin,
the pinned FP8 target/image and BF16 KV with the same native launch, transport,
caches, polling and dense decode graphs 1..64. The prefill chunk change naturally
reduces its capture range 8192 to 4096. The resolved speculative MoE backend field
also follows the selected runner, but speculative_algorithm remains None and no
draft is loaded. These dependent fields are recorded, not hidden or called
extra independent optimizations. Decode settings differ only in generated
engine seed between 27777 and 27783.

The retained approximately 3044.400475-good-token/s H200 repeat mean remains a
historical series, not the denominator for these new comparisons. Use the fresh
3038.022907 control to avoid selecting an unusually high or low old run.
No new optimum or submission promotion follows from this wave.

## Increasing load exposes waiting work without improving goodput

Compare 27781 and 27783: the serving arguments are identical except generated
engine seeds, while the independently checked client concurrency is 54 versus 64.

| Measurement | H100 recipe on H200, N54 | Same recipe on H200, N64 |
|---|---:|---:|
| Good output tokens/s |2738.940099|2721.815800|
| TTFT mean / p95, ms |896.156 /1106.815|1591.493 /2017.559|
| Request-mean ITL mean / p95, ms |14.868 /15.042|14.872 /15.033|
| Prefill 0/1 sampled queue means, requests |1.5417 /1.2083|7.3750 /4.4583|
| Decode sampled running requests, mean |42.4583|44.1667|
| Decode sampled queue max, requests |0|0|
| TTFT / ITL threshold breaches |18 /0|28 /0|

Goodput changes -0.625216%, while mean TTFT increases 695.337 ms; ITL is almost
unchanged. More outstanding requests coincide with larger prefill queues rather
than a comparable increase in running decode requests. This supports a waiting-
work interpretation for the increased first-token latency. We did not collect
per-request queue/computation/transfer time decomposition, so we cannot assign
the extra 695 ms to one component or establish a specific causal kernel bottleneck.
The workload is closed-loop; N controls outstanding work, not a fixed arrival
request rate. All requests, including errors, remain in the SLA denominator.

The FA3 pair shows another tradeoff: TTFT improves 57.425 ms, but request-mean ITL
increases 0.527 ms and mean end-to-end latency increases 47.522 ms. Faster first
token delivery alone does not maximise good output throughput for 200-token
responses. Keep FlashInfer decode for this measured deployment; do not turn a
losing decode result into a claim that FA3 prefill or every FA3 use case is bad.

## What H100 was useful for, and what we can tell the panel

H100 provided compatibility checks, failure mechanisms and candidate selection
while the clusters were independently available. H100 peak 222048 at N54,
2433.019859 good tokens/s, and fresh 225227, 2399.186728 good tokens/s, remain H100
observations. Neither can directly rank the new H200 alternatives or provide a
universal GPU conversion ratio.

The defensible conclusion is: **we used H100 to screen choices, then compared
the selected alternatives against a fresh control on H200. The H100-selected
recipe did not transfer as the best H200 choice, so we retained the H200-specific
recipe.** This is measured engineering selection, not a theoretical declaration
that one library or GPU is universally best. Host CPU affinity, runtime launch,
node state and independently generated seeds also limit cross-platform inference.

## Final diagnostics, preservation and decision

27783 completed 0:0 in 11:04, 1689/1717 good (98.369249%), with zero scored errors or
cancellations. Its actual HPC-Ops prefill and decode, chunk 4096, native graphs,
physical KV and both semantic routes pass the frozen reviewer. Role logs contain
no selected transport/OOM markers or Python tracebacks. No failed semantic setup
response file was produced; that is distinct from the earlier control's two
pre-score 503 retries. There are 72 successful/inspected server metric polls.

Five-second samples cover 24 observations per role and 16 distinct GPU UUIDs. Decode
GPU activity mean 100%, VRAM 130.631 GiB/GPU, running requests mean/max 44.1667/47,
sampled queue 0 and KV token usage mean 0.1196. Prefill activity means 94.635% and
91.719%, sampled queue maxima 10/8. GPU activity, VRAM and KV occupancy are
different measurements; they do not by themselves prove compute saturation.
CPU, power, temperature and clock distributions were inspected and preserved.
Sparse sampling, uncalibrated clocks and the request-start envelope exclude exact
final-drain coverage. Heavy kernel/per-thread profiles, Xid/throttle reasons and
authoritative generated token IDs remain uncollected.

Actual wave occupancy is 12.671111 GPU-hours versus maximum 18.133334 GPU-hours;
PBS SU = 0. All raw requests, exports, synthetic inputs, role telemetry, logs,
frozen payloads and scheduler evidence are sealed. Git retains recovery manifests;
large external object bytes require their own off-host copy.

**Decision:** retain the current H200 DeepGEMM/chunk 8192 prefill plus HPC-Ops,
FlashInfer/MNNVL decode at N64. Close both FA3-decode and unchanged H100-recipe
ports; no losing repeat or wider blind sweep. The requested four-job wave is
complete. Fresh queue state and accounting are in final-comparison.json.
No new GPU job, H100 authentication/spending, HPC modification, background Codex,
presentation/submission change or organiser upload is implied by completion.

Evidence: [final comparison](final-comparison.json),
[27783 complete extended review](result-27783.json),
[earlier three-run review](RESULTS.md),
[independent full gate](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-full-load-review-20261026/review-27783.json).
