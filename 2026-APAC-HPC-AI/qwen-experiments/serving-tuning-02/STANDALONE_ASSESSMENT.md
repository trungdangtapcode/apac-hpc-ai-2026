# Standalone N52 assessment — 14 October 2026

Same checkpoint, sixteen H200, TP4 prefill → TP8/EP8 decode, BF16 KV and the unchanged 60/120/30 protocol. Each deployment begins directly at N52.

| Job | Candidate | Good tokens/s | SLA | Versus control |
|---|---|---:|---:|---:|
| 23128 | s2-control-n52 | 1977.08 | 97.14% | +0.00% |
| 23129 | s2-chunk4096-n52 | 2033.03 | 97.39% | +2.83% |
| 23130 | s2-chunk4096-dense-n52 | 2078.96 | 97.43% | +5.15% |
| 23131 | s2-chunk16384-n52 | 1741.20 | 90.92% | -11.93% |

Chunk 4096 plus dense decode graphs was selected for a repeat (+5.15% in the first standalone measurement). Chunk 16384 lowers goodput and approaches the 90% latency gate; it was not selected for a repeat. All four points have zero benchmark errors and cancellations.

## Completed repeats and backend pilots

| Job | Candidate | Good tokens/s | SLA |
|---|---|---:|---:|
| 23266 | Chunk 4096 + dense graphs, repeat | 2079.18 | 97.43% |
| 23267 | Chunk 4096, repeat | 2032.13 | 97.39% |
| 23264 | Matched DeepGEMM control | 2018.01 | 97.37% |
| 23265 | FP8 KV | 1996.26 | 97.33% |
| 23272 | DeepEP low latency | 1957.15 | 96.35% |

All five jobs completed full measurements with zero benchmark errors/cancellations.
The scheduling winner measured 2078.96 and 2079.18 in independent deployments;
their mean is 2079.07, with a 0.0104% observed range relative to that mean.
This supports reproducibility in these two runs, not a universal noise estimate.
Chunk-only also repeated closely (2033.03 → 2032.13).
FP8 KV was slower than its BF16 chunk-only control, and DeepEP was slower than
its matched DeepGEMM control. Those backend changes are not selected for the next
load search. Runtime logs confirm FP8 E4M3 KV on both roles in job 23265;
job 23272 retains BF16 KV and selects the DeepGEMM/DeepEP path.

[Wave 3](../serving-tuning-03/PLAN.md) now refines concurrency on the repeated
BF16 scheduling winner. [Completion data](wave2-completion-2026-10-14.json)
retains the full measured rows and raw export paths.

The 2140.10 point from the previous wave followed an N48 measurement. Its larger gain has not reproduced in this standalone wave; it must not be described as a stable result.

Every candidate scored 7/8 on the hand-written output suite, failing only reverse-string instruction following. Unmodified monolithic deployments also failed that case in all twelve attempts; all other 120 responses passed, including 36 long-context retrieval checks. This supports continuing research without relabelling the incorrect answer or claiming the official 99% accuracy gate.

The controller now compares the unchanged output cases with that independent baseline. Additional failures or transport errors block follow-ups. Backend pilots and scheduling repeats remain experiments; the submission package is not promoted automatically.

[Live results](../SERVING_TUNING_RESULTS.md) · [Diagnostic](OUTPUT_DIAGNOSTIC.md) · [Raw comparison](standalone-assessment-2026-10-14.json)
