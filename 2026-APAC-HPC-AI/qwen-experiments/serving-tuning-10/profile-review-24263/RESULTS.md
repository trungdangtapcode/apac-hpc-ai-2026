# Job 24263: benchmark and profile review

The full N56 benchmark reached **2,667.46 good tokens/s**, SLA **98.80%**, zero
errors/cancellations, and 12/12 long checks. This confirms the existing performance
range; it is not a new gain.

## Diagnostic evidence

The profile ran after scoring with **48 concurrent requests**. Earlier notes
calling it a 52-request profile are historical; protocol.json records the actual
load. All 16 rank traces contain kernels, and all 415 diagnostic requests succeeded.

| Role | Mean MoE fraction | Mean collective fraction |
|---|---:|---:|
| Prefill 0 | 42.84% | 23.48% |
| Prefill 1 | 42.77% | 23.64% |
| Decode | 27.99% | 23.89% |

These are per-rank means of classifier fractions of summed kernel durations,
not fractions of job wall time or predicted speedups. Prefill/decode captured
4/32 steps respectively, so their absolute sums are not comparable phase times.

Start-profile returned HTTP200 but the client failed to parse its response as
JSON. Later explicit stops returned HTTP500: the server said profiling was no
longer running. Keep these control warnings. Valid traces exist for every rank;
no extra GPU rerun is justified merely to remove these warnings.

## Next trial: DeepGEMM for prefill only

The profile motivates testing the prefill MoE implementation. The earlier
DeepGEMM experiment changed **decode** and lost performance; that result does not
establish whether DeepGEMM helps the much larger prefill batches. It may still
lose here. Do not assume that a large kernel fraction proves a bottleneck.

Keep both prefill workers TP4/EP1 and decode TP8/EP8 with MNNVL+FlashInfer. Change
only prefill `--moe-runner-backend deep_gemm`. Exact image source snapshots under
source/ expose this backend and its standard-layout path for unsplit experts.
This is source compatibility evidence, not GPU validation.

One initial N56 allocation, 16H200/17min; official FP8, BF16KV, RR/NIXL and full
60/120/30 protocol unchanged, followed by the same short/12long checks. Compare
against 24263's benchmark before profiling and 24190/24235. Require runtime backend
proof, SLA>=90%, zero errors/cancel, short nonregression and long pass. Any useful
gain needs an independent repeat. No automatic repeat, new load, H100 spending,
or organiser accuracy claim.
