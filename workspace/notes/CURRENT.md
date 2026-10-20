# Current APAC Qwen handoff

Updated 2026-10-20T14:48:56.453856+00:00. Scheduler and credit observations are dated below; do not treat older linked snapshots as live.

## Accepted serving results

- H200 highest individual: **24915 = 3022.034919 good output tokens/s**, N62, 98.726% joint SLA. Full local gates pass; exact independent repeat 24962 is still pending at this check. Repeated N60 results 24738/24913 are 2990.151/2989.175. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md).
- H100 highest individual: **222048 = 2433.019859 good output tokens/s**, N54. Observed controls commonly measure about 2396–2412; no new serving peak. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md).
- Keep the platforms separate. **Official full-set accuracy at 99% of reference remains unverified**; local output checks are not that certification. Official metric is AIPerf Goodput × 200, with joint TTFT 3000 ms / ITL 20 ms and qualifying fraction >= 0.90. [Workload/source clarification](official-goodput-clarification-20261020.md).

## Latest completed comparison: startup cost

Both 222407 off and 222408 read pass all local serving and sealed node-prefetch gates. The candidate reads 24 model shards / 236426193880 bytes on each node, taking 27.527/27.290 seconds. It changes no model computation or prefix-reuse benchmark setting.

| Quantity | Off 222407 | Read 222408 |
|---|---:|---:|
| Topology-script start to workers-ready, seconds |602 |436 |
| PBS resources_used.walltime, seconds |934 |759 |
| Walltime-derived charge, SU |531.342222 |431.786667 |
| Good output tokens/s |2411.827128 |2395.929777 |
| Joint qualifying fraction |0.982850 |0.981445 |

Ready time decreases 27.575%, scheduler-reported walltime 18.737%, about 99.556 SU saving; goodput changes -0.659%. The readiness counter excludes earlier PBS prologue. Different nodes and unknown initial cache residency confound causality. All raw tails/runtime/output, sixteen traces per job and matched scored role/hardware evidence were inspected. Profile stop HTTP 500 after bounded post-score traces remains a known limitation. [Complete review and gates](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/PAIR_REVIEW.md).

## Submitted next step and queues

**PBS 222419 read first → 222420 off second**, afterany static probe 222412. Verified submission snapshot: probe R, pair H/H. The probe is now terminal F/exit 0; its sealed static topology has been collected and reviewed. Updated model states are Q/H in the balance check below. Each model job 16 H100 / 30 minutes / maximum 1024 SU. Reverse-order prospective gates: at least 10% lower walltime/SU, lower readiness time including prefetch, no more than 2% lower goodput and all full local gates. One confirmation only; if it fails, close or mark inconclusive. [Plan and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-confirm-20261020/RESULTS.md).

Static probe 222412 is one H100/three minutes/maximum 6.4 SU, no model loaded. Its allowed CPUs are entirely NUMA 0, while the allocated GPU locality is NUMA 1, with no intersection. This one-GPU allocation does not establish full-serving worker mappings, CPU saturation or a performance bottleneck. Collect actual worker affinity before changing binding. [Terminal review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-gpu-locality-20261020/REVIEW.md). Its local post-submit plan-writer correction is preserved; no duplicate qsub occurred. [Record](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-gpu-locality-20261020/RESULTS.md).

H200 **24928/24962/24964/24965** remain **Priority-pending**, fresh snapshot in the reverse confirmation folder. They test receive interval 2 / N60, exact N62 repeat and the observed DeepGEMM 8192 / HPC-Ops 8192 prefill pair. Keep positions and frozen payloads. H200 micro 25020 passes 256 cases but alternative providers lack a consistent useful signal; keep DeepGEMM. [Kernel evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-homebind-fix-20261020/REVIEW.md).

## Budget and next decisions

Fresh ledger queried 2026-10-20T14:21:57.736435+00:00: grant 64000 SU, Used 41238.397 SU, Balance 22761.603 SU, In Doubt 0. Static probe 222412 finishes exit 0 with 78 s reported walltime; its 2.773333 SU estimate reconciles to the 2.773 SU published delta. Its raw topology evidence is now collected and reviewed separately; scheduler exit alone is not a topology assessment. Current model jobs 222419/222420 are Q/H, reserving 2048 SU maximum. Retain 13000 SU project buffer; available internal research headroom is 7713.603 SU under the 51000 SU cap. Balance already excludes In Doubt, so do not deduct it again. No new job or GPU spending for this balance-only question. [Source and arithmetic](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/budget-checks/20261020-1421/review.json).

Keep H100 4096/round-robin; close tested chunk 2048 (-26.133%), 8192 (-0.781%) and native power-of-two (-4.865%) branches. Keep validated attention/transport/provider choices. Use measured bottlenecks for the next distinct experiment. [Priorities](../reports/research-priorities-20261020/PLAN.md), [upstream review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/upstream-review-20261020/REPORT.md), [full journal](../reports/research-journey-20261019/journal/README.md).

## DeepInfer review and next distinct leads

[Source-backed review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepinfer-review-20261020/REPORT.md) pins DeepInfer 774ce244 and the Nebius Qwen EAGLE3 draft ff0f0c09. Do not switch to DeepInfer: its listed model/hardware and released service components do not cover our Qwen/Hopper PD deployment. The pasted BF16 target / colocated replica recipes do not satisfy Basic rules. DeepGEMM and CPU/GPU overlap are already used. Historical attention-DP8/DeepEP trials 23780/23859 lost against contemporary MNNVL; do not reopen unchanged settings based on popularity.

Two concrete leads remain: collect actual full-serving worker CPU/NUMA mapping after the sealed static probe, and finish CPU compatibility checks for lossless EAGLE3. The public draft is a real candidate for the original Qwen checkpoint, not validated for our FP8 target or patched heterogeneous-TP NIXL. Native source exposes draft KV/hidden-state paths but loader, metadata/geometry, kernels/graphs and greedy equality remain unresolved. No weights downloaded, runtime imported, engine installed or new GPU job submitted for this review. No speedup or official accuracy result is claimed.

Read-only queues checked 2026-10-20T14:45:58Z: H200 24928/24962/24964/24965 Priority-pending; PBS 222419 Q and 222420 dependency-held H. Preserve positions. Credit remains the explicitly dated 14:21 ledger above; refresh before any additional PBS reservation. [Detailed hypotheses and stopping gates](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepinfer-review-20261020/REPORT.md).

## Persistent boundaries

English artifacts, Vietnamese chat; Qwen only, HPC_Task empty. No submission/package edit this checkpoint. Autopilot OFF: no background Codex, schedules or automatic chat-notification promises. Keep working VPN/SSH sessions; do not restart authentication unnecessarily. Never capture credentials or session state. Edit active sources once; explicitly capture/verify/commit/push each coherent safe milestone to the authorised private archive. Large external artifact bytes still need a separate off-host copy; Git pushes do not include them.

Prior detailed snapshots remain [historical](history/20261020-before-prefetch-confirmation.md); raw evidence and failures are retained in the linked records.
