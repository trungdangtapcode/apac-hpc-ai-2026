# Native FP8 linear screen before another large model job

## Evidence and precise hypothesis

The H100 interval2 candidate 222178 passes at 2420.817 good output tokens/s, pending fresh control review. Prior both-HPC-Ops profiles and uniform samples show sustained decode GPU activity; they do not prove a critical-path kernel or predicted speedup. The current phase-specific MoE runner does not settle the best dense blockwise FP8 linear helper for attention projections.

The exact deployed fp8_utils source selects native DeepGEMM in auto mode when available. Its `flashinfer_deepgemm` helper only uses swapAB for **1 <= M < 32**; at M >= 32 it returns the existing DeepGEMM helper. A full N54 deployment toggle would therefore largely leave the steady-state linear path unchanged. Prune that model-level hypothesis at this load instead of spending a full allocation on an unverified flag. The native CUTLASS selector explicitly rejects SM90 (it is restricted to SM120 in this image); do not bypass the guard.

Hypothesis: a different supported native helper, Triton, may have lower cost at these small decode matrices despite DeepGEMM's auto priority. Counterhypothesis: DeepGEMM is already superior or only wins/losses at isolated nonrepresentative shapes. A cheap direct screen decides whether there is any reason to allocate a full-model control/candidate. FlashInfer small-M cases are included only below its real guard to document that separate regime; they cannot be extrapolated to N54 steady state.

Primary sources, consulted 20 October: [deployed upstream FP8 helper source](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/layers/quantization/fp8_utils.py) and [FlashInfer GEMM API](https://docs.flashinfer.ai/api/gemm.html). Current web documentation is background; the local extracted source hash is the execution contract and every GPU rank asserts that actual installed file hash before running.

## Bounded experiment and numerical gates

One 8-GPU/10-minute isolated pilot per platform, no model loading, no weights copied. Eight independent GPU processes rotate backend order. Synthetic FP8 weights use 128x128 block scales, BF16 inputs, BF16 outputs. Shapes derive from the retained Qwen checkpoint config: TP8 packed QKV N1280/K4096 and O projection N4096/K1024, at M16/31/32/48/54/60/64. KV heads are replicated because four KV heads are fewer than TP8 ranks.

Each backend includes its real native activation quantisation and linear helper. Native DeepGEMM, Triton and (only M<32) FlashInfer DeepGEMM use the same generated tensors per case. Verify output shape/dtype/finiteness, relative RMSE <=5% against an explicit FP32 accumulation of BF16 input and dequantised FP8 weights, <=2% RMSE between backends, and unchanged input/weight/scale bytes after ordinary calls, graph replay and profiling. These are synthetic numerical sanity bounds, not model accuracy. Preserve partial/error results rather than counting a failed case as measured success.

Warm up/JIT before timing; capture 16 helper calls per graph, replay 10 times per sample, nine samples. CUDA-event microseconds are divided by all 160 calls to amortise host graph launch cadence. Report every rank/shape, not a cherry-picked fastest value. Profile CPU/GPU kernel names only after timing, on rank0 at M54, and save device UUID/clocks/power/VRAM before/after; those snapshots are not continuous scored telemetry. Python work is bounded at 450 seconds plus a 540-second external timeout inside the 600-second allocation.

A useful consistent >=5% improvement at representative M48/54/60/64, both projection shapes, all numerical/input gates and actual kernel proof can justify preparing a phase-specific full-model control/candidate. It cannot predict an end-to-end percent. Otherwise close the unsupported/losing branch and retain the data. Keep platforms separate; do not select model settings from a micro score or bypass native hardware guards.

## Resource and submission controls

H100: one node/eight GPUs, max **170.667 SU** for ten minutes, serial after any existing own 16-GPU allocation. Check real queue and fresh reconciled credit under the budget lock, at most three active PBS and one running allocation. Reserve before qsub; never retry uncertainty. H200: one node/eight GPUs, ten minutes, check under the shared watcher lock and remain within five active jobs including four preserved waiting model jobs. Do not cancel those jobs or modify their frozen bytes. No model/SLA/official accuracy claim, numeric shortcut, clock/power change, official package edit or background Codex.
