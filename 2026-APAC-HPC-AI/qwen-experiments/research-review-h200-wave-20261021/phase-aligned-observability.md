# Phase-aligned observability

This bounded summary reads existing telemetry and the sealed AIPerf profiling phase manifests. It conservatively keeps a nominal five-second sample window only when `sample utc_ns - 5 s >= profiling start_ns` and `sample utc_ns <= profiling end_ns`. This timestamp rule does not guarantee that each GPU activity value summarizes exactly that full interval; NVML uses its own underlying sample window. Run markers were checked as enclosing corroboration. No raw telemetry was changed.

| Job | Role | Samples inside score | UUIDs match role receipt | HTTP/status inside / outside | Server metric payloads inside | GPU activity mean/range (%) | Sampled VRAM mean/range (MiB) | Sampled power mean/range (W) |
|---|---|---:|---|---|---:|---:|---:|---:|
| 24964 | prefill-0 | 24 | match | {'200': 24} / {'200': 44, 'URLError': 52} | 24 | 92.8 (92.5–92.9) | 133334.0 (132998.0–133478.0) | 663.7 (663.1–664.7) |
| 24964 | prefill-1 | 24 | match | {'200': 24} / {'200': 45, 'URLError': 51} | 24 | 91.5 (89.2–92.8) | 133334.0 (132998.0–133478.0) | 658.1 (654.2–660.2) |
| 24964 | decode-0 | 24 | match | {'200': 24} / {'200': 58, 'URLError': 41} | 24 | 100.0 (100.0–100.0) | 134314.2 (133906.0–134386.0) | 471.4 (462.4–480.6) |
| 24965 | prefill-0 | 23 | match | {'200': 23} / {'200': 44, 'URLError': 40} | 23 | 97.4 (96.3–98.4) | 133492.0 (133156.0–133636.0) | 689.9 (688.3–691.7) |
| 24965 | prefill-1 | 23 | match | {'200': 23} / {'200': 44, 'URLError': 41} | 23 | 96.2 (95.5–97.0) | 133492.0 (133156.0–133636.0) | 691.9 (690.9–692.9) |
| 24965 | decode-0 | 24 | match | {'200': 24} / {'200': 48, 'URLError': 40} | 24 | 100.0 (100.0–100.0) | 134106.2 (133698.0–134178.0) | 464.9 (456.1–473.4) |
| 25051 | prefill-0 | 24 | match | {'200': 24} / {'200': 44, 'URLError': 51} | 24 | 92.2 (91.1–92.8) | 133334.0 (132998.0–133478.0) | 658.8 (656.6–661.7) |
| 25051 | prefill-1 | 24 | match | {'200': 24} / {'200': 43, 'URLError': 52} | 24 | 92.9 (92.7–93.3) | 133334.0 (132998.0–133478.0) | 665.3 (663.0–666.7) |
| 25051 | decode-0 | 24 | match | {'200': 24} / {'200': 57, 'URLError': 40} | 24 | 100.0 (100.0–100.0) | 134280.2 (133872.0–134352.0) | 471.8 (463.0–478.5) |
| 25283 | prefill-0 | 23 | match | {'200': 23} / {'200': 45, 'URLError': 51} | 23 | 84.8 (82.4–86.7) | 133334.0 (132998.0–133478.0) | 638.4 (634.7–640.7) |
| 25283 | prefill-1 | 24 | match | {'200': 24} / {'200': 43, 'URLError': 52} | 24 | 89.5 (89.0–90.3) | 133334.0 (132998.0–133478.0) | 668.8 (666.0–671.5) |
| 25283 | decode-0 | 24 | match | {'200': 24} / {'200': 59, 'URLError': 39} | 24 | 100.0 (100.0–100.0) | 134144.2 (133736.0–134216.0) | 466.3 (456.5–474.6) |

GPU activity is the reported sample-window activity percentage, with the telemetry interval only a nominal polling bound. VRAM and power are sampled values; the ranges shown are the minimum and maximum of per-GPU means, while per-GPU minima and maxima remain in JSON. The 23–24 in-window samples per role are sparse and cannot establish peaks or causal bottlenecks.

## SGLang role metrics inside scoring

All retained in-window server scrapes returned HTTP 200 with a metrics payload. The table reports means and min–max ranges across labeled TP/PP/EP series observations over those scrapes; it does not sum values across ranks. Counts are requests per series, `token_usage` and `cache_hit_rate` are unitless fractions, and `num_used_tokens` is tokens per series. Per-series details are in JSON. No inflight-request gauge was present.

| Job | Role | Running requests / series | Queue requests / series | Token usage fraction | Used tokens / series | Cache hit rate |
|---|---|---:|---:|---:|---:|---:|
| 24964 | prefill-0 | 2.04 (0.00–3.00) | 0.04 (0.00–1.00) | 0.019 (0.000–0.020) | 22847 (0–27119) | 0.001 (0.001–0.001) |
| 24964 | prefill-1 | 1.75 (0.00–3.00) | 0.00 (0.00–0.00) | 0.015 (0.000–0.020) | 20046 (0–25844) | 0.001 (0.001–0.001) |
| 24964 | decode-0 | 50.50 (40.00–52.00) | 0.00 (0.00–0.00) | 0.109 (0.080–0.110) | 240040 (164491–244998) | 0.000 (0.000–0.000) |
| 24965 | prefill-0 | 2.74 (2.00–4.00) | 0.13 (0.00–1.00) | 0.020 (0.020–0.020) | 25050 (23949–28383) | 0.001 (0.000–0.001) |
| 24965 | prefill-1 | 2.39 (0.00–3.00) | 0.04 (0.00–1.00) | 0.019 (0.000–0.020) | 23972 (0–28364) | 0.001 (0.000–0.001) |
| 24965 | decode-0 | 46.58 (16.00–50.00) | 0.00 (0.00–0.00) | 0.106 (0.030–0.110) | 234380 (66754–244783) | 0.000 (0.000–0.000) |
| 25051 | prefill-0 | 1.83 (0.00–3.00) | 0.04 (0.00–1.00) | 0.017 (0.000–0.020) | 20859 (0–25633) | 0.001 (0.001–0.001) |
| 25051 | prefill-1 | 1.92 (0.00–3.00) | 0.08 (0.00–2.00) | 0.018 (0.000–0.020) | 22085 (0–26482) | 0.001 (0.001–0.001) |
| 25051 | decode-0 | 50.75 (47.00–54.00) | 0.00 (0.00–0.00) | 0.109 (0.090–0.110) | 239349 (196840–245100) | 0.000 (0.000–0.000) |
| 25283 | prefill-0 | 1.65 (0.00–4.00) | 0.43 (0.00–3.00) | 0.010 (0.000–0.020) | 13658 (0–28168) | 0.001 (0.000–0.001) |
| 25283 | prefill-1 | 2.50 (0.00–4.00) | 1.83 (0.00–5.00) | 0.017 (0.000–0.020) | 21612 (0–27951) | 0.001 (0.000–0.001) |
| 25283 | decode-0 | 46.75 (40.00–51.00) | 0.00 (0.00–0.00) | 0.108 (0.070–0.110) | 237993 (156666–244844) | 0.000 (0.000–0.000) |

Status or payload gaps outside scoring remain separately counted and are not interpreted as zero. The UUID match compares each run’s in-window UUID set with the role mapping captured by job 25051 on the same named hosts. It demonstrates consistency with that receipt, not a new process-to-GPU locality capture in every run.
