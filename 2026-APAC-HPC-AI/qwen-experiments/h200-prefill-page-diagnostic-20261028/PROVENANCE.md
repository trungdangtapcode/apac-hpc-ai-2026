# Source provenance and static validation

Inspected 28 October 2026 from `/scratch/enroot-images/sglang-harbor.sqsh` with selective `unsquashfs` extraction. Exact image members:

| Image member | SHA256 | Relevant source evidence |
|---|---|---|
| `sgl-workspace/sglang/python/sglang/srt/layers/attention/flashinfer_backend.py` | `3cb0b4d5c4d3e8e94724d07c91130ab69d85e73c84cefaf3f69a5ad7813f5c7e` | Lines 74–75 import paged/ragged wrappers. Lines 474–475 construct ragged wrapper with workspace, `NHD`, backend. Lines 480–494 construct paged wrapper with workspace, `NHD`, backend. Lines 1300–1305 call paged `.forward(q, kv_cache, causal=causal, sm_scale=layer.scaling)`. Lines 1348–1355 call ragged `.forward(q,k,v, causal=causal, sm_scale=layer.scaling, logits_soft_cap=...)`; lines 1339–1345 set causal true except cross-attention/encoder-only cases. |
| `usr/local/lib/python3.12/dist-packages/flashinfer/prefill.py` | `7f4926dcf1610dfd058716e9ba3d8b08f15268e607ea1e28bef7d28b8b2f889e` | `BatchPrefillWithPagedKVCacheWrapper.plan` starts line 2080 and accepts query/paged-KV indptr, page indices/last-page lengths, head counts/dimensions, page size, causal, scale, and dtype arguments. Paged `.forward` at 2504 accepts Q/cache and causal/scale; `.run` overloads start 2531. `BatchPrefillWithRaggedKVCacheWrapper.plan` starts 3208 and accepts qo/kv indptr, head counts/dimensions, causal, scale and dtypes. Ragged `.forward` at 3597 accepts Q/K/V and causal/scale; `.run` overloads start 3623. |

The source establishes correct API names and argument shapes for implementation. `forward` is explicitly marked deprecated in native docstrings in favor of `run`; a final script should use documented `plan` and `run` APIs and match their installed signatures. Do not reuse guessed decode `plan` argument names: prefill uses `head_dim_qk`, and paged prefill additionally requires `qo_indptr` and `paged_kv_*` metadata.

## Failed and corrected extraction attempts

Initial `unsquashfs -cat` attempts failed because this installed utility does not support `-cat`. The `-ll` listing exposed names prefixed by `squashfs-root/`; passing that display prefix to selective extraction yielded zero files. Corrected command (successful, 2 files extracted):

```sh
unsquashfs -processors 2 -no-progress -d /tmp/pfextract4 /scratch/enroot-images/sglang-harbor.sqsh \
  sgl-workspace/sglang/python/sglang/srt/layers/attention/flashinfer_backend.py \
  usr/local/lib/python3.12/dist-packages/flashinfer/prefill.py
```

The two extracted source files are retained under this directory's `source/` tree and covered by `source/SHA256SUMS`; the duplicate source retention is limited to those two reviewed files. `validate_sources.py` checks their exact hashes, parses the native wrapper AST signatures, and verifies the diagnostic's paged/ragged plan/run argument bindings.

## Preparation status

Static API/source review and implementation: prepared. `sha256sum --check SHA256SUMS`, the offline AST/source validator, Python bytecode compilation, and `bash -n job.sbatch` pass. No CUDA runtime validation, native execution, submission, scheduler receipt, measurement, or correctness result exists. This record must not be interpreted as evidence that any prefill case ran.
