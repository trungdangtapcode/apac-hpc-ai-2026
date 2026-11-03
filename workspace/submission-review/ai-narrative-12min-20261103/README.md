# AI presentation: a 12–13 minute engineering investigation

Published locally **2026-11-03T22:45:41.355234+07:00, Vietnam time (UTC+7)**. The owner requested a stronger research narrative while preserving the existing slides' design and a **12–13 minute AI speaking allocation**. This edition keeps sixteen main AI slides, eighteen hidden AI backups and the latest eight HPC slides at their original positions.

## The audience should understand three decisions

1. **How did we obtain a usable phase-split deployment?** Start with the fixed GPU budget and distinct prompt/generation work. A particular heterogeneous-TP branch loaded its workers but could not finish warmup. Explain KV as reusable attention state and NIXL as the existing transfer library. Source-visible whole-pool address metadata suggested a bounded request-scoped change. CPU range checks and a real patched run establish feasibility; they do not establish an isolated descriptor speedup.
2. **Why did we choose this serving recipe?** A decode loss did not settle the prefill question, because the phases present different work shapes. When prefill/chunk changed, the old decode decision became worth rechecking. Explain matched control, prediction/counterprediction, result, latency tradeoff and repeat. Raise concurrency only while full comparisons support it; retain N64 and reject the unsupported N68 promotion. Where an original motive was not retained, the phase explanation is explicitly retrospective.
3. **Why trust the retained recipe enough to report it?** Distinguish the request-level symptom from its unknown cause. Test promising H100 ideas directly on H200. Reject proxy-only improvements. Check the delivered entry and answer quality separately, then close with the resulting engineering decisions.

## What changed on the actual slides

- Main 3 replaces the historical score list and incorrect topology-09/1666.01 pairing with the prefill/decode tradeoff under a two-node resource budget.
- Main 5 explains the KV/NIXL path before discussing the failure. Main 6 shows the team's metadata change and correctness invariant. Main 7 reports successful patched serving without turning the earlier timeout into a speedup.
- Main 8 retains profile limits and phase-specific reasoning without the percentage chart. Main 9 keeps the controlled experiment. Main 10 retains the few measurements needed to explain the throughput/latency tradeoff.
- Main 11 retains the N64 selection and repeated evidence with rounded numbers. Main 13 foregrounds the portable entry's complete execution, rather than reading three historical scores.
- Main 14 correctly says no tested port cleared the prospective 1% usefulness gate, including the slightly positive phase-mode points; it does not say all candidates scored lower.
- Main 16 is **The retained recipe survives performance and quality checks**. Two headline observations support three lessons: select for phase/hardware, keep full repeated gains, and validate deployment/quality separately.
- Detailed full-set accuracy counts are in backup 19. Original historical milestones remain retained in the research archive and the complete run-lineage viewer.

The original theme, backgrounds, main slide order and total deck size are retained. No new measurement or scientific result was created for the talk.

## Speak for 12:30; study separately

[English short script](../../reports/ai-final-report-20261030/TALK_SCRIPT_EN.md) and [Vietnamese short script](../../reports/ai-final-report-20261030/TALK_SCRIPT_VI.md) provide the spoken narrative. The main English body has **1358 words**, with a per-slide target totaling **750 seconds (12:30)**. At 120 words/minute the speech alone is about 679 seconds; the target reserves the remainder for figures, pauses and transitions. This is an estimate, not an actual timed mock.

The [contribution and story guide](../../reports/ai-narrative-audit-20261103/CONTRIBUTIONS_AND_STORY.md) explains the reasoning for a beginner. The longer [EN](../../reports/ai-final-report-20261030/TRANSCRIPT_EN.md) and [VI](../../reports/ai-final-report-20261030/TRANSCRIPT_VI.md) visual guides cover **AI slides 1–34 only**, with a quick brief before each purpose, terms, units, color interpretation and detailed reasoning. They intentionally no longer reproduce stale HPC explanations after that worker's later slide update. The combined deck still includes current HPC 35–42; [its presenter notes](../hpc-iris-slides-20261103/PRESENTER_NOTES.md) remain with the HPC owner. Original HPC transcript JSON records are preserved.

The public combined slot remains 15–20 minutes. The owner's 12–13 minute AI target leaves roughly 7–8 minutes within a 20-minute slot; a shorter assigned total requires the team to agree a cut rather than silently consume HPC time.

## Evidence and preserved surfaces

Accepted serving run 28197 remains **3051.518173 good output tokens/s**, **1881/1907 joint SLA passes**, zero errors. The complete local accuracy result remains **9452/9460 =99.915433%** of measured stock-reference accuracy over 12,032 identical questions per role. The local pass is not BTC certification. NIXL, SGLang, DeepGEMM, FlashInfer, HPC-Ops and MNNVL are reused projects; the team's claim is bounded implementation/integration and evidence-backed engineering, not invention of these libraries.

The ZIP still contains lossless full quality answers, the pinned scorer and a CPU replay. That replay reproduced all 24,064 response records and the exact score. All executable serving/client/reader files remain the accepted R2 bytes; documentary README/checksum changes do not require another GPU run.

The snapshot uses the current HPC owner's published 3 November PDF, not the older AI edition's HPC pages. Merge and publication verify **68 HPC dependency parts**, eight pixel-identical HPC PDF pages, 277 folder files/modes and 265 ZIP members/metadata, preserving 13 prior folder/ZIP differences. No HPC scientific payload or result was changed.

PPTX SHA-256: `0a5f347c8b276a60f87579315363c4d774226c7f3b7f09db546ee2117fb7f9af`.
ZIP SHA-256: `305d5f5e14e47704f6f63e87fe2632532a78273d0f41c7c95df2a63f080a088f`; size 185,183,256 bytes.

## Build and checks

Use the retained pinned presentation environment and set `TRIPLEU_REVIEW_STAGE=submission-review/ai-narrative-12min-20261103`, `TRIPLEU_PART_PREFIX=ain03_`. Preserve the original `inputs/` snapshot. Update narrative transcript source; build narrative slides; reuse the guarded acceptance merge; extract narrative source; build AI-only guides and PDFs; stage the quality evidence/package; replay packaged quality with a new output path; validate content, package, quality and stage; publish the reviewed stage; validate with `--published`.

The short spoken scripts are intentionally independently edited prose. Their extra reasoning need not be read verbatim from speaker notes. A source rebuild requires the exact captured input/version, not an assumption that the latest mutable teaching JSON reproduces an older deck hash.

Visual previews and PDF pages were inspected. No actual Office/projector test, human mock or organiser upload is claimed. Git/object capture and a separately verified off-host final-asset copy preserve the reviewable result.

## Off-host preservation

The [private asset receipt](offhost/README.md) verifies the slide and guide files downloaded from GitHub. The final ZIP has a separately uploaded and downloaded versioned asset, `TripleU-narrative-final-v2.zip`, verified by hash and byte length after the Q&A-title synchronisation. Earlier assets remain retained.
