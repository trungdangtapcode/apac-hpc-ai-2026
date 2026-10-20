# Research priorities after the upstream review

## Latest refinement — 2026-10-20T14:48:56.453856+00:00

The [DeepInfer review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepinfer-review-20261020/REPORT.md) adds two bounded leads without changing the serving incumbent: verify worker CPU/GPU NUMA locality in the full allocation, and complete source/loader/transport preflight for a public lossless EAGLE3 draft of the exact Qwen original. Its use with the official FP8 target and patched TP4-to-TP8 PD path is still unverified. CPU-only source extraction/AST checks are supporting evidence, not runtime compatibility or token-equivalence gates. No new allocation is authorised merely by writing this plan; use the existing research budget, real queue caps and fresh checks before submission.

Keep existing H200 repeats/prefill pair and PBS reverse startup pair queued. DeepGEMM and overlap scheduling are already active. Historical DP8/DeepEP measurements did not beat contemporary MNNVL, so do not restart unchanged trials. Do not port architecture-specific SWA replay, alter attention mathematics, truncate input or replace the target with BF16/colocated replicas. A later derived bundle may collect full-worker rank/UUID/mask mapping; change affinity only after that evidence. EAGLE3 requires correct draft loading, hidden-state/PD geometry, target verification of every token, greedy equality and a useful short load screen before a full matched scoring pair. Full stop conditions and source links are in the review. Earlier cost figures below are historical execution snapshots; CURRENT and dated ledger receipts govern current credit.


## Concrete execution and CPU preflight — 20 October, 15:20 UTC

Worker locality captures are now submitted on both platforms: H200 25051 (16 GPUs/17 minutes) and H100 222435 (16 GPUs/30 minutes/max 1024 SU, afterany 222420). They keep existing CPU bindings and model/benchmark settings; collect actual owned worker/rank/UUID/thread masks before a binding intervention. [H200 receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/worker-locality-baseline-20261020/RESULTS.md), [H100 receipt and budget](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/worker-locality-h100-20261020/RESULTS.md).

The [EAGLE3 followup](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/REPORT.md) passes limited native-method/header checks and prepares draft architecture metadata. No tensor bytes or GPU integration yet. Stage pinned verified draft weights outside Git, validate token-ID observation and both-phase state/transport, then prepare a correctness-first pilot when a queue slot is free. Do not skip greedy equality, inherit FP8 onto the BF16 draft, promote decoded-text equality to token equality or infer a goodput win from acceptance length. Both H100 prefetch confirmation jobs pass locally, but the reverse saves 9.836066% reported walltime/SU, below the prospective 10% gate. Close the unchanged confirmation with no automatic third repeat or default promotion; retain the descriptive cost signal. Later dated ledger/receipt snapshots supersede older budget figures below.

## Decision

Keep the current serving architecture and change the priority of further work. The upstream update adds useful deployment/reference evidence; it does not change Qwen's scoring rules or supply a new implementation that should replace our measured stack. The current experiment remains the official FP8 target, plain PD disaggregation, HPC-Ops/MNNVL where validated and separately tuned concurrency on H100/H200. Do not restart a broad topology grid, switch engine/image blindly, or revive unchanged losing provider/routing/chunk settings.

The latest full H100 pair strengthens that decision: at N54, chunk 2048 is locally valid but loses 26.1328% goodput (2396.779396 versus 1770.433299 good output tokens/s), while mean TTFT increases from 746.849 to 2039.078 ms. Its reduced ITL accompanies fewer active decode requests and larger prefill queues; that is not a useful throughput win. Retain 4096. Earlier tested 8192 and native power-of-two routing also lost. H200 25020 passes all 256 synthetic projection cases, but alternatives to DeepGEMM lack a consistent useful improvement. Preserve the complete failures, output/runtime checks and telemetry rather than treating local PASS as an optimisation success.

## Ordered work

