# How long does one HPC job take?

Checked on 21 October 2026. Queue waiting and execution are separate. The
walltime in a PBS/Slurm script is an upper limit, not a prediction and not the
time every job must consume. A job can finish earlier or be killed at its limit.

| Job/stage | Actual execution | Requested maximum | Scope |
|---|---:|---:|---|
| Iris 2293752: cut and restore | 2 min 41 s | 15 min | 56-way hierarchical preparation |
| Iris 2293753: parallel initialization | 1 min 43 s | 20 min | All three mandatory native stages |
| Iris 2293754: 40-step solver | 15 min 25 s | 40 min | Practice, one node/56 ranks |
| Iris complete split chain | 19 min 49 s | Sum of caps: 75 min | Execution only; excludes gaps and queue |
| ASPIRE CPU 25904765: tiny native timing gate | 1 min 24 s | 10 min | Compiler/runtime diagnostic, no score |
| ASPIRE CPU 25905006: mesh identity + cut/restore | 3 min 7 s | 15 min | Fresh N128 case; no solver yet |
| ASPIRE CPU 25905114: full init + 40-step solver | 12 min 8 s | 35 min | Full init + 40 steps passed |

25905006 waited about 3 min 43 s before starting. That single queue delay does
not predict later jobs; queued jobs can wait much longer. Time until a result
is queue waiting plus actual execution plus evidence collection/review.

The requested CPU preparation maximum reserves at most 8 SU (32 cores × 15/60
hours). Its observed 187 seconds estimates 1.662222 SU at the site's base rate;
posted charging is not individually reconciled. The next 128-core/35-minute
request reserves at most 74.666667 SU and may finish sooner. Keep allocation
cost separate from the solver Average in seconds per CFD step.

GPU/Qwen benchmark durations belong to the separate GPU conversation. This
report covers only this HPC worker's CPU jobs. Raw execution accounting and
per-run reviews live in hpc-experiments and the HPC_CURRENT handoff.

## Current solver queue wait, 14:48 UTC

25905114 is still queued about 12 min 30 s after submission. PBS explicitly
blocks it on the qdev overall 256-core limit: 148 cores assigned leaves 108,
but the request needs 128. This is not solver execution and the 35-minute
runtime limit has not begun. There is no reliable start-time estimate yet.

## Completed baseline update

25905114 finished exit 0 after 728 seconds; its earlier pending snapshot is historical. Queue wait was about 13 min 5 s. Native solver alone reports 643 seconds; whole allocation includes setup and initialization. Estimated base charge 25.884444 SU is not an individually reported invoice.

25907236 native Scotch mesh verification + serial cut/restore: 6 min 11 s execution, 15-minute requested maximum, estimated 3.297778 SU. It is preparation, not solver performance.

25907325 same-node H→S 40+40-step method pair: **22 min 53 s** allocation, requested 29 min, estimated **48.817778 SU**. Native solver clocks H 621 s / S 616 s; preparation and all guards are additional. Both exit 0; observed 0.994% step-average reduction is limited by one ordered pair and a candidate outlier.
