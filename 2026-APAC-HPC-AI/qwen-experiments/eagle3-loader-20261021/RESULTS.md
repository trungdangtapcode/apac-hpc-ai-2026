# Native draft loader receipt

**222750.pbs111**, submitted 2026-10-21T04:51:00.212783+00:00. One H100 / four minutes / max 8.533334 SU. Fresh own queue empty, no dependency. Locked ledger Used 43580.583, Balance 20419.417, In Doubt 0.000 SU. Retain both the unposted 222749 maximum and this new maximum; conservative headroom 7402.350333 SU. No cap/buffer increase. [Reconciliation](reconciliation.json).

This allocation tests actual native class construction and exact published-weight consumption/value coverage, with the absent target-shared embedding explicitly excluded and no forward executed. [Prospective acceptance and limitations](PLAN.md). There is no loader result or speedup at submission.

## Native draft load PASS — 2026-10-21T04:54:38.656130+00:00

F / exit 0, 99 seconds / estimated 3.520000 SU. Native class constructs; all 13 floating tensors cover 10 non-shared parameters exactly; hot-token map matches. Sole absent parameter is target-shared embedding, never used for inference here. [Review](REVIEW.md).
