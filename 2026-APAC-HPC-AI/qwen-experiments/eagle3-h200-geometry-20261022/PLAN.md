# Prospective H200 NIXL KV geometry capture

This directory contains a CPU-validated instrumentation proposal derived from the native H200 target-only source. It is not integrated into a serving bundle, has not run on a GPU, and has not been submitted. Registration geometry, file-system cost and startup overhead therefore remain unmeasured on H200.

The goal is to retain enough actual allocator and NIXL registration shape to interpret the earlier small-buffer transport probes. A receipt records the same sanitized geometry immediately before and after the existing `register_buffer_to_engine()` call. The native registration method itself, address grouping, NIXL calls, registration order and transfer implementation remain byte-for-byte unchanged in the derived module. If collection sees malformed or missing required geometry, it fails before native registration so a diagnostic cannot silently pass with incomplete evidence.

## Pinned derivation

Input: `serving-tuning-10/s37-h200-target-reference/nixl-conn.py`, SHA256 `912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f`.

The derived `nixl-conn-instrumented.py` SHA256 is `45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8`. The only changes are a helper import and replacement of the one constructor call with a wrapper around that same bound native method. `DERIVATION.json` records the pinned source and output hashes. The helper is mounted as `sglang.srt.disaggregation.nixl.kv_geometry` beside the replaced `conn.py` module.

## Receipt contents and bounds

The JSON whitelist contains role name and experiment ID from explicit environment values; engine rank, pipeline rank, GPU rank, TP size, page size, KV head counts and layer IDs from native runtime arguments; per-region KV lengths, item lengths and VRAM/DRAM kind; auxiliary and state region lengths; and the registration-returned result. Exact page and token byte strides are recorded only where the integer divisibility checks succeed. Missing dtype and tensor strides are explicitly `not_collected` because this manager's `KVArgs` metadata does not provide them.

Pointers are used only for shape checks and are never serialized, formatted or hashed. Agent names, peer metadata, remote addresses and authentication material are outside the schema. Each rank writes unique atomic `before` and `after` files under `$QWEN_ARTDIR/kv-geometry`; hard-link publication refuses an existing filename. Limits are 8,192 regions, 1 MiB per receipt, 32 receipts and 32 MiB total for the expected 16 ranks.

`validate_kv_geometry.py` requires exactly one successful before/after pair for each of the four prefill TP ranks and eight decode TP ranks, with the expected role names, experiment identity, PP rank zero and stable geometry. It rejects extra fields, duplicate/missing phases, oversized or malformed records and unsuccessful registration. This inventory reflects the present three-worker TP4/TP4/TP8 deployment; any topology change requires an explicit validator update and review.

## Proposed integration after reference acceptance

Only after job 25495 passes its H200 exact-token and semantic gates, derive a separate candidate bundle. Copy the two files from this directory into that new bundle and use the derived module as the read-only mount for SGLang's NIXL `conn.py`. Mount the helper at `/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/kv_geometry.py`. Update the bundle's NIXL source hash to the derived module SHA and seal both files in its fresh manifest.

For each worker's `srun env`, set `QWEN_ROLE_NAME="$name"`; the existing worker launch already forwards the experiment ID and artifact directory. After all three worker endpoints report healthy and before sending client traffic, run:

```bash
python3 "$BUNDLE/validate_kv_geometry.py" "$ART/kv-geometry" \
  --experiment-id "$QWEN_EXPERIMENT_ID" \
  --expected-role prefill-0=4 \
  --expected-role prefill-1=4 \
  --expected-role decode-0=8
```

The diagnostic must fail if the collector or validator fails. Review the raw rank receipts and their hashes with the terminal run bundle. Measure added startup and shared-filesystem overhead on the first actual H200 run; CPU fixtures establish schema and control flow only. Keep the existing absolute startup and allocation deadlines.

## CPU evidence

`test_kv_geometry.py` extracts and executes the actual pinned `NixlKVManager.register_buffer_to_engine` AST method with mock NIXL registration. Eleven tests pass, covering unchanged addresses/order/kinds, successful return, native failure propagation, before/after records, whitelist redaction, malformed/missing arrays, exact divisibility, list and byte bounds, full 16-rank coverage, malicious whitelisted values, false and boolean-derived strides, and missing/extra receipt rejection. The validator independently checks all field types, limits, identities and geometry relationships, including the 1 MiB per-file cap. No mock result is evidence of production NIXL behavior, KV dtype, tensor stride or H200 runtime performance.
