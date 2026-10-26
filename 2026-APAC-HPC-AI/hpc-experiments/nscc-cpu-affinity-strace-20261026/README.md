# Rank-zero affinity syscall trace

## Question

The 26 October launcher-order diagnostic completed as job 25999546 (Exit 0,
13 seconds). It retained 4,630 records: in all three launcher-option arms,
all 512 Python entry masks and all 512 native pre-`MPI_Init_thread` masks were
singletons, while every native post-init mask contained CPUs 0–255. All six
native arms returned zero across four hosts with 128 ranks per host. This
closes launcher option placement as an explanation for the observed widening.

This follow-up asks which calls made by the rank process coincide with the
mask change. It compares the same native MPI probe in an untraced control arm
and in an arm where only the process whose original `PMI_RANK` is zero execs
`strace -f -k -ttt`. The trace filters to `sched_setaffinity` and
`sched_getaffinity`, suppresses signal events, and writes to a rank-specific
file. No process is attached externally; there is no global trace, affinity
change, preload shim, MPI model, or solver.

The C probe is copied byte-for-byte from the launcher-order diagnostic. Both
arms use a 512-rank world, the same method-0 setting, identical module/runtime
setup, and `MPI_Init_thread(MPI_THREAD_SINGLE)`. The per-rank Python exec wrapper
records `PMI_RANK`, hostname, PID, and selected mode with exclusive file
creation, then execs either the probe or, for rank zero in the observed arm,
`strace` followed by the probe. The probe retains all 512 pre-init and post-init
JSON records. There is no mask-based abort.

## Resource and collection bounds

PBS requests four nodes, 128 CPUs and 128 MPI processes per node, 32 GB per
node, scatter/exclusive placement, CPU project 59000042, normal queue, and a
five-minute wall time. The worker has a 255-second shared deadline. Compilation
is capped at 45 seconds and each native arm at 45 seconds to allow for the
confirmed libdw stack-trace overhead. Failures and timeouts are retained; a
ptrace denial does not trigger an automatic retry. Phase timestamps, command
return codes, resource reports, the raw PBS node file, runtime version/help,
probe linkage and OpenFOAM Pstream library paths are collected. Only named
OMP/MPI reorder variables are recorded; the full environment is never dumped.

Before and after execution, the worker checks the reviewed
`payload-sha256.txt` manifest from the experiment root. The deployment owner
must seal that manifest for this payload before submission. This is an
observational diagnostic: strace changes execution overhead, only follows the
traced rank process and its descendants, and cannot reveal an external process
that changes another rank's affinity. Neither arm is a ranked timing result or
a performance claim.

## Local verification

The offline wrapper fixture uses temporary fake executables to check rank-zero
selection, untraced-rank selection, recorded mode/PID/host identity, and
duplicate-record rejection. Shell and Python syntax can be checked locally.
MPI compilation against the site headers and all cluster behavior remain
unverified until the separately reviewed job runs.

## Primary references and version limits

The official [strace project](https://strace.io/) describes syscall tracing through ptrace. The [Linux sched_setaffinity manual](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html) specifies that affinity belongs to a thread and that pid zero targets the caller. Therefore the trace must distinguish the native main thread, helper threads and external processes; a broad main-thread mask does not identify its caller by itself.

The actual installed login tool reports strace 5.18 with libdw stack traces. The job checks the compute-node tool again. The [HPE PALS guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00115110en_us&docLocale=en_US&page=Parallel_Application_Launch_Service_PALS.html) documents CPU-binding options; actual job 25999546 tested those syntaxes on installed PALS1.1.6 and found the same post-init widening for every arm. General documentation is not proof of this installation's runtime behavior.
