# S62 revision 2: two TP4/EP4 H200 decode replicas

This is a fresh immutable correction of `s62-h200-two-decode-tp4`; the earlier payload and job 26055 remain preserved. Job 26055 was cancelled before node allocation after review found it had a 120-second semantic warmup deadline and only two warmup threads for four P/D routes. Historical job 22219 took up to 150.55 seconds to warm all four routes. This revision starts all four route checks concurrently and grants up to 180 seconds. It does not change the model topology, runtime, request workload, score threshold, or GPU request.

The hypothesis is unchanged: replace a single TP8/EP8 decode worker with two TP4/EP4 replicas, preserving two TP4 prefill workers and aggregate decoder capacity 256 (128 per decode replica). Historical job 22219 used an earlier runtime and N40; its 1,666.01 good output tokens/s only motivates retesting. Current short target-only control 25947 scored 2,757.36 good output tokens/s.

The unranked screen uses 16 H200 GPUs, N64, fixed 4,000/200 requests, seed 2026, cold prefix cache, and the 20/40/30-second protocol. It requires four healthy workers, 32 before/after rank receipts, role-local runtime/KV/NIXL checks, four valid P/D semantic routes, >=90% joint SLA, zero errors/cancellations, 7/8 smoke and 12/12 retrieval. Official accuracy remains UNKNOWN.

Only advance to longer confirmation if all gates pass and throughput exceeds control 25947 by at least 3% (2,840.08 good output tokens/s). Otherwise retain the negative result and close the topology branch. See [plan](PLAN.md), [parent S62 bundle](../s62-h200-two-decode-tp4/), and [cancelled job receipt 26055](../SUBMISSION-26055.md).

Job 26064 reached worker readiness but failed on a validator NameError before benchmark start. Its 32 raw receipts were rechecked with the corrected role-aware validator and pass; the fix is in this immutable S62r3 derivative. No performance score exists for 26064. See the attached plan for limits.
