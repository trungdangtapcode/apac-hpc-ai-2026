# Research milestone — 25 October 2026: S62r2 failed before its worker script

**Question and prior evidence.** S62r2 was admitted as job 26057 to test whether two TP4/EP4 decode replicas improve on the modern single TP8/EP8 decode control. The 03:08 UTC receipt correctly recorded `PENDING (Resources)` at that observation. A later queue observation showed the job had started and disappeared, so its terminal record had to be checked before launching followups.

**Measurement or failure.** `sacct` now reports job 26057 `FAILED`, exit `0:53`, elapsed 1 second, on nodes g1 and g4. Its recorded stdout/stderr destinations are under the frozen bundle's `runs/` subdirectory, which did not exist. No stdout/stderr or run artifact was created, and no worker, model, AIPerf request, score or output check ran. This is a scheduler/log-path launch failure, not a topology measurement. The exact low-level Slurm diagnostic is unavailable because the log destinations could not be opened; the missing destination directory and immediate exit strongly indicate the cause but do not prove which Slurm layer returned code 53.

**Assessment and correction.** The earlier live queue state `RUNNING` was not evidence that the benchmark had started. The job reached allocation accounting but failed before worker startup. Preserve job 26057 as failed and do not count it as a completed topology trial. The frozen payload is unchanged.

**Next decision.** Re-admit the same immutable S62r2 payload only from the existing `qwen-experiments` working directory, where its relative `runs/%j.out` destination exists. This changes the Slurm submission working directory, not the experiment payload or tested factor. Verify the new definite receipt and live queue. The four S63 load screens must also be submitted from that parent directory so their relative output paths resolve to the established `qwen-experiments/runs/` store.

**Preservation.** Slurm accounting output and the missing-log limitation are recorded here. No performance or quality data exists for job 26057.
