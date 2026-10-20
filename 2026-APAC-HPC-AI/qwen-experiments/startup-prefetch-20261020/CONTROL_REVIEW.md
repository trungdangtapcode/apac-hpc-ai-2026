# Completed prefetch-off control: 222407

This is the first terminal control of the matched startup-cost pair. All local serving protocol, SLA/error, runtime/source/sealed payload and short/12-long output checks pass. Native mode-off receipts complete on both allocated nodes, with the expected 24 shards / 236426193880 bytes and matching helper hash. Candidate 222408 was still running at the dated scheduler query; its live mode-read receipts complete in 27.527/27.290 seconds on different nodes. Those live receipts are not terminal accepted evidence and cannot establish cost savings yet.

| Metric | Control 222407 |
|---|---:|
| Good output tokens/s | 2411.827128 |
| Joint good / requests | 1490 /1516 |
| Joint qualifying fraction | 0.982850 |
| Mean TTFT, ms | 720.685 |
| TTFT p99, ms | 3439.061 |
| Mean ITL, ms | 18.199 |
| ITL p99, ms | 19.194 |
| TTFT / ITL breaches, requests | 21 /5 |
| Errors / cancellations | 0 /0 |
| Topology script start to workers-ready, s | 602 |
| Full allocated walltime, s | 934 |
| Estimated charge, SU | 531.342222 |

The 602-second readiness counter begins in topology-job.sh; it excludes earlier PBS prologue. The 934-second allocation includes readiness, scoring, separate diagnostics and cleanup. Keep both quantities distinct, and include future candidate prefetch time rather than subtracting it. Initial page-cache residency and cross-run hardware/cache equality remain unverified; control nodes 14/16 differ from candidate 17/30. Logical read bytes do not prove physical cold storage reads. Model serving peaks remain unchanged.

## Inspection and remaining limits

All scored request tails/errors/concurrency, role batch/queue/KV gauges, runtime/source/transport checks, node CPU/memory/interface and GPU activity/VRAM/power/clocks were reviewed through the retained inspectors. The 16 separate CPU/GPU traces are sealed and rank-mapped; diagnostic requests succeed 356/356. Start-profile returns 200 on all roles, and the three post-score stop calls return 500 after bounded traces as previously recorded. Do not call the logs error-free. Whole-run log distributions mix phases; scored state uses the phase-bounded sampler.

Sixteen disjoint GPU UUIDs and 25 scored samples per role pass. Inflight and per-worker thread CPU/NUMA attribution are not collected by this sampler. Node-wide CPU busy percentage cannot identify a thread bottleneck; GPU activity is not FLOPS or bandwidth efficiency; kernel sums are not scored wall-time shares, node clocks are uncalibrated and IP counters miss kernel-bypass RDMA. [All resource fields](222407-resources.json), [server state](222407.pbs111-server-state.json), [tails/logs/profiles](222407.pbs111-inspection.json), [exact startup gates](222407.pbs111-startup-review.json).

## Cost and next decision

The published ledger still shows Used 40272.495 SU, with this 531.342222 SU estimate unposted, and 1024 SU InDoubt for the running candidate. Preserve both 1024 SU maximum reservations pending reconciliation; do not subtract prepaid credit a second time. The internal conservative headroom remains 8679.505 SU before any new spending, within the 51000 cap/13000 buffer. A scheduler success is not official accuracy verification; the full-set 99%-reference accuracy gate remains unverified.

Keep the current configuration while the candidate completes. A cheap static CPU/GPU topology probe can fill the missing hardware-locality evidence before any affinity experiment; it must not be mistaken for a performance test. Do not repeat failed chunk/provider/routing settings or submit a speculative full-model CPU-binding change without mapping evidence. Preserve the four pending H200 model jobs and leave their queue positions intact.
