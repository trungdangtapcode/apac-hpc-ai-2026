# Native Scotch 100:1 follow-up admitted on Iris

**Job 2294670 was accepted on 3 November 2026 at 00:24:52 Vietnam**, then observed RUNNING on iris001 at 00:25:02. One node, 56 CPUs, zero GPUs, maximum 30 minutes / 28 allocated CPU-hours. This is native decomposition and graph screening with conditional mandatory initialization, not a solver benchmark.

## Question and controlled change

Parent job 2294657 increased logical cross-package interfaces by 37.7308% under synthetic 10:1 weights and was rejected before initialization. The pinned OpenFOAM wrapper does not demonstrate a reversed weight vector; actual SCOTCH library labeling remains untraced. This single follow-up asks whether a stronger synthetic preference changes that outcome. Domains remain `(2 28)`; only `domainWeights (1 0.1)` becomes `(1 0.01)`, normalized to 100:1. Mesh, 41 canonical input pins, accepted control, graph grouping, numerical work, and all five graph gates remain fixed. This is not a measured hardware cost model.

## Frozen and submitted evidence

The root-reviewed 53-file payload passed canonical and wrong-treatment rejection fixtures, syntax checks, and isolated one-shot admission fixtures. It was committed before deployment. Remote root:
`/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch2x28-w100-init-20261102T172209Z`.

Deployment reply timed out, but one read-only reconciliation found its unique root, replayed all 53 hashes and both manifests, and verified no remote submission intent. No duplicate deployment was issued. A subsequent submission attempt timed out during its read-only queue preflight, before local intent/reservation/sbatch. Their absence and zero outstanding reservation were checked before one bounded retry. That retry obtained the definite receipt 2294670. The account queue was empty before admission; a budget lock, durable intent and reservation preceded exactly one sbatch.

## Acceptance, cost, next decision

Existing internal stage 1,009 allocated CPU-hours; 944 consumed plus 28 reserved = 972 committed. No stage increase or billed SU claim; no NSCC or AI accounting changes. A passing graph must still complete native initialization and seal READY before a separately admitted solver comparison. If graph gates reject, preserve the raw negative outcome and close further weight-only tuning for this topology. A stopped or successful setup allocation is not a speed result. No measured solver gain yet.

Hardware collection includes lscpu and available per-command resource timing. CPU utilization, hardware communication costs, bandwidth counters and cycle profiles are not yet inspected or claimed. Review runtime/source/graph/output gates and cost after completion.

[Payload and receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch2x28-w100-init-20261103).
