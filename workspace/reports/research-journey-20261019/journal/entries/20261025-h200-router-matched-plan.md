# H200 routing follow-up: fresh round-robin versus power-of-two

Question: can prefill dispatch reduce TTFT tails without changing compute kernels or target outputs? S63 N66–N72 lost good output throughput while ITL stayed below 20 ms; captured rank-local prefill queues reached 13–25 whereas decode queues were zero. These sparse gauges motivate a test but do not establish a bottleneck. Increasing concurrency is closed.

Prior negative evidence: H100 pair 222302/222303 lost 4.865% under power-of-two at N54, full protocol, both-phase HPC-Ops and chunk 4096. That exact H100 branch remains closed. H200 has different hardware, kernel split, chunk 8192 and N64. A one-time paired H200 screen tests this interaction rather than transferring a hardware ranking. The old H100 enum-review mistake is explicitly avoided: require Some(PowerOfTwo { load_check_interval_secs: 5 }) with normal native spacing, not Some(PowerOfTwo).

S65 is a fresh round-robin target-only control; S64 changes only main-router prefill_policy to power_of_two. Both derive from frozen S59 with identical configured-concurrency checker repair. They preserve P8-TP4/D8-TP8-EP8, all 16 H200 GPUs, exact model/image, BF16 KV, graphs/kernels, NIXL, request caps, fixed 4000/200 tokens, seed 2026, cold-prefix setting and short 20/40/30 protocol. Each is capped at 17 minutes. Submit control before candidate with afterany dependency; afterany avoids an unsatisfiable dependency but does not qualify a candidate if its control fails. No PBS SU.

CPU replay verifies checksums/syntax, actual N64–N70 raw workload and denominators, real N72 SLA rejection and wrong-N rejection. The real 25947 router log is accepted for round-robin and rejected for power-of-two. Actual new runtime/geometry/semantic paths, router enum, profiles and output checks must still be verified on GPUs. There are no new scores yet.

Advance only with all local runtime/route/output/workload gates, >=90% joint latency success, zero errors/cancellations and candidate good output tokens/s >=1.03 times the fresh S65 control. Do not substitute historical 25947 if S65 fails. Otherwise close this exact policy branch. Any useful short result needs independent full matched confirmation; full H200 frontier 3044.400475 and official accuracy UNKNOWN remain.

Inspect tails and raw errors/concurrency plus phase-bounded GPU/CPU/memory/queue/KV telemetry for both runs. Sampled active time is not FLOPS, VRAM is not KV occupancy, and missing telemetry is not zero. Preserve runtime/transport failures and full raw evidence.

Sources: serving-tuning-11/s64-h200-prefill-power-of-two/PLAN.md; matching S65 bundle; research-review-26064-26068-20261025/REVIEW.md; router-queue-research-20261020/PAIR_REVIEW.md and ROUTER_REVIEW_CORRECTION.md; h200-next-screens-20261025/verification.json. This checkpoint prepares the pair; submission requires definite receipts and a fresh queue check.
