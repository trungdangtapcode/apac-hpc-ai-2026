# Iris Scotch48 initialization kit

## Scope and hypothesis

This kit performs the mandatory native initialization for the completed Scotch
48-domain cut from Slurm job 2294914. The cut root is
`/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch48-cut-20261105T073707Z`,
with its unique artifact at `artifacts/cut-N48-scotch`. The cut evidence stays
in `kit/runs/` under that root. This job must verify the cut's terminal
accounting, exact 48-domain tree, all 48 cell counts, source pins, and complete
eight-member official serial-mesh identity before modifying the artifact.

The scientific lead is tentative rank density: 48 domains raise average cells
per domain by 16.7% relative to 56 domains, while fewer domains may reduce
communication. This initialization job measures neither effect. It runs no
solver and reports no performance or score. A later solver comparison needs
matched 48- and 56-domain controls with the same initialized inputs, machine,
numerical settings, and solver horizon.

## Resources and MPI placement

The job requests one exclusive 56-CPU Iris node, 48 MPI tasks, zero GPUs, low
QoS, and 20 minutes maximum. Whole-node maximum allocation is 18.667 CPU-hours.
An internal 1,140-second deadline leaves a minute for cleanup. It uses the same
GCC 11, HPC-X 2.50, and optimized OpenFOAM v2512 environment as the reviewed
cut.

The MPI launch preserves the existing default Open MPI mapping and binding
behavior: it requests 48 ranks and records `--display-map` and
`--report-bindings`; it adds no map or binding policy. The hostname probe must
show ranks 0 through 47 exactly once on one host. The displayed placement is
retained as evidence. No per-socket rank layout is assumed or claimed by this
kit; solver placement and performance require later qualification.

## Mandatory initialization and gates

The exact organizer stage order and arguments are retained:

1. `renumberMesh -constant -overwrite -parallel`
2. `potentialFoam -initialiseUBCs -parallel`
3. `applyBoundaryLayer -ybl 0.0450244 -parallel`

Each stage has its own 210-second cap within the shared deadline. Each log must
show return code zero, native `End`, OpenFOAM 2512, scalar64, exactly 48
processes, the exact command, and no fatal markers. Before initialization, the
kit seals 288 time-zero field files; afterward it records a new 288-file seal
because initialization may legitimately change values. It also retains cut
accounting, mesh proof, source hashes before/after, rank host/map/binding output,
per-stage GNU time resource records, and hardware information. READY is written
last only if every gate passes. Failed partial artifacts keep the in-progress
marker and cannot be resumed or overwritten.

The case source pins derive from the N48 cut payload. Compared with the prior
N56 initialization source, the only input-file difference is the pinned
`system/include/caseDefinition` rank count, 56 to 48; the N48 Scotch cut source
is the authority for this kit. `Allrun` is absent only from the operational
working copy. The operational `controlDict` and `fvSolution` use the pinned
no-write and fixed-iteration variants, as in the reviewed initialization
recipe.

## Offline review and status

Run `python3 review.py`, `bash -n init.sbatch`, and
`python3 -m py_compile verify-init.py review.py`. The review exercises passing
and rejecting source, cut, accounting, mesh, rank inventory, field inventory,
MPI completeness, and native log cases without contacting Iris or running
OpenFOAM.

This is a prepared payload. It has not been deployed or submitted. It does not
create solver timings or a performance claim.
