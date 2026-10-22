# Phase-aligned observability: full H200 N64 control and N64

This offline review compares completed job 25366 (N64 control) with job 25373 (N64). Both used the fresh full-protocol matched pair and the same resource observer. It reads retained run artifacts only. The scoring window comes from each AIPerf phase manifest; nominal five-second telemetry windows are included only when wholly inside that interval. Benchmark start/end markers enclose the AIPerf phase.

## Scored results

| Job | Client concurrency | Good output tokens/s | Good request fraction | Scored requests | Errors / cancellations | TTFT mean / p95 (ms) | Request-mean ITL mean / p95 (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 25366 | 64 | 3044.490 | 0.986330 | 1902 | 0 / 0 | 1110.5 / 1351.6 | 15.003 / 15.163 |
| 25373 | 64 | 3044.075 | 0.986323 | 1901 | 0 / 0 | 1113.2 / 1309.8 | 14.993 / 15.160 |

N64 is -0.014% (-0.415 good output tokens/s) versus N64 control, in one completed pair. This is descriptive evidence only; it does not establish repeatability or identify a cause.

## Role telemetry during scoring

The table shows sample counts, status coverage, and the average of per-GPU sample means within each role. The range is across GPU means, not individual sample minima and maxima. Gauge summaries pool observations across labeled series without summing the series; detailed per-series distributions and per-GPU values are in `observability.json`.

| Job | Role | In-window samples | GPU status | Server HTTP status | Metrics payloads | GPU activity mean (range, %) | Sampled VRAM mean (range, MiB) | Power mean (range, W) |
|---|---|---:|---|---|---:|---:|---:|---:|
| 25366 | prefill-0 | 23 | {'ok': 23} | {'200': 23} | 23 | 95.9 (95.5–96.4) | 133332.0 (132996.0–133476.0) | 685.3 (683.8–687.2) |
| 25366 | prefill-1 | 23 | {'ok': 23} | {'200': 23} | 23 | 96.6 (96.0–97.3) | 133334.0 (132998.0–133478.0) | 687.4 (683.4–689.0) |
| 25366 | decode-0 | 24 | {'ok': 24} | {'200': 24} | 24 | 100.0 (100.0–100.0) | 134433.8 (134025.5–134505.5) | 473.9 (464.8–480.5) |
| 25373 | prefill-0 | 24 | {'ok': 24} | {'200': 24} | 24 | 92.1 (91.6–92.3) | 133330.6 (132994.6–133474.6) | 663.8 (662.5–664.7) |
| 25373 | prefill-1 | 23 | {'ok': 23} | {'200': 23} | 23 | 96.5 (96.0–96.9) | 133332.0 (132996.0–133476.0) | 684.3 (681.1–686.2) |
| 25373 | decode-0 | 24 | {'ok': 24} | {'200': 24} | 24 | 100.0 (100.0–100.0) | 134348.8 (133940.5–134420.5) | 474.0 (464.7–480.7) |

SGLang gauges captured in-window:

| Job | Role | Running requests / series | Queue requests / series | Token usage fraction | Used tokens / series |
|---|---|---:|---:|---:|---:|
| 25366 | prefill-0 | 3.0 (2.0–4.0) | 0.7 (0.0–2.0) | 0.020 (0.020–0.020) | 26528 (23948–28374) |
| 25366 | prefill-1 | 2.7 (1.0–3.0) | 0.2 (0.0–3.0) | 0.020 (0.010–0.020) | 25656 (19958–27533) |
| 25366 | decode-0 | 50.3 (28.0–54.0) | 0.0 (0.0–0.0) | 0.117 (0.050–0.120) | 252372 (116089–260955) |
| 25373 | prefill-0 | 2.8 (0.0–3.0) | 0.2 (0.0–1.0) | 0.018 (0.000–0.020) | 23606 (0–27560) |
| 25373 | prefill-1 | 2.7 (2.0–4.0) | 0.2 (0.0–1.0) | 0.020 (0.010–0.020) | 25509 (20168–28165) |
| 25373 | decode-0 | 51.0 (31.0–56.0) | 0.0 (0.0–0.0) | 0.117 (0.060–0.120) | 251557 (120147–261224) |

Counts are per labeled TP/PP/EP series. They are not totals across ranks, and client concurrency is not presented as a server batch size. There was no in-window inflight-request gauge. The run-specific UUIDs and per-GPU readings are retained in JSON; these are sampler-reported role mappings, not independent process-locality proofs.

## Tail, errors and profiler controls

Job 25366: scored request records show 0 errors and 0 cancellations. TTFT p99/max was 3487.5/4768.3 ms, with 26/1902 over 3000 ms; request-mean ITL p99/max was 15.896/16.304 ms, with 0/1902 over 20 ms. Diagnostic profiler start returned HTTP 200, 200, 200; all three profiler stop requests returned HTTP 500. Each role log ends this traceback with `RuntimeError: Profiling is not in progress. Call /start_profile first.`. The profile-control failure is therefore a control-path failure, separate from the zero scored-request error count. Collected trace files by role: {'prefill-0': 4, 'prefill-1': 4, 'decode-0': 8}. Trace contents were not inspected; exact filenames are in JSON.
Job 25373: scored request records show 0 errors and 0 cancellations. TTFT p99/max was 3481.7/4770.2 ms, with 26/1901 over 3000 ms; request-mean ITL p99/max was 15.725/16.429 ms, with 0/1901 over 20 ms. Diagnostic profiler start returned HTTP 200, 200, 200; all three profiler stop requests returned HTTP 500. Each role log ends this traceback with `RuntimeError: Profiling is not in progress. Call /start_profile first.`. The profile-control failure is therefore a control-path failure, separate from the zero scored-request error count. Collected trace files by role: {'prefill-0': 4, 'prefill-1': 4, 'decode-0': 8}. Trace contents were not inspected; exact filenames are in JSON.

## Limits

- Nominal telemetry intervals conservatively bound sample timestamps but do not guarantee that every NVML activity value covers precisely that full interval.
- Sparse samples do not establish peaks. GPU activity, sampled VRAM, power and SGLang token/KV gauges are distinct quantities.
- Gauge counts are per labeled TP/PP/EP series and are never summed across ranks; no inflight gauge was present. Client concurrency is not asserted to equal server batch size.
- Missing fields and failed scrapes are reported by status or absence and are never interpreted as zero or healthy.
- The offline review does not inspect compressed trace contents; it records filenames only. Official model accuracy remains outside these artifacts.

Reproduce with `python3 observability.py` from this directory. The script writes only `observability.json` and `observability.md`; it performs no scheduler or network calls.
