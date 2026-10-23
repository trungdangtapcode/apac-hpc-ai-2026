# Four-rank MPI rank-reorder interface preflight

## Question and prior evidence

The retained four-node default-Scotch observation is 3.677906731 seconds per step at 512 ranks, but its independent confirmation remains a separate pending job. An offline graph screen kept the same 512-way partition and assigned its ranks to four logical groups of 128. The contiguous logical-host control crossed 337,324 processor-face entries; the candidate crossed 261,110, a 22.5937% lower graph-cut proxy. Root independently checked the arithmetic. This is not a runtime result or a speedup measurement. A cut proxy does not measure bytes, wait time, host topology, core binding, solver time, or numerical behavior.

The reviewed installed Cray MPICH 8.1.15 manual and PALS 1.1.6 interface review identify method 3 and `MPICH_RANK_REORDER_FILE` as the documented custom-order route. The retained interface review records no MPI processes launched. The purpose of this preflight is to verify actual `MPI_COMM_WORLD` rank-to-host/core behavior before preparing any larger candidate.

## Hypothesis and control

On one shared CPU node, method 3 with a custom order file can create the requested rank-to-slot permutation while retaining four distinct physical cores. The control order is `[0,1,2,3]`. The candidate order is `[0,2,1,3]`, with rank zero in the first position. Under the documented list semantics, candidate MPI rank `r` must land on the identity control slot `order.index(r)`. Both runs use the same four-rank PALS command, Cray MPICH module, display setting, binary, thread controls, and allocation; only the order-file contents differ. The identical command is `mpiexec -n 4 --cpu-bind thread`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, and `OPENBLAS_NUM_THREADS=1` are set before environment capture and both launches.

`MPI_Comm_rank` is authoritative. `PMI_RANK` is captured only for comparison and must not be used to infer reordered MPI world ranks. For each rank, the C probe reports the MPI world rank and size, processor name, CPU affinity mask, and optional PMI rank. The Python validator checks the PBS nodefile, one host, four ranks, one logical CPU per rank, four unique sysfs physical cores, and the expected control-slot mapping.

## Bounded execution and preservation

The PBS script requests one standard CPU node with four CPUs/four MPI processes, 4 GB, no GPU, normal queue, shared placement, and three minutes. It compiles on the compute node after loading `openfoam/2512`; it does not compile on a login node. The internal deadline is 135 seconds. The job creates separate `identity/` and `candidate/` run directories, stores complete logs and return codes, and verifies payload hashes before and after execution. A mismatch, compile failure, unsupported runtime setting, timeout, or unexpected rank mapping is retained as a failed preflight with no automatic retry.

The submission must wait for job `25940700` to finish using `afterany`, preserving the one-active-CPU-job cap. Root will handle the dependency, current queue/budget checks, reservation, and submission under its existing lock. The requested four-core/three-minute resource envelope is nominally 0.2 SU under the recorded core-hour conversion; the root conservatively reserves 6.4 SU using 128 cores for three minutes. This allowance is not a site-posted charge.

## Decision limits

A passing result establishes only that this four-rank single-node interface probe observed the specified method-3 mapping on the loaded Cray MPICH/PALS environment. It does not establish the four-node mapping, rank ordering on all 512 processes, runtime solver affinity, a performance effect, numerical equivalence, or a contest result. Any future four-node candidate needs a fresh review of the confirmation, budget, queue capacity, and actual four-host control mapping. The identity and candidate probe logs are required inputs to that review. This preflight itself runs no OpenFOAM solver and accesses no mesh.

## References and retained preparation

- [Offline graph screen and retained proxy evidence](../rank-placement-512-screen-20261023/PLAN.md).
- [Root-reviewed installed MPICH/PALS interface check](../rank-placement-512-screen-20261023/runtime-interface-review.json).
- [HPE Cray MPICH 24.03 rank-reordering documentation](https://h41374.www4.hpe.com/docs/24.03/mpt/mpich/intro_mpi.html#general-mpi-environment-variables), method 3 and order-file format. The cluster's installed 8.1.15 manual was reviewed separately; this public documentation is not a substitute for runtime verification.
