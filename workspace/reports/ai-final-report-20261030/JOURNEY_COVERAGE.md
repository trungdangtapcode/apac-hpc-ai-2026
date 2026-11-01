# Investigation coverage and supporting history

The current presentation is 42 slides: AI main talk 1–16, hidden AI backup 17–34, and the unchanged HPC content at 35–42. The show hands off from AI slide 16 to HPC slide 35. This index tracks how the retained evidence supports the argument; it does not claim every historic run appears in the main talk.

## Current four-question argument

| Research question | Main route | Supporting route |
|---|---|---|
| How do we divide the fixed two-node, 16-H200 budget? | 1–4 | 17–19, 26 |
| What failed in one transfer path, and what did its repair establish? | 5–7 | 20–21 |
| Which service-level changes improve goodput under the latency rule? | 8–12 | 22–28, 30, 32 |
| Which conclusions survive repeats, cross-platform checks and known quality limits? | 13–16 | 29, 31, 33–34 |

## Final 31 October measurements now represented

Nine H200 allocations were reviewed and are current in backup slide 34, the main cross-platform conclusion on slide 14, the talk scripts, evidence cards and panel Q&A. The four distinct H100-derived source ports on H200 were 27804/27806 (HPC-Ops prefill chunk settings) and 27828/27830 (phase-specific inference mode). Fresh explicit control 27826 is not counted as a candidate. Jobs 27777/27779/27781/27783 provide fresh control, FA3 decode and transferred full-recipe evidence. No result surpassed the incumbent by the team's prospective 1% gate, so the recipe remains unchanged.

The single held-out H100-to-H200 prediction remains in backup slide 33 and is clearly labelled one-point calibration, not conversion law. The main route presents direct H200 validation because it answers which choices actually transfer.

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
