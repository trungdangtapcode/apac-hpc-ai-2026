# Isolated H100 collective pilot 222022

## Submission and evidence

Submitted one 8-H100/10-minute allocation after all preceding model jobs were terminal and reconciled. Maximum reservation 170.667 SU, internal headroom 16814.330 SU at submission. Definite qsub receipt and post-submit resource request are retained. Job finished exit 0 after 71 seconds; estimated allocation charge 20.196 SU, not a released reservation until the published ledger matches it. No model was loaded.

All eight ranks completed 36 shape/strategy/repetition points each (288 total), all local numerical/input-integrity checks pass, and 24 nonempty rank/strategy traces are sealed. The full result is 222022-micro-review.json; source/config/metadata and original per-rank samples are retained. Local BF16 tolerance is not bitwise or official model accuracy.

## Observed timings and limitations

Values are the worst rank's median CUDA-event microseconds per graph replay; each graph contains one collective. They include graph-dispatch gaps and cross-rank waiting.

| Tokens | Reversed-order round | AUTO (us) | One-shot (us) | Two-shot (us) |
|---|---:|---:|---:|---:|
| 16 | 0 | 25.011 | 20.267 | 27.229 |
| 16 | 1 | 28.536 | 32.376 | 33.323 |
| 32 | 0 | 24.142 | 31.302 | 22.306 |
| 32 | 1 | 31.390 | 28.125 | 31.654 |
| 48 | 0 | 29.275 | 29.514 | 33.224 |
| 48 | 1 | 28.549 | 25.179 | 28.998 |
| 54 | 0 | 25.931 | 40.334 | 27.795 |
| 54 | 1 | 35.165 | 38.792 | 26.912 |
| 64 | 0 | 27.070 | 36.701 | 25.219 |
| 64 | 1 | 25.350 | 33.517 | 22.109 |

At 54/64 tokens, one-shot does not offer a useful positive signal. However, the exact-same algorithm cases (AUTO versus forced one-shot at 8/16, AUTO versus forced two-shot at larger shapes) also vary materially across order/ranks. Do not turn this into a clean isolated kernel-latency or model-speedup claim. The observed span includes CPU launch cadence because one collective is replayed per graph.

## Next decision

Do not prepare an expensive full-model one-shot patch/control on this evidence. Refine only the microbenchmark method: capture 32 identical collectives inside each graph and time 10 replays, retaining per-graph and per-collective units, both order-reversed rounds, the same shapes/precision/numerical gates and rank completeness. This amortises CPU graph-launch gaps; it still does not reproduce the model's full compute/communication overlap. If no useful consistent gain survives this screen, close one-shot forcing and move to another demonstrated cost.

No new model peak, official accuracy, slides, authentication or AI schedule is implied by this pilot. Raw failures and losing/ambiguous observations remain evidence.
