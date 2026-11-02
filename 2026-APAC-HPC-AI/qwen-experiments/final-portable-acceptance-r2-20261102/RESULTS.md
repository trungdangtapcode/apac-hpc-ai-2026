# Complete repaired portable AI entry accepted: 28197

Reviewed 2026-11-02T08:45:32.978352+07:00, Vietnam time (UTC+7). **PASS for local complete deployment and performance acceptance.** Slurm COMPLETED/0:0, 611 seconds, g1/g4, 16 H200, N64. Both semantic P/D paths, unchanged official benchmark, corrected readers, performance gate and all job cleanup completed. [Independent review](RESULTS_REVIEW.md), [machine-readable review](result-28197.json), [raw integrity manifest](ARTIFACT_MANIFEST.json).

| Metric | Value |
|---|---:|
| Good output tokens/s | 3051.518173303673 |
| Exported Goodput requests/s | 15.257590866518365 |
| Joint good requests | 1881 / 1907 = 98.63660199265862% |
| TTFT / ITL misses | 26 / 0; all misses TTFT-only |
| Scored errors / cancellations | 0 / 0 |
| TTFT mean / p95 | 1100.3153138463554 / 1285.9962342999993 ms |
| Request-mean ITL mean / p95 | 15.009828199279305 / 15.185750323618091 ms |
| Actual top-level GPU-hours | 2.715555556 |
| Both final attempts combined top-level GPU-hours | 4.2 (includes failed 28194) |
| PBS SU | 0; no H100 project use |

The improved gateway gate confirmed model registration at 333 seconds after job start; both semantic routes passed by 375 seconds and official client/postprocessing completed by 603 seconds. This fixes the specific /health 200 / /v1/models 503 race that made 28194 fail before scoring. Pair-specific routers also briefly returned 503 while registering; existing bounded retries then produced two valid semantic receipts. These are startup observations, not scored request errors.

The exact original official command and worker/readers/semantic gates remain byte-identical; only the deployment readiness function and checksum changed. All 26 frozen files match their actual submitted copies. The readers resolve the actual nested export and canonical /scratch/home alias successfully, so this is the first reviewed complete post-reader-fix portable entry, not CPU-only data recovery.

191 decode log snapshots show about 49.98 running requests on average, sampled queue 0 and token usage about 0.1175. These are scheduler log samples, not GPU utilization. NVML/VRAM/power/temperature/CPU/network/phase hardware telemetry was **not collected**. Exported client token lengths span 199–201; authoritative generated IDs were not retained, so no physical truncation cause is inferred. The official score remains exported Goodput×200.

This is a same-recipe deployment acceptance observation, not a matched optimisation gain. Historical three-run 3044.400475, native 26766: 3045.501509 and previous cache 27378: 3048.446289 remain separate series. Recovered raw 27145: 3055.330517 remains tied to an originally failed job. Official full-set model quality remains UNKNOWN; this job contains two semantic startup checks, not a new smoke 8 / retrieval 12 or full accuracy evaluation.

The independent reviewer accidentally reran the CPU fixture script while invoking --help, refreshing validation.json/setup-check.log after the GPU run. This did not touch raw inference evidence, payload or scheduler state. The original before-admission fixture report is recovered byte-for-byte from committed 9d472cb7 as validation-before-submit.json; the later validation is a separately timed CPU replay.

**Decision:** qualify the readiness-only R2 entry for deliberate publication to the submission, update accepted deployment claims and close the final GPU acceptance stage. Do not submit more tuning jobs. The published ZIP still needs the qualified deployment/code and evidence update; preserve both HPC surfaces independently during publication.
