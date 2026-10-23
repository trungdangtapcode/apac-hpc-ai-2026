# Whole-group host assignment with a non-regression interval

## Question and controls

Can the 32 fixed 16-rank logical NUMA groups from the prior within-host screen be reassigned as whole groups to four logical hosts, eight groups per host, so the assignment is no worse than the original contiguous control on both graph cut proxies?

The source graph is the sealed 512-rank processor graph. The 32 supernodes are exactly the prior screen's optimized rank groups. Their group membership and internal rank order are not modified. Aggregate every original processor edge between two distinct supernodes into a weighted superedge, then verify that the full edge weight is conserved.

Compare:

1. The original control (`host = rank // 128`, `NUMA = (rank % 128) // 16`).
2. The aggressive parent mapping, which reduces cross-host faces but has a higher same-host cross-NUMA subtotal than the control.
3. A balanced whole-supernode assignment, eight nodes per host, constrained to dominate or match the control on both proxy categories.

Let `H` be cross-host faces over the 32-node graph and `T = 993,822` be its total cross-NUMA superedge weight. For an assignment, same-host cross-NUMA faces equal `T - H`. The non-regression interval is therefore `283,741 <= H <= 337,324`, where the lower bound preserves the control's 710,081-face same-host subtotal and the upper bound preserves its 337,324-face host subtotal. Distance to this interval and proximity to its lower boundary guide the search algorithm only; they are not physical cost weights.

## Search and validation

First enumerate every one-swap exchange of two supernodes in different hosts from the aggressive parent assignment. Then perform a deterministic seeded search of balanced whole-supernode swaps, using seed 2026 and at most 500,000 proposals within 20 local seconds. Retain the best feasible mapping and unique nondominated cut points observed. Since `same_host_cross_numa = T - H`, each distinct feasible `H` produces a nondominated two-cut point; this is a sampled frontier, not a proof of the global Pareto set.

Validate supernode aggregation conservation, all 32 groups, eight groups per host, unchanged 16-rank membership, unchanged group cell counts, the full 512-rank permutation and rank-zero-first order. Check at least 100 incremental swaps against full supergraph recomputation, then independently recompute the chosen mapping's host and NUMA cuts from all 512 original graph edges. Report per-host external-face and cell-load proxies without combining them into a weighted objective.

## Limits

This is an offline graph assignment only. Eight logical NUMA domains per host remain a historical assumption; the current four-node topology, rank-to-host/core mapping and NUMA page placement are unverified. Face counts do not measure traffic, wait time, latency, locality or solver performance. The new mapping is not submitted and creates no runnable rank-order payload.

## Pinned inputs

- Processor graph: `../rank-placement-512-screen-20261023/graph.json`, SHA256 `3ba8612bf5e0521f2cfb39fdd4c9d0642f689c6e5a86a9bb93accad212b7a209`.
- Fixed 32 logical NUMA groups and aggressive host assignment: `../rank-placement-512-numa-screen-20261023/screen.json`; its exact SHA256 is recorded by the screen.
- Original control and provenance limitations: `../rank-placement-512-screen-20261023/RESULTS.md`.
