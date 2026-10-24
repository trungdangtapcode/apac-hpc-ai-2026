# MPI initialization expands the identity probe affinity

## Evidence and interpretation

All 40 collected files pass manifest hash/size checks. The diagnostic job **25956623** exits 1 after a two-minute allocation on four exclusive CPU nodes. Its **512 distinct MPI ranks** each report a one-CPU mask before MPI_Init and the full **0–255 CPU mask after MPI_Init**. The singleton gate therefore fails for every rank. Physical-core and NUMA lookups have status -99 (not attempted); this is not evidence that sysfs reads failed or that NUMA domains are absent.

No candidate mapping launches. This directly observes the derived probe and allocation; the earlier combined-error job lacked component records. The expansion is a concrete reproduced failure mode, but cannot be retroactively proven to be the sole cause of that earlier run. The four-rank successful shared allocation did not qualify this larger launch. It also does not establish that simpleFoam has the same post-init behavior: the baseline startup probe was Python and never called MPI_Init, so it proved only startup binding, as previously labeled.

The collective diagnostic emits TOPOLOGY_CHECK_FAILED ranks=512 and a rank exit14; MPI shutdown later reaches the launch timeout (command return143). The source payload remains sealed. This is a failed diagnostic, not a successful mapping or solver benchmark. Known terminal resources estimate 17.066667 SU at512 allocated cores×120seconds×rate1; this is not a posted charge.

## Next experiment

Consult the exact installed Cray MPICH/PALS documentation for a supported way to retain launcher binding through MPI initialization. Derive a separate bounded control/probe; retain before/after masks, actual MPI world ranks, local core/NUMA evidence and actual mapping. Do not weaken the singleton condition or treat the pre-init mask as post-init placement. Only after qualification should a solver A/B test compare identical launch settings except the rank-order file. Heavy profiling remains outside scored solver work. Preserve the failed run and timeout evidence.
