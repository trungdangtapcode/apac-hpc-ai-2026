# Replace ambiguous transcript labels with technical explanations

Date: 30 October 2026, Vietnam time (UTC+7). Reporting only; research remains stopped.

## Question and earlier evidence

The owner found “a reviewed local full run” unclear and rejected descriptions of obvious slide decoration as inadequate teaching material. The first bilingual transcript existed, but a label without an operational definition did not prepare a presenter to explain the work.

## Changes

Revise both [English](../../../ai-final-report-20261030/TRANSCRIPT_EN.md) and [Vietnamese](../../../ai-final-report-20261030/TRANSCRIPT_VI.md) guides and their per-slide source data. Explain that team-measured results ran on the assigned H200/H100 compute clusters; local refers to validation scope. Define the campaign's 60-second warmup, 120-second profiling and 30-second grace, implemented run checks versus scheduler success, official accuracy versus small output tests, control/candidate comparisons, repeat evidence and the team-set useful-gain threshold.

Replace visual-decoration narration with result interpretation and reasoning. Keep meaningful axes, units, colors and per-request semantics. Expand difficult terms such as native runtime, backend, allocation, graph buckets, profiling/kernel-time shares, input preservation and failed-reader score recovery. Preserve the distinction between NUMA memory locality and the ambiguous validation label. Explain the unchanged HPC section from its retained evidence without updating its historical scheduler status.

## Observations and assessment

Job 27378 remains an individual full measurement of 3048.446289 good output tokens/s, only +0.240921% over control 27376. The historical N64 mean remains 3044.400475 across three full runs. These are separate series, and the largest point does not by itself establish a useful improvement. Job 27145's recovered 3055.330517 remains a score inside an originally failed job. No new experiment, score, official acceptance or causal explanation is introduced.

## Verification and next decision

Render both languages from source-matched slide records. Check all 40 titles, populated fields, complete text and local document/image links; verify deck and team ZIP hashes are unchanged. Review critical definitions and charts manually. Capture and push this correction as a separate documentation checkpoint. Future presenter explanations should define the operational meaning of unfamiliar terms and explain decisions without assuming that literal translation makes a concept clear.
