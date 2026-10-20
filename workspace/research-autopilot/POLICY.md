## Extended run inspection — 20 October 2026

The user asked for utilization, resource usage, log and insight inspection for each run. Existing raw request/runtime/output/cost checks and selected CPU/GPU diagnostics do not establish uniform resource coverage. Added six sealed H200 extended inspections: all have TTFT p99 above 3000 ms while passing the existing joint fraction; 24738 has TTFT p99 3230.452 ms and ITL p99 15.720 ms. Sparse whole-run prefill queue peaks and decode KV token occupancy are observations, not phase-aligned causes. AIPerf telemetry endpoints are empty; no continuous GPU utilization/power/VRAM claim. Found 24819 start-profile HTTP 200 responses misclassified by unconditional JSON parsing, plus stop HTTP 500; 16 sealed traces still exist. Prepared a derived HTTP fix with six local fixture checks, not deployed to frozen jobs. Full report: [extended inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md); [reasoning entry](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261020-observability.md).

Every completed-run review should distinguish collected, inspected, findings, limits and next hypothesis. Include tail/error/concurrency, role queue/batch/KV, runtime/diagnostic and cost evidence; mark missing data explicitly. Future derived bundles need bounded matched hardware/server telemetry and phase markers after interface/overhead validation. Those collectors are not implemented/deployed by this audit. No GPU job, queue/credit refresh, authentication, slide or automation change.

## Research continuation — 20 October 2026

Reviewed five H200 and three H100 completed full-model runs. H200 N58 HPC-Ops interaction now repeats across three deployments; N60 reaches a new individual 2990.151 good output tokens/s, awaiting treatment repeat. Submitted H200 24912/24913/24914/24915; 24912 fresh auto N60 passes at 2838.853, the other three were Resources-pending at 00:51 UTC. H100 phase-specific inference mode is flat and closed. Three bounded 8-GPU collective screens preserve numerical gates and expose launch-cadence ambiguity, then reject forced one-shot and disabling PDL. Keep native AUTO+PDL; no full-model patch for these losses. New H100 native decode FlashInfer/FA3 pair 222027→222028 was R/H at 00:51–00:52 UTC, with 3072 SU maximum reserve. No attention score yet.

Published Used 34035.199 SU, Balance 29794.134 SU, In Doubt 170.667 SU (08:40 SGT publication); Balance already excludes prepayment. Total unreleased maximum reservation 3413.333 SU, internal headroom 13551.468 SU under unchanged cap/buffer. Existing access reused, no authentication or automation changes. Full official accuracy unverified. [Full hypothesis/control/result/assessment/next-decision entry](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261020-serving-and-collective.md). Earlier states below are historical.

## Complete retained journey and reasoning records — 2026-10-19T19:25:31.405094+00:00

The user clarified that the request covers the whole journey, not only the last NCCL interpretation: preserve each hypothesis, assessment, result, improvement and next decision. Added a 32-stage source-linked retrospective and a 194-job index, backed by an audit of 247 retained Markdown records. All audited source/archive/Git hashes match at the stated audit commit. 127 jobs have dedicated purpose/observation/lesson sections; an ID mention or plan is not a certified complete review. No claim recovers every unrecorded chat statement. [Entry point](/home/apacsc42/workspace/reports/research-journey-20261019/journal/README.md). New milestones must retain the question, control/change, evidence, units, assessment, next decision and corrections, then capture/commit/push promptly.

This is a documentation and coverage milestone only. Scheduler/credit snapshots remain dated; no job query/submission, model rerun, budget change, authentication, slides or background automation was performed. Existing GPU jobs are left alone.

## Prefill-only phase test submitted — 2026-10-19T18:00:11.710346+00:00

Submitted **221966.pbs111** after 221924, extending the verified chain **221923 → 221924 → 221966** (default control, decode-only inference mode, prefill-only inference mode). Actual post-submit states Q/H/H; no new measurement. New additional maximum reserve 1536 SU, total 4608 SU, internal headroom 13787.272 SU; published Used 32604.728 and Balance 31395.272 SU, no new charge. Caps/buffer unchanged, no overlapping 16-GPU allocation or fourth active PBS job. Five H200 jobs remain Priority-pending at the 17:55 check. [Hypothesis and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-prefill-inference/RESULTS.md).

The NCCL interpretation correction in the preceding checkpoint remains current: existing TUNING decisions show Simple selected and explain why missing Simple-labelled symbols were not evidence of failed activation. No GPU job is needed for that ambiguity. Preserve all historical measurements; no new peak, accuracy, authentication, slides or automation claim.

## NCCL interpretation correction and live queues — 2026-10-19T17:58:15.294282+00:00

At 17:55 UTC, PBS 221923 Q (exclusive nodes in use), 221924 H (afterany dependency); all five H200 jobs still Priority-pending. No new measurement or charge; Used 32604.728, Balance 31395.272 SU, 3072 SU maximum reserve and 15323.272 SU internal headroom. Existing access works, no reauthentication.

Corrected an old interpretation: LL-labelled NCCL symbols are representatives and do not identify selected protocol. Existing sealed TUNING logs show Simple selected in 221885 and already selected for the control's large operations; the small +0.2315% score does not establish a useful gain. No GPU rerun is needed to explain the names. Keep automatic protocol policy. [Correction, sources and parsed counts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1755/CORRECTION.md). Earlier activation claims and symbol-count gates are historical and superseded. No score, accuracy, slide or automation change.

## Decode inference-mode pair submitted — 2026-10-19T17:27:18.644559+00:00

