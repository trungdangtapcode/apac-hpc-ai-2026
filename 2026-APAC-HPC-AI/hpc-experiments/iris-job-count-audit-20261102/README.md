# Audited Iris job count

Fresh observation: **2 November 2026, 07:38:24 Vietnam / 00:38:24 UTC**. This worker has **21 distinct accepted Iris jobs** in retained receipts, all matched by the live scheduler accounting query: **19 COMPLETED 0:0, one FAILED 124:0, one RUNNING**. This does not count teammates sharing the login, prepared/unsubmitted trials, or `sbatch --test-only` IDs.

Purpose breakdown: **13 full-size solver benchmark jobs** (11 completed, one failed/censored, one running), **six decomposition/initialization jobs**, and **two toy/MPI diagnostic jobs**. One job may contain multiple sequential comparison arms, so this is neither 21 distinct configurations nor 21 validated performance gains. No own stable scored-platform speedup is demonstrated.

| Job | Purpose | Scheduler state | Receipt |
|---|---|---|---|
| 2293751 | Toy practice or MPI diagnostic | COMPLETED 0:0 | [iris-practice-20261021](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-practice-20261021/submission.json) |
| 2293752 | Mesh decomposition or mandatory initialization | COMPLETED 0:0 | [iris-65m-20261021](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/cut-submission.json) |
| 2293753 | Mesh decomposition or mandatory initialization | COMPLETED 0:0 | [iris-65m-20261021](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/init-submission.json) |
| 2293754 | Full-size solver benchmark | COMPLETED 0:0 | [iris-65m-20261021](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/solver40-submission.json) |
| 2294040 | Mesh decomposition or mandatory initialization | COMPLETED 0:0 | [iris-scotch56-20261025](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch56-20261025/submission-receipt.json) |
| 2294046 | Mesh decomposition or mandatory initialization | COMPLETED 0:0 | [iris-scotch56-init-20261026](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch56-init-20261026/submission-receipt.json) |
| 2294047 | Full-size solver benchmark | FAILED 124:0 | [iris-matched-solver56-20261026](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-matched-solver56-20261026/submission-receipt.json) |
| 2294097 | Mesh decomposition or mandatory initialization | COMPLETED 0:0 | [iris-hierarchical-order56-r2-20261026](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-hierarchical-order56-r2-20261026/submission-receipt.json) |
| 2294098 | Mesh decomposition or mandatory initialization | COMPLETED 0:0 | [iris-order56-init-20261026](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-init-20261026/submission-receipt.json) |
| 2294099 | Full-size solver benchmark | COMPLETED 0:0 | [iris-order56-screen30-20261026](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-screen30-20261026/submission-receipt.json) |
| 2294132 | Full-size solver benchmark | COMPLETED 0:0 | [iris-order56-reverse30-20261026](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-reverse30-20261026/submission-receipt.json) |
| 2294148 | Full-size solver benchmark | COMPLETED 0:0 | [iris-order56-zyx50-20261027](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-zyx50-20261027/submission-receipt.json) |
| 2294234 | Full-size solver benchmark | COMPLETED 0:0 | [iris-order56-full150-20261027](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-20261027/submission-receipt.json) |
| 2294262 | Full-size solver benchmark | COMPLETED 0:0 | [iris-order56-full150-reverse-20261028](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-reverse-20261028/submission-receipt.json) |
| 2294358 | Toy practice or MPI diagnostic | COMPLETED 0:0 | [iris-mpi-affinity-20261029](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-mpi-affinity-20261029/submission-receipt.json) |
| 2294366 | Full-size solver benchmark | COMPLETED 0:0 | [iris-graphmap-screen-20261029](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-screen-20261029/submission-receipt.json) |
| 2294390 | Full-size solver benchmark | COMPLETED 0:0 | [iris-graphmap-reverse-20261029](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-reverse-20261029/submission-receipt.json) |
| 2294634 | Full-size solver benchmark | COMPLETED 0:0 | [iris-collated40-20261101](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-20261101/submission-receipt.json) |
| 2294635 | Full-size solver benchmark | COMPLETED 0:0 | [iris-collated40-reverse-20261101](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-reverse-20261101/submission-receipt.json) |
| 2294637 | Full-size solver benchmark | COMPLETED 0:0 | [iris-recipes40-20261101](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-recipes40-20261101/submission-receipt.json) |
| 2294640 | Full-size solver benchmark | RUNNING 0:0 | [iris-own-zyx40-20261102](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx40-20261102/submission-receipt.json) |

The failed 2294047 completed hierarchical xyz but hit the time limit inside Scotch; it is not a complete matched performance result. Two later full-length jobs compare hierarchy axis orders and their reversal did not reproduce a stable gain. Other completed screens also have sampling/drift limits; scheduler success alone is not a winning or scored measurement.

Current 2294640 is the separate hierarchical zyx versus Scotch ABBA. At 07:37:15 Vietnam its first control was at native step 13/40; at 07:38:24 the allocation remained RUNNING. The completed organizer/teammate ABBA 2294637 favors the supplied teammate runtime by a drift-limited pooled 11.22%, not our own configuration.

The owner challenged why a week of work had not produced a gain. The evidence supports that native experiments did run, but their losing/reversed outcomes leave the performance objective unmet. Access/qualification work and delayed completion of the key matched method comparison did not deliver a validated speedup. Do not answer “no result yet” as though no previous work ran; distinguish the newly running comparison from the complete historical record. This is a retrospective assessment, not fabricated contemporaneous reasoning.

All submission receipts are hash-bound in [RECEIPTS.json](RECEIPTS.json), alongside the fresh raw scheduler reply. Existing source logs and failed evidence remain unchanged. No new job, spending, background process, or submission-package change was introduced by this count.
