# H200 FlashInfer FP8 KV primitive

## Scope

This bundle is a single-GPU, at-most-10-minute compatibility check for native
FlashInfer attention over synthetic `torch.float8_e4m3fn` KV tensors in NHD
layout. It loads no Qwen weights and starts no server. It can establish only
that the selected calls execute on one H200 and agree with the FP32 attention
oracle on the same rounded cache values within the predeclared 2% relative-L2
limit. It cannot establish model accuracy, calibrated KV scales, serving
throughput, speedup, memory fit, contest eligibility, or the official 99%
accuracy gate.

## Fixed experiment

- Image: `/scratch/enroot-images/sglang-harbor.sqsh`, the same pinned image
  reviewed by [the source preflight](../fp8-kv-source-preflight-20261023/REPORT.md).
- Source inventory: [SOURCE_MANIFEST.json](../fp8-kv-source-preflight-20261023/SOURCE_MANIFEST.json).
  It contains SHA-256 hashes for the extracted SGLang source files. In
  particular, `flashinfer_backend.py` is
  `3cb0b4d5c4d3e8e94724d07c91130ab69d85e73c84cefaf3f69a5ad7813f5c7e`, and
  `kv_cache_dtype.py` is
  `1931b22b3e271e0a2fc6b541ba1b3c0b00c01a01c479e6b8034be26ec30c0c41`.
  The full 25 GiB squashfs image has no recorded content digest in the prior
  source preflight; its path and read-only extraction provenance are retained
  there. Do not treat the SGLang file hashes as a digest of the entire image or
  of the separately installed FlashInfer Python package.
- The native script records the runtime FlashInfer version. It calls
  `single_decode_with_kv_cache` and `single_prefill_with_kv_cache` directly
  using `kv_layout="NHD"`, FP8 E4M3 cache tensors, explicit scales, and the
  lower-right causal custom mask for prefill. An unsupported API raises and
  fails the primitive; there is no alternate API or backend fallback.
- Seed: 2026. Context: 4,000 tokens. Query dtype/output dtype: BF16.
- Synthetic scale cases: K/V scales `1.0/1.0` and `0.5/0.5`.
- Local head geometries: TP4 (`q_heads=16`, `kv_heads=1`) and TP8
  (`q_heads=8`, `kv_heads=1`), each with head dimension 128. The source has an
  opt-in TP1 geometry for separate use; the batch script does not enable it.
- The mask aligns the query block to the end of the KV span. For the three
  checked queries over 4,000 keys, allowed-key counts are 3,998, 3,999, and
  4,000. CPU validation checks that convention independently of FlashInfer.
- The Slurm script preserves the scheduler's `CUDA_VISIBLE_DEVICES`, checks
  exactly one visible device, requires an H200 name and SM90 capability, and
  records the GPU UUID. The container stage has a 480-second timeout within
  the 600-second allocation. Raw Slurm stdout/stderr and `result.json` belong
  under `runs/<job-id>/`.

## How to read the two error measurements

`*_rel_l2_vs_same_rounded_fp8` compares FlashInfer's BF16 output to an FP32
oracle that reads the exact rounded FP8 K/V tensors and applies the same
synthetic scales. This is the kernel-agreement check and is gated at 0.02.

`*_rel_l2_vs_original_bf16_kv` compares that same output with an FP32 oracle
using the original unquantized BF16 K/V source. It includes the effect of FP8
rounding (and BF16 output conversion), so it is a quantization-impact
diagnostic, not the kernel-agreement gate. A larger value here does not by
itself indicate a kernel defect. Neither number is a model-quality score.

## CPU-only validation

Run `python3 -m py_compile primitive.py validate-cpu.py` and
`python3 validate-cpu.py`. These checks require only the Python standard
library and do not claim GPU execution. They cover geometry, the production
mask convention, fixed seeds/scales, scale-aware scalar attention, and the
separate error fields. The native runtime result is the only source of a GPU
pass receipt.

## Review status

See [ROOT_REVIEW.md](ROOT_REVIEW.md). It is a review template until a real job
has been submitted and its raw output inspected. A source or API incompatibility
is a failed diagnostic, not grounds to substitute a different image or API.
