# NSCC post-init main-thread pin qualification diagnostic

## Research question

The 26 October 512-rank diagnostics observed native masks expand to CPUs 0–255 after MPI initialization. The rank-zero trace identified a Cray MPICH `sched_getaffinity` query in its OFI NIC policy path, but no setter; the control also had an unexplained one-host pre-init mask exception. Those observations do not identify who changes the mask.

This proposed follow-up tests a different, bounded hypothesis: after MPI initialization, a native probe can choose one allowed logical CPU per validated physical core on each host and keep the probe's own MPI main thread on that CPU through collectives and a two-second wait, even when launcher-entry masks are unreliable. It has two 512-rank arms in one four-node allocation: the existing native initialization probe as a baseline and the new topology-gated pin probe. Neither arm runs OpenFOAM or another solver.

## Candidate behavior and fail-closed gates

The pin probe requests `MPI_THREAD_SINGLE`, records PMI identity and pre/post-init affinity, and builds an `MPI_COMM_TYPE_SHARED` communicator with world rank as its ordering key. It requires world size 512, four distinct processor names with 128 ranks each, local communicator size 128, and an exact match between shared groups and processor names. Only each shared-memory rank-zero process reads topology for CPUs in its post-init allowed mask. Every candidate must be online and have readable nonnegative package, core, and exactly one NUMA node mapping. The leader requires exactly 128 distinct physical `(package, core)` pairs, selects the lowest allowed logical CPU for each pair, sorts slots by `(package, core)`, writes a per-host complete CPU-to-sysfs map and selected slots, then broadcasts the CPU and topology tuple to local ranks. Offline replay recomputes selected slots from those retained maps.

Before any affinity change, every rank verifies its own selected CPU is in its own observed post-init affinity mask and is online; a global allreduce gates the change. Each rank then calls `sched_setaffinity(0, ...)` for its own calling thread only. The probe records the immediate mask, the mask after an allreduce, the mask after an absolute two-second monotonic wait, and the mask after a final allreduce. Any uncertain topology, allocation mismatch, syscall failure, or mask change is retained as failure and prevents a pin when the preflight gate has failed.

The key distinction is MPI local rank versus PMI rank: local rank comes from the shared communicator ordered by world rank. The record preserves both world and PMI rank. Both arms share the method-0 MPI reorder control used by the preceding native probe; the worker clears `PALS_CPU_BIND`, `MPICH_RANK_ORDER`, and `MPICH_RANK_REORDER_FILE`. It adds no CPU-binding launcher flag, `LD_PRELOAD`, OpenFOAM `libPstream` interposition, or solver.

## Limits

Linux `sched_setaffinity` with pid zero applies to the calling thread. This diagnostic therefore qualifies only the probe's MPI main thread. MPI helper or progress threads, solver runtime behavior, memory placement, and performance remain unqualified. A clean mask audit is a mechanism qualification, not evidence of a solver speedup or a production binding recommendation.

`MPI_Comm_split_type` groups processes that can create a shared-memory region; its key orders ranks within each resulting communicator. The code still checks processor-name counts and local size rather than assuming the scheduler layout. See the [MPI Forum MPI 3.1 communicator constructor specification](https://www.mpi-forum.org/docs/mpi-3.1/mpi31-report/node156.htm). Linux documents pid zero as the calling thread and notes that the effective affinity is restricted by online CPUs and cpuset permissions; this probe checks both before selecting a target. See [`sched_setaffinity(2)`](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html).

## Runtime and cost envelope

The PBS payload requests four exclusive scattered nodes, 128 CPUs and MPI processes per node, 32 GB per node, no GPUs, and five minutes. The worker deadline is 255 seconds, the outer timeout is 275 seconds, and each arm is capped at 60 seconds. The request maximum at 1 SU per CPU-hour is 512 × 300 / 3600 = **42.666667 SU**. A future admission requires a passed root review plus fresh CPU and AI queue checks, fresh project balance/rate, and the established serialized budget and combined-cap locks. This preparation has not queried a scheduler, deployed, reserved, or submitted anything.

## Validation and reproducibility

`payload/offline-fixtures.py` exercises synthetic 128-core topology selection, deterministic slot order and uniqueness, 512-rank identity/phase replay, and negative topology, target-mask, and stability cases. These fixtures do not claim anything about NSCC hardware. The local machine has no MPI compiler; `offline/include/mpi.h` is a narrow declaration shim used only for C syntax/warning checking, not an MPI ABI build or runtime qualification. A real Cray compiler/link/runtime check remains inside the future allocation.

`deploy_submit.py seal` creates the payload hash manifest locally. `ROOT_REVIEW.json` records the current offline evidence and exact source hashes. `collect_completed.py` is prepared to retain a native tar of only the eventual run records plus the explicit PBS stdout, excluding the compiled probe binaries; it records archive and per-member hashes. `review.py` replays the retained archive without extracting thousands of files.

## Root integration before any remote action

The active source preserves the prepared seal and PBS file in `pre-integration/`. Only a shutdown comment changed in the runtime payload before the final seal; the configured timeouts remain unchanged. Admission now records an unresolved ledger entry before qsub and updates that same entry after an unambiguous receipt. It also raises the conservative consumed allowance when the fresh shared-project usage requires it before checking the existing ceiling. These changes do not expand the CPU budget.

The probe binds the rank's calling main thread only. It neither adjusts existing MPI helper threads nor explicitly changes NIC selection. Mask stability is a qualification gate, not a prediction of solver speed. Primary references: [MPI-3.1 communicator constructors](https://www.mpi-forum.org/docs/mpi-3.1/mpi31-report/node156.htm) for shared-memory subcommunicators and key ordering; [Linux affinity semantics](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html) for calling-thread and cpuset limits. Actual Cray MPI compilation and behavior remain unverified until the allocation runs.
