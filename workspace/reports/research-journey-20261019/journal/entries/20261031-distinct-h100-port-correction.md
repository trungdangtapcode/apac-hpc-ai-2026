# Correct the candidate count and isolate the remaining chunk interaction

The owner repeatedly asked whether the next four best H100 configurations were
being measured on H200. Correct the earlier interpretation: the first four jobs
were four measurements, not four distinct H100 recipes. A H200 control and N54/
N64 of one H100 recipe were included. The original four-distinct-port request
is not fulfilled by that count.

Prior evidence: H100 peak 222048 and fresh 225227 repeat the same both-HPC-Ops/
chunk 4096 family. H100 6144 job 221828 scored 2411.995 versus 2413.802 control;
H100 8192 job 222282 scored 2382.811874 versus 2401.577649 control. Neither is a
proven gain. H200 27783 at N64 uses both-HPC-Ops/chunk 4096 and shows prefill queue
means 7.3750/4.4583 with TTFT 1591.493 ms; H200 27777 uses DeepGEMM/chunk 8192 at the
same N64 and scores 3038.022907 versus 2721.815800. That comparison couples two
serving factors and leaves a question worth measuring.

Hypothesis: larger chunks may reduce the observed waiting work with HPC-Ops,
and the 8192 point permits a same-chunk runner comparison. Prepare S114 (6144) and
S115 (8192) from actual frozen 27783, changing only prefill chunk and native graph
maximum/buckets. Keep current native N64, HPC-Ops both phases, FlashInfer decode,
FA3 prefill, topology, precision, caches, transport, workload and output gates.
Sixteen explicit CPU fixtures verify actual chunk/graph/backend acceptance and
reject mismatches; they are synthetic CPU data, not GPU evidence.

Each job maximum 16 H200/two nodes/17 minutes, 4.533334 GPU-hours; pair 9.066667,
zero PBS SU, own cap five. Compare with prior same-day 27783 for chunk sensitivity
and 27777 for incumbent selection; old controls and varying generated seeds are
limitations, so useful gains require a new independent confirmation. No such
gain is claimed at preparation.

The source audit does not establish four different winning untested H100 recipes.
Only two new informative ports are ready; two candidate slots remain unfilled.
Record this honestly rather than repeat unchanged losses to fill four entries.
Actual IDs and reservations follow after admission. Preserve prior raw failures,
H100/H200 attribution and the other worker's HPC payloads.

[Plan and source evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/PLAN.md).

## Definite admission

At 2026-10-31T13:30:58.841019+07:00, Slurm accepted **27804** (HPC-Ops prefill 6144) and **27806**
(prefill 8192), both N64/16 H200/two nodes/17 minutes. The shared admission lock
protected fresh cap-five/site/queue checks, frozen hashes and sbatch validation.
Preparation/16 CPU fixtures were committed and pushed in 94980434 before actual
submission. Maximum pair 9.066667 GPU-hours, zero PBS SU. Actual queue snapshot:

```text
27806|ap42-s115-hpc8192|PENDING|0:00|2|(Resources)
27804|ap42-s114-hpc6144|RUNNING|0:21|2|g[1,4]
```

No measured result yet, and the request for four distinct additional ports is
not fully satisfied: only two qualified candidates were identified/admitted.
Preserve that gap. Do not count prepared ideas, controls, retries or separate
loads as additional H100 methods. [Actual receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/STATUS.md).
