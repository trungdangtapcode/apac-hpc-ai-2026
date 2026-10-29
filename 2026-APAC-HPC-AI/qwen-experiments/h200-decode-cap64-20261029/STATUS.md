# Actual decode cap 64 admission

Observed 2026-10-29T21:33:55.348545+07:00, Vietnam time (UTC+7). Slurm accepted full candidate **27365**, frozen S102 manifest recorded in submission-receipt.json. This is submitted, not a measured improvement. The last queried own queue is below.

Only the decode running-request cap changes from 256 to 64. Transfer/preallocation slots are separate in pinned source. This small metadata/resource trim has low expected upside; the control does not demonstrate a capacity bottleneck. Keep all model weights/precision/topology, graph batches 1..64, full official requested N64 cold 4000/200 seed 2026 workload and all raw/runtime/KV/two-route/output gates. Require the actual final TP0 scheduler cap 64 before scoring. Nine adversarial runtime fixtures pass, not GPU proof. Actual full control 27270 is 3039.053386 good output tokens/s; no 128-cap sweep follows.

Maximum one allocation: 16 H200, two nodes, 17 minutes, 4.533334 GPU-hours and no PBS SU. Admission held the lock, queried the fresh own queue against cap 5, verified the manifest and obtained definite sbatch acceptance. Existing jobs were not cancelled or reprioritized. Passing performance must beat the >1% useful-gain gate and have acceptable tails before independent confirmation; otherwise close unchanged. Official accuracy remains UNKNOWN.

```text
27365|ap42-s102-dcap64|PENDING|0:00|2|(Resources)
```

Source/configuration checkpoint is 71e30c64. Actual receipt and reasoning follow as their own safe checkpoint. Published submission, HPC, authentication and background automation are unchanged. Git pushes preserve manifests, not sibling external object bytes.
