# Current Basic AI submission framing — 2 November 2026

Published locally **2026-11-02T22:25:35.912318+07:00, Vietnam time (UTC+7)**. The current AI deliverable foregrounds the official FP8 model, serving-only optimisation and actual performance evidence. It does not label the absence of an organiser score as a failed quality result, or assert an unmeasured >=99% pass. This is the current presentation/README edition; earlier acceptance measurements are unchanged.

## Submitted approach and facts

The team retains Qwen3-235B-A22B-Instruct-2507-FP8 as published, BF16 KV and all model layers/experts. No intentional requantisation, pruning or computation skipping is selected. Topology, supported backend selection, load tuning and request-scoped transfer metadata target the serving path. Source/range checks and actual serving evidence support this scope; full-set numerical quality remains the organiser Q1 comparison against its unchanged FP8 reference. The full-set comparison has not been measured by this worker. No organiser upload or evaluation receipt is claimed.

Completed job 28197 remains the verified performance point: 16 H200/two nodes/N64, 3051.518173 good output tokens/s, 1881/1907 joint SLA passes (98.636602%), zero request errors/cancellations, 611 seconds for the full allocation. Both P/D semantic paths, original official client, corrected readers, performance gate and cleanup pass. The latency fraction is not answer accuracy, and this acceptance does not establish a matched new optimisation gain.

## Actual edits

Main 16 is now **Preserve the model; optimise the serving path**, with model-preservation and verified-service panels. The Q1 workflow appears as neutral process context; detailed methodology and Q&A retain the exact evidence boundary. Spoken EN/VI scripts, learning Markdown/PDFs, report, README and compact package are source-matched.

The deployment README and log index contained stale statements denying a complete portable replay after reader repair. Both now reflect actual 28197. Only README/checksum metadata changed among the 26 submitted payload files; all executable worker/client/reader/environment/deployment bytes retain the accepted R2 identity. No GPU run was repeated for a documentary edit.

## Current files

- [ZIP](../VNUHCM%20-%20TripleU.zip), 151,963,879 bytes; SHA-256 `a733994595d3c11a685a35c88f5d901078394f66b8ff4b9ac6267edf1f5257d9`.
- [PowerPoint](../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx); SHA-256 `2c85a21ae0ca66b6955cfa102ca72e473f479734d9e7a2beccb3167a1a82b1ae`.
- [24-page main-talk PDF](../submission-review/ai-basic-submission-polish-20261102/TripleU_APAC2026_Main_Talk.pdf), [Vietnamese guide](../reports/ai-final-report-20261030/TRANSCRIPT_VI.md), [English guide](../reports/ai-final-report-20261030/TRANSCRIPT_EN.md), plus corresponding learning PDFs.
- [Release/reproduction notes](../submission-review/ai-basic-submission-polish-20261102/README.md), [publication verification](../submission-review/ai-basic-submission-polish-20261102/publication-validation.json), [cross-artifact checks](../submission-review/ai-basic-submission-polish-20261102/CROSS_ARTIFACT_VALIDATION.json).

Validation 637 package checks and 452 published cross-artifact checks pass. The deck retains 42 total slides: 16 main AI, 18 hidden AI and eight HPC. All 68 protected HPC dependency parts, eight HPC PDF pages, 277 folder files/modes, 265 ZIP files/member metadata and 13 earlier folder/ZIP differences are preserved. Human Office/device testing and a real timed combined rehearsal remain team actions. The HPC owner still controls its scientific payload and final snapshot selection.

Broad research remains stopped. No new GPU/PBS job, spending, authentication, organiser communication or background automation. Safe Git captures preserve changes and recovery metadata; large external-object bytes still require their separate off-host copy.
