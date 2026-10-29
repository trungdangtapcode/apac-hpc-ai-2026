# Partial polling bracket: interval 2 does not improve throughput

Reviewed 2026-10-29T16:09:37.025490+07:00, Vietnam time (UTC+7). Jobs 27270 and 27272 are terminal full local passes. Interval 4 job 27274 remains pending at this observation. This is a partial bracket, not a final assessment of interval 4.

| Metric | Fresh interval 1 control 27270 | Interval 2 candidate 27272 |
|---|---:|---:|
| Good output throughput, tokens/s | 3039.053386 | 3028.279635 |
| Joint latency SLA, percent | 98.527865 | 98.625793 |
| Mean TTFT, ms | 1116.426668 | 1131.178721 |
| p95 TTFT, ms | 1312.170457 | 1421.698485 |
| Mean request-mean ITL, ms | 14.994943 | 15.013912 |
| p95 request-mean ITL, ms | 15.169025 | 15.224444 |
| time_to_first_token p99 / max, ms | 3531.333 / 4820.335 | 3491.686 / 4775.537 |
| inter_token_latency p99 / max, ms | 15.766 / 17.587 | 16.111 / 17.021 |
| request_latency p99 / max, ms | 6484.791 / 7823.616 | 6433.488 / 7770.540 |

27270 has 1874/1902 good requests, 28 TTFT and zero ITL breaches. 27272 has 1866/1892 good requests, 26 TTFT and zero ITL breaches. Both have zero errors/cancellations, smoke 7/8 without regression and retrieval 12/12. All original fixed-workload configuration, exact runtime/KV and both semantic route gates pass. The independent performance checker replays raw per-role interval validation. All three roles print the pinned transfer-source verification exactly once. Target-only weights and precision are unchanged. Official accuracy remains UNKNOWN.

## Interpretation and decision

Interval 2 is **-0.354510%** versus the fresh control, a small loss and below the predeclared >1% useful-gain gate. TTFT p95 increases from 1312.170 to 1421.698 ms; ITL changes little. Close the unchanged interval 2 arm, with no repeat or promotion. Interval 4 was prospectively admitted before either outcome; preserve its accepted position and review its eventual evidence separately. No additional interval sweep follows automatically.

## Beyond the score

Both runs contain 24 five-second decode samples in the first-to-last profiling-request start envelope: 192 GPU observations each. GPU activity is 100% and SM clock is 1980 MHz in every decode sample, with memory clock 3201 MHz and P0 throughout. Mean memory activity is 45.057% / 44.839%, mean power is 474.804 / 474.833 W per GPU and maximum temperature is 68°C in both runs. These are activity, clock, power and temperature observations; they are not FLOPS, percent of peak HBM bandwidth or a throttling diagnosis. Throttling reasons, Xid and per-process hot-thread saturation were not collected. No heavy kernel profile was collected.

Mean sampled decode running requests are 51.500 / 50.875, queue zero in both, KV token usage 0.1196 / 0.1192 and VRAM 131.112 / 131.208 GiB per decode GPU. Prefill queue sample maxima are 5 / 10. All 72 server polls per run return HTTP 200; selected transport error lines and Python traceback counts are zero. Startup connection failures remain in raw samples and are excluded from this scored-envelope summary. Cross-host clock skew is uncalibrated; the request-start envelope excludes final drain and is not exact phase-clock coverage.

## Newly inspected token accounting

The command and exported input configuration match the canonical requested synthetic 4000/200, zero configured length deviation, seed 2026, cold protocol, with min_tokens=max_tokens=200 and ignore_eos=true. However, raw AIPerf reports input_sequence_length 3986 or 3987, and output_sequence_length=199 for 4/1902 control rows and 5/1892 candidate rows; the rest report 200. Historical 26949 also has 2/1895 rows reported as 199.

A newly added diagnostic assertion that every reported output count is exactly 200 failed. It was not an original prospective acceptance gate. Preserve that failure explicitly in new-length-diagnostic-observation.json; do not change frozen gates or relabel the original protocol checks. The cause is not yet established from raw counters alone: actual generated IDs and authoritative per-request server usage are not retained here. A separate pinned AIPerf source review is investigating count provenance. Do not claim physical truncation, a tokenizer explanation or exact observed lengths without that source evidence. Official scoring continues to use exported Goodput × the organiser-fixed multiplier 200.

## Queue, cost and preservation

At the dated observation, 27274 has the combined pending reason referring to DOWN/DRAINED/higher-priority reservations. Both g1 and g4 actually report ALLOCATED, with no node drain reason. That message alone does not establish a node outage; preserve the job and query fresh state before further admission. The H100 helper reports no live VPN session; no MFA was prompted and current PBS queues/credit remain unknown.

Terminal allocation occupancies are 3.066667 GPU-hours for 27270 and 3.133333 for 27272, total 6.2, distinct from the 9.066667 maximum reservation for those two. Pending 27274 retains maximum 4.533334 GPU-hours. No PBS SU; allocation arithmetic is not a metered site charge. Raw profiles, per-request rows, complete frozen payloads, logs, hardware samples and terminal accounting are sealed in each run/artifact-manifest.json. pair-review-27270-27272.json contains all measured distributions. Git captures safe data/manifests; external object bytes still need separate off-host backup.

## Later source result, 29 October

Pinned client source confirms default client-side tokenization, with server usage counting not enabled in the retained configurations/CLI. This explains why the reported quantities are text recounts rather than actual server IDs, but does not prove the specific per-row cause of 199 or 3986/3987. Keep that cause unknown and preserve the new diagnostic failure. Official Goodput ×200 remains unchanged. [Source-bound report](../aiperf-token-accounting-20261029/REPORT.md).
