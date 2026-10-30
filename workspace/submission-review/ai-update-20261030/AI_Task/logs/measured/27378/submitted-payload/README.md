# Full cold-prefill cache intervention and fresh control

Prepared 29 October 2026, Vietnam time (UTC+7), before either result. Test whether removing prefill prefix-tree bookkeeping helps the unchanged cold workload. Benefit is uncertain: extra recomputation of formatting prefixes or changed queue behavior may offset savings.

S103 retains default RadixCache on both prefills. S104 adds --disable-radix-cache to both prefills and requires native ChunkCache on every prefill rank. Decode remains cap 256/polling 1, native disable_radix_cache=True and ChunkCache in both. Do not combine the pending cap 64 intervention with this candidate. A fresh control addresses intervening cluster activity since 27270.

Keep the images, FP8 target/BF16 activation and KV, page size 1, P4+P4 / D8 TP8 EP8, DeepGEMM chunk 8192/breakable prefill, HPC-Ops/FlashInfer/MNNVL decode, all graph batches 1..64, tokenizer batching off and requested cold 4000/200 seed 2026/full 60/120/30. Score remains exported Goodput × 200. Physical KV buffers, their exact unchanged geometry validator, both semantic P/D routes and local output checks remain. The flag disabling physical prefill KV stays false.

Pin the cache factory, builder and release lifecycle source. Require exact per-role resolved flags and native cache classes on all ranks with no fallback/wrapping. The independent performance checker replays runtime raw logs. Meaningful CPU fixtures reject stale flags, wrong classes, missing ranks, physical-KV disabling and invalid graph/NIXL evidence; they are not GPU proof.

Admit exactly two full jobs under the Slurm lock and own cap 5, preserving existing jobs/positions. Each uses 16 H200/two nodes/17 minutes, maximum 4.533334 GPU-hours, no PBS SU. Obtain definite receipts and frozen hashes. No dependencies or background service.

Accept only complete terminal local passes: joint TTFT ≤ 3000 ms and request-mean ITL ≤ 20 ms for at least 90% of all requests, zero errors/cancellations, smoke 7/8 without regression, retrieval 12/12 and all source/runtime/KV/semantic checks. Inspect tails, queues/inflight/KV, sampled GPU/CPU/power/clocks/VRAM and cleanup. Require >1% useful gain against the fresh control with acceptable tails before independent confirmation; otherwise close unchanged. Official accuracy remains unknown. HPC, published submission, VPN and background Codex policy are unchanged.
