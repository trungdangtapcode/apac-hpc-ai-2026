# Research review: H100 replica diagnostic 224460

## Question and prior evidence

R2 asked whether the exact pinned SGLang FP8 activation quantizer could be supplied to the native HPC-Ops EP=1 and five-virtual-rank MoE calls while keeping the original numerical gates. The frozen R1 parent had exited before its first native call because an independent division-based quantizer produced different FP8 bytes. R2 retained the SGLang output as the actual native input and treated alternate quantizers only as diagnostics.

The proposed next cause for the R2 oracle discrepancy was that the independent FP32 MoE oracle omitted native intermediate formats. This review checks that cause against the exact upstream source for the installed build, rather than adjusting the oracle to match observed output.

## Exact run and evidence

Job `224460.pbs111` used one PBS-assigned NVIDIA H100 80 GB (SM90), seed 2026, synthetic 16-token/256-hidden/128-intermediate tensors, 128 logical experts, 130 physical expert slots and five serial virtual EP partitions. The pinned runtime reported `hpc-ops 0.0.1.dev0+gab1a402`; the submitted runtime source hashes match the R2 provenance. The job reached both native EP=5 and EP=1 calls and wrote all three relative-L2 metrics before failing its numerical gate.

The successful adapted collector preserved **30 terminal evidence files totaling 320,220 bytes**. `collected/evidence-sha256.json` lists each source path, byte size and SHA-256. The extracted files were checked against that manifest. The raw archive is `raw-evidence.tar.gz` (SHA-256 `9729258cbb5964f3e9e8b8c6e160c4d2279ce5819010414449b915894cfe5cb0`); the exact submitted payload is under `collected/hpc-ops-replica-r2-20261024/runs/224460.pbs111/submitted/`.

Observed diagnostics:

- The pinned SGLang FP8 activations differ from both direct-division and reciprocal-multiply PyTorch references at **3 of 4,096 values**: fraction **0.000732421875**, or **0.0732421875%**. The three byte pairs are retained in `output/result.json`.
- All **4,096 / 4,096** dequantized values satisfy the source-aware E4M3 spacing bound; violations: **0**. Maximum absolute dequantization error: **0.1183038**; RMS absolute error: **0.0261190**; relative L2 to the original BF16 input: **0.0255654**. These are activation quantization diagnostics, not MoE correctness results.
- Native EP=1 versus the old FP32 oracle: relative L2 **0.02292437665**, failed against the predeclared **0.02** limit.
- Native EP=5 versus the old FP32 oracle: relative L2 **0.02297911793**, failed against **0.02**.
- Native EP=5 versus native EP=1: relative L2 **0.00232611503**, or **0.2326115%**. This is pair agreement only; it does not establish correctness because both can share an omitted intermediate-format effect.
- The exact error was `relative-L2 gate failed`; PBS exit status was 2. The program's elapsed time was **22.922 seconds** and PBS walltime was **81 seconds**; PBS reports stage-out status **1** and exit status **2**. PBS accounting reports **90 seconds CPU time**, **637,676 KB** memory and **20,966,196 KB** virtual memory. The before/after GPU samples show 0 MiB at each sample; they do not measure utilization, peak VRAM, kernel time or hardware health. The budget ledger retains the submitted **21.333333 SU** maximum reservation pending unique accounting; no charge was inferred from the short runtime.

## Source check and assessment

The official Tencent/HPC-Ops repository at exact commit [`ab1a402724635507037426068f6cddc3d30dc0a8`](https://github.com/Tencent/hpc-ops/tree/ab1a402724635507037426068f6cddc3d30dc0a8) confirms the proposed missing stages:

1. [`entry.cc`](https://github.com/Tencent/hpc-ops/blob/ab1a402724635507037426068f6cddc3d30dc0a8/src/fuse_moe/entry.cc) allocates `gate_up_output` with BF16 dtype.
2. [`fuse_moe.cu`](https://github.com/Tencent/hpc-ops/blob/ab1a402724635507037426068f6cddc3d30dc0a8/src/fuse_moe/fuse_moe.cu) calls the gate-up blockwise FP8 GEMM, then activation-and-blockwise-quantization, then the down GEMM.
3. [`activation.cu`](https://github.com/Tencent/hpc-ops/blob/ab1a402724635507037426068f6cddc3d30dc0a8/src/activation/activation.cu) consumes BF16 gate/up values, computes `SiLU(gate) * up`, chooses `max(abs(product)) / 448` per routed row and 128-column block, multiplies by `1 / (scale + 1e-8)`, and casts to E4M3. The down GEMM result is stored in the BF16 output buffer. [`reduce.cu`](https://github.com/Tencent/hpc-ops/blob/ab1a402724635507037426068f6cddc3d30dc0a8/src/fuse_moe/reduce.cu) accumulates weighted BF16 contributions in FP32 and casts the final row to BF16.

This is direct source evidence that the old oracle used the wrong intermediate representation: it applied SiLU and the second linear layer directly to full-precision tensors, omitting the first GEMM BF16 store and the activation product's blockwise FP8 requantization. It is a plausible explanation for the small EP1/EP5-to-oracle gap, not proof that the corrected oracle will pass. No outputs from the intermediate native stages were captured, so their values were not independently compared. The CPU PyTorch linear accumulation order and SiLU implementation also will not reproduce native instruction-level math exactly; R3 retains the numerical gate to check the remaining difference.

## Next decision

The unsubmitted R3 oracle in [`hpc-ops-replica-r3-20261024/README.md`](../hpc-ops-replica-r3-20261024/README.md) models only source-documented intermediate casts and scales around independent FP32 linear operations. It continues to use the actual SGLang-quantized input for its oracle, retains the strict **2%** three-way relative-L2 limit and **1e-7** duplicate-copy limit, and does not fit any correction to the R2 outputs. Its CPU fixture validates source hashes, source-derived operations and toy quantization properties only. It has no GPU result and has not been admitted to PBS; root owns any next admission decision.

No claim is made that the synthetic replica path is correct, that the observed pair agreement proves correctness, or that this one-H100 test establishes distributed EP communication, Qwen accuracy, production routing, or serving performance.
