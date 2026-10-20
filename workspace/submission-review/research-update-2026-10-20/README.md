# Qwen research presentation — 20 October 2026

The 32-slide English talk retains the established Metropolis adaptation, light native gradients and 32 distinct sourced background photographs. The main talk is 24 slides; eight appendix slides support questions. The presentation explains the research, including topology selection, NIXL repair, phase-specific kernels, repeated gains, rejected branches, platform comparison and the next measurement design.

H200 job 24915 is the highest individual local observation at 3022.035 good output tokens/s and N62, with 1860 of 1884 requests meeting both limits. It still needs an independent repeat. H200 N60 is independently reproduced at 2990.151 and 2989.175. H100 remains a separate frontier at 2430.891; the fresh FlashInfer/FA3 pair explains its latency tradeoff. Local synthetic output checks do not establish the official full-set 99%-reference quality requirement.

## Build and review

Run from the restored original source layout, with the presentation dependencies in requirements.txt installed:

```bash
python workspace/submission-tools/build_research_update_20261020.py
python workspace/submission-tools/publish_research_update_20261020.py
```

The builder uses presentation-data.json as its frozen input, plus drawing-helpers.py, background-manifest.json and the retained design-assets directory. The freeze script reconstructs a snapshot from retained raw sources and the prior 17 October historical data/scanner; it rescans available records and therefore is not required when reproducing this frozen presentation. Source paths in the manifest use the original source layout. Preserve the retained inputs; do not substitute later benchmark files silently.

The publisher verifies all 107 frozen source hashes, English visible text and notes, headline values, raw per-request SLA counts, unique embedded backgrounds, gradient alpha, text-box bounds and package checksums. It archives the prior presentation/package, replaces the PPTX, updates presentation metadata and reseals the ZIP. It checks that AI job scripts remain byte-identical and HPC_Task remains empty. It does not submit to the organiser or promote a research script.

PDF, previews and overview use the same explicit drawing coordinates as the editable PowerPoint, rendered with ReportLab and PyMuPDF. They are not an Office or LibreOffice rendering. Automatic box checks and visual review cannot guarantee identical font rendering in every PowerPoint installation.

Speaker notes and source references are retained in the PPTX and PRESENTER_NOTES.md. Background attribution is in the source manifest and embedded credits; the photographs illustrate reference infrastructure, not the contest installations. No new AI-generated background is used.
