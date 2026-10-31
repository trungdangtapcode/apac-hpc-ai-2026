# Bounded H100-to-H200 verification

On 31 October 2026 the owner reopened AI research specifically to verify
promising H100 ideas on H200 after the panel challenged cross-hardware
comparisons. The prior global research stop is superseded only for this scope.
No H100 authentication or spending, HPC work, schedules or background Codex is
authorised by this change.

H100 is a screening platform for hypotheses, compatibility and tradeoffs. A
higher or lower score on a different GPU does not establish which configuration
wins on H200. The decisive comparison runs both alternatives on H200 under the
same workload, software and resource count. Calibration estimates are forecasts,
not substitutes for these measurements.

## How many jobs are enough?

Start with **two H200 jobs**, a fresh incumbent control and one candidate.
The candidate changes only decode attention from FlashInfer to FA3. H100 showed
a real tradeoff: mean TTFT improved 118.922270 ms, but goodput fell about 0.812%
and request-mean ITL worsened 0.773278 ms. This is not a winning H100 method; it is
a hardware-dependent question that has not been established on the current H200
deployment. CPU-envelope balancing's 0.289035% H100 gain does not justify another
priority trial. A four-job first wave was considered before the evidence audit;
the audit supports two, avoiding weak candidates merely to fill the queue.

If the valid candidate improves goodput by more than 1% with acceptable tails and
unchanged output gates, run a second independent control/candidate pair: **four
jobs total**. Otherwise stop this branch after two and retain the loss. Two runs
per arm are a practical confirmation checkpoint, not statistical proof of a
global optimum. Near-threshold noisy results need qualification, not rounding
into a win.

Each job uses 16 H200, two nodes, at most 17 minutes: maximum 4.533334 GPU-hours.
The initial pair reserves at most 9.066667 GPU-hours and no PBS SU. Four jobs would
take at most 68 allocated minutes if serial, plus queue wait; the initial pair
at most 34. Actual charges and elapsed time come from completed allocations.

The frozen full N64 protocol retains requested 4000/200 tokens, seed 2026,
60/120/30 seconds, joint TTFT <= 3000 ms and request-mean ITL <= 20 ms on at least 90% of
all requests, zero errors/cancellations and inherited output checks. Official
full-set quality remains UNKNOWN. No score improvement is claimed by submission.

[Plan, exact controls, validation and later receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-attention-transfer-20261031/PLAN.md).
The latest actual acceptance state belongs in AI_CURRENT and the study STATUS.
