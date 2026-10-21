# Cancelled before allocation: unsupported 22-minute request

Job 25338 received a definite ID at 2026-10-21T19:38:00.195147+00:00, but was PENDING/PartitionTimeLimit with runtime 00:00:00. The current hpcai partition caps allocations at 17 minutes, so the proposed 22-minute full N62/N64 pair could not start. This is a submission-planning error, not a failed GPU measurement or a serving result.

The pending-only cancellation confirms no GPU allocation. All four older positions 24964/24965/25051/25283 remain unchanged. Preserve the original plan, frozen payload, receipt, scheduler rejection and cancellation. Do not rewrite that payload or treat the submitted ID as usable scheduled work. [Actual limit](partition-limit.txt), [rejected job](invalid-walltime-job.txt), [cancellation](invalid-pending-cancellation.json).

Correction: derive a fresh 17-minute same-deployment N62/N64 short screen, 20-second warmup/40-second measurement/30-second grace on both. Explicitly label it unranked and require a useful gain before full confirmation. Share startup, retain exact workload/observation/error/SLA/quality controls and add an actual partition-limit check before sbatch. No GPU time, PBS SU, automatic retry or other queue cancellation in this repair.
