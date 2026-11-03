# Final full-quality run diagnostics — 3 November 2026

The completed fixed local study has candidate **9452/12032** and reference **9460/12032** correct, a matched retention ratio of **99.915433%** (-8 answers). The local 99% point threshold is met. This is not organiser BTC certification and does not identify a causal mechanism.

These eleven jobs cover candidate shard 2 and both roles on shards 3–7. Candidate shard 2 is paired to previously reviewed reference job 28386. Each displayed run has 1,504 questions. Response bodies were not printed.

## Per-job review

| Job | Role/shard | Correct | Invalid | Length cap | Errors | p50 / p95 / p99 / max latency (s) | sacct top-level | Paired retention |
|---:|---|---:|---:|---:|---:|---|---|---:|
| 28388 | candidate / 2 | 1167/1504 | 16 | 195 | 0 | 7.627 / 34.440 / 34.806 / 34.854 | COMPLETED 0:0, 00:11:27 | 100.0858% |
| 28390 | reference / 3 | 1175/1504 | 16 | 189 | 0 | 8.430 / 39.209 / 39.630 / 39.997 | COMPLETED 0:0, 00:10:27 | 99.2340% |
| 28392 | candidate / 3 | 1166/1504 | 20 | 186 | 0 | 7.189 / 34.430 / 34.812 / 34.846 | COMPLETED 0:0, 00:12:13 | 99.2340% |
| 28394 | reference / 4 | 1211/1504 | 12 | 162 | 0 | 8.402 / 38.986 / 39.749 / 40.537 | COMPLETED 0:0, 00:10:10 | 99.3394% |
| 28396 | candidate / 4 | 1203/1504 | 14 | 160 | 0 | 7.277 / 34.365 / 34.627 / 34.698 | COMPLETED 0:0, 00:10:45 | 99.3394% |
| 28398 | reference / 5 | 1149/1504 | 10 | 198 | 0 | 8.420 / 38.897 / 39.645 / 40.122 | COMPLETED 0:0, 00:10:29 | 100.3481% |
| 28400 | candidate / 5 | 1153/1504 | 8 | 200 | 0 | 7.485 / 34.526 / 34.768 / 34.830 | COMPLETED 0:0, 00:12:13 | 100.3481% |
| 28402 | reference / 6 | 1156/1504 | 11 | 189 | 0 | 8.654 / 39.044 / 39.419 / 40.105 | COMPLETED 0:0, 00:10:30 | 101.1246% |
| 28404 | candidate / 6 | 1169/1504 | 10 | 178 | 0 | 7.511 / 34.477 / 34.682 / 34.810 | COMPLETED 0:0, 00:11:08 | 101.1246% |
| 28406 | reference / 7 | 1197/1504 | 6 | 196 | 0 | 8.718 / 39.250 / 39.518 / 40.274 | COMPLETED 0:0, 00:10:34 | 98.9975% |
| 28408 | candidate / 7 | 1185/1504 | 10 | 186 | 0 | 7.499 / 34.473 / 34.709 / 34.809 | COMPLETED 0:0, 00:12:38 | 98.9975% |

## Collected and inspected

For each row, the review inspected the complete evaluation and validity receipt, non-stream response metadata without exposing answer content, reported token usage, prompt/generation settings, selected worker/router/client logs, and the native top-level `sacct` allocation record. Candidate worker logs cover both prefill workers and the decode worker; selected router transport logs were checked. Reference replica, router, and client logs were checked. Exact run/response hashes, log hashes, software settings, and per-run details are in `FINAL_DIAGNOSTICS.json`. Candidate package versions and image hashes are retained. The reference provenance identifies stock TP8/EP8 settings and model metadata hashes, but omits explicit runtime version strings and image digests; these are not inferred.

All runs have complete coverage, HTTP 200 for all 1,504 responses, zero service errors, and no deadline-skipped rows. Selected worker/router/client logs contain no Python traceback or ERROR/FATAL lines. Non-stream request p95 is about 34–35 seconds for the candidate and 39–40 seconds for the reference; total request latency cannot be interpreted as TTFT or ITL. Outputs ending at the 2,048-token generation cap range from 160 to 200 per shard. Invalid answer parses range from 6 to 20 per shard; the pinned scorer counts them incorrect. Token usage is server-reported and not an independent token recount.

All top-level scheduler records are `COMPLETED`, exit `0:0`, allocating 16 GPUs across two nodes. Elapsed allocation time ranges from 10:10 to 12:38. Child-step cancellation entries are cleanup behavior; the top-level jobs completed successfully.

## Limits and decision

GPU utilization, power, memory/bandwidth, bounded CPU telemetry, and quantitative queue/KV time series were not collected. The result is a local matched point estimate on the fixed MMLU-Pro corpus; it does not give a confidence guarantee, certify the organiser BTC evaluator, or identify a causal mechanism. Retain the run evidence and report the local ratio with these limits.
