# Local quality measurement: dated monitoring snapshot

Observed UTC: 2026-11-03T04:22:18.800331+00:00. Add seven hours for Vietnam time.

Admitted: **16/16**. Common completed coverage: **12032/12032 questions per role**.

The callback state records its last invocation; it is not a substitute for live scheduler state.

| Role | Shard (zero-based) | Job | Scheduler state | Client responses | Callback |
|---|---:|---:|---|---:|---|
|reference|0|28373|COMPLETED|1504|VALID|
|candidate|0|28375|COMPLETED|1504|VALID|
|reference|1|28382|COMPLETED|1504|VALID|
|candidate|1|28384|COMPLETED|1504|VALID|
|reference|2|28386|COMPLETED|1504|VALID|
|candidate|2|28388|COMPLETED|1504|VALID|
|reference|3|28390|COMPLETED|1504|VALID|
|candidate|3|28392|COMPLETED|1504|VALID|
|reference|4|28394|COMPLETED|1504|VALID|
|candidate|4|28396|COMPLETED|1504|VALID|
|reference|5|28398|COMPLETED|1504|VALID|
|candidate|5|28400|COMPLETED|1504|VALID|
|reference|6|28402|COMPLETED|1504|VALID|
|candidate|6|28404|COMPLETED|1504|VALID|
|reference|7|28406|COMPLETED|1504|VALID|
|candidate|7|28408|COMPLETED|1504|VALID|

Common completed correct counts: {'reference': 9460, 'candidate': 9452}.
Paired point ratio: 0.999154334038055; scope: Only common completed shards; not a full-set result unless all 12032 questions are covered.

Queue query available: True. Unknown queue state is never reported as empty.
STOP marker present: False. Full aggregate exists: True.

A validated callback does not replace the technical review of logs, diagnostics and limitations. This local benchmark does not certify the organiser's unpublished quality evaluation.
