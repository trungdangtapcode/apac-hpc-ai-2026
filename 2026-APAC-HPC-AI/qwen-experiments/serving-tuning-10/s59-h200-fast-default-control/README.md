# S59 fast-default target-only control

This is the control arm for an unranked matched fast-default performance exploration. It derives from the helper-fixed S57 control and changes only the serving mode and common prefill request cap required by the new pair. The deterministic-inference flag is removed. The pinned runtime's resolved defaults must show `enable_deterministic_inference=False`, `sampling_backend=flashinfer`, and `disable_custom_all_reduce=False`; decode resolves FlashInfer allreduce fusion to `mnnvl`, while prefill resolves it to `auto`.

The common shape is P8-TP4 with two prefill workers capped at 64 running requests each, D8-TP8-EP8 capped at 256, BF16 model/KV allocations, NIXL transfer, chunked prefill 8192, eager prefill graphs, and decode graphs 1 through 64. The fixed screen is N=64, 20-second warmup, 40-second profile, 30-second grace, fixed 4000 input and 200 output tokens, seed 2026. The performance gate retains the strict 90% good-request threshold, zero request errors/cancellations, 7/8 smoke floor with no known regression, both P/D semantic paths, and all 12 retrieval checks.

This is unranked exploratory evidence. Quality is UNKNOWN, and no exact-token, official-accuracy, or speedup claim is made. No job was submitted in preparation; root review and submission remain required.
