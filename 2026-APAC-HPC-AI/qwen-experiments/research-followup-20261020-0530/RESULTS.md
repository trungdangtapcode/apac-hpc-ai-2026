# H200 observer pilot review and next decisions

## Question, control and complete local gates

Jobs 24926 (observer off) and 24927 (observer on) share N60, DeepGEMM prefill/chunk8192, HPC-Ops decode, FA3 prefill attention, FlashInfer decode attention, MNNVL AUTO+PDL, dense graphs, native FP8/BF16 KV, topology, NIXL and full 60/120/30 protocol. Observation enables five-second role GPU/node/server sampling and SGLang metrics. This measures their combined overhead in one pair; it does not isolate the cost of each collector.

Both jobs are COMPLETED with exit 0:0, and both independently pass sealed-payload, raw protocol, runtime, per-request SLA/error, short nonregression and all 12 long-context output checks. They use the intended metrics setting in every role. Scheduler success alone is not acceptance. Official full-set accuracy remains unverified.

| Job | Observer | Good output tokens/s | Joint pass | Mean TTFT ms | Mean ITL ms | Scored / qualifying |
|---|---|---:|---:|---:|---:|---:|
|24926|Off|2991.708665|98.818475%|944.990860|14.935130|1862 / 1840|
|24927|On|2971.312150|98.811453%|975.868313|14.904758|1851 / 1829|

Observed goodput is 0.681768% lower in this pair. Both have exactly 22 TTFT breaches, zero mean-ITL breaches and zero request errors/cancellations. This small difference is descriptive, not a significant observer-cost estimate or a proven improvement. Keep interval2 compared against the equally observed 24927, not the unobserved score or a cross-platform peak.

## What was collected and inspected

The adjacent reviews and `inspection/` retain raw client tail distributions, effective concurrency, role queue/batch/KV log samples, warnings and evidence hashes. These sparse logs cover the whole deployment, not only scored traffic. `24927-resources.json` separately inspects the new uniform sampler; the old extended-inspection renderer's missing-telemetry text refers to its limited inputs and is superseded for 24927 by this dedicated resource inspection. 24926 intentionally collects no resource samples.

All three observer-on role files, phase manifest and orchestration markers are checked against their terminal seal. Scored-phase epoch-nanosecond boundaries lie inside the orchestration markers. The phase includes final request drain. There are 24 decode, 24 prefill-0 and 25 prefill-1 samples, with maximum gaps about five seconds and 16 distinct stable GPU UUIDs. Prefill workers each see relative IDs 0–3 inside their containers, but their UUID sets are disjoint; decoding sees eight other UUIDs. All scored GPU queries and server HTTP samples succeed; no selected numeric GPU fields are unsupported. Cross-node clock skew is not independently calibrated, so remote-role phase selection still assumes host clocks agree. No naive timezone conversion is used.

| Role | GPU activity mean % | Memory activity mean % | Sampled VRAM mean MiB | Mean power W | Mean SM MHz |
|---|---:|---:|---:|---:|---:|
|decode-0|100.00|44.58|134584.42|470.81|1980.00|
|prefill-0|96.52|50.65|133334.00|674.80|1930.16|
|prefill-1|96.63|50.62|133334.00|658.51|1922.10|

Statistics pool per-GPU observations in the phase; they are sample-weighted, not exact time integrals or instantaneous peaks. GPU/memory activity percentages do not measure peak FLOPS or HBM bandwidth efficiency. Dedicated samplers work even though AIPerf's own telemetry endpoints remain empty. CPU counters are deduplicated by host: mean busy 12.55% on g1 and 12.87% on g4, across the whole host. Aggregate host utilization cannot rule out a saturated individual thread. Node interface counters are retained once per host; they do not establish NVLink/RDMA utilization. The sampler takes at most 0.693 seconds per scored sample, mostly subprocess/HTTP elapsed time, not a measured CPU-time cost.

Separate N48 post-score diagnostics have 428/428 and 424/424 successful requests, with 16 sealed nonempty rank-checked GPU traces each. Successful profile start HTTP 200 text responses now parse correctly; stop still returns HTTP 500 after step-bounded capture. That limitation remains recorded and is not hidden. Kernel duration sums are descriptive, not critical-path fractions. All original failed controls remain preserved.

## Assessment, research and next actions

The unobserved N60 score independently agrees with earlier 2990.151/2989.175. Observation is usable for the pending equally observed interval2 comparison, but the pair alone does not establish a 0.68% causal overhead. High sampled GPU activity and substantial prefill power motivate further phase-specific kernel comparison, without claiming a proven power limit or bottleneck. Preserve native clock/power settings.

New independent N62 repeat **24962** is submitted with scored execution files byte-identical to accepted source 24915. It preserves the single 3022.035 N62 result's uncertainty until completion and full review. No automatic N64. A separate next plan will compare DeepGEMM versus HPC-Ops prefill at fixed chunk8192/N60, keeping the current HPC-Ops decode; this is a new interaction setting rather than a repeat of dense FlashInfer prefill, chunk12288, forced one-shot, PDL-off or phase-grad-mode losses.

Read-only extraction of the pinned FA3/HPC source verifies actual available paths. The attempted old `jit_kernel/flash_attention_v3.py` path is absent in this image; the real backend imports `sgl_kernel.flash_attn` directly. A declared environment variable alone therefore does not establish an executed alternate FA3 kernel. Do not spend a GPU job on that unproven toggle. The image's embedding-only KV-write bypass is inapplicable to this generation task and would violate required KV transfer if forced. Keep KV work intact. Upstream background reference: [SGLang FlashAttention source](https://github.com/sgl-project/sgl-flash-attn), consulted 20 October; the extracted deployed source decides compatibility.

## Access and cost limits

At this turn's read-only check, the VPN helper finds no live session and the detached pane is dead with exit zero. The cause/exact disconnection time is not established. No authentication was restarted. PBS outputs, job status and published credit were not refreshed; do not claim new H100 results or release reservations from old snapshots. No PBS jobs were submitted or new SU reserved. Existing H200 24928 retains its queue position; new 24962 is pending. The last reconciled PBS credit/reservation values retain their previous timestamps.
