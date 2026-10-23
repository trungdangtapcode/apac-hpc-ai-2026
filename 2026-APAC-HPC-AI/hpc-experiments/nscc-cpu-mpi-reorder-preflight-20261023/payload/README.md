# Four-rank Cray MPICH reorder interface preflight

This payload is a bounded MPI interface check only. It contains one small C program, validators, hash checking, and a PBS script. It does not contain an OpenFOAM case, mesh, solver, GPU code, or hardware profiler.

## Submission contract

Submit from the experiment root so PBS sets `PBS_O_WORKDIR` to this directory. The parent worker must submit only after the existing CPU confirmation job has ended, using an `afterany` dependency and its active-job/budget lock. The intended submission is:

```sh
qsub -W depend=afterany:25940700 payload/mpi-reorder-preflight.pbs
```

The job requests the normal queue, CPU project 59000042, one shared node, four CPUs and four MPI processes, 4 GB, no GPU, and three minutes. It starts a new `runs/<numeric-job-id>/` tree. The internal deadline is 135 seconds, leaving 45 seconds before the PBS wall limit for cleanup and source-hash verification. A failed preflight is retained and is not retried automatically.

## What the job checks

After loading `openfoam/2512`, it records the loaded modules, compiler version, PALS launcher version output, and selected linked MPI library paths. It compiles `mpi-probe.c` on the allocated compute node with `cc`, then launches the same four-rank probe twice through the same `mpiexec -n 4` PALS command:

1. Control rank order file: `0,1,2,3`.
2. Candidate rank order file: `0,2,1,3`.

Both runs set `MPICH_RANK_REORDER_METHOD=3`, `MPICH_RANK_REORDER_FILE=rank-order.txt`, and `MPICH_RANK_REORDER_DISPLAY=1`; both use the identical documented PALS `mpiexec -n 4 --cpu-bind thread` command. The job also sets `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, and `OPENBLAS_NUM_THREADS=1` before environment capture and both runs. Each run has its own working directory and rank-order file. The rank zero entry remains first. The files use the custom order format documented in the reviewed Cray MPICH interface manual.

Each rank emits its actual `MPI_Comm_rank`, `MPI_Comm_size`, `MPI_Get_processor_name`, Linux `sched_getaffinity` CPU mask, and optional `PMI_RANK` diagnostic. The validator uses MPI world rank as the authority, confirms four unique ranks and one allocated host, reads package/core IDs from Linux sysfs, and requires four unique physical cores in both runs. It then checks candidate MPI rank `r` against identity control slot `order.index(r)`, including host and logical CPU identity. It does not trust `PMI_RANK` for mapping.

The payload hashes its source files before and after the run. Every external command is bounded by the internal deadline, timed, recorded with a return code, and marked in `phases.tsv`. Module setup is performed without Bash `nounset` because site module scripts may inspect optional unset variables; required PBS and OpenFOAM variables are checked explicitly.

## Output review

Review `batch-lifecycle.json`, `command-return-codes.json`, `phases.tsv`, `pbs-nodefile.txt`, `environment.log`, `module-list.txt`, compiler and PALS version logs, linker output, both rank-order files, both probe stdout/stderr files, per-command resource logs, `mapping-validation.json`, and before/after source-hash reports.

The lifecycle record is wrapper evidence, not terminal PBS accounting. An accepted preflight establishes only that this four-rank Cray MPICH/PALS interface and observed single-node rank/core mapping work for this request. It does not establish four-host placement, any 512-rank mapping, solver behavior, graph-cut benefit, performance, or a contest score. Review the terminal PBS record separately. Keep the result or failure as evidence; do not automatically launch a larger run.
