# H200 routing under observed prefill-queue skew

Question: can native power_of_two prefill routing improve useful H200 N60 throughput when round_robin briefly leaves one prefill queue longer? Completed recv2 job 24928 yields 2983.506734 good output tokens/s, only +0.4105% over observed interval1 control 24927 and below observer-off 24926. Close that polling change unchanged. The evidence does not justify interval4 or another identical recv2 allocation.

## Why this different test

The actual measurement-window hardware/server samples of 24928 show an asymmetric prefill queue: strict 120-second sampled mean/max 0.125/3 requests on prefill0 versus 0.9167/22 on prefill1; decode queue stays 0 at sampled instants, running requests mean about 48/max 53. There are only 24 strict measurement samples per role (24/25/25 if the grace drain is included), so a causal routing bottleneck is unproven. Native power_of_two uses current worker load and may reduce a transient imbalance, or add cost/staleness and lose.

The H100 routing test previously lost 4.865% and worsened TTFT. That is negative transfer evidence, explicitly retained. This trial is H200-specific because the measured relative compute/queue regime differs; it is not a claim that the setting generally works or a repeat of H100 spending. Root chooses one bounded test now rather than waiting for all pending branches: the existing fresh RR control is already queued and a distinct source-supported candidate can retain a queue position without adding another control allocation. Do not infer a gain from GPU activity or sparse queue snapshots.

## Exact control and change

Derive from frozen 24964, s21-dg8192-hpc-n60-control. Keep two TP4/EP1 prefills with DeepGEMM/chunk 8192 and one TP8/EP8 decode with HPC-Ops, dense 1..64 decode graphs, FlashInfer attention, MNNVL, native dtype/FP8 target, NIXL patch, N60, resource observer and output/long-context/post-score diagnostic unchanged. Change only the main router's native --prefill-policy round_robin to power_of_two. Pairwarmup still uses its unchanged single-pair routers. Explicit inverse diff and all other execution-file byte checks pass; config/provenance/job name/checksums are updated.

Offer full official-shaped closed-loop 4000/200 seed 2026 cold-prefix traffic with 60-second warmup/120-second measurement/30-second grace. Both candidate and fresh control retain identical monitoring overhead. This is a full local performance trial, not official accuracy or a ranked submission. Different scheduling dates/nodes and sparse sampling remain limitations.

## Queue, gates and next decision

One allocation:16 H200, 2 nodes,at most17 minutes; no PBS SU. Under the shared watcher.lock, query own live queue, require total pending/running <=5, preserve24962/24964/24965/25051, record an unambiguous receipt once. Use afterok:24964 to preserve the fresh control followed by candidate sequence. If the control fails semantically despite a successful batch status, the candidate cannot be promoted as a valid matched improvement. No uncertain retry, background schedule or modification of old payloads.

Before promotion, require both completed raw protocol/runtime/output gates, zero errors/cancellations, joint SLA >=0.90, complete raw request/export evidence and actual native policy receipts. Require at least 1% good-output-token/s improvement over the fresh equally observed RR control and no adverse TTFT/ITL-tail shift beyond observed repeat variability. Inspect actual effective concurrency, queues/running/KV, role/phase telemetry, runtime/transport and available profiles. A single passing gain calls for independent confirmation, not global optimum. A subthreshold/negative/invalid result closes this exact H200 routing setting; do not retry it unchanged. The measured N62 best and official-accuracy gap remain unchanged until valid new evidence exists.
