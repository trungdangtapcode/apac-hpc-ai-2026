# H200 N64 kernel evidence before the next algorithm change

Inspected all **48 rank traces** retained from completed jobs 25365 (N62), 25366 (N64) and independent N64 repeat 25373. Every compressed trace, diagnostic protocol, request record and profile-control record used here matches its terminal-run seal. No new GPU allocation, PBS SU, serving change or ranked result was created.

## What was measured

These are separate **post-score N48 diagnostic** requests: 428/428, 427/427 and 425/425 succeeded respectively. Prefill captures four steps and decode 32, with GPU activities only. Each run has all expected TP4/TP4/TP8 traces. This is not a profile of N62 or N64 scored requests; the experiment's client load must not be substituted for the diagnostic load.

The table gives mean per-rank fractions of **summed GPU kernel durations**, classified by retained kernel names. MoE-associated includes actual HPC group GEMMs/reorder/reduce/activation and DeepGEMM grouped types 1/2; normal DeepGEMM type 0 remains other GEMM. Collective-associated includes fused MNNVL allreduce+RMSNorm, so that column is not pure communication. Other quantization excludes those associated fused kernels. Complete names, counts, kernel sums and assignments are in [REVIEW.json](REVIEW.json).

| Source job | Diagnostic role | MoE-associated | Collective / fused normalization | Attention-associated | Other quantization |
|---|---|---:|---:|---:|---:|
| 25365 | prefill-0 | 36.451% | 24.881% | 8.479% | 3.285% |
| 25365 | prefill-1 | 37.124% | 24.487% | 8.308% | 3.246% |
| 25365 | decode-0 | 35.043% | 23.423% | 16.338% | 10.676% |
| 25366 | prefill-0 | 36.465% | 24.842% | 8.495% | 3.291% |
| 25366 | prefill-1 | 37.087% | 24.530% | 8.301% | 3.246% |
| 25366 | decode-0 | 34.828% | 23.510% | 16.461% | 10.726% |
| 25373 | prefill-0 | 36.492% | 24.824% | 8.480% | 3.289% |
| 25373 | prefill-1 | 37.155% | 24.408% | 8.312% | 3.252% |
| 25373 | decode-0 | 34.900% | 23.444% | 16.440% | 10.708% |

## Interpretation

The same N48 diagnostic produces a stable kernel composition across the three deployments: decode MoE-associated work is about 34.8–35.0%, collective/fused normalization 23.4–23.5%, attention-associated 16.3–16.5%, and other quantization 10.7%. Prefill remains about 36.5–37.2% MoE-associated and 24.4–24.9% collective-associated. The exact grouped-GEMM classifier matters: counting only names that contain `moe` would omit substantial real grouped work.

These numbers support investigating methods that reduce repeated target decode work, including the already planned EAGLE3 branch. They do **not** predict its speedup: a draft adds computation, state, communication and verification overhead, and accepted tokens do not measure closed-loop goodput. They also do not justify repeating unchanged losing MoE backend/forced collective choices. The prior forced Tree, Simple-protocol, one-shot and PDL-off records remain separate measured branches; these new traces do not reverse them.

All starts returned HTTP 200. Later explicit stops returned HTTP 500 after the step-bounded capture had already finished; each role has complete actual kernel traces despite that control warning. Preserve the warning and keep it separate from zero scored-request errors.

## Limits and next action

Summed durations can overlap on multiple streams. The JSON also retains each trace's union of kernel intervals and first-to-last-kernel span, but neither is NVML utilization, job busy time or a transformer critical-path decomposition. Do not add GPU ranks into an elapsed fraction. Prefill/decode captured different step counts; their absolute totals cannot rank total phase cost. The repeated N64 prefill-1 trace has a much larger first-to-last span (about 3029 ms versus 852 ms in source), despite similar kernel composition; this is a diagnostic-window difference, not evidence of a scored regression. Batch/request sequence and capture alignment are not matched across traces.

Keep the already queued full N64/N68 pair 25487/25488. Require actual terminal exact-reference acceptance from 25495 before a separately derived EAGLE3 candidate; add reviewed redacted geometry and retain native runtime/correctness gates before any load comparison. A valid candidate would then need equally observed, equal-capacity control and speculative short runs, with fixed cold 4000/200 workload, zero errors and joint SLA >=0.90. Require at least 3% matched short goodput gain before funding full scoring. Do not change precision, omit initial failures or convert acceptance length/kernel fractions into a score. Official >=99% reference accuracy remains unverified.

## Reproduce

Run `python3 review-traces.py` in a fresh copy of this directory without REVIEW.json. It reads only the sealed local runs and refuses to overwrite its result. Decompression is bounded to 128 MiB per trace and traces are processed one at a time. No network or scheduler calls are made. [Classifier/interval sanity evidence](analysis-validation.json). [Prior grouped classifier correction](../research-followup-20261018-0900/review-h100-profile.py), [earlier actual profile-led prefill improvement](../serving-tuning-10/profile-review-24263/RESULTS.md), [current N64 observability](../research-review-25366-20261022/observability.md).
