# NSCC OpenFOAM Pstream late-pin adapter qualification

## State and admission gate

This directory is a **local, conditional preparation only**. It has not been sealed, root-reviewed, deployed, submitted, or run on NSCC. It contains no placeholder deployment record or `ROOT_REVIEW.json`.

The sole prerequisite is the independent passed review of native qualification job **26016270.pbs101** at [the retained review](../nscc-cpu-postinit-pin-20261027/completed-26016270/review.json). That review now passes: all 512 native probe main threads retained their selected singleton target through immediate, collective, delayed, and final checks; all four hosts exposed 256 allowed online CPUs and 128 physical cores; the probe and `libPstream.so` resolved to Cray MPICH 8.1.15. This prerequisite qualifies the native probe mechanism only. It does not qualify MPI interposition, OpenFOAM Pstream startup, a solver, or performance.

Any later admission still requires the current owner/root review and the established serialized CPU-then-AI admission checks: both live queues and the combined cap of three, fresh `myprojects -p 59000042` rate and balance, current CPU ceiling, both locks, and a durable uncertain reservation before `qsub`. The historical terminal query in the parent review is not fresh queue or budget evidence. This preparation did not run those checks or take either lock.

## Question and controlled arms

Can a PMPI adapter apply the previously qualified post-initialization main-thread placement when actual OpenFOAM `checkMesh -parallel` enters Cray MPICH through Pstream, then preserve that target until immediately before `PMPI_Finalize`?

One four-node, 512-CPU allocation is prepared for three sequential controls:

1. The unchanged native MPI initialization probe without an adapter.
2. The same native probe with the adapter preloaded only in the per-rank target executable.
3. The installed OpenFOAM 2512 `checkMesh -parallel` on a fresh synthetic mesh, with the same adapter.

All arms reapply `OMP_NUM_THREADS=1` and `MPICH_RANK_REORDER_METHOD=0` after OpenFOAM module setup; `PALS_CPU_BIND`, `MPICH_RANK_ORDER`, `MPICH_RANK_REORDER_FILE`, inherited `LD_PRELOAD`, and inherited adapter audit paths are cleared or rejected. The PMPI adapter reads only its whitelisted `NSCC_LATEPIN_AUDIT_DIR` and `PMI_RANK` values. Each MPI task receives a newly created mode-0700 audit directory beneath its own run's `adapter-ranks/rank-<PMI_RANK>` directory. The `rank-exec.sh` shim sets `LD_PRELOAD` with `env` only at the final `exec` of the target application; neither `mpiexec` nor the shim process inherits it.

The adapter interposes both `MPI_Init_thread` and `MPI_Init`, protects against nested or repeated initialization, and calls the matching `PMPI_*` initializer exactly once. It takes the entry affinity snapshot before that PMPI call and never calls MPI before initialization succeeds. After initialization it uses the real world communicator and `MPI_Comm_split_type(MPI_COMM_TYPE_SHARED)` with world rank as the local ordering key. Rank zero in each shared group reads and validates the online CPUs in its post-init mask against sysfs, requires exactly 128 physical `(package, core)` pairs with one NUMA node per physical core, and chooses the lowest allowed logical CPU for each pair. It broadcasts the complete CPU map and ordered target slots to its local peers. Every rank checks its own target against its own post-init mask and topology before pinning only the calling thread.

Each adapted rank records the hook name, requested and provided thread levels, return status, world/PMI/local rank, processor name, target CPU and physical package/core/NUMA coordinates, entry/post-init/after-pin masks, and a complete topology map with the map-source rank. The `MPI_Finalize` wrapper snapshots and collectively audits the main-thread target immediately before calling `PMPI_Finalize`; this pre-finalize log truthfully leaves the not-yet-observable return code null. After `PMPI_Finalize` returns, it writes a separate `finalize-return.json` with the actual return code using only OS-level file I/O and saved rank identities; it makes no MPI call after finalization. The finalize collective uses only `MPI_COMM_WORLD`, `MPI_INT`, and `MPI_SUM`; it does not rely on OpenFOAM-owned communicators or custom datatypes that Pstream may already have freed.

The installed OpenFOAM 2512 source inspection reported by root found Pstream initialization calling `MPI_Init_thread` with both null argument pointers in the no-argument path, and with the application argument pointers in the other path; both request `MPI_THREAD_SINGLE`. This wrapper passes the pointers unchanged and does not dereference them. Pstream imports `MPI_Init_thread` and `MPI_Finalize`, rather than `MPI_Init`. Root will retain the actual source/library inspection with the reviewed run package; this local preparation does not copy the external inspection artifact.

## Synthetic diagnostic case and runtime caps

The third arm uses only the fresh unit-cube `blockMeshDict` in this payload: 32 × 16 × 16 = 8,192 hex cells, then simple decomposition `(8 8 8)` into 512 tiny partitions with `decomposePar -force -noFields`. It contains no contest mesh, fields, solver, or organizer case. `checkMesh -parallel` must return zero and print both `Mesh OK.` and `End` for the collection to pass.

