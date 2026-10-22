# Current serving comparison — 22 October 2026

Recorded 2026-10-22T00:38:21.898834+00:00. This section supersedes older dated snapshots below; queue and credit claims in those sections are historical. Live state belongs to the scheduler and current AI handoff.

| Hardware / job | Client concurrency | Good output tokens/s | Joint SLA fraction | Errors | Assessment |
|---|---:|---:|---:|---:|---|
| H200 full 25366 | 64 | 3044.489701 | 98.633018% | 0 | Highest accepted single local point; independent repeat pending |
| H200 full 25365 | 62 | 3011.875113 | 98.722725% | 0 | Fresh matched-observer control; N64 gains 1.082867% |
| H200 full 24962 | 62 | 3023.072304 | 98.726790% | 0 | Prior reproduced observer-off point; paired source 24915=3022.034919 |
| H100 full 222048 | 54 | 2433.019859 | Local pass | 0 | Separate hardware incumbent; no H100-to-H200 score conversion |

Score is exported AIPerf Goodput in requests/s multiplied by 200, reported as good output tokens/s. Joint SLA counts a request only if TTFT is at most 3000 ms and its mean ITL is at most 20 ms; at least 90% of all scored requests, including errors in the denominator, must pass. Full points retain 60-second warmup, 120-second measurement and 30-second grace, fixed nominal 4000/200 workload, cold prefixes and seed 2026. Local pass does not establish official >=99% reference accuracy, which remains unverified.

N64 retains two TP4 DeepGEMM/chunk8192 prefills and TP8/EP8 HPC-Ops decode, native BF16 KV, FP8 target, FlashInfer/MNNVL, dense decode graph batches 1–64 and matched resource observation. Its 26 TTFT breaches all start within 33.481316 ms of scoring; there are no ITL breaches or scored errors/cancellations. The fixed export has 1898 output-length counters at 200, three at 199 and one at 198; actual generated output IDs were not retained for these performance records. Keep the official Goodput × 200 calculation unchanged.

[Full N64 review](research-review-25366-20261022/REVIEW.md), [matched telemetry and tail inspection](research-review-25366-20261022/observability.md), and [initial-cohort analysis](phase-transition-review-20261022/REVIEW.md) retain controls, units, source artifacts and limits. Full 25373 independently repeats N64; short/unranked 25371 explores N64→N68. No new result exists for those submissions at this record. The submission primary remains reviewed N62 until replication review.

Close unchanged both-HPC8192 and power_of_two losses; locality is diagnostic. Withhold P12/D4 pending bounded actual equal-TP NIXL whole-pool setup and reviewer support. A native H200 EAGLE3 correctness route is planned, not submitted or proven faster. [Current AI handoff](/home/apacsc42/workspace/notes/AI_CURRENT.md), [complete research journal](/home/apacsc42/workspace/reports/research-journey-20261019/journal/README.md).

---

# Historical serving records

## Reverse confirmation submitted — 2026-10-20T14:06:36.113310+00:00

222419→ 222420 is the reversed read/off pair after static probe 222412, max2048SU, exact serving/scoring retained. First pair full local PASS and18.737% lower scheduler-reported walltime with-0.659% goodput, different nodes/cache state; no causal or peak claim. Costs963.129SU reconcile, Used 41235.624 SU, Balance 22757.976 SU, In Doubt 6.4 SU, internal headroom 7709.976 SU after new reserve. Four H200 model positions remain Priority-pending. Read the concise CURRENT and linked full reports for units, gates and limits. Older snapshots below are historical.

## First prefetch cost signal accepted locally — 2026-10-20T13:59:49.446440+00:00

H100 222407/222408 full local serving and startup gates PASS. Prefetch readiness 436 s versus 602 s, allocation 759 s versus 934 s (-18.737%, estimated 99.556 SU saving), goodput 2395.929777 versus 2411.827128 (-0.659%). Exact receipts, native runtime/output/tails, 16 diagnostic traces and scored hardware/server evidence inspected. Nodes differ and initial cache residency is unknown; one reverse-order confirmation is justified, not a new scoring winner. [Full review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/PAIR_REVIEW.md). Static locality probe 222412 is active at last query; model peaks unchanged, official accuracy unverified. Preserve both 1024 SU maxima plus 6.4 SU static probe until fresh ledger reconciliation; no new followup receipt yet. Earlier running/pending snapshots are historical.

## Prefetch control accepted; static locality probe queued — 2026-10-20T13:55:03.119475+00:00

H100 control 222407 passes at 2411.827128 good output tokens/s; topology-script-to-ready 602 s, allocated 934 s, estimated 531.342222 SU not posted. Candidate 222408 was running at the 13:53 UTC check; both live prefetch receipts complete in 27.527/27.290 s, no accepted candidate score or saving yet. Static topology job 222412 is held after 222408, one H100/three minutes/max 6.4 SU, no model loaded. [Static probe, definite receipt and local bookkeeping correction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/cpu-gpu-locality-20261020/RESULTS.md), [control full inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/CONTROL_REVIEW.md).

Latest recorded Used 40272.495 SU, Balance 22703.505 SU, In Doubt 1024 SU; control charge still unposted, retain both 1024 SU maxima plus 6.4 SU probe, conservative internal headroom 8673.105 SU under 51000 cap/13000 buffer. Four H200 model jobs 24928/24962/24964/24965 still Priority-pending at query; positions preserved. Peaks unchanged, organiser full-set accuracy unverified. No package, auth or background AI change. Older snapshots below are historical.

## Prefetch control reviewed; candidate running — 2026-10-20T13:51:04.547728+00:00

H100 222407 full local PASS at 2411.827128 good output tokens/s, 98.285% qualifying, zero errors. Topology-script-to-ready 602 s, allocation 934 s, estimated 531.342222 SU unposted. Native off receipts pass both nodes; all 16 diagnostic traces and matched scored hardware/server/tail evidence inspected. Candidate 222408 running; live read receipts complete in 27.527/27.290 s per node, no terminal saving claim. H200 24928/24962/24964/24965 still Priority-pending. [Control review and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/CONTROL_REVIEW.md). Published Used 40272.495 SU unchanged, Balance 22703.505 SU, In Doubt 1024 SU; retain both maximum reservations, internal headroom 8679.505 SU. Peaks unchanged, official accuracy unverified. Earlier scheduler/credit snapshots below are historical.

## Priorities updated and startup-cost pair submitted — 2026-10-20T13:28:06.162122+00:00

Keep the current PD architecture and measured settings; prioritise repeatability/rebuild, then lower iteration cost and profile-supported distinct changes. Latest H100 chunk 2048 loses 26.1328%, retain 4096; H200 25020 passes 256 kernel cases but yields no consistent useful provider alternative. [Updated research priorities](../reports/research-priorities-20261020/PLAN.md).

New H100 **222407 R → 222408 H**, verified serial node-prefetch off/on pair at fixed 4096/N54/round-robin. Workers, official scoring, output checks, transport, observation and profiles are unchanged. Each 16 H100/30 min/max 1024 SU, total 2048 SU reserved after fresh empty queue/credit check. Pre-submit Used 40272.495 SU, Balance 23727.505 SU, In Doubt 0; internal headroom 8679.505 SU under unchanged 51000 cap/13000 buffer. No result yet. [Exact bounded hypothesis, cache-state limits, fixtures and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/startup-prefetch-20261020/RESULTS.md). Four H200 model positions 24928/24962/24964/24965 remain pending and untouched; no blind fifth job. Model peaks unchanged; official full-set accuracy still unverified. No submission package, auth or background AI change. Earlier scheduler/credit snapshots below are historical.

## Latest terminal reviews — 2026-10-20T13:22:09.369531+00:00

H100 222382/222383 full local PASS: chunk 2048 loses 26.1328% (2396.779396→1770.433299 good output tokens/s); TTFT grows 746.849→2039.078 ms, keep 4096. All tails, exact derived graph/runtime/output gates, 16 diagnostic traces and matched scored hardware/server samples reviewed; official accuracy remains unverified. H200 25020 passes 256 kernel cases and the actual /work-bind repair; retain DeepGEMM, no useful consistent alternative-provider signal. Four H200 model jobs 24928/24962/24964/24965 remain Priority-pending. PBS own queue empty at fresh query; all charges reconcile, Used 40272.495 SU, Balance 23727.505 SU, internal headroom 10727.505 SU before any new reserve. [H100 evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-hpc-smallchunk-20261020/PAIR_REVIEW.md), [H200 evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-homebind-fix-20261020/REVIEW.md). Older scheduler/credit snapshots below are historical.

