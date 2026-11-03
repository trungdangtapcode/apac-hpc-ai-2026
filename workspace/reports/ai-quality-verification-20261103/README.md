# Qwen answer-quality verification

This is the study guide and evidence route for the owner-authorised local quality measurement. Read [METHODOLOGY.md](METHODOLOGY.md) for the complete explanation, including why each step was necessary, what failed, how scoring works and which conclusions remain limited.

**The full paired test is complete: local gate PASS.** On all 12,032 questions per role, stock FP8 scored **9,460 correct (78.623670%)** and the optimised service **9,452 (78.557181%)**, retaining **99.915433%** of the reference accuracy. All sixteen allocations completed with zero service errors. [Read the final result, evidence and interpretation](FULL_RESULTS.md). This is a local regression check, not a BTC certificate. Earlier pilot and partial snapshots remain historical evidence.

| Need | Read |
|---|---|
| Understand and explain the experiment | [Methodology and presenter answer](METHODOLOGY.md) |
| Find every retained material and understand Git versus external bytes | [Materials and recovery](MATERIALS.md) |
| See current dated job progress | [Monitoring snapshots](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/monitoring/snapshots), [AI handoff](../../notes/AI_CURRENT.md) |
| Inspect original pilot failure and paired results | [Pilot review](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/PILOT_RESULTS.md) |
| Inspect the first 1,504-question pair | [Reviewed result](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/FIRST_FULL_PAIR.md) |
| Rebuild prompts or audit scoring | [Study source](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102) |
| Inspect the final full-set result | [Final report](FULL_RESULTS.md) |

All dates in original artifacts remain unchanged. Snapshot timestamps matter; a historical pending state is not live queue information. This report adds no new performance sweep or HPC change.

[Historical partial progress](PROGRESS_20261103.md) covered the first 3,008 questions per role; it is superseded by the complete result.
