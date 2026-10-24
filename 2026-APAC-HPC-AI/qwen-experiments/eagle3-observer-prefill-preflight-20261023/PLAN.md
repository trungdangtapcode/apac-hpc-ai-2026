# H100 TP4 observer preflight

**Status: PREPARED_NOT_SUBMITTED.** This is a separate 4-H100 readiness-only proposal. Root owns review, freeze, budget reservation, and submission. No GPU was started, no queue or ledger was touched, and no reservation was created.

## Prior evidence and question

The source is the retained H100 geometry probe for job **223788.pbs111**. Its four prefill ranks reached native initialization, but its strict geometry gate failed on an unsupported nonempty layer-ID assumption. This proposal preserves that run and failure unchanged. It does not reuse the old geometry instrumentation or nonempty layer-ID gate.

The question is whether the new `MetadataBuffers.get_buf_infos()` observer integrates in the actual four-rank H100 serving process and records one complete actual metadata receipt for every initialized TP rank. The proposed allocation contains one TP4 prefill worker and no decoder, router, transfer client, output client, or performance workload. Native `/health` readiness may perform an internal health check; that is not an explicit correctness request.

## Controlled setup

Use the same public target FP8 files and pinned EAGLE3 draft with the known BF16/unquant recipe, eager prefill graphs disabled, TP4/EP1, 4,096-token chunking, HPC-Ops, and the original 912b7 NIXL module. The worker runs the retained H100, draft digest, dynamic-grad-mode, and graph-source preflights. The only serving-process observer change is adding the reviewed `pd-observer/` directory to `PYTHONPATH` immediately before server launch. Its `sitecustomize` hook verifies the actual loaded utility/NIXL module hashes, wraps `MetadataBuffers.get_buf_infos()`, and writes metadata-only receipts.

The allocation envelope is one H100 node with four GPUs, project 59010042, queue `normal`, 15 minutes maximum (128 SU ceiling). T0 bounds startup at 720 seconds, the strict receipt check at 780 seconds, and cleanup at 840 seconds inside the 900-second PBS walltime. Runtime initialization and receipts are not measured by CPU fixtures.

## Acceptance gate

Require an HTTP 200 health response and the SGLang server-ready log; exact four H100 visibility; the expected SGLang graph-source hashes; exact pinned draft SHA; exact unchanged NIXL SHA `912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f`; resolved TP4 EAGLE3 prefill arguments; two BF16 KV allocation messages, two disabled-prefill-graph messages, and one NIXL initialization per actual TP rank; and no fatal startup line or prefill graph capture.

The separate `check_prefill_observer.py` gate requires exactly four `prefill-0` metadata receipts with ranks 0–3, correct initialized TP rank identity, equal ordered names and measured per-item widths/dtypes across ranks, all three source-list equality checks true, and actual loaded source reports for pinned `utils.py` plus the 912b7 NIXL module. Receipt row counts and widths are reported from runtime tensors; no geometry or hidden-state width is guessed. Missing or contradictory records fail the probe.

This check uses only the new observer metadata schema. It records no unsupported layer IDs and makes no requirement on NIXL registration receipt content. There is no actual model output comparison, KV/aux transfer, cross-role comparison, score, or claim about EAGLE3 correctness.

## CPU validation and limits

Six fake-tensor/mock-transfer observer tests are retained in `payload/pd-observer/tests/`. `test_prefill_observer_gate.py` validates only the four-rank schema against synthetic CPU receipts, and `bash -n` plus Python compilation check the draft interfaces. Those checks test serialization, validation, and syntax; they are not runtime evidence. The only acceptable evidence for observer integration is the later actual four-H100 PBS run reviewed by root.

Only source files selected from the prior payload manifest are copied. The old instrumented native module, geometry helper, layer-ID gate, previous receipts, payload tarball, and submission helper are excluded. The native NIXL method implementation remains the exact 912b7 source.
