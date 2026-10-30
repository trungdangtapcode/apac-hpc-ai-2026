# Presentation organised around technical reasoning

**Superseded:** see [the current engineering investigation edition](ai-investigation-presentation-20261031.md) for the main 16/hidden-backup 16 route and current files. Older counts, mappings and hashes below are historical.

Updated 30 October 2026, Vietnam time (UTC+7). The owner explained that the panel assesses how the team reasoned about the problem, rather than only the final score. They supplied a seven-step reasoning flow and four research questions. Reporting work follows that direction; research and new job submissions remain stopped.

## Current presentation

The [PowerPoint](../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx) and [review PDF](../submission-review/ai-reasoning-update-20261030/TripleU_APAC2026_Presentation.pdf) contain 20 main AI slides, 12 AI backups and the unchanged eight HPC slides. They retain the existing theme, gradients and distinct background photographs. Every AI slide names its hardware and research role. Timeline and configuration counts now support decisions in the backup material instead of organising the main talk.

| Research question | Main slides | Argument |
|---|---|---|
| How should prefill and decode be distributed across 16 H200 GPUs? | 2–5 | Fixed constraints, eligible layouts, measured alternatives, selected split and request-level validity |
| What limits the selected deployment? | 6–7 | Profiling and source/runtime observations first; distinguish suspected limits from a proven dominant cause |
| Which interventions improve goodput within the latency rules? | 8–13 | Hypothesis, comparable control, complete measurement, tradeoff and keep/reject decision |
| Are improvements reproducible and robust? | 14–18 | Repeats, runtime drift, held-out cross-platform check, quality and actual packaged replay limits |

Slide 1 frames the questions; slides 19–20 state supported decisions and proposed validation. The owner's seven-step chain is problem/constraints → baseline/observation → bottleneck analysis → prioritisation/hypothesis → intervention/measurement → causal assessment → decision/next iteration. The chain is used inside the questions, not as an unsupported assertion that every suspected bottleneck was verified.

## KV-transfer correction

The old descriptor-count headline did not adequately explain the symptom, affected component, prioritisation or end-to-end evidence. The [source audit](../reports/ai-final-report-20261030/KV_TRANSFER_REASONING_AUDIT.md) now traces them. Historical H200 job 22271 loaded its workers but timed out in P/D warmup after 360 seconds before scoring. The request-scoped descriptor patch targeted visible whole-pool setup work; bandwidth, layout and scheduling alternatives were not experimentally excluded.

CPU range equivalence passes 720 tested cases; the 403.8-million whole-pool entries/rank versus 188 ranges/request are different scopes, not a speed ratio. Patched job 22294 completed real P/D warmup in 0.68–0.70 seconds/request and a full N32 benchmark at 1422.96 good output tokens/s, 95.87% joint latency success and zero errors/cancellations. No successful unpatched scored control or isolated descriptor timer quantifies the patch's independent throughput effect. Main slides 5/7 and backups 24/25 preserve those boundaries. This recovery topology is not the selected two-TP4-prefill layout.

## Learning material and preservation

Both [Vietnamese](../reports/ai-final-report-20261030/TRANSCRIPT_VI.md) and [English](../reports/ai-final-report-20261030/TRANSCRIPT_EN.md) transcripts are remapped to the new slide order, with hardware labels, short spoken briefs, terms, numerical interpretation and evidence limits. Their [Vietnamese PDF](../reports/ai-final-report-20261030/TRANSCRIPT_VI.pdf) and [English PDF](../reports/ai-final-report-20261030/TRANSCRIPT_EN.pdf) are regenerated. Current page counts are recorded by PDF validation; the older 89-page editions are historical. Use the [18-minute plan](../reports/ai-final-report-20261030/PRESENTATION_PLAN.md), [evidence cards](../reports/ai-final-report-20261030/EVIDENCE_CARDS.md) and [panel Q&A](../reports/ai-final-report-20261030/PANEL_QA.md).

Publication changes the presentation and independently regenerated global manifests in the live folder and ZIP. AI serving code, metrics and all other package members retain their bytes. All 68 HPC presentation dependency parts, eight HPC slide/PDF pages, 277 current HPC folder files/modes and 265 ZIP HPC files/member metadata are preserved. Their 13 preexisting differing paths remain separate; no unpublished HPC work is silently packaged. [Publication validation](../submission-review/ai-reasoning-update-20261030/publication-validation.json).

Current PPTX SHA-256: 171fa7ce896ecbfc3708c1d15e5b603cb4bf80ee46a9c3a9f59af1ae0a1995d8. Current ZIP SHA-256: cb2400c1def737405a77ce22f56acb05acec7098097b9a13b70cc6f99265a986. No organiser upload or new scientific measurement occurred. Earlier deck/ZIP versions are backed up before publication. Safe source changes, rendered documents and recovery metadata are explicitly captured and committed; Git does not upload the sibling store's large object bytes.