## Smaller H100 prefill chunks submitted — 2026-10-20T12:06:14.504964+00:00

**H100 222382 R → 222383 H**, verified afterany pair: fresh chunk 4096 control versus chunk 2048 at fixed both-phase HPC-Ops, round-robin routing and N54. All other execution/observation/output/transport paths match accepted 222302. Exact pinned graph generator and negative fixtures validate the expected smaller prefill graph range; actual runtime and performance remain unmeasured. [Plan, receipts, gates and next review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-hpc-smallchunk-20261020/PLAN.md).

Prior routing pair full local PASS but power-of-two loses 4.865% (2396.201520 → 2279.626751 good output tokens/s); retain round-robin. Both charges reconcile. Pre-submit Used 39307.091 SU, Balance 24692.909, In Doubt zero; reserve 3072 SU maximum, internal headroom 8620.909 under unchanged 51000 cap/13000 buffer. H200 four model jobs plus repaired micro 25020 are pending, total five; no model position cancelled. Peaks unchanged, official accuracy unverified. No package, auth or background AI change. Earlier scheduler and credit snapshots below are historical.

## Routing pair reviewed and H200 launcher repaired — 2026-10-20T12:03:19.523895+00:00

H100 222302/222303 full local PASS at 2396.201520/2279.626751 good output tokens/s: power-of-two loses 4.865%; keep round-robin. TTFT rises 315.947 ms despite lower ITL; raw tails, exact native policy, all 16 traces and matched scored hardware/server samples inspected. [Full review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/router-queue-research-20261020/PAIR_REVIEW.md). Reviewer corrected the exact struct-like native enum; policy interval is five seconds, separate from earlier monitoring logs. Published Used 39307.091 SU, Balance 24692.909, In Doubt zero; charges reconcile, internal headroom 11692.909 before next spending.

H200 micro 24990 failed exit 127 in 34 seconds because private HOME hid the script path; no kernel cases. Derived /work bind passes actual scheduler-shell path fixture; replacement **25020 submitted**, one node/eight GPUs/ten minutes. Four model queue positions retained. [Fix and preserved failure](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-homebind-fix-20261020/PLAN.md). Model peaks unchanged; official accuracy unverified. Next prepare the distinct H100 HPC-Ops/chunk2048 interaction, not a repeat of losing routing/8192 settings. No package, auth or background AI changes. Older queue/credit snapshots are historical.

## Native prefill routing pair submitted — 2026-10-20T10:13:13.049729+00:00

H100 **222302 R → 222303 H**, verified serial round_robin/power_of_two at fixed HPC-Ops chunk 4096/N54 with matched observation, all worker/scoring/output/transport paths retained. Native CPU parser/Rust mapping validation and common runtime source/policy guards pass locally; no model result yet. [Full question, source evidence, bounded jobs, gates and review route](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/router-queue-research-20261020/RESULTS.md). Prior chunk pair fully accepted 2401.577649/2382.811874, -0.7814%; retain 4096 and corrected native prefill-graph interpretation. All previous costs reconcile; pre-submit Used 38396.869 SU, pair max 3072 reserved, internal headroom 9531.131 under unchanged 51000 cap/13000 buffer. H200 five jobs still Priority-pending, positions preserved. Model peaks unchanged, official accuracy unverified. No package, auth or background AI change. Earlier scheduler/credit snapshots below are historical.

## Observed H100 chunk pair complete — 2026-10-20T10:06:31.204284+00:00

222281/222282 both fully pass at 2401.577649/2382.811874 good tokens/s: chunk 8192 is −0.7814%, TTFT mean +75.665 ms, ITL mean −0.230 ms. Keep 4096; no useful gain or unchanged repeat. Both have 16 rank traces, verified 16-GPU scored samples and explicit server-gauge/inflight limits. Corrected interpretation: chunk changes native prefill graph range too, while complete decode graphs remain unchanged; strict native derivation and five rejection fixtures pass, original rejection retained. [Full evidence/assessment/next hypothesis](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-prefill-hpc-chunk-interaction-20261020/PAIR_REVIEW.md). Both charges reconcile: Used 38396.869, Balance 25603.131 SU, no In Doubt/maxima, internal headroom 12603.131 under unchanged 51000 cap/13000 buffer. Own PBS queue empty; five H200 jobs still Priority-pending. Prepare supported prefill power_of_two versus fresh round_robin at fixed chunk 4096/N54, no new jobs at this checkpoint. Older live snapshots below are historical; official accuracy still unverified.

## Fresh H100 control accepted — 2026-10-20T09:54:34.952862+00:00

222281 chunk 4096 passes full local gates at **2401.577649 good tokens/s**, joint 98.210736%, zero errors/cancellations, 12/12 long checks. Raw 21 TTFT and 6 ITL breaches, TTFT p99 3452.047 ms, ITL p99 19.072 ms. All 16 diagnostic traces and 16-GPU scored sampler mapping/coverage inspected; stop-profile 500 errors occur after scoring. New phase-bounded gauge reader marks inflight NOT_COLLECTED. **222282 chunk 8192 remains running** at the last scheduler query, no candidate score yet. [Full question/result/assessment/next-decision record](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-prefill-hpc-chunk-interaction-20261020/RESULTS.md). Control estimated 484.124444 SU unposted; published Used 37474.701, balance 24989.299, In Doubt 1536; retain 3072 maxima, internal headroom 10453.299 under unchanged 51000 cap/13000 buffer. H200 five jobs Priority-pending; no new model peak or official accuracy. Earlier running-control snapshots below are historical.

## Matched H100 prefill interaction submitted — 2026-10-20T09:30:58.728352+00:00

**222281 (R) → 222282 (H)**, verified afterany chain, compares both-phase HPC-Ops with prefill chunk 4096/8192 at fixed N54, equally observed. Default dense 132-SM DeepGEMM retained; no micro tweak. Two 16-GPU/45-minute maxima, 3072 SU, one running allocation. The previous 8192 loss used auto prefill and does not settle this interaction. [Exact plan, invariant checks, budget, receipts and review steps](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-prefill-hpc-chunk-interaction-20261020/RESULTS.md). Prior 160-case SM80 screen passes numerics but fails consistent benefit; all raw cases preserved. Serving peaks unchanged; official accuracy unverified. H200 all five still Priority-pending. Published pre-submit Used 37439.430; last micro 35.271111 unposted, retain 170.666667 plus 3072: total 3242.666667 bound, internal headroom 10317.903333 under unchanged 51000 cap/13000 buffer. No package, auth or background AI change. Earlier queue/credit snapshots below are historical.

## Scheduler family closed — 2026-10-20T09:26:13.430145+00:00

222279 passes 160 full cases and actual 132/80 traces, but 80 fails the declared useful-consistency gate: M54 QKV+5.17% versus O-proj+2.40%, other batches mixed. Keep 132 and close tested 80/96/120 budgets without a model tweak. Estimated cost 35.271111 SU pending ledger, retain maximum. [Complete cases, paired ratios, native proof and next model interaction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepgemm-sm80-20261020/RESULTS.md). H100 own queue empty; H200 five jobs still Priority-pending. Next prepare the missing H100 HPC-Ops-prefill/chunk 8192 interaction against fresh 4096 at N54, not a repeat of the old auto-prefill 8192 loss. Serving peaks unchanged. Earlier running/queued snapshots below are historical.

## Geometry-supported 80-SM pilot submitted — 2026-10-20T09:23:02.323548+00:00

H100 **222279.pbs111 R**, one 8-GPU/10-minute screen, fresh 132 versus 80 at the observed QKV tile boundary; no result yet. Prior 222277 passes 240 cases but 120/96 fail consistent 5% gates; keep 132. M54-only SM 96 gain about 2.7% is not a serving gain. H200 five jobs remain Priority-pending, positions preserved. All old charges reconcile; Used 37439.430 SU, new maximum reserve 170.666667, internal headroom 13389.903333 under unchanged 51000 cap/13000 buffer. [Plan, raw-source reasoning, numerical gates, cost and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepgemm-sm80-20261020/RESULTS.md). No model promotion, package edit, authentication restart or background AI. Earlier scheduler/credit snapshots below are historical.

