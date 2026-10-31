# Two new distinct H100-derived ports accepted; not four new configurations

Observed 2026-10-31T13:30:58.841019+07:00, Vietnam time (UTC+7). Slurm accepted:

| Job | Current H200 candidate | Resources |
|---|---|---|
| **27804** | Both-phase HPC-Ops, prefill chunk 6144, FlashInfer decode, N64 |16 H200 / two nodes / maximum 17 minutes|
| **27806** | Same recipe, prefill chunk 8192, FlashInfer decode, N64 |16 H200 / two nodes / maximum 17 minutes|

Actual queue snapshot:

```text
27806|ap42-s115-hpc8192|PENDING|0:00|2|(Resources)
27804|ap42-s114-hpc6144|RUNNING|0:21|2|g[1,4]
```

These are definite submissions, not measured results. The two proposed
additional slots in the requested four-distinct-configuration wave remain
unfilled: the retained H100 top rows mostly repeat the same recipe, and weaker
or already-tested alternatives do not justify pretending four new winners exist.
The earlier four-job wave included a H200 control and two loads of one recipe;
that count did not fulfil four distinct H100 ports.

Sixteen synthetic CPU chunk/graph/backend fixtures pass. Source preparation,
manifest hashes and strict native prefill graph guards were captured and pushed
in 94980434 before admission. Under the shared Slurm lock, fresh own cap-five,
site/queue, checksums and sbatch tests passed; accepted IDs, manifests and
maximum reservations are in admission/. No old payload, queue position or job
was changed. New pair maximum 9.066667 GPU-hours; no PBS SU.

This is the changed current-native N64 HPC-Ops chunk interaction, motivated by
observed prefill queues and the coupled runner/chunk comparison. The source H100
6144/8192 cases were valid near-flat/losing measurements, not H100 wins. Larger
chunks may help on H200; no improvement is promised. Compare against prior same-day
27783 for chunk sensitivity and 27806 versus 27777 for a same-chunk runner test.
Old control timing/state and generated seeds limit attribution; a useful gain
requires independent fresh confirmation. All original raw/source/runtime/KV,
both semantic P/D, output/error/full workload gates and telemetry remain.
Official quality UNKNOWN. No H100 authentication/spending, HPC edit, schedules,
background Codex, published PPTX/ZIP change or organiser upload.

[Plan](PLAN.md), [source audit](candidate-audit.json), [CPU validation](validation.json).
