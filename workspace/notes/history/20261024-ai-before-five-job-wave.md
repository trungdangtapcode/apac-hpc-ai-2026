# Current AI / Qwen handoff

Updated 2026-10-24T03:46:31.894588+00:00. GPU fork `01a166eb-33cb-7ce0-9699-ec65de26689a`, parent `01a15dd3-3094-7712-a991-8ce55b15cbfe`. This worker owns AI/Qwen; the other worker owns HPC/OpenFOAM. Snapshots below are dated: query actual schedulers before claiming live status. English artifacts, Vietnamese chat. Background Codex and schedules remain disabled.

## Owner-approved H100 budget

On **24 October**, the owner explicitly authorised using remaining H100 SU freely and reported a **30 October usable deadline**. The previous internal **51,000 SU ceiling / 13,000 SU buffer is superseded**. AI project **59010042** can use its actual **64,000 SU grant**, with **zero discretionary reserve**. The selected account report lists 15 November; plan against the earlier owner-supplied date without presenting it as a verified account-expiration fact. CPU project/budget and concurrency caps are unchanged. [Decision and direct account report](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-budget-owner-update-20261024/README.md).

At the locked **03:36 UTC** admission, used = **46,528.065 SU**, published balance = **17,343.935 SU**, In Doubt = **128 SU**. The 9.387 SU charge for 224275 is reconciled. Keep maxima **128 SU for terminal 224276**, **1024 SU for 224277**, and **21.333333 SU for 224278** until unique posting. Conservative remaining allowance after these maxima is **16,298.601667 SU**. Balance already excludes prepayment; do not subtract In Doubt twice. [Canonical ledger](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json).

New controllers must use this policy. Old frozen helpers assert 51000/13000: preserve them as evidence and derive a new controller rather than reusing or editing a submitted payload. Admission still needs CPU-before-AI locks, fresh queues and credit, maximum reservation and immediate receipts. Combined own PBS cap **3**, one running AI allocation, at most **16 GPUs / 45 minutes** per job. Slurm cap **5 own jobs / 17 minutes** per job.

## Queue checkpoint — 24 October 03:40 UTC

| Job | State at check | Purpose |
|---|---|---|
| H200 **25807** | R on g1/g4; still R at 03:44 | S44 deterministic target reference, 16 GPUs / 17 min, no PBS SU |
| H100 **224277.pbs111** | Q / aiq2 | R5 full EAGLE metadata/transport/output diagnostic, 16 GPUs / 30 min / max 1024 SU |
| H100 **224278.pbs111** | H, afterany 224277 | Native expert-replica primitive, 1 GPU / 10 min / max 21.333333 SU |

25807 qualifies two stable target passes with **1600 actual IDs** under new deterministic settings. Old 25585 equality is informational. It requires actual rank/BF16/graph/source/188-region target KV checks and both semantic P/D paths. S45 is an **unbound, unsubmitted template**: only bind/freeze it after reviewing the actual S44 reference, result hash, review hash/seal and job ID. [Protocol and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-h200-determinism-20261024/REPORT.md).

224277's afterok 224276 condition cleared after the real prefill observer pass. It independently checks the accepted parent receipt before loading models, then requires all 16 actual metadata records, native send observations, both semantic paths and 1600 IDs versus H100 reference 222761. A returned transfer handle is not completion. [Frozen R5 and receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-observed-r5-20261024/README.md).

224278 tests synthetic **128 logical / 130 physical experts**, two exact replicas and five sequential virtual partitions of 26 experts on one H100. It compares native output against a native 128-expert control and an independent oracle. It does **not** test five-GPU communication, DP attention, framework EPLB, model accuracy or serving speed. It may run after either R5 outcome. [Source and exact receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/hpc-ops-replica-primitive-20261024/README.md).

## Completed results and decisions

