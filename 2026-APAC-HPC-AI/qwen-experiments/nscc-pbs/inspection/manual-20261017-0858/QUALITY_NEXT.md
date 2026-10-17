# Quality and profiling work remaining

Local contest task rules Q1 state organisers run a full-set accuracy check at
99% of their own unchanged official FP8 reference score. Checks include but are
not limited to model-card tasks and AIPerf checks. The exact organiser hidden
suite/reference numbers are not supplied here. Do not invent a mandatory
MMLU-Pro/GPQA-only suite or claim our12retrieval/8smoke checks prove99%accuracy.
Model-math/precision unchanged is supporting evidence, not a measured score.

Preserve official FP8 model, all experts/layers, BF16KV, exact NIXLgeometry patch
and versions. Keep short/long outputs plus source/runtime hashes for each
candidate. Accuracy99% remains unverified until full benchmark scores and an
appropriate official reference are available. No contest-material change here.

Next actionable H200 optimization: inspect post-score traces from24263 across
all16ranks. Compare new attention/collective/MoE timings to23607 only as kernel
summed diagnostic durations, not wall-clock percentages or guaranteed speedup.
Missing/deferred/failed profile means no new bottleneck inference. Use traces
to select one factor with source compatibility evidence and a fresh same-load
control;N58plateau alone does not justify blindN60.

Research completion percentages previously given in chat were subjective rough
work estimates, not a measured checklist or fraction of all possible configs.
This note supersedes any implication of objective60–70%completion.
