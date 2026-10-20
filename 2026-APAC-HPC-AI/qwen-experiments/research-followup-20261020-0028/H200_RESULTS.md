# H200 repetition and load results — 20 October 2026

## Question and unchanged setup

The 2938.628 good output tokens/s N58 interaction needed its own repeat and fresh control. Five terminal jobs now have sealed artifacts and pass the full local raw-protocol, frozen-payload, runtime, short-output, 12-long-context, error and request-level joint latency gates. Native FP8 checkpoint, BF16 KV, no speculation, 16 H200 GPUs, DeepGEMM prefill chunk8192, MNNVL decode and dense FlashInfer decode remain unchanged. Auto versus HPC-Ops refers only to the decode MoE runner.

| Job | Trial | Good output tokens/s | Joint good requests | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|
| 24733 | Auto decode N62 | 2890.551 | 98.673% | 872.182 | 16.612 |
| 24736 | Fresh auto decode N58 | 2775.642 | 98.844% | 801.591 | 16.460 |
| 24737 | HPC-Ops decode N58 repeat | 2935.879 | 98.905% | 881.274 | 14.975 |
| 24738 | HPC-Ops decode N60 | 2990.151 | 98.819% | 947.652 | 14.931 |
| 24819 | HPC-Ops decode N58 repeat, separate profile | 2937.148 | 98.905% | 880.109 | 14.974 |

## Assessment

The N58 interaction reproduces: original 24724 = 2938.628, repeat 24737 = 2935.879, repeat/profile 24819 = 2937.148. Their descriptive range is 0.0936% of their mean, not a confidence interval. Fresh matched N58 auto control 24736 = 2775.642 gives repeat 24737 a **5.7730%** gain. The original improvement therefore survives a fresh control and independent deployments. The profiled observation's ranked score precedes its separate diagnostic traffic.

**New highest individual H200 observation: 24738 at N60 = 2990.151 good output tokens/s**, +1.8486% versus the fresh HPC-Ops N58 repeat. TTFT rises while ITL remains below 20 ms and joint success stays above 90%. N60 needs its own independent repeat and a fresh auto-decode N60 control. It is not a global optimum, official score or accuracy certificate.

The auto-decode N62 point passes at 2890.551. This is a valid same-platform operating point; it does not beat the new HPC-Ops N60 observation. Compare a future HPC-Ops N62 trial against a fresh auto N62 control to isolate the runner at that load. Do not pool H100 results or add improvements from unrelated stages.

## Next decision and limits

Prepare four bounded full-protocol trials: fresh auto N60, HPC-Ops N60 repeat, fresh auto N62, HPC-Ops N62 with separate post-score profile. This verifies the new point and tests one evidence-supported next load, without crossing the graph limit64 or changing model/output work. Keep the five-job account cap and preserve actual submission receipts. Stop further load expansion if these results add no useful goodput or fail acceptance gates. Profile the exact winning platform/runner before a deeper kernel change.

All underlying runs, submitted hashes, raw requests and per-job review JSONs are retained. The terminal worker-step cancellations visible in sacct are cleanup, not a replacement for reviewing actual requests; the batch allocations exit0 and all required evidence checks pass. Official full-set accuracy remains unverified. No slide/submission promotion, authentication or background Codex is performed.
