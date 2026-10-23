# Four-node default-Scotch replication plan

## Question and prior evidence

A sealed native review of the 23 October four-node collection found a 3.677906731 s/step mean for default Scotch at 128 MPI ranks per node (512 ranks total), after 150 solver steps with 149 timed samples. The 25921488 run's retained PBS request snapshot was queued, and current PBS history is unavailable. Its source was not proven to be the frozen submitted payload, and final scheduler accounting, native command return records, zero-field seals, and rank affinity were not collected. Treat the timing as a candidate native observation.

This new bundle is an independent, single-allocation replication attempt for the same 512-rank, four-node, 150-step default-Scotch configuration. The falsifiable expectation is that the complete native chain can reproduce the fixed numerical work and provide a fresh, auditable timing distribution. A similar mean would strengthen repeatability evidence, but one repeat with 149 serially correlated samples still does not prove a stable gain, establish a causal bottleneck, or create a new score/SOTA claim.

## Exact case and runtime changes

The read-only source is the accepted default-Scotch case from preparation job 25907236.pbs101, source revision `84c262431117f5c921db8335e368a12d0e9fa3f0`. The frozen case changes only `system/include/caseDefinition` (`nCores` 128 to 512) and `system/controlDict` (`endTime` 40 to 150). The decomposition method is already `scotch`; its default coefficients remain byte-identical. The field equations, boundary conditions, mesh controls, solver settings, function objects, and all other source files remain byte-identical. The payload manifest pins every included file and the accepted-source manifest retains the original source hashes.

The copied `PREPARATION.json` is intentionally preserved as provenance for the original accepted 128-rank Scotch preparation; its rank/end-time fields are not the derived run configuration. The effective prepared inputs are pinned separately and checked from `caseDefinition` and `controlDict` before execution.

Each allocation receives a new case copy in its unique PBS job directory. The only reused mesh is the previously verified unpacked directory `/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc/shared/polyMesh`, reached through the existing recorded shared path. The retained mesh identity is from preparation job 25907236.pbs101: official archive MD5 `50393a15d84f53255fda85ac702390e9`, SHA-256 `ef30fa8405dbaab77185ace2521b1bedc5650f245e40d7451259a5ac773a5376`, and eight checked member hashes. The allocation verifies those eight members before and after linking; it does not download or unpack the archive.

The wrapper records the allocation node file and effective environment, forces `OMP_NUM_THREADS=1`, and sets `FI_OFI_RXM_USE_SRX=0` to match the shared four-node runs. Other `FI_*` values are inherited from the loaded module/site environment and captured as observed; the payload invents no additional transport defaults. A bounded 512-rank startup probe must find four nodes, 128 ranks per node, one logical CPU per rank, and 512 distinct physical cores. It is allocation evidence only, outside solver timing; no continuous sampler or heavy profiler runs.

## Allocation, deadline, and lifecycle

The prepared PBS request is four exclusive CPU nodes, 128 CPUs and MPI processes per node, 440 GB per node, zero GPUs, `normal` routing, `scatter:excl` placement, and a 40-minute walltime. The maximum reservation is 341.333333 SU at the recorded one-SU-per-core-hour rate. The parent submission workflow owns the budget lock, fresh project/accounting and queue checks, durable reservation, intent, and any eventual qsub. This bundle does not create an intent, reservation, job, ledger edit, or submission.

A monotonic wrapper clock starts before module setup and every preparation step. Bounded commands stop at an internal 37-minute deadline, leaving three minutes before PBS walltime for cleanup and best-effort lifecycle/resource capture. A shell exit trap records wrapper return status, timestamps, elapsed wrapper time, and a best-effort live PBS resource snapshot. That snapshot and wrapper timing are not terminal PBS proof or billed cost; final scheduler/accounting evidence is still required after any authorized run.

## Native chain and review gates

The single case runs the full chain in fresh directories: serial `decomposePar -constant`, `restore0Dir -processor`, parallel `renumberMesh -constant -overwrite`, `potentialFoam -initialiseUBCs`, `applyBoundaryLayer -ybl 0.0450244`, and `simpleFoam -parallel` through Time 150. Every external OpenFOAM stage records its return code, native log, resource timing, phase timestamps, and a clean native `End`/no-fatal check. The decomposition must create exactly `processor0` through `processor511`, with 65,334,765 cells total. The solver must report v2512 double precision, 512 ranks, four native hosts with 128 ranks each, and fixed iterations Ux/Uy/Uz=15, p=12, omega=8, k=8 for every step.

The validator requires exactly 150 ordered solver times, 150 finite force-coefficient rows, 149 positive finite wall-clock samples for Time 2 through 150, exact time-index agreement with the native time-function file, matching per-step durations, the accumulated timer at every row, and agreement between native and recomputed means. It reports the full sample vector, mean, median, linearly interpolated p95, maximum and its Time, IQR fences/outliers, top steps, and force-coefficient range. No outlier is deleted or downweighted from the arithmetic Average. The OpenFOAM recommended sample count and actual short-sample warning are recorded as time-series diagnostics, not independent confidence intervals.

Zero-time fields are hashed after restore and again immediately before and after the solver. The initialized pre-solver seal must match the post-solver seal. Source and payload manifests are rechecked after execution. These native checks still do not substitute for frozen submission proof or terminal scheduler/accounting records.

## Falsification and stopping rule

Stop the allocation at the first source, mesh, topology, rank-count, native-stage, fixed-work, timer, force-output, field-seal, or deadline failure. Preserve the failed logs and lifecycle record; do not silently repair the case or repeat the same allocation to obtain a pass. A failed run is not a global research stop.

If every gate passes, compare the new untrimmed mean and full distribution with the prior candidate 3.677906731 s/step and disclose allocation/time-series limits. This single repeated observation can support or weaken the repeatability hypothesis; it cannot establish a speedup against other methods, causality, official acceptance, or a new best score. Any scored claim also requires the authorized frozen payload, final PBS state/exit, final output/field evidence, and authoritative posted charge review.

## Current status

Static bundle only; not deployed or submitted. Local source, shell, payload-manifest, and archived native-log replay checks are reported in `PRE_SUBMIT_REVIEW.md`. The shared mesh path cannot be inspected from this local environment, and the 512-rank affinity probe can only be qualified on an actual authorized four-node allocation. No HPC physical-placement or cost proof is claimed here.
