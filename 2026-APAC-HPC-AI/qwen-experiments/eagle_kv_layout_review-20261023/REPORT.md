# Native EAGLE3 MHA KV pointer order review

**Review date:** 2026-10-23  
**Result:** No source-proven pointer-order mismatch for candidate 25682's PP=1 path. GPU/NIXL transfer correctness remains unproven.

## Question and conclusion

The candidate has 94 target MHA layers and one EAGLE3 draft MHA layer on each worker. The count is 190 pointers per rank because each MHA pool exports one pointer per K buffer and one per V buffer. The concern was whether `get_mha_kv_ptrs_with_pp` halves the list at 95 and therefore reassigns a target V pointer or draft pointer to the wrong transfer origin.

Pinned `MHATokenToKVPool._pd_registerable_tensors` returns `k_buffer + v_buffer` (`memory_pool.py:2193-2196`). The prefill builder appends draft pointers after the target pointers (`prefill.py:217-229`); the decode builder does the same (`decode.py:453-466`). Thus the constructed order is:

```text
Ktarget[0..93], Vtarget[0..93], Kdraft[0], Vdraft[0]
```

The NIXL helper splits at the midpoint (`common/conn.py:792-823`). For 190 pointers it temporarily labels target `V0` as the 95th K-side pointer and starts the V-side view at target `V1`. But the NIXL heterogeneous-TP path then concatenates the selected K-side and V-side pointer slices in the same order (`nixl/conn.py:852-859`). Candidate 25682's prefill has PP size 1 and start layer 0, so both slices span their full 95-entry halves and recombination is identity. The final source and destination pointer vectors retain the original target-K, target-V, draft-K, draft-V order. The candidate's worker command has no PP-size override and enables EAGLE3 for both roles (`serving-tuning-10/s39-h200-eagle3-correctness/worker.sh:45-57`).

The 188→190 path also behaves as intended for the ordinary no-draft prefill to EAGLE3 decode case: its explicit special case selects target K/V entries only (`common/conn.py:804-815`). This matches the prior synthetic 94→95 pointer probe but does not stand in for a transfer.

Both role builders set `kv_layer_ids=[]` when a draft pool exists (`prefill.py:230-235`; `decode.py:467-472`). The NIXL equal-TP/MLA path permits positional pairing when PP=1 (`nixl/conn.py:1066-1071`; `utils.py:890-929`). The MHA auxiliary metadata pointers and item lengths are carried in separate `aux_*` fields (`prefill.py:243-244`; `decode.py:477-479`) and do not enter the 190-entry KV vector.

## CPU identity evidence

[cpu_native_layout_fixture.py](cpu_native_layout_fixture.py) AST-extracts the actual pointer assembly statements from both role builders and the actual `get_mha_kv_ptrs_with_pp` method from the pinned source. With labeled fake pointer origins, the 190→190 PP=1 case preserves the complete expected order on both sides. The 188→190 case selects all 94 target layers on both sides. Output is retained in [cpu_native_layout_fixture.json](cpu_native_layout_fixture.json).

This proves only Python list-origin/order behavior for the extracted source. It does not import SGLang, allocate a model or GPU buffer, invoke NIXL, or prove that runtime tensors, item strides, registration spans, and transfer bytes match the source model.

## Evidence and limits

The 23 October H200 candidate 25682 is pending resources. Its derived NIXL source has native base SHA256 `912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f` and geometry wrapper SHA256 `45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8`; the wrapper is documented as adding sanitized geometry observation around the registration call. The relevant upstream selector and pool construction were extracted from `/scratch/enroot-images/sglang-harbor.sqsh`; file hashes and image metadata are in [SHA256SUMS](SHA256SUMS) and [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json).

The earlier 223788 registration/readiness gate and three synthetic transfer layouts established counts/readiness and fake-layout behavior, not actual runtime pointer-origin bytes. No live GPU transfer, full-size span, actual tensor stride, NIXL copy, or output correctness was established here. A bounded actual-buffer NIXL probe can still add evidence about registration scale, per-entry strides, and transfer bytes; it is not needed to resolve a source-level PP=1 ordering mismatch because none was found. Nonzero PP stages with appended draft pools are outside this candidate configuration and were not certified by this review.

## Next evidence needed

Use any already-authorized bounded native transfer probe to label and verify bytes written through the exact 190-entry production geometry, preserving separate per-entry origins and auxiliary-item checks. Keep the eventual H200 25682 result gated on its existing runtime geometry, semantic receipts, and complete output checks; this review does not relax those gates.

## Root verification against the exact queued patch

The source-image review above is now supplemented by [candidate_patch_identity.py](candidate_patch_identity.py). It executes the exact frozen 25682 `_init_hetero_tp_prep_handle` method and pinned `compute_head_slice_params`, using the native role-builder and PP selector outputs. All 16 cases pass: eight valid TP4→TP8 head-peer pairs for 190→190, and the same eight for 188→190. Source/destination ordering, 256-byte item strides/length and zero per-head offsets agree with independent expected origins. Only NumPy's opaque pointer-container conversion is replaced by a CPU list shim; no memory layout, GPU or NIXL execution is inferred. [Actual results](candidate_patch_identity.json).

This closes the specific source-ordering suspicion for the queued PP=1 candidate; it does not relax any runtime or exact-output gate and does not warrant changing its frozen transport. A full-span registration/byte-transfer pilot remains a distinct question. No GPU allocation or PBS SU was used for this review.
