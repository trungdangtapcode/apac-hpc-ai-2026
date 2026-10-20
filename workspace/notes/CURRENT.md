# Current APAC handoff — 20 October 2026

Updated 2026-10-20T00:52:58.267867+00:00. Scheduler snapshots below were checked at 00:51 UTC; ledger publication has its own timestamp. Read live state before claiming a later queue status.

## Accepted local observations

**H200 highest individual: 24738 = 2990.151 good output tokens/s at N60**, DeepGEMM prefill chunk8192 + HPC-Ops decode. This N60 treatment is not independently repeated yet. N58 interaction is now reproduced across 24724/24737/24819 at 2938.628/2935.879/2937.148, approximately +5.77% versus fresh auto N58 control 24736. All pass full local protocol, joint latency SLA and output/runtime checks. [Reviewed results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0028/H200_RESULTS.md).

**H100 highest individual remains 221590 = 2430.891 good output tokens/s.** New control/decode-inference/prefill-inference 221923/221924/221966 pass at 2424.365/2430.657/2424.089: flat; close the tested phase-mode options and do not combine unproven gains. [Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0028/H100_RESULTS.md).

Keep platforms separate. Official full-set accuracy at 99% of reference remains unverified. Scheduler completion alone never means a valid measurement.

## Submitted followups and live snapshot

H200 **24912/24913/24914/24915**: fresh auto N60 control, HPC-Ops N60 repeat, fresh auto N62 control, HPC-Ops N62 with separate post-score profile. **24912 completed and passes** at 2838.853 good tokens/s, joint fraction 0.987599, TTFT 822.292 ms, ITL 16.579 ms. **24913/24914/24915 pending Resources** at 00:51 UTC. The original N60 treatment is preliminarily +5.33% above this control, still awaiting treatment repeat. No automatic N64. [Receipts, payloads and result](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-h200-load/RESULTS.md).

PBS **222027 → 222028**, **R/H** at 00:51–00:52 UTC: fresh FlashInfer decode control vs native FA3 decode, current both-phase HPC-Ops N54/chunk4096, MNNVL AUTO+PDL, default no_grad. Same BF16/protocol/output checks and separate post-score CPU/GPU profiles. No new attention result yet. Compare fresh control and repeat a useful gain before promotion. [Plan, receipts and checks](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-decode-attention/RESULTS.md).

## Collective screens and remaining costs

Micro jobs **222022/222023/222026 completed** with local numerical/completeness checks. First screen exposed host launch-cadence ambiguity; graph32 refinement rejects forced one-shot at 32–64 tokens. Separate on/off test rejects PDL disabled. **Keep native AUTO strategy and PDL enabled; no full-model patch for either losing override.** These are microseconds per collective, not model goodput or official accuracy. [Complete reasoning entry](../reports/research-journey-20261019/journal/entries/20261020-serving-and-collective.md).

Winning H200 profile has 16 sealed rank traces in a separate successful N48 diagnostic. Named HPC GEMM, MNNVL collective and attention sums motivate next experiments; they are not critical-path wall fractions. [Analysis](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0028/H200_PROFILE.md).

NCCL correction remains current: representative LL symbols cannot identify selected protocol. Sealed TUNING logs show forced Simple selected and control already Simple on larger operations. Forced Simple closed on flat performance, not failed activation. [Correction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1755/CORRECTION.md).

## Credit and execution

Published ledger **20 October 08:40 SGT**: Used **34035.199 SU**, Balance **29794.134 SU**, In Doubt **170.667 SU**. Balance already excludes prepayment. Three inference-mode charges reconcile to 1410.275 SU; first micro charge is reflected, two later micro maximum reservations remain until ledger reconciliation. Total unreleased maximum reserve **3413.333 SU**, internal headroom **13551.468 SU**, unchanged **51000-SU cap** and **13000-SU buffer**. These are conservative planning bounds, not actual charges. Actual records: nscc-pbs/nscc-budget.json.

Existing VPN/SSH works; no reauthentication or restart. A missing login-shell wrapper briefly caused `qstat: command not found`; the corrected command returned real states. Do not diagnose that as expired authentication.

During active authorised work, review completions and submit the next distinct justified hypothesis when budget/slots permit. Losing branches do not stop all research. No blind queue filling, unchanged losses or automatic load growth. At most five active H200 jobs, three active PBS jobs and one running PBS GPU allocation.

## Journey and backup

[Start with the retained journal](../reports/research-journey-20261019/journal/README.md). The initial dated retrospective has 32 stages; the linked 20 October entry records each new question, hypothesis, control, job, result, assessment, correction and next decision. Coverage counts belong to the dated audit, not a claim that every chat statement survived.

Capture, verify, commit and push each small coherent milestone promptly. GitHub contains the Git portion; large external evidence still needs separate off-host backup. Chat Vietnamese, artifacts English; Qwen only, HPC_Task empty. No slide/package promotion. Autopilot OFF: no background Codex, schedules or automatic chat notifications.

## VPN duration clarification — 20 October 2026, 01:04 UTC

Read-only inspection confirms the helper requests IKE 86400 seconds (24 hours), enables private persistence and runs under detached tmux. The client process had about 21 hours 3 minutes uptime; a fresh SSH command succeeded at 01:04:10 UTC. Requested lifetime is not the verified negotiated expiry; tmux, private state persistence and SSH ControlPersist are separate mechanisms. No current-session change, restart or authentication. [Duration, evidence and future configuration](../tutorial/19-vpn-session-lifetime.md). Queue and credit snapshots above are not refreshed by this VPN inspection.

## Extended run inspection — 20 October 2026

The user asked for utilization, resource usage, log and insight inspection for each run. Existing raw request/runtime/output/cost checks and selected CPU/GPU diagnostics do not establish uniform resource coverage. Added six sealed H200 extended inspections: all have TTFT p99 above 3000 ms while passing the existing joint fraction; 24738 has TTFT p99 3230.452 ms and ITL p99 15.720 ms. Sparse whole-run prefill queue peaks and decode KV token occupancy are observations, not phase-aligned causes. AIPerf telemetry endpoints are empty; no continuous GPU utilization/power/VRAM claim. Found 24819 start-profile HTTP 200 responses misclassified by unconditional JSON parsing, plus stop HTTP 500; 16 sealed traces still exist. Prepared a derived HTTP fix with six local fixture checks, not deployed to frozen jobs. Full report: [extended inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md); [reasoning entry](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261020-observability.md).

Every completed-run review should distinguish collected, inspected, findings, limits and next hypothesis. Include tail/error/concurrency, role queue/batch/KV, runtime/diagnostic and cost evidence; mark missing data explicitly. Future derived bundles need bounded matched hardware/server telemetry and phase markers after interface/overhead validation. Those collectors are not implemented/deployed by this audit. No GPU job, queue/credit refresh, authentication, slide or automation change.

