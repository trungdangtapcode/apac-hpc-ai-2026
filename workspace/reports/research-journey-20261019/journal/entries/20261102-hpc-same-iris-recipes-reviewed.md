# Same-Iris organizer versus teammate runtime comparison

Reviewed 2 November 2026, about 07:35 Vietnam. Actual job **2294637 completed 0:0**, iris001, 56 allocated CPUs, 4,669 seconds. Frozen payload and all 209 collected-file hashes verify. All four arms pass native 40-step / 39-interval, fixed-iteration, source/copy/field and runtime/library checks. All 40-row Cd trajectories are identical; final Cd is 0.4369593310096111.

| Execution order | Runtime recipe | Mean seconds/step |
|---|---|---:|
| A1 | Organizer: default MPI, uncollated | 25.581958377 |
| B1 | Teammate: socket/core MPI, collated | 22.396949743 |
| B2 | Teammate: socket/core MPI, collated | 27.093606214 |
| A2 | Organizer: default MPI, uncollated | 30.164981109 |

Teammate is 12.4502% lower than the adjacent A1 and 10.1819% lower than adjacent A2. The ratio of the equal-length pooled means is **11.2228% lower**. This is a favorable, directionally consistent short-run signal for the supplied teammate runtime, not an optimization invented by us. Repeat means still change by +17.9151% for organizer and +20.9701% for teammate. Organizer native sample recommendations are 45 and 56 intervals against only 39 measured. Nonlinear drift and sampling uncertainty prevent calling this a stable scored-platform win.

All four launcher reports show identical rank/package/logical-core assignments for all 56 ranks. The measured difference cannot be explained by a changed reported rank map alone. Actual helper-thread affinity, page residency, cycles and bandwidth were not collected. GNU time and outside-interval CPU snapshots were inspected and retained in INSPECTION.json; they do not establish sustained clock speed or a causal bottleneck. Full stderr/native logs were inspected for warning/fatal markers. Command maximum RSS is not summed node memory, and aggregate CPU time may include MPI busy waiting.

Both treatments share the accepted initialized Scotch source. This compares the solver runtime flags on Iris, not the teammate's full preparation pipeline. It does not compare Gadi's 2.079 seconds with Iris's roughly 20–30 seconds, and does not rank Iris as a faster machine. Our own hierarchical zyx configuration is a separate experiment **2294640**, actually RUNNING on iris001 at 2 November 07:32:47 Vietnam after this predecessor finished. It has no result yet. Earlier per-arm progress snapshots are historical.

Accounting: 56 × 4669 / 3600 = 72.628889 allocated CPU-hours, conservatively 73. The original 140-hour maximum was retired once under the ledger lock. Current local allowance is **666 consumed + 140 reserved = 806 CPU-hours**, within internal stage 873. This is not billed site SU. The remaining reservation belongs to 2294640; preserve it and its queue position. No new job or extra spending was created by this review.

Next: review our running method ABBA, including both adjacent directions, repeats, correctness and diagnostic limits. Do not combine separate allocation means into a three-way ranking; a surviving Iris signal still needs matched full-length validation on an authorized scoring platform. No submission/slide or AI payload was changed.

Evidence: [terminal result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-recipes40-20261101/completed-2294637/RESULTS.md), including replay, raw artifacts and diagnostic inspection.
