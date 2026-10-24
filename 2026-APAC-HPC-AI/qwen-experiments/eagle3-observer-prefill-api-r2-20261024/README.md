# EAGLE3 TP4 observer preflight

This folder is a prepared one-node, four-H100 readiness probe. It is separate from the prospective 16-rank full correctness candidate and is **not submitted**. Root owns independent review, final freezing, reservation, and any submission.

The runtime starts only `prefill-0` at TP4 and checks actual H100 visibility, the target/draft source and runtime preflights, BF16 allocations, disabled prefill graphs, NIXL initialization, HTTP health, and exactly four real `MetadataBuffers` metadata receipts with two actual loaded-module hash reports. The new probe validator is explicitly scoped to `prefill-0=4`. The full-P/D validator remains strict for two TP4 prefill roles plus TP8 decode.

This probe does not use the prior 223788 geometry files or its unsupported nonempty layer-ID gate. The source's failure stays preserved in its original folder. This draft emits no user request, output-ID comparison, transport workload, AIPerf profile, score, or EAGLE3 performance claim.

## CPU preparation checks

`payload/test_prefill_observer_gate.py` checks only receipt-schema acceptance/rejection with synthetic CPU JSON. The six tests under `payload/pd-observer/tests/` exercise fake tensors and mocked methods. Python compilation and Bash syntax checks validate draft code interfaces. None of these checks simulates H100 runtime behavior or counts as observer readiness proof.

The runtime script requires root's final `payload/SHA256SUMS` freeze manifest and exits before launch if it is absent. No submit helper is included.

## Derived correction, 24 October

Parent job224275 failed before model loading because the HPC API preflight called nonexistent `torch.cuda.get_device_count()`. R2 changes that single call to `torch.cuda.device_count()`. The original failing snippet fails a strict CPU CUDA API stub, while the corrected embedded snippet passes. Native model, observer, source/runtime, four-rank receipt, health and time-budget gates remain unchanged. A CPU stub is not GPU execution. This supersedes the inherited preparation-only draft status; submission and actual GPU proof are separate receipts.