| Run | Observation | Decision and limits |
|---|---|---|
| **25796**, one H200 | Kernel pass, exit0, 38 s; four FP8-KV cases; max same-rounded-cache relative-L2 **0.315902%** | Kernel compatibility only. No Qwen, transport, calibrated scales or performance proof. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25796-20261024/README.md) |
| **25797**, 16 H200 | Failed exact-token gate, exit1, 494 s; all ranks / 32 geometry records / both P/D paths pass; 1600 real IDs | Arithmetic matches reference; code/Unicode differ but repeat internally; long4000 also differs between repetitions. Preserve failure. No speculative score. [Review and bounded telemetry inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25797-20261024/README.md) |
| **224276**, four H100 | Prefill observer pass, exit0 / stageout1, 359 s; independent checker replay passes | Four real rank records: ten tensors with 96 rows, BF16 hidden states [96,4096], 8192 bytes/row. No decoder/remote transfer/output check. Shutdown child state incomplete; retain raw warnings. Estimate 51.057778 SU remains unposted. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-224276-20261024/README.md) |
| **25712 / 25713** | Auto **2826.264836**, disabled **2809.862095 good output tokens/s**; disabled −0.580368% | Both pass local SLA in short 20/40/30 screens. Close unchanged disabled-policy performance branch; fixed order and different server seeds limit inference. [Decision](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25712-25713-20261023/README.md) |

Earlier **25750** proves worker draft-byte portability but fails the old metadata gate; S43 narrowly preserves unknown decoder heads rather than inventing them. **224275** fails before model loading on our CUDA API typo; R2 changes only that call and passes. Full R4 was uploaded but never reserved/submitted because the parent-failure admission gate stopped it. Earlier 224157 passes native whole-span bytes and process exits but does not explain 223055's full NIXL disconnect. [Detailed chronological handoff](history/20261024-ai-output-and-credit-detailed-handoff.md).

## Interpretation and next hypotheses

The organiser compares full benchmark scores, **not token-by-token outputs**; the pass line is ≥99% of its own unchanged FP8 reference. Local 25797 failure is not official disqualification, and tiny output tests do not prove official quality. Do not retrospectively weaken its gate. The fresh deterministic pair asks a different, prospective question with a matched target reference. Native deterministic mode changes sampling, attention/collectives and disables MNNVL; it has no proven deterministic branch in Qwen3-MoE/HPC-Ops/EAGLE. A passing diagnostic would not establish a competitive speedup.

The new DP/EP lead is source-qualified only: TP5/DP5 gives effective attention TP1; adding two physical copies makes 130 experts divisible by EP5. Actual model config confirms 128 experts, 8 selected, 4 KV heads and dynamic FP8 E4M3 128×128 blocks. P12/D4 with matched attention TP4 is another candidate. Rank placement, backend resolution, expert dispatch, native P/D DP-rank mapping and model memory remain unproved. [Pinned source and next tests](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/dp-attention-ep-feasibility-20261024/README.md).

Team01's dated public accounting contains 370 retained allocation records versus our 175, not a score comparison; PBS is excluded. Do not infer their private flags or a measured performance gap from labels. [Public evidence and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/public-scheduler-review-20261023/README.md).

## Frontier and preservation

The reproduced H200 N64 choice remains **3044.400475 good output tokens/s** (25366/25373/25487); the H100 N54 result remains **2433.019859** (222048), separately ranked. H200 N68's single 3047.165853 misses the 1% confirmation gate. Official full-set accuracy remains unverified. The packaged primary is still N62 pending a separately reviewed promotion; no submission or HPC presentation payload changed this turn.

[Beginner journey](../reports/ai-research-learning-journey-20261023/README.md), [new reasoning entry](../reports/research-journey-20261019/journal/entries/20261024-fp8-output-and-credit.md), [complete journal](../reports/research-journey-20261019/journal/README.md). Preserve raw failures, review beyond scores and mark missing telemetry. Capture explicit safe milestones, verify hashes, commit actual dates and push small checkpoints. External large corpus objects still need separate off-host storage; Git contains their manifests. Healthy shared VPN/SSH remain in use. Do not reset private state or enable background Codex/schedules.