## Native scheduler result — 2026-10-20T09:20:20.459454+00:00

222277 fully passes 240 cases and six actual native traces. Neither 120 nor 96 SMs meets the declared 5% representative threshold: keep 132. SM 96 has a modest M54-only +2.73% QKV/+2.65% O-proj on 8/8 ranks but mixed other batches and M32 O-proj loss 5.99%. Not a serving improvement. [All settings, rank distributions, numerical gates and next geometric hypothesis](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepgemm-sm-screen-20261020/RESULTS.md). Estimated charge 37.262222 SU, ledger reconciled=False; retained maximum 170.666667 SU, internal headroom 13427.165333 under unchanged caps. Own PBS queue empty; five H200 jobs remain pending. Earlier running snapshots below are historical.

## Native scheduler screen submitted — 2026-10-20T09:16:33.708071+00:00

TP4 prefill 222245 passes 160 full cases but default Triton loses all tested ranks/shapes/M. Retain DeepGEMM; no losing model pair. New distinct native DeepGEMM 132/120/96-SM budget screen **222277.pbs111 R**, eight GPUs/ten minutes/maximum 170.667 SU, six-case provider preflight then 240 full cases. No numerical or serving result yet. H200 all five still Priority-pending, positions preserved. Published Used 37402.168 SU with all old charges reconciled; new reserve 170.666667, internal headroom 13427.165333 under unchanged 51000 cap/13000 buffer. [Exact source-backed question, gates and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepgemm-sm-screen-20261020/RESULTS.md). No model promotion, package edit, authentication restart or background AI. Earlier queue/credit snapshots below are historical.

## TP4 prefill screen closed — 2026-10-20T09:11:47.564445+00:00

H100 **222245** passes **160/160 full cases** and eight separate preflight cases. Native Triton loses every tested rank/shape/M; at M8192 QKV takes 57.55% longer and O projection 62.46% longer. Keep DeepGEMM, no full-model Triton pair or unchanged retry. [All raw evidence, units, paired distributions and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-prefill-tp4-20261020/RESULTS.md). Full three-charge delta reconciles 166.116 SU: Used 37402.168, Balance 26597.832, In Doubt 0, outstanding 0, internal headroom 13597.832 under unchanged 51000 cap/13000 buffer. Own PBS queue empty; all five H200 jobs still Priority-pending. No new serving peak or official accuracy. Older queued/running snapshots below are historical.

## Separate TP4 prefill screen submitted — 2026-10-20T08:01:59.878719+00:00

H100 decode 222242 fully passes 256 numerical/timing cases but rejects Triton/FlashInfer as useful replacements; retain DeepGEMM and do not spend on a losing model pair. New distinct **222245.pbs111 Q** screens native linear helpers for TP4 prefill at M512–8192 (eight GPUs/ten minutes/maximum 170.667 SU), after a separate provider preflight; no result yet. H200 24990 plus four model jobs remain Priority-pending, cap five preserved. Published Used 37236.052 SU; two unposted completed charges retain full max bounds plus new max, total 512 SU; internal headroom 13251.948 SU under unchanged 51000 cap/13000 buffer. [Full plan, checks, receipts and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-prefill-tp4-20261020/RESULTS.md). Model bests unchanged; no package, auth or background AI change. Earlier queue/budget snapshots below are historical.

## H100 decode linear screen complete — 2026-10-20T07:58:29.424255+00:00

222242.pbs111 passes all **256/256 full cases** on eight GPUs and ten separate preflight cases; numerical/input/source/config/UUID/trace checks pass. Triton loses every tested rank/shape/M; at M54 QKV takes about twice as long and O projection about 26% longer. Small-M FlashInfer is inconsistent and below the 5% gate; native M>=32 falls back to DeepGEMM. Retain DeepGEMM; no losing full-model pair. Estimated successful screen cost 73.955556 SU remains pending ledger, with its full max reservation retained. H200 24990 and four model jobs remain Priority-pending. [All rank comparisons, units, raw evidence and decision](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-privatehome-20261020/RESULTS.md). This is synthetic TP8 decode evidence, not a serving gain or official accuracy. Earlier queued/running snapshots below are historical.

## Private-home retry submitted — 2026-10-20T07:52:41.504271+00:00

H100 222232 failed after import/source checks with zero kernel cases (TVM/TensorRT home caches). This corrects earlier running/FlashInfer-only snapshots below. Both failures are sealed; estimated total 42.097778 SU, first 20.480 now posted and second pending ledger. New bounded H100 **222242 Q** and H200 **24990 Priority-pending** use private empty writable home plus a separate ten-case one-rank provider preflight. CPU wrapper/filesystem validation passes, full timing/config bytes unchanged, no GPU result yet. Only pending micro 24988 cancelled; four H200 model positions retained, five total. Published Used 37236.052, Balance 26593.281, In Doubt 170.667; conservative bound 341.333333 and campaign headroom 13422.615 SU under unchanged caps. [Full review and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/fp8-privatehome-20261020/RESULTS.md). No new model score, official accuracy, package edit, authentication restart or background AI. Earlier snapshots below retain their dates and are historical.

## Native kernel harness failure and bounded cache repair — 2026-10-20T07:42:45.154303+00:00

H100 222210: exit 1 before measurements, eight identical FlashInfer read-only-cache errors. New cache-only 222232 R /24988 H200 pending, no kernel results yet. Old micro 24983 cancelled before runtime; four model jobs preserved. Failed estimated 20.480 SU unposted, max combined reserve 341.333 and headroom 13443.095, unchanged caps. [Failure](fp8-linear-micro-review-20261020/RESULTS.md), [repair validation/receipts](fp8-linear-cachefix-20261020/RESULTS.md). Experimental config and numerical/timing body unchanged; no successful kernel/model result or official quality claim.

## Closed H100 polling and queued native FP8 kernel screens — 2026-10-20T07:08:09.091840+00:00

222178/222179 full local PASS at 2420.817/2419.693 good tokens/s, +0.0464%; default interval 1 kept, branch closed. New isolated eight-GPU/ten-minute probes 222210 H100 and 24983 H200 are queued, no timings or model score. H100 reserve 170.667 SU, internal headroom 13613.761 under unchanged caps; all old charges reconcile. Five H200 active. [Closed review](research-followup-20261020-0647/RESULTS.md), [new hypothesis, gates and receipts](fp8-linear-micro-20261020/RESULTS.md). Keep microseconds, goodput, numerical diagnostics and official accuracy distinct. No old job canceled or changed, package edit or background AI.

## H100 access, completed review and resumed research — 2026-10-20T06:22:50.124747+00:00

222048/222049/222050 full local PASS at 2433.020/2395.311/2406.802 good tokens/s; observer/poll differences remain unestablished, raw ITL breaches 0/4/5. All separate profiles and dedicated observed hardware samples inspected. Three charges reconcile 1335.751 SU. New serial unobserved interval2/control 222178→222179 is R/H at 06:21:45 UTC, no result yet, max reserve 3072 SU and headroom 11619.806. [Complete review](research-followup-20261020-h100-restored/RESULTS.md), [new plan/receipts](research-followup-20261020-h100-recv-unobserved/RESULTS.md). VPN/SSH restored and left active; no official accuracy, package or background AI change. Prior snapshots remain dated.

## Observer review and fixed-load prefill interaction — 2026-10-20T05:39:23.555756+00:00

H200 24926/24927 both pass full local gates at 2991.709/2971.312 good output tokens/s (N60), a −0.682% single on/off delta. Each has 22 TTFT breaches and no ITL/error/cancel breaches. New resource inspection verifies stable/disjoint 16 GPU UUIDs and 24/24/25 scored-phase samples. GPU activity is not peak FLOPS or bandwidth; host counters are deduplicated and remote clock skew remains uncalibrated. Two separate diagnostics retain 16 traces each. [Full observer review](research-followup-20261020-0530/RESULTS.md).

