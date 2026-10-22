# Job 25371: short N64/N68 screen review

Job 25371 completed successfully on 22 October 2026 (`COMPLETED`, exit `0:0`, elapsed 10:26). Its terminal run evidence is sealed in `runs/25371/artifact-manifest.json`; the review verified the seal and replayed the inherited protocol, raw request, SLA, output and long-context checks. The run compared N64 then N68 in one observed deployment using 20 seconds of warmup, 40 seconds of scoring and 30 seconds of grace. It is a short, fixed-order screen, not a full ranked result.

Both points passed the strict local gates. Good output-token throughput was **2,830.6994 tokens/s at N64** and **2,895.0541 tokens/s at N68**, a **2.27346%** increase against this run's N64 control. The prospectively required 1% screen threshold therefore passes and supports considering a fresh full N68 pair. No full N68 work was frozen or submitted by this review.

| Metric | N64 | N68 |
|---|---:|---:|
| Scored requests | 639 | 657 |
| Good output-token throughput | 2,830.6994 tokens/s | 2,895.0541 tokens/s |
| Joint SLA fraction | 95.9311% | 95.8904% |
| TTFT mean / p95 / p99 | 1,228.656 / 2,697.459 / 4,249.224 ms | 1,347.803 / 2,725.915 / 4,219.284 ms |
| Request-mean ITL mean / p95 / p99 | 14.909 / 15.198 / 15.827 ms | 15.040 / 15.425 / 16.077 ms |
| Request errors / cancellations | 0 / 0 | 0 / 0 |
| TTFT over 3,000 ms / ITL over 20 ms | 26 / 0 | 27 / 0 |

The score is calculated under the retained Goodput × 200 rule. N68 improves throughput by 2.27346%, while its mean TTFT is 119.148 ms higher, p95 TTFT is 28.456 ms higher, mean request ITL is 0.131 ms higher, and joint SLA fraction is 0.0407 percentage points lower. This is one short pair in fixed order; it does not establish a stable gain or statistical significance.

The eight-case output diagnostic passed 7/8 cases at both points. The single failure (`reverse`) is also present in the independent baseline, so there are no new failures and the local non-regression gate passes. The separate hand-written long retrieval check passed 12/12 requests, each with 3,839–3,842 prompt tokens. Neither diagnostic verifies organiser accuracy or the official ≥99% reference-accuracy requirement. The official workload's nominal 200-token output setting and scored denominator were not changed; exported sequence lengths are diagnostics and do not prove generated token IDs.

## Runtime and observability

During the two scoring windows, `decode-0.log` recorded 67 decode-batch lines per point: N64 reached **54** running requests and N68 reached **58**. Client concurrency 68 did not produce a logged decode batch of 68. Startup logs explicitly show target decode CUDA graphs captured for batch sizes 1–64 and prefill CUDA graphs disabled. No evidence here establishes graph coverage above 64 or the behavior of a batch above 64; none was observed in these scoring windows. Decode batch lines report CUDA graph use for the observed batches. The exact lines and phase-window sample counts are retained in `observability.json`.

The 5-second sampler produced 7–8 phase-aligned samples per role and screen. GPU status and server-metrics HTTP status were `ok`/200 for the included samples. Across 16 observed H200 GPU UUIDs, the mean of per-GPU sample means was approximately 95.5% GPU activity, 46.4% memory activity, 133,824–133,916 MiB sampled VRAM, and 562–564 W sampled power. These are sampled activity, allocation and power measurements; they are not kernel-time sums or proof of a causal bottleneck. UUIDs were not independently mapped to role processes.

The decode server gauge averaged 51.1 running requests at N64 and 52.6 at N68, with a sampled queue of zero in both windows. Decode token usage averaged 0.1175 and 0.12375, respectively. Prefill gauges are retained per role and label; no explicit inflight-request gauge was present. Deduplicated host CPU samples show approximate system-wide busy fractions of 12.4–13.1% and minimum available memory of 1,820.8 GiB on `g4` and 1,860.4 GiB on `g1`. CPU percentages use adjacent `/proc/stat` jiffy deltas and are approximate. Network counters were collected but per-interface traffic rates were not derived.

Diagnostic profile starts returned HTTP 200 for all three workers. All three stop calls returned HTTP 500, with `Profiling is not in progress` tracebacks in role logs. This diagnostic action was outside the scored interval; independently validated scored requests had zero errors and cancellations. The review inventoried 4 prefill-0, 4 prefill-1 and 8 decode trace files, but did not inspect trace contents. Role logs contain no NIXL error or CUDA OOM markers; their tracebacks correspond to the profile-stop errors.

## Decision and limits

The ≥1% prospective short-screen gate passes and all local protocol, SLA, output non-regression and long-retrieval gates pass. A fresh full N68 comparison is therefore justified for a separate freeze/submission decision. This report does not authorize or perform that submission. The short, fixed-order result is not a ranked score, the official accuracy gate remains unverified, and the diagnostic profile stop failures remain recorded rather than hidden.

Reproduce the sealed replay and observability summaries with:

```bash
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 python3 qwen-experiments/research-review-25371-20261022/review.py
```

The script writes the terminal manifest only if it does not exist, then validates it and writes `REVIEW.json` and `observability.json`. Subsequent runs reuse the manifest and fail strict hash checks if sealed raw evidence has changed. No scheduler mutation, queue operation or budget change is performed.
