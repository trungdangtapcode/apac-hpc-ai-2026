# H200 attention transfer: definite acceptance, no performance result

Observed 2026-10-31T10:26:03.546470+07:00, Vietnam time (UTC+7). Slurm accepted **27777**
(fresh FlashInfer control, S110) and **27779** (FA3 decode candidate, S111).
Both are independently submitted without dependencies, on two nodes / 16 H200,
each at most 17 minutes / 4.533334 GPU-hours. Pair maximum 9.066667 GPU-hours; zero
PBS SU. Current snapshot:

```text
27779|ap42-s111-fa3|PENDING|0:00|2|(Resources)
27777|ap42-s110-flashinfer|PENDING|0:00|2|(Resources)
```

The admission lock protected a fresh own-queue cap 5 check, manifest verification,
site query and sbatch test. Definite receipts and reservations are retained in
[admission/](admission/); actual frozen payload manifests are bound in each receipt.
The prepared code and 12 CPU backend/runtime fixtures were captured and pushed in
b0bbbd5a before sbatch. No old job was modified, cancelled or requeued.

Change only decode attention; retain native N64 and full 60/120/30 plus all prior
source, physical KV, both semantic P/D routes, output/error/runtime gates and
five-second telemetry. Both inherit harness arm=control to mean no draft; actual
study_arm identifies treatment. An FA3 H100 latency tradeoff is the rationale,
not an H100 win or promised H200 speedup. Official quality remains UNKNOWN.

Two jobs are enough for the initial question. Only a valid gain above 1% with
acceptable tails justifies a separately prepared second control/candidate pair
(four jobs total). Do not automatically submit two more after a loss. Existing
H100/PBS access stays unqueried; no authentication, schedules, background Codex,
HPC change, published presentation or submission update occurred.

[Plan and limits](PLAN.md), [CPU validation](validation.json).
