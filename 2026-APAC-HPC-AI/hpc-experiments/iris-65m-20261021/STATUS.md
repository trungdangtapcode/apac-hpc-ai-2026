# First full 65M Iris practice baseline

**2293754: COMPLETED / exit 0:0.** Hierarchical (7 4 2), one Iris node
iris031, 56 MPI ranks, 40 solver steps. Full preparation is retained under
2293752 (cut/restore) and 2293753 (renumber/potential/boundary layer).

| Quantity | Observed value | Meaning |
|---|---:|---|
| Solver Average | 21.9653538363 s/step | Mean of measured steps 2–40; lower is faster |
| Median / p95 step time | 21.965798 / 22.541902 s | Distribution across the 39 measured steps |
| Min / max step time | 21.109065 / 23.846916 s | All slow steps retained |
| Final Cd | 0.4405543814 | Dimensionless drag coefficient at step 40 |
| Solver job elapsed | 925 s | Whole allocation, distinct from solver Average |
| Complete split-chain elapsed | 1189 node-seconds | Cut + init + solve; excludes time between jobs |
| Scheduler batch MaxRSS | 133.3636 GiB | Reported batch memory, not bandwidth or per-rank RSS |

This is **practice on Iris**, not the scored Gadi/ASPIRE-2A four-node result.
There is no matched comparator or speedup yet. The final Cd is near the rule's
approximate 40-step value (~0.43); Basic has no universal ±0.5% gate. Forty
steps are the requested endpoint, not proof of a fully converged aerodynamic
solution. Keep all original physics and numerical controls.

## What was actually checked

Seal 54 text artifacts plus both preceding preparation collections. Confirm
payload/receipt hashes, terminal exit, v2512/scalar64, exact prepared processor
links, all 40 contiguous steps and 40 coefficient rows. Independently recompute
all 39 measured step times: mean agrees with the printed Average, and the
native wallClockTime.dat agrees with the log. Every step uses Ux/Uy/Uz 15,
p 12, omega/k 8 iterations. Retain seven native omega bounding messages;
no fatal error or timing-confidence warning appears. No CPU/NUMA/bandwidth/
network hardware counter or billed Iris SU is collected.

The organiser solver script uses foamDictionary -set, which expands includes.
Native v2512 replay on allocated ASPIRE-2A CPUs produces otherwise byte-identical
expected/actual expanded dictionaries after normalizing only one generated
filename comment. Exact coded-function bodies and every other retained system
file match. The CPU comparison job 25904959 failed on that comment before mesh
work; preserve that failure, not a fictitious successful CPU preparation.

The first review expected empty stderr; actual stderr contains exactly the
two foamDictionary assignment echoes (startFrom startTime; endTime 40;).
The corrected reviewer permits only those exact entries. A first large PTY
base64 transfer was truncated and rejected before extraction. The successful
bounded chunk transfer matches the full remote archive SHA256. Neither review
correction changes the computation or hides a native error.

Run python3 review-solver.py to reproduce the checks. It links the frozen
CPU native expansion evidence. Complete result is solver-review.json; raw
artifacts remain under collected/2293754. Submission HPC_Task remains empty.

## Next decision

The Iris validity ladder has served its purpose. Prioritize the separate
ASPIRE-2A CPU baseline on required contest hardware before another Iris timing
sweep. CPU 25905006 is submitted for fresh N128 mesh identity and cut/restore;
review it before native parallel initialization and 40-step solve. Later compare
hierarchical/Scotch on matched target hardware, with independent repetitions
before any speedup claim. Do not pool Iris timings with CPU-site measurements.
