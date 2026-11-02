# Final exact packaged-entry acceptance — job 28194

**Terminal correction:** job 28194 FAILED/22:0 before benchmark because router health did not guarantee model registration. [Failure evidence](FAILURE_28194.md). The PENDING snapshot below is historical. [Qualified readiness repair](../final-portable-acceptance-r2-20261102/PLAN.md) is a derived new attempt, not a mutation of this job.

Observed 2026-11-02T07:37:07.867301+07:00, Vietnam time (UTC+7). Slurm definitely accepted **28194**, named TripleU-Qwen-Basic. Current scheduler output:

```text
28194|PENDING|0:00|17:00|2|(Resources)
```

This is SUBMITTED, not a completed or passing measurement. Two nodes/eight H200 each, N64, maximum 17 minutes / 4.533334 GPU-hours, zero PBS SU. The active/pending cap check passed under the shared Slurm lock. Resources pending means both required nodes are busy; it is not evidence of a job failure. Do not cancel/requeue merely for this state.

The source ZIP is a0da31120fa6cb5d1c49bfbb693ca74af20610e5cf368f9c3cc18dd703c3659e. All 26 extracted job-script/tokenizer files match it and the working submission exactly, with original modes. setup.sh --check passed from this delivery copy. [Frozen bytes](FROZEN_PAYLOAD.json), [plan and acceptance](PLAN.md), [definite receipt](admission/submission-receipt.json), [reservation](admission/reservation.json).

Prepared source was captured/pushed in 5b50c397 before admission. The scheduler test-only message used its own provisional test ID, which is not a second actual submitted job. Only 28194 has an actual acceptance receipt. There is no dependency chain, scheduled Codex task or background model worker beyond this normal Slurm job.

Outputs will be written beneath delivery/VNUHCM - TripleU/AI_Task/logs/reruns/28194, with allocation stdout/stderr under logs/slurm. The frozen submission folder and ZIP are not used as writable output directories and remain unchanged. Preserve runtime-home/cache exclusions during later Git capture.

Review terminal top-level state, both semantic routes, exact scored raw/export protocol, summary.json, performance-gate.json, actual worker/backend/KV/patch logs and cleanup. Missing hardware telemetry must be labelled not collected. Do not replace the historical selected mean with an isolated acceptance score or relabel the earlier failed portable jobs.

This run tests complete deployment/performance acceptance after the reader repair. It does not provide the official full-set accuracy score or ≥99%-reference quality ratio. [Quality and submission clarification](../../../workspace/notes/ai-quality-threshold-clarification-20261102.md).
