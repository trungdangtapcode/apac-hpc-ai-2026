# 22 October: full N64 repeats within 0.014%

The question was whether the 1.082867% gain of full N64 source 25366 over matched observed N62 could repeat. Job 25373 uses a fresh full deployment, unchanged operational payload and 60/120/30 protocol. It passes all local protocol/runtime, SLA, zero-error, short-output and long 12/12 gates.

Source/repeat scores are 3044.489701/3044.074628 good output tokens/s, a repeat difference of -0.013634%; mean 3044.282165. Joint SLA is 98.633018%/98.632299%, errors and cancellations zero. Repeat TTFT mean/p95 is 1113.240102/1309.781135 ms; request-mean ITL mean/p95 is 14.992752/15.159936 ms. All 26 repeat failures breach TTFT; none breaches ITL. Exported counts 1896×200 and 5×199 remain distinct from nominal requested 200 and actual generated-ID proof.

The matched telemetry review and raw artifacts are retained under `research-review-25373-20261022` and `runs/25373`. Sampled GPU UUID sets match the source, limiting hardware diversity. Profile stop failures are diagnostic control errors, separate from the zero scored-request errors. Traces are inventoried, not causally interpreted.

This supports a reproduced local N64 point, not global optimality or official accuracy. Review the N68 short screen before a full N64/N68 pair; do not treat short throughput as a full score. N64 may be promoted through a separately reviewed AI submission update; keep the existing frozen primary unchanged until that milestone. Official >=99% reference accuracy remains unverified.
