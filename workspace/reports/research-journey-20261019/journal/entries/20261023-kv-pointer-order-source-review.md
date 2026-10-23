# 23 October: a suspicious intermediate list was not a proven transport bug

**Concept.** A pointer identifies a memory buffer. Transfer correctness depends on the final list of source/destination buffers and byte offsets. A temporary grouping can look strange without changing that final mapping.

**Question and prior evidence.** Full H100 transport 223055 failed remotely; current H200 candidate 25682 remains pending. Actual 223788 EAGLE3 prefill registers 190 KV regions, built from 94 target K buffers, 94 target V buffers and one draft K/V pair. Does splitting that list at 95 accidentally map the wrong tensors?

**Source and control.** Extracted only relevant files from the pinned serving image, retaining hashes. Actual native prefill/decode builders append the draft vector after target. The PP helper temporarily splits at 95. For this PP=1 / start 0 configuration, the full halves recombine in original order; the plain 188→190 special case selects only the target 94 K/V pairs. Root also executes the exact frozen candidate's request-plan/head-slice methods on labeled CPU origins for all eight valid TP4→TP8 head-peer pairings and both 190→190/188→190 cases: 16 checks pass. [Exact source, fixture and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle_kv_layout_review-20261023/REPORT.md).

**Assessment.** No source-proven ordering bug exists for the candidate as configured. Do not modify its frozen transport based on the misleading intermediate split. CPU labels and a pointer-container shim do not verify physical tensor origins, actual NIXL writes, all possible PP stages, model output or speedup.

**Next decision.** Preserve 25682's queue position and runtime/output gates. Prepare a separate two-H100 full-span transfer diagnostic using actual 190-region/ten-auxiliary geometry; require actual byte integrity and bounded cost before treating it as component evidence. No new GPU job or reservation exists at this source-review checkpoint.

**Spoken explanation.** We suspected the cache addresses were reordered incorrectly. After tracing the complete function chain and checking independent labels, we found the final list was unchanged. That let us close an unsupported code-fix branch and test the remaining real transfer question instead.

**Preservation.** Keep the negative hypothesis and exact source/CPU checks, link the learning journey, then capture and push this small milestone. No model weights, credentials or HPC work are included.
