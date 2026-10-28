# Iris MPI rank-affinity qualification probe

## Why this probe exists

The completed Iris reverse-order pair showed a strong first-arm timing effect in
both tested orders. It did not establish a cause. The solver logs retained
whole-node process and resource summaries, but no rank-level CPU affinity. This
small diagnostic fills that evidence gap before interpreting any placement
trial. It runs no OpenFOAM case and produces no solver-performance result.

## Frozen question and observations

On one exclusive Iris node, what main-thread CPU mask does each of 56 MPI ranks
have immediately before and after `MPI_Init`, and how do the rank-to-CPU/NUMA
mappings differ among:

1. **A-default:** `mpirun -np 56` with runtime defaults.
2. **B-fill:** `--map-by ppr:28:package --bind-to core --rank-by fill`.
3. **C-span:** the same process mapping and core binding as B, but
   `--rank-by span`.

The pair B/C holds the mapped CPU set and binding width fixed while changing
`MPI_COMM_WORLD` rank order across the two packages. Open MPI documents `fill`
as ranking all processes on one mapped resource instance before moving on and
`span` as round-robin ranking across mapped resource instances. The actual
rank masks are still measured and validated; command-line intent is not treated
as proof of runtime placement.

## Resource and runtime bounds

- Slurm: one exclusive node, 56 tasks, zero GPUs, Iris `low` QoS.
- Requested wall time: five minutes. A cumulative elapsed-time guard bounds
  timed build/probe/analysis commands to 235 seconds, leaving over one minute
  for termination and scheduler bookkeeping.
- Three 56-rank, no-work probes, each with a 40-second timeout; compile has a
  35-second timeout. No solver, mesh, field, MPI microbenchmark, profiling,
  LD preload/audit, or helper-thread experiment is included.
- Runtime modules: `gcc/11` and `hpcx/2.50`, matching the existing Iris native
  work. The resulting module list, selected runtime identities, compiler and
  launcher versions, executable hashes, dynamic-library inventory, CPU
  topology, allocation CPU mask, thread limits, and selected MPI placement
  environment overrides are recorded. No full environment dump is collected.

## Admission gate

Before any scheduler admission, the reviewer must independently check the
frozen payload and current budget/queue/locks. At runtime the validator requires
56 ranks on one host and the observed topology to expose exactly 56 physical
cores, two sockets, two NUMA nodes, and one hardware thread per core. For B and
C it requires singleton post-init masks forming a bijection over the actual
56-CPU allocation. It also requires B and C to produce distinct rank-to-CPU
mappings. Any mismatch is a failed qualification, not a performance result.

`job.sbatch` writes under `runs/$SLURM_JOB_ID`; create the top-level `runs/`
directory before submitting so Slurm can open its output paths. This directory
contains only `.gitkeep` in the frozen source payload.

## Interpretation limits and next gate

The C program reads the calling thread's affinity immediately before
`MPI_Init` and immediately after it returns. It does not inspect OpenMP or other
helper threads, page placement, memory bandwidth, solver behavior, or runtime
cost. The operating system's CPU-to-NUMA map is recorded for each post-init CPU.
That map is not a NUMA page-residency measurement.

If A and B produce the same rank masks, do not spend a solver allocation on an
A-versus-B placement comparison. If B/C differ and both pass the bijection
gate, the result may justify a separately reviewed native solver trial that
changes rank placement only. It does not itself show that `span` is faster.
Keep this diagnostic out of scored/native performance comparisons.

## Primary reference

Open MPI 5.0.5 `mpirun` documentation, mapping/ranking/binding options:
<https://docs.open-mpi.org/en/v5.0.5/man-openmpi/man1/mpirun.1.html>

## Offline use

`python3 analyze.py RUN_DIRECTORY` validates captured rank files and topology;
it makes no network or scheduler calls. `job.sbatch` is a prepared payload only.
No job is submitted by this folder or README.

The top-level `payload-sha256.txt` seal covers all files used by the job and
is checked before and after the run. It intentionally does not hash itself.
