# Local quality measurement: dated monitoring snapshot

Observed UTC: 2026-11-02T19:21:29.911362+00:00. Add seven hours for Vietnam time.

Admitted: **10/16**. Common completed coverage: **3008/12032 questions per role**.

The callback state records its last invocation; it is not a substitute for live scheduler state.

| Role | Shard (zero-based) | Job | Scheduler state | Client responses | Callback |
|---|---:|---:|---|---:|---|
|reference|0|28373|COMPLETED|1504|VALID|
|candidate|0|28375|COMPLETED|1504|VALID|
|reference|1|28382|COMPLETED|1504|VALID|
|candidate|1|28384|COMPLETED|1504|VALID|
|reference|2|28386|COMPLETED|1504|VALID|
|candidate|2|28388|RUNNING|—|—|
|reference|3|28390|PENDING|—|—|
|candidate|3|28392|PENDING|—|—|
|reference|4|28394|PENDING|—|—|
|candidate|4|28396|PENDING|—|—|
|reference|5|—|NOT_SUBMITTED|—|—|
|candidate|5|—|NOT_SUBMITTED|—|—|
|reference|6|—|NOT_SUBMITTED|—|—|
|candidate|6|—|NOT_SUBMITTED|—|—|
|reference|7|—|NOT_SUBMITTED|—|—|
|candidate|7|—|NOT_SUBMITTED|—|—|

Common completed correct counts: {'reference': 2406, 'candidate': 2409}.
Paired point ratio: 1.0012468827930174; scope: Only common completed shards; not a full-set result unless all 12032 questions are covered.

Queue query available: True. Unknown queue state is never reported as empty.
STOP marker present: False. Full aggregate exists: False.

A validated callback does not replace the technical review of logs, diagnostics and limitations. This local benchmark does not certify the organiser's unpublished quality evaluation.
