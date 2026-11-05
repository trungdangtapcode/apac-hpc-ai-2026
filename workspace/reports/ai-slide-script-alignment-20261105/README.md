# AI slides and spoken-script alignment — 5 November 2026

**Correction:** The first review missed the stale packaged English script and left ambiguous zero-based script headings. [Actual PPTX page map](PAGE_MAP.md) now resolves both. The earlier all-artifact alignment statement was too broad. The corrected packaged script remains local/uncommitted.

The owner identified a real mismatch: the spoken seventeen-layout search was absent from the active topology slide. The review covers every main AI slide and both short scripts, the four spoken backups, all 34 teaching-guide title routes, numerical conditions, the scatter plot and the distinction between local evidence and organiser certification.

Use the [current canonical PPTX](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), [main-talk PDF](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Main_Talk.pdf), [English script](../ai-final-report-20261030/TALK_SCRIPT_EN.md) and [Vietnamese script](../ai-final-report-20261030/TALK_SCRIPT_VI.md). Script pages 0–15 map to printed pages 01–16. The 78-slide root-level deck is a different historical presentation.

[Full slide-by-slide audit](AUDIT.md) explains each comparison and fix. [Changes](CHANGES.json), [validation](VALIDATION.json) and [local publication receipt](PUBLICATION.json) preserve the exact checked artifact hashes. [Overview](OVERVIEW.jpg) shows all sixteen main AI slides. The retained helper performs only native-text edits in eight AI slide parts; every other package member stays byte-identical, including the entire HPC dependency graph. All eight HPC PDF pages remain pixel-identical.

The visible additions anchor seventeen layouts, input/output lengths, safe coalescing, phase-specific DeepGEMM selection, the full-run usefulness cutoff, readiness repair and complete quality coverage. The scripts now explain code inspection on the intervention slide and refer to the profiling visual as a category map. Short sentences and rounded speech remain; all figures have been checked against the existing evidence. Approximate English duration is 12.6–13.1 minutes under the stated assumptions, not a human-timed rehearsal.

## Reproduce and review

Install `requirements.txt` in a Python 3.9-compatible virtual environment. Run `build_alignment.py`, then `validate_alignment.py`. The builder reads the preserved `inputs/before.pptx` and the retained historical coordinate PDF in `submission-review/ai-narrative-12min-20261103`. It writes review candidates and render previews; it does not publish them automatically. The old input PPTX is preserved for recovery. The original short scripts in `inputs/` remain local only.

PDF previews are coordinate renders with matching overlays, not an actual Microsoft Office render. The built PPTX was reopened and text/route/package checks passed. Human rehearsal and projector testing remain outside these checks.

The short scripts remain uncommitted under the earlier owner instruction. This checkpoint archives the reviewed deck/PDF bytes through the local external object store plus code, audit, manifests and receipts. Git alone does not upload external artifact bytes. No new GPU work, budget, VPN change, HPC edit or organiser upload occurred. The historical submission ZIP and long teaching-guide PDFs are unchanged; they are not relabelled as this new presentation revision.