Submitted **24962** exact N62 repeat, plus **24964** fresh observed DeepGEMM8192/HPC-decode N60 control and **24965** observed HPC-prefill8192/HPC-decode candidate. Existing **24928** receive2 keeps its position. All four are Resources-pending at the retained 05:38 check; no new result yet. [New interaction plan and receipts](research-followup-20261020-prefill-interaction/RESULTS.md). H200 highest remains single 24915 = 3022.035; official quality unverified. No live VPN session, so no PBS output/credit refresh, authentication restart or new SU spending. Previous snapshots retain their dates.

# Qwen serving tuning — next wave

Updated UTC: 2026-10-18T19:24:16.365875+00:00

Control: measured job 22415, TP4 prefill → TP8/EP8 decode, BF16 KV, request-scoped NIXL patch.
Every ranked point uses 60 s warmup, 120 s measurement, 30 s grace. Profiling traffic is separate.
Full results are required; FAILED/TIMEOUT without an export is never a completed benchmark.

| Experiment | Jobs / states | Missing N | Status |
|---|---|---|---|
| control-load | 23102:COMPLETED, 23106:COMPLETED | [] | MEASURED |
| dense-decode-graphs | 23103:COMPLETED, 23109:COMPLETED | [] | MEASURED |
| profile-control | 23104:COMPLETED | [] | MEASURED |
| load-best-repeat | 23113:COMPLETED | [] | MEASURED |
| prefill-chunk4096 | 23114:COMPLETED | [] | MEASURED |
| decode-deepgemm | 23115:COMPLETED | [] | MEASURED |
| s2-control-n52 | 23128:COMPLETED | [] | MEASURED |
| s2-chunk4096-n52 | 23129:COMPLETED | [] | MEASURED |
| s2-chunk4096-dense-n52 | 23130:COMPLETED | [] | MEASURED |
| s2-chunk16384-n52 | 23131:COMPLETED | [] | MEASURED |
| s2-deepgemm-control-n52 | 23264:COMPLETED | [] | MEASURED |
| s2-fp8-kv-n52 | 23265:COMPLETED | [] | MEASURED |
| s2-repeat-best | 23266:COMPLETED | [] | MEASURED |
| s2-repeat-runner | 23267:COMPLETED | [] | MEASURED |
| s2-deepep-ll-n52 | 23272:COMPLETED | [] | MEASURED |
| s3-control-n52 | 23286:COMPLETED | [] | MEASURED |
| s3-best-n54 | 23287:COMPLETED | [] | MEASURED |
| s4-prefill-single-n52 | 23324:COMPLETED | [] | MEASURED |
| s4-prefill-roundrobin-n52 | 23325:COMPLETED | [] | MEASURED |
| s3-best-n56 | 23437:COMPLETED | [] | MEASURED |
| s3-best-n60 | 23495:COMPLETED | [] | MEASURED |
| s3-midpoint | 23505:COMPLETED | [] | MEASURED |
| s3-best-load-repeat | 23516:COMPLETED | [] | MEASURED |
| s5-rr-repeat-n52 | 23576:COMPLETED | [] | MEASURED |
| s5-rr-n50 | 23577:COMPLETED | [] | MEASURED |
| s5-rr-n54 | 23583:COMPLETED | [] | MEASURED |
| s6-rr-profile-n52 | 23607:COMPLETED | [] | MEASURED |
| s6-rr-fp8kv-n52 | 23608:COMPLETED | [] | MEASURED |
| s6-rr-deepgemm-n52 | 23609:COMPLETED | [] | MEASURED |
| s5-rr-midpoint | 23616:COMPLETED | [] | MEASURED |
| s5-rr-best-repeat | 23773:COMPLETED | [] | MEASURED |
| s7-rr-cutlass-n52 | 23776:FAILED | [52] | INCOMPLETE |
| s7-rr-flashinfer-n52 | 23777:COMPLETED | [] | MEASURED |
| s7-rr-mnnvl-n52 | 23778:COMPLETED | [] | MEASURED |
| s8-rr-dpa8-deepep-n52 | 23780:COMPLETED | [] | MEASURED |
| s7-mnnvl-repeat-n52 | 23839:COMPLETED | [] | MEASURED |
| s8-dpa8-repeat-n52 | 23859:COMPLETED | [] | MEASURED |
| s9-mnnvl-flashinfer-n52 | 23904:COMPLETED | [] | MEASURED |
| s9-mnnvl-chunk2048-n52 | 23905:COMPLETED | [] | MEASURED |
| s9-mnnvl-chunk8192-n52 | 23906:COMPLETED | [] | MEASURED |
| s7-mnnvl-n54 | 23924:COMPLETED | [] | MEASURED |
| s8-dpa8-n54 | 23934:COMPLETED | [] | MEASURED |
| s10-combo-repeat1-n52 | 23973:COMPLETED | [] | MEASURED |
| s10-mnnvl-control-n52 | 23974:COMPLETED | [] | MEASURED |
| s10-combo-repeat2-long-n52 | 23975:COMPLETED | [] | MEASURED |
| s10-mnnvl-repeat-n54 | 24009:COMPLETED | [] | MEASURED |
| s10-combo-n54 | 24131:COMPLETED | [] | MEASURED |
| s10-combo-fresh-n52 | 24174:COMPLETED | [] | MEASURED |
| s10-combo-repeat-n54 | 24175:COMPLETED | [] | MEASURED |
| s10-combo-control-n54-v2 | 24189:COMPLETED | [] | MEASURED |
| s10-combo-probe-n56 | 24190:COMPLETED | [] | MEASURED |
| s10-combo-repeat-n56 | 24235:COMPLETED | [] | MEASURED |
| s10-combo-probe-n58 | 24236:COMPLETED | [] | MEASURED |
| s10-combo-profile-n56 | 24263:COMPLETED | [] | MEASURED |
| s10-cross-platform-n50 | 24272:COMPLETED | [] | MEASURED |
| s10-combo-prefill-single-n56 | 24281:COMPLETED | [] | MEASURED |
| s10-combo-prefill-tp8-n56 | 24282:FAILED | [56] | INCOMPLETE |
| s10-prefill-deepgemm-n56 | 24291:COMPLETED | [] | MEASURED |
| s10-combo-control-n56-v3 | 24320:COMPLETED | [] | MEASURED |
| s10-prefill-tp8ep2-n56 | 24321:FAILED | [56] | INCOMPLETE |
| s10-prefill-prefetch-n56 | 24322:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-repeat-n56 | 24327:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-n58 | 24352:COMPLETED | [] | MEASURED |
| s10-prefill-tp8ep2-equal-n56 | 24375:COMPLETED | [] | MEASURED |
| s10-prefill-no-graph-n56 | 24376:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-chunk8192-n56 | 24425:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-no-graph-n56 | 24426:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-n54 | 24428:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-profile-n56 | 24429:COMPLETED | [] | MEASURED |
| s11-dg-control-n56 | 24526:COMPLETED | [] | MEASURED |
| s11-dg-chunk8192-repeat-n56 | 24527:COMPLETED | [] | MEASURED |
| s11-dg-chunk6144-n56 | 24528:COMPLETED | [] | MEASURED |
| s11-hpc-prefill-n56 | 24529:COMPLETED | [] | MEASURED |
| s11-hpc-decode-n56 | 24538:COMPLETED | [] | MEASURED |
| s11-dg-chunk8192-n58 | 24544:COMPLETED | [] | MEASURED |
| s12-dg-chunk6144-repeat-n56 | 24573:COMPLETED | [] | MEASURED |
| s12-hpc-prefill-repeat-n56 | 24574:COMPLETED | [] | MEASURED |
| s12-dg-fresh-control-n56 | 24575:COMPLETED | [] | MEASURED |
| s12-dg-chunk8192-repeat-n58 | 24588:TIMEOUT | [58] | INCOMPLETE |
| s12-dg-fresh-control-n58 | 24589:PENDING | [58] | ACTIVE |
| s13-hpc-decode-n58 | 24639:PENDING | [58] | ACTIVE |
| s13-hpc-prefill-chunk6144-n56 | 24640:PENDING | [56] | ACTIVE |
| s13-hpc-both-n56 | 24641:PENDING | [56] | ACTIVE |

