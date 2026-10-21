# Short observed H200 N62 to N64 frontier within the real time limit

The exact independent N62 repeat 24962 passes full gates at 3023.072304 good
output tokens/s, within 0.034327% of 24915. Both have about 98.727% joint-good,
zero errors/cancellations and mean/p95 request-mean ITL around 14.97/15.13 ms.
Dense decode graph sizes stop at 64, making N64 a justified next load boundary.
No N64 benefit or global optimum is assumed.

The original full two-point 22-minute request 25338 was rejected by the actual
17-minute partition limit and cancelled while pending with zero GPU runtime.
Preserve that failed plan/receipt; do not modify its frozen payload. This fresh
bundle instead measures a short, unranked pair on one deployment: **N62 then
N64, each 20-second warmup / 40-second measurement / 30-second grace**. Every
other AIPerf workload/data/seed/streaming/latency flag stays unchanged, fixed
4000/200, seed 2026, cold prefixes. Results live under screen/n62 and screen/n64,
so they cannot silently be mistaken for full confirmed scores.

Both points have identical native serving and observation: two TP4 DeepGEMM /
chunk 8192 prefills, TP8/EP8 HPC-Ops decode with dense 1..64 graphs, FlashInfer,
MNNVL, round_robin, public FP8 target / BF16 KV, NIXL and the same bounded
sampler/phase markers. The source is frozen observed 24964. Only within-job
concurrency changes between the two points. Use fresh observed N62 as control;
older observer-off 24962 is context, not an overhead-corrected comparison.
Four actual-shell gate fixtures ensure control SLA/error failure stops N64,
both points run on a valid control, and insufficient time defers work.

One allocation requests 16 H200 / two nodes / at most 17 minutes. Validate the
actual hpcai MaxTime and own live queue under watcher.lock before sbatch;
preserve 24964/24965/25051/25283 and stay within cap five. No PBS SU, changed
budget, uncertainty retry or background schedule. Sharing startup makes this
short pair economical; unchanged post-score/output diagnostics remain bounded
by the existing deadline. Missing/deferred required output evidence invalidates
the screen; never count scheduler completion alone.

Before a later full-duration matched pair, require zero errors/cancellations,
joint SLA >=0.90 on both, complete raw short protocol/runtime/output gates and
at least 1% canonical goodput gain on N64 versus same-job N62. Inspect relevant
latency tails, effective concurrency, role queues/KV and phase-aligned samples.
Samples are sparse; no causal CPU/GPU/network claim follows. A lesser/negative
screen closes this exact unchanged load increase. A gain only permits full
60/120/30 confirmation with a fresh matched observer control when queue/budget
allow; it does not update the 3023.072304 full-score incumbent. Order/thermal
confounding needs independent or reversed confirmation. Official >=99%
reference accuracy remains unverified.
