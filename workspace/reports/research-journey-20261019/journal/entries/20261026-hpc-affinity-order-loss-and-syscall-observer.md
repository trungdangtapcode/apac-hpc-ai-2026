# 26 October: close launcher syntax changes and identify the affinity caller

## Prior question and experiment

The partial method-3 pre-exec failure did not show which actor widened affinity. Actual installation inspection also found mpirun is a symlink to PALS mpiexec 1.1.6. Job 25999546 instead compared bare, global-binding and command-specific-binding syntax under method 0. Each arm collected plain Python entry, native entry before MPI_Init_thread(SINGLE), and native post-init records for all 512 ranks on four nodes. No mask-based abort or solver was included.

## Findings and limits

All six commands returned zero, and PBS ended F / Exit 0 in 13 seconds. Each phase has 128 records on each of four hosts. Every Python and native pre-init mask contains one CPU; every post-init mask contains CPUs 0–255. Rank and hostname association is complete. Actual MPI world rank and PMI rank form a bijection but are mostly nonidentity; never substitute launcher PMI rank for MPI world rank in placement proofs. Physical-core topology was not collected.

The archive holds 4,630 hash-verified records, plus separately verified PBS stdout with three world-size-512 / zero-capture-error summaries. An initial per-file Python pack timed out; native tar retained the complete records. Runtime environment and compiled binaries were excluded. This diagnostic establishes a repeatable before/after observation, not MPI_Init as the sole global cause or an OpenFOAM speedup. Close unchanged option-placement tests. [Full replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-launcher-order-20261026/completed-25999546/RESULTS.md).

## Next hypothesis and admission

The [Linux affinity manual](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html) defines affinity per thread. The [official strace project](https://strace.io/) describes observing syscalls through ptrace. A bounded trace can identify which observed thread or library requests a changed mask, rather than guessing another undocumented environment variable. Installed strace 5.18 advertises libdw stack traces; the job verifies compute-node support again.

Job **26004608.pbs101** compares an untraced method-0 512-rank control with the identical probe while tracing only the process selected by PMI_RANK=0 and its descendants. The actual MPI world-rank record remains separate. Trace only sched_getaffinity and sched_setaffinity with stacks; do not attach to unrelated processes, mutate affinity or record a full environment. External actors outside that subtree may remain invisible, so absence of a syscall does not prove no external change. The observer may perturb startup and is never a ranked solver measurement.

The first admission check stopped before qsub because the completed review had no explicit passed field. The replay now writes that field after all assertions, was rerun, and admission succeeded once. The old payloads stayed frozen. Source checks, receipt and maximum reservation are preserved. At the retained 13:01 UTC check, the job was Q/q5 for node_pool. [Frozen observer and actual receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-affinity-strace-20261026/STATUS.md).

## Cost and next decision

The completed diagnostic estimates 1.848888889 SU at the verified rate. Only its maximum reservation was retired; a rounded two-SU allowance was added. Older unknown maxima remain. The new observer reserves 42.666667 SU for four nodes / 512 CPUs / five minutes. No individual posted bill is claimed and the AI project is unchanged. Inspect the trace and runtime linkage before another binding hypothesis. Never weaken actual world-rank, field, numerical-work or topology gates to count a failed qualification as a completed solver.
