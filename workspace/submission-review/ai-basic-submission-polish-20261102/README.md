# Basic submission framing and consistency update — 2 November 2026

This edition leads with the preserved official FP8 model, serving-only optimisation scope and verified 16-H200 performance. It does not present the absence of an organiser quality score as a failed experiment or invent a measured >=99% pass. Main slide 16 now says **Preserve the model; optimise the serving path**, with model-preservation and verified-service panels and a neutral Q1 evaluation-process line.

## Scientific scope

The official Qwen3-235B-A22B-Instruct-2507-FP8 checkpoint is retained without intentional requantisation, layer/expert skipping or approximation. The served KV cache uses BF16. The text-submitted request-descriptor patch targets transfer metadata; source/geometry checks and the actual serving run support the stated scope. These are the grounds for the Basic approach, not a replacement for numerical full-set accuracy measurement.

Job 28197 remains the same completed 16-H200/two-node/N64 measurement: 3051.518173 good output tokens/s, 1881/1907 joint latency passes (98.636602%), zero request errors/cancellations and full deployment/client/readers/gate/cleanup success in 611 seconds. The 98.636602% fraction is a latency result, not model accuracy. Raw evidence, original failures and machine-readable quality provenance remain unchanged. No new GPU trial, quality result or organiser upload was performed.

## Documentary corrections

The main conclusion and spoken scripts foreground the retained model and measured serving contribution. Detailed methodology and Q&A still explain that organiser Q1 uses its own unchanged FP8 reference and that no team full-set score is claimed. The report preserves reasoning, negative results and observation/hypothesis distinctions. No limitation was relabelled as a measured pass.

Two stale README statements incorrectly said that a complete reader-repaired GPU replay had not occurred. They are corrected to reflect actual job 28197. The deployment README and its checksum are documentary changes; all executable files, environment, workers, clients and readers are required to match the accepted R2 runtime exactly.

## Verification and reconstruction

The source tools now select a separate review directory using `TRIPLEU_REVIEW_STAGE`; `ai_release_context.py` rejects absolute paths and parent traversal. The earlier default stage remains a dated record. This stage was created with `TRIPLEU_REVIEW_STAGE=submission-review/ai-basic-submission-polish-20261102` and `TRIPLEU_PREVIOUS_STAGE=submission-review/ai-acceptance-update-20261102`; the merge uses `TRIPLEU_PART_PREFIX=aib02_` to avoid existing PowerPoint part names. Run the slide, merge, guide-source, guide and PDF builders in that order, then `prepare_ai_basic_polish_20261102.py` and the package/release validators before the guarded publisher. Dependencies are pinned in `slides/requirements.txt`.

The snapshot protects each HPC delivery surface independently: 277 folder files/modes, 265 ZIP files/member metadata, 68 PowerPoint dependency parts and eight PDF pages. The 13 existing HPC folder/ZIP differences remain. No HPC scientific payload is selected or updated by the AI worker. The complete deck still has 16 main AI slides, 18 hidden AI backups and eight HPC slides; the main PDF has 24 pages.

`VALIDATION.json`, `merge-validation.json`, guide/PDF source identities and cross-artifact reports distinguish prepared, locally published and organiser-uploaded states. Actual Office/device rendering and a human timed mock remain outside automated validation. Official quality follows the organiser's protocol; there is no organiser upload receipt from this worker.

Safe Git captures preserve source changes and recovery metadata. Large retained objects remain in the sibling artifact store and need a separate off-host byte copy; a Git push is not that transfer. Prior releases, raw runs and the former wording remain recoverable in history.
