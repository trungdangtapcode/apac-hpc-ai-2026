# Native Iris screen: copy preparation policy

## Question

Does interleaving memory for the short copy-and-hash process change a native OpenFOAM solver screen when the solver command is fixed and the launcher parent retains its inherited memory policy? The preceding preparation qualification (job 2294675, reviewed separately) observed `FilePages` deltas of approximately +9.78 GiB on node 1 and +0 on node 0 for each inherited-policy arm, and approximately +4.89 GiB on each node for each interleaved arm. These are node-wide cumulative counters, not process-attributed placement; they do not prove that preparation policy changes solver performance. This job makes the direct, bounded solver comparison.

## Controlled comparison

All four arms use the same accepted Scotch N=56 initialized source, original physics and fields, Iris node, OpenFOAM v2512 double-precision runtime, `mpirun -np 56 --report-bindings --display-map`, uncollated file handler, five-second node sampler, and 20 solver steps (19 intervals). The runner requires `WM_PROJECT_VERSION=v2512` and `WM_PRECISION_OPTION=DP`. Every arm gets a fresh copied case. The only intended treatment is the policy of the copy/hash child:

| Arm order | Copy/hash child | Launcher parent policy |
| --- | --- | --- |
| A1 | inherited policy | same frozen inherited policy |
| B1 | `numactl --interleave=all` | same frozen inherited policy |
| B2 | `numactl --interleave=all` | same frozen inherited policy |
| A2 | inherited policy | same frozen inherited policy |

The runtime checks that the B child actually reports interleave across both NUMA nodes; it rejects the trial before copying if B and inherited policies are effectively identical. It checks the solver parent's effective memory policy before each solver and requires it to match the frozen inherited policy. Source and destination checks cover the accepted 1,040-file solver manifest plus the separately reviewed 13-file supplementary initialization manifest and explicit directory inventory. Copies are unique and retained. Source files are never modified.

The derived bundle reuses the native solver/runtime helpers from `iris-xyz20-scotch-screen-20261103` and the verified copy/hash guard from `iris-preparation-numa-qualify-r2-20261103`. Only this new bundle's runner, resource envelope, and treatment selection are derived. The earlier native bundle remains frozen.

## Bounds and interpretation

The Slurm request is one exclusive Iris node, 56 CPUs, no GPU, 75 minutes, low QoS. Each solver arm is capped at 1,000 seconds; copy/hash is capped at 50 seconds and the solver-policy check at ten seconds. Before the first arm, four full 1,060-second windows plus 180 seconds of finalization must fit the 4,480-second internal deadline. That leaves at most 60 seconds for source/runtime preflight. The earlier qualification needed about 32 seconds for the 10.5 GiB source hash and roughly ten seconds for field/runtime checks, so the gate has limited margin; a slower preflight fails before the first solver arm. Before every later arm, the runner rechecks the remaining full-arm and finalization budget and never silently shortens a solver cap. The 70 CPU-hour request is a bounded job envelope, not a statement of the owner’s total project allowance.

The comparison is a 20-step directional screen, not a complete simulation, contest score, or promotion. ABBA balances simple linear time drift but not nonlinear node activity. Page-cache state can persist between arms. Whole-node `meminfo`/`numastat` counters and five-second procfs samples are diagnostic observations, not per-process page placement, bandwidth, or proof of cause. A performance difference would need a longer, independently reviewed confirmation under the same matched runtime.

No job is submitted by this prepared payload. Scheduler acceptance, job ID, reviewed results, and budget reservation must be recorded separately by the owner-controlled admission process.

Policy observations come from the runner immediately before `mpirun`, not from inside individual MPI ranks. Launch commands and environment remain fixed. No per-rank memory-policy measurement is claimed. A final cross-arm force-coefficient check requires equal trajectories within relative 1e-9 / absolute 1e-10 tolerances; frozen payload hashes are checked before and after runtime.

Stopping rule: a valid directional gain requires all four native/source/runtime gates, both adjacent contrasts favorable, and explicit inspection of repeat drift and tails. This does not certify significance. If only startup/preparation changes or the solver contrast reverses, do not promote a solver gain; preserve the negative result. Any promising signal needs a longer confirmation.
