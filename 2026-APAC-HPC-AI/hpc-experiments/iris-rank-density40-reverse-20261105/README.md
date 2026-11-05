# Iris Scotch rank-density reverse confirmation

This is a distinct reverse-order confirmation of the 40-step Scotch rank-density comparison: `B1-48, A1-56, A2-56, B2-48`. The prior 14-step observation belonged to a separate graph-placement branch at 56 ranks; its reverse lost 5.37%, and it was not a Scotch48 result.

The reviewed 40-step ABBA trial (job 2294916) completed all four arms. Preliminary means favored 48 ranks in both adjacent pairs, but the two 48-rank repeats differed by about 15.17%. This BAAB run tests whether that apparent benefit persists under reversed order. It uses the same pinned sources, physics, initialized fields, runtime, default file handler, 40-step horizon, and exclusive 56-CPU Iris allocation; only order is reversed. Rank counts and required Scotch partitions differ as before. MPI placement remains the default and must be observed from each launch; no per-socket balance is assumed.

The job retains the original 2.5-hour, 140 allocated CPU-hour maximum, zero GPUs, low QoS, 1,800-second solver caps and 150-second preparation caps. Each arm must complete 40 steps and all 39 timed intervals. Same-partition force repeats are paired by arm label with the existing tolerance. Cross-partition Cd drift is reported without an invented tolerance. This is a native confirmation trial, not a contest score or promotion by itself.
