# H200 prefill routing: controlled short pair

S63 N66–N72 did not improve good throughput. TTFT tails grew while ITL stayed below 20 ms; sparse rank-local prefill queues reached 13–25, whereas captured decode queues were zero. This motivates testing prefill dispatch but does not prove a causal bottleneck.

S65 is a fresh round-robin control; S64 changes only main-router prefill policy to power_of_two. It compares two workers using the pinned default five-second load check interval. Native startup must show the exact PowerOfTwo struct enum, not an invented unit-like enum. Worker-local load_balance_method is a different mechanism. All target-only model/image/precision/kernel/graph/transport settings, P8-TP4/D8-TP8-EP8 topology, N64, 4000/200 tokens, seed 2026, cold prefixes and 20/40/30 protocol match. Both bundles include the same configured-concurrency checker fix. No scoring settings are relaxed.

H100 full N54 pair 222302/222303 lost 4.865% under power-of-two. That negative prior is retained; this is a one-time H200 interaction screen at a different runtime/kernel/load, not a repeat of H100 or a pooled hardware comparison. See router-queue-research-20261020/PAIR_REVIEW.md and ROUTER_REVIEW_CORRECTION.md.

Require full runtime/native geometry, two semantic paths, complete raw request denominator, >=90% joint latency success (TTFT <=3000 ms; request-mean ITL <=20 ms), zero request errors/cancellations, no smoke regression below 7/8, retrieval 12/12, exact main-router native policy and pinned workload. Short synthetic output checks do not establish official accuracy; it remains UNKNOWN.

Advance only if candidate passes every local gate and exceeds fresh S65 control by at least 3% good output tokens/s. Historical 25947 is descriptive (2757.36), never substituted for a failed fresh control. Otherwise close this exact H200 policy branch. One pair cannot establish a reproduced gain or replace the full-protocol 3044.400475 frontier. If useful, require independent full matched confirmation.

Each job allocates 16 H200 GPUs / two nodes for at most 17 minutes. Submit control then candidate with afterany dependency; admission cap 5 includes both. Preserve all logs and sampling, inspect phase-bounded GPU/CPU/VRAM/queue/KV/tails beyond the score, mark missing telemetry explicitly. No heavy profiling in scoring. Run from qwen-experiments so relative log paths exist. No PBS spending, frozen parent edits, target-weight changes or background Codex.
