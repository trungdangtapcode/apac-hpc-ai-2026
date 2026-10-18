# Current APAC handoff — 18 October 2026, 19:25 UTC

## Standing instructions

Vietnamese chat only. All work artifacts in readable English. Qwen only; keep HPC_Task empty. Preserve failed runs, raw artifacts and corrected interpretations. No organiser upload or official script promotion. Update slides when requested.

Review each completed job, refine the hypothesis and submit the next justified experiment without waiting for unrelated pending jobs. Research, runtime/output evidence and cost must guide every trial. Close losing branches; no unchanged retries for backend/output failure. Preserve queue positions. Respect five active H200 jobs and three PBS jobs, with one 16-GPU PBS allocation at a time.

Codex autopilot remains OFF. No replacement schedules or background Codex. The old non-AI Slurm watcher exited after its prior wave. Its submission function has been invoked once per manual batch under its lock; no background watcher is running. Do not promise automatic chat notifications.

## Latest failure and live queue — supersedes older queue snapshots

Latest report: [19:25 UTC](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1923/RESULTS.md). **24588 TIMEOUT, no accepted measurement**: sent 858 warmup requests, 857 raw warmup records, zero scored records. One completion remained outstanding through warmup's infinite drain. Workers loaded normally; health responses do not establish stream completion. Shutdown connection refusals are consequences, not the isolated root cause.

**24647** is one bounded diagnostic retry: same serving/scoring configuration, whole-AIPerf limit 360 seconds plus 15-second forced-stop fallback. No per-request filtering, phase shortening or precision changes. This is containment, not a proven repair. Passing still requires all full normal protocol/runtime/output gates. An abort is a failed attempt. If the stall repeats, stop this retry path; no unchanged repeat or automatic walltime extension. Exact inverse guard patch and frozen hashes validated. No background watcher is running; do not enable generic auto-retries on this candidate.

At 19:24 UTC queue **24589/24639/24640/24641/24647** is pending Resources: five active, no sixth. 24588's previous pending status below is historical. H100 still fails before SSH because VPN is not live; no new PBS results/credit verified. Preserve auth cache and conservative reservations; no DUO request triggered. A user-input question is pending about whether someone is available to approve DUO for restoring H100 access. Do not initiate authentication while that availability is unknown.

## Latest H200 reviews and next hypotheses

Latest full report: [18:46 UTC](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1845/RESULTS.md). Frozen reviewers, raw artifacts, hashes, controls and scheduler receipts are retained beside it.

- **24573:** DeepGEMM prefill chunk 6144 N56 independent repeat, **2,737.410 good tokens/s**, **+0.8590%** versus fresh control 24575. Original 24528 was 2737.011 (+0.7798% versus its control). Descriptive mean 2737.210. Joint SLA 98.9437%, TTFT 717.263 ms, ITL 16.472 ms.
- **24574:** HPC-Ops prefill chunk 4096 N56 independent repeat, **2,728.962**, **+0.5477%** versus fresh control. Original 24529 was 2732.459 (+0.6122%). Descriptive mean 2730.711. Joint SLA 98.8249%, TTFT 714.981 ms, ITL 16.536 ms. Decode unchanged.
- **24575:** fresh confirmed DeepGEMM prefill chunk 4096 N56 control, **2,714.097**, near prior controls 2715–2717. All three pass full terminal seal, frozen payload, 60/120/30 protocol, resolved runtime, joint latency/error and short/12-long gates. Native FP8 checkpoint and BF16 KV retained; speculative decoding off. Official full-set accuracy at 99% of reference evaluation score remains unverified.
- **Highest observation still 24544: 2,786.696**, DeepGEMM chunk 8192 N58, +2.5244% versus historical same-load chunk 4096 control 24352. Independent repeat 24588 timed out before scoring; guarded attempt 24647 and fresh control 24589 are pending; do not promote a historical comparison as a confirmed chunk gain.
- **24538:** DeepGEMM prefill + HPC-Ops decode N56, 2733.199 (+0.6395% versus 24526), mean ITL 14.858 ms, higher TTFT 1037.104 ms. Passing actual GPU/runtime/output evidence motivates the newly submitted N58 load trial.

## Previous Slurm submission record (superseded above)

At 18:46 UTC all five own jobs are pending Resources, each 16 H200 / 17 minutes:

