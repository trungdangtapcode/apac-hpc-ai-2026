# HPC presentation update — 3 November 2026

Published locally at **3 November 2026, 16:44:09 Vietnam (UTC+7)**. The owner requested an HPC-only slide update after asking why the lowest Iris observation used 14 rather than 40 steps. The eight HPC slides remain at positions 35–42 of the 42-slide deck. All 34 AI slides, their dependency bytes and speaker-note bodies remain unchanged; 18 AI backups remain hidden.

The new HPC content defines the three Iris recipes, shows their lowest reviewed whole-arm means with explicit horizons, and distinguishes those observations from pooled within-job comparisons. The 21.0512 s/step graph-placement arm has only 13 measured intervals. Its complete reversed test loses 5.37%; the separate plain-zyx 40-step comparison loses 10.21%. No own stable win or three-way ranking is claimed. The teammate's 11.22% lower mean remains a qualified short-run signal. The obsolete queued NSCC job is replaced by the completed 3.3646 s/step organizer-recipe reproduction. NSCC, Iris and Gadi raw seconds are never ranked together.

The original visual theme, eight distinct photographic backgrounds, metric/pipeline explanation and historical tail example remain. Sources and job IDs are in speaker notes. Slide text is for presenting the research, not explaining archive folders.

## Outputs and verification

- `TripleU_APAC2026_Presentation.pptx`: combined 42-slide deck.
- `TripleU_APAC2026_Presentation.pdf`: all 42 slides.
- `TripleU_APAC2026_Main_Talk.pdf`: 16 main AI slides followed by eight HPC slides.
- `slide-section/HPC-section.pdf`: just the eight updated HPC slides.
- `PRESENTER_NOTES.md`: combined notes with AI note bodies unchanged.
- `merge-validation.json`: byte-identical AI dependency closure, sequence, notes and pixel-identical AI PDF pages; resolved OOXML links, slide bounds and background checks.
- `SOURCE_EVIDENCE.json`: pinned evidence and content/visual review scope.

PDFs and preview images share drawing coordinates with the editable slides. They are not an Office or presentation-device rehearsal. The stored-slide proportion remains 8/42 (19.05%); the visible main talk is 16 AI +8 HPC because AI backup slides are hidden.

## Publication scope

The guarded publisher replaces only the canonical PPTX and its dependent global checksum entries, then replaces the same three entries in the existing team ZIP. Those checksum files happen to live under `AI_Task/logs/`; no AI content is edited. All HPC and AI job scripts, measurements and other payloads remain unchanged, including existing folder/ZIP differences. Publication requires the input snapshot to remain unchanged under the shared publication lock. `publication-validation.json` is the receipt when publication completes. This is a local package update, not an official contest upload.

## Rebuild

Use `/home/apacsc42/.local/share/tripleu-presentation-venv/bin/python` and the pinned section requirements. Run `workspace/submission-tools/build_hpc_iris_slides_20261103.py`, then `merge_hpc_iris_slides_20261103.py` against the retained `inputs/`. Inspect the generated previews and validation before running `publish_hpc_iris_slides_20261103.py`. Publication refuses a changed or already-published snapshot; do not bypass its guard.

The publication verified 200 protected AI PowerPoint parts, 34 unchanged AI PDF pages, 2,152 unchanged folder files and 2,452 unchanged ZIP entries. The only package edits were the combined PPTX and its two global checksum records. The old NSCC tail example remains explicitly dated; the new native preparation trial is not counted as a reviewed performance result.

## Verified off-host copy

All six final presentation/package assets were uploaded to the existing private GitHub repository, downloaded again and verified by SHA-256 and byte length. [Private backup receipt](offhost/README.md) preserves source paths, remote asset names and recovery commands. The broader external artifact store is outside this six-file backup.
