# 512-rank placement preflight qualification

## Prepared state

The conditional PBS payload and the refined assignment with source pins are prepared. The job is not submitted. It must remain behind `afterok` dependencies on both CPU jobs `25940700` and `25943865`, and root owns all live queue/budget checks, reservation, active-cap and submission work.

## Offline checks

- Source hashes cover every fixed payload file and the hash verifier passes locally; the PBS job repeats this check before and after execution.
- Bash syntax and Python 3.6 grammar checks pass for the execution script and helpers.
- Synthetic fixtures randomize the identity ranks over four hosts and eight NUMA domains, then render and validate all 512 candidate slots. This specifically exercises a noncontiguous control slot order and does not claim anything about ASPIRE topology.
- Negative fixtures reject an identity host with the wrong NUMA-domain rank count, a duplicate/missing MPI rank, a wrong physical core, a wrong host, and a wrong NUMA domain.
- Both arms use identical `mpiexec -n 512 --cpu-bind thread`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, and `FI_OFI_RXM_USE_SRX=0`; the job captures remaining FI settings at module/site defaults.
- Local `mpicc` and `mpi.h` are unavailable, so the C probe was not compiled locally. No real MPI process or allocation was launched.
- The retained target interface review identifies Cray MPICH 8.1.15, PALS 1.1.6, and method 3, but launched zero MPI processes. The runtime job captures the actual module, compiler, launcher, and linked-library evidence.

## Runtime evidence still required

Review the terminal PBS state/accounting, source-hash reports, full 4x128 identity topology, all eight actual 16-rank NUMA domains on each host, generated identity-slot rank-order file, all 512 candidate world-rank host/core/NUMA matches, thread and FI controls, module/compiler/launcher/library versions, per-command returns, and both complete arm logs. A pass is allocation-specific placement qualification only. It does not establish solver behavior, memory-page locality, performance or score.
