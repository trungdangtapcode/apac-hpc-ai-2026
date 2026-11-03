# Investigation coverage and supporting history

The current presentation is 42 slides: AI main talk 1–16, hidden AI backup 17–34, and the unchanged HPC content at 35–42. The show hands off from AI slide 16 to HPC slide 35. This index tracks how the retained evidence supports the argument; it does not claim every historic run appears in the main talk.

## Current four-question argument

| Research question | Main route | Supporting route |
|---|---|---|
| How do we divide the fixed two-node, 16-H200 budget? | 1–4 | 17–19, 26 |
| What failed in one transfer path, and what did its repair establish? | 5–7 | 20–21 |
| Which service-level changes improve goodput under the latency rule? | 8–12 | 22–28, 30, 32 |
| Which conclusions survive repeats and cross-platform checks, and how is the official checkpoint handled? | 13–16 | 29, 31, 33–34 |

## Final 31 October measurements now represented

Nine H200 allocations were reviewed and are current in backup slide 34, the main cross-platform conclusion on slide 14, the talk scripts, evidence cards and panel Q&A. The four distinct H100-derived source ports on H200 were 27804/27806 (HPC-Ops prefill chunk settings) and 27828/27830 (phase-specific inference mode). Fresh explicit control 27826 is not counted as a candidate. Jobs 27777/27779/27781/27783 provide fresh control, FA3 decode and transferred full-recipe evidence. No result surpassed the incumbent by the team's prospective 1% gate, so the recipe remains unchanged.

The single held-out H100-to-H200 prediction remains in backup slide 33 and is clearly labelled one-point calibration, not conversion law. The main route presents direct H200 validation because it answers which choices actually transfer. Slide 16 now adds the full packaged-entry acceptance after the result-reader and gateway-readiness failures; backup 31 preserves that failure-to-repair chain.

## Prior question-led edition to current deck

| Prior slide | Current slide(s) |
|---|---|
| 1 | 1, 2 |
| 2 | 1 |
| 3 | 3 |
| 4 | 4 |
| 5 | 5 |
| 6 | 8 |
| 7 | 6, 7 |
| 8 | 32 |
| 9 | 9, 10 |
| 10 | 11 |
| 11 | 12 |
| 12 | 15, 22 |
| 13 | 15, 30 |
| 14 | 13 |
| 15 | 13, 29 |
| 16 | 33, 14 |
| 17 | 16 |
| 18 | 16, 31 |
| 19 | 2 |
| 20 | 16 |
| 21 | 17 |
| 22 | 18 |
| 23 | 19 |
| 24 | 6, 20 |
| 25 | 7, 21 |
| 26 | 22 |
| 27 | 23 |
| 28 | 24 |
| 29 | 25 |
| 30 | 26 |
| 31 | 27 |
| 32 | 15, 28 |

The source index retains 220 dated entries, provenance and prior mappings. See [feedback response](FEEDBACK_RESPONSE.md), [Q&A evidence](MOCK_QA_EVIDENCE.md) and [claim cards](EVIDENCE_CARDS.md). Historical jobs and failures remain in the reports and research archive; inclusion in a slide is not the audit's unit of completeness.


## Full-set answer-quality verification — 3 November 2026

The open question was whether the serving configuration retained the stock FP8 reference accuracy; job 28197 answered deployment and performance questions but not answer quality. The bounded local study ran the same pinned 12,032 MMLU-Pro questions against both deployments on 16 H200 GPUs, holding prompt preparation, generation settings and parsing fixed. Across 16 completed allocations, the stock reference scored 9,460 correct (78.623670%) and the candidate 9,452 (78.557181%), giving 99.915433% reference-score retention and passing the predeclared local 99% point gate. There were zero service errors, 101 invalid answers per role, and 1,484/1,468 length-capped outputs; all were retained. Paired outcomes were 9,018 both correct, 2,138 both wrong, 434 candidate-only correct and 442 reference-only correct, so “eight fewer” is a net difference across 876 disagreements. Computer science and philosophy retention were 97.971014% and 98.966408%; no category gate was declared. Independent raw-response replay reproduced the aggregate.

This is a complete local point comparison, not statistical equivalence, a causal kernel result or BTC certification. The study used 51.533333 allocated H200 GPU-hours including pilots (47.32 for the full study), not active compute time or money. The earlier N16 pilot remains a distinct failed point result at 98.076923%; the earlier partial snapshot remains historical. The local quality result does not change the exact serving performance result of 3,051.518173 good output tokens/s or its separate 98.636602% request-latency fraction. See [full results](../ai-quality-verification-20261103/FULL_RESULTS.md) and [methodology](../ai-quality-verification-20261103/METHODOLOGY.md).

## Packaged-entry acceptance and official evaluation workflow

After the 31 October cross-platform verification, the team retried the exact AI submission entry. Job 28194 failed before benchmarking because `/health` returned 200 before asynchronous model registration, followed by `/v1/models` 503. The source-bound readiness change waited for the Qwen model to appear and verified workers remained alive. It passed five local HTTP/liveness fixtures and the exact setup. Job 28197 then passed the full portable entry in 611 seconds. This closes the “no post-reader-fix full GPU replay” gap. It is not a new configuration or a matched speed comparison. Answer quality was later measured in the separate 3 November full-set study above. See [acceptance review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/REVIEW.md), [job status and receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/STATUS.md), and [quality clarification](/home/apacsc42/workspace/notes/ai-quality-threshold-clarification-20261102.md).
