# APAC Qwen execution policy

Updated 2026-10-20T17:29:26.672121+00:00. This compact policy supersedes old execution snapshots, preserved in [the historical policy](../notes/history/20261020T172926Z-before-compact-POLICY.md). The owner instructions in AGENTS.md remain authoritative.

## Read and preserve context

Read notes/README.md, notes/CURRENT.md and the relevant plan before work. Treat scheduler/budget snapshots as dated; query actual state when needed. Use concise Vietnamese for chat and English for all new work artifacts. Qwen track only; keep HPC_Task empty. Do not edit frozen submitted payloads or unrelated submission materials.

Record each reviewable milestone in the linked research journal: question, prior evidence, hypothesis, control/change, exact job/bundle IDs, observations with units, assessment/limits, correction and next decision. Preserve raw failures and losing branches. Do not invent historical reasoning or measurements. Do not repeatedly audit unchanged sealed runs without a new concern.

## Authorised active research loop

During authorised work, review completed results, inspect beyond the score, identify a distinct justified hypothesis, check queue capacity and budget, then submit the feasible followup. A status request is also a continuation checkpoint. Closing a losing branch is not a global stop. Do not fill queues with blind duplicates or revive unchanged losses. A prepared plan is not a submission receipt.

**Codex autopilot remains disabled at the owner's request of 16 October, 13:42:29 UTC.** No background Codex, replacement schedules or automatic chat-notification promises. Existing GPU jobs, the non-AI Slurm watcher and VPN may remain running. Scheduled sessions would use file handoff, not this chat's context. Do not spawn subagents without explicit applicable authorisation.

GPU computation belongs on allocated compute nodes. CPU staging uses at most four threads. Preserve Priority-pending positions; do not cancel merely to requeue. At most **five own active/pending H200 jobs**, counting watcher and untracked jobs; do not duplicate the watcher. At most **three active/pending PBS jobs** with verified serial dependencies and **one running own 16-GPU PBS allocation**.

## PBS budget and submission safety

Project grant 64000 SU; rate 128 SU per GPU-hour. The existing internal cap is **51000 SU**, retaining **13000 SU** project buffer. Do not increase it implicitly. Use nscc-budget.json and its budget lock; check the fresh published ledger, own job states and outstanding maxima before qsub. Balance already excludes In Doubt prepayment; never subtract it twice. Reserve maximum charge first, record each definite ID immediately and retain uncertain outcomes until resolved. Never blindly repeat an uncertain qsub.

Latest completed H100 pair: 222551/222552, full local gates and actual mappings PASS but only +0.289035% goodput, below the prospective 1% gate. Close without an unchanged repeat or default promotion. At the locked 21 October 03:21:52 UTC reconciliation: Used 43571.410 SU, Balance 20428.590 SU, In Doubt zero, no outstanding maxima and internal headroom 7428.590 SU. Refresh before spending; these are dated values.

222721 is terminal exit 1: the native gateway filters chat token-ID extensions, before tensor checks. Derived 222722 is submitted for /generate+logprob forwarding and unchanged tensor/config checks, one H100 / four minutes / maximum 8.533334 SU. Retain both maxima until posted reconciliation; conservative headroom is 7411.523333 SU at reservation. No target inference or ranked score. Review actual terminal evidence and refresh credit before further spending. A component PASS does not waive real draft loading, both-phase PD transfer or exact greedy equality. Current H200 positions remain 24928/24962/24964/24965/25051, all pending at the latest check; no sixth job. No budget increase.

## Measurement and acceptance

Preserve the official published FP8 target, model architecture/experts/layers, plain PD split, all 16 GPUs and gateway. BF16 KV is allowed; replacing target weights with BF16 or colocated replicas is a different deployment. Keep the locked AIPerf command: closed-loop team concurrency, 4000 input / 200 output tokens, seed 2026, cold prefixes, full 60-second warmup / 120-second measurement / 30-second grace.

Rank by exported AIPerf goodput × 200 good output tokens/s. Require joint TTFT ≤ 3000 ms and request-mean ITL ≤ 20 ms, qualifying fraction ≥ 0.90 including errors. Final local candidate gates also require zero errors/cancellations, valid runtime/protocol, short/long output checks and exact payload/source provenance. Tiny output checks do not establish organiser accuracy at 99% of reference; that gate remains unverified.

Keep H100 and H200 series separate. A single peak is not a reproduced gain, a micro/short diagnostic is not a ranked score and startup savings are not serving throughput. Use fresh matched controls and independent confirmation only when justified. Follow each experiment's prospective stopping gates; never weaken them after seeing results.

For terminal runs inspect raw tail latency, errors and concurrency; role-specific queue/batch/inflight/KV state; runtime/transport logs; available CPU/GPU diagnostics; and cost. Explicitly mark missing or uninspected telemetry. GPU activity, VRAM allocation, KV occupancy and summed kernel times are different quantities. Keep heavy profiles after scoring and preserve known profile-stop HTTP 500 failures. The observability report linked from CURRENT defines actual rollout and limits.

## Current branch decisions

Keep native NUMA binding. H100 222435 shows actual scheduler locality with an asymmetric outer CPU envelope, not measured CPU saturation. The completed pair verifies the intended same-budget change but misses its 1% gain gate; keep the previous default and close this exact policy.

Close unchanged reverse startup-prefetch confirmation: 9.836066% walltime/SU saving misses its prospective 10% gate. Do not automatically repeat or promote it. Keep H100 chunk 4096 and round-robin; unchanged 2048/8192/power-of-two trials lost. Historical DP8/DeepEP did not beat its contemporary MNNVL control.

EAGLE3 remains a prepared correctness branch. Public draft bytes/digest are staged outside Git. Native token-ID support is inspected, but gateway forwarding and real draft loading/PD integration remain unverified. First establish target-only repeat stability and exact actual token IDs, then correct draft loading/state/transport/kernels/memory and long-context checks. Only a useful valid short screen merits full scoring. No full-model speculative GPU job exists yet; do not weaken target verification or infer speedup from acceptance length.

## Access, backup and handoff

Use existing VPN/SSH without exposing or capturing authentication/session material. Do not restart or trigger DUO without current explicit authorisation. No passwords, OTPs, private VPN caches, tokens, model weights or disposable caches in notes, Git or research object storage.

Edit active sources once in 2026-APAC-HPC-AI or workspace. The sibling apac-hpc-ai-research repository is an explicit archive, not a third development tree. At each small coherent checkpoint, capture only relevant safe paths, scan, verify, review staged paths, commit with a descriptive conventional subject and actual date, push to the existing private origin and verify live origin/main equals HEAD. Do not accumulate unrelated milestones or create empty commits. Preserve original provenance/history; never rerun the initial snapshot builder over the existing repo.

Retain external-object manifests and hashes. A Git push does not upload sibling artifact bytes; they still need separate off-host backup. End each work turn with a safe checkpoint or name exactly what remains uncaptured/unpushed. Keep CURRENT under 120 lines and POLICY under 100, with historical material linked separately. No automatic sync or background AI service is enabled.
