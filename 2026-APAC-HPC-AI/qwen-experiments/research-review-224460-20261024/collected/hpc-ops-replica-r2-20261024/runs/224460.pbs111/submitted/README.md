# Prospective R2: source-aware activation quantization diagnosis

## Question and prior evidence

Can the pinned SGLang FP8 activation quantizer feed the native HPC-Ops expert-replica diagnostic when its FP8 result differs from an independent PyTorch group quantizer by rounding, while preserving a strict, interpretable numerical gate?

The frozen parent, `hpc-ops-replica-primitive-20261024`, tested 128 logical experts, 130 physical experts, five sequential virtual partitions of 26 experts, and exact replicas at physical IDs 128/129. Its submitted payload must remain unchanged. Job `224278.pbs111` exited 2 after 83 seconds of PBS walltime (the program recorded 23.645 seconds) at the exact-byte activation comparison, before the first native HPC-Ops MoE call. Scales passed the preceding comparison. The partial result and raw submission are preserved in the linked review. This is a failed pre-kernel diagnostic, not a passed or partially passed replica primitive.

The pinned runtime file is `pinned-source/sgl-workspace/sglang/python/sglang/kernels/ops/quantization/fp8_kernel.py`, SHA-256 `c690ea19a6ca401c07e60a835c2470039d8f99e1574196f0d5e14e3c6797c742`. Its Triton kernel converts loaded values to FP32, computes `scale = max(abs(x), eps) / 448`, computes `scale_inv = 1 / scale`, multiplies `x * scale_inv`, clamps to the FP8 limits and casts to the FP8 dtype. The frozen fixture independently computed `x / scale`, then clamped and cast. These are algebraically equivalent but need not produce identical FP32 intermediates or identical FP8 boundary rounding. The runtime source and package version are also carried in the exact remote submitted bundle and checksum manifest.

## Hypothesis

The first mismatch is due to the source-documented multiply-by-reciprocal versus direct-division path (or the final FP8 conversion at a representable boundary), rather than an incorrect scale or non-finite activation. This is only a hypothesis until mismatch counts and values are inspected. R2 must quantify it and still reject malformed activations or a MoE result that exceeds the existing numerical tolerance.

## Prospective R2 change

Start from a byte-for-byte copy of the frozen source into this separate directory. Keep seed 2026, BF16 input generation, 128-wide groups, 448 FP8 maximum, expert tensors, routes, weight copies, native API arguments, and all existing MoE thresholds unchanged. Before making an edit, verify the source hash above against both the frozen local source and the remote submitted `SOURCE_SHA256SUMS` / `submitted` copy. Record source paths and hashes in the R2 provenance file. Do not edit or re-upload the parent.

The activation check will:

1. Keep the pinned SGLang quantizer as the exact input to every native HPC-Ops call. Require expected shape and dtype, finite quantized values and scales, positive finite scales, exact scale shape, and the existing scale comparison.
2. Compute two diagnostic references on the same seeded pre-quantized input: the current direct-division reference and a multiply-by-reciprocal reference matching the pinned Triton expression. Record each reference's byte mismatch count and fraction versus SGLang output, grouped by byte pair; do not assume either reference matches the Triton execution.
3. Record input, scale, and FP8 extrema; mismatch byte pairs; count and fraction; and maximum/RMS absolute dequantized-input error and relative L2 against the original FP32 view. Calculate a per-value FP8 rounding bound from the adjacent finite E4M3 representable values and that value's group's actual scale, with a small explicit FP32 arithmetic allowance. Require all actual dequantized values to fall within that source-aware bound. Saturation, non-finite values, invalid scales, unexpected shapes/dtypes, or bound violations remain hard blockers.
4. Atomically write this activation diagnostic to the partial result JSON before raising any numerical gate. Thus a rejected gate retains the metrics that explain why it failed.
5. Continue the native EP=1 and five virtual-rank calls with the actual pinned `x_q` and `x_scale`. Build the independent FP32 MoE oracle from those same actual quantized activations dequantized by the actual scales. This avoids making the oracle depend on identical activation bytes from a separate quantizer. Preserve the current three relative-L2 checks at 2% and the duplicate physical-copy oracle at `1e-7`; write their partial metrics before threshold failures as well.

R2 retains the same one-H100 scope and synthetic limitations as its parent. The result can only establish the tested local native API geometry; it cannot establish multi-GPU communication, production dispatch, Qwen accuracy, or performance.

## CPU-only checks and limits

The CPU fixture may verify that the diagnostic helper counts mismatches, groups byte-pairs, computes fractions and rejects deliberately malformed metric inputs. Source-string checks may confirm the pinned kernel's reciprocal multiply and cast sequence and confirm that runtime hashes are compared before execution. Such fixtures test bookkeeping and source provenance only. They do not emulate Triton, FP8 hardware rounding, CUDA, the HPC-Ops extension, or prove the GPU path. The actual-device quantization and native calls remain required for any GPU conclusion.

## Prospective gates and decision

- Source/image/package hashes match the preserved provenance; the public `hpc.fuse_moe_blockwise` callable and expected signature are checked before any native work.
- Exactly one assigned H100 SM90 is visible; fixed seed and all existing tensor/route invariants pass.
- Actual scales and FP8 activations are finite with correct shapes/dtypes; source-aware dequantization error satisfies the calculated rounding bound.
- Full mismatch diagnostics are persisted before any numerical gate raises.
- Native EP1, five virtual rank contributions, and the independent oracle all run on the same actual quantized activations.
- Existing MoE relative-L2 and duplicate-copy gates remain unchanged.

This directory is an unsubmitted research plan and implementation workspace. It creates no scheduler, budget, queue, or submission authorization. R2 requires root review of the exact runtime source and any eventual immutable payload before admission.
