# Pre-submit review: four-node default-Scotch replication

**State: STATICALLY PREPARED, UNSUBMITTED.** No SSH, deployment, scheduler intent, reservation, ledger change, or `qsub` was performed. Submission and fresh queue/accounting checks remain with the parent workflow.

## Source and payload

The payload derives from the accepted default-Scotch source in `nscc-cpu-scotch128-20261021/payload/case`, preparation job 25907236.pbs101, revision `84c262431117f5c921db8335e368a12d0e9fa3f0`. A byte comparison confirms exactly two source edits: `nCores` 128 to 512 and `endTime` 40 to 150. The method stays default Scotch and all default coefficients, solver numerics, field definitions, function objects, and other case files are unchanged. The accepted-source hash list, all payload file hashes, and the prior recorded mesh manifest are included.

The case's retained `PREPARATION.json` describes the original 128-rank Scotch preparation and is preserved byte-for-byte as provenance. Runtime rank and endpoint values are validated from the derived `caseDefinition` and `controlDict`, not inferred from that historical metadata file.

The known mesh source is the existing shared directory `/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc/shared/polyMesh`. The prior accepted preparation records the official archive path `/scratch/users/industry/hpcadvisorycouncil/pengzhi/public/2026-apac-hpc-ai/openfoam/polyMesh_65M.tar.gz`, MD5 `50393a15d84f53255fda85ac702390e9`, and SHA-256 `ef30fa8405dbaab77185ace2521b1bedc5650f245e40d7451259a5ac773a5376`. The payload checks each of the eight retained unpacked-member SHA-256 values at that known shared path before use. That path is not mounted in this local environment, so the mesh files were not checked here and the payload makes no new physical mesh claim.

## Static and offline checks

- `bash -n payload/pair.pbs` passes.
- All payload Python files compile in memory without writing bytecode.
- Payload membership and every file SHA-256 pass; the derived case has exactly the accepted file set and the only allowed modifications.
- An independent byte comparison against the canonical source confirms exactly the two stated line edits and no other changed source bytes.
- The timer validator replays the sealed prior S128 native collection at the actual archive member prefix `runs/4n-scotch-25921488/`. The raw archive SHA-256 matches its collection manifest (`2910c573166cef4ebd07c5fc5a3c6ddfbc1d6a10819007f7fa828b8be6edd933`). It reproduces 150 ordered steps, 149 timed samples, exact solver-log/time-function sample agreement, accumulated-time agreement, the 3.677906731 s/step mean, and all 150 finite force rows. This is validator-only replay of retained evidence; it is not a new run or proof of scheduler completion, placement, source submission identity, or mesh availability.
- Processor directory validation uses numeric IDs as a set and explicitly requires `processor0` through `processor511`; it avoids the earlier lexical-list and stale 40-step validator assumptions.

## Runtime design and limits

The PBS script requests four exclusive nodes with 128 CPUs/MPI processes and 440 GB each, no GPUs, normal routing, `scatter:excl`, and 40 minutes. Maximum reservation: 341.333333 SU. Its internal deadline is 37 minutes from before module setup, leaving three minutes of cleanup margin. It records module and effective `FI_*` values, PBS nodefile, timestamps/phases, each OpenFOAM stage return code, native logs, field seals, rank-probe records, wrapper lifecycle, and best-effort pre-exit live PBS resources. It explicitly sets SRX-off to match the reviewed shared run and leaves other FI flags at their observed site/module values.

The full run performs serial `decomposePar -constant`, restores initial processor fields, runs `renumberMesh`, `potentialFoam`, `applyBoundaryLayer`, and the 150-step `simpleFoam`, then validates all fixed work and output timing. It uses a fresh case root per PBS ID and the known shared mesh only. Source and zero-time initialized fields are checked before and after their relevant stages.

The four-host / 512-unique-physical-core probe, actual module environment, shared mesh contents, command timings, terminal PBS result, final allocation charge, and frozen scheduler-submitted bytes remain unobserved until a separately authorized job is run and reviewed. A live `qstat` query or wrapper status alone will not be presented as terminal proof. The proposal is a repeatability check, not a new performance claim. No failed run may be deleted or replaced by a quiet retry.

## Root integration and current launch authorization

The owner explicitly raised the cumulative CPU ceiling to 5,000 SU, conservatively including shared use, on 23 October. The ledger retains 4,524.2 SU before this new request; adding this maximum produces 4,865.533333 SU. Historical missing-job costs remain reserved and no old final state is invented. Fresh account CPU/AI queues were empty. The actual submitter checks both queues and project rate/balance again under the CPU lock; a new shared CPU job or a breached cap stops submission.

Root found and corrected the nodefile Counter guard before first submission: a Counter contains four host keys with multiplicities summing to 512, not 512 keys. A synthetic four-host/512-rank fixture now passes, and an incomplete nodefile is rejected; this tests guard logic, not actual physical placement. Root independently verified all 54 payload hashes and the two exact canonical source edits. The sealed earlier 150-step S128 archive replay passes 149 matched samples and native mean 3.677906731 seconds/step; that is old evidence, not a result from this new bundle. qualification.json retains these checks and limits. The deployment hash response confirms the fresh scratch copy.

The local deploy-submit.py separates staging from submission, handles CPU and AI server suffixes and job-array IDs, writes an fsynced unique intent and full maximum reservation before one qsub, and retains them on ambiguous output. The receipt and PBS resource proof must still be reviewed. No repeated submit or inherited afterok dependency is used. The first intent remains a one-way gate; query the scheduler rather than running this script again after it exists.
