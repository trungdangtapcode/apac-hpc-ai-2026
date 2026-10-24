# Optional PMPI affinity-preservation shim

This directory contains an unqualified diagnostic shim for a future, explicitly
approved cluster experiment. It is not a production fix and has not been built
against Cray MPICH or run on a compute allocation.

The shim wraps the C `MPI_Init` and `MPI_Init_thread` profiling entry points and
calls their corresponding `PMPI_` routines. It is inert unless
`APAC_PRESERVE_AFFINITY=1`; an unset or other value leaves initialization
unmodified. When enabled, it snapshots the calling thread's Linux affinity before
MPI initialization. After successful initialization it requires that the saved
mask contain exactly one CPU, reads the post-init mask, sets the calling thread
back to the exact saved mask, and verifies the restored mask by rereading it.
Any failed precondition or failed restoration proof emits one bounded JSON line
and calls `PMPI_Abort`; if that returns, the process exits with status 127. A
failed `PMPI_Init*` return is propagated unchanged without post-init calls.

The diagnostic reports the world rank from `PMPI_Comm_rank` plus the pre-init,
post-init, and verified restored CPU lists and syscall statuses. CPU lists are
bounded; the truncation fields indicate when a list exceeds the line budget.
The shim only restores the thread that called MPI initialization. It does not
bind MPI helper threads or establish a general process-wide affinity policy.
The implementation uses `cpu_set_t` and `CPU_SETSIZE`, so CPU IDs outside the
platform's fixed set representation are outside this diagnostic's current
scope.

The MPI Forum profiling interface supplies the `MPI_`/`PMPI_` interception
model used here: [MPI-4.1, Section 15.2](https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report.pdf)
and [MPI-1.1 Profiling Interface](https://www.mpi-forum.org/docs/mpi-1.1/mpi-11-html/node152.html).
Those specifications establish the profiling entry points; they do not promise
that changing affinity around initialization is safe for every MPI library.
Cray MPICH ABI behavior and OpenFOAM compatibility therefore still require
actual qualification.

## Local synthetic test

Run `python3 test_stub.py` on a Linux development host with a C compiler. The
test compiles against a tiny synthetic `mpi.h`, mocks affinity calls, and makes
the fake PMPI initialization widen the main-thread mask. It checks both MPI
initialization entry points, opt-in and pass-through behavior, empty and
multi-CPU source masks, restore failure, and a failed MPI initialization return.
It does not use a real MPI library, scheduler, cluster allocation, or remote
compiler.

For any later cluster qualification, build the shared object inside an approved
compute allocation with that allocation's compiler/MPI headers and libraries.
Set `LD_PRELOAD` only on the application launched by `mpiexec`, never on the
launcher. Keep the preservation opt-in explicit and first use a bounded MPI
diagnostic; do not launch the solver until the restored mask, all ranks, and
runtime behavior have been reviewed. No such cluster test or solver run is
authorized by this artifact.
