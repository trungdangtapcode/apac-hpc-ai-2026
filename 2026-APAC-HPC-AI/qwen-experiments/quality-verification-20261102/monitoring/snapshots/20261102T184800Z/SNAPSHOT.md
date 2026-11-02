# Local quality measurement: dated monitoring snapshot

Observed UTC: 2026-11-02T18:48:00.701292+00:00. Add seven hours for Vietnam time.

Admitted: **7/16**. Common completed coverage: **1504/12032 questions per role**.

The callback state records its last invocation; it is not a substitute for live scheduler state.

| Role | Shard (zero-based) | Job | Scheduler state | Client responses | Callback |
|---|---:|---:|---|---:|---|
|reference|0|28373|COMPLETED|1504|VALID|
|candidate|0|28375|COMPLETED|1504|VALID|
|reference|1|28382|RUNNING|99|—|
|candidate|1|28384|PENDING|—|—|
|reference|2|28386|PENDING|—|—|
|candidate|2|28388|PENDING|—|—|
|reference|3|28390|PENDING|—|—|
|candidate|3|—|NOT_SUBMITTED|—|—|
|reference|4|—|NOT_SUBMITTED|—|—|
|candidate|4|—|NOT_SUBMITTED|—|—|
|reference|5|—|NOT_SUBMITTED|—|—|
|candidate|5|—|NOT_SUBMITTED|—|—|
|reference|6|—|NOT_SUBMITTED|—|—|
|candidate|6|—|NOT_SUBMITTED|—|—|
|reference|7|—|NOT_SUBMITTED|—|—|
|candidate|7|—|NOT_SUBMITTED|—|—|

Common completed correct counts: {'reference': 1200, 'candidate': 1205}.
Paired point ratio: 1.0041666666666667; scope: Only common completed shards; not a full-set result unless all 12032 questions are covered.

Queue query available: True. Unknown queue state is never reported as empty.
STOP marker present: False. Full aggregate exists: False.

A validated callback does not replace the technical review of logs, diagnostics and limitations. This local benchmark does not certify the organiser's unpublished quality evaluation.
