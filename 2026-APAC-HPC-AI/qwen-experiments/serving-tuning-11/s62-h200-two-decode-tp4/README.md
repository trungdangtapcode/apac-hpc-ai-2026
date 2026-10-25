# S62: H200 two-replica TP4 decode topology screen

This frozen target-only candidate asks whether two independent 4-GPU decode workers (TP4/EP4) serve closed-loop N64 requests better than the current single TP8/EP8 decode worker, while retaining the two TP4 prefill workers and aggregate decode admission capacity of 256. Each decode worker is capped at 128 running requests.

Historical job 22219 selected P8-TP4_D8-TP4-EP4 at N40 under an earlier runtime and short benchmark. Its 1,666.01 good output tokens/s is not a direct comparison to the modern runtime or current N64 workload. Job 25947 is the modern target-only short-protocol control at 2,757.36 good output tokens/s. The topology must be remeasured with current images, NIXL path, BF16 KV settings and validation gates.

The job uses 16 H200 GPUs across two nodes, 17 minutes maximum. It uses the same unranked N64 20/40/30-second AIPerf screen, fixed 4,000/200 request lengths and seed 2026. Admission requires all four worker health checks, 32 before/after per-rank KV receipts across four TP4 roles, fast-runtime rank checks, all four prefill/decode semantic routes, zero profiling errors/cancellations, at least 90% joint TTFT/ITL success, 7/8 smoke and 12/12 retrieval. Official quality remains UNKNOWN.

Do not promote from one screen. Advance to a matched longer confirmation only if the gate passes and good output throughput exceeds the modern control by at least 3%; otherwise retain the control and stop this topology branch. [Detailed hypothesis and admission record](PLAN.md).
