# Current AI / Qwen research handoff

Updated 2026-10-23T15:53:59.929324+00:00. GPU parent session: `01a15dd3-3094-7712-a991-8ce55b15cbfe`; current verified GPU fork: `01a166eb-33cb-7ce0-9699-ec65de26689a`. The separate worker owns HPC/OpenFOAM. This file is a dated handoff; query actual schedulers before claiming live state.

## Read and explain the journey

Start with the [beginner narrative](../reports/ai-research-learning-journey-20261023/README.md), [speaker notes](../reports/ai-research-learning-journey-20261023/SPEAKER_NOTES.md) and [glossary](../reports/ai-research-learning-journey-20261023/GLOSSARY.md). The [detailed journal](../reports/research-journey-20261019/journal/README.md) retains questions, controls, failures, measurements, limits and next decisions. Preserve every milestone in English with metric units and a short spoken explanation. Vietnamese is for chat only. The [previous full handoff](history/20261023-ai-before-concise-nonlogin-handoff.md) preserves all earlier accounts; it is historical.

## Measured frontier

| Hardware / point | Good output tokens/s | Meaning |
|---|---:|---|
| H200 N64: 25366 / 25373 / 25487 | Mean **3044.400475**; highest repeat 3044.637094 | Reproduced local choice; last joint SLA 98.632299%, zero errors/cancel |
| H200 N68: 25488 | **3047.165853** | Single local peak, only +0.083056% over fresh N64; below 1% repeat gate, close unchanged |
| H200 N62: 25365 | **3011.875113** | Fresh matched control; N64 improves 1.082867% |
| H100 N54: 222048 | **2433.019859** | Separate hardware series; do not merge rankings |

**Official accuracy at least 99% of reference remains unverified.** No global SOTA or EAGLE speedup claim. Short/long output diagnostics support local non-regression only. Keep official Goodput × 200, fixed 4000/200 workload, seed 2026, cold prefixes and closed-loop concurrency. Full local scoring is 60/120/30 seconds; shorter screens are unranked. [Official clarification](official-goodput-clarification-20261020.md), [full N64/N68 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25487-25488-20261023/REVIEW.md).

## H200 queue: last checked 23 October 15:52 UTC

- **25682**, EAGLE3 correctness, PENDING/Resources. Canonical `s39-h200-eagle3-correctness`, 16 H200/two nodes/max 17 minutes, no PBS SU. Require all 1600 actual IDs equal accepted H200 reference 25585, native speculative counters, both semantic P/D receipts, all-rank BF16/graph/source and 32 geometry records. No candidate output or score exists yet. [Frozen design and definite receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-h200-candidate-20261023/RESULTS.md).
- **25712 → 25713**, matched target-only graph-policy short pair, dependency-pending. Control follows afterany:25682; treatment afterok:25712. Each 16 H200/two nodes/max 17 minutes/no PBS SU. Common explicit BF16, prefill 64/decode 256 capacities, DeepGEMM 8192/HPC-Ops, MNNVL, FlashInfer, native NIXL and decode graphs 1–64. Auto means omit the unsupported literal auto flag; native role-specific resolution is checked. Require initialized capacity, all-rank graph/KV, semantic P/D, exact 20/40/30 client protocol, raw SLA and short/long response gates. No result yet. A valid short gain ≥ 1% permits considering full confirmation; otherwise close this standalone policy unchanged. [Receipts, controls and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-prefill-graph-policy-20261023/RESULTS.md).

Preserve these positions and frozen payloads. The H200 target-only reference 25585 is accepted: all 1600 real IDs/four repeated pairs, actual 4+4+8 BF16 logs, asset binding and both semantic P/D paths; 458 s. Earlier 25495 failed solely before token-client launch because role HOME was absent; preserve that failure. [Accepted reference](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25585-20261023/REVIEW.md).

## H100: repair running after an isolated shell failure

**224157.pbs111**, submitted 15:49 UTC, last PBS state R on 037/039, two H100/max ten minutes. This separately frozen nonlogin batch/node repair explicitly bootstraps required modules and retains the exact native transfer program, strict errors, full-span byte gates and independent Python/container/node/batch exits. Require terminal PBS exit 0 and all semantic/process gates; no pass exists at this snapshot. [Definite receipt and plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-nonlogin-exitfix-20261023/RESULTS.md).

