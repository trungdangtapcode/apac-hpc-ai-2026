# S62 research plan: two TP4/EP4 H200 decode replicas

## Why this trial

The current modern-runtime target-only layout has two TP4 prefill workers and one TP8/EP8 decode worker. Short N64 control 25947 scored 2,757.36 good output tokens/s. The recent decode-only EAGLE3 change reduced that to 2,626.71, so speculative decoding is closed for the pinned draft/runtime. The result logs and sampled telemetry show room to question decode topology, but five-second GPU activity samples do not prove a compute bottleneck.

Earlier H200 job 22219 tested `P8-TP4_D8-TP4-EP4` and selected it at N40, scoring 1,666.01 good output tokens/s under an older runtime, KV auto settings, and an earlier short-protocol implementation. This old number is not directly comparable to 25947. It is a reason to re-evaluate the topology with current SGLang defaults, explicit target-only decoding, per-role KV receipts, and the current AIPerf input.

## Hypothesis and control

Hypothesis: replacing the single TP8/EP8 decode worker with two independent TP4/EP4 workers may reduce cross-GPU collective cost and allow independent scheduling, improving N64 good output throughput while preserving the same total GPU count and total maximum decode admission capacity.

The frozen configuration keeps two TP4 prefill workers on node 0. It places `decode-0` and `decode-1` as TP4/EP4 on node 1. Each decode worker has `max_running_requests=128`, preserving the control's aggregate cap of 256. Compared with current target-only control 25947, this is one topology change. The model/image, BF16 model dtype, KV auto resolution, NIXL path, attention/kernel defaults, graph policy, prefill settings, context, 4,000/200 synthetic workload, seed, concurrency and short screen duration remain fixed.

The evidence is an unranked single N64 screen with 20 seconds warmup, 40 seconds measurement and 30 seconds grace, using all 16 H200 GPUs. It is not an official leaderboard measurement and cannot replace the 60/120/30 full-protocol frontier by itself.

## Gates before measurement

The bundle expects exactly four role endpoints on two nodes; every worker must pass health and its own TP4 BF16 KV rank check. The full native geometry observer must collect 32 before/after receipts across the four roles, with 16 distinct ranks and stable registration. Any new shape outside the exact whitelisted 188-region target geometry fails closed. The runtime gate checks role-local TP/EP sizes, request limits, NIXL, BF16 allocations, disabled prefill graphs, decode graph batches 1–64 and MNNVL world size four for both decode replicas. Four isolated semantic prefill/decode routes must return valid responses before AIPerf starts.

The performance gate requires a complete raw request denominator, at least 90% meeting both TTFT <= 3,000 ms and mean ITL <= 20 ms, zero request errors/cancellations, no smoke regression below 7/8 and retrieval 12/12. Official task accuracy is not evaluated and remains UNKNOWN.

## Decision rule

Only advance this topology to a longer matched confirmation if the short screen passes every correctness/latency gate and exceeds the modern target-only short control by at least 3% in good output tokens/s (at least 2,840.08 tokens/s versus 25947). If it misses the SLA, errors occur, any runtime gate fails, or the gain is below 3%, preserve the run and close this branch. Do not compare it numerically to old job 22219 as if workloads matched.

## Admission and preservation

Original job 26055 was cancelled before allocation at 03:06 UTC (no node, zero elapsed) after review found its 120-second/two-thread warmup could not safely cover four routes; historical job 22219 needed up to 150.55 seconds. This immutable revision launches all four route checks concurrently with a bounded 180-second warmup. At the fresh 03:06 UTC check, apacsc42 had no job and both nodes were occupied by another user's 2-node job. Refresh queue and node state immediately before admission. Request only one 16-GPU job for at most 17 minutes. No PBS SU is charged by this H200 Slurm screen.

The topology/runtime files descend from frozen S59 control bundle `serving-tuning-10/s59-h200-fast-default-control`; this revision additionally records exact hashes of the cancelled S62 parent in `PARENT_BUNDLE.json`. The candidate runner is adapted for four role workers, four P/D route checks, and per-role geometry. Do not mutate the payload after submission. Record the scheduler receipt and immutable hashes in a separate admission checkpoint. Preserve raw failures and do not count startup-only or failed gates as a benchmark.

