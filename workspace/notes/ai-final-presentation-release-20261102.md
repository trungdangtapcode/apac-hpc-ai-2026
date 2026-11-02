# Current AI presentation and accepted deployment — 2 November 2026

Updated **2026-11-02T08:57:13.375119+07:00, Vietnam time (UTC+7)**. **Job 28197 completed successfully, and its tested readiness correction is now in the published local submission ZIP.** The earlier pending/R1-defect accounts below are historical; original failed evidence remains unchanged.

On 16 H200 GPUs / two nodes / N64, the complete job took **611 seconds (10 min 11 s)** and scored **3051.518173303673 good output tokens/s**. Exported goodput is 15.257590866518365 requests/s; multiplier 200 is the official unit conversion. **1881/1907 requests passed both latency limits (98.63660199265862%)**. There were 26 TTFT misses, zero mean-ITL misses and zero errors/cancellations. TTFT mean/p95: 1100.315/1285.996 ms; request-mean ITL mean/p95: 15.010/15.186 ms. Both semantic P/D routes, the official client, corrected summary readers, performance gate and cleanup pass. Independent replay of raw scored request rows agrees. Only the two startup semantic checks ran here; do not invent a new smoke-8/retrieval-12 quality suite.

The old exact-ZIP attempt **28194 remains FAILED 22:0**, before AIPerf. Gateway health returned HTTP 200 before asynchronous model registration, followed by /v1/models 503. R2 waits for valid registered `qwen` inventory within the existing startup deadline and checks worker liveness. Five CPU fixtures preceded the successful full GPU qualification. No worker/model/client/reader configuration changed; publication changes README/checksum metadata in addition to that tested deployment script.

The new score is an accepted **same-recipe deployment measurement, not a matched speedup**. Historical N64 mean 3044.400475, native 26766 3045.501509 and failed-allocation recovered raw 27145 3055.330517 remain separately classified. Lower valid replay 2830.923547 is still unexplained. H100 measurements are separate and were not rerun or converted. Hardware telemetry was not collected for 28197; runtime log observations are not GPU utilization or causal profiling.

Actual top-level use: 28197 2.715556 GPU-hours, failed 28194 1.484444, total 4.2; zero PBS SU. The bounded final-acceptance objective is complete and reservations are retired. Broad research remains stopped; no further AI job, VPN login, HPC action or automation is authorised by this completion.

## Current deliverables

- [Submission ZIP](../VNUHCM%20-%20TripleU.zip), 151,822,442 bytes; SHA-256 `303178c0da0dc8ad93ad71f75004143d191b94074e4acfbb7a9e8109ec9430ca`.
- [PowerPoint](../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), SHA-256 `6af3c79387baedb16b350450242214a669afc9fc34b10b5b4f1fecac5770be96`.
- [Current release and verification](../submission-review/ai-acceptance-update-20261102/README.md); [24-page main PDF](../submission-review/ai-acceptance-update-20261102/TripleU_APAC2026_Main_Talk.pdf).
- Source-matched [Vietnamese guide](../reports/ai-final-report-20261030/TRANSCRIPT_VI.md), [English guide](../reports/ai-final-report-20261030/TRANSCRIPT_EN.md), and their printable PDFs are updated. English submission script and separate Vietnamese learning script now explain the accepted run.
- [Independent result review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/RESULTS.md) and [full evidence route](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/STATUS.md).

The deck remains 16 main AI + 18 hidden AI backups + eight preserved HPC slides. All 68 HPC PowerPoint dependencies, 277 folder files/modes, 265 ZIP files/member metadata and the 13 prior folder/ZIP differences are preserved. English package documents and compact raw evidence are current; private runtime caches, weights and the large generated input file are excluded from the compact delivery. Full raw input remains in the research archive/external store.

**Official quality remains UNKNOWN:** deployment/SLA acceptance is not the organiser's full-set ≥99%-reference evaluation. The organiser evaluates its own reference and rebuild; pending quality is not an invented Basic pre-upload prohibition. Still requires the responsible owners: HPC scientific/snapshot approval, a real timed combined rehearsal and Office/device check, and final portal logistics/upload receipt. No organiser upload was performed. Safe Git commits include recovery metadata; large external-object bytes still need a separate off-host copy.
