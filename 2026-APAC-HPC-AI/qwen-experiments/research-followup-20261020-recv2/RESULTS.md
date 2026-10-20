# Six receive-poll and observer pilots submitted

Submitted 20 October 2026 at 01:43 UTC. Payloads are frozen and hash checked. No new score, telemetry success or overhead improvement is claimed yet.

| Platform | Job | Trial |
|---|---|---|
| H200 | 24926 | Observer off, default receive interval 1, N60 |
| H200 | 24927 | Observer on, interval 1 control, N60 |
| H200 | 24928 | Observer on, decode interval 2 candidate, N60 |
| H100 | 222048.pbs111 | Observer off, interval 1, N54 |
| H100 | 222049.pbs111 | Observer on, interval 1 control, N54 |
| H100 | 222050.pbs111 | Observer on, decode interval 2 candidate, N54 |

The verified PBS chain is **222048 → 222049 → 222050**, post-submit states **R/H/H**. Only one 16-GPU PBS allocation runs at once. New maximum reserve **4608 SU**; published Used **34972.443 SU**, Balance **29027.557 SU**, In Doubt zero at the pre-submit ledger; internal headroom **11419.557 SU** under unchanged cap/buffer. Reservations are bounds, not actual charges.

At 01:43:56 UTC all three new H200 jobs and existing 24915 were Resources-pending. Existing 24914 completed separately and its offline review follows; it is not a new receive-interval result. Existing positions were preserved, no cancellation/resubmit or active-cap violation.

Observer-on jobs sample every five seconds, bounded by worker-parent/job lifetime and a hard duration. GPU UUID/role/coverage, hardware query support, server counters, scored-phase alignment and monitoring overhead must be inspected. Missing telemetry remains unknown. Heavy diagnostics follow scoring and use the prepared HTTP response fix. Controls/candidate retain the full workload, numerical settings, transport and output gates.

[Plan and rationale](PLAN.md), [local validation](validation.json), [definite PBS receipts](pbs-receipts.json), [PBS dependencies/status](pbs-post-submit.txt), [Slurm receipts](slurm-receipts.json), [Slurm post-submit status](slurm-post-submit.txt), [exact payload hashes](pilots.json). Compare candidate with equally observed control and report off/on overhead separately; repeat a useful gain, close a loss, no automatic interval or load growth. Official accuracy is unverified.
