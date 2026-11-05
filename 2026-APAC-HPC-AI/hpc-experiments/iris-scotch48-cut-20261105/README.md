# Iris Scotch 48-domain cut qualification

## Question and hypothesis

The previous Iris Scotch cut used 56 domains. This bounded follow-up asks
whether using 48 Scotch domains on the same 65,334,765-cell mesh gives a useful
lower rank density for a later solver comparison. At 48 domains, average mesh
size is about 1,361,141 cells/domain; at 56 it is about 1,166,692, a 16.7%
increase per domain. Fewer MPI domains could reduce communication overhead, but
the increased per-rank work and different partition can offset that. This cut
job measures neither effect and makes no speed, solver, or score claim.

The controlled factor here is only the decomposition count, set through
`nCores=48` / `numberOfSubdomains $nCores`; Scotch remains selected. The pinned
case source differs from the reviewed 56-domain input only in that one
`nCores` value. All other source pins and the official serial mesh identity
checks are retained. The new artifact root and exact processor-directory gate
prevent reuse of a prior partition.

## Stage and resources

The job uses one exclusive Iris node, 56 CPUs, one serial task, zero GPUs, low
QoS, and a 40-minute maximum (37.333 allocated CPU-hours at whole-node
accounting). Scotch decomposition is capped at 30 minutes. The existing group
serial mesh is used in place; all eight complete mesh members must match the
retained official archive extraction before decomposition. The same 41 case
source files remain SHA-256 pinned, with the deliberate `nCores` change
reflected in the updated pin.

Only serial `decomposePar -constant` and `restore0Dir -processor` run. The
validator requires exactly `processor0` through `processor47`, no symlinked
processor directories, all six restored fields in every domain, native
v2512/scalar64/`End` output without fatal errors, and all 48 per-domain cell
counts summing to 65,334,765. It retains input hashes before and after, mesh
proof, hardware information, decomposition output/resource log, restore log,
and cut validation. Any failed gate remains an unsuccessful cut record.

## Later work required before a solver comparison

A successful cut is still not a ready case. The owner must review the exact
artifacts, then separately prepare and validate the required `renumberMesh`,
`potentialFoam`, and `applyBoundaryLayer` initialization stages. A later solver
comparison must use matched initialization, mesh, numerical settings, and
solver horizon. To claim a rank-density effect, compare matched 48-domain and
56-domain controls; the previously retained 56-domain solver result is not by
itself a matched control. Keep each machine's measurements separate.

This payload has no READY marker, does not run initialization or a solver, and
contains no job receipt or measurements. It has not been deployed or submitted.
Shared-account billing, memory bandwidth, NUMA placement, and network counters
are not collected by this cut stage.
