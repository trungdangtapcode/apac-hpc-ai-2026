# Native MPI-rank memory-policy comparison

## Question and hypothesis

Preparation-child-only interleaving lost the independent 40-step ABBA confirmation (2294800). The outer launcher-level diagnostic (2294801) applied policy to all 56 ranks but did not run the solver. The distinct hypothesis here is that `numactl --interleave=all` applied inside each MPI rank immediately before `simpleFoam` changes the native solver's memory policy and may affect its timing.

Diagnostic 2294802 qualified the mechanism: all 56 candidate ranks reported interleave across both NUMA nodes with an exact 8 MiB mapping; control ranks reported default policy and a single-node 2048-page mapping. Its affinity mapping was identical by rank. This supports testing the policy mechanism, not a solver speed claim.

## Controlled comparison

The four arms are `A1-default-solver`, `B1-interleaved-solver`, `B2-interleaved-solver`, and `A2-default-solver`. They retain the accepted Scotch source, initialized case, solver, runtime, physics, 40 steps / 39 timed intervals, sampler, and inherited preparation validation. Solver rank policy is the only treatment. The candidate arm's `mpirun` launches `numactl --interleave=all python3 rank_exec.py`; the wrapper reads the actual MPI rank and `numactl --show`, atomically records rank, policy, affinity, and PID, then `execvp`s `simpleFoam -parallel` in the same process. It performs no performance probe or memory touch.

Before using an arm's timing, the runner requires 56 unique rank proofs, the expected policy on every rank, nonempty nonoverlapping CPU affinities, and the same per-rank core map as the first arm. Native output, source, force trajectory, runtime identity, preparation, and payload checks from the parent bundle remain in force.

## Bounds and status

One exclusive Iris node, 56 CPUs, zero GPUs, low QoS, and a two-hour maximum. Each solver arm is capped at 1,500 seconds; the internal sequence deadline is 6,800 seconds and the outer job timeout is 7,190 seconds. The plan is a directional native comparison, not a scored contest run or a promised improvement. Offline checks do not authorize or imply scheduler submission.