| Job | Experiment | N | Good tokens/s | SLA | TTFT mean ms | ITL mean ms | Errors | Cancelled | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 23102 | control-load | 48 | 1911.08 | 97.46% | 1470.60 | 16.78 | 0 | 0 | PASS |
| 23102 | control-load | 52 | 2096.88 | 98.86% | 1383.15 | 17.27 | 0 | 0 | PASS |
| 23106 | control-load | 56 | 2057.87 | 97.05% | 1813.44 | 16.93 | 0 | 0 | PASS |
| 23103 | dense-decode-graphs | 48 | 1933.05 | 97.47% | 1525.35 | 16.29 | 0 | 0 | PASS |
| 23103 | dense-decode-graphs | 52 | 2123.30 | 98.73% | 1449.42 | 16.61 | 0 | 0 | PASS |
| 23109 | dense-decode-graphs | 56 | 2069.20 | 96.48% | 1837.46 | 16.52 | 0 | 0 | PASS |
| 23104 | profile-control | 48 | 1910.32 | 97.47% | 1470.16 | 16.79 | 0 | 0 | PASS |
| 23113 | load-best-repeat | 52 | 1986.39 | 97.24% | 1633.31 | 16.97 | 0 | 0 | PASS |
| 23114 | prefill-chunk4096 | 48 | 1962.70 | 97.60% | 1245.64 | 17.33 | 0 | 0 | PASS |
| 23114 | prefill-chunk4096 | 52 | 2140.10 | 98.81% | 1173.18 | 17.84 | 0 | 0 | PASS |
| 23115 | decode-deepgemm | 48 | 1904.20 | 97.44% | 1458.15 | 16.97 | 0 | 0 | PASS |
| 23115 | decode-deepgemm | 52 | 2085.67 | 98.78% | 1373.60 | 17.46 | 0 | 0 | PASS |
| 23128 | s2-control-n52 | 52 | 1977.08 | 97.14% | 1639.15 | 17.07 | 0 | 0 | PASS |
| 23129 | s2-chunk4096-n52 | 52 | 2033.03 | 97.39% | 1420.60 | 17.41 | 0 | 0 | PASS |
| 23130 | s2-chunk4096-dense-n52 | 52 | 2078.96 | 97.43% | 1430.49 | 16.93 | 0 | 0 | PASS |
| 23131 | s2-chunk16384-n52 | 52 | 1741.20 | 90.92% | 2147.07 | 16.07 | 0 | 0 | PASS |
| 23264 | s2-deepgemm-control-n52 | 52 | 2018.01 | 97.37% | 1407.68 | 17.67 | 0 | 0 | PASS |
| 23265 | s2-fp8-kv-n52 | 52 | 1996.26 | 97.33% | 1355.69 | 18.27 | 0 | 0 | PASS |
| 23266 | s2-repeat-best | 52 | 2079.18 | 97.43% | 1432.37 | 16.93 | 0 | 0 | PASS |
| 23267 | s2-repeat-runner | 52 | 2032.13 | 97.39% | 1419.36 | 17.42 | 0 | 0 | PASS |
| 23272 | s2-deepep-ll-n52 | 52 | 1957.15 | 96.35% | 1317.64 | 18.71 | 0 | 0 | PASS |
| 23286 | s3-control-n52 | 52 | 2075.11 | 97.42% | 1437.63 | 16.94 | 0 | 0 | PASS |
| 23287 | s3-best-n54 | 54 | 2111.91 | 97.33% | 1517.78 | 16.99 | 0 | 0 | PASS |
| 23324 | s4-prefill-single-n52 | 52 | 2082.09 | 97.44% | 1412.99 | 16.96 | 0 | 0 | PASS |
| 23325 | s4-prefill-roundrobin-n52 | 52 | 2402.64 | 98.93% | 333.25 | 19.57 | 0 | 0 | PASS |
| 23437 | s3-best-n56 | 56 | 2141.20 | 97.22% | 1610.94 | 17.06 | 0 | 0 | PASS |
| 23495 | s3-best-n60 | 60 | 2133.30 | 94.51% | 1780.49 | 17.35 | 0 | 0 | PASS |
| 23505 | s3-midpoint | 58 | 2157.31 | 96.76% | 1687.40 | 17.20 | 0 | 0 | PASS |
| 23516 | s3-best-load-repeat | 58 | 2159.79 | 96.83% | 1691.06 | 17.19 | 0 | 0 | PASS |
| 23576 | s5-rr-repeat-n52 | 52 | 2397.72 | 98.93% | 365.29 | 19.46 | 0 | 0 | PASS |
| 23577 | s5-rr-n50 | 50 | 2350.25 | 99.04% | 335.48 | 19.23 | 0 | 0 | PASS |
| 23583 | s5-rr-n54 | 54 | 2358.64 | 95.34% | 428.19 | 19.51 | 0 | 0 | PASS |
| 23607 | s6-rr-profile-n52 | 52 | 2400.02 | 98.93% | 346.84 | 19.52 | 0 | 0 | PASS |
| 23608 | s6-rr-fp8kv-n52 | 52 | 254.47 | 10.75% | 342.90 | 20.07 | 0 | 0 | FAIL / incomplete |
| 23609 | s6-rr-deepgemm-n52 | 52 | 2021.39 | 84.71% | 394.50 | 19.63 | 0 | 0 | FAIL / incomplete |
| 23616 | s5-rr-midpoint | 53 | 2433.41 | 98.88% | 339.35 | 19.66 | 0 | 0 | PASS |
| 23773 | s5-rr-best-repeat | 53 | 2438.47 | 98.88% | 328.90 | 19.67 | 0 | 0 | PASS |
| 23777 | s7-rr-flashinfer-n52 | 52 | 2440.39 | 98.95% | 438.05 | 18.71 | 0 | 0 | PASS |
| 23778 | s7-rr-mnnvl-n52 | 52 | 2592.16 | 99.01% | 516.28 | 17.13 | 0 | 0 | PASS |
| 23780 | s8-rr-dpa8-deepep-n52 | 52 | 2549.20 | 98.87% | 596.44 | 16.96 | 0 | 0 | PASS |
| 23839 | s7-mnnvl-repeat-n52 | 52 | 2592.92 | 99.01% | 508.25 | 17.15 | 0 | 0 | PASS |
| 23859 | s8-dpa8-repeat-n52 | 52 | 2538.08 | 98.87% | 617.14 | 16.96 | 0 | 0 | PASS |
| 23904 | s9-mnnvl-flashinfer-n52 | 52 | 2631.09 | 99.02% | 635.23 | 16.23 | 0 | 0 | PASS |
| 23905 | s9-mnnvl-chunk2048-n52 | 52 | 2331.35 | 98.77% | 1188.77 | 15.81 | 0 | 0 | PASS |
| 23906 | s9-mnnvl-chunk8192-n52 | 52 | 2547.85 | 98.87% | 735.56 | 16.32 | 0 | 0 | PASS |
| 23924 | s7-mnnvl-n54 | 54 | 2634.03 | 98.90% | 600.44 | 17.11 | 0 | 0 | PASS |
| 23934 | s8-dpa8-n54 | 54 | 2555.42 | 98.75% | 751.99 | 16.89 | 0 | 0 | PASS |
| 23973 | s10-combo-repeat1-n52 | 52 | 2632.06 | 99.02% | 632.66 | 16.24 | 0 | 0 | PASS |
| 23974 | s10-mnnvl-control-n52 | 52 | 2594.03 | 99.01% | 518.90 | 17.09 | 0 | 0 | PASS |
| 23975 | s10-combo-repeat2-long-n52 | 52 | 2632.61 | 99.02% | 634.42 | 16.23 | 0 | 0 | PASS |
| 24009 | s10-mnnvl-repeat-n54 | 54 | 2629.51 | 98.90% | 615.90 | 17.06 | 0 | 0 | PASS |
| 24131 | s10-combo-n54 | 54 | 2654.17 | 98.91% | 736.69 | 16.27 | 0 | 0 | PASS |
| 24174 | s10-combo-fresh-n52 | 52 | 2632.96 | 99.02% | 637.78 | 16.21 | 0 | 0 | PASS |
| 24175 | s10-combo-repeat-n54 | 54 | 2658.20 | 98.91% | 734.65 | 16.25 | 0 | 0 | PASS |
| 24189 | s10-combo-control-n54-v2 | 54 | 2658.55 | 98.91% | 739.13 | 16.23 | 0 | 0 | PASS |
| 24190 | s10-combo-probe-n56 | 56 | 2671.11 | 98.80% | 847.85 | 16.29 | 0 | 0 | PASS |
| 24235 | s10-combo-repeat-n56 | 56 | 2669.80 | 98.80% | 852.28 | 16.26 | 0 | 0 | PASS |
| 24236 | s10-combo-probe-n58 | 58 | 2667.97 | 98.68% | 991.14 | 16.27 | 0 | 0 | PASS |
| 24263 | s10-combo-profile-n56 | 56 | 2667.46 | 98.80% | 856.62 | 16.26 | 0 | 0 | PASS |
| 24272 | s10-cross-platform-n50 | 50 | 2601.63 | 99.13% | 505.18 | 16.37 | 0 | 0 | PASS |
| 24281 | s10-combo-prefill-single-n56 | 56 | 2621.29 | 98.78% | 936.61 | 16.19 | 0 | 0 | PASS |
| 24291 | s10-prefill-deepgemm-n56 | 56 | 2715.84 | 98.82% | 749.05 | 16.45 | 0 | 0 | PASS |
| 24320 | s10-combo-control-n56-v3 | 56 | 2670.32 | 98.80% | 851.83 | 16.27 | 0 | 0 | PASS |
| 24322 | s10-prefill-prefetch-n56 | 56 | 2665.57 | 98.80% | 859.13 | 16.26 | 0 | 0 | PASS |
| 24327 | s10-prefill-deepgemm-repeat-n56 | 56 | 2716.79 | 98.82% | 748.99 | 16.45 | 0 | 0 | PASS |
| 24352 | s10-prefill-deepgemm-n58 | 58 | 2718.08 | 98.71% | 872.26 | 16.49 | 0 | 0 | PASS |
| 24375 | s10-prefill-tp8ep2-equal-n56 | 56 | 28.33 | 2.00% | 5013.77 | 16.56 | 0 | 0 | FAIL / incomplete |
| 24376 | s10-prefill-no-graph-n56 | 56 | 2530.83 | 98.43% | 1079.94 | 16.07 | 0 | 0 | PASS |
| 24425 | s10-prefill-deepgemm-chunk8192-n56 | 56 | 2722.28 | 98.94% | 755.65 | 16.40 | 0 | 0 | PASS |
| 24426 | s10-prefill-deepgemm-no-graph-n56 | 56 | 1590.31 | 72.72% | 1998.40 | 15.09 | 0 | 0 | FAIL / incomplete |
| 24428 | s10-prefill-deepgemm-n54 | 54 | 2693.16 | 98.93% | 661.67 | 16.35 | 0 | 0 | PASS |
| 24429 | s10-prefill-deepgemm-profile-n56 | 56 | 2715.55 | 98.82% | 741.42 | 16.49 | 0 | 0 | PASS |
| 24526 | s11-dg-control-n56 | 56 | 2715.83 | 98.82% | 751.28 | 16.44 | 0 | 0 | PASS |
| 24527 | s11-dg-chunk8192-repeat-n56 | 56 | 2718.69 | 98.94% | 770.05 | 16.37 | 0 | 0 | PASS |
| 24528 | s11-dg-chunk6144-n56 | 56 | 2737.01 | 98.94% | 720.38 | 16.48 | 0 | 0 | PASS |
| 24529 | s11-hpc-prefill-n56 | 56 | 2732.46 | 98.94% | 715.07 | 16.53 | 0 | 0 | PASS |
| 24538 | s11-hpc-decode-n56 | 56 | 2733.20 | 98.83% | 1037.10 | 14.86 | 0 | 0 | PASS |
| 24544 | s11-dg-chunk8192-n58 | 58 | 2786.70 | 98.85% | 774.06 | 16.51 | 0 | 0 | PASS |
| 24573 | s12-dg-chunk6144-repeat-n56 | 56 | 2737.41 | 98.94% | 717.26 | 16.47 | 0 | 0 | PASS |
| 24574 | s12-hpc-prefill-repeat-n56 | 56 | 2728.96 | 98.82% | 714.98 | 16.54 | 0 | 0 | PASS |
| 24575 | s12-dg-fresh-control-n56 | 56 | 2714.10 | 98.82% | 750.64 | 16.46 | 0 | 0 | PASS |

