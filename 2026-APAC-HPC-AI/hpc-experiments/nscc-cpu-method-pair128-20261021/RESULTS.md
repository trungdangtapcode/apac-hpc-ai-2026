# Same-node result: a small observed Scotch gain, not an established win

Job **25907325.pbs101** passed both native solves on the same exclusive ASPIRE-2A CPU node, x1001c0s1b0n0. Order was hierarchical then Scotch, 128 MPI ranks, OpenFOAM v2512 / double precision, 65,334,765 cells, identical fixed physics, iteration counts and function objects. This is a one-node 40-step method screen, not the four-node 150-step contest score.

| Metric | Hierarchical (16 4 2) | Default Scotch |
|---|---:|---:|
| Average, seconds per step | 14.7872238123 | 14.6402329083 |
| Median, seconds per step | 14.708853 | 14.480458 |
| p95, seconds per step | 15.222146 | 14.848304 |
| Slowest step, seconds | 15.693371 (step 36) | 21.120703 (step 9) |
| Standard deviation, seconds per step | 0.236305 | 1.060469 |
| Measured steps | 39 (steps 2–40) | 39 (steps 2–40) |
| Final Cd, dimensionless | 0.4389323284 | 0.4359888360 |
| Native solver clock, seconds | 621 | 616 |
| Omega bounding messages | 8 | 10 |
| Native timing confidence warning | No; calculated minimum 2 samples | Yes; calculated minimum 50 samples |

Scotch has the lowest observed average in this pair, a **0.9940% reduction in time per step** (1.01004 control/candidate ratio). It is not a confirmed optimization: one ordered pair, a seven-second outlier and the native confidence warning do not establish a stable one-percent gain. Keep step 9 in the average; do not trim it or raise the official 40-step endpoint just to suppress a warning. Median and p95 are useful diagnostics, not replacement contest metrics. The independent hierarchical baseline was 14.921981 s/step on another node and is contextual only.

## Numerical and execution inspection

Every native stage exited zero and has End, v2512, scalar64 and 128-rank markers. Candidate mandatory initialization completed once. All 40 steps keep Ux/Uy/Uz=15, pressure=12, omega/k=8 iterations. All force rows are finite, the timer file and log agree, and both initial zero-time field trees have identical before/after hashes. Control Cd exactly reproduces the prior baseline; Scotch Cd reproduces the public method-specific reference to printed precision. A change in decomposition can change floating-point operation order and GAMG behavior. Do not impose the Bonus accuracy comparison as a universal Basic ±0.5% gate. Lower continuity error alone is not proof of better physical accuracy.

Atomic diagnostic rank records verify unique cores 0–127 and groups of sixteen within each of eight NUMA CPU sets. These are pre-solve diagnostic bindings, not solver migration or actual memory-page residency. Whole allocation: **1373 seconds / 22 min 53 s**, estimated **48.817778 SU**, batch MaxRSS **121.3995 GiB**, aggregate CPU time **45:49:28**. GNU time wraps the launcher; its reported 0% CPU is not solver inactivity. Hardware bandwidth/cache/MPI counters and power were not collected. Read-only status/log snapshots and small boundary metadata collection overlapped the timed allocation; their overhead was not independently measured and no outlier cause is assigned.

## Assessment and next decision

The graph inspection reproduces native totals: Scotch has 1,549,377 total unique interface faces versus 2,109,346, and 371,658 faces across logical groups of sixteen versus 1,203,493. This structure supports a NUMA-aware partition hypothesis, not a measured MPI/NUMA bottleneck. Default Scotch is a provisional candidate; keep hierarchical as an accepted stable control. A reverse-order full repeat would be useful, but the remaining first-wave budget cannot cover its maximum; do not increase the ceiling silently.

Promote only the prepared low-cost native NUMA partition screen: domains (8 16), synthetic integer costs 10:1. It changes only scotchCoeffs. Its preregistered graph/balance filter, exact source reference and native payload live in ../nscc-cpu-numa-scotch128-20261021. Only submit after the locked reconciliation and queue/balance checks, maximum 8 SU, no solver claim. A promising graph still needs an independently budgeted solve and repeat.

## Cost and reproducibility

All seven recorded CPU allocations are terminal. Their requested-core × elapsed-time estimates sum to **79.995556 SU**. Project report still shows a stale amount delta of **27.879 SU**, with In Doubt zero; do not call this exact posted billing. Use conservative **81 SU consumed** = ceil(max(reported delta, terminal estimate) + 1 SU). Unchanged wave ceiling 100 SU leaves **19 SU**, sufficient for the full next 8-SU prep maximum. Original requested maxima remain in the ledger history. Retain refresh/timestamp limitations and never deduct prepaid In Doubt twice.

`review.py` reproduces review.json from **127 sealed text artifacts**, including fixed inputs, both native logs/timers/force outputs, init logs, phase markers, rank records and zero-field seals. detailed-inspection.json retains outlier indices and final diagnostics. Processor fields/meshes remain on the cluster and can be rebuilt from the verified official archive and pinned native preparation. No AI jobs, ledger, payload or submission package changed.
