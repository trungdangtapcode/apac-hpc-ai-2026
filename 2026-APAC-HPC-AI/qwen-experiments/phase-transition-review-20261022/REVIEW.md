# SLA failures belong to the initial profiling cohort

Reviewed 2026-10-22T00:20:57.655133+00:00, using sealed raw request timestamps and phase manifests.
The scoring definition and all scored requests are retained unchanged.

| Run / load | All scored requests | TTFT failures | Failed requests' latest start after profiling begins | Later failures |
|---|---:|---:|---:|---:|
|24962 full N62|1885|24|37.15 ms|0|
|24964 full N60|1856|22|35.09 ms|0|
|25339 short N62|632|24|38.52 ms|0|
|25339 short N64|649|22|37.79 ms|0|
|25365 full N62|1879|24|35.44 ms|0|

In each point, the first100 ms contains exactly the offered concurrency's number
of requests. Every observed joint-SLA failure starts in this initial cohort;
there are no request-mean ITL breaches or request errors in these observations.
The timestamp is the client's actual request_start_ns relative to the manifest's
profiling start, not the response completion or server kernel start time.

This localizes the observed failures to the start-of-phase cohort. It does not
identify the hardware/queue/kernel cause, prove later workloads never fail, or
make a request eligible for exclusion. All failures continue to count in official
goodput and the joint-good fraction. Score is exported goodput × nominal200.

If the full-run duration and all request counts were unchanged, recovering all
these failures could increase goodput by only about1.20–1.29% in the full runs;
the corresponding arithmetic ceiling is3.51–3.95% in the shorter screens. These
are ceilings under fixed observations, not achievable speedup forecasts. The
shorter window magnifies a fixed initial cohort's impact, reinforcing why the
accepted short N64 gain still needs a full matched confirmation.

The next server-side question is initial-burst handling under the current stack.
Backend/resource-split interactions may be distinct from old topology results,
but any test must account for the lost decode capacity and pass actual native
support, memory, output and SLA gates. Current full N64 is already in flight;
no client timing, dataset, seed, prefix behavior or denominator is changed here.
[Reproducible timestamp/count inspection](review.py) preserves the exact evidence.