Actual new PBS chain **221923 → 221924**: explicit-default control Q and decode-only inference-mode candidate H at the post-submit check. Fixed N54 scoring, model precision, transport and output checks remain unchanged; separate CPU/GPU profiles and pinned DynamicGradMode source/context preflights are retained. No benchmark result yet. New maximum reserve 3072 SU; published Used 32604.728, Balance 31395.272, In Doubt zero; internal headroom 15323.272 SU under unchanged cap/buffer. Five H200 jobs remained Priority-pending at 17:20 UTC. [Rationale and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-inference-mode/RESULTS.md). The preceding empty-queue review checkpoint is historical. Continue review and justified research during authorised work; no blind repeats, authentication, background Codex or slides.

## H100 protocol and host-profile review — 2026-10-19T17:25:27.642282+00:00

Jobs 221884/221885/221886 pass full local gates at 2415.474/2421.066/2425.886 good tokens/s; no new peak. Global Simple parses but its actual kernel activation remains unverified, so close full-model selector sweeps. Attention 221880 is a valid −7.74% regression and closed. All four charges reconcile at 1875.626 SU; published Balance 31395.272, Used 32604.728, no outstanding reservations, internal headroom 18395.272 under unchanged caps. PBS empty and H200 five Priority-pending at 17:20 UTC. Continue with a source-supported matched decode inference-mode test rather than stopping research. No new GPU job at this review checkpoint; no official accuracy, slide or automation claim. [Full review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1720/RESULTS.md). Older snapshots below are historical.

## Global protocol activation followup — 2026-10-19T14:37:21.593278+00:00

Reviewed H100 control/chunk/scoped-protocol points at 2413.802/2411.995/2414.548 good tokens/s; no established gain, scoped Simple activation unverified in separate N48 traces. Submitted and verified chain **221880 → 221884 → 221885** (attention, instrumented default control, global prefill Simple). Attention was running at 14:30 UTC; others dependency-held. Three active PBS jobs and five H200 pending at prior 14:18 check. Total max PBS reserve 4608 SU; Used 30729.102, published Balance 33270.898, In Doubt zero; internal headroom 15662.898 SU. Budget cap/buffer unchanged. Review each completion and continue justified research without another reminder. No new official accuracy or performance claim, VPN auth, background AI or slides. [Receipts and rationale](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-protocol-check/RESULTS.md).

## Research continuation — 2026-10-19T14:27:36.052008+00:00

At the 14:18 UTC check all three preceding PBS allocations finished and H200's five jobs remained pending Priority. Submitted **221880.pbs111** for the already prepared dense FlashInfer-prefill N54 trial, source/fresh control 221827 passing at 2413.802 good tokens/s. The other completed trials show no clear throughput gain; preserve their separate reviews. Scoped Simple activation is unverified because separate N48 traces still show Ring LL. Chunk6144's derived prefill graph settings are now strictly checked against the exact runtime source. Published Balance 33270.898 SU, Used 30729.102, In Doubt zero; terminal charges 1337.458 SU reconciled. New maximum reserve 1536 SU; internal headroom 18734.898 SU. Continue researching and using available PBS slots within caps. [Submission and budget evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1418/SUBMISSION.md). No new peak, official accuracy, scheduler automation or slide claim.

## Frequent commit and push rule — 2026-10-19T13:38:30.266691+00:00

The user requires small, coherent backup checkpoints rather than large batches. Commit and push each safe, reviewable unit as it is completed: hypothesis/scripts/config; submission receipts with reservation updates; one completed-run review; a fix; or docs. Do not wait for GPU completion or a whole experiment wave, and do not sweep unrelated staged changes together. Keep dependent files reproducible, exclude secrets, verify capture and origin/main, and disclose exact uncaptured/unpushed work if interrupted. No artificial commit count, new history rewrite, background sync, schedule or GPU allocation is authorised by this rule. Persisted in home and archive AGENTS.md and archive docs/GITHUB_WORKFLOW.md. Existing research snapshots below retain their original timestamps.

## Continue research and submitted batch — 2026-10-19T12:02:20.997548+00:00

The user explicitly corrected idle research: during active authorised work, review results, research the next distinct hypothesis and submit when capacity/budget permit without another reminder. Losing N56 or Tree is not a global stop. Actual new jobs: PBS **221827 → 221828 → 221829** (N54 fresh control/profile, HPC-Ops chunk6144, prefill Simple protocol/profile); H200 **24819** (N58 winning interaction repeat/profile), preserving four older queued jobs. Five active H200 jobs and three serial PBS jobs. New PBS maximum reserve 4608 SU; pre-submit Balance 34608.356, Used 29391.644, In Doubt zero; internal headroom 17000.356 SU under unchanged cap/buffer. New jobs have no measurements yet. Full plan, references, hashes and receipts: [research continuation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1200/RESULTS.md). Review each completion and continue justified work. No blind duplicates, unchanged loss retries, automatic load growth, AI schedules or background Codex. Highest observations/accuracy limits unchanged.

## Status review — 2026-10-19T11:15:15.315162+00:00

Live checks at 11:11 UTC: H200 24733/24736/24737/24738 remain pending for Priority; two hpcai nodes allocated. Highest H200 observation remains 2938.628 good tokens/s; its own interaction repeat has not run. All three PBS jobs completed and pass full local protocol/SLA/runtime/output checks: N54 repeat 221645 = 2418.588; N56 221646 = 2407.364; forced prefill Tree 221669 = 2160.946 good tokens/s. Tree execution is proved on all eight prefill ranks in 16 sealed diagnostic traces (355/355 successful requests); it loses 10.65% versus fresh N54 and is closed. N56 has no observed gain; no automatic N58. Highest H100 individual observation remains 2430.891. Official accuracy unverified. PBS queue empty; VPN/SSH usable without restart or authentication. Balance 34608.356 SU; three terminal charges reconcile, zero remaining reservations and internal headroom 21608.356 SU under the unchanged cap/buffer. No new GPU job, schedule, slide or submission change. [Full report and raw evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1111/RESULTS.md). This supersedes earlier queue and credit snapshots below.

