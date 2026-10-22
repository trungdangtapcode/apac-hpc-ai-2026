# Initial-cohort SLA analysis

This offline review uses sealed raw per-request exports and phase manifests. It preserves all scored requests, the official SLA thresholds and the exported Goodput × 200 score. Requests are classified jointly by TTFT at most 3000 ms and request-mean ITL at most 20 ms.

| Job / phase | Concurrency | Bad / total requests | Latest bad request start after profiling begins, ms | Requests started in first 100 ms | Arithmetic gain ceiling, % |
|---|---:|---:|---:|---:|---:|
| 24962 / confirm | 62 | 24 / 1885 | 37.154544 | 62 | 1.289629 |
| 24964 / confirm | 60 | 22 / 1856 | 35.087101 | 60 | 1.199564 |
| 25339 / screen | 62 | 24 / 632 | 38.518190 | 62 | 3.947368 |
| 25339 / screen | 64 | 22 / 649 | 37.792950 | 64 | 3.508772 |
| 25365 / confirm | 62 | 24 / 1879 | 35.444853 | 62 | 1.293801 |
| 25366 / confirm | 64 | 26 / 1902 | 33.481316 | 64 | 1.385928 |

Every bad request in these six observations belongs to the initial request cohort; none starts at or after 100 ms and none breaches ITL. Newly added full N64 job 25366 has 26 TTFT failures, all beginning by 33.481316 ms. Its arithmetic ceiling from recovering those requests alone, at unchanged duration and total request count, is 1.385928%. The earlier full points have ceilings about 1.20–1.29%; short windows have larger proportional ceilings. These calculations are not achieved improvements or speedup forecasts.

This localizes the failing cohort, not a causal GPU diagnosis. The first cohort can include server queues, prefill work, transport and decode startup. Sparse server/GPU samples cannot separate those causes at millisecond resolution. Do not delete these requests, extend warmup, stagger official arrivals or otherwise alter the scoring protocol to improve the reported fraction. Investigate supported server-side behavior while retaining the same client workload and denominator.

The immediate measured improvement is full N64 versus matched N62, not recovered TTFT failures. Independent full N64 replication and a short N64/N68 screen are submitted separately. The P12/D4 proposal is withheld pending an equal-TP NIXL whole-pool descriptor assessment; it is not evidence of a prefill bottleneck or a measured failure.

Reproduce with `python3 review.py`. The script checks raw hashes against the terminal manifests before classifying every scored request. Detailed start offsets and latencies remain in `REVIEW.json`.
