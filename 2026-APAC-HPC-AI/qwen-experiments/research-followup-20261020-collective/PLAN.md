# Screen the MNNVL strategy before another full-model experiment

## Question and evidence

The phase-specific inference-mode trials passed but produced no useful established H100 gain: decode-only +0.2596%, prefill-only −0.0114% versus their matched control. Close that tested option. Actual H100 profiles retain substantial MNNVL all-reduce/RMSNorm and MoE GPU work, so investigate an isolated GPU implementation choice rather than repeatedly loading 235B weights for small host-setting changes. [Completed comparison](../research-followup-20261020-0028/H100_RESULTS.md).

The exact pinned FlashInfer source uses AUTO one-shot only when tokens × hidden × TP × element size ≤1048576 bytes. At hidden 4096, TP8, BF16 this is at most 16 tokens. Observed decode batches often exceed that. A one-shot strategy might reduce latency at the actual 32–64 shapes, or the current two-shot bandwidth tradeoff may already be better. This is a hypothesis, not a predicted model speedup.

## Bounded experiment

One node, **8 H100 GPUs, at most 10 minutes**, maximum **170.667 SU**, no model weights loaded. Use the pinned image and verify the exact collective source hashes at runtime. Screen token counts 8/16/32/48/54/64, hidden 4096, TP8, BF16, fused all-reduce + residual + RMSNorm, PDL enabled. Compare AUTO, forced one-shot and forced two-shot. Run two order-reversed rounds, five timed samples per point,20 CUDA-graph replays per sample; save every rank's samples and separate 54-token traces. Gloo handles rendezvous only. Private writable runtime caches prevent inherited cache-permission failures.

Allocate workspace with `force_oneshot_support=True`, covering the largest forced shape, and check strategy-specific sufficiency before each case. Check fused residual and normalised output against a seeded CPU BF16 reference, retain max errors and assert original inputs/residual unchanged. The local tolerance 0.02 absolute/relative is a kernel sanity gate, not bitwise equivalence or official accuracy. Inspect all eight ranks, completeness, workload shape, hardware and actual trace evidence before trusting timing. CUDA-event durations can include graph-dispatch gaps; they are not isolated kernel-only critical-path shares.

The official full-model scored benchmark is not changed or replaced by this microbenchmark. Do not report its microseconds as model tokens/s. If one-shot shows a useful consistent result across ranks and rounds, prepare a narrowly scoped decode-only model candidate plus matched control, with workspace capacity and full output/latency gates. If no useful result, close forced strategy tuning rather than extrapolating a speedup. Any model-level improvement needs its own repetition and official accuracy remains separate.

## Credit and source constraints

Reserve under the existing 51000-SU cap and 13000-SU buffer after reconciling prior jobs. At most three active PBS jobs and one running GPU allocation; this pilot requests eight GPUs only. No new campaign budget, authentication, model patch, precision change, slides or AI schedule. Preserve the source, definite qsub receipt, raw traces and failures; do not retry an uncertain submission.

Primary references, accessed 20 October 2026: [FlashInfer allreduce_fusion](https://docs.flashinfer.ai/generated/flashinfer.comm.allreduce_fusion.html), [workspace construction](https://docs.flashinfer.ai/generated/flashinfer.comm.create_allreduce_fusion_workspace.html). Current web docs may differ from the installed image; extracted hashed source and runtime signature/hash checks take precedence. Exact source: `../research-followup-20261019-1720/comm-runtime-source/` and `../research-followup-20261020-0028/collective-source/`. The pinned cache environment source is retained here. This does not reopen the corrected NCCL symbol-name issue.
