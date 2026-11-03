# Completed quality evidence in the AI presentation — 3 November 2026

Published locally and checked **2026-11-03T14:00:51.849386+07:00, Vietnam time (UTC+7)**. The owner asked whether the report, slides and transcript contained the completed quality comparison. The research report already did; this update integrates the result into the current presentation, both speaking/learning scripts and the AI submission evidence.

## What changed and why

Main slide **16** now states **“The optimised service retains 99.9154% of reference accuracy.”** Two columns show stock FP8 9460/12032 = 78.6237% versus optimised service 9452/12032 = 78.5572%, followed by the ratio 9452/9460 = 99.9154% and the local 99% threshold. Both measurements use the same 16 H200 GPUs and frozen MMLU-Pro questions. Dark teal identifies the reference and orange the candidate; color does not imply higher candidate accuracy. The existing theme, background imagery and slide order remain.

The scripts explain the reasoning: fast synthetic answers do not establish correctness, unchanged weights alone do not prove a quality pass, so we froze questions and scoring and measured the complete deployments. They distinguish absolute accuracy from accuracy retention and the latency SLA fraction. The local check passes; organiser certification remains separate. Full guides preserve the failed pilot, category losses, invalid/length-cap handling, paired disagreements and one-pass-per-role limit. Slides 1 and 13 have only the relevant current-quality clarification in their notes. The eight HPC slide records and transcript sections are unchanged.

The English final report, short EN/VI talks, Q&A, evidence cards and journey are updated. The generated EN and VI learning guides retain a 10–20-second brief before each slide purpose, hardware labels, units, visual interpretation and speaking transitions. EN PDF has 111 pages; VI PDF has 104. Slide 16 begins on PDF page 51 EN /49 VI.

## Packaged reproducible evidence

`AI_Task/logs/quality-20261103/` contains the prepared corpus, exact frozen scorer, all 24,064 raw responses in lossless gzip, run metadata, complete comparison, native accounting and analysis. Its `replay.py` reconstructs the same full score without GPUs. The actual staged replay reproduced reference 9460 / candidate 9452 and every paired outcome. Invalid parses are wrong; length-capped answers stay in the denominator and are scored normally, not automatically marked wrong.

The accepted 28197 serving runtime is byte-identical; only documentation and its checksum metadata changed in `job_scripts/`. Its **3051.518173 good output tokens/s** and **98.636602% joint SLA fraction** remain performance results. No new GPU job, benchmark, authentication or official upload occurred in this publication turn.

## Validation and protected surfaces

- 847 staged package checks, 76 quality evidence checks, and 596 published cross-artifact checks passed.
- PPTX, slide PDF, Markdown source and learning PDF hashes are tied to the same publication. New slide and EN/VI page previews were visually inspected; the PDF is coordinate-rendered, not a claim of an Office/device rehearsal.
- All **68 HPC PowerPoint dependency parts**, **eight HPC PDF pages**, **277 folder files and modes**, **265 ZIP files and ZIP metadata**, and **13 existing folder/ZIP differences** remain preserved. Existing HPC transcript sections also match byte-for-byte.
- Final deck: 42 slides, 16 main AI +18 hidden AI backups +8 HPC. Main-talk PDF: 24 pages. Slide 16 advances to the unchanged HPC 35.

Current PPTX SHA-256: `239a89d2b23fef51be4ae7f53b5de5ab79a725f6499c4a76268e40d9b81b642b`.
Current ZIP: 185,018,580 bytes; SHA-256 `28504d43febea5dd5ab8578a03ff6ca2a0d168f9319f96547fc2e7026f1c1d42`.

## Rebuild route

Use `/home/apacsc42/.local/share/tripleu-presentation-venv/bin/python` with pinned `slides/requirements.txt`. Set `TRIPLEU_REVIEW_STAGE=submission-review/ai-quality-update-20261103` and `TRIPLEU_PART_PREFIX=aiq03_`. The original snapshot is retained under `inputs/`; never overwrite it with a later deck.

Reproduction scripts in `workspace/submission-tools/` run in this order: quality transcript update; quality slide builder; acceptance merge; acceptance source extraction; quality guide builder; acceptance guide-PDF renderer; quality package preparation; the packaged CPU replay with a fresh output path; acceptance package validation; quality package validation; quality release validation. Publish only the reviewed stage using the guarded acceptance publisher, then rerun quality release validation with `--published`. The base acceptance tools are reused for their exact HPC-preservation checks, not to claim an earlier quality test.

Published locally is separate from an organiser upload. Git captures retain sources and recovery manifests; final off-host artifact receipts are recorded separately.
