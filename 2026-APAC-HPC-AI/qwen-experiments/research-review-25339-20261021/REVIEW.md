# Short matched N64 screen warrants full confirmation

Reviewed 2026-10-21T23:55:57.519836+00:00. Job **25339** completes with exit0 in 617 seconds. Both short
20-second warmup / 40-second measurement / 30-second grace points pass frozen
payload and raw protocol checks, independent per-request joint threshold
classification and zero errors/cancellations.

| Same deployment | Good output tokens/s | Joint-good / total | TTFT mean / p95 (ms) | Request-mean ITL mean / p95 (ms) |
|---|---:|---|---|---|
| N62 |2811.316116|608 / 632 (96.202532%)|1143.755390 / 2554.557154|14.883168 / 15.200919|
| N64 |2891.760212|627 / 649 (96.610169%)|1132.299657 / 2453.747070|15.082836 / 16.050419|

N64 gains **2.861439%** over the same-job observed N62 control. Both exceed the
0.90 contest fraction gate. The 24 and 22 outside-SLA requests respectively are
TTFT breaches; no request-mean ITL breach is observed. Long retrieval passes 12/12
and inherited short output comparison has no new failures. These local checks
are not the official accuracy >=99% reference gate.

## Output length interpretation and review correction

The requested min_tokens and max_tokens are fixed at 200 with ignore_eos.
A strict offline assertion that every exported length equals 200 failed: N62 has
631 records at 200 and one at 199; N64 has 649 at 200. The earlier accepted full
24962 has 1883 at 200, one at 199 and one at 201; full 24964 also contains two
199 records. This is a recurring exported-length variation, not evidence that
the request settings changed in this screen. Actual generated token IDs are not
retained here, so a retokenization explanation is plausible but not proven.
Preserve the histograms and raw counters; do not claim every response has
exactly 200 server token IDs. Score with official exported goodput times the
fixed nominal 200, not raw output throughput times a fraction. No GPU failure
or payload mutation occurred during this offline review correction.

## Assessment and next decision

This is a short screening result, not a full ranking result. Fixed order and
shortened timing can affect initialization and tails. Observer-off best
24962=3023.072304 is not a matched comparator. The prospective 1% short gain gate
is met, supporting fresh equally observed full N62/N64 deployments, 60/120/30,
each within 17 minutes. No promotion before full checks and replication.

Telemetry, phase markers and role logs are retained with the sealed raw run;
this checkpoint validates scored raw protocol and outputs. Detailed hardware/
server demand inspection remains separate and must not be inferred from scores.
No official accuracy or measured hardware bottleneck is claimed.
