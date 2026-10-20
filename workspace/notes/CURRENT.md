# Current APAC handoff — 20 October 2026

Updated 2026-10-20T02:28:43.092358+00:00. Presentation evidence freeze: 2026-10-20T02:21:11 UTC. Actual scheduler read at 02:17 UTC: H200 24915 completed, 24926/24927/24928 pending; PBS 222048/222049 completed and 222050 running. The latter PBS outputs/charges are not reviewed in this presentation pass. Earlier scheduler/credit snapshots below retain their dates and are historical.

## Reproduced local findings

**H200 highest individual: 24915 = 3022.035 good output tokens/s at N62**, joint success 98.726%, 1860/1884 qualifying, 24 TTFT breaches, zero ITL breaches/errors. Full local protocol/runtime/output PASS, **+4.537% vs fresh auto N62 24914 = 2890.878**; one treatment observation, not independently repeated. **N60 independently repeats 24738 = 2990.151 and 24913 = 2989.175**, only −0.033%, +5.295% vs fresh auto N60 control 24912. DeepGEMM prefill chunk8192 + HPC-Ops decode. N58 repeats across 24724/24737/24819. The former claim that 24915 had no accepted measurement is historical. [N62 review, tails, diagnostic and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md). No automatic N64.

**H100 highest individual remains 221590 = 2430.891.** Fresh FlashInfer control 222027 = 2420.945; decode FA3 222028 = 2401.284, both full local PASS. FA3 loses 0.812%, despite lower mean TTFT; mean ITL rises 0.773 ms. Keep FlashInfer decode for this H100 N54 setting; this is one matched pair, not a universal FA3 ranking. Prefill still uses FA3. Both have exactly **22 scored TTFT breaches**, zero request-mean ITL breaches/errors/cancellations. TTFT p99 3454.130/3472.798 ms. Separate N48 CPU/GPU traces all rank-checked; recorded-kernel interval coverage about 95–96% does not prove CPU starvation or causal wall fractions.

Keep platforms separate. Official full-set 99%-reference accuracy remains unverified; scheduler exit 0 alone never means accepted evidence.

## Actual submitted work

H200 **24915/24926/24927/24928**: **24915 completed and reviewed; 24926/24927/24928 Resources-pending** at the 02:17 check above. All four were pending at 01:43. 24915 is the preserved HPC-Ops N62 treatment/profile. New N60 group: 24926 observer off/default interval 1; 24927 observer on/interval 1 control; 24928 observer on/decode receive interval 2. Old 24914 completed and was fully reviewed. [Receipts and plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-recv2/RESULTS.md).

PBS **222048 → 222049 → 222050**, **C/C/R at 02:17 UTC**, with outputs and charges not reviewed this pass; the earlier post-submit R/H/H snapshot is historical: same off/on/interval-2 plan at N54, both-phase HPC-Ops/chunk4096. Only one 16-GPU PBS allocation runs at once. No new observer/polling score or confirmed telemetry coverage yet. Compare candidate with equally observed control; report observer overhead separately. Pinned native scheduler/receiver/skipper/env source hashes match both images and local selector tests pass. No token work, numerical or workload shortcut.

## Inspect beyond scores

The prior observability audit found missing uniform GPU/node sampling. **Collector is now implemented and deployed through the six new frozen pilots**, replacing the earlier “not implemented” status. Every five seconds per role: UUID/index, GPU/memory activity, VRAM MiB, W, degrees C, MHz/P-state, node CPU/memory/interface counters and whitelisted worker metrics. It is bounded by parent/job/hard duration; no background Codex. Actual support/coverage, UUID mapping, clock alignment, unsupported fields and off/on overhead remain to be inspected. Node counters must be deduplicated by host. [Collector and local checks](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/resource-telemetry-20261020/README.md).

Common phase markers and exact AIPerf phase manifests distinguish scoring from startup/warmup/checks/diagnostic work. Sparse old logs mix phases; KV token occupancy, allocated/sampled VRAM, GPU activity and summed kernel time differ. Do not infer a bottleneck from an aggregate. [Full new reasoning entry](../reports/research-journey-20261019/journal/entries/20261020-receive-polling.md).

The prepared profiler HTTP parsing fix is now deployed only through these new derived bundles: successful empty/text control responses no longer require JSON, generation JSON and HTTP failures stay strict. Historical 24819 and old PBS controls retain parser/stop errors; sealed traces remain usable with limits. Preserve original evidence. Native MNNVL AUTO+PDL remains; forced one-shot, PDL off, flat phase-specific inference-mode and forced NCCL Simple options stay closed. LL-labelled symbols are not protocol identifiers; sealed TUNING decisions supersede earlier symbol assumptions.

## Budget and execution

Pre-submit published Used **34972.443 SU**, Balance **29027.557 SU**, In Doubt **0**. Four terminal charges reconcile **937.244 SU**; prior reserves released. New maximum outstanding reserve **4608 SU**, internal headroom **11419.557 SU**, unchanged **51000-SU cap / 13000-SU buffer**. The published source/as-of time is in nscc-budget.json. Balance already excludes prepayment when present; do not subtract it twice. Bounds are not expected actual charges.

During active authorised work, review completions and submit the next distinct justified hypothesis when capacity/budget permit. No blind duplicates, unchanged losses, automatic interval/load growth or global stop because a branch loses. At most five active H200, three active PBS and one running PBS allocation. Existing VPN/SSH reused; no restart or authentication. The 24-hour IKE request is not verified exact negotiated expiry; read [VPN duration](../tutorial/19-vpn-session-lifetime.md).

Capture, verify, commit and push small milestones promptly. GitHub contains Git data; external large artifacts still need separate off-host backup. [Retained journey](../reports/research-journey-20261019/journal/README.md) and its dated audit are not a claim to recover every old chat statement. Chat Vietnamese, artifacts English; Qwen only, HPC_Task empty. The current explicit slide request authorises the 20 October presentation update and package reseal; AI job scripts remain unchanged. Autopilot OFF: no background Codex, replacement schedules or automatic chat notifications.


## Presentation update

The requested English 32-slide talk has been published into the local submission package and its ZIP resealed. It includes the reviewed N62 result, repeated N60 gain, separate H100 frontier, FA3 tradeoff and resource-observer experiment design. [Build, frozen inputs and rendering limits](../submission-review/research-update-2026-10-20/README.md); [new reasoning entry](../reports/research-journey-20261019/journal/entries/20261020-n62-presentation.md). No official quality claim or research-script promotion. [Delivery and backup scope](presentation-update-20261020.md).
