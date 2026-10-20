# Native DeepGEMM scheduler budget screen

## Why this is a new question

H100 222242 validates 256 TP8 decode projection cases and 222245 validates 160 TP4 prefill cases. Native default Triton loses every rank/shape/M in both regimes; small-M FlashInfer has no consistent useful gain. Retain DeepGEMM and do not submit full-model jobs for these losses. The current H100 serving incumbent already uses HPC-Ops for both MoE phases, leaving native DeepGEMM for dense FP8 attention projections. This screen changes the winning helper's internal scheduler budget, not its backend or tensor work.

The exact image's deep_gemm 0.1.5.post1 exposes native set_num_sms/get_num_sms in __init__.py. Its SM90 GEMM kernel passes kNumSMs to the native persistent scheduler (see extracted impls/sm90_fp8_gemm_1d2d.cuh and scheduler/gemm.cuh); the successful 222242 traces include 132 in this template parameter. The same SGLang wrapper contains configure_deep_gemm_num_sms, which saves/sets/restores that native state. This supports testing the API; it does not establish a faster setting. All inspected primary source is retained under runtime-source and the earlier pinned wrapper directory, with guarded hashes.

Hypothesis: for small TP8 decode matrices, a smaller native scheduler budget may arrange work more efficiently than the physical total of 132 SMs. Counterhypothesis: fewer scheduling slots lose throughput or are inconsequential. SM means streaming multiprocessor, a compute unit inside one GPU. **All eight allocated GPUs remain available; no model work, experts, precision or tokens are removed.** This does not change GPU power/clock settings or impose a hardware partition.

## Controlled experiment

Same synthetic TP8 QKV N1280/K4096 and O projection N4096/K1024. Compare native DeepGEMM at 132 (control), 120 and 96 SMs, at M32/48/54/60/64, eight independent GPU ranks with rotated setting order. Each process first asserts physical SM count and default native getter are exactly132; every case records/asserts set/get agreement. Restore the original value before declaring completion. No serving process shares this isolated allocation.

Use the identical tensors for each setting and all prior numerical/input bounds: BF16 inputs/output, 128x128-block FP8 weights, finite output, <=5% relative RMSE versus explicit FP32 accumulation, <=2% between settings, unchanged inputs/scales/weights after ordinary calls/graphs/profiling. Keep 16 operations per graph, ten replays and nine samples. Set the scheduler value outside timing/capture; native GEMM plus its activation quantisation remains inside. Thirty full cases per rank, 240 total. Rank0 profiles both shapes/all three settings at M54 after timing (six traces). Reviewer must verify the real SM90 kernel's template budget, not only the setter log. Eight distinct GPU UUIDs must agree with rank mapping.

Use the proven private writable home/cache wrapper and bounded one-GPU/six-case provider preflight at M54 (all settings/both shapes). It must complete numerical/input/setter checks before the full eight-rank screen. Preflight has one graph operation/replay/sample and is excluded from timing comparisons. Keep the ten-minute allocation, 210-second preflight cap and remaining full-task budget out of 540 seconds. No model weights loaded.

For this isolated multi-setting screen, disable SGLang's **broad all-M precompile** using its supported SGLANG_JIT_DEEPGEMM_PRECOMPILE=0 before imports. Exact compile_utils source proves this only skips the unrelated 1..16384-M sweep; native calls still execute/JIT on demand. Four ordinary calls per exact shape/setting and graph warmup occur before CUDA timing. Assert the actual wrapper/init source hashes and disabled broad-precompile state. The retained CPU fixture executes the real pinned hook AST with compiler recording to verify unrelated Ms are skipped; it is not a GPU numerical pass. Do not disable actual computation or treat compilation time as a performance gain.

## Acceptance and limits declared before submission

For either candidate separately, require all eight representative shape/M48/54/60/64 points to have >=5% median paired latency reduction and >=6/8 ranks faster, with no median regression >5% at diagnostic M32. Require all numerical/input/default-restoration/source/UUID/sample/native-template checks. Otherwise retain132 and close these budgets without unchanged retries. Report every rank and setting, not the fastest subset. Eight hardware repetitions are not independent full-model runs.

Even a positive screen only supports **planning** a real model pair. First inspect all serving callers of this global native state and safe per-worker integration, including startup/fork safety and CPU overhead omitted by this kernel screen. Do not alter MoE runners, graphs, model outputs or global serving defaults on the strength of a micro alone. No goodput/SLA/official accuracy prediction or cross-platform conversion is permitted.

## Cost and queue gates

One H100 node/eight GPUs/ten minutes, maximum170.666667 SU. Fresh own queue must be empty; under budget.lock require the now fully reconciled Used37402.168 SU, no unexplained ledger delta, reserve the maximum, stay under51000 SU campaign cap and retain13000 SU project buffer. Never retry uncertain qsub. At most three active PBS and one running allocation. No additional H200 job: 24990 plus four existing model jobs already fill cap five and their positions remain unchanged. No official package edit, authentication restart or background Codex.
