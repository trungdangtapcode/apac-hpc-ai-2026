# Current APAC Qwen handoff

Updated 2026-10-21T09:46:58.182280+00:00. [21 October complete submission](submission-update-20261021.md) now includes the primary N62 script, build instructions, raw evidence and updated slides. Scheduler snapshots below are dated; query real state on resume.

## Retained serving results

| Platform | Highest individual accepted job | Good output tokens/s | Status |
|---|---|---:|---|
| H200 | 24915 | 3022.034919 | N62, 98.726% joint SLA; exact independent repeat 24962 pending |
| H100 | 222048 | 2433.019859 | N54 incumbent; no new throughput result in this branch |

Repeated H200 N60 is about 2989–2990. Keep platforms separate. These are local results, not global optimality or organiser accuracy. **Official accuracy ≥99% of reference remains unverified.** Rank by exported AIPerf goodput×200; fixed 4000/200, seed 2026, cold prefixes, joint TTFT≤3000 ms / request-mean ITL≤20 ms, fraction≥0.90 including errors. [Units/protocol](official-goodput-clarification-20261020.md).

## Actual submitted work

- H200 **24928 / 24962 / 24964 / 24965 / 25051** are PD / Priority at 2026-10-21T09:44:32.900086+00:00; earlier Resources reason is historical. Preserve all five, no sixth: recv2, N62 repeat, observed prefill backend pair and worker locality.
- H100 **222780.pbs111 current state is unavailable**: last known R in the earlier 06:02:49 UTC snapshot; no live VPN session at the latest collection attempt. It is the separately derived explicit-BF16 native EAGLE3 PD correctness repair, **16 H100 / at most 30 minutes / max 1024 SU**. [Receipt and raw snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-bf16-20261021/RESULTS.md). No full repair output/graph/transport or performance result yet.
- PBS own queue was empty before submission; no dependency, overlap or uncertain retry. No background Codex/schedule is enabled.

## EAGLE3 journey: accepted evidence and failures

| Jobs | Actual observation | Decision and limit |
|---|---|---|
| 222721 / 222722 / 222729 | Unsupported chat extension, read-only HOME, then missing raw UUID comparison | Preserve failures; diagnostic repairs are separate frozen payloads |
| 222749 / 222750 | Registry/tensor/map checks pass; actual native single-rank draft loads all 13 float tensors into 10 exact non-shared parameters | No full attention or real target-shared embedding in that earlier loader |
| 222752 / 222759 | Full reference fails BatchEncoding JSON despite exit0; cheaper actual-tokenizer corpus repair passes | Never promote scheduler exit alone; freeze plain IDs and use semantic result gate |
| 222761 | Sealed real target reference: 1600 actual output IDs, four exact A/B pairs including long4000 | Usable exact reference; cached repeat/N1 timings are not throughput |
| 222763 | Full native candidate fails before readiness at draft input RMSNorm graph; target KV BF16/draft KV FP16 | 408 s / estimated 232.106667 SU; no request, output-equivalence or score |
| 222769 | Native auto FP16/shared BF16 mismatch reproduces; explicit BF16/unquant eager and graph norm pass | 157 s / estimated 5.582222 SU; real target embedding alias in one-rank layer fixture, not full PD |
| 222780.pbs111 | Explicit BF16/unquant full repair submitted | Await actual native graphs/state/transport/output evidence |

[Reviewed real reference](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-reference-corpusfix-20261021/REVIEW.md), [native PD failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-candidate-20261021/REVIEW.md), [verified dtype mechanism](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-dtype-probe-20261021/REVIEW.md), [complete journal](../reports/research-journey-20261019/journal/README.md). Preserve raw payloads, failures and seals.

