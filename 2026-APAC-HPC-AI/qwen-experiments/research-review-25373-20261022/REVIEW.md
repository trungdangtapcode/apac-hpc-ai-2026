# Independent full H200 N64 replication passes

Job **25373** completed with exit 0 in 643 seconds. All local payload/runtime, full 60/120/30 protocol, joint SLA, zero-error score, short-output non-regression and long retrieval 12/12 gates pass against full source 25366. Operational bytes are unchanged except job identity/configuration; resolved server arguments differ only in per-process random seed.

| Metric | Source 25366 | Independent repeat 25373 |
|---|---:|---:|
| Good output tokens/s | 3044.489701 | 3044.074628 |
| Joint-good / all scored requests | 1876 / 1902 | 1875 / 1901 |
| Joint SLA fraction | 98.633018% | 98.632299% |
| Errors / cancellations | 0 / 0 | 0 / 0 |
| TTFT mean / p95, ms | 1110.463377 / 1351.632306 | 1113.240102 / 1309.781135 |
| Request-mean ITL mean / p95, ms | 15.002881 / 15.163328 | 14.992752 / 15.159936 |

The repeat differs by **-0.013634%**; the two-run mean is **3044.282165 good output tokens/s**. This supports local repeatability of the N64 operating point, not a statistical confidence interval or global optimum. The N64 repeat is 1.069085% above the fresh observed N62 control 25365. Source and repeat use the same physical sampled GPU UUID sets, so hardware diversity remains limited.

All 26 failures breach TTFT; none breaches ITL. Keep all requests in the official score denominator. Nominal requested output is 200; export counts are 1896 at 200 and five at 199. Actual generated output token IDs were not retained for these performance records. Score remains exported AIPerf Goodput × 200.

The separate `observability.md` compares phase-aligned per-role hardware/server samples, tail latency and profile controls. It retains exact units and missing-data limits. Three profile starts return HTTP 200 and three stops HTTP 500 with profiling-not-in-progress; scored request errors remain zero. Trace filenames are retained; trace contents are uninspected. High GPU activity alone does not diagnose a compute or memory bottleneck.

**Official >=99% reference accuracy remains unverified.** Local smoke and retrieval are not MMLU-Pro/GPQA. N64 is now a reproduced local candidate for an explicitly reviewed AI submission update; frozen previous payloads remain unchanged. The distinct short N64/N68 screen still needs its own full review before fresh full N68 measurements. No N68 full score is claimed here.

Host CPU/network counters were collected by the resource observer but were not separately inspected in this full-repeat review; no CPU or network bottleneck conclusion is supported.
