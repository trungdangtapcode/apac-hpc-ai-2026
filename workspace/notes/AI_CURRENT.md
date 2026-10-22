# Current GPU / AI / Qwen handoff

Updated 2026-10-22T14:18:28.492036+00:00. This handoff belongs to AI session `01a15dd3-3094-7712-a991-8ce55b15cbfe`. The separate HPC worker owns OpenFOAM. Do not modify HPC payloads, queues, notes or spending.

## Current measured results

| Hardware / point | Good output tokens/s | Joint SLA | Interpretation |
|---|---:|---:|---|
| H200 full N64, 25366 | 3044.489701 | 98.633018% | Highest single accepted local measurement; repeat 25373=3044.074628, two-run mean 3044.282165 |
| H200 fresh observed N62, 25365 | 3011.875113 | 98.722725% | Matched control; N64 improves by 1.082867% |
| H200 reproduced observer-off N62, 24962 / 24915 | 3023.072304 / 3022.034919 | Both pass | Prior reproduced point; mean 3022.553611 |
| H100 incumbent N54, 222048 | 2433.019859 | Local pass | Different hardware; do not merge H100/H200 rankings |

Full N64 has zero request errors/cancellations, 1876/1902 jointly good, TTFT mean/p95 1110.463377/1351.632306 ms, and request-mean ITL mean/p95 15.002881/15.163328 ms. Raw classification finds 26 TTFT breaches and no ITL breach. Local short output non-regression and long retrieval 12/12 pass. Exported output-length counts are 1898 at 200, three at 199 and one at 198; actual per-response generated token IDs were not retained. Keep the nominal 200-token workload and official Goodput × 200 rule unchanged.

**Official accuracy at least 99% of reference remains unverified.** No global SOTA claim. N64 replication 25373 now passes full local gates within −0.013634% of source 25366. The existing packaged primary remains N62 until a separate reviewed AI package update; N64 is a reproduced local candidate, not an official accuracy pass. [Full N64 proof](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/REVIEW.json), [matched N62](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25365-20261022/REVIEW.md).

## Current H200 followup and completed evidence

- **25487 → 25488**, fresh full N64 control then N68 candidate afterok, each 16 H200 GPUs / two nodes / at most 17 minutes, full 60/120/30. Only offered load differs; all operational files are byte-identical. Immediate queue snapshot: Resources / Dependency. Query Slurm for live state. [Definite receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261022-n68-full/RESULTS.md).
- Completed **25371** short N64/N68 passes all local gates: 2830.699360 → 2895.054081 good output tokens/s, +2.273457%, joint SLA 95.931142% / 95.890411%, zero errors/cancellations, long retrieval 12/12. Actual scored decode running-request log maxima are 54 / 58, below graph cap 64. Fixed-order short scores are unranked. [Review, tails and telemetry](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25371-20261022/REVIEW.md).
- Completed **25373** independently repeats full N64 at 3044.074628 good output tokens/s, joint SLA 98.632299%, zero errors/cancellations, long 12/12. TTFT mean/p95 1113.240102 / 1309.781135 ms; request-mean ITL mean/p95 14.992752 / 15.159936 ms. All 26 failures breach TTFT; output-length counters are 1896 at 200 and five at 199. Same sampled UUID sets as source limit hardware diversity. [Full review and observability](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25373-20261022/REVIEW.md).

The full N68 pair must pass protocol/runtime/output/SLA and zero-error gates, and improve by at least 1% over its own fresh full N64 control before N68 replication. Dense graphs remain 1–64; client concurrency is not actual batch size. Maximum five own active/pending jobs and the actual 17-minute partition limit remain unchanged. No PBS SU is reserved by these Slurm jobs.

## Decisions from completed runs

The reviewed full N60 wave scores are control 24964=2981.417188, both-HPC 24965=2886.298789 (−3.1904%), locality capture 25051=2985.515382 (+0.1375%), and power_of_two router 25283=2867.923337 (−3.8067%). Close unchanged both-HPC and power_of_two branches; locality is diagnostic, not a demonstrated gain. [Wave review and phase-aligned observability](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-h200-wave-20261021/REVIEW.md). Short 25339 favored N64 by 2.861439%; it justified the fresh full pair, not a ranked score.

