# Production-span pilot submission

Submitted 23 October 2026 at 13:08:26 UTC as **224116.pbs111**. The immediate scheduler receipt reports **R**, physical hosts **a2ap-dgx036 / a2ap-dgx037**, one H100 per host, 28 CPU cores total and ten minutes maximum. Requested `normal` is routed by PBS to `aiq1`; this is a scheduler observation, not a queue modification.

This is a no-model full-span registration and sparse byte-transfer diagnostic, not a scored inference run. See [PLAN.md](PLAN.md), [root review](ROOT_REVIEW.json) and [definite receipt](pbs-receipt.json). No GPU result is claimed at submission. The frozen payload was backed up and pushed as `0df6566b` before submission.

The locked preflight found an empty selected AI queue and Used 46,449.630 SU / Balance 17,550.370 SU / In Doubt negative zero (numerically zero). Reserve at most **42.666667 SU**; internal headroom after reservation **4,507.703333 SU** under the unchanged 51,000 SU cap and 13,000 SU project reserve. Published balance is a dated pre-submission snapshot, not final charge. Preserve the maximum until terminal and uniquely posted reconciliation.

The existing authenticated SSH path handled upload, selected queue/credit checks and qsub successfully. No new VPN or DUO authentication was attempted. H200 25682 remains separately pending resources, unchanged.
