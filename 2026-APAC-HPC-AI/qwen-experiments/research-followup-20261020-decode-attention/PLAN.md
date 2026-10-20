# Re-evaluate dense decode attention after the MoE/load changes

## Hypothesis and why this is a new comparison

The H100 both-HPC-Ops incumbent now runs at N54 and repeatedly scores around 2424–2431 good output tokens/s. Phase-specific inference mode showed no useful established gain, and the graph32 collective screen rejects forced one-shot. The actual decoder profile still contains material FlashInfer paged-attention work. These are descriptive kernel sums, not a predicted attention-only speedup.

Compare **FlashInfer versus FA3 only in decode**, keeping both-phase HPC-Ops and N54. Earlier attention results were measured on a different runner/load pipeline; they do not establish the best decode attention implementation after those changes. This is a phase/runner interaction test, not an unchanged retry of dense FlashInfer prefill (which already lost and remains closed). A native supported alternative merits one matched pair, not a broad backend sweep.

The exact pinned image registry explicitly registers `fa3`; the same image already executes FA3 for prefill. [SGLang's primary documentation](https://docs.sglang.io/docs/advanced_features/attention_backend), checked 20 October 2026, lists dense FlashInfer and FA3 and says backend choice depends on model/hardware/use case. Current docs are not runtime compatibility proof: actual resolved arguments, GPU kernels and output gates still decide this experiment. No new version or image is installed.

## Frozen pair and gates

| Trial | Prefill | Decode MoE | Decode attention | Load |
|---|---|---|---|---:|
| Control 55 | HPC-Ops, chunk 4096 | HPC-Ops | FlashInfer | 54 |
| Candidate 56 | Identical | Identical | FA3 | 54 |

One worker argument differs. Retain 16 H100, MNNVL fusion/AUTO strategy/PDL, exact decode graphs 1–64, native checkpoint precision, BF16 KV, no speculation, request-scoped NIXL transport, explicit no_grad mode, full closed-loop 4000/200 and 60/120/30 protocol, raw errors in denominator and all short/12-long checks. Both have the same post-score CPU/GPU diagnostic protocol. No request or numerical work is skipped. Do not combine an unproved PDL setting with FA3.

Compare at the same N against the fresh control. Require sealed payload, full raw protocol, intended runtime/rank/kernel evidence, error/joint-latency/output gates. Keep a measured SLA failure separate from invalid evidence. A useful gain requires an independent matched repeat before promotion. Close this candidate on no useful signal or correctness failure; no load increase follows automatically. Local checks do not establish official ≥99%-reference accuracy.

## Resource bound

Reserve 3072 SU maximum for two 45-minute 16-GPU allocations, within the unchanged 51000-SU operating cap and 13000-SU buffer. Retain unbilled microbenchmark reservations and reconcile the actual ledger first. At most three active PBS jobs and one running allocation: if PDL pilot 222026 is still active, control follows it, then candidate follows control. If it is already terminal, submit control directly with the same verified serial model pair. No uncertainty retry. H200's four existing positions remain unchanged; its measurements are not pooled with H100.
