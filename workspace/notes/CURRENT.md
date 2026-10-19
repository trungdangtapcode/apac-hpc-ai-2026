# Current APAC handoff — 19 October 2026

Updated 2026-10-19T18:00:11.710346+00:00. PBS states are from the actual post-submit check below; H200 states were checked at 17:55 UTC.

## Queued work

PBS **221923 → 221924 → 221966** is verified, states **Q/H/H**: explicit-default control, decode-only inference-mode candidate, prefill-only inference-mode candidate. Control is waiting for exclusive nodes currently in use; followers wait on afterany dependencies. No new measurements exist. All retain fixed N54 scoring and separate CPU/GPU post-score profiles. Each candidate must be compared with 221923; do not assume independent phase gains combine. Actual DynamicGradMode source/context, runtime, payload, latency/error and output checks are required. [Plan and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-prefill-inference/RESULTS.md). Three active PBS jobs, at most one running 16-GPU allocation; no fourth job.

H200 **24733/24736/24737/24738/24819** remain Priority-pending; preserve all five positions. Highest individual observations remain **H200 24724 = 2938.628** and **H100 221590 = 2430.891 good output tokens/s**. The H200 interaction's own repeat has not run. Keep platforms separate. Official full-set accuracy at 99% reference remains unverified.

## Latest evidence and correction

H100 221884/221885/221886 passed full local gates at **2415.474/2421.066/2425.886** good tokens/s; no useful gain or new peak. Attention 221880 passed but scored **2227.031**, a **−7.74%** regression, and that branch is closed. [Results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1720/RESULTS.md). CPU/GPU sums and synchronisation waits are not causal bottleneck fractions.

**Corrected:** LL-labelled NCCL kernels are representatives, not reliable protocol identifiers. Existing sealed TUNING logs demonstrate Simple selected in 221885. Control 221884 already selects Simple for larger 18–32 MiB operations; its observed LL decisions are 4-byte operations. The single +0.2315% result remains unestablished. Keep automatic protocol policy and close forced-Simple on performance evidence. Older name-count booleans/activation doubts are historical and superseded. [Sources, counts and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1755/CORRECTION.md). No GPU rerun was needed to resolve the names.

## Credit and workflow

Published Used **32604.728 SU**, Balance **31395.272 SU**, In Doubt **0**; the latest publication time is recorded in nscc-budget.json. No newly published charge. Total maximum outstanding reserve **4608 SU**, internal headroom **13787.272 SU** under unchanged **51000-SU cap** and **13000-SU project buffer**. Bounds are not actual charges. Four preceding terminal charges were reconciled before reservations. Existing VPN/SSH works; no reauthentication or restart.

During active authorised work, review completions and submit the next distinct justified hypothesis when budget/slots permit. Do not interpret a losing branch as a global research stop. No blind duplicates, unchanged losses or automatic load growth. Capture, verify, commit and push small coherent milestones promptly; large external evidence still needs separate off-host backup.

Chat Vietnamese; new work artifacts English. Qwen only, HPC_Task empty. No slide/package promotion. Autopilot OFF: no background Codex, schedules or automatic chat notifications. Older scheduler snapshots are historical.
