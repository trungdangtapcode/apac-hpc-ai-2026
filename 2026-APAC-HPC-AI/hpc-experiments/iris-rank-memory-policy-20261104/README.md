# Iris MPI-rank memory-policy diagnostic

## Question and hypothesis

Does setting `numactl --interleave=all` on the solver-launcher process propagate
to its MPI ranks, and does each rank's anonymous first-touch mapping show a
different NUMA page placement from the inherited-policy control? This is a
mechanism diagnostic. It runs no OpenFOAM solver, mesh or performance trial.

The hypothesis is that the launcher policy is inherited by all ranks and that
the ranks' 8 MiB private anonymous mappings are distributed over the allowed
NUMA nodes under interleave, while the control reflects its inherited policy.
The observation unit is one MPI rank; this does not represent solver memory.

## Arms and controls

Both arms run the same `mpirun -np 56 --report-bindings --display-map --`
command with `rank_probe.py`, each under a 100-second timeout:

1. `inherited`: no launcher policy wrapper.
2. `interleave`: `numactl --interleave=all` wraps the same MPI launcher.

Each rank records its explicit Open MPI rank, `numactl --show`, CPU affinity and
allowed CPU/memory masks, then allocates an 8 MiB `MAP_PRIVATE | MAP_ANONYMOUS`
mapping and writes one byte per system page. It finds the exact mapping start
address in its own `/proc/self/numa_maps` and records that complete line, node
page counts, the reported byte count, and whether the counts equal the request.
Each rank writes its JSON record atomically to a separate arm directory. There
is no optional or periodic sampler.

The job uses one exclusive Iris node, 56 CPUs, zero GPUs, low QoS, and a five
minute maximum. The batch setup follows the parent native bundle's GCC 11,
HPC-X 2.50, and OpenFOAM environment setup to keep the software environment
comparable; no solver executable is launched. The wrapper provides 240 seconds
for both launches together, leaving job cleanup margin.

## Interpretation limits and failure behavior

The two arms execute sequentially on the same allocation, so this tests policy
propagation and placement reporting rather than a concurrent or randomized
comparison. The anonymous mapping is a small probe, not the solver's allocation
pattern. `numa_maps` may account for pages with details that vary by kernel;
the script reports the exact line and counts without assigning absent pages to
a node. Missing or ambiguous start-address matches, absent rank identity,
missing policy text, failed launches, incomplete ranks, or absent node-page
counts are explicit errors, not fabricated placement. If mapped-byte accounting
differs from 8 MiB, retain the raw line and qualify the result rather than
claiming exact full-segment placement.

Before and after both arms, the driver verifies every path listed in
`payload-sha256.txt`; a mismatch aborts the diagnostic. Runtime records are
written under `runs/inherited/` and `runs/interleave/`. Offline checks validate
syntax, arm structure, resource limits, required instrumentation and the
payload hash manifest without launching MPI or requiring Iris modules.

## State

Prepared for offline review only. It has not been deployed or submitted and has
no scheduler receipt or placement observations. A result must report whether
both arms produced 56 distinct rank files, each actual rank policy, all mapping
lines and per-node page counts, and any accounting or collection limitations.
