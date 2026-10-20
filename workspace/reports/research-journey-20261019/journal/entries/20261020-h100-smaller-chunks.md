# H100: smaller HPC-Ops prefill chunks

## Question and prior evidence

Both-HPC-Ops chunk 8192 lost 0.7814% against 4096; native power-of-two routing lost 4.865% against round-robin. Keep the incumbent 4096/round-robin. Scored control 222302 still records prefill queues (means 0.60/0.417 requests, maxima 8/2), TTFT p99 3457.303 ms and 21 TTFT breaches, while the sampled decode queue is zero. These are associations, not proof of a causal bottleneck. See the [complete preceding pair review](../router-queue-research-20261020/PAIR_REVIEW.md).

A bounded retained H100 worker scan finds no explicit chunk 2048 bundle. Old H200 job 23905 at a different load/implementation/hardware cannot settle this H100 both-HPC-Ops interaction. The question is whether smaller native chunks reduce the scheduling interval enough to offset repeated transformer passes and smaller matrix efficiency. A loss is plausible; do not predict a gain or extrapolate from GPU activity.

## Controlled change

Fresh serial control 72 uses 4096, candidate 73 uses 2048. Both use two TP4/EP1 prefill replicas and one TP8/EP8 decode replica, 16 H100 total, N54, HPC-Ops both MoE phases, FA3 prefill/FlashInfer decode, native dense auto, MNNVL, official FP8 model, BF16 KV, NIXL and identical patched transport. Main prefill router remains round-robin. Both derive from accepted 222302; control worker is byte-identical, and inverse-diff candidate 2048 to 4096 restores the exact control bytes.

All other execution files, benchmark 60 s warmup/120 s measure/30 s grace and 4000/200 workload, short/12-long output checks, matched resource samples and separate post-score CPU/GPU profiles remain identical. Existing profiler stop HTTP 500 limitation is preserved and reported; profiles do not affect ranked scoring. No background service or package edit.

## Native derived graph effect

Pinned ServerArgs defaults prefill graph max_bs to the chunk size and generates capture buckets accordingly (runtime-source/server-args, lines 4725 onward and 4990 onward). Thus 2048 also reduces prefill graph range/buckets. The exact AST-derived fixture validates this expected effect and rejects unrelated backend/compiler/range changes. Complete decode graphs must remain byte-for-byte equal. This tests the deployed chunk-setting effect including native prefill graph consequences, not batching at fixed graph geometry. Actual runtime must independently match before any performance result is accepted.

## Gates and inspection

Require terminal exit 0, all sealed hashes, unchanged runtime beyond random seed and exact prefill chunk/derived graphs, full protocol/errors/joint SLA of at least 90%, retained short-output baseline and 12/12 long checks. Review raw TTFT/ITL/request tails and concurrency, batch/queue/KV state by role, transport/runtime warnings, all 16 native profiles, bounded scored GPU/CPU/node samples and charge. Inflight remains not collected in the frozen sampler; no dispatch counter was added. Five-second aliasing, uncalibrated node clocks and kernel-time-versus-wall-time limits remain explicit. Official full-set accuracy of at least 99% of the reference accuracy is still unverified.

Only a gain of at least 1% in fresh paired goodput with useful tails merits independent matched confirmation. A useful TTFT-only observation without goodput gain is descriptive, not a new contest winner. Close an unchanged loss; do not automatically grow load, change precision or schedule a sweep.

## Budget and submission

Two serial PBS allocations, 16 H100 each, 45 minutes maximum, 1536 SU per job/3072 total. Published preceding Used 39307.091 SU, Balance 24692.909 SU, In Doubt 0; all routing charges reconcile. This pair leaves conservative internal headroom 8620.909 SU under unchanged 51000 cap/13000 buffer. Refresh own queue and credit under the budget lock, reserve before qsub, control then candidate afterany, verify dependency. At most 3 active PBS jobs and 1 running allocation; uncertain receipts are never retried. H200 four full-model positions and repaired micro 25020 are untouched.

## Reproduction

Read pilots.json, validation.json, prior-scan.json and declared graph fixtures; SHA256SUMS freezes each payload. submit-pbs.py refuses existing receipts and checks fresh ledger/queue. After terminal state collect each run with nscc-pbs/collect-run.py; review-pbs.py checks both runtime and native routing, inspect-pbs.py and inspect-server-state.py separate whole-run logs from scored gauges, and resource-telemetry-20261020/inspect-resources.py checks sealed matched hardware samples. Preserve failures and collection pointers before further decisions.

## Submission evidence — 2026-10-20T12:06:14.504964+00:00

## Smaller H100 prefill chunks submitted — 2026-10-20T12:06:14.504964+00:00

**H100 222382 R → 222383 H**, verified afterany pair: fresh chunk 4096 control versus chunk 2048 at fixed both-phase HPC-Ops, round-robin routing and N54. All other execution/observation/output/transport paths match accepted 222302. Exact pinned graph generator and negative fixtures validate the expected smaller prefill graph range; actual runtime and performance remain unmeasured. [Plan, receipts, gates and next review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-hpc-smallchunk-20261020/PLAN.md).

