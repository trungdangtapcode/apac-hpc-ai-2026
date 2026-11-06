# R3: single-pass preparation with unchanged native experiment

This derived bundle preserves failed job 2295000 and changes only preparation verification and phase reporting. The actual timeout substage was not observed. It applies the complete-tree verification pattern used by successful 2294997, with each clone core inventoried once and all supplementary/path/field/inode checks retained. The source is checked before and after; the same native forty-step 48/40/40/48 test, default MPI and uncollated I/O remain. Root regression executes the real preparation CLI on an offline fixture with a clearly synthetic launcher; this does not qualify real MPI.

# Rank-density comparison: Scotch40 versus Scotch48

## Research question

On one Iris node, does the initialized 40-domain Scotch case run faster per step than the initialized 48-domain case while keeping the same mesh, physics, OpenFOAM build, MPI placement policy, I/O handler, iteration limits, and solver horizon?

## Evidence and hypothesis

Two earlier complete forty-step comparisons on Iris reported lower pooled time for 48 than for 56 domains: 26.704 versus 32.322 seconds per step in job 2294916, then 26.159 versus 32.381 in reversed-order job 2294918. This is scoped to that initialized pair and does not establish a universal optimum. Job 2294997 compared 48-default with collated and uncollated I/O; its repeats drifted in opposite directions, so the I/O change was not promoted. The Scotch40 cut 2294919 retained all 65,334,765 cells, and initialization job 2294998 produced an independently reviewed READY source. Those facts justify a distinct, direct 40-versus-48 trial; cell balance does not predict runtime.

Fewer partitions may reduce MPI communication, but each rank then handles more cells and local work. The experiment must measure both effects together in the native solver. A 40-rank win remains a hypothesis until the four complete arms and all source/runtime/force gates pass.

## Matched design

One exclusive iris001 node, 56 allocated CPUs, zero GPUs. Four arms run in ABBA order: `A1-control48`, `B1-candidate40`, `B2-candidate40`, `A2-control48`. Each arm uses 40 physical solver steps and 39 measured intervals. Both sources use the official 65,334,765-cell mesh, OpenFOAM v2512, double precision, identical pinned physics inputs and fixed solver iteration counts. Both use default Open MPI mapping and the default uncollated file handler. Only the initialized Scotch partition and partitioned input files vary. The N40 source receives the exact mandatory organizer initialization before READY; the N48 source is the accepted initialized control.

Per-arm source clones are isolated and hash-checked. The exact qualified exclusive per-rank proof writer and reader are retained from job 2294996. A new thin CLI wrapper selects 40 or 48 ranks through the already qualified generic reader API; it does not alter either protocol byte stream. Solver outputs retain rank binding reports, force coefficients, whole-node samples, per-command resource use, and before/after source, payload, and runtime identities.

## Admission and acceptance

The frozen Slurm request is one exclusive Iris node, `iris001`, 56 allocated CPUs, 56 task slots, no GPU, low QoS, and at most 2.5 hours. The internal deadline preserves four full solver windows and final validation. Before deployment, a root review must verify every selected hash, the passing terminal initialization review for 2294998, and all offline acceptance/rejection checks. Immediately before `sbatch`, the helper rechecks the shared Iris budget lock, current ledger, actual queue, READY source review, exact deployed hashes, and absence of another own active `tu-` allocation. It reserves at most 140 allocated CPU-hours; this is an internal bounded planning allowance, not known billed site SU or a new owner-set budget.

The run is valid only if all four arms reach native step 40 and `End`, have exactly 39 positive time intervals and 40 force records, pass source and field gates, use complete non-overlapping per-rank proofs, retain all expected Open MPI binding reports, match the runtime identity before and after, and pass same-partition force-repeat checks for both N40 and N48. Compare the two-replicate mean and median of seconds per step, both repeat values, paired contrast, tails, and telemetry. Never require bitwise-equal force trajectories across different domain counts, and never infer a causal bottleneck from the timing result.

This is a native forty-step comparison, not a full official simulation or a scored contest result. Historical approximately 22.4-second Iris runs remain the absolute reference to beat.
