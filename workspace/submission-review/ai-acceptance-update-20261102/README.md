# AI acceptance release — 2 November 2026

This edition incorporates the reviewed successful portable run **28197** into the AI deployment, presentation, English submission reports and bilingual learning guides. It preserves the separate HPC worker's folder, ZIP member bytes and metadata, and eight slides. It is a local release, not an organiser upload or official quality evaluation.

## Evidence and decision

The exact previous ZIP retry, **28194**, failed before scoring: the health endpoint was available while asynchronous model registration still returned HTTP 503. There is no performance score for that failed allocation. The narrow R2 fix waits for a valid `qwen` model inventory within the existing job-start deadline, checks worker liveness and retains the official workers, workload, semantic checks and readers unchanged. Five CPU readiness fixtures passed before the new GPU run.

**28197 completed 0:0 in 611 seconds on 16 H200 GPUs, two nodes, closed-loop N64.** Its exported goodput is 15.257590866518365 requests/s. The contest score is therefore **3,051.518173303673 good output tokens/s**. Independently replaying all scored raw records gives **1,881 / 1,907 = 98.63660199265862%** joint SLA success, 26 TTFT misses, zero mean-ITL misses and zero errors/cancellations. Both P/D semantic routes, the official AIPerf client, summary readers, the performance gate and terminal cleanup pass. The scored request duration is 120 seconds; 611 seconds is the entire allocation, including deployment and cleanup.

This is a same-recipe deployment acceptance result. It does not isolate an optimisation speedup or establish a global optimum. The historical N64 three-run mean remains 3,044.400475, native 26766 remains 3,045.501509, and failed-allocation raw observation 27145 remains a separate 3,055.330517 record. Do not pool those result classes or relabel failures. No new smoke-8 or retrieval-12 suite was run in 28197. Official full-set quality is **UNKNOWN**, pending organiser evaluation against its FP8 reference. A local deployment/SLA pass is a different claim.

Actual top-level use is 2.715556 GPU-hours for 28197 and 1.484444 GPU-hours for failed 28194, total 4.2 GPU-hours, zero PBS SU. Runtime server samples were reviewed; GPU/CPU/network hardware telemetry was not collected for 28197. No compute-bound or transport-bandwidth causal claim follows.

## What changed

- Main AI slide 13 distinguishes the historical repeated result, native reproduction and new accepted portable deployment. Slide 16 closes the deployment gap while retaining the separate official quality limit. Backup 31 explains failure, narrow hypothesis, repair and complete verification. Topology, descriptor and backend reasoning remain problem-driven.
- The full deck remains 42 slides: 16 main AI, 18 hidden AI backups and eight unchanged HPC slides. The main PDF has 24 pages; the full PDF has 42. English and Vietnamese Markdown guides and their printable PDFs remain bound to the exact new PowerPoint hash.
- The runtime deployment edit is exactly the one qualified by 28197. README and SHA256SUMS are documentary updates; other executable model/worker/client/reader files retain tested bytes. The compact package retains score exports, losslessly compressed request rows, semantic receipts, runtime/Slurm logs, failure history and independent review. Large generated inputs stay in the research archive, not the compact competition package.
- Publication updates each delivery surface separately. It preserves all 277 HPC folder files/modes, 265 HPC ZIP files/member metadata, 68 PowerPoint dependency parts, eight PDF slide images and the 13 existing HPC folder/ZIP differences. Never recreate the ZIP indiscriminately from the working folder.

## Verification and reproduction

The source builders are under `workspace/submission-tools/` with suffix `ai_acceptance_*_20261102.py`. Build order: slides → merge → extract guide source → build guides → render guide PDFs. Package preparation and validation precede the guarded publisher. `merge-validation.json`, `VALIDATION.json`, `publication-validation.json` and `CROSS_ARTIFACT_VALIDATION.json` record their respective actual scopes. The publication report exists only after successful local publication.

Use a dedicated Python environment with `slides/requirements.txt`. The working rebuild environment is `/home/apacsc42/.local/share/tripleu-presentation-venv/bin/python`. The older temporary environment had incomplete imports; the cause was not established. The replacement was built from pinned packages without changing the model container or shared system Python. The virtual environment, private runtime home and authentication material are excluded from preservation.

The snapshot is `HPC_BEFORE.json`. The publisher retains the previous local release under `workspace/submission-archive/` and rolls back an interrupted mutation. `PUBLISHER_CANDIDATE.json` distinguishes local publication from organiser submission. No new optimisation job, H100 login/spending, HPC payload change or background Codex was authorised here.

Still requires the owners: official quality/rebuild scoring, HPC scientific approval for its final snapshot, a real timed combined mock and device check, and the actual portal destination/deadline/upload receipt. Pending official quality is not a fabricated Basic pre-upload prohibition. Git pushes preserve safe Git bytes and external-object recovery metadata; they do not upload large sibling-store artifact bytes off-host.