Prior routing pair full local PASS but power-of-two loses 4.865% (2396.201520 → 2279.626751 good output tokens/s); retain round-robin. Both charges reconcile. Pre-submit Used 39307.091 SU, Balance 24692.909, In Doubt zero; reserve 3072 SU maximum, internal headroom 8620.909 under unchanged 51000 cap/13000 buffer. H200 four model jobs plus repaired micro 25020 are pending, total five; no model position cancelled. Peaks unchanged, official accuracy unverified. No package, auth or background AI change. Earlier scheduler and credit snapshots below are historical.

The exact terminal job reviews and GPU diagnostic observations will be added after completion; none are invented from the CPU fixture.

## Terminal review — 2026-10-20T13:22:09.369531+00:00

# H100 smaller-chunk pair: retain 4096

Both terminal jobs pass all local protocol, sealed payload, runtime, source/precision/transport, output and joint-SLA checks. This is one equally observed N54 comparison of the deployed chunk setting, including its exact native derived prefill graph range. The complete decode graph configuration is unchanged. Official full-set accuracy remains unverified.

| Metric | 222382: chunk 4096 | 222383: chunk 2048 |
|---|---:|---:|
| Good output tokens/s | 2396.779396 | 1770.433299 |
| Joint good / requests | 1481 / 1509 | 1111 / 1215 |
| Joint qualifying fraction | 0.981445 | 0.914403 |
| Mean TTFT, ms | 746.849 | 2039.078 |
| TTFT p99, ms | 3465.948 | 4306.295 |
| Mean ITL, ms | 18.162 | 17.122 |
| ITL p99, ms | 19.064 | 17.447 |
| TTFT / ITL breaches, requests | 22 / 6 | 104 / 0 |
| Errors / cancellations | 0 / 0 | 0 / 0 |
| Long output checks | 12 / 12 | 12 / 12 |
| Allocated walltime | 13:53 | 14:24 |
| Estimated charge, SU | 473.884444 | 491.520000 |

Chunk 2048 loses **26.1328%** goodput. Its lower ITL accompanies fewer active decode requests (47.292 to 33.600 mean sampled requests) and much worse TTFT. Prefill sampled queue means rise from 0.84/0.76 to 5.24/9.04 requests; decode sampled queues stay zero. The intervention shows this smaller deployed chunk is harmful at this setting; it does not identify a unique kernel-level cause or prove global optimality. Keep 4096, and close unchanged 2048/8192 trials instead of expanding a blind chunk grid.

## Inspection beyond score

All raw scored client records and tails/concurrency were inspected. The twelve long output checks and retained short-output baseline pass. Exact worker ServerArgs and graph-generator checks accept only chunk2048 and its native prefill graph consequences; main router remains round-robin and the official model/FP8 weights/BF16 KV/NIXL path are unchanged.

Each job has sixteen sealed post-score CPU/GPU native traces with verified rank mapping. Separate diagnostic requests succeed 376/376 and 328/328. Start-profile control returns 200; all three stop calls return 500 after bounded capture, with ASGI stacks in stop_profile_async after scoring. The existing stop-profile limitation is reported, not hidden or called error-free. Whole-log NIXL error/OOM pattern scans and complete raw logs are retained; their absence is not proof of universal health.

Matched five-second scored hardware sampling verifies sixteen unique GPU UUIDs and 24–25 samples per role. Mean prefill0/prefill1/decode GPU activity is 88.97/88.03/99.99% for control and 90.30/92.25/100.00% for candidate. Prefill VRAM means decrease from 76700/76681 MiB to 76060/76060 MiB while queueing worsens. Mean decode KV token occupancy is 0.23625/0.232 and differs from VRAM. Node CPU/memory and interface evidence is retained in the resource review. Inflight is not collected; node clocks are not calibrated; five-second samples alias short events. GPU activity does not measure FLOPS or bandwidth efficiency; IP interface bytes miss kernel-bypass RDMA; summed post-score kernels are not scored wall-time shares. Whole-run batch log distributions mix phases; use phase-scoped server gauges for scored state.

## Cost and decision

The pair costs 965.404444 SU estimated from 16 allocated GPUs at 128 SU/GPU-hour and reconciles to the published965.404 SU delta within rounding. Used 40272.495 SU, Balance 23727.505 SU, In Doubt 0; internal campaign headroom 10727.505 SU under unchanged 51000 cap and 13000 reserve. No new measurement peak. Close the exact losing setting; the next distinct question is startup cost and reproducibility while the H200 confirmation queue retains its positions.

Read PLAN.md, receipts, per-job gates/reviews/inspection/server-state/resources/runtime scans, pair-accounting.json and collect pointers for sealed raw exports, submitted payloads and profiles. Frozen payloads are unchanged. Scheduler success and local checks are separate from organiser accuracy.
