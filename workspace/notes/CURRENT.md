# Current APAC handoff — 19 October 2026

## Frequent commit and push rule — 2026-10-19T13:38:30.266691+00:00

The user requires small, coherent backup checkpoints rather than large batches. Commit and push each safe, reviewable unit as it is completed: hypothesis/scripts/config; submission receipts with reservation updates; one completed-run review; a fix; or docs. Do not wait for GPU completion or a whole experiment wave, and do not sweep unrelated staged changes together. Keep dependent files reproducible, exclude secrets, verify capture and origin/main, and disclose exact uncaptured/unpushed work if interrupted. No artificial commit count, new history rewrite, background sync, schedule or GPU allocation is authorised by this rule. Persisted in home and archive AGENTS.md and archive docs/GITHUB_WORKFLOW.md. Existing research snapshots below retain their original timestamps.


## Continue research and submitted batch — 2026-10-19T12:02:20.997548+00:00

The user explicitly corrected idle research: during active authorised work, review results, research the next distinct hypothesis and submit when capacity/budget permit without another reminder. Losing N56 or Tree is not a global stop. Actual new jobs: PBS **221827 → 221828 → 221829** (N54 fresh control/profile, HPC-Ops chunk6144, prefill Simple protocol/profile); H200 **24819** (N58 winning interaction repeat/profile), preserving four older queued jobs. Five active H200 jobs and three serial PBS jobs. New PBS maximum reserve 4608 SU; pre-submit Balance 34608.356, Used 29391.644, In Doubt zero; internal headroom 17000.356 SU under unchanged cap/buffer. New jobs have no measurements yet. Full plan, references, hashes and receipts: [research continuation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1200/RESULTS.md). Review each completion and continue justified work. No blind duplicates, unchanged loss retries, automatic load growth, AI schedules or background Codex. Highest observations/accuracy limits unchanged.

## Current observations and acceptance limits

Best accepted H200 observation is 24724 = 2938.628 good tokens/s, still awaiting its own interaction repeat. Auto-decode N60 has independent measurements 24722 = 2839.532 and 24732 = 2836.531; those do not repeat the HPC-Ops-decode interaction. Highest H100 individual observation is 221590 = 2430.891; N54 repeat 221645 = 2418.588. N56 221646 = 2407.364 has no observed gain; forced prefill Tree 221669 = 2160.946 loses 10.65%, with actual Tree execution proved on all eight prefill ranks. Keep that branch closed. All are platform-specific local research measurements; official accuracy at 99% reference remains unverified.

[Completed H100 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1111/RESULTS.md). [Illustrated research journey](../reports/research-journey-20261019/diagram/README.md) retains its 06:14 UTC cutoff and is historical. [Last status-only snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1144/RESULTS.md) is superseded by the submitted batch above. Earlier handoffs are in notes/archive and Git.

## Standing workflow

Vietnamese chat only; all new work artifacts in readable English. Qwen only; keep HPC_Task empty. Preserve raw failures and corrected interpretations. No slide, official script promotion or organiser upload without relevant authorisation. Keep queue bounds: at most five active H200 jobs, three active PBS jobs and one running PBS 16-GPU allocation.

Codex autopilot stays OFF. No background Codex, replacement schedules or automatic chat notifications. No background Slurm watcher is running; this batch was submitted explicitly under locks.

Work once in `/home/apacsc42/2026-APAC-HPC-AI` and `/home/apacsc42/workspace`. Capture completed milestones into `/home/apacsc42/apac-hpc-ai-research` with sibling artifact store, scan/verify and commit. AGENTS.md records this manual workflow; no automatic mirror. GitHub publication is now authorised and the private remote stores Git. The sibling artifact store still has no configured off-host copy, so the GitHub clone is not complete evidence/runtime recovery. Historical handoff snapshots are in notes/archive and Git; they are not live scheduler state.

## Prepared next hypothesis

The exact retained runtime supports phase-specific FlashInfer prefill; standby h100-hpc-prefill-flashinfer-n54-45 is frozen locally, not submitted or reserved. Review fresh control 221827 and live queue/credit, then select a serial dependency and submit if it remains justified when a PBS slot frees. Read [next research and source evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1200/NEXT_RESEARCH.md). Actual kernel and output checks remain necessary. NVLS needs a support-first probe; no full-model sweep or official-accuracy claim is prepared blindly.
