# Actual-runtime tokenizer corpus receipt

**222759.pbs111**, submitted 2026-10-21T05:14:01.950230+00:00, initially R. One H100 reserved for at most four minutes/max 8.533334 SU; the probe performs CPU tokenizer operations only, no weight loading/inference/GPU math. Nine malformed normalization fixtures and JSON roundtrip pass before submission. [Exact protocol and limits](PLAN.md).

Fresh own queue empty and locked ledger Used 43586.876, Balance 19730.457, In Doubt 682.667 SU. Both later component charges uniquely reconcile; terminal 222752 remains unposted, so retain its full maximum plus the new maximum. Conservative internal headroom 6721.924000 SU, unchanged cap/buffer. [Reconciliation](reconciliation.json). No runtime corpus PASS at receipt.
