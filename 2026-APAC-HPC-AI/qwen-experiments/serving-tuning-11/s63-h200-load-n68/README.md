# H200 closed-loop load screen at N=68

This unranked single-factor screen changes concurrency from the N64 baseline to N=68. It keeps the pinned S59 target-only serving topology, model, BF16 KV, P/D transport, sampling and batching settings, 4,000 input / 200 output tokens, seed 2026, and 20/40/30 second client protocol.

The reason to test this point is the earlier short N64-to-N68 sweep, which showed +2.27% good output throughput while passing the local latency gate. That was unranked and short; it motivates a controlled operating-point check, not a score claim. Historical full N64 remains 3,044.400475 good output tokens/s.

Gate: AIPerf joint good-request fraction >=90%, zero errors/cancellations, then the existing 7/8 output smoke and 12/12 retrieval checks. A run that misses a gate is preserved but is not a passing candidate. Official accuracy remains unknown; this is not an official ranking score. Compare good output tokens/s and TTFT/ITL distributions with N64 control 25947, while noting the control is not contemporaneous.

The four N66/N68/N70/N72 jobs form a bounded load sweep. Each is an independent frozen payload with one concurrency value. Do not promote from one point; retain the highest passing goodput point for a matched full-protocol confirmation.
