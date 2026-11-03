# H200 Slurm run inventory

## Source and scope

This inventory is based on the fresh raw output in `sacct-20260901-now.raw.txt`, queried as `apacsc42` with `sacct -X` for 1 September 2026 through the current query time on 3 November 2026. The query returned 295 retained rows, with the earliest returned submission on 29 September 2026. The scheduler therefore does not establish coverage for 1–28 September; the counts below describe returned records, not proof that no earlier jobs existed. The raw response is preserved unchanged.

The results cover the AI/Qwen Slurm account. Every started row with a `gres/gpu` allocation is counted once, including short failed probes and full-node reservations that produced no benchmark score. There are 284 started GPU allocations: 219 `COMPLETED`, 64 `FAILED`, and 1 `TIMEOUT`. Eleven additional accepted Slurm rows have no start and no GPU allocation; all are cancelled before running. Job 20201 (`learn-gpu`) is present and counted as one completed 8-GPU allocation; it is a GPU learning/HelloGPU job, not a Qwen score. No CPU-only jobs are counted as GPU allocations because their TRES rows have no `gres/gpu` field.

H100-named N54/N64 configuration comparisons in this Slurm inventory ran on the H200 platform. Actual H100 jobs used the separate PBS scheduler and are not included in this H200 inventory. This report does not merge their counts or results.

## Quality run contents

The quality stage contains 3 pilot jobs and all 16 full-set shard jobs. The original reference pilot 28367 failed before inference; corrected reference 28371 and candidate 28368 scored 104/128 and 102/128 respectively, a 98.076923% retention pilot result below the local 99% gate. All 16 full-set shard allocations completed. Across 12,032 questions per role, stock FP8 reference scored 9,460 and candidate 9,452, retaining 99.915433% of the reference score and passing the predeclared local threshold. This is a local MMLU-Pro comparison, not organiser certification. Per-job shard scores and the caveats are in the linked [full result](../../ai-quality-verification-20261103/FULL_RESULTS.md) and cited directly from each quality record in `inventory.json`.

## Lineage

`parent_job_ids` is populated only where an explicit dependency was retained in `RUNS.md`; blank arrays mean no explicit parent was established for this inventory, not that jobs were experimentally unrelated. The inventory records scheduler acceptance/run state as separate fields (`status`, `started`) and does not treat cancellation, failure, or a completed scheduler state alone as a valid benchmark result.
