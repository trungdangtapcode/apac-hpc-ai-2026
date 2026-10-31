# Final job and hardware reconciliation

Observed **2026-10-31T09:54:58.497091+07:00**, Vietnam time (UTC+7); UTC 2026-10-31T02:54:58.497091+00:00. This is a live queue check plus retrospective documentation. Research remains stopped; no job, VPN login or DUO request is initiated.

## Hardware and result separation

**H200 / Firmus / Slurm:** selected N64 historical three-run mean **3044.400475 good output tokens/s**; separate native reproduction 26766 **3045.501509**. Highest complete team-reviewed full measurement 27378 **3048.446289**, only +0.240921% versus its own control, so not a confirmed replacement. Recovered portable 27145 **3055.330517** remains data from an originally failed postprocessing job.

**H100 / NSCC ASPIRE 2A+ / PBS:** retained historical peak 222048 **2433.019859 good output tokens/s**, N54; fresh full control 225227 **2399.186728**. These are separate hardware/configuration series, not pooled with H200. The same-configuration forecast check is a bounded analysis, not a universal conversion.

## Current queues

- H200: successful squeue query returns no jobs for apacsc42.
- H100: the existing-path probe returns NAMESPACE_UNAVAILABLE. PBS queue and any newer remote terminal results are **UNKNOWN**, not empty. No fresh authentication or MFA is attempted. The retained H100 scores above are historical, not new observations.

## Terminal runs and missing notes

Fresh accounting from 29 October UTC through the query has 13 AI-owned allocation rows, all terminal: 10 completed and 3 failed. The latest accepted jobs are 27506 and 27510; no later own Slurm allocation appears. See slurm-accounting.psv for exact IDs/times and audit.json for the snapshot. No global claim about every historical run or inaccessible PBS job is made.

| Job | Resource / actual outcome | Existing final-report coverage | Reconciliation |
|---|---|---|---|
| 27510 | 16 H200; completed 0:0/13:15; 3029.861122 good tokens/s, -0.370208% vs 27376 | Already in report, measured delivery notes and sparse result review | Advance admission status, final RUNS and comparison index; keep dense graphs |
| 27506 | CPU only, zero GPUs; completed 0:0/95s; two synthetic fixtures pass; JIT 26.605s | Already mentioned in final report; no inference score | Add source-bound terminal review and original-path seal; raw delivery copies were already backed up |
| 27383 | 16 H200; failed before benchmark at native RoPE/fused-KV assertion | Already documented | Failure remains; no score |
| 27387 | CPU only; failed process deadline before fixture completion | Already documented | Failure remains; successful 27506 is a different allocation |

No newly found score changes the selected configuration. The gap was stale status/ledger entries and missing canonical run-path seal and terminal review, not an omitted winning benchmark. Official model quality remains unverified. Other 29 October terminal results were already documented in retained reviews; the table focuses on the final two completion gaps and their prerequisite failures.

## Limits and next decision

H100 cannot be called reconciled without authenticated read-only PBS access. The user asked to inspect and record, not resume experiments; do not submit, cancel, retry or authenticate repeatedly. Preserve the independent HPC worker's queues, payloads and budget. Slides and ZIP remain unchanged because their scientific result summaries already include both final jobs.

A hash-based preservation check confirms all four CPU raw files already had identical captured copies under final delivery cpp-cpu-27506 and its review stage. The earlier admission-time stop note warning about uncaptured raw files is historical. This turn adds original source-path capture, not a claim that previously preserved bytes were missing. See cpu-existing-backup-coverage.json.