## Report update — 19 October 2026

The owner requested a source-linked research journey and future-direction report, committed with category `report`. See workspace/reports/research-journey-20261019/REPORT.md. Highest accepted H200 observation remains 24724 = 2938.628, interaction repeat pending; completed auto-decode N60 repeat 24732 passes at 2836.531. No new submission, budget change, authentication or AI schedule in this report turn. Later scheduler changes need a fresh check. Earlier running 24732 statements below are historical and superseded by this report. Autopilot remains OFF.

## Manual optimisation — 2026-10-19T06:04:59.145550+00:00

H200 24724 passes at 2938.628 good tokens/s, +5.6907% versus fresh same-N58 control 24721. Chunk-12288 job 24723 passes but loses 2.3789%; close it. Submitted H200 24736/24737/24738 for fresh control, independent interaction repeat and N60. Existing 24732 running, 24733 pending. Submitted one source-checked H100 N54 prefill Tree trial 221669 after 221646, preserving 221645→221646→221669 serial chain. Total PBS max reserve 4608 SU; ledger Balance 36024.320 SU, internal headroom 18416.320 SU, no budget increase. Full local gates and actual Tree trace activation required. Report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md. No official accuracy claim, slides, organiser upload or AI schedule; autopilot OFF. Supersedes older snapshots below.

## Repository publication update — 2026-10-19T05:48:14.782568+00:00

The owner authorised the private GitHub repository, safe Git publication and a conventional-subject history correction with at least 60 commits. This supersedes older GitHub-deferred statements below. Git is hosted privately; external artifact bytes remain local. No new GPU submission, scheduler query, VPN authentication, budget change or AI schedule occurred in this repository task. Autopilot remains OFF. Report: workspace/reports/github-publication-20261019/REPORT.md.

## Manual result review and next batch — 2026-10-19T05:32:52.311985+00:00

H200 24722 N60 passes at 2839.532 good tokens/s (+2.1266% vs fresh 24721); H100 221590 N54 passes at 2430.891 good tokens/s (+0.8123% vs fresh N52 repeat 221589). All local terminal/protocol/runtime/short/long gates pass; official accuracy unverified. Submitted H200 24732 N60 repeat and 24733 N62; PBS 221645 N54 repeat → 221646 N56, new maximum 3072 SU. Older 24723/24724 keep positions. Conservative internal headroom 18814.542 SU; no budget increase. Full readable report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0527/RESULTS.md. Autopilot remains OFF. This supersedes older queue/measurement/credit snapshots below.

## Manual continuation — 19 October 2026

Four H200 trials 24721–24724 and two serial PBS trials 221589→221590 were explicitly submitted after user continuation, source review and live queue/credit checks. New maximum reserve 3072 SU, internal headroom 20728.853 SU; no budget increase. No new score yet. Latest report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0412/RESULTS.md. This supersedes scheduler/access/budget snapshots below; standing safety and acceptance rules continue. Autopilot remains OFF and no background watcher was started.

## Live status update — 19 October 2026

This user-requested status/login check supersedes older queue, VPN and credit snapshots below. Both own queues are empty; VPN and SSH restored at 04:01 UTC with private cache retained. Five H200 runs and three recovered PBS runs pass local protocol/SLA/output checks. H200 24647 repeats 2780.483 good tokens/s; H100 221341 N52 reaches 2398.728, awaiting an independent N52 repeat. Fresh PBS balance is 36800.853 SU, In Doubt 0; all three terminal reservations reconciled. No new job or AI schedule was submitted. Full report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0400/RESULTS.md. Autopilot remains OFF. Older access restrictions describe their historical checks; this login was explicitly requested by the user.

## 18 October 2026 — local Git preservation task

The user requested a local backup first, with GitHub CLI/authentication/upload deferred. Created `/home/apacsc42/apac-hpc-ai-research` plus its required sibling `apac-hpc-ai-research-artifacts`. The base capture has 17,570 retained source files, 477 verified unique external objects, about 93.31 GB logical data and 18.83 GB compressed objects. Metadata-backed import groups use real retained dates and current committer dates; no fake daily/month activity. User identity is `trungdangtapcode <tcuong1000@gmail.com>`. Intended later remote is private `trungdangtapcode/apac-hpc-ai-research`.

Authentication/session material is excluded. Two damaged archives are preserved as local-only review objects. Exact local container hashes match the tested contract. Public model weights and uncollected remote H100 results are outside the capture; metadata and reproduction limits are documented. Deep checksum and representative recovery tests pass. Local data is not protected against loss of this machine until copied off-host. Original research directories, queued jobs, VPN and disabled autopilot are untouched. This is an archive copy; later original-directory changes need a new explicit capture.

See [preservation report](../reports/local-repository-backup-20261018/REPORT.md) and the new archive README. Earlier experiment scheduler/credit statements remain dated snapshots, not live observations.

## 18 October 2026, 19:25 UTC — failed N58 replication, bounded diagnostic retry

24588 timed out: raw records 857 warmup, zero scored. Warmup sent 858 and indefinitely awaited its final completion; all model workers became ready normally. Connection refusals at shutdown are downstream, not an identified root cause. No accepted measurement. Raw artifacts/phase evidence retained. Prior peak remains unconfirmed by N58 repeat/new same-load control.

