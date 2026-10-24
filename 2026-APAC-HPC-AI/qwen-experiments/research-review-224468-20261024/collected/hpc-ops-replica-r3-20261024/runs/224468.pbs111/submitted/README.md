# Prospective R3: source-modeled MoE intermediate-format oracle

## Question and prior evidence

R2 job `224460.pbs111` completed both native HPC-Ops calls, but the EP=1 and five-virtual-rank outputs differed from the independent FP32 oracle by relative L2 **0.02292437665** and **0.02297911793**. Both exceed the predeclared **0.02** limit. The native EP5/EP1 pair differs by **0.00232611503** (**0.2326115%**), which is agreement between implementations, not a correctness pass.

R2's actual SGLang activation input had only **3 / 4,096** byte differences (**0.0732421875%**) versus each independent quantizer, and all 4,096 values satisfied the E4M3 rounding bound. That mismatch is not a basis for changing the oracle or any threshold.

## Source-supported hypothesis

The old FP32 oracle omitted real intermediate formats in the pinned native operator. Official Tencent/HPC-Ops source at commit `ab1a402724635507037426068f6cddc3d30dc0a8` shows:

- The gate-up GEMM output buffer is BF16 (`src/fuse_moe/entry.cc`).
- The fused path runs gate-up blockwise FP8 GEMM, activation plus blockwise FP8 quantization, then down GEMM (`src/fuse_moe/fuse_moe.cu`).
- Activation reads BF16 gate and up values, computes `SiLU(gate) * up`, computes a row/block scale as `max(abs(product)) / 448`, multiplies by `1 / (scale + 1e-8)`, then casts to E4M3 (`src/activation/activation.cu`).
- Down-GEMM contributions are BF16; top-k reduction accumulates weighted contributions in FP32 and stores BF16 (`src/fuse_moe/entry.cc`, `src/fuse_moe/reduce.cu`).

Selected upstream files, commit, license and SHA-256 values are retained in `pinned-source/tencent-hpc-ops/`. `HPC_OPS_SOURCE_PROVENANCE.json` records exact source hashes. The compiled extension remains from the image and is not represented by these source copies.

## Prospective change

R3 is derived separately; frozen R1 and R2 payloads are untouched. It replaces only the oracle pipeline. Independent FP32 linear operations still use the actual dequantized SGLang activation and actual dequantized quantized weights. It now models the source-documented sequence: BF16 gate-up output, SiLU product from those BF16 values, per-row/block E4M3 requantization with the source scale and reciprocal epsilon, down GEMM, BF16 contribution, FP32 top-k weighted accumulation, and final BF16 cast.

This is a source-derived comparison model, not a copied native result or a fitted correction. The implementation verifies the retained upstream source hashes before native work starts. It continues to call the native API with the actual SGLang quantized input. The independent Torch linear operations and `F.silu` do not reproduce the native GEMM accumulation order or its fast-math implementation bit for bit; the 2% gate remains the required numerical check.

## Gates and limits

The existing gates are unchanged: all three relative-L2 measurements must remain **<= 0.02**, and the exact duplicate-copy oracle must remain **<= 1e-7**. A failure remains a failure. No threshold increase, output-specific bias, or fit to the R2 numbers is allowed.

`cpu_fixture.py` checks upstream hashes, source code evidence, oracle stage markers, unchanged thresholds and a small CPU-only BF16/E4M3 arithmetic fixture. It does not emulate CUDA, PyTorch kernels, Triton, HPC-Ops, H100 rounding behavior, or the native MoE result. The R3 bundle is **unsubmitted** and has no GPU result. One GPU, synthetic shapes and serial virtual partitions remain the experiment's scope; distributed communication, real routing, model accuracy and serving speed remain untested.

Root owns any scheduler admission. This directory creates no job, queue reservation or GPU authorization.
