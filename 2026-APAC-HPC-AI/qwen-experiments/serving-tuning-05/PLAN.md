# Confirm round-robin prefill and find its useful load range

All six wave-3 load measurements and both wave-4 prefill pilots completed.
The old cache-aware configuration peaked at N58, measuring 2157.31 and 2159.79
good tokens/s, approximately 96.8% SLA, without benchmark errors or cancellations.

The round-robin prefill pilot, job 23325, measured **2402.64 good tokens/s at N52,
98.93% SLA**, versus 2075.11 for its fresh cache-aware N52 control. That is a 15.78%
single-run gain; it needs an independent repeat. The actual router log confirms
`prefill_policy: Some(RoundRobin)`, with decode routing retained. Checkpoint,
BF16 KV, TP4→TP8/EP8, sixteen H200, chunk 4096 and dense decode graphs are unchanged.

Round-robin TTFT mean fell from 1437.63 to 333.25 ms and P95 to 636.61 ms. Mean ITL
rose to 19.57 ms, P99 to 19.89 ms and maximum per-request average ITL to 19.90 ms,
which is close to the 20 ms gate. Faster admission can keep the decode batch
fuller; that is a plausible explanation, not yet a measured causal breakdown.

The other prefill pilot, one request per prefill batch, measured 2082.09 at N52.
Its gain over the fresh control is only 0.34%; it is not selected over round-robin.

| Trial | Condition |
|---|---|
| Round-robin N52 repeat | Submit now; required to confirm the pilot |
| Round-robin N50 | Submit now; test decode latency headroom |
| Round-robin N54 | Only after the N52 repeat has a full passing benchmark and research output eligibility |
| Optional midpoint | Refine below a measured SLA failure, or between loads where goodput declines; no boundary inference from deployment/request errors |
| Best new-point repeat | Confirm the highest passing new point, even if the original pilot score does not reproduce |

At most five jobs, apart from recorded time-budget retries; at most four account
jobs queued/running. Each deployment starts directly at its sole concurrency.
The official 60/120/30, 4000/200, seed 2026, 12800-entry, closed-loop/cache-bust protocol
is copied byte-for-byte. Worker, topology, transport and router scripts are copied
from job 23325 unchanged; only concurrency and experiment metadata change.

All eight original output cases and the independent baseline comparison remain.
The reverse-string answer remains wrong; the organiser 99% full-set accuracy gate
is unverified. No submission-package promotion is automatic.

Submitted: **23576** round-robin N52 repeat and **23577** round-robin N50.
Both frozen payloads retain the exact router, worker, benchmark and patch files
from job 23325; [payload validation](payload-validation.json).

- [Plan state and job IDs](load-plan.json)
- [Live results](../SERVING_TUNING_RESULTS.md)
- [Prefill research and hypotheses](../serving-tuning-04/RESEARCH.md)
