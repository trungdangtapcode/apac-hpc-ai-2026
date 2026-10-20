# First startup-prefetch pair completed

Both 222407 (off) and 222408 (read) pass all full local protocol/SLA/error, exact frozen/runtime/source/precision/transport, short-output and 12-long-output gates. The extra startup reader accepts two sealed node receipts per job, the common helper/index/24-shard / 236426193880-byte manifest, modes and exact candidate logical read counts. This is a positive startup-cost signal, not an accepted new goodput record or official accuracy verification.

| Metric |222407 off |222408 read |
|---|---:|---:|
| Topology-script start to workers-ready, seconds |602 |436 |
| Full allocated walltime, seconds |934 |759 |
| Estimated allocated cost, SU |531.342222 |431.786667 |
| Good output tokens/s |2411.827128 |2395.929777 |
| Joint good / requests |1490 /1516 |1481 /1509 |
| Joint qualifying fraction |0.982850 |0.981445 |
| Mean TTFT, ms |720.685 |749.707 |
| Mean ITL, ms |18.199 |18.161 |
| TTFT / ITL breach counts |21 /5 |21 /7 |
| Errors / cancellations |0 /0 |0 /0 |
| Long-context checks |12 /12 |12 /12 |

The candidate reaches workers-ready 166 seconds sooner (27.575%) and uses 175 seconds less allocated walltime (18.737%), about 99.556 SU less, including its 27.527/27.290-second node read stages. Goodput changes -0.659% and mean TTFT rises 29.022 ms. Keep scoring, startup readiness and full allocation cost separate. The readiness counter excludes earlier PBS prologue, while allocated cost includes startup, scoring, diagnostic profiles and cleanup. Nothing is subtracted from the candidate to manufacture a saving.

## What was inspected

Both scored raw request/tail/concurrency streams, native role ServerArgs and router configuration, sealed payloads and startup receipts were inspected. Same 16-GPU worker split, graph configuration, HPC-Ops, BF16 KV, attention, native dense provider, transport patch and the full 60/120/30 official workload remain in both. Each has sixteen sealed separate CPU/GPU traces with rank mapping; diagnostic requests succeed 356/356 and 350/350. Start-profile HTTP 200 and post-score stop-profile HTTP 500 on all three roles remain preserved with stop_profile_async stack context, not described as clean logs.

Matched resource readers verify sixteen disjoint GPU UUIDs and 24–25 scored samples per role. Role GPU activity/VRAM/power/clocks, node CPU/memory/interface counters, server running/queue/KV state and tails are retained in per-job resources/server-state/inspection reports. Inflight and per-worker CPU demand/NUMA placement are not collected. Whole-run batch log summaries mix phases, cross-node clocks are uncalibrated, short events alias the five-second cadence, IP counters miss kernel-bypass RDMA and kernel-time sums are not scored wall-time shares. Missing metrics are not zero or healthy.

## Limits and decision

Control nodes are dgx014/016; candidate nodes are dgx017/030. Initial page-cache residency and physical storage bytes are unmeasured, and control-first ordering can warm shared filesystem/cache state. These factors can change startup time independently of the helper. Logical shard reads and Cached/MemAvailable snapshots do not prove all pages were cold or resident. One favourable pair does not establish causality or an across-node saving guarantee.

The signal is large enough to justify **one independent confirmation in reverse order**, keeping exact workers and full scoring, and explicitly retaining node/cache/order limits. The followup must predeclare a material cost target and scoring tolerance, then close or mark inconclusive if the direction fails to reproduce. Do not change the incumbent or claim higher serving performance from this first pair. No unbounded cache sweep, cache flush, engine change or numerical shortcut is authorised by this result.

Both estimates total 963.128889 SU. Keep both 1024 SU maxima until their exact ledger delta is posted and reconciled; the small 6.4 SU static-topology probe is a separate allocation and is not included in these pair costs. The fresh ledger will be checked before any followup reservation. H100/H200 model peaks remain unchanged, official full-set 99%-reference accuracy is still unverified, and H200 model queue positions remain preserved.

Read [original plan](PLAN.md), [startup comparison](startup-comparison.json), exact per-job startup/serving gates, inspections, resource/server-state data and terminal collection pointers. Both frozen payloads and raw exports/profiles are retained. Earlier running-candidate snapshots are historical.