The public draft is nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507 at ff0f0c0999f6c86b21dfd2f5803eebc4ac712224, 1145943008 bytes, SHA256 bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86, outside Git on both sites. Serialized tensors are BF16 but config has no dtype: native auto actually casts draft to FP16. The small fixture proves target remains BF16 activations/FP8 quantization in both auto and explicit modes, while the corrected draft/norm/embedding all become BF16. Native draft quantization can inherit an explicit target setting; **unquant** is the supported explicit opt-out. Earlier blanket default-none claims were incomplete.

222780.pbs111 adds only **--dtype bfloat16** and **--speculative-draft-model-quantization unquant** to both roles. Official FP8 target files, accepted 222761 corpus/reference, native verification, client/semantic/transport bytes and nine guard fixtures stay unchanged. [Exact repair/gates](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-bf16-20261021/PLAN.md). This is not a target precision conversion or unchanged retry.

## Next decision

The full submission is updated and validated: primary H200 N62 from 24915, 264 component checks, 32 English slides, raw control/repeat logs and ZIP checksums. Portable GPU replay and official accuracy remain unverified. [Delivery](submission-update-20261021.md). No new GPU reservation; five H200 slots occupied and PBS access unavailable. Preserve VPN/auth; no replacement login or DUO was started.

Collect 222780.pbs111 only after owned terminal F with its collect-terminal.py. Inspect semantic artifact, actual native precision/loading/embedding/auxiliary state, TP4-to-TP8 KV transfer, all verification/draft graphs, memory and exact actual IDs against 222761. A layer fixture does not waive full integration. Inspect runtime/transport errors and phase-aligned hardware/server/locality evidence; missing fields remain missing. Use inspect-speculative-metadata.py on the collection: acceptance length includes bonus and is tokens per verification forward, not tokens/s or speedup. No direct full-PD pointer-identity instrumentation exists; distinguish native source and fixture proof from full runtime proof.

If valid and useful, prepare a fresh equally observed/capacity-controlled short N54 pair before full scoring. The [new capacity contract](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-screen-contract-20261021/PLAN.md) explicitly sets prefill 64 / decode 256 on both sides and checks early arguments plus final scheduler capacity. Four native branch cases and eleven adversarial log fixtures pass; no GPU screen or reservation. 222761 logs None then scheduler 4096; failed 222763 logs 48 with no final scheduler receipt. These are different initialization stages, not new throughput results. [Prospective screen](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-candidate-20261021/SCREEN_PLAN.md): 20/40/30, zero errors, joint fraction≥0.90 and at least 3% short goodput gain before a full official 60/120/30 pair. It is not submitted/reserved. Prefill speculative default 48 differs from baseline 4096; do not call N1 correctness matched throughput. Failure requires a concrete supported repair or branch closure, not a blind scoring run.

## Budget and scope

Locked pre-submit 2026-10-21T06:01:09.427656+00:00 ledger: Used **44625.453**, Balance **19366.014**, In Doubt **8.533 SU**. Failed 222763 charge 232.107 SU reconciles. Retain unposted 222769 maximum 8.533334 SU plus 222780.pbs111 maximum 1024 SU. Conservative internal headroom **5342.013667 SU**, unchanged **51000 cap / 13000 buffer**. [Reconciliation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-bf16-20261021/reconciliation.json). Refresh under lock before spending; Balance already excludes In Doubt. Estimated terminal costs do not release maxima alone.

CPU envelope gains 0.289035%, below 1% gate; reverse prefetch saves 9.836066%, below 10% gate. Both exact methods stay closed unchanged, as do losing chunk/routing/DP8/DeepEP repeats. Keep native NUMA and retained backends. [Priorities](../reports/research-priorities-20261020/PLAN.md), [observability limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md).

English artifacts, Vietnamese chat. Qwen only; HPC_Task empty. The owner authorised a full submission update on 21 October; the previous no-edit restriction is superseded. **Autopilot OFF**: no background Codex, schedules or automatic chat notification. Preserve VPN/authentication and exclude session/credential state. Explicit safe small capture/commit/push checkpoints; Git carries external-object manifests, not sibling artifact bytes (separate off-host backup still needed). [Policy](../research-autopilot/POLICY.md).
