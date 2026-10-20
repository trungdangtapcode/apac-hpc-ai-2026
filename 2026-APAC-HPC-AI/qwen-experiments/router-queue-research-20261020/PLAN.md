# Native prefill load-aware routing versus round-robin

## Question and evidence

The accepted observed H100 pair 222281/222282 finds no useful chunk 8192 gain: 2401.578 versus 2382.812 good tokens/s, -0.7814%, with TTFT mean increasing 75.665 ms. Retain HPC-Ops prefill chunk 4096/N54 and close that tested interaction. All local protocol, output, runtime and source gates pass, including exact native derived-prefill-graph validation. This routing test does not deploy a kernel/SM/graph/precision change.

Scored-phase gauges on the accepted 4096 control show prefill queue maxima 3/17 across 24/25 samples, running-request means 1.208/1.56 and GPU activity 91.42%/85.21%. Cache-hit gauges are near zero. Candidate8192 also has transient queue imbalance, without improving goodput. These coarse observations justify testing native load-aware selection, not claiming routing is a proven bottleneck. Inflight is not in the current sampler whitelist, short excursions can be missed and host clock skew is uncalibrated.

A bounded scan of 135 retained explicit routing configurations in the selected serving/PBS directories finds round_robin only; this is not a claim that every historical file or chat was recovered. The exact deployed sglang_router 0.3.2 Python parser advertises power_of_two and maps it to the actual Rust PolicyType.PowerOfTwo. It rejects shortest_queue, so prune that unsupported suggestion. Pinned source and native-validation.json retain parser/mapping/enum hashes and a real CPU check. The initial host import failed due older host GLIBC, not policy incompatibility; a private image-matched loader/libc resolved it without changing the operating system or allocating GPUs. That check starts no router, loads no model and does not establish routing performance.

Hypothesis: selecting between prefill workers using native load reduces transient imbalance/first-token tails enough to improve jointly qualifying goodput. Counterhypothesis: coarse/stale load, randomness or PD request accounting makes it neutral/worse than fixed alternation. Existing native logs show a 30-second load-monitor interval; leave it unchanged in both jobs. Do not import newer experimental-router semantics or set unverified recent environment options.

## Exact pair

| Pilot | Prefill routing | Worker configuration | Load | Observer |
|---|---|---|---:|---|
|h100-prefill-rr-n54-control-70|round_robin|Both-phase HPC-Ops, chunk 4096|54|On|
|h100-prefill-p2c-n54-candidate-71|power_of_two|Identical|54|On|

Both derive from accepted 222281's frozen chunk 4096 bundle. Workers, NIXL patch, FP8 checkpoint/BF16 KV, TP4/EP1 prefill replicas, TP8/EP8 decode, attention, default dense kernels, graphs, received-batch interval, benchmark client, full 60/120/30 and 4000/200 protocol, output checks, resource sampler and separate post-score profiler remain byte-identical. Both add the same bounded CPU native-policy/source-hash preflight before main-router launch. Inverse-diff candidate topology power_of_two→round_robin and it equals the new control exactly. Only the main prefill policy changes; decode policy and single-worker warmup routers stay unchanged. Frozen metadata/job labels identify the pair.

## Acceptance and detailed inspection

Require sealed terminal payload/full protocol, zero errors/cancellations, >=90% joint TTFT<=3000ms/ITL<=20ms request success, short-output nonregression, all 12 long checks and actual intended role/rank runtime. Compare each job's workers to 222281; only random seeds may differ. The runtime CPU preflight must verify the exact router files/native extension and native policy mapping. Find the main 8000-port router initialization in actual task-aux/PBS spool logs: Some(RoundRobin) versus Some(PowerOfTwo), decode_policy unchanged. Existing per-model cache-aware assignments and worker local load_balance_method warnings must be distinguished from the explicit PD prefill override. Startup configuration and enum proof do not establish every individual dispatch decision; record that telemetry gap rather than invent selection counters.

Inspect all raw request tails and error components, actual scored hardware/server gauges and phase coverage with 16 disjoint GPU UUIDs, node CPU/memory/interfaces, batch/queue/KV logs and all 16 separate diagnostic traces. Do not conflate sampled VRAM, token occupancy, GPU activity and kernel-time sums. Deduplicate node counters, preserve clock/field gaps and the existing post-score stop_profile errors. Heavy profiles stay outside scoring; no blanket quality waiver or profiler traffic in the score.

A >=1% paired goodput improvement with all local gates and useful tails warrants independent controlled confirmation before adoption. Smaller or tail-only differences remain descriptive/inconclusive. A loss or failure closes this exact native default-policy trial without an unchanged retry, automatic load growth or polling/metric-policy expansion. Do not compare candidate to a substituted historical control. Official full-set >=99%-reference accuracy remains unverified.

## Budget and queue

Two serial PBS allocations, each 16 H100/45 minutes/max 1536 SU, total 3072 maximum. Fresh empty own queue and published credit under budget.lock; all preceding charges must be reconciled or spending stops. Keep Used plus reserved maxima below 51000 SU and retain 13000 project buffer. At the current reconciled Used 38396.869, this pair leaves conservative internal headroom 9531.131 SU. Control first, candidate afterany control; verify dependency, max three active PBS and one running allocation. Preserve definite receipts and never retry uncertainty.

H200 24990/24928/24962/24964/24965 already fill cap five and retain positions. No new H200 job, cancellation, official package change, authentication restart or background Codex.

## Primary references and scope

The execution contract is the retained pinned Python files and actual Rust extension hashes, not mutable upstream main. [Official gateway overview](https://github.com/sgl-project/sglang/blob/main/sgl-model-gateway/README.md) provides background on PD routing/load monitoring. [Official current power-of-two implementation](https://github.com/sgl-project/sglang/blob/main/sgl-model-gateway/src/policies/power_of_two.rs) describes comparing two workers and fallback load choices; its newer metric options are not assumed present in the pinned binary. [Current worker-policy registration](https://github.com/sgl-project/sglang/blob/main/sgl-model-gateway/src/core/steps/worker/shared/update_policies.rs) distinguishes worker metadata warnings/per-model assignments from PD phase policies. Those current sources support mechanism context, not exact compiled-version identity or a speed estimate. The separate experimental router found in search is not the deployed package and is excluded.