## Backend pilots

| Pilot | Matched control | State | Job |
|---|---|---|---|
| s2-deepgemm-control-n52 | s2-chunk4096-n52 | MEASURED | 23264 |
| s2-deepep-ll-n52 | s2-deepgemm-control-n52 | MEASURED | 23272 |
| s2-fp8-kv-n52 | s2-chunk4096-n52 | MEASURED | 23265 |

## Load refinement

| Trial | N | State | Job |
|---|---:|---|---|
| s3-control-n52 | 52 | MEASURED | 23286 |
| s3-best-n54 | 54 | MEASURED | 23287 |
| s3-best-n56 | 56 | MEASURED | 23437 |
| s3-best-n60 | 60 | MEASURED | 23495 |
| s3-midpoint | 58 | MEASURED | 23505 |
| s3-best-load-repeat | 58 | MEASURED | 23516 |

## Prefill routing/admission pilots

| Trial | State | Job |
|---|---|---|
| s4-prefill-single-n52 | MEASURED | 23324 |
| s4-prefill-roundrobin-n52 | MEASURED | 23325 |

[Research and measured TTFT failure analysis](serving-tuning-04/RESEARCH.md). Same N52 benchmark, one prefill factor per pilot.

## Round-robin confirmation and load refinement

| Trial | N | State | Job |
|---|---:|---|---|
| s5-rr-repeat-n52 | 52 | MEASURED | 23576 |
| s5-rr-n50 | 50 | MEASURED | 23577 |
| s5-rr-n54 | 54 | MEASURED | 23583 |
| s5-rr-midpoint | 53 | MEASURED | 23616 |
| s5-rr-best-repeat | 53 | MEASURED | 23773 |

## Round-robin backend/profile experiments

| Trial | State | Job |
|---|---|---|
| s6-rr-profile-n52 | MEASURED | 23607 |
| s6-rr-fp8kv-n52 | MEASURED | 23608 |
| s6-rr-deepgemm-n52 | MEASURED | 23609 |

## Backend follow-ups

| Trial | State | Job |
|---|---|---|
| s6-fp8kv-repeat-n52 | SKIPPED_NO_VALIDATED_GAIN | — |
| s6-fp8kv-n54 | SKIPPED_NO_REPEAT | — |
| s6-deepgemm-repeat-n52 | SKIPPED_NO_VALIDATED_GAIN | — |
| s6-deepgemm-n54 | SKIPPED_NO_REPEAT | — |

## MNNVL + FlashInfer replication

| Trial | State | Job |
|---|---|---|
| s10-combo-repeat1-n52 | MEASURED | 23973 |
| s10-mnnvl-control-n52 | MEASURED | 23974 |
| s10-combo-repeat2-long-n52 | MEASURED | 23975 |
| s10-mnnvl-repeat-n54 | MEASURED | 24009 |
| s10-combo-n54 | MEASURED | 24131 |
| s10-combo-fresh-n52 | MEASURED | 24174 |
| s10-combo-repeat-n54 | MEASURED | 24175 |
| s10-combo-control-n54-v2 | MEASURED | 24189 |
| s10-combo-probe-n56 | MEASURED | 24190 |
| s10-combo-repeat-n56 | MEASURED | 24235 |
| s10-combo-probe-n58 | MEASURED | 24236 |
| s10-combo-profile-n56 | MEASURED | 24263 |
| s10-cross-platform-n50 | MEASURED | 24272 |
| s10-combo-prefill-single-n56 | MEASURED | 24281 |
| s10-combo-prefill-tp8-n56 | INCOMPLETE | 24282 |
| s10-prefill-deepgemm-n56 | MEASURED | 24291 |
| s10-combo-control-n56-v3 | MEASURED | 24320 |
| s10-prefill-tp8ep2-n56 | INCOMPLETE | 24321 |
| s10-prefill-prefetch-n56 | MEASURED | 24322 |
| s10-prefill-deepgemm-repeat-n56 | MEASURED | 24327 |
| s10-prefill-deepgemm-n58 | MEASURED | 24352 |
| s10-prefill-tp8ep2-equal-n56 | MEASURED | 24375 |
| s10-prefill-no-graph-n56 | MEASURED | 24376 |
| s10-prefill-deepgemm-chunk8192-n56 | MEASURED | 24425 |
| s10-prefill-deepgemm-no-graph-n56 | MEASURED | 24426 |
| s10-prefill-deepgemm-n54 | MEASURED | 24428 |
| s10-prefill-deepgemm-profile-n56 | MEASURED | 24429 |
| s11-dg-control-n56 | MEASURED | 24526 |
| s11-dg-chunk8192-repeat-n56 | MEASURED | 24527 |
| s11-dg-chunk6144-n56 | MEASURED | 24528 |
| s11-hpc-prefill-n56 | MEASURED | 24529 |
| s11-hpc-decode-n56 | MEASURED | 24538 |
| s11-dg-chunk8192-n58 | MEASURED | 24544 |
| s12-dg-chunk6144-repeat-n56 | MEASURED | 24573 |
| s12-hpc-prefill-repeat-n56 | MEASURED | 24574 |
| s12-dg-fresh-control-n56 | MEASURED | 24575 |
| s12-dg-chunk8192-repeat-n58 | ACTIVE | 24588 |
| s12-dg-fresh-control-n58 | ACTIVE | 24589 |
| s13-hpc-decode-n58 | SUBMITTED | 24639 |
| s13-hpc-prefill-chunk6144-n56 | SUBMITTED | 24640 |
| s13-hpc-both-n56 | SUBMITTED | 24641 |

