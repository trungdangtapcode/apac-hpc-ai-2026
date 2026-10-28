# Offline NUMA rank-group search

## Question

The actual affinity qualification (Iris job **2294358**) found that default
Open MPI and explicit `B-fill` produce the same rank-to-CPU and rank-to-NUMA
masks. That closes the default-versus-`B-fill` branch. `C-span` alternates rank
ownership between NUMA nodes, but its measured cross-NUMA proxy was worse than
the default. A read-only extraction of the retained 56 processor-boundary files
now supplies a weighted rank-neighbor graph for the exact `xyz` and `zyx`
decompositions.

## Method and constraints

`graph_search.py` runs a deterministic, multistart Kernighan–Lin pair-swap
bisection separately for each graph. It uses the actual default rank groups as
one start and 32 balanced randomized starts per order with seeds 2026–2057.
Every candidate assigns exactly 28 ranks to each NUMA node. For each order, the
larger node's cell count must stay at or below 1.01 times the default's larger
node load. The 20-second wall and process-CPU guards apply to the full search.
The default partition is retained as the fallback and can never be replaced by
a worse cut.

## Results

The objective is the weighted count of unique processor-interface faces whose
two ranks are assigned to different NUMA nodes. The zyx candidate is the one
relevant to the initialized source already staged for the HPC work.

| Decomposition | Default cross-NUMA faces | Candidate faces | Reduction | Default cell load (NUMA 0 / 1) | Candidate load (NUMA 0 / 1) |
|---|---:|---:|---:|---:|---:|
| xyz | 375,788 | 84,919 | 77.40% | 32,667,378 / 32,667,387 | 32,667,385 / 32,667,380 |
| zyx | 129,700 | 90,953 | 29.87% | 32,667,376 / 32,667,389 | 32,667,376 / 32,667,389 |

Both candidates keep 28 ranks per NUMA node. The maximum permitted node loads
are 32,994,060 cells for xyz and 32,994,062 for zyx, so both are well inside
the 1% balance bound. The graph has 227 weighted neighbor edges for xyz and 221
for zyx; those edge weights sum to 1,326,716 and 1,269,961 unique interface
faces respectively.

### Exact zyx candidate groups

- NUMA 0: ranks `0–23`, plus `26, 28, 30, 36`.
- NUMA 1: ranks `24, 25, 27, 29, 31–35, 37–55`.

The exact xyz groups, per-rank cell counts, all seed outcomes, and face counts
are in [graph-search.json](graph-search.json). The interim combined-graph
objective is retained as [combined-graph-search.json](combined-graph-search.json)
for provenance; it was superseded because each decomposition needs its own
rank grouping.

## Decision and limits

The zyx cut falls 29.87%, above the 5% screening threshold. This is enough to
justify considering a short **18-step ABBA native measurement** for zyx after a
reviewer verifies how the proposed rank groups map to the actual 56 single-core
binding slots. It is not evidence of solver speedup, and no performance job has
been prepared or submitted by this graph search. The xyz result is a separate
candidate for xyz; these two order-specific mappings must not be conflated.

This proxy counts unique partition-interface faces. It does not measure bytes,
communication time, page residency, memory bandwidth, runtime binding, or
solver performance. The bisection is a bounded heuristic, not a proof of global
optimality. Keep the completed probe receipt and the input graph hashes with any
later experiment review.
