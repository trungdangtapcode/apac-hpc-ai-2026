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
