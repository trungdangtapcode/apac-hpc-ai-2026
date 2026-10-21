# Strict GPU identity component receipt

Submitted **222749.pbs111** at 2026-10-21T04:46:42.173024+00:00. One H100, four-minute ceiling, maximum 8.533333 SU; fresh own queue empty, no dependency needed. Payload/source and CPU strict UUID rejection checks pass. No component outcome, model inference or speedup is claimed at submission.

Fresh locked ledger: Used 43580.583, Balance 20419.417, In Doubt 0.000 SU. The previous two component charges uniquely reconcile: total 5.440 SU (89 + 64 seconds). The new full maximum remains reserved; internal headroom 7410.883667 SU under the unchanged 51000 cap and 13000 project buffer. Balance already excludes In Doubt. [Raw reconciliation](reconciliation.json).

Review the actual raw Torch/scheduler/nvidia-smi identity evidence, then native config and tensor stages. Even complete component success does not prove actual model loading, PD transfer or exact greedy outputs. [Plan](PLAN.md).
