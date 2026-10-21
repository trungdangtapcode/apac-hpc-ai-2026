# Native EAGLE3 PD correctness submission

**222763.pbs111**, submitted 2026-10-21T05:39:09.523920+00:00, initial state R. **16 H100 / at most 30 minutes / maximum 1024 SU**. Fresh owned queue empty, no dependency or overlapping allocation. The accepted real target reference is **222761**, four exact generic cases with 1600 output IDs. Native single-rank draft weight loading passed separately in 222750.

The new frozen payload enables native EAGLE3 on both phases with the pinned public BF16 draft, two draft steps/topk1/three verification slots and FlashInfer draft attention. Target weights, saved input IDs, target identity and request-scoped NIXL transport remain unchanged. Nine reference-derived guard fixtures pass, including same text/different IDs and changed identity/platform. These are CPU fixtures, not candidate inference. [Plan and remaining runtime gates](PLAN.md), [guard validation](semantic-validation.json).

Locked pre-submit ledger: Used **43965.542**, Balance **19351.791**, In Doubt **682.667 SU**. 222752 and 222759 uniquely reconcile, total **378.666 SU**. Retain unposted 222761 full maximum plus this 1024 SU maximum; conservative internal headroom **5327.791333 SU**, unchanged 51000 cap / 13000 project buffer. [Structured reconciliation](reconciliation.json). Balance already excludes In Doubt; do not subtract twice or release maxima merely from estimated cost.

No full-target speculative runtime/ID result or throughput score exists at submission. Inspect actual loading, target embedding/auxiliary/TP4-to-TP8 state/KV/verification graphs/memory and exact output IDs. Prefill capacity may resolve 48 versus baseline4096; N1 correctness cannot be sold as matched throughput. Only a valid useful bounded load permits full scoring. Keep five H200 queue positions, no background AI/schedules or submission-material changes.

## Terminal native integration FAILED — 2026-10-21T05:49:28.124067+00:00

F/exit1, 408 seconds/estimated 232.106667 SU. Draft decode graph fails at input RMSNorm dtype; target KV BF16/draft KV FP16. No request or score. [Evidence, correction and cheaper next gate](REVIEW.md).
