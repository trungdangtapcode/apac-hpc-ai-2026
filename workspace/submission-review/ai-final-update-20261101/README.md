# Final AI presentation and evidence update — 1 November 2026

This authorised revision explains the engineering decisions behind the AI results and includes the final nine H200 verification allocations. It addresses the exact owner-supplied `/home/apacsc42/requirement.md`; its SHA-256 is `c5501a44540ca7d3834e731dac3472afacdf1d5505cabdfdaf2d29809323ae20`. It does not alter the independent HPC technical content, claim an official quality result, conduct a human mock or launch research.

## Presentation and learning route

- `TripleU_APAC2026_Presentation.pptx`: 16 main AI slides, 18 hidden AI backups (17–34) and eight preserved HPC slides (35–42).
- `TripleU_APAC2026_Main_Talk.pdf`: 24 visible pages, going directly from AI 16 to the preserved HPC section.
- `TripleU_APAC2026_Presentation.pdf`: all 42 slides for Q&A.
- [Concise English script](../../reports/ai-final-report-20261030/TALK_SCRIPT_EN.md) and [Vietnamese script](../../reports/ai-final-report-20261030/TALK_SCRIPT_VI.md): explain observations, decisions and transitions without reading every table value.
- [English slide learning guide](../../reports/ai-final-report-20261030/TRANSCRIPT_EN.md) and [Vietnamese guide](../../reports/ai-final-report-20261030/TRANSCRIPT_VI.md), each with a matching PDF: each slide starts with a short spoken brief, then explains hardware, symbols, colors, axes, units, tradeoffs and evidence limits.

The four research questions remain resource distribution, performance limits, useful SLA-qualified interventions and robustness. The topology selection gates are visible on slide 3. Slides 5–7 explain why the descriptor hypothesis was bounded and cheap to check, and exactly what the patched run established. Slides 8–10 separate diagnostic profiling from a controlled service-level decode experiment. Main slide 14 now uses direct H200 verification; backup 33 retains the historical forecast and backup 34 records all nine final jobs. Failed, losing and unresolved branches remain in the journey and Q&A, not erased to make the result look monotonic.

## Current scientific conclusion

Retain the H200 N64 recipe: two TP4/EP1 DeepGEMM prefill workers, chunk 8192; one TP8/EP8 HPC-Ops decode worker, FlashInfer decode attention, MNNVL collectives and NIXL cross-role KV transfer. The historical three-run mean of 3044.400475 good output tokens/s remains distinct from the final fresh controls. None of the final candidates establishes a useful gain above the prospective team-set 1% decision gate. Eight final jobs are N64 and one (27781) is N54; the two controls serve different comparison branches.

Descriptor counts are not a speed ratio, a failed unpatched warmup is not a throughput baseline, N48 kernel-duration sums are not N64 request wall time, and H100 scores do not rank H200 configurations. Official full-set accuracy against ≥99% of the organiser reference remains UNKNOWN. A complete portable GPU replay after result-reader repair is not claimed.

## Checks and publication

`STAGED_VALIDATION.json` verifies actual logical slide order, titles/notes, visible sequence, guide/PDF identity, nine exact score exports and nine lossless request-export decompressions. Independent read-only reviews found the reasoning gaps addressed in the actual deck and no compact-package content blocker. The stale stage-plan navigation note found during review was corrected to 17–34 / 35–42 before publication.

`package-file-map.json` is the explicit AI-only delivery selection. English report/scripts and compact raw evidence are staged under `package-files`; linked full research sources outside that selection are labelled explicitly. No Vietnamese learning guide is put into the English submission. `publish_ai_final_20261101.py` validates the live preservation snapshot, updates only the reviewed presentation, selected AI logs/documents and global manifests, retains old archive member metadata, and preserves the folder/ZIP HPC surfaces separately. The 13 existing HPC surface differences are not silently merged. `publication-validation.json` and `FINAL_VALIDATION.json` are written only after their corresponding operations succeed; absence means the operation is not yet certified.

The team still needs the real timed combined mock, an unfamiliar-listener/Q&A check and actual Office/screen-sharing/microphone tests. Public rules provide a combined AI/HPC talk of 15–20 minutes plus a separate 10-minute Q&A. The AI 10–12-minute target is a proposed share, not permission to consume all presentation time. No organiser upload is performed here.

## Reproduction

Use the retained Python environment with python-pptx, PyMuPDF, ReportLab, Pillow, matplotlib, numpy and mistune. The snapshot step refuses to overwrite its frozen inputs. With the preserved inputs, plan, transcript JSON and assets in place, run these tools in order from the workspace's parent directory:

1. `build_ai_final_slides_20261101.py`
2. `merge_ai_final_20261101.py`
3. `extract_ai_final_transcript_source_20261101.py`
4. `build_ai_final_guides_20261101.py`
5. `render_ai_final_transcripts_20261101.py`
6. `prepare_ai_final_package_docs_20261101.py`
7. `validate_ai_final_20261101.py`
8. `publish_ai_final_20261101.py` only against its matching unchanged live snapshot.
9. `validate_ai_final_20261101.py --published`

Tools live in `workspace/submission-tools/`. AI PDFs use the same coordinates as the editable PowerPoint, not an Office renderer. Large artifacts are retained through the research archive's external-object mechanism; pushing Git alone does not upload their bytes off-host.