## MNNVL interaction pilots

| Trial | State | Job |
|---|---|---|
| s9-mnnvl-flashinfer-n52 | MEASURED | 23904 |
| s9-mnnvl-chunk2048-n52 | MEASURED | 23905 |
| s9-mnnvl-chunk8192-n52 | MEASURED | 23906 |

## DP-attention architecture pilot

| Trial | State | Job |
|---|---|---|
| s8-rr-dpa8-deepep-n52 | MEASURED | 23780 |

## DP-attention architecture follow-ups

| Trial | State | Job |
|---|---|---|
| s8-dpa8-repeat-n52 | MEASURED | 23859 |
| s8-dpa8-n54 | MEASURED | 23934 |

## Profile-guided decode kernels

| Trial | State | Job |
|---|---|---|
| s7-rr-cutlass-n52 | INCOMPLETE | 23776 |
| s7-rr-flashinfer-n52 | MEASURED | 23777 |
| s7-rr-mnnvl-n52 | MEASURED | 23778 |

## Profile-guided kernel follow-ups

| Trial | State | Job |
|---|---|---|
| s7-cutlass-repeat-n52 | SKIPPED_NO_VALIDATED_GAIN | — |
| s7-cutlass-n54 | SKIPPED_NO_REPEAT | — |
| s7-flashinfer-repeat-n52 | SKIPPED_NO_VALIDATED_GAIN | — |
| s7-flashinfer-n54 | SKIPPED_NO_REPEAT | — |
| s7-mnnvl-repeat-n52 | MEASURED | 23839 |
| s7-mnnvl-n54 | MEASURED | 23924 |

## Interpretation

Dense graph N48 versus mean of 2 new N48 controls: +1.17%. One candidate run remains provisional; repeated confirmation is needed before promotion.
Highest new load point: N52, 2096.88 good tokens/s, 98.86% SLA (+9.65% versus job 22415). Provisional until independently repeated; the submission is unchanged.
Highest single full measurement: s11-dg-chunk8192-n58 / job 24544 / N58: 2786.70 good tokens/s, 98.85% SLA. Backend/FP8 quality remains unverified; the largest single run is not automatically the final configuration.
Repeated BF16 chunk4096/dense-graph candidate at N52: 2079.07 mean good tokens/s across jobs 23130, 23266 (range 2078.96–2079.18). Two deployments agree closely; this does not establish accuracy or variability under all cluster conditions.
Round-robin prefill pilot / job 23325: 2402.64 good tokens/s, 98.93% SLA, mean TTFT 333.25ms and ITL 19.57ms. ITL is close to its20ms limit; independent confirmation and a lower-load comparison are required before selection.

Standalone measurements above begin directly at their listed concurrency; they do not run a lower-load benchmark first.
Job 23128 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23129 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23130 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23131 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23264 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23265 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23266 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23267 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23272 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23286 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23287 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23324 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23325 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23437 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23495 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23505 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23516 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23576 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23577 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23583 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23616 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23773 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.

## Traces

profile-control: 16 trace files; kernel summaries are beside the traces. Summed GPU time is not wall-time speedup.
s6-rr-profile-n52: 16 trace files; kernel summaries are beside the traces. Summed GPU time is not wall-time speedup.
s10-combo-profile-n56: 16 trace files; kernel summaries are beside the traces. Summed GPU time is not wall-time speedup.
s10-prefill-deepgemm-profile-n56: 16 trace files; kernel summaries are beside the traces. Summed GPU time is not wall-time speedup.

## Next steps

- Prefill chunk 4096/16384 after control.
- MoE runner after profiler identifies compute cost.
- Expert communication after profiler identifies dispatch/collective cost.
- FP8 KV with separate quality check.
- Engine comparison after reproducible current-stack baseline.

Wave5: independently repeat round-robin N52 and compare N50 for ITL headroom; N54 only after the N52 repeat passes. Optional midpoint and best-new-point repeat, at most five deployments. See [round-robin plan](serving-tuning-05/PLAN.md).

Accuracy against the organiser reference remains unverified. No official score is claimed.

Output diagnostic job 23146: COMPLETED; 132/132 responses recorded. [Status and purpose](serving-tuning-02/OUTPUT_DIAGNOSTIC.md). Not a ranked benchmark.

## 19 October 2026 — recovered measurements and new controlled batch

[Accepted source results](research-followup-20261019-0400/RESULTS.md): H200 24647 repeats 2780.483 good tokens/s; H100 221341 N52 reaches 2398.728, awaiting repeat. All local gates pass; full organiser accuracy remains unverified. [New plan and receipts](research-followup-20261019-0412/RESULTS.md): H200 24721–24724 and PBS 221589→221590 submitted. New jobs have no accepted measurement yet. Preserve all raw runs and use platform-matched controls.

## 19 October 2026 — new load observations and independent repeats

H200 24722 = 2839.532 good tokens/s, +2.1266% versus fresh N58 control 24721. H100 221590 = 2430.891, +0.8123% versus N52 repeat 221589. All local gates pass; new operating points await independent repeats and official accuracy remains unverified. Submitted H200 24732/24733 and PBS 221645→221646. [Full measurements, units, control mapping and receipts](research-followup-20261019-0527/RESULTS.md).

## 19 October 2026 — prefill/decode interaction

H200 24724 passes at 2938.628 good tokens/s (+5.6907% versus same-N58 control 24721); 24723 chunk 12288 loses 2.3789% and is closed. New H200 24736–24738 repeat/control/load trials, plus H100 prefill Tree N54 job 221669 after existing221645→221646. [Full report and source references](research-followup-20261019-0600/RESULTS.md). All new jobs await complete GPU gates; official accuracy unverified.

## 19 October 2026 — research progression and independent N60 repeat

24732 auto-decode N60 completes full local review at 2836.531 good tokens/s (−0.106% versus source 24722). The highest observed HPC-Ops-decode point 24724 still awaits its own repeat. [Research progression, units, attribution limits and next priorities](../../workspace/reports/research-journey-20261019/REPORT.md). No new job submitted in this report turn.

## Status review — 2026-10-19T11:15:15.315162+00:00

Live checks at 11:11 UTC: H200 24733/24736/24737/24738 remain pending for Priority; two hpcai nodes allocated. Highest H200 observation remains 2938.628 good tokens/s; its own interaction repeat has not run. All three PBS jobs completed and pass full local protocol/SLA/runtime/output checks: N54 repeat 221645 = 2418.588; N56 221646 = 2407.364; forced prefill Tree 221669 = 2160.946 good tokens/s. Tree execution is proved on all eight prefill ranks in 16 sealed diagnostic traces (355/355 successful requests); it loses 10.65% versus fresh N54 and is closed. N56 has no observed gain; no automatic N58. Highest H100 individual observation remains 2430.891. Official accuracy unverified. PBS queue empty; VPN/SSH usable without restart or authentication. Balance 34608.356 SU; three terminal charges reconcile, zero remaining reservations and internal headroom 21608.356 SU under the unchanged cap/buffer. No new GPU job, schedule, slide or submission change. [Full report and raw evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1111/RESULTS.md). This supersedes earlier queue and credit snapshots below.


