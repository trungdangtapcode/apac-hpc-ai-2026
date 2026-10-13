# Qwen serving improvement plan — 13 October 2026

Starting point: job **22415**, `P8-TP4_D8-TP8-EP8`, N48, request-scoped NIXL
descriptors, BF16 KV. Full measurement: **1912.30 good tokens/s**, **97.44% SLA**,
zero errors and cancellations. The 17 usable topology configurations have been
measured: 14 original layouts and three separately named EP2 replacements.

Latest results: control N48 repeats at **1911.08** (23102) and **1910.32**
(23104), both approximately 97.47% SLA. Control N52 reaches **2096.88 good
tokens/s, 98.86% SLA**; N56 reaches **2057.87, 97.05% SLA** (23106).
Dense decode graphs reach **1933.05 at N48** and **2123.30 at N52, 98.73% SLA**
(23103), all with zero errors/cancellations. Dense N52 is **+1.26% versus the
same-N control** and **+11.03% versus the old best N48**. These remain provisional
until independently repeated. Dense N56 is queued as **23109**.
Profiling 23104 completed with 16 per-rank traces. Decode TP0 identifies about
28.1% summed kernel time in MoE kernels and 20.7% in collectives; these fractions
are not end-to-end wall-time percentages or speedups.

## Current wave: submitted

| Trial | Job | Change | Measurements |
|---|---|---|---|
| control-load | 23102, 23106 | Existing winning deployment | Full N48/N52/N56 complete |
| dense-decode-graphs | 23103, 23109 | Decode graph batch sizes 1..64 | Full N48/N52 complete; N56 pending |
| profile-control | 23104 | Independent winning deployment | Full N48 and P/D GPU traces complete |

Each full point keeps the official 60/120/30 protocol and 4000/200 workload.
Stop increasing N after a failed SLA/error gate. If the 17-minute allocation
cannot accommodate a point, record it as missing and submit a frozen follow-up,
at most two retries. Performance runs and profiling traffic never overlap.

The graph hypothesis comes from real decode logs: active batches commonly vary
between 31 and 42, while the original captured graph sizes jump 32 → 40 → 48.
Dense capture may reduce padding; it can also cost more startup and memory, so
it must be measured. The current same-N improvements are small: approximately
1.17% at N48 versus the two fresh controls, and 1.26% at N52 versus its control.
This does not establish a stable gain yet.

The profile records four prefill steps per worker and 32 decode steps per rank,
after seven seconds of separate diagnostic traffic at concurrency 48. Prompts
are approximately 4000 tokens and request 200 output tokens. This diagnostic
is not the official synthetic dataset, an accuracy test or a scored benchmark.

## Remaining axes, selected from observations

| Axis | Concrete next trial | Reason to select it | Acceptance check |
|---|---|---|---|
| Concurrency | N52/N56; then N50/N54 near the measured boundary | Higher load still has enough per-request latency margin | Repeated full runs, SLA ≥90%, errors/cancellations reported |
| Decode CUDA graphs | Confirm dense capture; consider a smaller targeted graph list | Padding or launch overhead visible in decode | N48 against new controls, startup/memory also recorded |
| Prefill scheduling | Chunk 4096, then 16384 against current 8192 | Logs show queueing or requests split between chunks | Same model, N and decode flags; compare TTFT tail and goodput |
| MoE kernels | Decode `--moe-runner-backend deep_gemm` versus current auto/Triton | MoE GEMM/dispatch occupies substantial GPU time | Supported path in actual image; full run and output-quality validation |
| Expert communication | DeepEP low-latency with compatible EP8/DP settings | Collective or dispatch/combine cost dominates the profile | Check backend/model compatibility first; no missing experts or precision below FP8 |
| KV path | Measure transfer separately, then compare FP8 KV against BF16 | Transfer waiting is substantial, not just cold setup | Same FP8 checkpoint; full quality check before promotion |
| Serving version | Existing staged SGLang 0.5.20 image versus current image | Specific supported backend/fix has a measured bottleneck to address | Inspect/rebuild patch against new source; record versions and keep an old-image control |
| Alternative engines | vLLM or TensorRT-LLM disaggregated serving | Current stack improvements plateau and images are reproducible | Exact checkpoint, genuine P/D split, identical official protocol |
| Lossless speculation | Select a compatible public draft and target verification path | Decode remains the primary cost after kernels/communication | No benchmark-targeted training; correctness/quality and acceptance rate recorded |
| Quality and replay | Organiser full-set/reference evaluation; clean standalone replay | Required before treating the result as contest-ready | ≥99% organiser reference score; benchmark goodput is not an accuracy metric |

No row is a promise of speedup. The initial three jobs are actually submitted.
After they finish, the watcher automatically schedules an independent repeat
of the highest passing load point if it improves >3% over job 22415. It schedules a prefill-chunk-4096
trial if a new N48 control passes. It schedules decode DeepGEMM only if complete
P/D traces identify at least 20% summed decode kernel time in MoE kernels.
It schedules an independent dense-graph repeat if N48 improves more than 3%
over the new controls. These are at most four bounded follow-ups, each frozen
under its own configuration and job ID. The remaining precision/communication/
engine trials await their required observations and compatibility/quality work.

## Records and automation

- [Live results](../SERVING_TUNING_RESULTS.md): all successful and failed points.
- [Registry](registry.json): job IDs, frozen payload hashes and missing points.
- [Raw runs](../runs/): exports, per-request metrics, worker logs and traces.
- [CPU validation](cpu-validation.json): actual-image graph argument parsing,
  official-duration client arguments, failed-gate stopping and time-budget handling.
- `watch-serving-tuning.py --run` watches every 45 seconds, archives finished
  run checksums, submits time-budget retries and the bounded follow-ups above.
  It never replaces the
  winning submission based on one provisional result.

The submission package keeps its current measured winning AI scripts. HPC
subdirectories are intentionally empty as requested. No organiser upload occurs
as part of these experiments.

Reference: [SGLang tuning](https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning)
and [profiling](https://docs.sglang.io/docs/developer_guide/benchmark_and_profiling).
Flag names and the profile schema were checked against the actual staged image,
whose original NIXL source hash matches the patch's recorded base source.
