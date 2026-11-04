# Tokenizer, prefill attention and EAGLE losses

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Do tokenizer, prefill-attention, or shallow speculative-decoding changes improve the H200 incumbent?

## Why investigate this?

The team screened several distinct ideas against the current H200 context: dynamic tokenization may reduce client overhead, an alternative attention backend may change prefill computation, and shallow EAGLE3 speculation may reduce sequential decode work. Each mechanism affects a different stage, so results should not be combined into one general backend claim.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Tokenization | Existing tokenizer path. | Dynamic tokenizer variants. |
| Prefill attention | Incumbent attention backend. | FlashInfer prefill. |
| Decode generation | Ordinary decode. | Shallow EAGLE3 draft/verification path. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| H200 dynamic tokenizer | +0.192% / +0.270%; not promoted. |
| FlashInfer prefill | −6.385%. |
| Shallow EAGLE3 | −2.080%. |

## What did we learn?

- Small tokenizer differences were below the useful-gain bar.
- FlashInfer prefill and shallow speculation reduced goodput in these tests.

## Decision

Keep the incumbent and close these tested branches.

## Limits and remaining questions

- Percentages apply to the cited matched tests and versions.
- A loss in one implementation does not reject the technology family universally.

## Sources

- [ai-final-report-20261030/REPORT.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-final-report-20261030/REPORT.md)
- [h200-native-chunk-review-20261028/REVIEW.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h200-native-chunk-review-20261028/REVIEW.md)
