# Current APAC Qwen handoff

Updated 2026-10-21T05:45:58.044033+00:00. Last native startup observation: **2026-10-21T05:42:26.240756+00:00**. Dated snapshots are not future live guarantees. [Earlier component handoff](history/20261021-before-real-token-control.md) is historical.

## Retained serving results

| Platform | Highest individual accepted job | Good output tokens/s | Status |
|---|---|---:|---|
| H200 | 24915 | 3022.034919 | N62, 98.726% joint SLA; exact independent repeat 24962 pending |
| H100 | 222048 | 2433.019859 | N54, unobserved incumbent; no new throughput result this turn |

Repeated H200 N60 is about 2989–2990. Keep platforms separate. These are local results, not global optimality or organiser accuracy. [H200 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md), [H100 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md).

**Official accuracy ≥99% of reference remains unverified.** Rank by exported AIPerf goodput ×200, fixed 4000/200, seed 2026, cold prefixes. Joint TTFT ≤3000 ms and request-mean ITL ≤20 ms; good fraction ≥0.90 including errors. [Workload and units](official-goodput-clarification-20261020.md).

## Actual submitted work

- H200 **24928 / 24962 / 24964 / 24965 / 25051** remain PD / Resources at this turn's queue query. Preserve all five; no sixth. They cover recv2, N62 repeat, observed prefill backend pair and H200 worker locality.
- H100 **222763.pbs111 is R** at 2026-10-21T05:42:26.240756+00:00: first full-target native EAGLE3 PD correctness candidate, **16 H100 / at most 30 minutes / max 1024 SU**. Native target checkpoint loading has begun; no matching fatal patterns in the bounded startup observation. No candidate result or score yet. [Receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-candidate-20261021/RESULTS.md), [startup snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-candidate-20261021/live-native-startup.json).
- **222761 is sealed usable real reference**: all **1600 actual output IDs**, four exact A/B pairs including long4000, runtime/transport/locality and sparse diagnostic telemetry reviewed. 752 seconds / estimated 427.804444 SU, still unposted at reservation. Repeated prefix caching limits timing claims. [Full review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-reference-corpusfix-20261021/REVIEW.md).
- 222752 remains a failed reference despite exit zero; 222759's cheaper actual-image tokenizer/corpus repair passes. Original failures/payloads are sealed. No organiser accuracy or new throughput claim.

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

222763 enables native EAGLE3 on both phases using the pinned BF16 public draft, two draft steps/topk1/three verification slots and FlashInfer draft attention. Target/corpus identity and transport stay unchanged. Nine semantic fixtures reject altered actual IDs even with identical text, missing first ID, changed prompts/finishes and altered identity/platform. The semantic head-script artifact gate is independent of task-launch exit. Prefill capacity may resolve 48 versus reference 4096; this N1 job is not a matched throughput comparison. [Exact gates](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-candidate-20261021/PLAN.md).

Next collect 222763 only after owned terminal F with its collect-terminal.py. Require actual native loading/precision/state/embedding/TP4-to-TP8 KV/kernel/graph/memory evidence and all exact output IDs against reviewed 222761. Inspect per-response speculative counters with inspect-speculative-metadata.py: acceptance length includes bonus and is tokens per verification forward, not tokens/s or speedup. Missing counters remain missing. Direct embedding-pointer identity is not instrumented; distinguish inspected native sharing source from runtime proof.

A valid candidate still needs a useful bounded matched load screen before full official scoring. [Prospective screen](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-candidate-20261021/SCREEN_PLAN.md) proposes a fresh equally observed N54 control/candidate at 20/40/30, zero errors, joint fraction≥0.90 and at least 3% short goodput gain before buying a full scored pair. It is not submitted/reserved; refresh actual runtime/capacity, queue and budget first. Stop/repair a failed correctness branch rather than sending a performance job.

## Budget

Locked 2026-10-21T05:39:09.523920+00:00 ledger: Used **43965.542**, Balance **19351.791**, In Doubt **682.667 SU**. 222752/222759 charges uniquely reconcile to 378.666 SU. Retain 222761 unposted full maximum 682.666667 SU plus 222763 maximum 1024 SU until uniquely reconciled. Conservative internal headroom **5327.791333 SU**, unchanged **51000 cap / 13000 buffer**. [Reconciliation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-candidate-20261021/reconciliation.json). Balance already excludes In Doubt. Refresh under lock before spending; estimated terminal cost alone does not release maxima.

The previous handoff miscopied 03:46 Balance/In Doubt; its raw response was 20416.324 / 8.533 SU, not zero doubt. Corrected in the journal and current records. No extra spending follows from that correction.

## Closed branches and boundaries

CPU envelope 222551→222552 passes full local gates/mapping but gains **0.289035%**, below its prospective 1% gate: close unchanged, no repeat/promotion. Reverse startup-prefetch confirmation saves **9.836066%**, below its 10% gate: same decision. Keep H100 chunk4096/round-robin/native NUMA/MNNVL/backends; unchanged chunk/routing/DP8/DeepEP losers stay closed. [CPU review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-envelope-balance-20261020/PAIR_REVIEW.md), [priorities](../reports/research-priorities-20261020/PLAN.md), [journal](../reports/research-journey-20261019/journal/README.md), [observability limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md).

English artifacts, Vietnamese chat. Qwen only; HPC_Task empty; no slide/package changes. **Autopilot OFF**: no background Codex, schedules or automatic original-chat notifications. Preserve VPN/SSH; exclude all authentication/session state. Capture, verify, commit/push small safe milestones. Git pushes include external-object manifests, not sibling object bytes; separate off-host backup remains needed. [Policy](../research-autopilot/POLICY.md).
