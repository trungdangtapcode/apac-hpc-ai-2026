# Current submission readiness — 2 November 2026

Updated **2026-11-02T08:57:13.375119+07:00, Vietnam time (UTC+7)**. **The AI portable entry now has one complete reviewed GPU acceptance pass, job 28197; its tested readiness fix is in the current submission ZIP.** The prior [audit before GPU acceptance](README-before-acceptance.md) is retained as history. Its recommended replay and known readiness-defect gaps are now closed, not outstanding actions.

## Verified current result and materials

28197: COMPLETED 0:0 in 611 seconds, 16 H200/two nodes/N64, 3051.518173303673 good output tokens/s. Joint SLA: 1881/1907 (98.63660199265862%); 26 TTFT, zero mean-ITL misses, zero errors/cancellations. Both semantic P/D routes, exact official AIPerf protocol, corrected result readers, independently replayed raw performance gate and cleanup pass. This is a same-recipe acceptance run, not a matched optimisation speedup. Historical failures remain failed; official quality is a separate question. [Result analysis](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/RESULTS.md).

[Current release](../../submission-review/ai-acceptance-update-20261102/README.md): package validation 635 checks; publication cross-artifact validation 452 checks. The deck/guide/PDF sources match exactly. Main 13 and 16 and backup 31 incorporate the final acceptance with reasoning, failure diagnosis and claim limits. The 42-slide deck retains 16 main AI, 18 hidden AI and eight HPC; main PDF 24 pages, full PDF 42; EN/VI learning PDF 111/104 pages. English report and speaking script inside the ZIP are current.

The deployed script matches the tested R2 runtime bytes; README and checksum changes are documentary. The single entry preserves native model precision, disaggregated two-node topology, N64 and all required client parameters. [Rule audit](AI_RULE_CHECK.md), [pinned official sources](official-rules/source.json), [offline audit](OFFLINE_PREFLIGHT.json). Upstream b4df52907f5bbb9152ef6ae902c925fc79d54417 remains the verified rules revision. Same-computation text patches are permitted under Q1; no mandatory unpatched-Basic rule was invented.

All 68 HPC PowerPoint parts, eight HPC slide images, 277 folder files/modes and 265 ZIP files/member metadata remain unchanged, including 13 existing folder/ZIP differences. This is preservation, not scientific approval of the other worker's HPC results. Do not rebuild the ZIP blindly from the divergent folder.

## Still requires the responsible owners

1. **Official quality and rebuild:** UNKNOWN pending organiser full-set evaluation against its own FP8 reference at ≥99%. Local SLA and two semantic checks are not that evaluation; no fresh smoke-8/retrieval-12 suite ran in 28197. Pending organiser quality is not a published Basic pre-upload prohibition, and does not guarantee acceptance.
2. **HPC handoff:** the HPC owner must select and scientifically approve its final required Basic payload, platform, scaling and Cd evidence. The AI worker did not replace that snapshot.
3. **Human presentation:** run an actual timed combined AI+HPC 15–20 minute rehearsal, plus separate 10 minute Q&A; test Office rendering, hidden-slide navigation, screen sharing, microphone and speaker handoff. Generated render/layout checks are not a human mock.
4. **Upload logistics and receipt:** verify the assigned deadline/timezone, destination and size/additional-file limits; upload the reviewed ZIP and retain receipt/file identity. No organiser upload was performed.

## Exact current delivery

- [ZIP](../../VNUHCM%20-%20TripleU.zip): **151,822,442 bytes**, SHA-256 `303178c0da0dc8ad93ad71f75004143d191b94074e4acfbb7a9e8109ec9430ca`.
- [PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx): SHA-256 `6af3c79387baedb16b350450242214a669afc9fc34b10b5b4f1fecac5770be96`.
- [Main PDF](../../submission-review/ai-acceptance-update-20261102/TripleU_APAC2026_Main_Talk.pdf), [Vietnamese guide](../ai-final-report-20261030/TRANSCRIPT_VI.md), [English guide](../ai-final-report-20261030/TRANSCRIPT_EN.md), [study/Q&A route](../teacher-qa-preparation-20261101/README.md).

Final acceptance used 4.2 actual top-level GPU-hours across failed 28194 and successful 28197, zero PBS SU, with reservations retired. Broad research and background Codex remain stopped. Git preserves safe bytes and external-object metadata; large sibling-store artifact bytes need a separate off-host transfer.
