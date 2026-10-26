# Iris short screen: promising order change, not a confirmed score

Job **2294099 completed 0:0** on iris001 in 2,029 allocated seconds with 56 CPUs. Independent replay verifies 231 retained artifacts, the frozen 49-file runtime, both complete native outputs, 30 solver steps / 29 timed intervals per arm, unchanged fixed iterations, matching native wall-clock output, finite Cd rows, and unchanged source snapshots across isolated copies.

| Metric | xyz, first | zyx, second |
|---|---:|---:|
| Mean seconds per step | 32.592668524 | 23.811097072 |
| Median seconds per step | 31.978769372 | 23.721697773 |
| p95 seconds per step | 33.104158664 | 24.711300693 |
| Maximum seconds per step | 48.177250648 | 25.560905887 |
| Final Cd, dimensionless, step 30 | 0.441369407 | 0.437604579 |
| Native recommended minimum samples | 82 | 4 |
| Measured samples | 29 | 29 |
| GNU time major page faults | 398,390 | 31,526 |
| GNU time filesystem input count | 373,832 | 69,616 |
| GNU time aggregate CPU percentage | 5,545% | 5,547% |
| GNU time maximum RSS, KiB | 2,909,316 | 3,029,704 |

zyx took **26.9434% less time per step** in this pair. The control is below its native minimum-sample recommendation and the order is fixed. Preserve all slow intervals. Do not claim a confirmed 26.94% decomposition speedup, a full-length result or a new official score. Earlier Iris timings from another allocation are not this matched control. The NSCC reference remains separate.

The difference in page faults and filesystem inputs makes a reverse-order test more informative than immediately spending the remaining budget on an unmatched full-length candidate. These counters are associated observations, not proof of a cache or NUMA cause. GNU time process-tree CPU statistics and maximum RSS differ from total node residency; the Slurm batch MaxRSS is 140,228,748 KiB. No bandwidth, solver-time CPU mask, NUMA residency or kernel counters were collected. Prelaunch affinity probes observe 56 distinct singleton masks; they do not establish the solver's post-MPI binding.

Both solver stderr files initially report a missing dynamic wall-clock function library. Native logs then show `wmake libso`, and the completed timing function emits all 29 expected intervals. This is retained runtime compilation output, not an unexplained solver failure or empty stderr. Native work remains Ux/Uy/Uz 15 iterations, pressure 12, k/omega 8 at every step. Finite Cd and equal work do not certify official numerical accuracy. Both transient Cd values are at step 30 and must not be compared directly with a converged step-150 value.

Cost estimate is **31.562222 allocated CPU-hours**. Retire only this job's 42-hour reservation and retain a rounded 32-hour allowance: cumulative Iris allowance 169 of 224 hours, leaving 55 before a new reservation. This is an internal conservative ledger, not an Iris posted SU charge; SU rate is unknown.

Next: reverse the same two 30-step arms on one allocation, zyx then xyz, and collect lightweight memory/VM snapshots outside native timing. Keep the 42-hour maximum so the next commitment is at most 211 of 224. Require all existing evidence gates and the one-own-job cap; inspect the reverse result before deciding whether the apparent gain survives order effects. Close a gain claim if its direction follows execution order. Further confirmation still needs adequate samples and a budget decision.

Recovery: `raw-evidence.tar.gz` contains the exact retained small text records; `collection.json` records their SHA-256 hashes and actual Slurm accounting. Run `python3 replay.py` to verify without accessing the cluster. Full initialized fields and mesh remain remote, with byte seals and reproducible preparation retained; this archive does not contain those large binary trees.
