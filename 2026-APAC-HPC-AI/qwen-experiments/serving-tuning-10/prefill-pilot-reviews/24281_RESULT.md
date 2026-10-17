# Reject the single-request prefill batch limit

Reviewed: 2026-10-17 12:27 UTC. Job24281 completed with exit0, but it did not improve performance.

| Metric | Single-request batches,24281 | Fresh control,24263 |
|---|---:|---:|
| Good output tokens/s |2621.292|2667.465|
| SLA |98.7805%|98.7995%|
| Mean TTFT |936.611ms|856.622ms|
| Mean ITL |16.190ms|16.257ms|
| Request errors/cancellations |0/0|0/0|
| Long retrieval checks |12/12|12/12|

Goodput fell **1.73%**, while TTFT increased about80ms. A small ITL reduction does
not compensate for the loss. Against all three unchanged N56 controls, mean
2669.459, the measured change is **-1.80%**.

The terminal seal, raw full protocol, submitted payload, intended runtime change,
unchanged decode backends, short nonregression and long checks all passed review.
This is a valid negative measurement, not a deployment failure or accuracy proof.

Runtime/log review confirms prefill_max_requests=1 and no steps starting multiple
new sequences in either worker. Whole-log counts mix startup/warmup/measurement/
checks; the control also profiles afterward, so counts do not establish causality.

**Decision:** close this branch without spending another allocation to repeat the
loser. Retain raw data and the predeclared rationale. One run is not a universal
proof that this flag is always harmful; the decision is limited to the current
configuration/load and observed controls.

The distinct TP8-prefill and prefill-only DeepGEMM trials remain queued. Do not
invent another variant solely to fill available queue slots before those results.

[Detailed review](24281.json) · [Batch log observations](batching-observations.json)
