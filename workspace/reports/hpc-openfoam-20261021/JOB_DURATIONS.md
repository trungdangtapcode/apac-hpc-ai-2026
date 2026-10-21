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
| Next ASPIRE CPU full init + 40-step solver | Not measured yet | 35 min | Conditional promotion after reviewed prep |

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
