# PALS CPU binding option placement diagnostic

## Question and evidence

The `mpirun` executable was verified on 26 October to be a symlink to the same
PALS `mpiexec` 1.1.6 executable. Earlier 512-rank probes showed broadening of
rank affinity. The failed 25957725 pre-exec wrapper retained 128 singleton
observations, 17 broad-mask rejections and 367 absent records before MPI, but did not produce a
complete MPI-initialization audit; that result cannot be attributed to MPI
alone. This diagnostic isolates launcher option placement and the bare
launcher while keeping the MPI identity method constant.

## Frozen design

Request four nodes, 128 CPUs per node, 128 MPI processes per node, 32 GB per
node, scatter/exclusive placement, CPU project 59000042, normal queue, and five
minutes. The script enforces a 255-second internal deadline. Each Python
capture phase and native MPI phase has an independent 20-second timeout. Each
command records its exit status and the next phase proceeds after failures.

The three arms run in this order:

1. `mpiexec -n 512`
2. `mpiexec --cpu-bind thread -n 512` (deprecated/global placement)
3. `mpiexec -n 512 --cpu-bind thread` (command-specific placement)

Every arm first launches a plain Python process that writes its own
`PMI_RANK`-named JSON observation of rank, host and entry affinity. Then a
separate native C program records affinity immediately before and after
`MPI_Init_thread(MPI_THREAD_SINGLE)`, host, PMI rank and MPI rank. It does not
reject any mask or perform topology lookups. It completes a collective summary
and calls `MPI_Finalize` when MPI initialization succeeds. Per-rank files use
exclusive creation, so duplicate ranks remain visible as errors. Affinity
snapshots contain all CPU indexes through the platform's `CPU_SETSIZE`; an
explicit status/error field is retained if a snapshot fails.

All arms set `MPICH_RANK_REORDER_METHOD=0` and unset `PALS_CPU_BIND`,
`MPICH_RANK_ORDER`, and `MPICH_RANK_REORDER_FILE`. The script logs only a
whitelist of runtime variables, never the complete environment. It preserves
the raw PBS node file, phase timestamps, per-command return codes, stdout,
stderr and `/usr/bin/time -v` resource reports. It writes pre-run and post-run
SHA-256 manifests for the frozen payload. No solver, numerical workload,
exec wrapper, `LD_PRELOAD` shim, rank-affinity gate or performance conclusion
is included.

This is pure collection, not binding qualification. Launcher failures,
missing rank files or timeouts are data and do not stop later arms. Module setup and pinned-source failures stop the job. A successful
run only reports what these three command forms did on that allocation; it
cannot establish solver placement or performance.

## Verification status

Source syntax and shell parsing are checked locally. No cluster execution or
site-module compatibility is claimed here. The diagnostic must be submitted
only through the separately reviewed deployment driver and existing CPU
authorization workflow.
