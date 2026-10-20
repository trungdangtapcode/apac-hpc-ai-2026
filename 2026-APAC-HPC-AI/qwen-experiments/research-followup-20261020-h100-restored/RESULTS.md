# Recovered H100 observer/polling results

## Question, controls and complete review

After the owner requested H100 access, VPN and SSH were restored and the three completed jobs were collected read-only. Observer off/on compares the combined five-second GPU/node/server sampler and SGLang metrics. Interval2 changes only the native decode request-receive polling interval relative to the equally observed interval1 control. All use N54, two TP4/EP1 prefill workers, TP8/EP8 decode, both-phase HPC-Ops, chunk4096, native FP8 checkpoint/BF16 KV, FA3 prefill, FlashInfer decode, MNNVL AUTO+PDL, graphs1–64 and request-scoped NIXL.

All three independently pass terminal seals, submitted hashes, actual runtime/ranks, complete 60/120/30 and 4000/200 protocol, raw per-request latency/error gates, short-output nonregression and all 12 long-context checks. Runtime differences are limited to intended metrics/poll interval and random seeds; speculative decoding stays disabled. These are local serving/output checks, not full organiser accuracy.

| Job | Observer / interval | Good tokens/s | Joint success % | Mean TTFT ms | Mean ITL ms | Scored / good |
|---|---|---:|---:|---:|---:|---:|
|222048|Off / 1|2433.019859|98.687664|688.759160|18.255476|1524 / 1504|
|222049|On / 1|2395.310646|98.339973|763.004573|18.136530|1506 / 1481|
|222050|On / 2|2406.802229|98.280423|728.957967|18.205185|1512 / 1486|

The observed interval2 difference is **+0.479753%** against observed interval1. Observation on/off differs **−1.549893%** in one pair. Neither establishes a causal monitoring cost or a reproducible scheduler gain. Mean ITL rises 0.068655 ms for interval2, while mean TTFT improves 34.046606 ms. Raw failures matter: off has 20 TTFT / zero ITL breaches; on-control has 21 TTFT / four ITL breaches; interval2 has 21 TTFT / five ITL breaches. There are zero errors/cancellations or overlapping latency breaches. Means alone would hide those ITL-tail failures.

2433.020 is the highest individual locally reviewed H100 observation, only about 0.088% above prior 2430.891. It is an additional incumbent observation, not a new optimisation gain. H200 stays separate at its own 3022.035 N62 single observation.

## Collected and inspected diagnostics

Three immutable collection snapshots preserve PBS output/accounting, frozen payloads, raw request data, output checks and CPU/GPU diagnostics with evidence hashes. Each snapshot has 16 rank-checked nonempty traces. Separate N48 diagnostics succeed 357/357, 376/376 and 373/373. All start-profile HTTP 200 text responses are correctly accepted; each has three explicit stop HTTP 500 errors after step-bounded capture. Those stop errors are preserved, not silently reclassified as success. CPU operators can nest and recorded GPU interval coverage is not hardware utilization or a causal critical path.

Dedicated resource samples are available only for observer-on 222049/222050. The inspector verifies phase-manifest/orchestration order, sealed inputs, 16 disjoint stable UUIDs, successful GPU/HTTP queries and 24–25 samples per role, with roughly five-second spacing. Prefill visible IDs are physically disjoint 0–3 and 4–7 on PBS. Node CPU/network counters are deduplicated by host. The shared inspector now supports the PBS collection hash mapping as well as the prior Slurm terminal inventory. Remote-node clock skew remains independently unmeasured; phase selection assumes host clocks agree, including final request drain.

| Job / role | GPU activity mean % | Memory activity mean % | VRAM mean MiB | Power mean W |
|---|---:|---:|---:|---:|
|222049 decode|100.00|53.33|77998.00|416.03|
|222049 prefill-0|88.62|47.81|76682.00|620.28|
|222049 prefill-1|86.20|46.05|76685.44|630.06|
|222050 decode|100.00|53.52|77996.00|415.17|
|222050 prefill-0|88.50|47.98|76680.00|617.01|
|222050 prefill-1|87.77|46.92|76707.12|617.39|

These are sample-weighted per-GPU observations, not bandwidth/FLOPS efficiency, peak usage or a proven bottleneck. Dedicated resource samples are intentionally absent from observer-off 222048. AIPerf's own telemetry endpoints remain empty; they do not describe the separate working collector. Sparse whole-deployment batch/queue/KV logs and tail distributions are retained in the per-run inspections. No health conclusion is inferred from missing telemetry or a coarse aggregate.

## Cost reconciliation

Published Used 36308.194 SU, Balance 27691.806, In Doubt zero (14:00:02 SGT publication). The three allocated-walltime charges are 493.795556, 432.924444 and 409.031111 SU, total **1335.751111 SU**. They reconcile the published delta **1335.751 SU** within ledger rounding. All three previous maximum reservations are released; no outstanding reserve remains at this checkpoint. Internal headroom is **14691.806 SU** under the unchanged 51000 cap, retaining the 13000 project buffer. Reconnection itself did not spend GPU credit.

## Assessment and next decision

The observed polling difference is positive but smaller than the on/off deployment difference; it does not justify promotion or interval/load growth. Both observed runs have a few request-mean ITL breaches, while the unobserved reference has none. One bounded unobserved interval2/control pair can test the native setting without the sampler/metrics overhead and reverse candidate/control order. It remains a new controlled check, not a claim that subtracting 1.55% predicts a score. Reserve at most two jobs/3072 SU, serial, only after a fresh queue/credit check. If the unobserved pair is flat/losing or fails gates, close this setting. If a useful >=1% fully gated gain appears, require independent confirmation before adoption. No automatic interval4, new load, changed numerics, official accuracy claim or broad sweep.

This continues the previously authorised research after restoring access. Source explanations, failures, raw artifacts and exact controls are retained. The 20 October presentation is a dated snapshot and is not modified here. No background Codex is enabled.
