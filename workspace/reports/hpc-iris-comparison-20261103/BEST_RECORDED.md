# Lowest observed completed mean for the three Iris recipes

The owner asked for concrete best observations, not pooled comparison means. These are the lowest reviewed whole-arm means found in the retained Iris records for each group. Every mean includes all prescribed timing intervals in that completed arm. It is not the fastest individual step. Timeout and live unreviewed output are excluded.

| Recipe group | Lowest mean, seconds/step | Job / arm | Steps / timed intervals |
|---|---:|---|---:|
| Ours: hierarchical zyx with graph-based placement | **21.051168942** | 2294390 / B1-graph | 14 / 13 |
| Organizer (BTC): Scotch, default MPI, uncollated | **22.358237138** | 2294640 / A1-scotch | 40 / 39 |
| Supplied teammate runtime settings ported to Iris | **22.396949743** | 2294637 / B1-teammate | 40 / 39 |

These are separate observations with different horizons and allocations, not a matched three-way ranking. Our 14-step diagnostic is particularly short. The graph-placement branch still lost its complete reversed comparison; the lower selected arm does not establish a stable optimization.

Our zyx also completed **50 steps at 21.112004724 s/step** in 2294148 and **150 steps at 21.229593669 s/step** in 2294234. Calling 21.2296 the absolute fastest completed Iris mean was too broad: it is the retained 150-step value, not the minimum across all screening horizons. The raw records have not changed; this clarification supersedes any absolute-minimum interpretation of earlier answers.

The 21.431810307-second Scotch arm in 2294635 uses the teammate's `--map-by socket --bind-to core` with uncollated I/O. It is a hybrid, not the unchanged organizer launch recipe, and is not assigned to the organizer row. The teammate row covers the settings actually ported to Iris, not the whole Gadi environment.

The earlier 24.75 and 27.87 numbers are pooled teammate/control means within job 2294637. They answer a different question from each group's lowest completed arm. [Matched comparisons](README.md) retain the direct contrasts and contradictory repeats. No NSCC/Gadi timings enter this table.

[BEST_RECORDED_EVIDENCE.json](BEST_RECORDED_EVIDENCE.json) pins exact source values and hashes. The audit includes older lowercase and newer uppercase review files, list and dictionary arm schemas, and the 14/30/50/150-step branches.

At **3 November 2026 14:29:10 Vietnam**, native job 2294676 remained RUNNING on iris001, elapsed 32:08. It is not counted as a reviewed new best. The owned allocation remains occupied; this clarification changes no budget, queue or submitted payload.
