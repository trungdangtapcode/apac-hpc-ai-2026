# H100 phase-specific inference-mode review

## Hypothesis and actual treatment

CPU/GPU traces motivated reducing supported DynamicGradMode view/version tracking overhead. The matched default control and two phase candidates retain fixed N54, chunk4096, both-phase HPC-Ops, MNNVL and dense FlashInfer decode, native checkpoint precision, BF16 KV, unchanged scored client and output checks. Frozen sources and the logged DynamicGradMode context preflights match each intended phase; resolved ServerArgs differ only in random seeds from the accepted reference.

All three pass full local sealed-payload/raw-protocol/error/joint-latency/short-output/12-long/runtime gates. Official full-set accuracy remains unverified.

| Job | Trial | Good output tokens/s | Joint good requests | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|
| 221923 | Explicit-default control | 2424.365 | 98.552% | 719.384 | 18.146 |
| 221924 | Decode-only inference mode | 2430.657 | 98.620% | 710.493 | 18.158 |
| 221966 | Prefill-only inference mode | 2424.089 | 98.618% | 717.194 | 18.165 |

## Assessment and next decision

Decode-only is **0.2596%** above its matched control; prefill-only is **-0.0114%**. These single small differences do not establish a useful improvement. Neither beats the retained individual H100 peak 221590 = 2430.891. Close the tested inference-mode option rather than repeatedly funding full-model deployments or assuming phase gains combine. This is not a statistical proof of zero effect.

The decoder's profile has substantial actual GPU collective and MoE cost. Next investigate a lower-cost, isolated MNNVL all-reduce-plus-residual/RMSNorm strategy benchmark on eight H100 GPUs. The pinned FlashInfer AUTO selector switches to two-shot above 16 tokens at hidden 4096, TP8 and BF16, whereas observed decode batches are often 32–64. A one-shot variant may or may not help. Verify correctly sized workspace, numerical checks and CUDA-graph timing before considering any full-model patch. No model speedup or accuracy follows from a microbenchmark.

## Credit and preservation

Published Used 34015.003 SU, Balance 29984.997 SU, In Doubt signed -0.000 (numerically zero), as of 20/10/2026-08:20:01 SGT. Three charges total 1410.275 SU and reconcile the Used delta; release the old 4608-SU maximum reservations only after that reconciliation. Internal headroom before new work is 16984.997 SU under unchanged 51000-SU cap and 13000-SU buffer. A parser initially rejected signed zero; it was corrected before any ledger mutation and the initial script is retained. Bounds are not actual charges.

Collector receipts, immutable remote snapshots, per-job reviews, gates, exact raw responses and frozen payloads are preserved. No authentication, slides, model promotion or background Codex changes.
