# Current APAC Qwen handoff

Updated 2026-10-21T03:48:12.009783+00:00. Scheduler and credit observations below have explicit dates. [Earlier handoff](history/20261021-before-component-handoff.md) is historical.

## Retained serving results

| Platform | Highest individual accepted job | Good output tokens/s | Status |
|---|---|---:|---|
| H200 | 24915 | 3022.034919 | N62, 98.726% joint SLA; exact independent repeat 24962 still pending |
| H100 | 222048 | 2433.019859 | N54, unobserved incumbent; no new useful gain in the CPU pair |

Repeated H200 N60 is about 2989–2990. Keep H100/H200 series separate. These are local accepted results, not proof of global optimality or organiser full-set accuracy. [H200 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md), [H100 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md).

**Official accuracy at 99% of reference remains unverified.** Rank by exported AIPerf goodput × 200, fixed 4000/200 tokens, seed 2026 and cold prefixes. Require joint TTFT ≤ 3000 ms / request-mean ITL ≤ 20 ms and good fraction ≥ 0.90 including errors. [Workload and units](official-goodput-clarification-20261020.md).

## Actual queues at 2026-10-21T03:48:12.009783+00:00

- H200 **24928 / 24962 / 24964 / 24965 / 25051** remain pending for Resources. Preserve all five positions; no sixth job. They cover receive interval 2, the N62 repeat, the observed prefill backend pair and actual H200 worker locality.
- H100 **222729.pbs111 is running**, one GPU / four minutes / maximum 8.533334 SU. The last reported walltime is 12 seconds. It is a component gate, not a full model benchmark. [Own queue snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-component-homefix-20261021/live-final.json).
- Earlier H100 222551/222552 and 222721/222722 are completed; exit status alone is not a performance/quality PASS. Their reviewed outcomes follow.

## CPU-envelope branch closed

**222551 legacy → 222552 balanced** passes sealed local protocol/SLA/runtime/output-comparison gates and proves the intended masks on all 16 GPU schedulers. Same 32/32/64 CPU/core budgets, unchanged serving/benchmark and native NUMA locality. Goodput **2407.544052 → 2414.502691**, only **+0.289035%**, below the prospective **1%** useful-gain gate. **Close this exact policy, no unchanged repeat or default promotion.** [Complete result, mapping, tails, hardware and cost review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-envelope-balance-20261020/PAIR_REVIEW.md).

The same baseline short mismatch persists; long checks are 12/12, scored request errors zero, and 16 post-score rank traces per job are inspected. Native profile-stop HTTP 500 remains. Sampled decode GPU activity is near 100%, not a causal bottleneck proof; scored per-thread demand, memory placement and inflight remain uncollected. H200 mapping job 25051 has not run; do not transfer the H100 result numerically.

## EAGLE3 component progress

| Job | Actual observation | Interpretation |
|---|---|---|
| 222721 | F / exit 1, 105 s: actual chat gateway drops token-ID extensions | Unsupported diagnostic route; config/tensor stages not reached; no model load |
| 222722 | F / exit 1, 89 s: native /generate forwarding and synthetic logprob IDs pass; imports fail at read-only HOME | Gateway capability is verified only with synthetic workers; native config/tensors still unverified |
| 222729 | Running: same diagnostic scripts with writable private HOME/cache | Await actual component result; no correctness or performance claim |

[First failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-component-20261021/REVIEW.md), [second review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-component-generate-20261021/REVIEW.md), [current exact repair and gates](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-component-homefix-20261021/PLAN.md), [receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-component-homefix-20261021/RESULTS.md).

The public draft ff0f0c09 is staged and digest-verified on both sites, outside Git. Its size is 1145943008 bytes and SHA256 bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86. Only recovery metadata is captured. The draft-only architecture adapter changes no official target file. Synthetic gateway IDs are never counted as model output; the official AIPerf streaming chat command remains unchanged.

Next review 222729. A complete component PASS only permits preparing the next bounded integration stage: real draft class/parameter loading, feature layers, TP4-to-TP8 state/KV transfer, kernels/graphs, memory and stable target-only versus speculative actual token IDs. A real response must expose every output ID, including its first token; text equality is insufficient. Only a valid useful unranked load screen warrants a full scoring pair. No full-target speculative GPU job exists yet; keep native verification intact. Preserve all failures and repair derived payloads rather than mutating submitted files.

## Credit and reservations

Fresh locked pre-submit ledger for 222729: Used **43575.143 SU**, Balance **20424.857 SU**, In Doubt **0 SU**. The CPU pair's 938.098 SU and first component's 3.733 SU reconcile. The second component's estimated 3.164444 SU is unposted; retain its full maximum plus 222729's maximum, total **17.066667 SU**. Conservative internal headroom is **7407.790333 SU**, unchanged **51000 cap / 13000 buffer**. [Structured queue/accounting/ledger and proof](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-component-homefix-20261021/reconciliation.json). Refresh and uniquely reconcile before further spending; Balance already excludes In Doubt.

The submission adapter now parses only the independent qstat -u response, avoiding wrapped historical argument lines. Its initial false-positive guard failed before reservation/qsub and is preserved. Upload resumption required reverified manifests and proof of no uncertain submission. No duplicate allocation occurred.

## Other decisions and boundaries

Close unchanged startup-prefetch confirmation: reverse pair saved 9.836066% allocated walltime/SU, below its 10% prospective gate; no automatic third repeat or default promotion. [Pair review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-confirm-20261020/PAIR_REVIEW.md). Keep H100 chunk 4096/round-robin, native MNNVL and validated compute backends. Unchanged losing chunk/routing/DP8/DeepEP branches stay closed. [Priorities](../reports/research-priorities-20261020/PLAN.md), [journal](../reports/research-journey-20261019/journal/README.md), [observability limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md).

[Competition registration clarification](contest-scoring-and-tracks-20261020.md) preserves conflicting recruitment/current-rule wording; original accepted entry and AI-only specialist eligibility remain unverified. Qwen-only work scope and empty HPC_Task do not establish an exemption. The owner authorised committing the clarification on 21 October; the earlier no-commit restriction is historical.

English artifacts, Vietnamese chat. Qwen only; HPC_Task empty. No package/slide edit. **Autopilot OFF**: no background Codex, schedules or automatic chat notifications. Preserve VPN/SSH and exclude credentials/session state. Capture, verify, commit and push small safe milestones. External sibling artifact bytes still require off-host backup; Git pushes contain their manifests, not those bytes. [Execution policy](../research-autopilot/POLICY.md).
