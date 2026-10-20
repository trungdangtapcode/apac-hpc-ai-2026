# Current APAC Qwen handoff

Updated 2026-10-20T15:21:42.581358+00:00. Queue and budget observations have explicit times; earlier snapshots are historical.

## Accepted serving results

- H200 highest individual **24915: 3022.034919 good output tokens/s**, N62, 98.726% joint SLA. Exact independent repeat 24962 remains pending. Repeated N60 is about 2989–2990. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0218/RESULTS.md).
- H100 highest individual **222048: 2433.019859 good output tokens/s**, N54. New read-first 222419 gives 2398.983183, not a new peak. [Incumbent review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h100-restored/RESULTS.md).
- Keep platforms separate. **Official full-set accuracy at 99% of reference remains unverified.** Score is AIPerf Goodput × 200, with joint TTFT ≤ 3000 ms / average request ITL ≤ 20 ms and fraction ≥ 0.90 including errors. [Official workload](official-goodput-clarification-20261020.md).

## Actual queues and new submissions

Read-only scheduler check **2026-10-20T15:21:42.581358+00:00**, [raw snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/final-queues.json):

- H200 **24928 / 24962 / 24964 / 24965 / 25051** are all Priority-pending. Five active/pending positions: preserve them, no sixth job. Older jobs test receive interval 2, exact N62 repeat and the observed prefill backend pair.
- PBS **222420 is R**, reported elapsed 7:19 at the check. It is the reversed prefetch off-control, not yet a terminal result. **222435 is H afterany 222420**. Keep the serial one-running allocation limit.
- New H200 **25051**, two nodes / 16 GPUs / 17 minutes, gathers actual N60 worker locality before changing binding. [Receipt and plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/worker-locality-baseline-20261020/RESULTS.md).
- New H100 **222435**, two nodes / 16 GPUs / 30 minutes / maximum 1024 SU, gathers the corresponding N54 placement on the platform where the original static mismatch was measured. [Receipt and plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/worker-locality-h100-20261020/RESULTS.md).

Both new bundles retain model/benchmark/transport/normal resource sampler and profiler settings plus the original CPU bindings. The only new intervention is a bounded pre-score observer of owned process/thread CPU masks and namespace PID → GPU UUID/PCI/NUMA mapping. CPU fixtures and frozen-payload derivation checks pass; there is no actual worker mapping result or optimisation claim yet. Inspect full role/rank data before a separate controlled affinity candidate. Missing fields or ambiguous PIDs are incomplete evidence, not healthy placement. No scored per-thread CPU-demand or host memory-placement measurement is claimed.

## Startup cost branch

Original off/read **222407/222408** pass locally: topology-to-ready 602/436 s, PBS walltime 934/759 s, goodput 2411.827128/2395.929777. Initial cost signal is promising but different nodes/unknown cache residency confound causality. [Pair review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/PAIR_REVIEW.md).

Reversed **read-first 222419** passes sealed serving/startup/runtime/output gates: **2398.983183 good tokens/s**, joint **98.146923%**, mean TTFT **737.915273 ms**, mean ITL **18.180412 ms**, errors/cancellations 0, long 12/12. Reads take 27.858/28.008 s, topology-to-ready **438 s**, PBS walltime **770 s**, estimated **438.044444 SU** unposted at the last ledger check. Sixteen rank traces, 357/357 post-score diagnostic requests and 25 scored resource/server samples per role / 16 UUIDs inspected. Known profile-stop HTTP 500 remains; inflight, scored per-thread CPU and memory placement are uncollected. [Complete review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-confirm-20261020/222419_REVIEW.md).

Wait for **222420** before accepting the reverse confirmation: require at least 10% lower walltime/SU, lower readiness including reads, no more than 2% lower goodput and all local gates. If it fails, close or mark inconclusive; no automatic third prefetch repeat. Startup saving is not a new serving peak.

## Budget and reservations

Last locked ledger query **2026-10-20T15:16:00.806345+00:00**, published balance timestamp 20/10/2026-23:00:02: grant **64000 SU**, Used **41238.397 SU**, Balance **21737.603 SU**, In Doubt **1024 SU**. Balance already excludes In Doubt. Terminal 222419 has not yet increased Used; retain its full maximum until uniquely reconciled. Outstanding maxima for 222419/222420/222435 total **3072 SU**. Internal research headroom **6689.603 SU**, unchanged **51000 SU cap / 13000 SU buffer**. [Fresh source and arithmetic](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/worker-locality-h100-20261020/RESULTS.md). Refresh and reconcile before any new PBS reservation; do not subtract prepayment twice.

## EAGLE3 and next distinct hypotheses

[DeepInfer assessment](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepinfer-review-20261020/REPORT.md): do not migrate this Qwen/Hopper PD stack to its currently listed DeepSeek/SM100 engine. DeepGEMM and scheduling overlap are already active; historical DP8/DeepEP trials lost to contemporary MNNVL, so do not repeat unchanged settings based on popularity. BF16 target / colocated replica recipes do not satisfy Basic rules.

[New EAGLE3 CPU preflight](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-preflight-20261020/REPORT.md) pins Nebius draft ff0f0c09 for the exact original Qwen. Public header-only requests read 1504 bytes, **15 tensor entries**; shapes match the native one-layer BF16 EAGLE3 structure. A draft-only architecture metadata adapter is prepared. Actual native pointer helper checks preserve 188/188/190 ordered pairs in the three limited fixtures. No tensor payload downloaded, full runtime imported or speculative GPU job submitted.

Next stage verified pinned draft bytes outside Git, validate loader coverage and token-ID observation, then prepare a correctness-first H200 pilot when a slot becomes available. Both-phase hidden state/KV metadata, patched TP4→TP8 byte/page geometry, verification kernels/graphs, memory and **exact greedy token equality** remain runtime gates. Decoded text equality alone is weaker; acceptance length is not goodput. Do not change target FP8 math, relax verification or promise a speedup. Current queues remain occupied while these source questions are resolved.

Keep H100 chunk4096/round-robin; close unchanged chunk2048 (-26.133%), chunk8192 (-0.781%) and native power-of-two (-4.865%) branches. H200 micro25020 passed 256 cases without a consistent alternative-provider win: keep DeepGEMM. Static H100222412 has sealed CPU NUMA0 versus GPU NUMA1 locality, 78 s / 2.773333 SU reconciled; it does not establish full-serving misbinding or CPU saturation. [Priorities](../reports/research-priorities-20261020/PLAN.md), [full journal](../reports/research-journey-20261019/journal/README.md).

## Persistent boundaries and preservation

English artifacts, Vietnamese chat; Qwen only, HPC_Task empty. No submission/package edit. Autopilot OFF: no background Codex, schedules or automatic chat-notification promises. Keep working VPN/SSH sessions and never capture authentication/session material. Edit active sources once; capture, verify, commit and push small safe milestones. Large sibling artifact bytes still require a separate off-host copy; Git pushes contain manifests, not those bytes. [Earlier detailed handoff](history/20261020-before-worker-locality-handoff.md) is historical.
