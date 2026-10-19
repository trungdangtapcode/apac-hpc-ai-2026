# Inference-mode submission receipts

Submitted at 2026-10-19T17:26:42.459884+00:00: **221923.pbs111 → 221924.pbs111**, explicit-default control followed by decode-only inference mode. Post-submit scheduler evidence confirms control Q (exclusive nodes currently in use), candidate H with `afterany:221923.pbs111`. Neither has a benchmark result at this checkpoint.

Both jobs have fixed N54, the same scored workload and all output/runtime gates, with a separate CPU/GPU profile after scoring. Frozen workers differ only in the decode inference-mode value; their source-hash and context activation preflights are identical. See [the hypothesis, sources and stopping rules](PLAN.md).

Published ledger at submission: Used **32604.728 SU**, Balance **31395.272 SU**, In Doubt **0**. Two maximum reservations total **3072 SU**, leaving **15323.272 SU** internal headroom under the unchanged 51000-SU cap and 13000-SU project buffer. These are maximum bounds, not actual charges. All previous four terminal charges were reconciled first. No overlapping 16-GPU allocation is allowed. A third active slot remains available for a separately justified hypothesis.

Raw qsub receipts, upload hash verification, pre/post scheduler snapshots, budget guards and frozen hashes are retained in this directory. Highest H100/H200 observations remain unchanged; no official accuracy, model promotion, slide change or automatic Codex schedule is claimed.