Prior **224155 is F / exit 1**, 262 s / posted 18.631 SU. Actual native bytes pass; both Python children, containers and temporary deletion return 0, but node shells return 1. Eight remote CPU cases isolate login shell  + errexit  + console-cleanup logout; all other combinations pass. User startup/logout files were not edited. The repair changes launcher environment setup instead of suppressing errors. **224116 also remains F / exit 1** with passing full-span byte proof; posted 16.284 SU. [Exact boundary evidence and CPU reproducer](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-224155-20261023/REVIEW.md).

The bounded byte proof covers 190×76,132,096-byte KV spans per rank, 380 selected pages / 97,280 transferred bytes, 14,465,000,960 untouched destination bytes scanned on GPU, source preservation and ten whole auxiliary buffers / 933,888 bytes. Registered capacity differs from transferred payload. It does not certify full TP serving, model outputs or production auxiliary request rows.

The earlier full **223055** actually fails at native NIXL remote disconnect with HTTP 500 and zero diagnostic outputs; its warmup success marker was false. The shell repair does not explain or fix that separate serving failure. **223788** records four real full-sized native registrations but fails its original unsupported nonempty-layer-ID gate. A restricted candidate-local empty-list exception is source-backed; do not change the failed job or invent semantic layer IDs. [Full integration failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-eager-prefill-r3-20261021/REVIEW.md), [geometry correction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-223788-20261023/REVIEW.md).

The [auxiliary-row source review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-aux-layout-review-20261023/REPORT.md) distinguishes whole spans from request-slot transfer. P cap 48 independently gives 96 metadata rows. D allocates 2×its request-pool size; logged D serving cap 256 alone does not prove that pool size. Actual D row count/widths and hidden-state tensor layout remain uncollected. Source-shaped CPU bounds are conditional, not runtime proof.

## Access and AI budget

AI SSH reaches `a2ap-login01` through the healthy shared VPN, reauthenticated 15:27 UTC with the previously supplied credential. This worker did not restart VPN or perform a fresh DUO step; preserve the healthy shared session and private recovery state. A server notice says the account password expires in three days; this is unrelated to VPN lifetime and no password change was attempted. [Dated access history](vpn-access-20261023.md).

Latest locked ledger 15:42 UTC: **Used 46484.545 SU / Balance 17515.455 SU / In Doubt 0**; 224155's 18.631-SU charge is uniquely posted. New 224157 reserves at most **42.666667 SU**, leaving internal headroom **4472.788333 SU** under unchanged **51000 cap / 13000 reserve**. Retain that maximum until terminal unique posting. Balance already includes any prepayment; do not subtract it twice. [AI ledger](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json). AI project 59010042 is distinct from the HPC CPU project; do not modify the latter.

## Next decisions and operating rules

1. Review 224157 terminal raw byte/exit receipts, PBS accounting, phase memory/RSS and actual charge. A failure needs a supported new diagnosis, not an unchanged retry. Preserve every old failed result.
2. Review 25682 before any EAGLE load screen. Correctness alone is not speedup; any later performance pair must match dtype, capacities, graph policy, observers and workload.
3. Review 25712/25713 as short controls, including raw tails/errors, role queues/running/KV, available hardware samples and source identity. If control fails, inspect/cancel its held candidate appropriately. Close unchanged losing branches without globally stopping research.
4. A further full H100 repair must collect actual P/D metadata counts/row layout and semantic warmup before all 1600 IDs against accepted H100 reference 222761. Do not substitute H200 outputs or assume the shell fix resolves native transport. Prepare and review before any spend.

Maximum five own active/pending Slurm jobs and actual 17-minute limit; PBS max three own pending/active and one running allocation. Review fresh queue and selected credit under the AI lock before spending. No blind queue filling, cap increases, background Codex, autopilot, schedules or automatic chat notifications. Existing scheduler jobs may continue.

Edit active sources once; capture explicit safe milestones to the Git archive, screen, verify, commit actual dates and push promptly with reviewed paths and locks. Git excludes credentials/private session state/models/runtime caches; external large objects still need separate off-host backup. [Archive/recovery](../reports/github-publication-20261019/REPORT.md).

The packaged AI primary remains N62 until separately reviewed promotion; AI slide content last changed 22 October. The separate HPC worker rebuilt the combined delivery 23 October. Do not modify its HPC_Task or CPU results. [AI presentation](presentation-update-20261022.md), [combined delivery](../submission-review/hpc-update-20261023/README.md).
