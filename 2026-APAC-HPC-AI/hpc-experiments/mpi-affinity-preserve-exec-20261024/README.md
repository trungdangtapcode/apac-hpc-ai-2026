# Exec-time affinity capture and optional PMPI restoration

This is a separate, unqualified diagnostic path for a future approved cluster
test. It does not modify the earlier shim or any sealed payload. It was created
after matrix 25957267 showed that the affinity observed inside the MPI wrapper
before `MPI_Init` could already be wider than the singleton mask the application
observed before MPI initialization.

## Launcher wrapper

`capture-affinity-exec.py` captures `os.sched_getaffinity(0)` in the launched
rank before it executes the MPI application. It refuses to execute unless the
mask contains exactly one CPU. It records the launcher PID, `PMI_RANK`, captured
CPU list, best-effort package/core/NUMA metadata, application path, and shim path
in one bounded JSON line on stderr. It stores the captured CPU as the decimal
environment variable `APAC_LAUNCH_CPU`.

The wrapper requires an absolute, readable shared-library path and a resolvable
executable application. It refuses a nonempty inherited `LD_PRELOAD`, then sets
`LD_PRELOAD` to the selected shim only in the environment passed to the
application's `execve`. The launcher process itself runs without the selected
preload. Example shape, only after the shared object is built and a bounded
diagnostic is approved:

```sh
mpiexec ... python3 /absolute/path/capture-affinity-exec.py \
  --library /absolute/path/preserve-affinity.so -- /absolute/path/application args...
```

The helper is a per-rank executable wrapper and relies on the launcher exporting
`PMI_RANK` to the rank process. The emitted record makes missing rank metadata
visible as JSON `null`; it does not invent a rank number.

## MPI shim

The C shared-library source wraps `MPI_Init` and `MPI_Init_thread` through their
profiling counterparts `PMPI_Init` and `PMPI_Init_thread`. It is inert unless
`APAC_PRESERVE_AFFINITY=1`. When enabled, it requires `APAC_LAUNCH_CPU` to be a
strict decimal CPU index within `CPU_SETSIZE`; a missing or malformed value
terminates before MPI initialization. It records the contemporaneous mask just
before the PMPI call, separately from the exec-time captured CPU. After
successful initialization, it sets the calling thread to exactly the captured
CPU and rereads affinity to verify a singleton mask containing that CPU. It
does not select a CPU from a widened mask or infer a replacement.

The bounded `APAC_AFFINITY_JSON` record includes the world rank from
`PMPI_Comm_rank`, captured CPU, pre-init mask, post-init mask, verified restored
mask, syscall results, and outcome. On failed proof it logs then calls
`PMPI_Abort`, exiting with status 127 if that call returns. A failed PMPI init
return is propagated unchanged. The shim only addresses the thread that calls
MPI initialization; it does not bind MPI helper threads or make a claim about
process-wide affinity. The `cpu_set_t`/`CPU_SETSIZE` representation is a stated
limit.

The MPI Forum profiling interface provides the `MPI_`/`PMPI_` interception
model ([MPI-4.1, Section 15.2](https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report.pdf)).
That interface does not establish that post-init affinity changes are safe for
every MPI implementation. This shim has not been built against Cray MPICH and
is not a production fix. Actual Cray MPI behavior, OpenFOAM compatibility, and
all-rank mapping remain unverified.

## Local synthetic test

Run `python3 test_stub.py` with a Linux C compiler. The C test substitutes mock
affinity calls and synthetic PMPI routines. It covers both initialization
entry points, including a shim pre-init mask already widened while the
exec-captured CPU remains singleton; successful restore; missing, malformed,
negative and out-of-range captured CPU; restore and verification failures; and
failed PMPI initialization. The launcher tests cover successful environment
handoff when the local CPU mask is singleton, rejection of non-singleton masks,
and rejection of a nonempty inherited `LD_PRELOAD`.

These local tests do not use Cray MPICH, PALS, a scheduler, or an allocation.
No cluster build, job submission, solver run, budget change, or production
qualification is authorized by this artifact. Root review and a separately
authorized bounded compute-node test are still required. If used later, build
the shared object only in an approved compute allocation and preload it only
into the application rank, never `mpiexec`.
