# NIXL production-span pilot

## Question and evidence

The prior two-H100 native probe established small synthetic memory registration and transfer, but used 1 KiB per KV range and only three auxiliary regions. Run 223788 advertised 190 KV ranges of 76,132,096 bytes each and ten auxiliary regions. This pilot tests whether native NIXL registration and request-scoped writes work at those full region sizes without loading model weights.

The retained role-builder source constructs the flat vector as target K, target V, draft K, draft V: each pool exposes `k_buffer + v_buffer`, then the draft pool vectors are appended. For PP=1 and start layer zero, the pinned helper's 95-entry K/V halves are recombined to the original 190-entry order. The CPU fixture AST-extracts both role builders, the pool ordering method, and the helper using labeled fake pointers. This source-level identity result is already reviewed in `eagle_kv_layout_review-20261023`; it does not prove that a live engine's pointer values and backing tensors match those source labels.

## Bounded experiment

Request two physical H100 GPUs on two distinct nodes, one rank per node. Each rank allocates 190 distinct CUDA uint8 spans of 76,132,096 bytes (14,465,098,240 bytes total), plus ten pinned CPU spans with exact lengths `[6144, 6144, 6144, 6144, 49152, 49152, 6144, 12288, 786432, 6144]`. No model, checkpoint, weights, full TP collective, or benchmark is loaded.

The rank pair uses mapped source/destination TP metadata 4 and 8, local/total KV heads 1 and 4, page size one, 256 bytes per slot, 297,391 slots, PP rank zero, and the observed empty `kv_layer_ids`. One native 95-to-95 case transfers source pages 1 and 297,390 to destination pages 0 and 297,389 across all 190 ranges. Pattern headers encode region and source page IDs; all 380 selected page hashes must be unique. Only the sender is patterned; the receiver retains the allocation-time sentinel in both KV and auxiliary spans. The receiver checks the selected pages and GPU-scans every other registered destination byte for the initial sentinel. The sender independently scans its own selected and untouched bytes after the transfers to verify source preservation.

The native `send_aux` call transfers slot zero across all ten auxiliary spans using each whole-buffer length as its diagnostic item size. This validates span registration/rkey coverage and byte integrity, but does not reconstruct production request-level auxiliary strides, which were not collected. Buffers stay referenced through NIXL agent lifetime and are released by rank process teardown.

## Limits and gates

This can establish two-rank physical transport for the stated registration and selected request pages, plus whole-buffer auxiliary transport. It cannot establish live engine tensor provenance, all-rank deployment behavior, model outputs, EAGLE correctness, latency under serving load, or request-level auxiliary layout. The NIXL agent and registration sources are pinned and checked at runtime. Integer T0 begins at batch-script startup: rank containers are bounded by T0+535 seconds, outer `pbsdsh` waits by T0+540, and the head semantic check by T0+555. Owned task processes are terminated/reaped by T0+563 and private exchange deletion has a three-second timeout. A final check enforces T0≤570 seconds inside the 600-second PBS walltime. Each rank independently records phase time, process RSS, and CUDA memory samples. Raw peer metadata and pointer tables stay in a mode-0700 runtime exchange directory; deletion status is explicit and a timeout is not reported as successful cleanup.

A GPU run has not been submitted or executed by this payload preparation. Runtime full-size registration/transport remains unvalidated.

## Root review correction

The first unsubmitted preparation patterned both ranks. That would leave source-page patterns in the receiver outside the destination writes and fail its untouched-span check; it would also prefill auxiliary expectations and hide a missing auxiliary write. Root corrected initialization to source-only before any GPU submission. A sparse CPU fixture runs the actual full-span verifier, accepts the expected destination mapping, and rejects the reproduced receiver-contamination case. Five CPU test functions pass after this correction. This was a preparation defect, not a failed GPU run.