Submitted 24647: exact same serving config and scoring arguments, with a 360-second whole-client guard plus 15-second kill fallback. This is containment and one diagnostic retry, not a root-cause repair. Any aborted client is rejected; no request filtering or phase shortening. If repeated, stop this retry path and diagnose stream completion rather than unchanged retries. Queue 24589/24639/24640/24641/24647 pending Resources, five active. H100 VPN still unavailable; no new PBS outcomes or credit. No AI schedule/background watcher or official changes.

Full evidence and acceptance rules: [failure diagnosis and retry](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1923/RESULTS.md). Older entries are historical snapshots.

## 18 October 2026, 18:46 UTC — H200 small gains independently repeated

24573 chunk 6144 repeats at 2737.410 good tokens/s, +0.8590% versus fresh control 24575 at 2714.097. 24574 HPC-Ops prefill repeats at 2728.962, +0.5477% versus that control. All three pass terminal payload/protocol/runtime/SLA and short/12-long output gates. The original observations were 2737.011 and 2732.459. These small positive differences persist across repeat/fresh control; official full-set accuracy remains unverified.

Submitted and verified 24639 (HPC-Ops decode with DeepGEMM prefill N58), 24640 (HPC-Ops prefill chunk 6144 N56), 24641 (HPC-Ops prefill+decode N56). Existing 24588/24589 keep positions. Five active H200 jobs; no sixth. Declared comparisons isolate runner/chunk/load where possible; no additive gain assumption or automatic higher load. Full controls and stopping rules: [review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1845/RESULTS.md).

H100 remains inaccessible: no live VPN process, SSH not attempted by wrapper. No reauthentication/DUO/cache modification. Actual later PBS job outcomes and credit unknown; preserve conservative reservations. Last known H100 peak 2371.961 and repeat 2371.341 remain historical verified evidence, not new results. No AI scheduling, background watcher, official package or organiser upload.

Older dated entries below are historical snapshots.

## 18 October 2026, 13:51 UTC — H100 both-phase HPC-Ops repeats consistently

Independent repeat 221339 passes all local gates at 2,371.341 good tokens/s versus original 221315 at 2,371.961. Mean 2,371.651; repeated gain 2.7009% versus matched decode-only control 221314 (original 2.7277%). Fresh reversed-order control 221340 is running; N52 job 221341 held. Official full-set accuracy unverified.

Submitted 221346: full N50 score followed by separate N48 profile of both-phase HPC-Ops, 16 ranks expected. Verified chain 221340 → 221341 → 221346. Previous auto-prefill profile is no longer sufficient for the changed prefill implementation. H200 five jobs still pending Priority; no new H200 submission. Ledger Used 25,846.898 SU, Balance 36,617.102 SU, In Doubt 1,536 SU. Terminal 221316/221339 charges 897.706 SU reconcile. New reserve 1,536 SU; total outstanding 4,608 SU; planning headroom 20,545.102 SU. Autopilot stays off.

Full evidence and stopping rules: [repeat and profile plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1350/RESULTS.md). Older entries are historical snapshots.

## 18 October 2026, 13:27 UTC — new peaks and five submitted followups

H200 24544 passes full local gates at 2,786.696 good tokens/s: DeepGEMM prefill chunk 8192 N58, +2.5244% versus historical same-load chunk 4096 control 24352. New independent repeat 24588 and fresh same-load control 24589 submitted; historical comparison alone cannot isolate chunk benefit. H200 HPC-Ops decode 24538 also passes at 2,733.199 (+0.6395% versus 24526), ITL 14.858 ms with higher TTFT 1037.104 ms. Future bounded N58 test is a hypothesis, not submitted while the five-job queue is full.

H100 HPC-Ops prefill+decode 221315 passes at 2,371.961, +2.7277% versus fresh decode-only control 221314 at 2,308.979. TTFT falls 669.245 → 486.401 ms; ITL rises 17.831 → 18.221 ms. Decode-only N52 repeat 221316 passes at 2,318.328, +0.4049% versus N50 with higher TTFT. New verified chain 221339 (both-phase N50 repeat) → 221340 (fresh decode-only N50 control) → 221341 (both-phase N52). All local quality/runtime gates retained; official full-set accuracy unverified.

Ledger Used 24,949.192 SU, Balance 37,514.808 SU, In Doubt 1,536 SU as of 21:20:07 SGT. Reconciled 918.756 SU for 221314/221315. Terminal 221316 cost 519.964 SU pending in ledger, retain full reserve. New maximum reserve 4,608 SU; conservative outstanding 6,144 SU; planning headroom 19,906.808 SU. Do not subtract prepayment twice. No AI scheduling, background watcher, slide/package changes or organiser upload.

Full hypotheses, controls, stopping rules and raw evidence: [review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1323/RESULTS.md). Older dated entries are historical snapshots.

## 18 October 2026, 12:19 UTC — five completed reviews and six new trials

H200 chunk 6144 job 24528 passes all local checks at 2,737.011 good tokens/s, +0.7798% versus control 24526. HPC-Ops prefill 24529 passes at 2,732.459, +0.6122%. Single observations; independent repetitions and a fresh control submitted as 24573/24574/24575. Keep existing 24538/24544 queue positions; five active H200 jobs, no sixth.

H100 N52 job 221276 passes at 2,314.735, only 0.2384% above new N50 score 221284 (2,309.229), with higher TTFT. Job 221285 chunk 8192 loses 2.4813% versus the preceding N50 score; close this H100 branch. New profile 221284 has 16 valid rank traces and 371/371 successful requests. Prefill fused MoE remains a large named kernel; HPC-Ops group GEMM is visible in decode. Kernel shares describe summed durations, not wall-time speedups.

