# Bounded H100 startup-cost experiment

The main serving strategy stays unchanged: the official FP8 model, plain prefill/decode disaggregation, BF16 KV, NIXL, two TP4/EP1 prefill replicas, one TP8/EP8 decode replica, HPC-Ops, chunk 4096 and round-robin. Recent full-model interventions lost: power-of-two routing -4.865%, chunk 8192 -0.7814%, chunk 2048 -26.1328%. H200 synthetic TP8 provider alternatives do not offer a consistent useful gain. Preserve those losses and stop extending those unchanged grids.

## Question and evidence

Can reading the 24 model shards once on each allocated node reduce total startup time and allocated SU, including the read itself? The pinned October ASPIRE notes report a large loading improvement after a host page-cache read. This is a cost hypothesis, not a prediction of higher good output tokens/s. Our existing weight-loader-prefetch-checkpoints flag is a different per-loader operation. The current topology has no explicit once-per-node read stage.

Metadata-only validation over existing SSH finds the model index and 24 safe single-component safetensors names totalling 236426193880 bytes. No model data was read on the login node. Actual bulk reads run only inside the allocated two-node job. The same model stays in place; no weights are copied or modified.

## Exact intervention

Both fresh derived jobs add the same common bounded helper and two-node startup stage before any model worker. The control uses mode off, reading only index/size metadata; the candidate uses mode read, consuming each shard once. Both wait for the per-node stage before launching their identical workers. Each stage uses no GPU, eight CPU I/O threads, at most 16 MiB per thread, an internal 120-second read budget and an outer 150-second timeout with a ten-second termination allowance. Paths, manifest range (200–300 GiB total), shard count and read-byte counts are checked. JSON receipts preserve index/helper hashes, logical bytes read, elapsed monotonic time, node name and node cache/memory snapshots.

Worker, model, precision, topology placement, native graph/routing guards, N54 scoring and short/long output checks are byte-identical to accepted 222382. The benchmark remains full 60-second warmup, 120-second measured window and 30-second grace at fixed 4000/200, seed 2026 and cache-busted prefixes. Hardware/server sampling and separate post-score CPU/GPU diagnostics remain matched. Both jobs use the same reduced 30-minute allocation bound; recent accepted jobs finished in roughly 12–15 minutes. No frozen prior payload, image or source guard is edited.

## What counts as a useful result

Review full local gates and all usual tails/errors, runtime/transport logs, scored queues/batches/KV, hardware/node samples and separate traces. Also require two completed node-prefetch receipts with correct modes and matching index/total sizes. Parse actual scheduler-declared stdout and worker logs for per-stage and worker readiness timing. Include all prefetch time in job-to-ready, allocated walltime and SU; do not subtract it to manufacture an improvement. Distinguish startup cost from the unchanged scored goodput interval.

One pair is descriptive. The filesystem and host page caches are not flushed, initial residency is unmeasured, allocation nodes may differ and control-first order can warm later runs. Logical bytes read do not prove cold physical storage reads; MemAvailable and Cached do not certify all shard pages are resident. A useful repeatable reduction needs a balanced independent comparison with reported node/cache state; do not automatically repeat or claim causality from one favourable pair. Keep prefetch only if the full end-to-end cost is lower without a material scored-quality/latency regression. Otherwise close this exact approach. Official full-set model accuracy remains unverified.

## Budget and queue

Two serial PBS jobs, each 16 H100 GPUs and at most 30 minutes, maximum 1024 SU each / 2048 SU total. Published Used 40272.495 SU and Balance 23727.505 SU, In Doubt zero, with the previous chunk pair charges reconciled. This leaves conservative internal headroom 8679.505 SU under the unchanged 51000 SU cap and 13000 SU project buffer. Refresh the own queue and credit under the existing budget lock before reserving and qsub; require an empty own queue for this pair, then chain candidate afterany control. Maximum three active PBS jobs and one running allocation; never retry uncertain qsub. Preserve four pending H200 model positions; no H200 speculative duplicate is added to fill the fifth slot.

## Reproduction and provenance

Read pilots.json, validation.json, prefetch-validation.json, launch-fixtures.json and frozen SHA256SUMS. The bounded CPU fixtures exercise real read bytes and reject oversized models, escaping paths and excess threads; the actual PBS shim dry run checks both zero-GPU launch mappings. These fixtures do not establish GPU performance. Collect terminal jobs with nscc-pbs/collect-run.py, then review-pbs.py and the retained inspectors. The exact upstream source is pinned in upstream-review-20261020, especially the ASPIRE notes at 3d050964d1008b97fb6d0d7ec5160087cd6883d9. Keep native Enroot/image migration a separate future reproducibility experiment; it is not combined with this test.

## Timing reader distinction

The future review-startup.py requires full serving gates and two sealed matching-mode node receipts before accepting a cost observation. It reads the actual scheduler-declared stdout. Its ALL_WORKERS_READY counter is elapsed topology-script time, not the entire allocation-to-ready interval: earlier PBS prologue is excluded. Report that counter accurately alongside complete allocated walltime/SU, rather than inventing uncollected prologue timing. Initial cache residency remains unmeasured.

## First terminal checkpoint — 2026-10-20T13:51:04.547728+00:00

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
