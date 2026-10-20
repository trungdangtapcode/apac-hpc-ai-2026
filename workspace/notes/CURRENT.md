# Current APAC handoff — 20 October 2026

Updated 2026-10-20T01:48:55.712530+00:00. Final scheduler refresh 2026-10-20T01:49:48.588916+00:00: H200 24915 running, 24926/24927/24928 pending; PBS 222048 R and 222049/222050 H. Earlier 01:43 post-submit statements below retain their dates. Credit publication has its own timestamp; refresh live state before a later status claim.

## Reproduced local findings

**H200 highest individual: 24738 = 2990.151 good output tokens/s at N60. Independent repeat 24913 = 2989.175**, only −0.033%, and **+5.295% vs fresh auto N60 control 24912 = 2838.853**. DeepGEMM prefill chunk8192 + HPC-Ops decode. N58 also repeats across 24724/24737/24819 = 2938.628/2935.879/2937.148. Full local protocol/SLA/output/runtime gates pass. Fresh auto N62 24914 passes at **2890.878**, closely repeating 24733; its HPC-Ops treatment 24915 has no accepted measurement yet. No automatic N64. [Reviews and insight](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0132/RESULTS.md).

**H100 highest individual remains 221590 = 2430.891.** Fresh FlashInfer control 222027 = 2420.945; decode FA3 222028 = 2401.284, both full local PASS. FA3 loses 0.812%, despite lower mean TTFT; mean ITL rises 0.773 ms. Keep FlashInfer, close tested FA3 option. Both have exactly **22 scored TTFT breaches**, zero request-mean ITL breaches/errors/cancellations. TTFT p99 3454.130/3472.798 ms. Separate N48 CPU/GPU traces all rank-checked; recorded-kernel interval coverage about 95–96% does not prove CPU starvation or causal wall fractions.

Keep platforms separate. Official full-set 99%-reference accuracy remains unverified; scheduler exit 0 alone never means accepted evidence.

## Actual submitted work

H200 **24915/24926/24927/24928**: **24915 running; 24926/24927/24928 Resources-pending** at the final check above. All four were pending at 01:43. 24915 is the preserved HPC-Ops N62 treatment/profile. New N60 group: 24926 observer off/default interval 1; 24927 observer on/interval 1 control; 24928 observer on/decode receive interval 2. Old 24914 completed and was fully reviewed. [Receipts and plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-recv2/RESULTS.md).

PBS **222048 → 222049 → 222050**, post-submit **R/H/H**: same off/on/interval-2 plan at N54, both-phase HPC-Ops/chunk4096. Only one 16-GPU PBS allocation runs at once. No new observer/polling score or confirmed telemetry coverage yet. Compare candidate with equally observed control; report observer overhead separately. Pinned native scheduler/receiver/skipper/env source hashes match both images and local selector tests pass. No token work, numerical or workload shortcut.

## Inspect beyond scores

The prior observability audit found missing uniform GPU/node sampling. **Collector is now implemented and deployed through the six new frozen pilots**, replacing the earlier “not implemented” status. Every five seconds per role: UUID/index, GPU/memory activity, VRAM MiB, W, degrees C, MHz/P-state, node CPU/memory/interface counters and whitelisted worker metrics. It is bounded by parent/job/hard duration; no background Codex. Actual support/coverage, UUID mapping, clock alignment, unsupported fields and off/on overhead remain to be inspected. Node counters must be deduplicated by host. [Collector and local checks](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/resource-telemetry-20261020/README.md).

Common phase markers and exact AIPerf phase manifests distinguish scoring from startup/warmup/checks/diagnostic work. Sparse old logs mix phases; KV token occupancy, allocated/sampled VRAM, GPU activity and summed kernel time differ. Do not infer a bottleneck from an aggregate. [Full new reasoning entry](../reports/research-journey-20261019/journal/entries/20261020-receive-polling.md).

The prepared profiler HTTP parsing fix is now deployed only through these new derived bundles: successful empty/text control responses no longer require JSON, generation JSON and HTTP failures stay strict. Historical 24819 and old PBS controls retain parser/stop errors; sealed traces remain usable with limits. Preserve original evidence. Native MNNVL AUTO+PDL remains; forced one-shot, PDL off, flat phase-specific inference-mode and forced NCCL Simple options stay closed. LL-labelled symbols are not protocol identifiers; sealed TUNING decisions supersede earlier symbol assumptions.

## Budget and execution

Pre-submit published Used **34972.443 SU**, Balance **29027.557 SU**, In Doubt **0**. Four terminal charges reconcile **937.244 SU**; prior reserves released. New maximum outstanding reserve **4608 SU**, internal headroom **11419.557 SU**, unchanged **51000-SU cap / 13000-SU buffer**. The published source/as-of time is in nscc-budget.json. Balance already excludes prepayment when present; do not subtract it twice. Bounds are not expected actual charges.

During active authorised work, review completions and submit the next distinct justified hypothesis when capacity/budget permit. No blind duplicates, unchanged losses, automatic interval/load growth or global stop because a branch loses. At most five active H200, three active PBS and one running PBS allocation. Existing VPN/SSH reused; no restart or authentication. The 24-hour IKE request is not verified exact negotiated expiry; read [VPN duration](../tutorial/19-vpn-session-lifetime.md).

Capture, verify, commit and push small milestones promptly. GitHub contains Git data; external large artifacts still need separate off-host backup. [Retained journey](../reports/research-journey-20261019/journal/README.md) and its dated audit are not a claim to recover every old chat statement. Chat Vietnamese, artifacts English; Qwen only, HPC_Task empty; no slide/package promotion. Autopilot OFF: no background Codex, replacement schedules or automatic chat notifications.
