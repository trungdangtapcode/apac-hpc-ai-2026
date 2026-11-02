# Our hierarchical zyx choice versus default Scotch

Question: does our tested hierarchical `(7 4 2)`, `order zyx` configuration improve native solver timing relative to default Scotch on a matched Iris allocation? The method is standard OpenFOAM, not an algorithm we invented. Our contribution is the parameter selection and its experimental validation, which has **not established a stable gain yet**.

Prior evidence does not answer this exact question. Job 2294047 completed a hierarchical xyz reference but timed out before its Scotch arm finished; its matched-prefix advantage was censored. Full jobs 2294234/2294262 compared hierarchy orders only and reversed the apparent winner when execution order changed. Graph-placement gains failed confirmation and are not revived here. The current 2294637 organizer/teammate run uses Scotch in both recipes; it cannot test our alternative decomposition.

## Controlled comparison

| Treatment | Mesh decomposition | MPI and I/O |
|---|---|---|
| A: organizer baseline | Default Scotch, 56 subdomains | Default native MPI, uncollated |
| B: our configuration | Hierarchical 7x4x2, order zyx, 56 subdomains | Same default native MPI, uncollated |

One exclusive Iris node, 56 ranks, same official v2512 double-precision build, original 65M mesh, fixed physics/fvSchemes/fixedIter/function objects and 40 steps / 39 timings each. The physical problem and numerical work are fixed; **partitioned meshes and initialized fields differ by method**. Both method-specific full initialization chains previously passed review and each exact 1040-file accepted source is rechecked. Candidate source is initialized/order-zyx from job 2294098, not the older original h742 xyz source. Source_case checks use the same 41 canonical pins with only permitted decomposition transforms.

Execute **Scotch → our zyx → our zyx → Scotch** on independent copies. Common --report-bindings/--display-map diagnostics and passive node snapshots are outside measured solver steps. Preserve initial fields, validate independent copy inodes, all 40 steps, 39 native timings/wall-file rows, iteration counts 15/12/8/8, 40 finite Cd rows, actual uncollated I/O, stable executables/libraries and source after execution. Do not require Cd to be bit-identical across different decompositions; report trajectories and sanity context without inventing a universal Basic tolerance band.

The primary mean ratio and both adjacent effect directions must be reviewed alongside repeated controls, trends/tails and warnings. A method-specific initialized source is held fixed for that treatment; this does not pretend the two partitioned fields are identical. ABBA balances linear drift but does not establish independent repeated-allocation confidence. Iris one-node 40-step performance is not an NSCC/Gadi four-node 150-step score. Success would justify subsequent confirmation, not automatic promotion.

## Bounded dependent job

Request one exclusive node / 56 CPUs / zero GPUs / maximum 2.5 hours = 140 allocated CPU-hours. Protected four full 40-step solver windows, 64 GiB filesystem-free preflight, original source pins and both full accepted manifests are retained. The new job is conditioned on **afterany:2294637**, preserving one active own CPU allocation; only that exact predecessor may already be queued/running. A failed preceding optional experiment must not stop this independent native comparison, which applies its own input/correctness gates. No predecessor cancellation, frozen mutation or Codex background schedule.

The standing research execution contract requires justified followups during active research. This current owner inquiry concerns our own configurations. The agent selects only this one bounded 140-hour experiment: 593 consumed + 140 current maximum + 140 new maximum = 873 CPU-hours, a transparent 103-hour extension of the agent-selected 770 internal stage, not an owner numerical cap, site SU grant or NSCC/AI debit. Intent and maximum reservation are written under lock before one sbatch call; unknown outcomes retain the maximum and block replay. Preparation alone is not submission.

The already-running organizer/teammate comparison is preserved. Its results and this separate comparison must be evaluated relative to each allocation's own controls, not by pooling raw seconds across different times. No winner or achieved optimization is claimed before complete independent review.
