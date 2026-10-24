# H200 EAGLE3 reaches real output, but fails the exact-token diagnostic

Job **25797** is **FAILED / exit 1:0 after 494 seconds**. The output gate was not skipped or reclassified as a pass. It collected **1,600 real candidate output token IDs**, two 200-token responses for each of four frozen prompts.

The portable draft-byte repair and narrow metadata correction now work in the actual deployment: every model rank initializes, all 32 registration before/after records pass, and both P/D semantic warmup paths return valid receipts. The candidate's native speculative counters are internally consistent in both passes for all four prompts. This establishes substantially more integration evidence than the earlier startup-only failures, but not a passing output result or a speedup.

Arithmetic matches the accepted target reference. Code and Unicode repeat consistently within EAGLE but differ from the target. The 4,000-token prompt differs both from the target and between the two EAGLE repetitions. `REVIEW.json` records exact first-divergence indices, lengths and native counters. Those observations do not identify whether the cause is floating-point order, draft verification, graph/backend behavior or a P/D state defect. Do not assume harmless numerical drift without a controlled check.

The local gate is deliberately stricter than the organiser's benchmark-score requirement. The retained official task FAQ explicitly compares full benchmark scores, not token-by-token output; the pass line is at least 99% of the organiser's own unchanged FP8-checkpoint score. A local exact-token failure therefore does not itself prove official accuracy failure. Conversely, these eight outputs cannot establish official accuracy. See `1. Qwen3 AI Task Rules.md`, Q1 and FAQ, lines215–252 in the retained source.

Next, source-qualify a matched deterministic target and EAGLE pair. SGLang's deterministic flag changes sampling and collectives, including disabling MNNVL, so compare against a newly qualified target reference using the same changes. Preserve 25585 and this failed run unchanged. The flag has no source-backed guarantee of deterministic HPC-Ops/EAGLE FP8 accumulation. The new experiment must be labelled diagnostic and must not be promoted as a performance winner.

Runtime/transport logs, phase markers, request responses/counters, role resource samples and geometry receipts are retained. Response-level comparison and logs were inspected; periodic hardware samples are collected but not independently summarized in this review. No AIPerf workload, SLA distribution, score, official full-set accuracy or heavy kernel profile was collected.

For a presentation: “We moved past initialization and transfer tests and obtained real speculative outputs. The strict comparison then exposed differences that need a matched numerical-control experiment. We preserve the failure and do not call the engine faster or accurate yet.”
