# Test 48-rank Scotch at a matched horizon

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does a 48-rank Scotch partition reduce solver time relative to 56 ranks when both use the same fixed 40-step work in one matched allocation?

## Why investigate this?

A short graph-placement arm had been highlighted despite using only 14 steps and losing in its full reversed comparison. This trial asks a distinct rank-density question with four full 40-step arms. The rank count and required partition change together, so a result cannot isolate a specific communication or hardware mechanism.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Prerequisite partition and initialization | No initialized 48-rank Scotch source was ready for native timing. | Job 2294914 validated the native Scotch48 partition; job 2294915 completed the required 48-rank initialization. The sealed initialization retained 896 core-file hashes against the accepted 1,040-input source context. |
| Matched solver comparison | 56-rank Scotch in all arms. | Job 2294916 used A1 56 ranks, B1 48, B2 48, A2 56; each completed 40 steps /39 intervals with fixed native work. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Pooled within-job means | 48-rank candidate 26.703647651 versus 56-rank control 32.322052535 s/step; candidate time −17.382574569%. |
| Adjacent pairs | Both favor 48 ranks: −25.157475% and −9.191942%. |
| Repeat drift | 48-rank repeat drift is +15.1737%; 56-rank control changes −5.0757%. |
| Completed arms | A1 33.163697419, B1 24.820548476, B2 28.586746826, A2 31.480407650 s/step; all are 40 steps /39 measured intervals. |
| Cost and telemetry | 82.397778 allocated CPU-hours, not billed SU. Pressure telemetry was unavailable; the available whole-node samples do not establish a hardware bottleneck. |

## What did we learn?

- This is a promising matched rank-density signal within one Iris allocation; both adjacent contrasts favor 48 ranks.
- The candidate repeat drift and single-allocation design require an independent reversed-order confirmation before calling the advantage stable.
- Rank count and Scotch partition change together; communication, memory, frequency and other bottlenecks remain unproven.

## Decision

Keep the result qualified. A reversed 48→56→56→48 40-step confirmation was accepted as job 2294918; it is pending review and has no result yet. Do not claim a stable win over teammate or organizer/BTC settings.

## Limits and remaining questions

- Only one completed allocation supports this result; 48-rank repeat drift is 15.1737%.
- The partition changes with rank count, so the trial does not isolate rank count from decomposition effects or prove a causal hardware bottleneck.
- Pressure telemetry was unavailable; whole-node frequency and memory sampling are not hardware-cycle or bandwidth profiles.
- This is Basic practice, not an official score or cross-platform comparison.

## Sources

- [Native matched rank-density review](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-20261105/completed-2294916/RESULTS.md)
- [Scotch48 partition gate](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-scotch48-cut-20261105/completed-2294914/RESULTS.md)
- [Native 48-rank initialization](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-scotch48-init-20261105/completed-2294915/RESULTS.md)
- [Accepted reverse confirmation receipt](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-reverse-20261105/submission-receipt.json)
