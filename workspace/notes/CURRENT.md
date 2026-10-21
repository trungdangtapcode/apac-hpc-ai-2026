# Current APAC Qwen handoff

Updated 2026-10-21T05:03:27.169907+00:00. Queue observations are from **2026-10-21T04:58:33.945996+00:00**, not a future live guarantee. [Earlier component handoff](history/20261021-before-real-token-control.md) is historical.

## Retained serving results

| Platform | Highest individual accepted job | Good output tokens/s | Status |
|---|---|---:|---|
| H200 | 24915 | 3022.034919 | N62, 98.726% joint SLA; exact independent repeat 24962 pending |
| H100 | 222048 | 2433.019859 | N54, unobserved incumbent; no new throughput result this turn |

Repeated H200 N60 is about 2989–2990. Keep platforms separate. These are local results, not global optimality or organiser accuracy. [H200 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md), [H100 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md).

**Official accuracy ≥99% of reference remains unverified.** Rank by exported AIPerf goodput ×200, fixed 4000/200, seed 2026, cold prefixes. Joint TTFT ≤3000 ms and request-mean ITL ≤20 ms; good fraction ≥0.90 including errors. [Workload and units](official-goodput-clarification-20261020.md).

## Actual submitted work

- H200 **24928 / 24962 / 24964 / 24965 / 25051** are PD / Priority. Preserve all five; no sixth. They cover recv2, the N62 repeat, observed prefill backend pair and H200 worker locality.
- H100 **222752.pbs111 is now F / exit 0 but the reference FAILED**: BatchEncoding input IDs cannot serialize and no result artifact exists. Actual 662 seconds / estimated 376.604444 SU. The preceding dated receipt requested **16 H100 / at most 20 minutes / maximum 682.666667 SU**. It runs the real target-only PD token reference, not EAGLE3 inference or ranked AIPerf. [Receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-integration-20261021/RESULTS.md), [raw queue snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-integration-20261021/live-receipt.json).
- All five smaller EAGLE3 component/load jobs are terminal and reviewed below. No completed full-model speculative job exists.

## EAGLE3 progress and exact remaining gates

| Job | Actual observation | Assessment |
|---|---|---|
| 222721 | F / exit 1, 105 s: actual chat gateway filters token-ID extensions | Close that diagnostic route; later stages not reached |
| 222722 | F / exit 1, 89 s: synthetic /generate IDs preserved, imports fail on read-only HOME | Route capability only; repair private cache |
| 222729 | F / exit 1, 64 s: imports now pass, direct UUID/name assertion fails without raw values | Preserve failure; cannot infer its cause from that log alone |
| 222749 | F / exit 0, 78 s: complete UUID identity, real registry, finite tensors and mapping pass | Raw values prove GPU- representation difference; no class constructed |
| 222750 | F / exit 0, 99 s: actual native class constructs and loads all 13 float tensors | All 10 non-shared parameters and hot-token map match exactly; no forward |

[222729 failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-component-homefix-20261021/REVIEW.md), [222749 complete component review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-component-uuid-20261021/REVIEW.md), [222750 native loading and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-loader-20261021/REVIEW.md). Raw submitted payloads and evidence seals are preserved. The only missing draft parameter is the actual target-shared embedding; no substitute embedding or inference used. Single-rank loading is not TP4/TP8 runtime compatibility. Peak diagnostic allocations are not serving overhead/utilization.

Public draft nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507, revision ff0f0c0999f6c86b21dfd2f5803eebc4ac712224, remains outside Git on both sites. Full digest bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86, 1145943008 bytes. Draft-only architecture adapter changes no official target file. No training here.

222752 keeps baseline 222551 worker and transport bytes. Through actual /generate, it checks three generic short prompts and one exact 4000-token generic prompt twice, with 200 outputs each. Require all actual output IDs, including first token, and exact target-a/target-b stability. Diagnostic logprobs and ignore_eos stay outside ranking. [Prospective protocol and stopping rules](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-integration-20261021/PLAN.md), [updated token-route status](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-integration-20261021/TOKEN_ROUTE.md).

222752 is collected and reviewed; see [failure and telemetry](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-integration-20261021/REVIEW.md). Next use a small actual-runtime tokenizer/corpus gate before any full target-only repair. No speculative candidate is eligible. A passing JSON alone needs runtime review. Failure blocks the speculative comparison and calls for a concrete derived repair. Success permits preparing a separately frozen EAGLE3 target/draft integration with explicit capacity, real embedding sharing, feature layers, TP4/TP8 KV/state, verification kernels/graphs, memory and exact same prompt/output IDs. Only a valid useful short load warrants full scoring. No draft inference or speedup is claimed yet.

## Budget

Locked pre-submit 2026-10-21T04:57:40.859253+00:00 ledger: Used **43580.583**, Balance **20419.417**, In Doubt **0.000 SU**. Retain 222749 and 222750 unposted full maxima plus 222752 maximum; conservative internal headroom **6719.683667 SU**, unchanged **51000 cap / 13000 buffer**. [Reconciliation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-integration-20261021/reconciliation.json). The first three component charges are posted; the later two estimated charges are 2.773333 and 3.520000 SU. Retain maxima until uniquely reconciled; Balance already excludes In Doubt. Refresh under budget.lock before spending.

The previous handoff miscopied 03:46 Balance/In Doubt; its raw response was 20416.324 / 8.533 SU, not zero doubt. Corrected in the journal and current records. No extra spending follows from that correction.

## Closed branches and boundaries

CPU envelope 222551→222552 passes full local gates/mapping but gains **0.289035%**, below its prospective 1% gate: close unchanged, no repeat/promotion. Reverse startup-prefetch confirmation saves **9.836066%**, below its 10% gate: same decision. Keep H100 chunk4096/round-robin/native NUMA/MNNVL/backends; unchanged chunk/routing/DP8/DeepEP losers stay closed. [CPU review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-envelope-balance-20261020/PAIR_REVIEW.md), [priorities](../reports/research-priorities-20261020/PLAN.md), [journal](../reports/research-journey-20261019/journal/README.md), [observability limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md).

English artifacts, Vietnamese chat. Qwen only; HPC_Task empty; no slide/package changes. **Autopilot OFF**: no background Codex, schedules or automatic original-chat notifications. Preserve VPN/SSH; exclude all authentication/session state. Capture, verify, commit/push small safe milestones. Git pushes include external-object manifests, not sibling object bytes; separate off-host backup remains needed. [Policy](../research-autopilot/POLICY.md).
