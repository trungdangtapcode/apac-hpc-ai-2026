# Public scheduler labels are leads, not results

The owner pointed to team 01's full queue. This snapshot preserves public job names and scheduler outcomes only. We did not inspect their private files or outputs and have no performance or leaderboard data for them. A completed job is not necessarily a valid benchmark; a larger version number is not a count of improvements.

Labels such as `11to5`, `DP5`, `130` and `13to3-fp8kv` suggest uneven prefill/decode splits, five-way data/expert distribution and padded expert slots, or an FP8 KV branch. Those are hypotheses inferred from labels. They do not establish the exact code, engine, settings, quality or speed. Prefixes `ce`, `px` and `lor1` remain unexplained.

Our corresponding work uses independently retained source and experiments: native expert arithmetic, actual five-rank startup and its vocabulary failure, the native DP LM head correction, and a measured FP8 cache comparison. The FP8 cache candidate passed local gates but lost 3.52239% on our H200 short protocol. That result applies to our configuration, not to theirs. The new topology remains under qualification; no competitor score comparison is supported.