[Initial-cohort analysis](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/phase-transition-review-20261022/REVIEW.md) finds that all TTFT failures in six inspected full/short points started within the first 39 ms of profiling; new N64 failures start no later than 33.481316 ms. No later failures or ITL breaches in those points. This is an association, not a causal prefill diagnosis. Recovering all such failures at unchanged duration would yield only about 1.20–1.39% in those full points; this arithmetic ceiling is not a forecast. Keep all official scored requests in the denominator.

Sampled GPU activity, allocated VRAM, KV token occupancy and kernel-time sums are different quantities. The phase-aligned wave review corrects the server-metrics success key and retains HTTP 200 payloads. Profile stop can return HTTP 500 even though scored requests have zero errors. Trace names are inventoried; trace contents are not generally inspected. [Matched N62/N64 inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25366-20261022/observability.md) now retains per-role telemetry, tail latency, profile controls and explicit limits.

## H100 NIXL / EAGLE3 branch

All no-model component probes pass: 223091 base VRAM transfers, 223097 actual patched descriptors, and **223132 native 190-range VRAM registration plus pinned-DRAM auxiliary transfer**. Latest is F/exit 0, 315 seconds, estimated 22.4 SU, on 039/037. Three KV writes and one auxiliary write pass independent byte/hash checks. [Sealed native review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-native-registration-probe-20261021/REVIEW.md).

These small buffers and different hosts do not prove full EAGLE3 transport or output correctness. Full 223055 failed at an earlier NIXL remote disconnect; later metadata-not-found was downstream. Its ALL_PAIRS_WARM marker was false because remote child status was masked; the final token gate correctly rejected HTTP 500 and zero outputs. [Failure review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-eager-prefill-r3-20261021/REVIEW.md). The independent [semantic warmup receipt gate](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/pair-warmup-semantic-20261021/PLAN.md) is CPU-validated, not yet deployed into a full-model run.

Prepare a native H200 target-only reference and separate EAGLE3 exact-token diagnostic to save H100 SU. The first reference proposal is under isolated CPU development in `eagle3-h200-reference-20261022`, not frozen or submitted. Do not copy PBS aliases into Slurm. Require verified draft/model/image identity, one absolute startup deadline, fresh H200 reference IDs and semantic pair receipts before scoring. No full EAGLE3 equivalence or throughput gain is established. The [native H200 EAGLE3 design](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-h200-port-20261022/PLAN.md) is preserved but not frozen/submitted. The [P12/D4 proposal](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261022-p12-hpc/PLAN.md) is withheld after source review: equal-TP NIXL prepares the entire KV pool, with actual candidate geometry/memory/time unbounded; topology-specific validator support is also missing. Seven CPU structure checks pass, not GPU readiness.

## Access, budget, backup and operating policy

**22 October access attempt:** the previous VPN pane was dead. At the owner's explicit request only that pane was restarted, preserving private recovery state. Gateway authentication failed; no VPN connection or DUO phone approval was established, and SSH reachability timed out. The rejection reason is unverified; no repeat login loop. [Safe record](vpn-access-20261022.md). PBS credit below is a dated retained snapshot, not a fresh query.


Latest retained locked PBS snapshot: **2026-10-22T00:09:19.059347Z**, Used **46381.861 SU**, Balance **17575.472 SU**, In Doubt **42.667 SU**. Maximum **42.666667 SU** for 223132 remains reserved until its charge is uniquely reconciled. Internal headroom **4575.472333 SU** under the unchanged 51000 cap / 13000 reserve. The published balance already excludes the prepayment; do not subtract it twice. This is a dated snapshot, not live credit. No new PBS GPU job is authorised merely by an access check, and HPC spending is separate.

Edit active sources once, capture explicit safe checkpoints into the local archive, verify, commit with actual dates and push promptly. GitHub contains the Git portion and external-object manifests; the sibling artifact store still needs a separate off-host copy. Never capture credentials or session state. English artifacts, Vietnamese chat. Autopilot is OFF; no schedules, background Codex or automatic chat-notification promises.

[Complete journal](../reports/research-journey-20261019/journal/README.md), [historical pre-consolidation handoff](history/20261022-ai-before-n64-handoff.md), [21 October submission](submission-update-20261021.md), [official protocol and units](official-goodput-clarification-20261020.md).
