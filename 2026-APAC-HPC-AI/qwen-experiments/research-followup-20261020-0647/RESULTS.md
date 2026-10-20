# Unobserved receive-interval check: flat, close this setting

## Controlled question and actual result

222178 (interval2) and 222179 (fresh interval1 control) reverse the prior candidate/control order and disable SGLang metrics/resource sampling on both. N54, chunk4096, both-phase HPC-Ops, FA3 prefill/FlashInfer decode, topology, native FP8/BF16 KV, MNNVL AUTO+PDL, graphs, NIXL and full workload are unchanged. Actual runtime differs only in intended decode scheduler_recv_interval and random seeds, with speculative decoding disabled.

Both independently pass terminal seals, frozen payloads, complete raw 60/120/30 and 4000/200 protocol, joint per-request SLA/error gates, short-output nonregression and all 12 long retrieval checks. Official full-set accuracy remains unverified.

| Job | Interval | Good output tokens/s | Joint success % | Mean TTFT ms | Mean ITL ms | Requests / good |
|---|---:|---:|---:|---:|---:|---:|
|222178|2|2420.816780|98.615689|724.709694|18.166868|1517 / 1496|
|222179|1|2419.693212|98.613861|728.772117|18.149490|1515 / 1494|

The difference is only **+0.046434%**, below the predeclared 1% advancement threshold. Both have 21 TTFT breaches, zero request-mean ITL breaches and zero errors/cancellations. Keep default interval1 and close this H100 N54 interval2 setting without another unchanged repeat or automatic interval4/load growth. The earlier +0.480% observed pair did not become a useful unobserved improvement. This does not establish a universal scheduler ranking.

## Inspected beyond goodput

Both separate N48 diagnostics have 16 sealed, nonempty rank-checked CPU/GPU traces, with 353/353 and 375/375 successful diagnostic requests. Start HTTP200 text controls now parse correctly; step-completed stop HTTP500 errors remain in raw artifacts. CPU operations may nest and kernel sums/interval coverage are not critical-path fractions. Client tail/concurrency distributions, exact raw failure components, sparse role queue/batch/KV samples and trace observations are retained in adjacent inspections.

Uniform scored hardware/server samples are intentionally **not collected** on either unobserved job. Full-job PBS GPU fields are retained, but mixed-lifetime/cumulative values are not phase-aligned observations or proof of health. Do not reinterpret the scheduler's unusually large lifetime counters as model VRAM peaks. Missing dedicated telemetry is not zero. Earlier observed samples are separate deployments.

## Charges and queue snapshot

222178 consumed 14:35 allocated walltime: **497.777778 SU**. 222179 consumed 12:00: **409.600000 SU**. Each charge separately reconciles the published Used delta within rounding; all corresponding maximum reservations were released. At the 07:02 UTC review, published Used **37215.572**, Balance **26784.428**, In Doubt zero and no outstanding reserve, internal headroom **13784.428** under unchanged 51000 cap /13000 project buffer. Subsequent microbenchmark reservation is a separate receipt milestone.

The four existing H200 model jobs remain Priority-pending; their positions and frozen payloads were preserved. No new H200 model result is claimed. The 3022.035 H200 N62 single observation and 2433.020 H100 individual incumbent remain separate.

## Source-based next hypothesis and pruning

The exact pinned FP8 linear source was selectively extracted read-only. The native auto selector uses DeepGEMM when available. FlashInfer DeepGEMM only uses swapAB for **1 <= M < 32**; at M>=32 it calls the existing DeepGEMM helper. Do not buy a full-model N54 toggle assuming it changes the sustained large decode batch. The native CUTLASS selector rejects SM90 and is restricted to SM120 in this image; do not bypass that guard. Current public docs are background, not runtime compatibility proof: [SGLang source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/layers/quantization/fp8_utils.py), [FlashInfer GEMM API](https://docs.flashinfer.ai/api/gemm.html), consulted 20 October.

The remaining native Triton versus DeepGEMM linear helper is a distinct hypothesis from the phase-specific MoE runner. First screen exact Qwen TP8 projection shapes on both GPUs with synthetic same-input numerical checks, graph-amortised timing and actual kernel traces, before paying for full-model loading. The separate [bounded microbenchmark plan](../fp8-linear-micro-20261020/PLAN.md) details the numerical gates, shape derivation, guard/hash checks and >=5% representative improvement requirement for advancing to a model-level pair. These microseconds cannot be converted into serving speedup without a complete serving measurement. Preserve failures and numerical differences. No precision/workload shortcut, clock/power change, official quality claim, package edit or background Codex.
