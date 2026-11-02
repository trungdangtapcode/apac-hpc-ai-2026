# Second review: preparation locality, MPI waiting, and allocator qualification

The new time series changes what we can say about memory. It does not yet identify the cause of the timing variation. The highest-value additional observation is **memory per NUMA node**, together with the preparation process's CPU and memory policy. Preserve the running diagnostic; do not add work to its later arms or change its frozen payload.

## What is newly measured

Partial capture at **3 November 2026, 02:25:40 Vietnam**, job 2294671 still active. S1 Scotch completed its 20 steps and the frozen runner reported 33.672468410 s/step. X1 xyz had only 11 measured intervals in the captured log, mean 25.421571143 s. These unequal horizons and missing repeats do not establish a speedup.

| Whole-node observation | S1, 142 samples / 705 s | X1, partial: 70 samples / 345 s |
|---|---:|---:|
| Lowest MemAvailable | 39.58 GiB | 41.44 GiB |
| Highest Active(anon) | 130.84 GiB | 130.62 GiB |
| Cached range | 6.46–36.26 GiB | 26.81–27.93 GiB |
| NUMA allocation miss counter increase | 66,718,152 | 38,689,049 |
| NUMA hint faults / local hint faults | 18,520,415 / 18,010,517 | 10,430,006 / 10,358,932 |
| Pages migrated counter increase | 220,368 | 17,219 |
| Swap-in / swap-out | 0 / 0 | 0 / 0 |
| Available CPU/memory/I/O pressure files | None | None |

The snapshot includes startup and process-exit boundaries. Earlier 162–168 GiB values were outside the solver, so they were not representative of its memory footprint. The active intervals still had roughly 40 GiB of aggregate available memory; this is not proof of machine-wide memory exhaustion. More reclaim appeared in the faster partial xyz arm, contradicting a simple explanation that reclaim always determines step speed.

Hint faults were mostly local in these observations. They sample the kernel's balancing mechanism; neither this ratio nor allocation-miss counts measures all application loads or proves bad NUMA placement. The per-socket distribution remains uncollected. These counters must not be converted into remote memory bandwidth.

Exact slow-step/reclaim alignment is not proven. The native log clock starts inside OpenFOAM, while sampler phase markers precede process launch; their origins differ. Without a qualified alignment, describe phase-level coexistence rather than claiming a particular five-second event caused a particular slow step.

The partial artifact retains all 13 file hashes and a replay script. Full Cd/field/source checks were performed by the frozen runner for S1 but are not all in this small partial capture. Independent complete-run review remains pending. [Partial evidence and replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xyz20-scotch-screen-20261103/partial-review-20261103-01/ANALYSIS.json).

## 1. Test whether preparation influences memory placement

**Hypothesis, not a finding:** serial copying and checksum verification may allocate file-cache pages disproportionately on the NUMA node where the preparation process runs. Subsequent solver ranks span both packages. This could make run order matter even though copied bytes and rank bindings match.

The Linux kernel documents that task memory policy can govern page-cache allocation and that interleave policy spreads newly allocated cache pages. Changing policy does not generally relocate pages already present. This supports the mechanism's plausibility, not its occurrence in this job. [Kernel NUMA policy](https://www.kernel.org/doc/html/latest/admin-guide/mm/numa_memory_policy.html).

**Qualification before a trial:** in a later derived bundle, record the preparation process's allowed CPUs/memory nodes and effective policy; read node0/node1 meminfo and numastat before/after copy, hash and solver phases; verify numactl availability and allowed memory nodes. Validate collection overhead. These are missing from the current frozen bundle.

**Controlled treatment to prepare if the imbalance appears:** keep native Scotch, 56 ranks, all source hashes, fields, MPI placement and numerical work fixed. Change only the memory policy of the copy/checksum child processes to interleave across the two allowed NUMA nodes. End that policy with those children so the solver does not inherit it. Use fresh isolated destination files for every arm. No global cache drop, forced page migration, system sysctl or source modification. Existing shared page cache can survive from earlier runs, so interleave is not a guarantee of a perfectly balanced cache.

Success needs evidence that the treatment actually changes node-level distribution **and** improves repeated solver timing. If placement does not change, the intervention is not qualified. If placement changes but timing does not improve or gets worse, reject the performance hypothesis. Preparation time and energy remain separate from the contest's solver timing metric.

## 2. Distinguish MPI waiting from useful computation

S1 reports 37,658.53 user CPU seconds and 1,471.93 system CPU seconds over 706.43 wall seconds, about 55.39 busy CPU equivalents. That does not establish a compute-bound solver. Open MPI documents that message-progress waiting can spin; inspect a representative MPI/profile breakdown before choosing communication knobs. [Open MPI 5 scheduling](https://docs.open-mpi.org/en/v5.0.5/launching-apps/scheduling.html).

A later diagnostic should distinguish local solver work, MPI communication/waiting and rank imbalance. Keep intrusive sampling outside the scored run and qualify the available tool, runtime interface and overhead first. Do not set mpi_yield_when_idle simply to reduce the CPU percentage: a lower busy percentage is not the objective and can slow progress.

The 48-versus-56 rank experiment remains a candidate, but it is no longer the automatic next submission. With a fixed 65M-cell mesh, fewer ranks give each rank more cells. Total cell-dependent memory does not fall in proportion to rank count; only some rank/halo/runtime overhead may shrink. It is a tradeoff to measure, not a memory-saving fact.

## 3. Qualify allocator behavior before changing it

Retained ldd/library hashes support glibc use, with LD_PRELOAD/LD_AUDIT unset in the saved environment. They do not identify all allocator internals or record inherited MALLOC_* / GLIBC_TUNABLES. The installed libc version and relevant effective settings require qualification on the compute environment.

A tentative fixed **1 MiB trim threshold is not admitted**. GNU documentation says the default trim threshold adapts dynamically; setting a fixed value disables that adaptation. Therefore 1 MiB is not necessarily larger than the effective default and could cause more trimming. Do not describe it as an eightfold increase relative to this solver's actual threshold. [GNU memory-allocation tunables](https://sourceware.org/glibc/manual/latest/html_node/Memory-Allocation-Tunables.html).

Before selecting a value, preserve an allowlist of relevant allocator settings, identify the actual libc build, and obtain overhead-qualified allocation/syscall evidence in a separate diagnostic. Choose one knob only after that evidence. Any treatment must retain sufficient per-node memory and pass native outputs. GNU page-fault counts alone do not establish malloc overhead; this branch remains a hypothesis, not a ready solver job.

## Execution decision

Job 2294671 occupies the one-owned-allocation cap. Its full 56 CPU-hour reservation stays in place; this partial observation retires no budget. Complete the current four arms and review both repeated controls before selecting a successor. The current packet prepares the next hypothesis and its qualification/stop criteria; it does not claim another deployed payload or scheduler ID.

The original report's rank-density-first ordering is historical. The new priority is preparation/NUMA qualification and a representative compute-versus-MPI breakdown, while retaining the rank-density option. Do not convert this into an unrestricted profiler project or parameter sweep: one concrete observation must select the next controlled test.
