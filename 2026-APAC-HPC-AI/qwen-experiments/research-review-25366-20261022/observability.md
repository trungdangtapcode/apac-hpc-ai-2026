# Phase-aligned observability: full H200 N62 and N64

This offline review compares completed job 25365 (N62) with job 25366 (N64). Both used the fresh full-protocol matched pair and the same resource observer. It reads retained run artifacts only. The scoring window comes from each AIPerf phase manifest; nominal five-second telemetry windows are included only when wholly inside that interval. Benchmark start/end markers enclose the AIPerf phase.

## Scored results

| Job | Client concurrency | Good output tokens/s | Good request fraction | Scored requests | Errors / cancellations | TTFT mean / p95 (ms) | Request-mean ITL mean / p95 (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 25365 | 62 | 3011.875 | 0.987227 | 1879 | 0 / 0 | 1037.6 / 1316.5 | 14.958 / 15.209 |
| 25366 | 64 | 3044.490 | 0.986330 | 1902 | 0 / 0 | 1110.5 / 1351.6 | 15.003 / 15.163 |

N64 is +1.083% (+32.615 good output tokens/s) versus N62, in one completed pair. This is descriptive evidence only; it does not establish repeatability or identify a cause.

## Role telemetry during scoring

The table shows sample counts, status coverage, and the average of per-GPU sample means within each role. The range is across GPU means, not individual sample minima and maxima. Gauge summaries pool observations across labeled series without summing the series; detailed per-series distributions and per-GPU values are in `observability.json`.

| Job | Role | In-window samples | GPU status | Server HTTP status | Metrics payloads | GPU activity mean (range, %) | Sampled VRAM mean (range, MiB) | Power mean (range, W) |
|---|---|---:|---|---|---:|---:|---:|---:|
| 25365 | prefill-0 | 24 | {'ok': 24} | {'200': 24} | 24 | 96.5 (95.8–97.5) | 133334.0 (132998.0–133478.0) | 686.1 (684.9–687.0) |
| 25365 | prefill-1 | 24 | {'ok': 24} | {'200': 24} | 24 | 92.4 (90.5–93.4) | 133331.9 (132995.9–133475.9) | 677.0 (673.2–680.0) |
| 25365 | decode-0 | 24 | {'ok': 24} | {'200': 24} | 24 | 100.0 (100.0–100.0) | 134316.2 (133908.0–134388.0) | 473.1 (466.3–479.6) |
| 25366 | prefill-0 | 23 | {'ok': 23} | {'200': 23} | 23 | 95.9 (95.5–96.4) | 133332.0 (132996.0–133476.0) | 685.3 (683.8–687.2) |
| 25366 | prefill-1 | 23 | {'ok': 23} | {'200': 23} | 23 | 96.6 (96.0–97.3) | 133334.0 (132998.0–133478.0) | 687.4 (683.4–689.0) |
| 25366 | decode-0 | 24 | {'ok': 24} | {'200': 24} | 24 | 100.0 (100.0–100.0) | 134433.8 (134025.5–134505.5) | 473.9 (464.8–480.5) |

SGLang gauges captured in-window:

| Job | Role | Running requests / series | Queue requests / series | Token usage fraction | Used tokens / series |
|---|---|---:|---:|---:|---:|
| 25365 | prefill-0 | 2.3 (0.0–3.0) | 0.1 (0.0–2.0) | 0.018 (0.000–0.020) | 22823 (0–27935) |
| 25365 | prefill-1 | 2.2 (0.0–4.0) | 0.0 (0.0–0.0) | 0.018 (0.000–0.020) | 22009 (0–27940) |
| 25365 | decode-0 | 51.4 (48.0–56.0) | 0.0 (0.0–0.0) | 0.116 (0.100–0.120) | 247009 (224758–253045) |
| 25366 | prefill-0 | 3.0 (2.0–4.0) | 0.7 (0.0–2.0) | 0.020 (0.020–0.020) | 26528 (23948–28374) |
| 25366 | prefill-1 | 2.7 (1.0–3.0) | 0.2 (0.0–3.0) | 0.020 (0.010–0.020) | 25656 (19958–27533) |
| 25366 | decode-0 | 50.3 (28.0–54.0) | 0.0 (0.0–0.0) | 0.117 (0.050–0.120) | 252372 (116089–260955) |

Counts are per labeled TP/PP/EP series. They are not totals across ranks, and client concurrency is not presented as a server batch size. There was no in-window inflight-request gauge. The run-specific UUIDs and per-GPU readings are retained in JSON; these are sampler-reported role mappings, not independent process-locality proofs.

## Tail, errors and profiler controls

Job 25365: scored request records show 0 errors and 0 cancellations. TTFT p99/max was 3466.5/4504.5 ms, with 24/1879 over 3000 ms; request-mean ITL p99/max was 15.678/16.938 ms, with 0/1879 over 20 ms. Diagnostic profiler start returned HTTP 200, 200, 200; all three profiler stop requests returned HTTP 500. Each role log ends this traceback with `RuntimeError: Profiling is not in progress. Call /start_profile first.`. The profile-control failure is therefore a control-path failure, separate from the zero scored-request error count. Collected trace files by role: {'prefill-0': 4, 'prefill-1': 4, 'decode-0': 8}. Trace contents were not inspected; exact filenames are in JSON.
Job 25366: scored request records show 0 errors and 0 cancellations. TTFT p99/max was 3487.5/4768.3 ms, with 26/1902 over 3000 ms; request-mean ITL p99/max was 15.896/16.304 ms, with 0/1902 over 20 ms. Diagnostic profiler start returned HTTP 200, 200, 200; all three profiler stop requests returned HTTP 500. Each role log ends this traceback with `RuntimeError: Profiling is not in progress. Call /start_profile first.`. The profile-control failure is therefore a control-path failure, separate from the zero scored-request error count. Collected trace files by role: {'prefill-0': 4, 'prefill-1': 4, 'decode-0': 8}. Trace contents were not inspected; exact filenames are in JSON.

## Limits

- Nominal telemetry intervals conservatively bound sample timestamps but do not guarantee that every NVML activity value covers precisely that full interval.
- Sparse samples do not establish peaks. GPU activity, sampled VRAM, power and SGLang token/KV gauges are distinct quantities.
- Gauge counts are per labeled TP/PP/EP series and are never summed across ranks; no inflight gauge was present. Client concurrency is not asserted to equal server batch size.
- Missing fields and failed scrapes are reported by status or absence and are never interpreted as zero or healthy.
- The offline review does not inspect compressed trace contents; it records filenames only. Official model accuracy remains outside these artifacts.

Reproduce with `python3 observability.py` from this directory. The script writes only `observability.json` and `observability.md`; it performs no scheduler or network calls.
