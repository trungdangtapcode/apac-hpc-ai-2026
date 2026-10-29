# 29 October: close the full transfer polling bracket

Written 29 October 2026, Vietnam time (UTC+7), after actual terminal inspection.

**Question and controlled change.** Can less frequent decode KV-completion polling reduce overhead without delaying admission? Full source-qualified intervals1/2/4 keep requested N64 cold4000/200 seed2026/full60/120/30, target-only model/topology/precision and all original gates. Actual engine seeds are auto-generated and vary; workload seed2026 is separate. The configured intervention is one factor, but this is not deterministic/seed-matched execution.

**Complete observations.** Control27270=3039.053386 good output tokens/s; interval2/27272=3028.279635, −0.354510%; interval4/27274=3016.700285, −0.735528%. All three are terminal COMPLETED0:0 full local passes with zero errors/cancellations, smoke7/8 without regression and retrieval12/12. Joint good fractions are98.527865%,98.625793%,98.622152%; TTFT breaches28/26/26 and no ITL breaches. Official accuracy remainsUNKNOWN.

**Final arm inspection.** 27274 completes in11:34 on g1/g4. TTFT mean/p95/p99/max is1132/1356/3494/4776ms; request-meanITL is15.088/15.342/15.965/17.118ms. Twenty-four sparse scored-envelope decode samples show49.875 mean running,max54,queue0 and meanKVtokenusage0.1192. Source guards/runtime/KV/two-route checks pass;72role pollsHTTP200,no selected transport errors or Python tracebacks. Nonfatal InvalidHTTPwarnings are unassigned, not silently classified healthy. Hardware/CPU/power/temperature/VRAM observations and missing Xid/throttling/hot-thread/kernel coverage are retained with phase/clock limits. Client counts are text recounts, not actual model IDs; official multiplier200 stays.

**Assessment and decision.** Scores decline across the three point estimates, but each setting has one run and differences are below1%; latency tails are not monotone. Keep polling1 and close intervals2/4 without another sweep or causal claim. This branch closure does not stop independent cap64/cache/compile research already admitted. Actual allocation occupancy totals9.284444 GPU-hours versus maximum13.6, noPBS_SU. [Full review, raw seal and regeneration reader](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-transfer-poll-final-20261029/RESULTS.md).

**Preservation.** Final27274 raw requests/exports, complete frozen payload, logs, telemetry and accounting are sealed, with original failed/losing paths retained. Capture this review separately; Git does not upload sibling external object bytes. HPC/submission/authentication/background automation are unchanged.
