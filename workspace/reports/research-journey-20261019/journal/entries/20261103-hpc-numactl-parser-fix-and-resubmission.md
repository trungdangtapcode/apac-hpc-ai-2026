# Actual NUMA qualification submission, early failure and corrected retry

Recorded 3 November 2026, Vietnam time. HPC only.

**Question and prior evidence.** Incomplete job 2294671 left a promising first xyz contrast but a timed-out slower repeat. Aggregate telemetry cannot distinguish solver computation, MPI waiting or preparation-induced memory locality. The next bounded measurement qualifies a preparation mechanism, not another unqualified performance claim.

**Changed factor and control.** Four fresh copies of identical initialized Scotch source use inherited versus child-only interleaved policy in A/B/B/A order. Source physics, files and hashes are fixed. Extra initialization metadata is separately pinned (13 files, 50,497 bytes); the original 1,040 inputs remain unchanged. The test runs no solver. Node-wide counters do not locate file pages or certify causal placement.

**Actual failure.** Job 2294674 was accepted at 11:31:21, then FAILED 1:0 after one allocated second before any copying. The compute node reported interleave policy through `interleavemask: 0 1`. Our parser did not recognize this spelling, interpreted an empty mask, and rejected the preflight. This is our portability bug. Original submitted files and raw output are preserved. Allocation 0.015556 CPU-hours, conservative ledger 1; maximum 9.333333 retired once.

**Fix and validation.** R2 recognizes `interleavemask` while retaining the prior spellings. Its exact observed-output fixture passes. Only parser and job-name runtime files changed; inherited-policy equivalence, distinct-treatment, full-copy/source hash, inode and extra-path gates stay in place. No frozen payload was edited. [Derived bundle](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-numa-qualify-r2-20261103/README.md).

**Actual retry.** Job **2294675** accepted at **11:33:56 Vietnam**, observed **RUNNING on iris001 at 11:34:15**. One exclusive 56-CPU node, zero GPUs, low QoS, maximum ten minutes. Locked admission refreshed the queue and reserved 9.333333 CPU-hours. Ledger 985 consumed + 9.333333 reserved, unchanged stage 1009. [Receipt and dated state](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-numa-qualify-r2-20261103/STATUS.md).

**Assessment and next decision.** No mechanism result or speedup yet. Require four complete arms, actual distinct policies and all source/copy/post gates before deriving another hypothesis. Reconcile cost from terminal accounting once. A later solver trial must include finalization margin and matched controls. This job does not use NSCC/AI budgets or create background Codex schedules.

**Preservation.** Failed receipt and evidence, parser fix and corrected acceptance are separate safe checkpoints pushed to the existing private repository. Recovery metadata is refreshed separately; external artifact bytes are not uploaded by Git.