| Job | Trial and comparison |
|---|---|
|24588|Existing DeepGEMM chunk 8192 N58 repeat of 24544|
|24589|Existing fresh DeepGEMM chunk 4096 N58 control|
|24639|New DeepGEMM prefill chunk 4096 + HPC-Ops decode N58; compare same-load 24589 and source 24538|
|24640|New HPC-Ops prefill chunk 6144 N56, auto decode; compare 24574 for chunk and 24573 for runner|
|24641|New HPC-Ops prefill+decode chunk 4096 N56; compare 24574 for decode and 24538 for prefill|

No sixth job; preserve positions. Independent improvements do not guarantee additive combination gains. Require full local gates for every combination, repeat useful gains before promotion, and close losing/backend/output-failing branches without unchanged retries. No automatic N60. H100 chunk 8192, graph-off branches and invalid equal-TP8/EP2 job 24375 stay closed/quarantined. CPU geometry tests are not model correctness evidence; see nixl-equal-ondemand/VALIDATION_STATUS.md.

## H100 access and historical verified results

At 18:44 UTC SSH wrapper still fails before SSH: no matching live rootless VPN process. Last sanitised log finding is IKE SA expired 18 October 14:08:45 UTC, about 24 hours after documented restoration. This timing is consistent with configured lifetime 86,400 seconds, not proof of server policy or cache validity. tmux presence is not a live tunnel. Authentication cache is preserved; no restart, reauthentication or DUO request this turn. Do not claim remote PBS outcomes, queue or credit without live access. Local VPN loss does not itself cancel PBS allocations.

Last validated H100 peak remains **221315: 2, 371.961 good tokens/s**, HPC-Ops prefill+decode N50, chunk 4096, prefetch matched. Independent 221339 repeat **2371.341**; descriptive mean 2371.651. Original/repeat gains 2.7277%/2.7009% versus preceding decode-only control 221314 at 2308.979. Mean TTFT around 486–493 ms versus 669 ms; ITL around 18.2 ms versus 17.83 ms. All local checks pass. Later decode-only control 221340, both-phase N52 candidate 221341 and score/profile 221346 are unreviewed because remote access is unavailable. Do not describe them as still running or finished based only on the old snapshot.

Historical budget as of 18 October 21:40:01 SGT: Used 25,846.898 SU, Balance 36,617.102 SU, In Doubt 1,536 SU. These are not current credit. Conservative outstanding reservations for 221340/221341/221346 total 4,608 SU; retain until actual accounting reconciles. Historical headroom 20,545.102 SU under internal 51,000 SU cap. The 13,000 SU buffer is internal planning, not BTC quota. Do not deduct prepayment twice. No new qsub or budget reconciliation without fresh scheduler/credit under budget.lock; never retry uncertain submissions.

## Reports and profile limits

- Full metric definitions, units and source-linked cards: workspace/reports/all-history-metric-records-20261017/REPORT.md. Peak holders unchanged this turn; current repeat evidence is in the latest review. Last 32-slide presentation remains a historical snapshot; no slide/package changes.
- Cross-platform frozen report: workspace/reports/cross-platform-20261017/REPORT.md. Old ratio 1.188096805 and local N50 error −1.5371% do not convert gains for new backends. Measure on each GPU platform.
- H200 profile 24429 legacy ~0.8% MoE estimate undercounted renamed grouped kernels. Corrected prefill shares 34.81%/34.83%; old 42.84%/42.77%. See research-followup-20261018-0800/profile-comparison.json.
- H100 decode-HPC profile 221284 is valid: 16 nonzero ranks, 371/371 successful separate requests. Prefill fused MoE still about 42%; decode contains HPC group GEMM, activation/reduction, attention and collectives. See research-followup-20261018-1215/hpc-profile-kernels.json. Both-phase profile 221346 must be collected and classified by actual names after access is restored.
- Kernel shares describe summed durations, not wall time, causal gains or speed predictions; batch shapes need not match. Initial-burst TTFT analysis in research-followup-20261017-1830/RESULTS.md does not justify removing requests or phase-aware benchmark changes.
- VPN helper: workspace/vpn-rootless/vpn.sh ssh-batch. Never record credentials/session material or mistake VPN process loss for an SSH password failure.