## Continue research and submitted batch — 2026-10-19T12:02:20.997548+00:00

The user explicitly corrected idle research: during active authorised work, review results, research the next distinct hypothesis and submit when capacity/budget permit without another reminder. Losing N56 or Tree is not a global stop. Actual new jobs: PBS **221827 → 221828 → 221829** (N54 fresh control/profile, HPC-Ops chunk6144, prefill Simple protocol/profile); H200 **24819** (N58 winning interaction repeat/profile), preserving four older queued jobs. Five active H200 jobs and three serial PBS jobs. New PBS maximum reserve 4608 SU; pre-submit Balance 34608.356, Used 29391.644, In Doubt zero; internal headroom 17000.356 SU under unchanged cap/buffer. New jobs have no measurements yet. Full plan, references, hashes and receipts: [research continuation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1200/RESULTS.md). Review each completion and continue justified work. No blind duplicates, unchanged loss retries, automatic load growth, AI schedules or background Codex. Highest observations/accuracy limits unchanged.


## Global protocol activation followup — 2026-10-19T14:37:21.593278+00:00

Reviewed H100 control/chunk/scoped-protocol points at 2413.802/2411.995/2414.548 good tokens/s; no established gain, scoped Simple activation unverified in separate N48 traces. Submitted and verified chain **221880 → 221884 → 221885** (attention, instrumented default control, global prefill Simple). Attention was running at 14:30 UTC; others dependency-held. Three active PBS jobs and five H200 pending at prior 14:18 check. Total max PBS reserve 4608 SU; Used 30729.102, published Balance 33270.898, In Doubt zero; internal headroom 15662.898 SU. Budget cap/buffer unchanged. Review each completion and continue justified research without another reminder. No new official accuracy or performance claim, VPN auth, background AI or slides. [Receipts and rationale](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-protocol-check/RESULTS.md).


## H100 protocol and host-profile review — 2026-10-19T17:25:27.642282+00:00

Jobs 221884/221885/221886 pass full local gates at 2415.474/2421.066/2425.886 good tokens/s; no new peak. Global Simple parses but its actual kernel activation remains unverified, so close full-model selector sweeps. Attention 221880 is a valid −7.74% regression and closed. All four charges reconcile at 1875.626 SU; published Balance 31395.272, Used 32604.728, no outstanding reservations, internal headroom 18395.272 under unchanged caps. PBS empty and H200 five Priority-pending at 17:20 UTC. Continue with a source-supported matched decode inference-mode test rather than stopping research. No new GPU job at this review checkpoint; no official accuracy, slide or automation claim. [Full review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1720/RESULTS.md). Older snapshots below are historical.


## Decode inference-mode pair submitted — 2026-10-19T17:27:18.644559+00:00

Actual new PBS chain **221923 → 221924**: explicit-default control Q and decode-only inference-mode candidate H at the post-submit check. Fixed N54 scoring, model precision, transport and output checks remain unchanged; separate CPU/GPU profiles and pinned DynamicGradMode source/context preflights are retained. No benchmark result yet. New maximum reserve 3072 SU; published Used 32604.728, Balance 31395.272, In Doubt zero; internal headroom 15323.272 SU under unchanged cap/buffer. Five H200 jobs remained Priority-pending at 17:20 UTC. [Rationale and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-inference-mode/RESULTS.md). The preceding empty-queue review checkpoint is historical. Continue review and justified research during authorised work; no blind repeats, authentication, background Codex or slides.


## NCCL interpretation correction and live queues — 2026-10-19T17:58:15.294282+00:00

At 17:55 UTC, PBS 221923 Q (exclusive nodes in use), 221924 H (afterany dependency); all five H200 jobs still Priority-pending. No new measurement or charge; Used 32604.728, Balance 31395.272 SU, 3072 SU maximum reserve and 15323.272 SU internal headroom. Existing access works, no reauthentication.

Corrected an old interpretation: LL-labelled NCCL symbols are representatives and do not identify selected protocol. Existing sealed TUNING logs show Simple selected in 221885 and already selected for the control's large operations; the small +0.2315% score does not establish a useful gain. No GPU rerun is needed to explain the names. Keep automatic protocol policy. [Correction, sources and parsed counts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1755/CORRECTION.md). Earlier activation claims and symbol-count gates are historical and superseded. No score, accuracy, slide or automation change.


## Prefill-only phase test submitted — 2026-10-19T18:00:11.710346+00:00

Submitted **221966.pbs111** after 221924, extending the verified chain **221923 → 221924 → 221966** (default control, decode-only inference mode, prefill-only inference mode). Actual post-submit states Q/H/H; no new measurement. New additional maximum reserve 1536 SU, total 4608 SU, internal headroom 13787.272 SU; published Used 32604.728 and Balance 31395.272 SU, no new charge. Caps/buffer unchanged, no overlapping 16-GPU allocation or fourth active PBS job. Five H200 jobs remain Priority-pending at the 17:55 check. [Hypothesis and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-prefill-inference/RESULTS.md).

The NCCL interpretation correction in the preceding checkpoint remains current: existing TUNING decisions show Simple selected and explain why missing Simple-labelled symbols were not evidence of failed activation. No GPU job is needed for that ambiguity. Preserve all historical measurements; no new peak, accuracy, authentication, slides or automation claim.


## Research continuation — 20 October 2026

Reviewed five H200 and three H100 completed full-model runs. H200 N58 HPC-Ops interaction now repeats across three deployments; N60 reaches a new individual 2990.151 good output tokens/s, awaiting treatment repeat. Submitted H200 24912/24913/24914/24915; 24912 fresh auto N60 passes at 2838.853, the other three were Resources-pending at 00:51 UTC. H100 phase-specific inference mode is flat and closed. Three bounded 8-GPU collective screens preserve numerical gates and expose launch-cadence ambiguity, then reject forced one-shot and disabling PDL. Keep native AUTO+PDL; no full-model patch for these losses. New H100 native decode FlashInfer/FA3 pair 222027→222028 was R/H at 00:51–00:52 UTC, with 3072 SU maximum reserve. No attention score yet.

Published Used 34035.199 SU, Balance 29794.134 SU, In Doubt 170.667 SU (08:40 SGT publication); Balance already excludes prepayment. Total unreleased maximum reservation 3413.333 SU, internal headroom 13551.468 SU under unchanged cap/buffer. Existing access reused, no authentication or automation changes. Full official accuracy unverified. [Full hypothesis/control/result/assessment/next-decision entry](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261020-serving-and-collective.md). Earlier states below are historical.


## Reproduced N60 and observed polling submissions — 20 October 2026

H200 24913 passes at 2989.175 good output tokens/s, independently repeating 24738 = 2990.151 and +5.295% above fresh auto control 24912. Auto N62 24914 passes at 2890.878; keep HPC-Ops N62 24915 position. H100 222027/222028 both pass at 2420.945/2401.284: FA3 lowers mean TTFT but loses 0.812% goodput and increases ITL, so retain FlashInfer. Raw scored failures are 22 TTFT breaches per run and zero ITL/error/cancel breaches; all rank CPU/GPU traces inspected, without claiming a large CPU bottleneck.

Submitted three matched off/on/receive-2 pilots per platform: H200 24926/24927/24928 and serial PBS 222048→222049→222050. At 01:43 UTC H200 new group plus old 24915 were Resources-pending; PBS R/H/H. New bounded resource collector and phase markers are deployed in those frozen bundles; actual telemetry coverage and observer overhead are not yet verified. No numerical/workload change. Earlier “collector not implemented” status is historical. Local fixtures and seven source-file hashes agree across both images; control/candidate differ only in polling interval after observation settings match.

Published Used 34972.443 SU, Balance 29027.557 SU; four terminal charges reconcile 937.244 SU. New maximum reserve 4608 SU, internal headroom 11419.557 SU under unchanged cap/buffer. Existing access reused, no authentication, background AI, slides or official accuracy claim. [Full result/insight/next-decision entry](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261020-receive-polling.md). Older states below retain their timestamps.