Submitted verified PBS chain 221314 (fresh HPC-Ops decode N50 control) → 221315 (add HPC-Ops prefill only) → 221316 (independent N52 repeat with auto prefill). Full gates remain mandatory. Official reference-set accuracy unverified. Ledger increment 1,957.547 SU reconciles all four previous terminal jobs; Used 24,030.436 SU, Balance 39,969.564 SU, In Doubt 0. New reserve 4,608 SU, planning headroom 22,361.564 SU. No AI scheduling, background watcher, slide/package change or organiser upload.

Full hypothesis/control/stopping rules and evidence: [review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1215/RESULTS.md). Older dated entries below are historical snapshots.

## 18 October 2026, 09:28 UTC — result-driven continuation and three new jobs

Standing user instruction: review each completed job, refine the hypothesis and submit the next justified experiment without waiting for an unrelated batch. Respect runtime/output gates, budget and queue caps. This does not enable Codex autopilot or replacement scheduling.

Fresh H100 control 221275 passes full local review at 2,248.459 good tokens/s. HPC-Ops repeat 221274 remains 2.4739% above this new control; its previous control comparison was +2.6073%. The original pair was +2.7955%. The direction survives a fresh reversed-order control, while first-token latency remains higher and inter-token latency lower. Official full-set accuracy remains unverified.

Submitted and verified 221284 (HPC-Ops N50 score then separate profile) → 221285 (HPC-Ops N50 with prefill chunk8192), after existing running 221276 (N52). New H200 24544 tests DeepGEMM chunk8192 at N58 after two small positive N56 observations. Existing pending H200 jobs retain positions. Full hypotheses, controls and stopping rules: [plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-0925/PLAN.md).

Ledger Used 22,072.889 SU, Balance 40,391.111 SU, In Doubt 1,536 SU (17:20:01 SGT). Reconciled 221274 charge 492.658 SU. Terminal 221275 charge 492.089 SU is still pending in ledger, so retain full reservation. New pair reserves 3,072 SU; total conservative outstanding 6,144 SU; planning headroom 22,783.111 SU. Prepayment is not deducted twice. No slide, official package, organiser upload, AI schedule or background Codex change.

Older dated entries below are historical snapshots.

## 18 October 2026, 09:18 UTC — repeat results, no new submissions

H100 HPC-Ops decode independent repeat 221274 passes full local runtime, protocol and output review at 2,304.083 good tokens/s, +2.6073% versus previous matched control 221262. Original 221263 was 2,308.308; descriptive mean 2,306.196. Fresh control 221275 is running; bounded N52 job 221276 is held behind it. Do not claim a confidence interval or official full-set accuracy.

H200 chunk8192 repeat 24527 completes and passes full local review at 2,718.692 good tokens/s, +0.1053% versus fresh control 24526. The original +0.2022% observation is now supported by a second small positive difference; no large material gain established. Jobs 24528, 24529 and 24538 remain pending Priority. Preserve positions. No new job this turn.

Ledger snapshot as of 17:00:01 SGT: Used 21,580.231 SU, Balance 40,883.769 SU, In Doubt 1,536 SU. Terminal 221274 cost estimate 492.658 SU is not yet reconciled; retain full reservation. Total outstanding maximum reserve remains 4,608 SU, planning headroom 24,811.769 SU. Do not subtract prepayment twice. Autopilot remains OFF.

Full details: [repeat reviews](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-0917/RESULTS.md). Earlier entries are historical snapshots.

## 18 October 2026, 08:56 UTC — HPC-Ops decode gain and confirmation jobs

H100 221263 reaches 2,308.308 good output tokens/s, +2.7955% versus fresh matched 221262 at 2,245.534. Mean ITL improves to 17.804 ms from 19.448; mean TTFT rises to 678.908 ms from 457.898. Joint SLA 98.7526%; full local payload, protocol, runtime and short/12-long checks pass. Independent replication remains pending; organiser full-set accuracy is unverified. H200 fresh control 24526 passes at 2,715.832, matching prior controls. Other existing H200 trials are still pending.

Submitted and verified PBS chain 221274 (HPC-Ops N50 repeat) → 221275 (fresh auto control N50) → 221276 (bounded HPC-Ops N52). Submitted H200 24538 (HPC-Ops decode only, confirmed DeepGEMM prefill) without combining the pending prefill backend change. Preserve queue positions and close failures rather than retrying unchanged. H100 profile has 16 valid rank traces and 360/360 successful separate diagnostic requests. Kernel fractions are descriptive, not speed predictions.

Reconciled the completed PBS pair: 925.013 SU. Latest Used 21,580.231 SU, Balance 42,419.769 SU; new maximum reserve 4,608 SU; planning headroom 24,811.769 SU. Existing cap/buffer unchanged. All-history metric report and job cards refreshed. Slides and official package untouched. Codex autopilot remains OFF; no schedule, background Codex or watcher launched.

Full evidence and next-step stopping rules: [review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-0900/RESULTS.md). Older entries below are historical snapshots, not live state.

## 18 October 2026, 08:12 UTC — reviewed completions and submitted six controlled trials

H200 chunk 8192 job 24425 reaches a provisional 2722.281 good tokens/s, +0.2022% over control; independent repeat required. New control 24429 is 2715.549. Graph-off branches lose on both platforms, and H200 DeepGEMM graph-off fails SLA. H100 prefetch throughput gain does not replicate: 2225.562 versus 2238.778 control; startup remains much shorter but cache/node/order confounds remain. Official full-set accuracy remains unverified.

