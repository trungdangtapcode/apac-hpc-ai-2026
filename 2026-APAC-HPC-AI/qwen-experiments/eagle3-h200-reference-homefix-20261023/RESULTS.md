# Terminal accepted H200 reference — 23 October

**25585 is accepted**, terminal COMPLETED/0:0, elapsed 458 seconds. All 8 real native responses contain 1600 actual output IDs, including the first token; four A/B pairs agree exactly in request, complete IDs and finish. Both independent semantic P/D receipts, complete 4+4+8 BF16 rank records, pre-worker/result asset identity, actual head result and independent post-run head replay pass. Worker/router ready at 328 s, both paths initialized at 368 s, exact reference gate at 452 s from allocation start. [Full sealed review](../research-review-25585-20261023/REVIEW.md).

The repair fixes the actual missing HOME prerequisite demonstrated by 25495. It does not demonstrate EAGLE3 correctness, throughput, official accuracy or cold-cache N1 latency; second-pass prefix reuse and startup-only telemetry limits are retained. Full KV region geometry is not collected in this target-only reference. A separately reviewed speculative correctness candidate may now be derived against these exact actual IDs.

## Historical submission record

# Repaired native H200 reference submitted

Definite scheduler receipt: **25585**, submitted 2026-10-23T04:06:12.208938+00:00, native Slurm bundle `s38-h200-target-reference-homefix`. It requests 16 H200 GPUs across 2 nodes for at most 17 minutes, no PBS SU, no dependency on a scored run. [Actual receipt](slurm-receipt.json). The first post-submit snapshot is pending/Resources; query Slurm for live state.

This repairs the proven missing token-client HOME prerequisite of failed 25495. The source job reached all workers and passed both independently replayed semantic P/D receipts but captured no actual reference IDs. The repaired bundle changes only that directory creation plus job/config provenance; all target, transport, precision, client/corpus and absolute budgets remain unchanged. The old-source/repaired actual shell regression and four asset-bound client/head tests pass; actual Pyxis/GPU outcome is pending.

Require 8 complete real responses/1600 output IDs, repeat equality, independent head acceptance, complete 4+4+8 BF16 records and both semantic P/D receipts before accepting this reference. Do not treat COMPLETED alone as success. There is no EAGLE3 run, throughput score or official accuracy result. A supported terminal result determines the next candidate or concrete repair; no unchanged duplicate or background automation is armed.
