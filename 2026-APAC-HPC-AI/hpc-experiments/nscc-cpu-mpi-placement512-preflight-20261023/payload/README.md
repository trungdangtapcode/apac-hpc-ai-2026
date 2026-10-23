# 512-rank MPI placement preflight

This is a short runtime mapping check, not an OpenFOAM experiment. It contains a small MPI C probe, the refined rank-group assignment, identity-slot renderer, validators, source-hash tools, and one PBS script. No mesh, solver case, GPU code, or hardware profiler is included.

## Submission

Submit from the experiment root so PBS uses it as `PBS_O_WORKDIR`. The parent worker must hold its CPU/budget lock and submit this child only after both prerequisite jobs finish successfully:

```sh
qsub -W depend=afterok:25940700:25943865 payload/mpi-placement512-preflight.pbs
```

The request is the normal queue, project 59000042, four exclusive standard CPU nodes, 128 MPI ranks per node, 32 GB per node, no GPUs, scatter placement, and three minutes. The memory request provides headroom for 128 MPI processes per node and the transport runtime; it is not a measured RSS requirement. The wrapper starts its 135-second internal deadline before module setup and leaves 45 seconds for validation, source-hash verification, and cleanup. At 512 requested cores this is a conservative maximum of 25.6 SU by the recorded core-hour conversion, not an estimate of posted job accounting. The root worker owns the queue, dependency, active-cap, budget reservation, and submission decision. A failed interface check is preserved and is not retried automatically.

## Identical control and candidate setup

After loading `openfoam/2512`, the job compiles `mpi-probe.c` on an allocated compute node. Both arms use the same binary, `mpiexec -n 512 --cpu-bind thread`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, and `FI_OFI_RXM_USE_SRX=0`. Other `FI_*` settings remain at site/module defaults. The environment snapshot is restricted to an allowlist of `FI_*`, `OMP_*`, `MKL_*`, `OPENBLAS_*`, `CRAY_*`, and `MPICH_*` variables. Both arms use `MPICH_RANK_REORDER_METHOD=3`, `MPICH_RANK_REORDER_FILE=rank-order.txt`, and `MPICH_RANK_REORDER_DISPLAY=1`; the order-file contents are the only intended difference.

The control file is `0,1,...,511`. After the identity run, the renderer uses each actual MPI world rank as an identity slot index. It does not infer contiguous host or NUMA placement from rank arithmetic. Logical host group zero maps to the host observed for identity rank zero; other hosts are ordered deterministically by their smallest identity rank. On that host, logical NUMA group zero maps to identity rank zero's observed domain; other actual domains receive deterministic labels. On the other hosts, observed NUMA domain IDs are sorted. Each refined 16-rank logical group is assigned to the observed 16 identity slots for its mapped host/domain, and the resulting 512-rank file is emitted in identity slot order. Rank zero remains in the first slot.

Each MPI process reports its actual `MPI_Comm_rank` and size, `MPI_Get_processor_name`, one-CPU `sched_getaffinity`, and physical package/core/NUMA IDs read from that process's local Linux sysfs. Optional `PMI_RANK` is recorded as diagnostic metadata only. Before candidate launch, the identity gate requires four PBS hosts with 128 ranks per host, 128 unique physical cores per host, and eight actual NUMA domains with 16 ranks each on every host. If the requested topology does not match, the job stops before launching the candidate.

The candidate validator checks every actual MPI world rank against the intended host, logical CPU, physical core, and NUMA domain of its rendered identity slot. It also checks all 512 rank IDs, world size, fixed host-group membership, 16-rank refined groups, and rank zero's first-slot rule. The output includes the per-rank intended and observed mapping.

## Captured evidence and limits

Outputs are written under a fresh `runs/<numeric-job-id>/` path. Review the PBS nodefile, module/compiler/PALS logs, selected `ldd` MPI libraries, return codes, phase timestamps, resource logs, identity and candidate stdout/stderr, generated rank-order file, intended per-rank mapping, mapping validation, before/after payload hashes, and lifecycle record. Lifecycle and `/usr/bin/time` records are diagnostics, not terminal PBS accounting.

A pass qualifies only the method-3 512-rank placement on that exact four-node allocation. It does not qualify a later allocation, OpenFOAM's decomposition or initialization, memory page placement, solver-time migration, communication traffic, performance, or score. No CPU/GPU replay or solver run is part of this payload. Review final PBS state/accounting separately and preserve any failure without automatic retry.