Corrected the old DeepGEMM profile classifier: ~0.8% was an undercount of renamed kernels. Corrected MoE-associated prefill shares are 34.81%/34.83% versus 42.84%/42.77% previously, descriptive summed kernel duration shares only. All 16 ranks and 421/421 diagnostic requests are valid.

Submitted H200 job 24526 control, 24527 chunk 8192 repeat, 24528 chunk 6144, 24529 HPC-Ops prefill. Submitted PBS 221262 prefetch control/profile → 221263 HPC-Ops decode. HPC-Ops has source compatibility only; GPU, latency and output gates remain mandatory. Reserve 3,072 SU; reconciled Used 20,655.218 SU, Balance 43,344.782 SU, headroom 27,272.782 SU under unchanged planning cap. Prior three jobs charged 2173.156 SU. Queues/receipts verified. The old non-AI watcher exited; its submission function ran once under lock. Codex autopilot stays OFF.

Full details and frozen evidence: [review and plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-0800/RESULTS.md). Earlier dated entries below are historical snapshots, not live scheduler state. No slide, official script or organiser upload changes.

## Current follow-up — 17 October 2026, 23:55 UTC

Five Slurm jobs are pending: 24376, 24425, 24426, new 24428 (DeepGEMM N54), new 24429 (DeepGEMM N56 score plus post-score diagnostic). Three PBS jobs remain queued in the verified chain; no fourth was submitted. Ledger reconciled: Used 18482.062 SU, Balance 45517.938, In Doubt 0; outstanding reserve 4608, planning headroom 27909.938. The invalid TP8/EP2 branch stays closed. No new AI scheduling is enabled.

## Current follow-up — 17 October 2026, 23:43 UTC

DeepGEMM H200 N56 gain is replicated. Equal-TP8/EP2 candidate 24375 is rejected for severe SLA and output failure; do not retry unchanged. Pending H200: 24376, 24425, 24426. Pending PBS chain: 221181 → 221194 → 221195. Ledger Used 17612.800, Balance 44851.200, In Doubt 1536; retain full terminal reserve for 221177 until billed. Outstanding reserves 6144 SU, planning headroom 27243.200 SU. Never subtract prepaid credit twice. Read the latest results before new trials. No Codex autopilot is enabled.

## Current follow-up — 17 October 2026, 18:33 UTC

Queues remain full at the existing caps: five H200 and three PBS jobs. No new submissions this turn. A frozen DeepGEMM/chunk8192 N56 candidate exists but is not registered with the watcher. Read research-followup-20261017-1830/conditional-candidate.json; review pending 24327 and 24376 before deciding to arm it. Initial-burst TTFT misses do not authorise changing or filtering the official benchmark. No Codex autopilot is enabled.

## Current follow-up — 17 October 2026, 17:54 UTC

H100 pending chain 221153 → 221177 → 221181 reserves 4,608 SU; headroom within existing internal limit is 29,316.800 SU. H200 equal-TP repair 24375 and graph ablation 24376 are submitted. Review the observed failures and new outcomes before further retries. Verify transport patch selection against TP geometry before cloning a baseline. Separate startup savings from ranked throughput. No Codex autopilot is enabled.

## Current follow-up — 17 October 2026, 16:59 UTC

H100 control and failed startup are reconciled; 221153 and readiness-only retry 221177 retain 3,072 SU maximum reservation. Ledger balance is 46,924.800 SU, operating headroom 30,852.800 SU under the existing internal limit. H200 N58 prefill DeepGEMM test 24352 is submitted. Do not extrapolate the historical control comparison as a same-time causal effect or automatically advance to N60. Review pending outcomes before choosing the next trial. No Codex autopilot is enabled.


## 2026-10-17 14:18 UTC — submissions on both clusters

The user requested continued submissions on both servers and clarified that the Slurm server is not credit limited. Three H100 jobs (221151, 221152, 221153) were submitted and verified in an afterany chain; three H200 jobs (24320, 24321, 24322) were submitted by the existing watcher. They test fresh controls, phase-specific compute/layout changes and prefill weight prefetch. Full plan and receipts: qwen-experiments/nscc-pbs/inspection/manual-20261017-1410/PLAN.md.

Corrected the budget interpretation: project balance is 48,463.075 SU, not 847.075 SU. The latter was the old internal campaign remainder. The user authorised continuation after this clarification. The revised 51,000 SU planning bound retains a 13,000 SU buffer; neither amount is an organiser quota. The batch reserves at most 4,608 SU.

H200 job 24282 failed before measuring because TP8/EP1 produces a 192-element MoE weight partition incompatible with FP8 block 128. TP8/EP2 gives 384; corrected job 24321 tests that layout. H200 job 24291 passed protocol/runtime/SLA/short/12-long review at 2,715.842 good tokens/s, +1.8136% versus 24263. An independent repeat is armed. Its first reviewer rejection was an overly narrow runtime delta allowlist; the revised review explicitly checks both main and speculative runner values and that speculative decoding remains disabled. Preserve both review files.

Autopilot remains disabled. GPU submissions do not authorise background Codex scheduling. No submission slides or BTC upload changed.

## Latest decision — 2026-10-17 12:27 UTC

Job24281 is a reviewed performance regression,−1.73% versus fresh control.
Close this branch; do not automatically repeat it. Jobs24282/24291 remain pending.
See serving-tuning-10/prefill-pilot-reviews/24281_RESULT.md. Codex autopilot stays off.

