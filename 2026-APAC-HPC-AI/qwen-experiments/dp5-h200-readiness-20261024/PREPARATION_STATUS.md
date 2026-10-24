# D5 H200 readiness preparation status

State: paused after source feasibility review. This directory contains source evidence and CPU-side inspection material only. It is not a runnable or submission-ready payload.

No GPU allocation, Slurm submission, queue change, endpoint request, model preflight, or performance/correctness run was performed for D5.

The next stage is blocked on root review of the native physical-replica GPU primitive result from `hpc-ops-replica-r2`. Before constructing any candidate payload, the remaining source proof must establish the actual per-rank physical expert mapping during model load and validate the runtime CLI/model support contract. Any runtime observer whose API cannot be verified from source must remain a fail-closed missing proof; no runtime evidence may be fabricated.

The intended configuration remains an ordinary target-model D5 feasibility candidate: Qwen 235B FP8 checkpoint, explicit BF16 runtime dtype, TP=5, DP=5 with DP attention, EP=5, one MoE TP shard, and two redundant experts (130 physical experts / 5 ranks = 26 each). This is a proposed configuration, not a validated runnable payload. D mode, eager mode, small decode graph, private HOME, pinned image, and a five-GPU allocation are planning constraints only.

Resume only after root has reviewed the prerequisite primitive result and the source-level expert mapping and CLI constraints are documented. Preserve this source-only state until those gates are met.
