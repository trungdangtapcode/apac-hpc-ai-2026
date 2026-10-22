# 22 October: short N68 gain supports full matched confirmation

Job 25371 tests N64 then N68 in the same observed deployment with 20/40/30 timing and unchanged serving/runtime settings. Both points pass strict local protocol/runtime/payload, SLA, zero-error, output non-regression and long retrieval 12/12 gates. N68 scores 2895.054081 versus 2830.699360 good output tokens/s, +2.273457%, exceeding the preset 1% short gate.

N68 increases TTFT mean/p95 to 1347.803/2725.915 ms from 1228.656/2697.459 ms; request-mean ITL is 15.040 versus 14.909 ms. Joint SLA is 95.8904% versus 95.9311%, with 27 versus 26 TTFT breaches, no ITL breaches and zero request errors/cancellations. Keep every request in the denominator. This fixed-order short result is unranked and cannot be compared directly with full N64 throughput.

Actual scored-window decode log running-request maxima are 58 versus 54, below the unchanged graph cap 64. Sampled role metrics, hardware activity/VRAM/power, approximate host counters, tails and profile controls are inspected with explicit limits. Three profile stops return HTTP 500 outside scoring. Trace filenames are inventoried; contents remain uninspected. No causal bottleneck or official accuracy claim is made.

The first root preparation stopped safely at a schema guard: the agent's computed true gate conflicted with stale literal interpretation and differing state/key names. Root corrected the derived review contract and made interpretation depend on computed gain, preserving raw evidence and thresholds. The formal replay now passes. See VALIDATION_CORRECTION.md; no GPU job was created by the failed preparation.

Next freeze a fresh full N64 control and N68 candidate, each at most 17 minutes/16 H200 GPUs, serial afterok, no PBS SU. Require full local gates and at least 1% matched full gain before N68 replication. Official >=99% reference accuracy remains unverified.
