# Preflight bundle qualification

## Prepared state

The four-rank preflight payload, validators, PBS script, source-hash manifest, plan, and qualification record are prepared. No MPI compile or launch, SSH, PBS query, qsub, budget change, mesh access, or OpenFOAM solve was performed in this preparation task. Submission is owned by the root worker and must use `afterany:25940700` after current queue and budget checks.

## Offline checks

- PBS Bash syntax and Python 3.6 grammar parsing are recorded in `qualification.json`.
- The source-hash verifier covers the payload inputs and validates both before and after the future job.
- Both future probe arms use identical `mpiexec -n 4 --cpu-bind thread` options and fixed `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, and `OPENBLAS_NUM_THREADS=1`; these controls make the single-logical-CPU affinity requirement explicit.
- Synthetic positive and negative fixtures exercise the MPI-rank mapping rule, unique physical-core guard, duplicate-rank guard, and four-slot nodefile guard. The fixture records are explicitly synthetic; their CPU IDs are read from this local host's sysfs, not from ASPIRE.
- The local machine has `cc` but no `mpicc` or MPI headers. Therefore `mpi-probe.c` was not compiled locally and its compile result is pending the allocated node.
- The deployed target's earlier manual review recorded Cray MPICH 8.1.15, PALS 1.1.6, method 3, and `MPICH_RANK_REORDER_FILE`; it launched zero MPI processes. The PBS payload captures the runtime module list, compiler version, launcher version output, and linked MPI library paths for the actual job.

## Runtime qualification still required

Review the final PBS exit and accounting, source hash reports, both command return codes, module/compiler/launcher/library evidence, actual `MPI_Comm_rank` records, nodefile, CPU affinity, sysfs physical-core map, and validator output. If the candidate mapping fails, preserve the failure and stop this branch. A pass is only an interface preflight; it is not evidence of four-node placement, solver performance, speedup, or score.
