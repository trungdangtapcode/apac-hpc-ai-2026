# 23 October: submit the supported H200 reference launcher repair

**Question and prior evidence.** Failed 25495 reached native readiness and both actual semantic P/D routes, but its client container never started because the mounted role HOME did not exist. The old mock skipped mount checks. Preserve that failure and fix the concrete prerequisite rather than retry unchanged.

**Change and control.** New frozen `s38-h200-target-reference-homefix` adds one token-client HOME mkdir before its srun. The old-source/repaired actual launcher regression reproduces missing-mount exit 86 and reaches fake-client deliberate exit 7 only with the fix. All four asset-bound actual client/head tests pass. Worker, NIXL, model/image, TP/EP, precision, corpus, request fields and deadline bytes remain unchanged; no Pyxis/GPU success is inferred from mocks.

**Actual submission.** **25585**, definite receipt 2026-10-23T04:06:12.208938+00:00, 16 H200/two nodes, maximum 17 minutes, zero PBS SU. Lock, real own queue cap, partition limit, source accounting/review, current asset preflight and frozen SHA checks passed. No uncertain retry. [Receipt and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-h200-reference-homefix-20261023/RESULTS.md).

**Assessment and next decision.** Pending is not an accepted reference. Require all 1600 actual output IDs, exact A/B equality and independent semantic replay, all rank BF16 receipts and both P/D paths. Only a terminal accepted H200 reference permits EAGLE3 derivation. Another failure needs concrete review and supported repair, not a duplicate. No performance or official accuracy result yet.

**Preservation.** Repair/frozen source was committed before submission. Capture actual receipt/status/provenance as a separate checkpoint; do not include credentials, weights or the separate HPC track.
