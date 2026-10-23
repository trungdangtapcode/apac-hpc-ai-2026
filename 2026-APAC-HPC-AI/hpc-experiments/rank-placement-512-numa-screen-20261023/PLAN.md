# Fixed-host logical NUMA grouping screen

## Question

For the sealed 512-rank logical-host candidate in [the parent four-host screen](../rank-placement-512-screen-20261023/RESULTS.md), can each fixed set of 128 ranks be regrouped into eight balanced 16-rank logical NUMA groups with fewer same-host crossing faces? This is a graph tradeoff screen only. The historical one-node machine had eight NUMA domains; the current four-node topology and rank-to-NUMA placement are unverified.

## Inputs and controls

Use only the validated processor graph and parent `screen.json`. Verify the graph file hash, the parent 512-rank bijection, four host groups of 128, and a recomputed parent cross-host cut of 261,110 faces. Do not change host membership.

Compare three assignments on the same graph:

1. **Contiguous control:** host `rank // 128`; logical NUMA group `(rank % 128) // 16`.
2. **Parent mapping:** retain the parent host membership and take consecutive groups of 16 from its sorted group-major rank permutation within each host.
3. **Optimized within host:** keep each parent's 128-rank host set fixed, then optimize eight groups of 16 independently within each host.

For every assignment, report cross-host faces separately from same-host cross-NUMA faces. Keep all four host sets and the parent cross-host cut unchanged. Derive per-host NUMA interface matrices and external-face totals; do not combine the two cut types using an arbitrary weighted physical cost.

## Search and acceptance

Use seeded, bounded balanced swaps with seed 2026. Search each host independently and retain its baseline mapping as the minimum accepted result, so a host cannot regress. Follow the seeded exploration with baseline-anchored deterministic best-improvement swaps. Verify at least 100 incremental swap deltas against full cut recomputation; verify all host memberships, rank bijections, subgroup capacities, rank-zero-first permutation, unchanged host cut, and objective recomputation. Stop the combined search within 30 local seconds and make no global-optimum claim.

The mapping is not a runtime artifact. No solver, MPI, rank-order file, PBS script, SSH, scheduler or budget action is part of this screen. The report must distinguish graph faces from communication volume, physical NUMA locality, page residency, affinity and solver speedup.

## Source provenance

The parent graph SHA256 is `3ba8612bf5e0521f2cfb39fdd4c9d0642f689c6e5a86a9bb93accad212b7a209`. Its intake contains 512 retained boundary dictionaries and the matching native decomposition log, but those boundaries were collected after submission and do not prove frozen mesh identity or historical rank placement. The parent mapping itself was independently screened as a logical four-host graph grouping; this follow-on does not upgrade it to physical placement evidence.
