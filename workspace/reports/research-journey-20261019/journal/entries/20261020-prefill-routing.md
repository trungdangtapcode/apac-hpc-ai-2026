# Native prefill routing pair: submitted

Updated 2026-10-20T10:13:13.049729+00:00. No routing result yet. Both new jobs retain HPC-Ops prefill/decode, chunk 4096 and N54; the main prefill router policy is the only candidate change.

| Job | Current state at query | Main prefill policy | Allocation |
|---|---|---|---|
|222302.pbs111|R|round_robin control|16 H100, <=45 min|
|222303.pbs111|H|power_of_two candidate|Identical|

The second waits on verified **afterany:222302**; no overlapping allocation. [Receipts](pbs-receipts.json), [live PBS](live-pbs.txt), [predeclared hypothesis and acceptance rules](PLAN.md), [frozen payload checks](validation.json).

## Evidence behind the experiment

Accepted observed chunk pair 222281/222282 measures **2401.577649 versus 2382.811874 good output tokens/s**: chunk 8192 is **-0.7814%**, TTFT mean rises 75.665 ms while ITL mean falls 0.230 ms. Both pass full local protocol/runtime/output/SLA and 12 long checks; keep 4096. Native prefill graphs expand automatically with chunk, so the first reviewer rejection was corrected through exact pinned-source derivation and negative mutation checks, not a blanket waiver. [Complete pair review, raw evidence, tails, hardware/server gauges and graph correction](../h100-prefill-hpc-chunk-interaction-20261020/PAIR_REVIEW.md). This is no new serving peak or official model accuracy claim.

The sampled control has some prefill imbalance/queue excursions with near-zero cache hit; these motivate testing load-aware selection without proving a routing bottleneck. The pinned 0.3.2 CPU parser, actual Rust enum and mapping all pass with the image-matched private loader/libc; shortest_queue is rejected. The initial host GLIBC failure is retained as an environment mismatch, not unsupported policy. No CPU check started a router, used GPUs or measured performance. [Native validation](native-validation.json), [probe source](validate-native.py), [failed/corrected attempt record](preflight-history.json).

Both new bundles add the same source/native hash guard and policy mapping check before actual router launch. Workers, scoring/quality checks, topology, transport, uniform sampler and profiles remain byte-identical to accepted 222281. Candidate topology inverse-diffs exactly after reverting power_of_two→round_robin. Decoder policy and single-prefill warmup routers are unchanged.

## What the next review must establish

Collect only terminal full-model evidence. Receipt-driven review-pbs.py verifies frozen hashes/full protocol/SLA/error/short/long gates and exact worker runtime against 222281 with only random-seed differences. It checks the CPU policy preflight and the native **main 8000-port** PD router initialization in task-aux logs, distinguishing it from warmup-router logs and the separate per-model cache-aware registry. Empty router.log is not proof of missing router output under the PBS logging shim. Individual dispatch decision counters are NOT_COLLECTED; do not invent policy execution counts or ignore worker metadata warnings.

Run inspect-pbs.py, inspect-server-state.py and the existing resource inspector with the new IDs/seals. Inspect tails, batch/queue/KV state, 16 disjoint GPU UUIDs, scored sample/phase coverage, all 16 separate post-score CPU/GPU traces, CPU/memory/network evidence and sampler/error statuses. Retain missing inflight, clock skew, shared-node counter and efficiency limits. Existing stop_profile errors occur after scoring and must stay visible. A >=1% paired goodput gain with all local gates requires independent confirmation; no adoption from one run, unchanged loser retry or automatic policy/polling/load expansion. Official full-set >=99%-reference accuracy remains unverified.

## Budget and other queue

Pre-submit ledger queried 2026-10-20T10:10:36.854514+00:00: Used **38396.869 SU**, Balance **25603.131 SU**, In Doubt **0.000 SU**. All previous charges reconcile; reserve only this pair's **3072 SU** maximum. Conservative internal headroom **9531.131 SU** under unchanged 51000 cap/13000 project buffer. [Published query](pbs-pre-submit.txt), [budget reservation workflow](submit-pbs.py). This is a dated pre-submit ledger, not a promise of current remaining spend after job progress. Never deduct prepaid credit twice.

H200 24990/24928/24962/24964/24965 still fill five Priority-pending positions; no cancellation or sixth job. [Fresh Slurm query](live-slurm.txt). H100 highest individual remains 2433.019859, H200 3022.034919 good output tokens/s; platforms and observation settings remain separate. No official package edit, authentication restart, background Codex or schedule. Git captures include safe source/records; external large objects still require separate off-host backup.
