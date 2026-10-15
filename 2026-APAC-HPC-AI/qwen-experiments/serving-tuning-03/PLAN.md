# Concurrency refinement on the repeated scheduling winner

Wave 2 finished all nine planned full standalone measurements, plus the separate
output diagnostic. Chunk 4096 with dense decode graphs measured 2078.96 and
2079.18 good output tokens/s in two deployments at N52, both with approximately
97.43% SLA and zero benchmark errors/cancellations. The observed range is 0.0104%
of their mean; two repetitions do not establish variation under all cluster conditions.

The chunk-only repeat measured 2032.13 versus 2033.03 initially. FP8 KV measured
1996.26, below its chunk-only BF16 control. DeepEP measured 1957.15, below its
matched DeepGEMM control at 2018.01. These backend pilots are not selected for
promotion or further load search on the current evidence.

The next variable is concurrency on the repeated BF16 scheduling winner:

| Trial | Condition |
|---|---|
| Fresh N52 control | Launch after the previous wave finishes |
| N54 | Launch after the previous wave finishes |
| N56 | N54 has a full passing benchmark and research output eligibility |
| N60 | N56 has a full passing benchmark and research output eligibility |
| One midpoint | Refine the interval below a measured SLA failure, or a goodput decline; do not infer a boundary from deployment/request errors |
| One winner repeat | Highest passing new point exceeds the mean of the two previous N52 deployments by at least 2% |

Each job runs exactly one concurrency, with the same model, sixteen H200,
TP4 prefill → TP8/EP8 decode, chunk 4096, dense decode graphs 1–64, BF16 KV,
NIXL patch and unchanged official 4000/200, 60/120/30 client protocol. Frozen
workers and benchmark scripts are copied without modification. The graph cap
64 covers all coarse candidate loads. No tuning traffic is mixed into a ranked
point. At most four account jobs are pending/running, and at most six full
deployments are selected by this plan, apart from explicitly recorded time-budget retries.

All eight original output cases are retained. Research eligibility requires
8/8 or no newly failed case versus independent baseline 23146. The known
reverse-string failure stays wrong. This is not the organiser's full-set 99%
accuracy gate, and no submission promotion is automatic.

Initial jobs submitted: **23286** fresh N52 control and **23287** N54. Later
loads are submitted by the controller after their prerequisites pass.

## Completed results

| Job | N | Good tokens/s | SLA |
|---|---:|---:|---:|
| 23286 | 52 | 2075.11 | 97.42% |
| 23287 | 54 | 2111.91 | 97.33% |
| 23437 | 56 | 2141.20 | 97.22% |
| 23495 | 60 | 2133.30 | 94.51% |
| 23505 | 58 | 2157.31 | 96.76% |
| 23516 | 58 repeat | 2159.79 | 96.83% |

All six full measurements completed without benchmark errors/cancellations.
The cache-aware load search peaks at N58 among these tested points, with a
2158.55 mean across its two deployments. A higher single measurement was found
by the separate round-robin pilot at N52; see the
[confirmation plan](../serving-tuning-05/PLAN.md).

- [Plan state and job IDs](load-plan.json)
- [Live measurements](../SERVING_TUNING_RESULTS.md)
- [Previous standalone assessment](../serving-tuning-02/STANDALONE_ASSESSMENT.md)

## Article-driven prefill investigation

The [14 October review](../serving-tuning-04/RESEARCH.md) adds a parallel,
bounded two-pilot investigation at N52. Analysis of the retained per-request data
shows that both scheduling-winner deployments have 34 TTFT-only failures and
zero ITL failures; all 34 start within the first 30 ms of the profiling window.
The revised priority is to test prefill routing and admission as well as increasing
decode batching. Round-robin prefill routing and one-request prefill batches are
tested separately, keeping the official workload/window and all failures intact.
They share the four-job account cap with this load search.