`payload/nscc-cpu-pstream-latepin.pbs` requests four exclusive scattered nodes, 128 CPUs/ranks per node, no GPUs, and ten minutes. The PBS maximum at the verified one SU per CPU-hour rate is **85.333333 SU** (512 × 600 / 3600); this is a reservation maximum, not a charge or authorization. An outer 575-second timeout leaves a 25-second PBS margin. The worker has a 555-second global deadline and separate phase caps: module setup 45 seconds, native compile 30 seconds, adapter compile 45 seconds, `blockMesh` 20 seconds, `decomposePar` 60 seconds, then arm caps of 30, 60, and 90 seconds. Other ldd/help and hashing steps are individually limited as well. Each timed phase retains its exact argument vector, return code, wall/resource record, stdout, stderr, and phase timestamps. Any nonzero target-arm status fails the worker even though later arms still run to preserve diagnostic evidence.

Before and after execution the worker hashes all payload source files, the native MPI/Pstream dependencies resolved by `ldd`, the native probe, checkMesh, and the adapter. No runtime binary is written into the payload. Collection or review must reject any mismatch.

## Validation and acceptance

`payload/offline/fixtures.py` builds a synthetic positive tree containing 512 ranks per arm, four hosts, two logical siblings per physical core, a nonidentity world/PMI mapping, and separated per-rank work roots. It also exercises negative gates for an after-pin mismatch, a missing finalize audit, missing `Mesh OK`, a nonzero target command status, and a runtime hash mismatch. These are replay fixtures only; they are not site measurements.

The shim at `payload/offline/include/mpi.h` is deliberately declaration-only. It supports a strict local C syntax/warning check with `-Wall -Wextra -Werror`; it is not a Cray MPICH ABI build or runtime test. The actual allocation must compile the adapter with `cc -shared -fPIC -Wall -Wextra -Werror -pthread` linked to the exact `libmpi` path resolved from Pstream’s `ldd` output (rather than a generic `-lmpi` search), capture `ldd` for the adapter, native probe, `checkMesh`, and Pstream, and require `/mpich/8.1.15/` in all four dependency traces.

Run replay only on a complete collected run directory:

```sh
python3 review.py /path/to/run --output /path/to/review.json
python3 payload/offline/fixtures.py
```

The reviewer requires 512 unique world ranks and PMI ranks in each adapted arm; four hosts with 128 local ranks each; each rank's target inside its own post-init mask; an independently recomputed 128-core topology selection; singleton after-pin and pre-finalize masks on all 512 main threads; complete per-rank init/pre-finalize/post-finalize audits, including actual `PMPI_Finalize` return codes; zero collective failures; complete checkMesh markers; all required commands successful; unchanged payload/runtime hashes; and resource/phase evidence. It joins each adapted target to the no-adapter baseline by `(host, PMI_RANK)` and reports how many match the baseline entry singleton. It does not assume world rank equals PMI rank or that a future mapping will match this observed baseline.

A passing result qualifies only the PMPI startup/finalize interface and this tiny `checkMesh` Pstream path on the observed allocation. It does not test full-solver startup or benefit, MPI helper/progress-thread masks, NIC placement, memory locality, numerical correctness, solver speed, or a contest score. The thread pin applies to the calling main thread only. Any future derived solver bundle must preserve its own frozen payload and pass separate review.

## Root review and actual installed interface

The actual v2512 Pstream source and dynamic-library symbols were read on NSCC. The source uses MPI_Init_thread for its normal and null-argument paths and MPI_Finalize during shutdown; the binary imports those symbols. `pstream-entry-inspection.json` retains source line numbers and SHA-256. The Cray compiler wrapper prints `-lmpi_gnu_91` itself, not generic `-lmpi`; the worker links the exact MPI shared library resolved from the installed Pstream and verifies it again. Source availability and symbols justify the integration test but do not replace actual rank audits.

Root review added a collective preflight before any setter, persistent runtime paths and safe watchdog cleanup, exact frozen payload checks before/after execution, actual post-PMPI_Finalize return records, and real OpenFOAM version/precision/rank/cell-count checks in replay. The native-record parser was tested against 1,024 records from the real passing parent, correcting a synthetic-only world_size field assumption. A local declaration-header failure was corrected before deployment; its earlier seal/header are retained under `pre-integration/`. The declaration shim is used only for local syntax checks, never by the compute compiler. The diagnostic case now includes minimal fvSchemes and fvSolution dictionaries; the official DrivAer case is untouched.

A future full solver comparison remains conditional on this integration gate. The reference solver took 549.16 seconds for 150 steps and 1,133.66 seconds for its whole wrapper; four solver arms alone therefore suggest about 36.6 minutes, not a promised 90-minute completion. Four ABBA arms should share one fully initialized source but use independent clones and identical fixed 150-step work. The retained 43-file/300KiB source-case observation and seven-second initial copy do **not** bound those initialized clones, which also contain processor mesh and fields. Clone and hashing costs remain unmeasured for that full design; measure them rather than assuming tiny copies. Do not reuse the old unqualified entry-capture shim or graph permutation in an identity-pin comparison.

Primary API references: [MPI profiling-interface requirements](https://www.mpi-forum.org/docs/mpi-1.1/mpi-11-html/node153.html) and [MPI-3.1 initialization/thread support](https://www.mpi-forum.org/docs/mpi-3.1/mpi31-report/node303.htm). The latter permits null argc/argv pointers; optional arguments are forwarded unchanged. All timing and placement statements about NSCC above come from retained local evidence.