| Priority | Work | Evidence needed / acceptance |
|---|---|---|
| 1 | Confirm and preserve the best serving configuration | H200 exact N62 repeat 24962 and paired prefill-backend jobs 24964/24965 retain queue positions. Review native settings, raw tails/errors, source/output gates, profiles and matched hardware evidence before promoting a repeat. H100's retained best stays separate. |
| 2 | Make the winning result reproducible | Pin image/source/model/tokenizer hashes and account-independent build instructions. Preserve gateway, transport patches, warmup and the locked official command. Test a derived rebuild separately when needed; do not mutate frozen jobs or current submission materials during this decision turn. |
| 3 | Reduce experiment cost and startup time | Run the bounded once-per-node shard-read intervention described below. Judge end-to-end startup and allocated SU, including the prefetch stage. A startup reduction is not a new goodput record. |
| 4 | Use profiles to select the next distinct performance hypothesis | Inspect role-specific prefill and decode work, queue/batch/KV state, CPU affinity/NUMA evidence, native kernel traces and transport. Host-average CPU busy does not establish worker saturation; near-100% GPU activity does not identify a kernel bottleneck. Collect missing evidence in later derived bundles before changing the corresponding setting. |
| 5 | Separate screening from final verification | Use bounded CPU/micro or short exploratory screens when they actually answer a new question; require a full 60/120/30 scored-protocol confirmation for any final performance claim. H100 and H200 remain separate series. Do not buy a full-model run for a failed micro gate or repeat unchanged losses to fill the queue. |

Official full-set model accuracy is still unverified. The target is at least 99% of the organiser's reference score; tiny output checks are supporting diagnostics only. The public rules do not fully specify the exact evaluation implementation/dataset suite. Prepare a faithful general quality-validation route and retain this gap; do not invent a certification or promise the entire official full-set check fits the remaining credit without knowing its cost.

## Immediate bounded cost experiment

Prepared bundles 74/75 compare prefetch off versus on at fixed H100 N54, chunk 4096 and round-robin, with identical workers, official scoring, output checks, telemetry and post-score profiles. The intervention reads each indexed model shard once per allocated node before worker launch, with checked paths, bounded CPU threads/memory blocks and deadlines. It is supported by the pinned ASPIRE notes and a metadata-only check of 24 shards / 236426193880 bytes; the actual I/O runs only on the allocated nodes. Native Enroot/image migration is deliberately a separate reproducibility branch.

No cache flush or initial page-residency proof is claimed. Node assignment, filesystem state and control-first order can confound a single comparison. Count the read time in job-to-ready and SU, record both node receipts, compare all usual serving gates, and only retain a cost benefit after useful independent confirmation. Otherwise close this exact method. [Exact script, control, fixtures, limits and submission route](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/PLAN.md).

The fresh published ledger is Used 40272.495 SU / Balance 23727.505 SU / In Doubt 0; the preceding 965.404 SU chunk-pair charge reconciles. Planned pair maximum 2048 SU (two 16-H100/30-minute jobs) leaves conservative internal headroom 8679.505 SU within the unchanged 51000 cap/13000 buffer. Submission still requires a fresh own-queue/credit check under the budget lock; a prepared plan is not a receipt. Do not increase the budget or add background AI/schedules.

## Provenance and current limits

- [Pinned upstream delta and official raw reference exports](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/upstream-review-20261020/REPORT.md): main 3d05096 versus retained 5a67229, Qwen rules unchanged. Published H100 N32 reference 1173.718122 is contextual, not a matched speedup comparison with our different stack.
- [Latest H100 full pair](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-hpc-smallchunk-20261020/PAIR_REVIEW.md): exact derived-prefill-graph consequences retained, both local PASS, candidate loses.
- [Latest H200 native kernel screen](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-homebind-fix-20261020/REVIEW.md): actual /work repair and numerical/provider outcome, no new model goodput claim.

The official published source supporting the startup idea is [ASPIRE notes at 3d05096](https://github.com/hpcac/2026-APAC-HPC-AI/blob/3d050964d1008b97fb6d0d7ec5160087cd6883d9/3.2%20Qwen3%20Application%20Notes%20-%20ASPIRE%202A%2B.md). Its observed loading times are not predictions for our image, allocation or cache state.

## Definite execution checkpoint — 2026-10-20T13:28:06.162122+00:00

The planned pair is now submitted: 222407.pbs111 running, 222408.pbs111 held by afterany 222407. Both new allocations are 30 minutes / 16 H100 / maximum 1024 SU, maximum 2048 SU combined; the full official scoring interval and workers are unchanged. Published credit was rechecked before reservation; internal headroom 8679.505 SU. No measured benefit yet. The future startup reader labels topology-script-to-ready separately from complete allocated walltime, because the readiness counter excludes earlier PBS prologue.
