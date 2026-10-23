# Fixed-host logical NUMA grouping tradeoff

## Finding

Holding the parent four-host rank membership fixed preserves its **261,110 cross-host interface-face cut**. The parent mapping's sorted rank order, split into eight 16-rank logical NUMA groups per host, has **1,097,554 same-host cross-NUMA faces**. The bounded within-host search reduces that subtotal to **732,712**, a reduction of **364,842 faces (33.24%)**. Every host's optimized subtotal is no worse than its own parent baseline.

The comparison also shows a tradeoff against the original contiguous control. Its host assignment has 337,324 cross-host faces and 710,081 same-host cross-NUMA faces. The optimized parent candidate keeps its lower 261,110 cross-host proxy, while its same-host cross-NUMA subtotal remains 22,631 faces (3.19%) above the original control. No arbitrary weights were applied to combine these two quantities.

The eight groups of 16 ranks are an assumption based on historical one-node topology. The four-node topology, actual MPI rank-to-host/core mapping, and NUMA page placement remain unverified. These graph cuts do not predict runtime or speedup.

## Comparison

| Assignment | Cross-host faces | Same-host cross-NUMA faces | Within-host same-NUMA faces |
|---|---:|---:|---:|
| Original contiguous control (`rank // 128`; NUMA `(rank % 128) // 16`) | 337,324 | 710,081 | 1,879,617 |
| Parent four-host candidate, sorted rank blocks of 16 | 261,110 | 1,097,554 | 1,568,358 |
| Same parent hosts, optimized NUMA groups | 261,110 | 732,712 | 1,933,200 |

The three columns sum to the same **2,927,022 unique interface faces** in each assignment. The host cut is unchanged by the optimization. The optimized full permutation is a 512-rank bijection with rank 0 first and 128 ranks per host, split into eight groups of 16 within each host.

| Parent host group | Same-host cross-NUMA faces, parent | Optimized | Reduction | Max external faces for one logical NUMA group, parent → optimized |
|---|---:|---:|---:|---:|
| 0 | 380,828 | 256,721 | 124,107 | 151,601 → 115,234 |
| 1 | 262,281 | 178,170 | 84,111 | 94,052 → 63,332 |
| 2 | 177,262 | 110,501 | 66,761 | 60,207 → 41,451 |
| 3 | 277,183 | 187,320 | 89,863 | 89,482 → 60,844 |

The maximum logical-NUMA-group external-face proxy falls in every host. The complete 8×8 unique-face matrices for the original control, parent mapping, and optimized grouping are retained per host in [screen.json](screen.json). Matrix entries count each undirected edge once in the upper triangle; diagonal entries are within-group faces. External-face totals count a crossing edge at each endpoint group, so they are useful per-group summaries and are not additive as unique edges.

## Workload balance and search

Host membership and the cell total on each host are unchanged from the parent mapping: **16,393,858; 16,327,121; 16,279,147; and 16,334,639 cells**. Within each host, the eight logical NUMA groups have these cell-count ranges: host 0, **2,039,642–2,055,400**; host 1, **2,029,572–2,051,281**; host 2, **2,030,024–2,038,323**; host 3, **2,030,758–2,050,700**. These are sums of existing rank cell counts assigned hypothetically to groups; no cells moved or ran on NUMA nodes.

The seeded search used seed **2026**, up to **250,000 balanced swaps per host** and deterministic best-improvement descent from each host's own baseline and annealing best. It completed **1,000,000 proposals** in **5.05 seconds total local elapsed time**, under the 30-second combined limit. It checked **128 random incremental swap deltas** against full cut recomputation. Each host retained its baseline as the minimum acceptable candidate and improved its same-host cross-NUMA subtotal. The method makes no global-optimum claim.

See [PLAN.md](PLAN.md) for the controls and acceptance rules, [screen.py](screen.py) for reproducible calculations, and [qualification.json](qualification.json) for structural checks. Qualification is limited to graph bookkeeping, group sizes, mapping preservation and objective recomputation; it is not a physical-topology or runtime qualification.

## Limits and next check

Boundary graph face counts do not measure bytes, message sizes, network or NUMA traffic, MPI wait, memory locality, page placement, process affinity, solver critical path, or speedup. The earlier parent graph's source limitations remain: boundary dictionaries were collected after submission and do not independently establish original mesh identity or historical placement.

The next low-cost step is the separately queued four-rank MPI rank-reordering interface preflight. It can test whether the installed runtime exposes the requested MPI-world reordering behavior, but it cannot qualify the 512-rank mapping or current four-node NUMA topology. Keep the solver queue and both existing PBS jobs unchanged.
