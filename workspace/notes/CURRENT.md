# Current APAC handoff — 19 October 2026

## Latest research checkpoint — 2026-10-19T14:37:21.593278+00:00

The H100 matched batch is fully reviewed: control 221827 = **2413.802**, chunk6144 221828 = **2411.995** (−0.0749%), and scoped-protocol setting 221829 = **2414.548** (+0.0309%) good output tokens/s. All local protocol/SLA/runtime/output gates pass. No useful gain is established. Simple activation is unverified: separate N48 traces show Ring LL and no named Simple all-reduce kernel. The chunk reviewer was corrected to validate graph buckets derived from the chunk using the hashed runtime generator; initial and corrected reviews are preserved. [Results and raw evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1418/RESULTS.md).

## Current jobs, checked 14:30 UTC

PBS serial chain **221880 → 221884 → 221885**: dense FlashInfer-prefill N54 running at the check; fresh instrumented default-protocol control and global prefill Simple candidate dependency-held. The latter pair holds instrumentation identical, keeps automatic algorithm selection and must prove actual kernel/communicator execution. Their profile is separate from ranked traffic. [Plan, receipts and budget](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-protocol-check/RESULTS.md). Three active PBS jobs, at most one running 16-GPU allocation.

H200 jobs **24733/24736/24737/24738/24819** were still pending Priority at 14:18 UTC; preserve positions and the five-job cap. Best individual observations remain **H200 24724 = 2938.628** and **H100 221590 = 2430.891 good tokens/s**. The H200 interaction's own repeat has not run; do not confuse the separate auto-decode N60 repeat with it. Official full-set accuracy at 99% reference remains unverified.

## Credit

Published ledger 19/10/2026-22:20:02 SGT: Used **30729.102 SU**, Balance **33270.898 SU**, In Doubt **0.000**. Three terminal charges **1337.458 SU** reconciled; old 4608-SU reservations released only after Used matched. New total maximum reserve **4608 SU**, internal headroom **15662.898 SU** under the unchanged 51000-SU cap and 13000-SU buffer. Balance already excludes published prepayment; do not deduct it twice. Existing VPN/SSH works without authentication or restart.

## Continue without another reminder

During active authorised work, each completion or status request triggers review, research and the next justified submission when a slot and budget permit. A losing branch is not a global research stop. Keep Tree, unchanged scoped-protocol and unpromising chunk repeats closed. Do not fill queues with blind duplicates or automatically increase load. Resolve global protocol activation before further full-model protocol sweeps; target demonstrated decode/MoE/host costs next. Existing profiles capture GPU only and cannot establish CPU critical-path costs by themselves.

Commit/push small coherent checkpoints as work becomes reviewable: preparation, receipts/budget, review, fix and docs. Do not wait for a whole wave or bundle unrelated code. Active sources remain /home/apacsc42/2026-APAC-HPC-AI and /home/apacsc42/workspace; capture only relevant safe changes into the private Git archive, verify and push, preserving raw failures and external manifests. GitHub alone does not contain the sibling large-object store.

Vietnamese chat only; all new work artifacts English. Qwen only, HPC_Task empty. No slide or official-package promotion without relevant authorisation. Codex autopilot stays OFF: no background Codex, schedules or automatic chat-notification promise. Historical snapshots are in notes/archive and Git; read their timestamps.
