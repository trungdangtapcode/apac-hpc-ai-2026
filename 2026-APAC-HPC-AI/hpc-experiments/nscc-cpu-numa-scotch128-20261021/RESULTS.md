# NUMA-aware Scotch passes the partition screen

Job **25907688.pbs101**: F / exit 0, **385 seconds / 6 min 25 s**, native v2512 / double precision, 32 allocated CPUs / serial task, estimated **3.422222 SU**, batch MaxRSS **32.0174 GiB**. Full mesh identity, 128 partitions / 65,334,765 cells, restored fields, native tree request and reciprocal graph checks pass. All **168 safe text artifacts** are sealed.

| Quantity | Default Scotch | NUMA tree (8 × 16) |
|---|---:|---:|
| Unique cross-group interface faces | 371,658 | 332,157 |
| All unique interface faces | 1,549,377 | 1,570,175 |
| Worst-rank interface faces | 42,141 | 43,115 |
| Maximum processor neighbors | 35 | 32 |
| Maximum cell excess over mean | 1.177864% | 1.005460% |
| Synthetic 10:1 objective | 4,894,299 | 4,559,588 |

Cross-group faces fall **10.6283%**, while total faces rise **1.3423%**. All five preregistered filters pass. This is a promising partition, not a measured solver gain. Logical groups of sixteen correspond to the earlier diagnostic NUMA CPU sets only if the next allocation's placement also matches. Weights 10:1 are synthetic, not measured latency. Tree execution is inferred from matching pinned source/build and requested native dictionary, not direct tracing. No bandwidth, cache, MPI wait/traffic, page residency or power measurements were collected.

Decision: proceed to a same-node 40-step default-Scotch versus NUMA-Scotch pair, complete mandatory candidate initialization, verified physical placement, unchanged numerical work and sealed zero fields. Preserve the native Average including outliers. The preceding H→S pair's observed 0.994% saving remains unconfirmed. A partition benefit must survive a solve and a reverse-order repeat before promotion.

All eight recorded allocations are terminal; core-hour estimates total **83.417778 SU**. Conservative consumed ceiling is **85 SU**, no reservations. The stale project amount delta is not actual current wave spending. The original 100-SU wave could not afford a full pair. The owner then explicitly requested much more research/submission based on the separate large HPC grant. A new bounded continuation raises the **cumulative CPU research ceiling to 1,000 SU**, still far below the 30,000-SU project grant. Keep actual spending/reservations under the CPU lock, one active CPU allocation, combined own PBS cap three, no AI changes or background Codex. This is a new owner-directed phase; preserve original 100-SU provenance.
