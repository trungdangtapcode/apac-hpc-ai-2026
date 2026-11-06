# Matched native forty-versus-forty-eight trial accepted

6 November 2026, Vietnam (UTC+7). Iris accepted **2294999** at 16:18:00 Vietnam; at 16:18:38 it is RUNNING on iris001, elapsed 38 seconds, 56 allocated CPUs and zero GPUs. Payload-before checks pass; the source40 preflight is in progress, with no solver arm started at this snapshot and no batch stderr. No new timing or complete benchmark is claimed.

## Question and hypothesis

Two opposite-order forty-step comparisons showed lower time at 48 than 56 ranks. A further reduction to 40 ranks might reduce communication enough to outweigh more work per process; it may also lose. The latest I/O-only treatment gave opposing paired contrasts amid large timing drift, so this allocation tests rank density with uncollated I/O fixed, rather than repeating unchanged I/O or placement flags. The primary outcome is absolute seconds per step; historical approximately 22-second observations remain unpassed.

## Exact controlled trial

Four arms **A1 control48 → B1 candidate40 → B2 candidate40 → A2 control48**, forty solver steps and 39 measured intervals each, in one exclusive iris001 allocation. Both use default MPI mapping/binding, uncollated file handling, native OpenFOAM v2512 DP, the exact organizer physics/fixed iteration inputs and unchanged 65,334,765-cell problem. Partition count and the corresponding initialized partitioned files differ. This is not a pure single-kernel test or a full official simulation.

N40 source is the actually initialized and reviewed 2294998 artifact; N48 is the source used by reviewed R2. Manifests are byte-equal to their reviewed origins. All other pinned physics input files match, with only rank-dependent caseDefinition different. Each arm is an isolated new clone, with no source inode reuse, exact zero-time field seals, strict per-rank files and native rank/precision/end/error gates. EndTime is exactly 40. Same-decomposition force repeats use the existing tolerance; no invented byte-identical cross-partition force gate is imposed. Runtime binaries/libraries, accepted source manifests and payload hashes are checked before/after. All intervals and whole-node telemetry are retained; rank proofs are pre-MPI_Init, not all solver helper threads or NUMA pages.

Root ran the offline/source/protocol checks and independently reviewed manifests, source transformations, control commands and timing envelopes. It caught an inherited 48/56-only READY parser before deployment; the new derived payload now accepts exactly 40/48, with actual complete manifest-shaped inventory traversal tests for both ranks and rejection of unselected 56. All **100 operational files** are frozen and unchanged after deployment. A separate helper schema mismatch (`passed` absent from the R2 review) failed before reservation or sbatch; the helper now checks the actual measurement_valid/complete-matrix/rank/runtime fields. The prior rejected attempt created no job and did not mutate the budget. Old submitted payloads are unchanged.

## Resources, acceptance and limits

One exclusive iris001 node, 56 allocated CPUs, zero GPUs, low QoS, at most **2.5 hours /140 allocated CPU-hours**. Each solver cap is 1,800 seconds; preparation 180 seconds; final reserve 480; complete initial arm window 8,400; internal runner 8,800; wrapper 8,940 under the 9,000-second wall. Insufficient remaining window stops rather than certifying a partial comparison. The internal stage increases **1,724→1,768 (+44)** to cover the selected bounded request: **1,628 consumed +140 reserved**. This is agent-selected planning, not a new owner budget or known billed site SU. NSCC CPU and AI ledgers remain separate.

Fresh queue was empty both before locked admission and immediately before sbatch. Actual receipt and job ID fulfil submission; the earlier prepared/deployed states alone did not. One-own-allocation cap is now occupied. Keep the reservation and frozen payload while running; do not fill the queue with duplicates. No background Codex, schedule, MFA retry or automatic chat wake-up is enabled.

A full terminal artifact review is required before interpreting means, force trajectories, tails and repeated contrasts. If a candidate loses unchanged, close that branch. If promising, the next decision must weigh order drift and credible controls rather than promoting a selected minimum. No speed claim is made here.

[Actual receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-vs48-20261106/submission-receipt.json). [Startup snapshot](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-vs48-20261106/post-submit-status.json). [Independent review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-vs48-20261106/ROOT_INDEPENDENT_REVIEW.json). [Frozen source/configuration](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-vs48-20261106/README.md).
