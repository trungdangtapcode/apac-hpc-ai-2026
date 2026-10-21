# Current APAC Qwen handoff

Updated 2026-10-21T03:32:47.139280+00:00. Queue observations are dated snapshots; refresh schedulers before acting. Historical snapshots are preserved in [the previous handoff](history/20261020T172926Z-before-compact-CURRENT.md).

## Accepted serving results

| Platform | Highest individual accepted run | Good output tokens/s | Context |
|---|---|---:|---|
| H200 | 24915 | 3022.034919 | N62, 98.726% joint SLA; exact independent repeat 24962 pending |
| H100 | 222048 | 2433.019859 | N54; later observed baseline 222435 gives 2413.341139 |

Keep platform series separate. Repeated H200 N60 is about 2989–2990. See [H200 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md) and [H100 incumbent](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md). These are retained best measurements, not proof of global optimality.

**Official full-set accuracy at 99% of reference remains unverified.** Score is AIPerf goodput in requests/s × 200, with joint TTFT ≤ 3000 ms / request-mean ITL ≤ 20 ms and qualifying fraction ≥ 0.90 including errors. Use fixed 4000/200 tokens, seed 2026, cold prefixes and closed-loop team-selected concurrency. [Official workload and units](official-goodput-clarification-20261020.md).

## Latest queue and completed CPU pair

At the 21 October continuation check, H200 24928/24962/24964/24965/25051 remain Priority-pending. Preserve all five positions; no sixth job. PBS has no active owned jobs. **222551 and 222552 are terminal F / exit 0**, with sealed local protocol/SLA/runtime/output-comparison PASS, 12/12 long checks, 16 diagnostic rank traces each and complete actual 4/4/8 GPU scheduler mappings.

Legacy **2407.544052** versus balanced **2414.502691 good tokens/s** is only **+0.289035%**, below the prospective 1% gate. The actual scheduler CPU masks change as intended: prefill 1 grows from 56–63 to 56–87; decode changes from 56/8 to 32/32 local CPU IDs across its NUMA groups, with the same total CPU/core budgets. **Close this exact policy without an unchanged repeat or default promotion.** Native NUMA locality stays enabled. Mean TTFT improves but ITL and p99 TTFT worsen slightly; scored request errors are zero. The same baseline short mismatch persists, and profile-stop HTTP 500 remains. This does not establish CPU saturation or official model accuracy. [Full review and raw evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-envelope-balance-20261020/PAIR_REVIEW.md).

Next prepared step: **one H100 / four minutes / at most 8.533334 SU** for an EAGLE3 component gate. Test actual native gateway forwarding with clearly synthetic workers, then native draft config/registry resolution and real tensor/token-map integrity. No target weights, draft model construction, PD transfer, inference or ranked score. The pinned public draft is verified in the excluded ASPIRE cache. [Prepared payload and stopping gates](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-component-20261021/PLAN.md). No receipt exists at this preparation checkpoint; require fresh locked checks before qsub.

## Closed startup-cost branch

Original off/read 222407/222408 suggested 18.737% lower allocated walltime. Reverse read/off **222419/222420** both pass local gates, but the saving is **9.836066%** (84 seconds / 47.786667 SU), below the prospective 10% gate. Goodput changes −0.326388%. **Close the unchanged confirmation; no automatic third repeat or default promotion.** Different nodes and unknown cache residency limit causality. All prior terminal charges now reconcile. [Complete pair review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-confirm-20261020/PAIR_REVIEW.md).

## Budget snapshot and commitments

Locked terminal reconciliation at **2026-10-21T03:21:52 UTC**: Used **43571.410 SU**, Balance **20428.590 SU**, In Doubt **0 SU**. Both CPU jobs uniquely reconcile **938.098 SU** posted cost; no outstanding maxima. Internal headroom is **7428.590 SU**, unchanged **51000 SU cap / 13000 SU project buffer**. [Accounting proof](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-envelope-balance-20261020/reconciliation-terminal.json). A later component reservation would reduce this headroom; refresh before submission. Balance already excludes In Doubt, so never subtract it twice.

## EAGLE3: staged and prepared, not measured

[CPU preflight](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/REPORT.md) pins the exact-original-Qwen Nebius draft at ff0f0c09. Fifteen tensor entries match the expected native one-layer BF16 structure; a draft-only architecture metadata adapter is prepared. Limited native pointer-list fixtures preserve 188/188/190 ordered pairs and do not prove byte/page transfers.

[Public draft staging](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/STAGING.md) verifies **1145943008 bytes**, SHA256 **bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86**. Weights are in an excluded public cache; Git holds pinned recovery metadata only. The official FP8 target is untouched.

[New token diagnostic](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/TOKEN_IDS.md) uses actual nonstreaming chat token IDs. Native worker support is inspected, but gateway request-schema forwarding remains unverified. Thirteen adversarial CPU fixtures pass; no live model call, SGLang draft load, speculative GPU job or SU reservation occurred. First establish gateway support and stable target-only repeats, then require exact prompt/output IDs and finish reasons with the draft. Loader coverage, both-phase state/TP4-to-TP8 transport, kernels/graphs, memory and long-context correctness remain runtime gates. Only a useful valid short screen justifies a full matched scoring pair.

## Competition scope clarification — observations from 20 October

[Scoring and registration evidence](contest-scoring-and-tracks-20261020.md): the pinned README requires Basic results for both tasks, with 50 points each; NCI recruitment invites track choice, while the inspected current form has no track selection control. Original registration/acceptance and one-task specialist eligibility remain unverified. Do not infer an exemption or invalid registration from this conflict. Qwen-only work scope and empty HPC_Task are unchanged.

On 21 October the owner authorised committing these previously local notes. The earlier no-commit restriction is historical. This checkpoint preserves the corrections and form observation; it adds no fresh queue/budget observations or organiser confirmation.

## Direction and persistent boundaries

Keep the measured PD stack. [DeepInfer review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepinfer-review-20261020/REPORT.md) does not support migrating this Qwen/Hopper deployment. DeepGEMM and overlap scheduling are already active; historical DP8/DeepEP trials lost to contemporary MNNVL. Keep H100 chunk 4096 and round-robin; unchanged chunk 2048, chunk 8192 and native power-of-two branches lost. H200 micro 25020 found no consistent provider alternative. [Priorities](../reports/research-priorities-20261020/PLAN.md), [full journal](../reports/research-journey-20261019/journal/README.md), [observability limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md).

English artifacts, Vietnamese chat; Qwen only, HPC_Task empty. No package or slide change. **Autopilot OFF**: no background Codex, schedules or automatic chat notifications. Keep working VPN/SSH and exclude credentials/session state. Capture, verify, commit and push each coherent milestone. GitHub contains safe Git files and manifests; sibling large artifact bytes still need a separate off-host copy. Read [POLICY](../research-autopilot/POLICY.md) for execution rules.
