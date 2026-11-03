# Native solver test actually submitted

**Job 2294676 accepted 3 November 2026 at 13:57:02 Vietnam (UTC+7)**. At 13:58:42 the scheduler reported RUNNING on iris001, elapsed 1:40. Source and official-input checks passed; the first inherited-policy copy/hash took 38.612 seconds and passed. The launcher-parent policy check passed. The first actual OpenFOAM arm started at 13:58:25 with equal five-second sampling. No completed arm mean or speedup is available in this dated snapshot.

Four arms use the identical initialized Scotch source and unchanged native solver command, numerical settings, v2512 DP build and uncollated file handler. Only the copy/hash child's memory policy differs: inherited / interleaved / interleaved / inherited. Policy is observed in that actual preparation child and in the runner before each solver; individual MPI-rank memory policy is not collected. Each solver arm has 20 steps / 19 intervals and a 1,000-second cap. Maximum request: one exclusive Iris node, 56 CPUs, zero GPUs, 75 minutes, low QoS.

The parent preparation qualification 2294675 proved that the applied policies produced different repeated node-wide counter patterns; it did not measure a solver gain. This test can falsify the proposed performance effect. Full native/source/runtime/payload gates and cross-arm force-coefficient agreement must pass. It remains a short directional screen requiring longer confirmation if favorable.

## Locked accounting

Existing agent-selected stage 1009 had 989 consumed and zero reserved. The selected 70 CPU-hour maximum requires 989 + 70 = 1059. The documented stage record therefore adds only 50 to reach 1059, then reserves 70 for this one job. Fresh queue checks found no other owned job. This is a bounded internal planning change, not a site SU grant or an owner-specified total allowance. No NSCC/AI debit and no automatic schedule.

## Review route

`collect_completed.py` is prepared for the new arm labels and refuses an existing collection directory. It may run only after terminal state and verifies retained bytes/frozen hashes. It does not collect binary field trees or constitute review by itself. Independently inspect full arm count, exits, source/copy/post checks, actual policy scope, timing/Cd/native counters, tail/repeat behavior, telemetry availability and cost. Retain failures as failures; retire the reservation once from actual accounting.
