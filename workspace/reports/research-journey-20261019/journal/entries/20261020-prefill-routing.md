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

## Completed review — 2026-10-20T12:03:19.523895+00:00

# Native prefill routing: completed comparison

Both 222302 (round-robin control) and 222303 (power-of-two candidate) finish exit 0 and pass the full local protocol, runtime/source/payload, joint latency/error and output gates. This is one equally observed N54 pair on H100, with both-phase HPC-Ops and prefill chunk 4096. Official full-set accuracy is still unverified.

| Metric | 222302 round-robin | 222303 power-of-two |
|---|---:|---:|
| Good output tokens/s | 2396.201520 | 2279.626751 |
| Joint good / requests | 1480 / 1507 | 1410 / 1432 |
| Joint SLA, % | 98.2084 | 98.4637 |
| Mean TTFT, ms | 749.170 | 1065.117 |
| TTFT p99, ms | 3457.303 | 3522.852 |
| Mean ITL, ms | 18.183 | 17.768 |
| ITL p99, ms | 19.201 | 18.760 |
| Raw TTFT / ITL breaches, requests | 21 / 6 | 22 / 0 |
| Errors / cancelled, requests | 0 / 0 | 0 / 0 |
| Long-context output checks | 12 / 12 | 12 / 12 |
| Allocated walltime | 14:44 | 11:56 |
| Estimated charge, SU | 502.897778 | 407.324444 |

Power-of-two loses **4.865% goodput**. Its mean ITL improves 0.415 ms, but mean TTFT rises 315.947 ms; a larger passing-request percentage does not mean more useful requests per second. Retain round-robin, close this exact default policy trial and do not repeat it unchanged. This is not a universal ranking of routing algorithms. H100 peak 2433.019859 and H200 peak 3022.034919 remain separate and unchanged.

## What was inspected

All scored request records, output checks, exact three worker ServerArgs, native main-router startup and common hash/enum preflight were inspected. All sixteen sealed CPU/GPU diagnostic traces per run are present; separate post-score requests succeed 372/372 and 352/352. Start-profile calls return 200, and all three stop-profile calls return 500 after bounded captures in both jobs, matching the previously recorded post-score stop-profile limitation. Do not describe these logs as error-free.

The candidate startup uses `PowerOfTwo { load_check_interval_secs: 5 }`, not a unit-like Debug enum. [Preserved reviewer correction](ROUTER_REVIEW_CORRECTION.md) explains the exact acceptance and corrects the earlier separate 30-second monitoring interpretation. Main port 8000 explicitly configures the phase override; default cache-aware registry labels and worker-local load_balance_method warnings describe other paths. Per-dispatch decision counters were not collected, so configuration proof cannot attribute individual assignments.

Five-second scored hardware/server sampling verifies sixteen disjoint GPU UUIDs and 24–25 samples per role per run. Mean prefill-0/prefill-1/decode GPU activity is 87.94/91.27/96.575% for control and 85.46/89.92/98.425% for candidate. Mean decode running requests decrease 45.88 to 42.16; decode sampled queue stays zero. Mean prefill queues increase from 0.60/0.417 to 2.08/3.125 requests, with observed maxima 8/2 versus 17/9. Mean decode KV token occupancy is 0.2248/0.2264 and is distinct from sampled VRAM (78000/77808 MiB). Near-zero prefix hit remains. These associations support rejecting this policy at this setting; they do not establish a causal bottleneck or dispatch bias.

Resource records also retain role VRAM, memory activity, power, temperature, clocks and deduplicated node CPU/memory/interface counters. Their five-second cadence aliases short events; cross-host clock skew is uncalibrated. Inflight is NOT_COLLECTED, no missing metric means zero, GPU activity is not FLOPS/bandwidth efficiency, and summed post-score kernel time is not scored wall time. Whole-run batch log distributions mix phases; scored state comes from the phase-bounded sampler.

## Decision and next hypothesis

The prior larger-chunk 8192 trial lost 0.7814%; this routing trial loses 4.865%. Keep the accepted 4096/round-robin implementation. A bounded metadata scan found no retained H100 worker with chunk 2048; the old H200 23905 chunk2048 at a different implementation/load/hardware does not settle the both-HPC-Ops H100 interaction. A smaller prefill chunk might reduce individual prefill scheduling intervals and tails, but repeats transformer passes and may lose efficiency. Inspect the exact pinned defaults/derived graph range and prepare a fresh controlled 4096/2048 pair only after explicit validation and budget checks. No model-quality or precision relaxation, no blind load growth.

Both charges sum to 910.222222 SU and reconcile to the published 910.222 SU delta within rounding. Fresh Used 39307.091 SU, Balance 24692.909 SU, In Doubt 0, internal headroom 11692.909 SU under the unchanged 51000 cap/13000 buffer. [Accounting](pair-accounting.json), [published source](pbs-final-credit.txt).

## Reproduction and evidence

Read [PLAN.md](PLAN.md), definite [receipts](pbs-receipts.json), per-job `*-review.json`, `*-inspection.json`, `*-server-state.json`, `*-resources.json`, and collection pointers. The collected terminal snapshots preserve raw exports, frozen submitted payloads, profiles and evidence SHA-256 seals. The original reviewer rejection is retained. Git contains safe manifests and inline evidence; large external objects still need a separate off-host copy.

