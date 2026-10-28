# H200 KV page-size feasibility review

**Date:** 2026-10-28 UTC  
**Decision:** Conditional go for a bounded same-GPU source/runtime geometry probe; no-go for a full Qwen or P/D retry yet. Page size 16 is the better first candidate. This is read-only source research, with no GPU, model, scheduler, or external service used.

## Question and current baseline

The current valid result is N64, score 26766 (3045.501509), using P4+P4/D8, page size 1, DeepGEMM prefill with chunk 8192, breakable prefill and FA3 attention, and HPC-Ops/FlashInfer/MNNVL decode. Larger-chunk and N68 branches are closed unchanged. The proposed intervention changes page size to 16 or 64; all other settings and source must stay pinned for a causal comparison.

The existing source preflight at `fp8-kv-source-preflight-20261023/REPORT.md` qualifies only an FP8-KV plumbing primitive, and already warns that actual layer IDs and D-role KV heads are uncollected. The current receipt collector records `page_size_tokens`, but the validator permits missing D-role head fields only for the exact page-size-1 signature (`runs/26766/submitted-payload/validate_kv_geometry.py`, constants lines 24–34, gate lines 90–105). Its source-backed implicit MHA signature also pins page size 1. These exceptions cannot be widened by assumption.

## Findings from exact pinned source

- The pinned image is `/scratch/enroot-images/sglang-harbor.sqsh`; the preflight’s `SOURCE_MANIFEST.json` records selected-file hashes. Extracted source identifies that on Hopper/H200, automatic backend selection uses FA3 for MHA/Qwen unless speculative top-k > 1 **or page_size > 1**; otherwise it selects FlashInfer when available (`source-image/.../server_args.py:5658–5663`). Thus either 16 or 64 changes the automatic attention path away from FA3. The existing candidate’s FA3 result does not establish behavior or speed of the resulting FlashInfer path. Explicitly forcing FA3 is not justified by this selector evidence.
- `server_args.py:8758–8763` requires positive-chunk prefill size divisible by page size. Chunk 8192 is divisible by both 16 and 64, so this check alone does not block either candidate.
- NHD pool allocation and descriptor code are page-aware, but the actual buffers/layout and per-page item lengths depend on selected layout and runtime geometry (`memory_pool.py:1798–1834, 2051–2129, 2198–2212`). For vectorized_5d, a page must be divisible by `X=16/store_dtype.itemsize`; this may further constrain layouts (`memory_pool.py:1824–1834`). Do not extrapolate current page-1 receipt strides into page 16/64.
- P/D handshake checks that both roles advertise the same page size and KV dtype (`disaggregation/common/conn.py:528–544`). The native NIXL transfer constructs page/token offsets from its page-size and descriptors; the patched `nixl-conn.py` is the required transport source (hash below). Source-level page arithmetic does not prove correctness for new actual head geometry or address layouts.
- The model’s `--decode-attention-backend flashinfer` and MNNVL settings refer to attention and communication/MoE paths respectively; MNNVL is not evidence that the KV page layout is compatible. Need inspect resolved backend per role after page change.
- The `nixl-ondemand` implementation contains generic page-based address and byte slicing (`nixl-ondemand/conn.py:315–327, 783–817, 1618–1625`), but its page-1/4/16 range checks are not proof of supported FlashInfer kernels, NIXL patch behavior, or Qwen geometry. Page 64 is a larger extrapolation.

## Minimum gate before any full-model retry

First run one rank on one H200, inside the exact pinned image and native submitted source, without loading Qwen weights. Use the intended Qwen MHA local head shape only if that shape is obtained from pinned model metadata/source rather than guessed. Compare page 1 control to page 16 candidate (leave 64 for a separate follow-up only if 16 fails a clear hypothesis). Collect: resolved attention backend; pool class/layout; K/V tensor shapes, strides, storage dtype; observed page size; actual per-region bytes, page item lengths and token strides from `get_contiguous_buf_infos()`; layer/rank identifiers where available; and a write/read attention correctness check against page-1 reference over token positions including page boundaries and partial final page. Preserve any uncollected fields as such.

If that passes, the next gate is not a full model score: start both same-GPU P/D roles with matched candidate page size and native patched NIXL, register and transfer a small deterministic KV payload across page boundaries, then verify destination bytes/attention output and record before/after native geometry receipts. This gate must cover the actual candidate H200 role layout and show resolved attention backends; failure or missing head/layer identity blocks full-model P/D work. Only after this gate should an owner-gated, budgeted full-model trial be considered. Keep the page-size change isolated from FP8 KV or other interventions.

## Provenance and hashes

- `runs/26766/submitted-payload/nixl-conn.py`: SHA-256 `45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8` (native patch source).
- `runs/26766/submitted-payload/kv_geometry.py`: SHA-256 `bc7972ac2207b12d479e6d46df092486ffe792a18497305a1b3f88971b45e18a`.
- `runs/26766/submitted-payload/validate_kv_geometry.py`: SHA-256 `08a3ce36db9ba031ed8d2df0003e68e1d7d222483e544eb1b36afaf170c3a47e`.
- Extracted pinned `server_args.py`: SHA-256 `79d9bbb61b429574e31e7a7e319831fcd129a83a475e6ffe2b7e8a5e8eb06b0f`.
- Extracted pinned `memory_pool.py`: SHA-256 `29ef7b37d2e12b1a4b674b97c33b3ceb05cd8421a3742eb33cb6a75f52896ddc`.
- Extracted pinned `disaggregation/common/conn.py`: SHA-256 `ba33d63c6920f87b55cf57f9224bb7d08af67e1476bd70b8e1a70067f33a29d7`.

No validator exception was changed and no claim is made that page 16 or 64 preserves the current runtime head count, layer identity, layout, attention backend, NIXL interoperability, or score.