## Latest experiment decision — 2026-10-17 10:58 UTC

Profile 24263 supports one prefill-only DeepGEMM trial, job 24291. This differs from the rejected decode-only trial. Four H200 jobs are pending; H100 budget is unchanged. Profile concurrency was 48, correcting older plans. Keep all control warnings and do not convert kernel fractions to wall-time gains.

See serving-tuning-10/profile-review-24263/RESULTS.md. Codex autopilot remains OFF.

## Language policy — 2026-10-17 10:10 UTC

The user clarified: **Vietnamese for chat only. English for the codebase and all work artifacts**, including code, comments, documentation, research plans, reports, notes, tutorials, and submission materials. This supersedes earlier permission to write tutorials or learning notes in Vietnamese. Use readable English with normal spacing and explain unfamiliar terms. Do not translate immutable raw logs or historical experiment evidence.

The current prefill experiment plan has been rewritten in English. Existing Vietnamese historical documents remain historical; this update does not claim they have all been translated.

## Additional bounded pilots — 2026-10-17 09:58 UTC

24281batchlimit1/24282singleTP8prefill addedfromexistingTTFT/batchingobservations;
notrequiredtowaitforprofileforallhypotheses. Queue4/5,H100budgetunchanged.
Fullproofandcounterhypotheses:serving-tuning-10/next-evidence/PLAN.md.
SingleTP8reviewmustexpectoneprefill/onewarmuppair. CodexautopilotOFF.

## Chú ý: tiết kiệm credit và thời gian — 2026-10-17 09:25 UTC

Chỉ đạo người dùng: research phải đi cùng phân tích output các lượt trước để quyết định job tiếp theo. Không submit chỉ để lấp queue hoặc chạy hết biến thể một cách mù quáng.

- Trước mỗi job, đọc kết quả liên quan: raw benchmark, goodput/SLA/TTFT/ITL, errors/cancellations, output quality, runtime/backend thực, startup, GPU trace và phí đã dùng. Giữ cả kết quả âm; job exit0 không tự chứng minh benchmark/quality đạt.
- Kết hợp dữ liệu đó với tài liệu/source chính thức: ghi giả thuyết, bằng chứng ủng hộ, điều còn chưa biết, cấu hình/control cần so và điều kiện dừng. Không dùng research bên ngoài thay bằng chứng chạy thực tế.
- Mỗi allocation phải trả lời một câu hỏi có ích. Ưu tiên phép thử có khả năng đổi quyết định và giá trị thông tin cao so với SU/thời gian; lặp để xác nhận gain nhỏ hoặc frontier khi cần, không lặp mặc định hoặc bỏ qua biến thiên.
- Tận dụng startup đã trả phí để đo vài điểm full protocol trong cùng job nếu walltime cho phép; dừng tăng tải khi fail. Không rút ngắn protocol hoặc bỏ quality gate để tiết kiệm credit rồi báo thành kết quả đầy đủ.
- Đối chiếu chéo hai server khi cùng model/config/protocol/tải. Chỉ dùng kết quả bên kia để định hướng giả thuyết; không mặc định gain chuyển được qua GPU khác. Estimate phải tách khỏi measurement, có sai số/giới hạn và holdout khi cần.
- Trước submit: đối soát queue/credit/accounting, dự trù phí tối đa và budget còn lại; chuẩn bị sẵn payload/control để gửi khi đủ bằng chứng. Song song hai cluster khi có câu hỏi độc lập hữu ích và đủ budget; không chi credit chỉ để giữ cả hai queue bận.
- Khi bằng chứng cho thấy nhánh kém, đã bão hòa hoặc không đủ budget, đóng nhánh và ghi lý do. Chuyển sang phân tích log/source/trace hoặc chuẩn bị CPU có mục đích; không mở thêm job tùy tiện.

Yêu cầu tận dụng hai server được hiểu theo nguyên tắc này. Không tăng budget ngầm, không bật lại Codex autopilot.

## Two-cluster direction — 2026-10-17 09:20 UTC

User requests useful submissions on BOTH H200/Slurm and H100/PBS to reduceelapsed
researchtime. Respectexistingcaps;H100847.075SUremainingdoesnotfitknownstartup+
fullbenchmark. Noimplicitcapincrease orCodexautopilotre-enable.

## Latest 2026-10-17 09:01 UTC

AllPBSreservesreconciled,847.075SUactualremaining;noadditionalbenchmarkfits
knownstartup. H20024263profilequeued;N58plateau,noN60. CodexautopilotOFF.
Evidence:nscc-pbs/inspection/manual-20261017-0858/.

## Latestbudget 2026-10-17 07:30 UTC

22105840minreplicationqueuedafter221052;headroom116.051SU. NoadditionalH100
allocationuntilactualchargesreconciled. CodexautopilotOFF.

## Latest bounded continuation — 2026-10-17 06:52 UTC

GPUresearchcontinueswithoutreminders,AIautopilotOFF. H20024235/24236;
H100221051→221052;budgetheadroom824.319SUafterreserves. OldnoN58is
historical;newpassingN56supportsexactlyoneN58probe,noN60.
Plan/evidence:nscc-pbs/inspection/manual-20261017-0650/PLAN.md.

## Latest manual GPU direction — 2026-10-17 02:24 UTC

User explicitly says keep useful GPU submissions moving within budget/gates;
do not wait for a reminder after each result. Codex autopilot remains OFF.
H20024189/24190 and H100221020→221021 submitted. Updated plan/evidence:
nscc-pbs/inspection/manual-20261017-next/PLAN.md. Remaining campaignheadroom
2713.599SU after current maxreserves. Earlier noN56 is historical, superseded
by the bounded evidence-based N56 plan after two passing N54 runs.

