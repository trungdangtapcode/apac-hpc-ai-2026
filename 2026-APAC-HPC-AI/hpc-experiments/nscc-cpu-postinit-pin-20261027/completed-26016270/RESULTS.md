# NSCC post-init pin qualification: job 26016270

## Question and controls

The prior 512-rank diagnostics observed per-rank affinity masks expand during MPI initialization, but did not establish that a chosen post-init binding could remain stable. This short diagnostic asked whether one allowed logical CPU per physical core, selected from each host's observed post-init mask and validated sysfs topology, could remain pinned on each MPI main thread through collectives and a two-second wait.

Job **26016270.pbs101** ran two arms on the same four-node allocation: the existing native MPI initialization probe as a baseline, then the native post-init pin probe. Both used 512 ranks, `MPICH_RANK_REORDER_METHOD=0`, with `PALS_CPU_BIND`, `MPICH_RANK_ORDER`, and `MPICH_RANK_REORDER_FILE` unset. `LD_PRELOAD` was empty. No OpenFOAM solver or Pstream interposition ran.

## Verified result

The fresh PBS history query was collected at **2026-10-27 04:52:30 UTC** from `asp2a-login-nscc01`. It reports state F, exit 0, project 59000042, four exclusive scattered nodes, 512 CPUs, no GPUs, and 17 seconds walltime against the five-minute request. The saved query JSON has `Variable_List` and environment fields removed before it was written. The failed-query fallback remains supported in the collector and accepts either an `utc` or `observed_at_utc` timestamp.

The baseline retained 512 native pre-init and 512 post-init records. Every pre-init mask was a singleton; every post-init mask contained logical CPU IDs 0–255. The candidate retained all 512 rank records and four per-host topology maps. Each shared-memory group had 128 ranks, with four processor names and 128 ranks per host. The local rank sequence matched ascending world rank within each host. The world-rank-to-PMI-rank crosswalk matched the baseline and was nonidentity for 510 of 512 ranks.

On every host, the rank-zero topology map covered all 256 online CPUs allowed after MPI initialization. Replay independently recomputed the 128 selected slots from each complete sysfs map. Every host reported two packages and 128 unique physical cores; its eight NUMA nodes each mapped 16 physical cores and 32 logical CPUs. Selection chose CPU IDs 0–127, one lowest allowed logical CPU per physical core, sorted by package and core. All selected CPUs were in each process's own observed post-init allowed mask.

All 512 calls to `sched_setaffinity(0, ...)` returned success. For every rank, the immediate mask, post-allreduce mask, post-two-second mask, and post-final-allreduce mask all remained exactly the selected singleton CPU. Sleep elapsed time ranged from **2.000073363 to 2.000999951 seconds**. Preflight, immediate-audit, post-wait-audit, and record-write global error counts were all zero. The baseline and candidate summaries each reported world size 512 and zero capture/identity errors.

All 18 worker command return codes were zero. The worker and after-run source-hash gate returned zero, and all six deployed payload files passed identical before/after `sha256sum` checks. Both probes compiled without warnings in the job. The recorded OpenFOAM 2512 native `libPstream.so` path resolves to Cray MPICH 8.1.15; both probe executables also link to that MPICH version. This verifies the runtime linkage used by the diagnostic, not an OpenFOAM solve or Pstream interposition.

## Resource evidence and limits

PBS reported 17 seconds walltime, 6 minutes 2 seconds CPU time, 13,937,880 KB memory, 93,899,968 KB virtual memory, and `cpupercent=7944`. These are scheduler accounting fields. `/usr/bin/time -v` recorded 2.59 seconds and 8,616 KiB maximum RSS for the baseline `mpiexec` wrapper tree; the pin arm recorded 4.75 seconds and 8,280 KiB. The pin arm intentionally waits two seconds, and these wrapper measurements are not comparable solver timings or per-rank hardware telemetry. No sampled CPU/GPU utilization was collected. At the requested CPU-hour rate of 1, 512 CPUs × 17 seconds / 3600 gives a **2.417778 SU walltime estimate**, not a posted-charge claim; the full five-minute reservation maximum was 42.666667 SU.

The result qualifies the candidate's calling-thread binding mechanism for this observed four-host topology. Linux `sched_setaffinity` with pid zero binds the calling thread, so MPI helper and progress-thread masks remain untested. There is no solver, performance, accuracy, or official-score result.

## Next distinct hypothesis

A separate bounded application-level PMPI adapter test can ask whether the same post-init selection can be applied at the actual OpenFOAM MPI initialization boundary while preserving native Pstream initialization and rank identity. Begin with a short solver-free Pstream initialization check; include explicit helper-thread limits. This run does not deploy or test that adapter.

## Replay and retained evidence

Run `python3 review.py` from this directory. It checks the native tar against the per-member byte/SHA-256 manifest, validates both 512-rank arms and all four topology maps, recomputes selected slots, checks phase masks and return codes, confirms the sanitized fresh PBS response and native MPI/Pstream linkage, then regenerates `review.json`. The archive contains 1,569 files (1,609,012 uncompressed bytes) and is retained as one compressed tar without an extracted per-rank file tree. Compiled probe binaries were excluded before transfer.

## Additional matched entry-placement check

Joining the candidate targets to the baseline's pre-init records by PMI rank and host gives **512 of 512 identical singleton CPU choices**, with zero differences. In this allocation the deterministic physical-slot selection restores the baseline entry placement, rather than adding a new rank-to-core permutation. The helper derives targets from validated topology and actual local rank, so it does not depend on capturing an entry singleton on every process. Future application runs must still preserve and inspect their own mappings; this equality cannot be assumed globally. `placement-difference.json` retains the comparison.

A logical CPU is an operating-system scheduling target. The retained topology shows 256 logical CPUs representing 128 physical cores on each host. The candidate selects one logical sibling from each physical core, so all 128 ranks on that host have distinct physical cores. This is a verified placement property, not a measured solver-speed result.
