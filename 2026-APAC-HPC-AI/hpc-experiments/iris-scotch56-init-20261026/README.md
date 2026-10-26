# Iris 65M Scotch N56 initialization draft

## Purpose and status

This is a derived, unsealed initialization kit based on organizer stage 13.2 for the already reviewed Iris Scotch 56-rank cut from job 2294040. It does not run `simpleFoam`, produce solver timings, or claim a score. It is prepared for root review; no remote files have been changed and no job has been submitted from this draft.

The intended unique workroot is `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z`. The submission directory is a new sibling `init-kit/` inside that workroot. The script follows organizer 13.1's artifact layout: the cut root's `runs/` contains job 2294040 evidence, and `artifacts/ready-N56-scotch/` is the existing owned cut in that workroot. It never copies, removes, truncates, or edits the cut kit or its logs.

## Admission and pre-mutation gates

The batch request is one exclusive 56-core Iris node, account `rdmaworkshop`, QOS `low`, all node memory, and a 20-minute wall limit. It loads the actual `gcc/11`, `hpcx/2.50`, and optimized OpenFOAM v2512 environment. It uses the organizer's `mpirun -np 56 -- utility ...` launch semantics and adds only Open MPI map and binding-report output flags; it does not prescribe a new binding policy.

Before writing to the cut artifact, the job requires:

- Slurm accounting for cut job 2294040 to be `COMPLETED`, exit `0:0`, with 56 allocated CPUs.
- The retained native cut-validation JSON to pass for exactly 56 Scotch ranks, 65,334,765 cells, and 336 restored time-zero fields.
- The cut stdout native pass marker and the cut source-after hash check to pass.
- Exactly processor0 through processor55, N=56 and `scotch`, no existing `READY` or initialization marker, and no prior job-specific evidence paths.
- All 41 pinned case inputs to match this kit and the operational cut copy. The permitted cut-time changes are explicit: `Allrun` is absent, `caseDefinition` specifies N=56/Scotch/(7 4 2), `controlDict` equals the pinned no-write variant, and `fvSolution` equals the pinned fixed-iteration variant.

It records a before hash inventory for the inputs and all 336 time-zero field files outside the cut artifact. Those field hashes are seals of the actual restored pre-initialization bytes; initialization is expected to change some fields, so the post hashes are captured independently and are not required to equal the pre hashes.

A bounded 56-rank hostname probe runs before any case mutation. It must report exactly ranks 0 through 55 on one node. The probe and all three utility logs preserve Open MPI's displayed rank map and observed binding reports. No solver executable is launched by the probe.

## Initialization and completion gates

The required order and arguments are unchanged from organizer 13.2:

1. `renumberMesh -constant -overwrite -parallel`
2. `potentialFoam -initialiseUBCs -parallel`
3. `applyBoundaryLayer -ybl 0.0450244 -parallel`

Each stage has its own 210-second timeout, further capped by a shared 1,140-second internal deadline so the last minute remains for cleanup. The 30-second cut/source gates, 60-second MPI probe, and 150-second field hashes also draw from that remaining deadline; a watchdog bounds module and shell startup. Each stage saves stdout/stderr in the workroot's `init-runs/` directory outside the kit and frozen cut, and must return zero, report `OPENFOAM=2512`, `scalar=64`, `nProcs : 56`, and the exact organizer command, contain a native `End` line, and contain no `FOAM FATAL`, `MPI_ABORT`, or `FATAL ERROR`. Afterward, source input checks and a separate 336-field hash inventory must pass. Only then does the script create the organizer-compatible `READY` marker with the exact upstream contents. `.INIT_IN_PROGRESS` remains as a no-resume guard if a stage fails; retrying requires a newly reviewed artifact.

All external evidence checks, source hashing, field hashing, the hostname probe, and each native stage have bounded timeouts under the 20-minute allocation. The payload source checksum list is verified before and after execution. The output directory `init-runs/` must exist before `sbatch`, because Slurm opens its batch stdout/stderr before the script starts. The review/submission driver is maintained separately by root.

## Offline review

Run `python3 review.py` from this directory. It exercises accepted and rejected cut evidence, accounting, source pins and operational variants, processor/field inventories, divergent pre/post field seals, rank completeness, and native log failure detection. It does not contact Iris or execute OpenFOAM.

Run `bash -n init.sbatch` and `python3 -m py_compile verify-init.py review.py` for syntax checks. Root review must still confirm the remote paths and captured job evidence before sealing or admitting the payload.
