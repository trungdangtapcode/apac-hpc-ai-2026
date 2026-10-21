# Current APAC Qwen handoff

Updated 2026-10-20T17:29:26.672121+00:00. Queue observations are dated snapshots; refresh schedulers before acting. Historical snapshots are preserved in [the previous handoff](history/20261020T172926Z-before-compact-CURRENT.md).

## Accepted serving results

| Platform | Highest individual accepted run | Good output tokens/s | Context |
|---|---|---:|---|
| H200 | 24915 | 3022.034919 | N62, 98.726% joint SLA; exact independent repeat 24962 pending |
| H100 | 222048 | 2433.019859 | N54; later observed baseline 222435 gives 2413.341139 |

Keep platform series separate. Repeated H200 N60 is about 2989–2990. See [H200 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md) and [H100 incumbent](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md). These are retained best measurements, not proof of global optimality.

**Official full-set accuracy at 99% of reference remains unverified.** Score is AIPerf goodput in requests/s × 200, with joint TTFT ≤ 3000 ms / request-mean ITL ≤ 20 ms and qualifying fraction ≥ 0.90 including errors. Use fixed 4000/200 tokens, seed 2026, cold prefixes and closed-loop team-selected concurrency. [Official workload and units](official-goodput-clarification-20261020.md).

## Actual queues at 2026-10-20T17:29:26.672121+00:00

- H200 **24928, 24962, 24964, 24965 and 25051** are Priority-pending. Preserve all five positions; no sixth job. They test receive interval 2, exact N62 repeat, the observed prefill backend pair and actual worker locality.
- H100 **222551.pbs111 is running**, reported elapsed eight minutes; **222552.pbs111 is held afterany 222551**. This is the new legacy/balanced CPU-envelope pair, not an EAGLE3 run. Maximum one own running PBS allocation.
- All three live control prelaunch receipts exist and apply legacy CPU budgets of 32, 32 and 64 distinct physical cores, with actual CUDA UUID mapping. This validates the helper's initial runtime interfaces, not scored behavior, full worker masks or candidate success. [Snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-envelope-balance-20261020/live-20261020T172926Z.json).

## Current CPU hypothesis and completed observations

[H100 222435](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/worker-locality-h100-20261020/REVIEW.md) passes full local gates at **2413.341139 good tokens/s**, joint **98.416887%**, zero errors, long checks 12/12 and diagnostic requests 355/355. All 16 actual GPU scheduler processes are already NUMA-local. The outer envelope is asymmetric: NUMA 1 GPU groups share only **8 local CPU IDs**, versus 32 for prefill 0 and 56 for decode NUMA 0. This is not evidence of CPU saturation; scored per-thread demand and memory placement were not collected.

[222551 → 222552](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-envelope-balance-20261020/RESULTS.md) keeps native SGLang locality, model, transport, kernels, N54 and official benchmark unchanged. Both run identical metadata checks; only the same 32/32/64 CPU budget distribution changes. The candidate uses actual GPU UUID/PCI/NUMA identity and verifies the predecessor before loading weights. Require full local gates, complete intended worker mapping, equal core budgets and at least 1% goodput gain for a useful provisional pair. Only a valid useful gain warrants independent confirmation. No new candidate score exists yet.

H200 **25051** gathers the analogous pre-score worker mapping while retaining existing binding. [Receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/worker-locality-baseline-20261020/RESULTS.md). Do not assume H100 mapping or a future gain transfers to H200.

## Closed startup-cost branch

Original off/read 222407/222408 suggested 18.737% lower allocated walltime. Reverse read/off **222419/222420** both pass local gates, but the saving is **9.836066%** (84 seconds / 47.786667 SU), below the prospective 10% gate. Goodput changes −0.326388%. **Close the unchanged confirmation; no automatic third repeat or default promotion.** Different nodes and unknown cache residency limit causality. All prior terminal charges now reconcile. [Complete pair review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-confirm-20261020/PAIR_REVIEW.md).

## Budget snapshot and commitments

Locked pre-submit ledger at approximately **17:20 UTC**: Used **42633.312 SU**, Balance **21366.688 SU**, In Doubt **0 SU**. Published Balance already excludes In Doubt; never subtract it twice. New 222551/222552 maxima total **2048 SU**, leaving conservative internal headroom **6318.688 SU** under the unchanged **51000 SU cap / 13000 SU project buffer**. Each requests 16 H100 for 30 minutes, at most 1024 SU. Refresh and reconcile under the budget lock before another reservation. [Source and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-envelope-balance-20261020/RESULTS.md).

The first adapter attempt rejected signed negative zero before reservation or qsub. The correction retained the failure, verified existing upload hashes and made definite submissions without duplication. [Correction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-envelope-balance-20261020/PRE_SUBMIT_CORRECTION.md).

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
