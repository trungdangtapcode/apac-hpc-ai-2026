# Matched H100 results — 19 October 2026

All three allocations have now been collected, sealed and reviewed. They pass terminal accounting, planned payload hashes, full 60/120/30 protocol and 4000/200 workload, request/error/SLA gates, the intended TP/EP/MoE/decode runtime, short nonregression and all 12 long-output checks. Local synthetic checks do not establish official full-set accuracy at 99% reference.

| Job | N54 configuration | Good output tokens/s | vs fresh control | Joint success (%) | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|---:|
| 221827 | Fresh N54 control | 2413.802 | +0.0000% | 98.6120 | 717.698 | 18.255 |
| 221828 | HPC-Ops prefill chunk 6144 | 2411.995 | -0.0749% | 98.5459 | 748.500 | 18.115 |
| 221829 | Function-scoped Simple setting | 2414.548 | +0.0309% | 98.6139 | 723.351 | 18.223 |

Neither candidate establishes a useful throughput gain. The chunk-6144 point is slightly below the fresh control; its single small difference does not prove a statistically significant regression. Do not spend another unchanged run on this result while more informative hypotheses are available. The best historical individual H100 observation remains 2430.891 good tokens/s, not a new record in this batch. H200 remains a separate platform with five queued jobs and no new observation at the 14:18 UTC check.

## Chunk review correction

The initial strict reviewer held 221828 because changing the chunk also changed automatically derived prefill graph maximum and bucket shapes. [The retained correction](REVIEW_CORRECTION.md) verifies those exact fields against the hashed runtime's own pure generator, while rejecting changed backend/compiler or other graph fields. Initial and corrected reviews are both preserved. This is a review-tool correction, not a failed GPU run and not a change to the frozen benchmark. The chunk effect includes its derived graph-shape effect; it is not an ablation holding graph shapes fixed.

## Simple is not yet an established treatment

The scoped setting was printed in both prefill logs and SGLang reported NCCL 2.28.9. Nevertheless, the separate N48 diagnostic contains 16 sealed nonempty rank traces and 373/373 successful requests, with Ring LL all-reduce kernels and no named Simple all-reduce kernel on the prefill ranks. Environment intent alone therefore does not establish actual Simple activation. This profile is not ranked N54 traffic and does not prove the protocol used by every ranked call. The +0.0309% observation cannot be attributed to a demonstrated protocol switch.

[The next matched diagnostic](../research-followup-20261019-protocol-check/PLAN.md) tests a global prefill protocol selector with identical instrumentation in candidate and control. It changes the scope of the attempted setting rather than retrying the unchanged scoped candidate. It must establish the actual communicator/kernel path before any performance promotion.

## Evidence and costs

Full collection receipts, per-job gates, point reviews and protocol profile are retained under research-followup-20261019-1200/. Each receipt identifies an immutable nscc-pbs/collected snapshot containing raw exports, records, logs, payloads and hashes. All three terminal walltimes sum to 39:11 and approximately 1337.458 SU, matching the published Used delta; reconciliation.json preserves the arithmetic. No observations were discarded to choose a better result.

The budget and new attention submission are recorded independently in [SUBMISSION.md](SUBMISSION.md). Raw large evidence is captured in the sibling artifact store, while Git contains manifests, hashes and recovery metadata; a Git push does not upload those external bytes. Research continues with distinct hypotheses within the existing budget and queue caps.
