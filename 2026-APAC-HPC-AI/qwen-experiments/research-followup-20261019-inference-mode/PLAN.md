# Matched decode inference-mode experiment

The latest baseline repeat 221886 passes at 2425.886 good output tokens/s and provides CPU/GPU traces on all 16 ranks. Decode traces contain view, slice, copy and indexing operations around CUDA graph launches. This does not prove CPU limitation: much of the runtime time is synchronisation waiting and profiling perturbs the service. It does justify a bounded test of a supported host-overhead option instead of more unverified NCCL protocol sweeps.

The pinned runtime's `utils/common.py` defaults `DynamicGradMode` to `no_grad`; setting `SGLANG_ENABLE_TORCH_INFERENCE_MODE=1` selects inference mode before decorators are imported. Both scheduler event loops use that decorator (`scheduler.py`, lines 1681 and 1715 in the extracted source). The [PyTorch API reference](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html) documents reduced view tracking and version-counter work. This explains the hypothesis and does not guarantee serving gains or compatibility. Runtime source hashes, context activation checks and ordinary output checks must pass.

Two new serial 16-GPU jobs use the same accepted both-HPC-Ops, chunk4096, N54, MNNVL decode and dense FlashInfer decode configuration:

| Trial | Prefill DynamicGradMode | Decode DynamicGradMode |
|---|---|---|
| Explicit-default control 49 | no_grad | no_grad |
| Candidate 50 | no_grad | inference_mode |

Both workers include identical source-hash and context preflights; they differ only in the decode environment value. Ranked benchmark, request dataset, model precision, CUDA graph sizes, transport, output checks, synchronisation barriers and separate CPU/GPU post-score profile are unchanged. No model patch, quantisation change, request truncation or speculative decoding is introduced. Source schema support is not runtime compatibility proof.

Reserve at most 3072 SU for two 45-minute allocations; use a verified dependency chain and at most one running allocation. Recheck live own queue and ledger under the budget lock before submission. The current operating cap remains 51000 SU with a 13000-SU project buffer; reservations release only after ledger reconciliation. A third active slot is intentionally available for a different evidence-supported followup, not a blind duplicate.

Reject startup/context failures, payload drift, errors, latency failure or output regression. A single small difference comparable to baseline variation is not an established improvement. Repeat a practically useful candidate with a fresh matched control before promotion. If this option loses or offers no meaningful signal, close it and investigate communication kernel strategy or a smaller communicator reproduction without repeating the failed selector sweeps. Official 99%-reference accuracy remains unverified.

Evidence and sources accessed 19 October 2026: [latest matched results and profiler evidence](../research-followup-20261019-1720/RESULTS.md), `../research-followup-20261019-1720/host-runtime-source/`, and [PyTorch inference-mode design RFC](https://github.com/pytorch/rfcs/blob/master/RFC-0011-InferenceMode.md). FlashInfer [all-reduce strategy documentation](https://docs.flashinfer.ai/generated/flashinfer.comm.allreduce_fusion.html) was reviewed for a later hypothesis; forcing one-shot requires workspace-size verification and is not part of these jobs.