## Codex autopilot đã tắt — 2026-10-16 13:42:29 UTC

Theo yêu cầu người dùng: dừng tự gọi Codex để giảm tiêu hao quota.
Đã gỡ cron `ap42-qwen-autopilot`, tạo `PAUSED`, xóa trigger `FORCE` nếu có.
Không tự bật lại, tạo lịch thay thế hoặc gọi Codex nền nếu chưa được yêu cầu rõ ràng.
Giữ nguyên VPN, job GPU đã gửi và watcher Slurm không gọi AI.
Các hướng dẫn tự chạy bên dưới chỉ là lịch sử; không phải quyền tiếp tục autopilot.

# APAC research policy — compact,16Oct2026

Read notes/README.md,notes/CURRENT.md and relevant plan. Do not read full HISTORY,
archived handoffs,allrunlogs or unchangedseals routinely. Currentstatefiles must
stay concise (CURRENT<=120lines,POLICY<=100lines); archive full history separately.
Never prepend prior CURRENT to itself. Append chronological events to HISTORY.

User authorizes ongoing Qwen research/measure/decide/submit without reminders.
Maintain Slurmwatcher (PIDfile serving-tuning/watcher.pid),cap5 incluntrackedjobs;
never duplicate watcher or cancelPrioritypendingjobs just to requeue.
GPUwork only on compute;CPUstaging<=4threads. No subagents,nestedCodex,
new schedules,externalmessages,BTCuploads orsubmission/slidechanges.

NSCC existingVPN/SSH restored13:23UTC using persistenttmux. Keep it;do not
restart,authenticate orDUO unlessuserexplicitlyasks. SavedSAprivatecache is
sensitive: don't read/copy blobs orcredentials into notes. Private metadatacount
is evidence of persistence,not guarantee24h/serverexpiry recovery.

NSCC project59010042, rate128SU/GPU-hour. Campaign16384SUtotal includingprevious
usage,retain13000SUprojectbalance. At most16GPUsallocated simultaneously,
max45min/job=1536SUreserve. Up to3pending/running jobs ONLY with verified
sequentialafterany chain,max1running. Use nscc-budget.json+budget.lock;reconcile
ownjobstates,ledger,InDoubt beforeqsub; pre-reserve maxcharge,recordjobIDimmediately,
keepuncertainoutcomes untilreconciled. Never subtract InDoubtprepaymenttwice.
Already queued220720→220721→220722; inspect them before ANY duplicate/newtrial.
Pilot04/05/06 are independentvscontrol220575; afterany means end,not success.
Failureofonebackenddoesn't automaticallyinvalidate independentothers. If common
infrastructure failure,investigate before spending more. No blind retry loops.

Follow serving-tuning-10/PLAN.md and nscc-pbs/continuous-plan.json.
Fullrankedprotocol60warmup/120measure/30grace,4000input/200output,closedloop,
SLA TTFT<=3000ms andmeanITL<=20ms,>=90%requests inclerrorsdenominator.
Use AIPerfexportgoodput,not own divisionby120. Singlepeak isn't reproducedgain.
ModelofficialFP8,keeparchitecture/experts/layers. Samehardware/load/matchedcontrol
forclaims;smoke/longretrieval aren't organiser99%accuracy. No falseaccuracyclaims.

H200wave10:combo23904/23973 observed2631.09/2632.06;freshcontrol23974 andsecond
repeat23975+longstillneeded. Require eachcombo fullprotocol,SLA>=90%,0errors/cancel,
no newshortoutputfailures,eachbeatsfreshcontrol andmeanbeatscontrolmean before
reproducedgain. ComboN54plan only if eachcomboSLA>=95%,ITL<=19.3ms andlongPASSED;
missing/deferred/failedlong blocks that gate. MNNVLrepeat24009 doesn'twaiveit.
Do not blindN56,thirdsuccessfulMNNVLrepeat,or promotecontestcandidate.

Eachwake: read compactstate;check actualqueues/access;identify a NEW actionable
job event or one useful researchstep;perform it andsaveevidence,write shortreport.
Reviewer/audit only once per immutableterminalseal unlessnewfailure/concern justifies
it. Don't re-audit everypendingpoll or prepare dozens ofmocktestsforidleturns.
Whenjobsmerelypendingandnothingnew,finish promptlywithonebriefrecord;nohistorydump.
Use precise rgqueries/limitedlinewindows,notcatwholegrowingnotes/logs.
Keep allrawartifact/history on disk; retrieval whenneeded,noteverywake.

Cronchecks every5min withoutmodel. snapshot ignoresreason/timing/metadatachanges;
realjobstate/completion/accesschanges orFORCE/6hmayinvokeCLI. Quotaerrorsbackoff30min.
SameChatGPTCLIaccountconsumesCodexallowance;GPUSUare separate. No modelchange
was made by quotaoptimization.20minmax eachwake is an upperbound,notatarget.

Reports:conciseVietnameseLATEST.md andappendHISTORY;rewriteCURRENTwithcurrent
facts+links only. Knowledge Q&A andDECISIONSget durable additions,not wholechat.
Current chatnot auto-woken/notified; new CLIruns usefilehandoff,notforks.

H100220720 first terminal sweep reviewed13:36UTC; do not rerun unchangedseal.
Runtime8rank unresolved(emptyrolelogs); no promotion. Next220721 sealedfirstreview,
then complete interrupted220722collection/review. Budgetreconciled13:27UTC;
headroom10721.279SU is not a waiver ofruntime/quality/newqsubgates.
