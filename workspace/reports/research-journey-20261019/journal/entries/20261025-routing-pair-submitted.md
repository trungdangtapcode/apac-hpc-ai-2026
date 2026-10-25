# Matched H200 routing pair submitted

At 06:03:42 UTC on 25 October 2026, submitted fresh target-only round-robin control 26083 (S65), then power-of-two prefill candidate 26085 (S64) with afterany:26083. Admission used a fresh own-queue check under the Slurm admission lock, both SHA256SUMS checks and scheduler test-only checks. Job 26081 was already pending. All three count within cap 5. No uncertainty/retry occurred.

The immediate states are 26081 PENDING (Resources), 26083 PENDING (Resources), 26085 PENDING (Dependency). The dependency is expected and satisfiable: candidate becomes eligible after the control terminates regardless of exit code. It is not DependencyNeverSatisfied. A control failure still blocks interpretation/promotion of the candidate; historical 25947 is not substituted.

Each new routing arm requests 16 H200 GPUs/two nodes/at most 17 minutes and incurs no separate PBS SU. Both stdout/stderr paths and WorkDir were checked under qwen-experiments/runs. Exact commands, definite IDs, test output, dependency and scontrol state are in receipts-routing.json. Fresh status/node inventory is in post-submit-queue.json. No job has an allocation or measured score at this snapshot.

Hypothesis, pinned settings, H100 negative prior, local accuracy limits and beyond-score telemetry plan remain in the preceding matched-plan entry and bundle PLAN.md. Advance only for >=3% good output throughput over the actual fresh control with all runtime, semantic, exact workload, zero-error and joint-SLA gates; otherwise close this exact policy branch. The accepted full-protocol H200 frontier remains 3044.400475 good output tokens/s and official accuracy is still unknown.

Evidence root: qwen-experiments/h200-next-screens-20261025. No submitted parent was edited and no background Codex/schedule was enabled.
