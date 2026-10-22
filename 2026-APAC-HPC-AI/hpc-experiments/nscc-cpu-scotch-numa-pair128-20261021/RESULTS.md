# Native NUMA timing reviewed; unchanged branch closed

Scratch evidence for **25907753.pbs101** was recovered and sealed after VPN/CPU SSH restoration on 22 October. **127 text artifacts** pass the files-only reviewer: all native commands exit zero, 40 fixed-work steps per solve / 39 timed samples, original source/precision/function objects, finite forces, exact timing crosschecks, unchanged zero-time fields, and physical-core/eight-NUMA grouping. The final native wrapper marker exists. **PBS history returns Unknown Job Id**, so final scheduler exit, whole-allocation elapsed time, resource maxima and actual billing are not claimed. Retain the full **61.866667-SU** reservation.

| Metric | Default Scotch | NUMA tree (8 16), synthetic 10:1 |
|---|---:|---:|
| Average, seconds per step | 13.880988254 | 14.358714620 |
| p95, seconds per step | 14.018158 | 14.566025 |
| Maximum, seconds | 14.237294 | 16.614805 (step 10) |
| Final Cd, dimensionless | 0.4359888360 | 0.4345811574 |
| Omega bounding messages | 10 | 8 |

Candidate time per step increases **3.4416%** in this ordered same-node pair. Its graph had 10.6283% fewer logical cross-NUMA faces but 1.3423% more total faces; the graph objective did not translate into a timing gain. The evidence does not establish the cause: no measured MPI wait/traffic, bandwidth/cache counters, power or page residency, and no reverse-order repeat. Do not infer a causal NUMA bottleneck or remove the slow step. Default's 13.880988 is the best observed one-node average so far, but comparisons to earlier hosts/allocations are contextual, not additional controlled speedups. No four-node score.

Decision: close this unchanged NUMA configuration as a performance candidate and prioritize the validated two-node baseline. A source/graph improvement alone is insufficient. Keep the complete losing run and exact samples in review-files-only.json. No quality claim follows from a different Cd or fewer bounding messages. Numerical work remains fixed; no universal Basic ±0.5% gate is invented.
