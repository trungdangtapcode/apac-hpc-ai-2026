# Native Scotch N128 preparation accepted

Job **25907236.pbs101** passes the full reviewer: F / exit 0, 371 seconds (6 min 11 s), 32 allocated CPUs / one serial task, native v2512 / double precision. Official archive MD5/SHA256 and all eight unpacked members match. Exactly 128 partitions contain 65,334,765 cells and all restored fields. Initial control fields are sealed: 768 files. Sealed collection contains 164 safe text files; processor trees remain on cluster.

| Partition statistic | Hierarchical (16 4 2) | Default Scotch |
|---|---:|---:|
| Maximum cells | 510,431 | 516,440 |
| Maximum cell excess over mean | about 0.000617% | 1.177864% |
| Maximum processor interface faces | 131,252 | 42,141 |
| Unique interface faces | 2,109,346 | 1,549,377 |
| Maximum processor neighbors | 16 | 35 |

Scotch reduces interface faces but increases cell imbalance and neighbor fan-out. This supports testing, not a proven speedup or a measured bottleneck: all ranks will communicate within one node for the immediate screen. Native decomposition/preparation took longer than hierarchical (371 vs 187 seconds), and that setup cost must remain visible independently of solver seconds/step. Batch MaxRSS 31.906254 GiB; estimated allocation charge 3.297778 SU, not individually posted billing. Hardware bandwidth/cache/MPI counters, power and actual page placement were not collected.

Next decision: promote to the frozen same-node H→S pair, with candidate mandatory initialization, unchanged numerical work, exact zero-field reuse guards and all native output checks. Do not rerun decomposition or modify submitted payloads. Retain the terminal prep maximum 8 SU pending reconciliation, so conservative total planning commitment remains 29 consumed + 8 retained + 61.866667 requested pair = 98.866667 / 100 SU. No budget increase or AI changes.
