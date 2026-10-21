# Reverse startup confirmation misses its predeclared cost gate

**Both 222419 read-first and 222420 off-second pass all local serving, runtime, output and sealed startup checks. The reversed comparison is not accepted:** its **9.836066%** reduction in PBS-reported walltime/SU falls below the prospective minimum **10%**. Do not round it into a pass or change the threshold after seeing the result. Close this unchanged prefetch confirmation branch; no automatic third repeat or default promotion.

| Quantity | Read-first 222419 | Off-second 222420 | Unit |
|---|---:|---:|---|
| Good output throughput |2398.983183 |2406.838816 |good output tokens/s |
| Joint qualifying fraction |98.146923 |98.412698 |percent |
| Mean TTFT |737.915273 |738.672315 |ms |
| Mean request ITL |18.180412 |18.181710 |ms |
| Errors/cancellations |0 |0 |requests |
| Long-context checks |12/12 |12/12 |passed/total |
| Topology-script start to ready |438 |514 |seconds |
| PBS resources_used.walltime |770 |854 |seconds |
| Walltime-derived cost |438.044444 |485.831111 |SU |

Read-first saves **84 reported seconds / 47.786667 estimated SU**, readiness decreases **14.785992%**, and goodput changes **-0.326388%**. These are descriptive measurements, not evidence that every future allocation saves the same amount. The original comparison saved 18.737% reported walltime, whereas this reverse misses the cost acceptance gate. A directional benefit survives, but the predeclared reproducibility requirement does not. Keep the inexpensive shard-read helper and all evidence for later cost analysis; do not buy another unchanged repeat under this branch.

## Control integrity and confounding

222419 uses dgx014/016 and 222420 dgx016/017. Both retain N54, official 4000/200 closed-loop 60/120/30 scoring, seed 2026, gateway, original FP8 target/BF16 KV, two TP4 prefill workers and TP8/EP8 decode, both-phase HPC-Ops/chunk 4096, MNNVL, FlashInfer decode/FA3 prefill, round-robin and receive interval 1. Only the frozen shard-read intervention and experiment provenance differ. Same-source startup hashes and actual native resolved runtimes are checked separately per job. [Structured gates and arithmetic](paired-comparison.json), [candidate](222419_REVIEW.md), [control serving gates](222420.pbs111-gates.json), [control startup receipts](222420.pbs111-startup-review.json).

Initial page-cache residency is unmeasured and no cache flush is attempted. Node 016 appears in both sequential allocations, so the read-first candidate may warm files later used by the off-control; that is a possible explanation, not a measured causal effect. One node also changes. The readiness counter includes this intervention but starts after earlier PBS prologue. PBS-reported resources_used.walltime is labelled explicitly; it is not queue wait, critical-path inference time or the topology readiness counter. No node-conditioned or cold-physical-read guarantee is established.

## Full control inspection beyond the score

222420 has **1488/1512** good requests; 21 TTFT breaches, 3 ITL breaches, 0 errors/cancellations and no overlapping latency breaches. TTFT p99/max are 3450.302340/4566.516391 ms; ITL p99/max 19.167119/20.725532 ms. Effective concurrency p99/max 54. It passes the same short-output nonregression and 12/12 raw long-answer checks. Full local output eligibility is not organiser accuracy verification.

Control diagnostic N48 succeeds **375/375** with sixteen sealed 4/4/8 rank CPU/GPU traces; candidate 357/357. All start_profile HTTP responses are 200; three stop requests return HTTP 500 after bounded traces, as in the earlier run. [Control raw-tail/role/profile inspection](222420.pbs111-inspection.json). A successful job and complete traces do not imply error-free profiling logs.

[Matched resources](222420-resources.json) cover 16 unique GPU UUIDs and 24/24/25 scored samples for decode/prefill0/prefill1. Decode activity averages 100%, VRAM 77968 MiB and power 411.631 W; prefill activity 90.833%/88.36%, VRAM 76715.583/76686.16 MiB, power 651.548/622.538 W. Host CPU busy averages 6.995%/7.246%. [Phase-bounded role gauges](222420.pbs111-server-state.json) retain queue, active-request and KV-token labels. GPU activity is not FLOPS or bandwidth efficiency; sparse host means do not rule out a hot thread or remote placement. Missing inflight, scored per-thread CPU demand and host memory placement remain uncollected. Five-second samples miss short transitions, host clock skew is uncalibrated and IP interface counters do not prove RDMA/NVLink utilisation. Kernel-time sums from the post-score diagnostic are not a score-time critical path.

Only new control 222420 is audited by the derived off-only readers; accepted immutable 222419 outputs are reused with their original seals. Reader scope provenance is retained, without re-running the previous measurement or changing any submitted payload.

## Cost and next decision

Walltime-derived pair cost is **923.875556 SU**. At the 15:30:36 UTC locked reconciliation, published Used 41676.441 / Balance 21299.559 / In Doubt 1024 SU. Candidate 438.044 SU is newly posted and uniquely reconciles; control 485.831111 SU is not yet posted, so its full 1024 maximum remains with running worker-locality 222435's 1024 maximum. Outstanding 2048 SU; internal headroom 7275.559 SU under unchanged 51000 cap/13000 buffer. Do not double-subtract In Doubt. [Raw accounting](accounting-final.txt), [unique cost reconciliation](reconciliation-final.json).

Continue the independent worker-locality and EAGLE3 branches. H100 222435 was running at the 15:30 accounting snapshot; a fresh 17:01 check finds F/exit 0, awaiting its own terminal review; H200 25051 and the four earlier jobs remain queued. Locality observations do not themselves change binding; use actual worker/rank/UUID evidence before an affinity candidate. The public EAGLE3 draft is staged and hash-verified outside Git, but real loading, both-phase state transfer, verification kernels and exact greedy token equality remain outstanding. No new performance peak, global optimality or official full-set accuracy claim. Closing this startup method is not a global research stop.
