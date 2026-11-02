# Qwen answer-quality verification

This is the study guide and evidence route for the owner-authorised local quality measurement. Read [METHODOLOGY.md](METHODOLOGY.md) for the complete explanation, including why each step was necessary, what failed, how scoring works and which conclusions remain limited.

The reviewed first two matched shards cover **3,008 questions per role**: our service answered **2,409** correctly and the stock FP8 reference **2,406**, giving **100.124688%** retention. The earlier small pilot was below 99% and is retained. A third reference shard is complete but has no matched candidate yet. This remains partial evidence, not the complete 12,032-question result or an organiser certificate. [The latest verified material backup](MATERIALS.md) includes all five completed full-study runs and has been downloaded/restored successfully.

| Need | Read |
|---|---|
| Understand and explain the experiment | [Methodology and presenter answer](METHODOLOGY.md) |
| Find every retained material and understand Git versus external bytes | [Materials and recovery](MATERIALS.md) |
| See current dated job progress | [Monitoring snapshots](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/monitoring/snapshots), [AI handoff](../../notes/AI_CURRENT.md) |
| Inspect original pilot failure and paired results | [Pilot review](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/PILOT_RESULTS.md) |
| Inspect the first 1,504-question pair | [Reviewed result](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/FIRST_FULL_PAIR.md) |
| Rebuild prompts or audit scoring | [Study source](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102) |
| Find the eventual complete comparison | `quality-verification-20261102/workflow/FULL_COMPARISON.json` — only exists after all 16 valid events |

All dates in original artifacts remain unchanged. Snapshot timestamps matter; a historical pending state is not live queue information. This report adds no new performance sweep or HPC change.

[Later dated progress: both first two matched shards](PROGRESS_20261103.md) covers 3008 questions per role; the fixed first-shard example above remains unchanged.
