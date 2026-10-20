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

# Sổ các lần chạy Qwen

Cập nhật UTC: 2026-10-18T19:24:16.398608+00:00

Mỗi job là dữ kiện: lỗi deploy dùng sửa quy trình; số đo qua/trượt SLA dùng chọn cấu hình. Không lấy job lỗi trước benchmark làm số liệu tốc độ.

| Job | Topology | Trạng thái | Lượt đo đã có | Có manifest checksum |
|---|---|---|---:|---|
| [22130](runs/22130/) | 07 | FAILED | 0 | [manifest](runs/22130/artifact-manifest.json) |
| [22131](runs/22131/) | 09 | COMPLETED | 4 | [manifest](runs/22131/artifact-manifest.json) |
| [22135](runs/22135/) | 07 | COMPLETED | 3 | [manifest](runs/22135/artifact-manifest.json) |
| [22143](runs/22143/) | 07 | FAILED | 0 | [manifest](runs/22143/artifact-manifest.json) |
| [22147](runs/22147/) | 07 | FAILED | 0 | [manifest](runs/22147/artifact-manifest.json) |
| [22197](runs/22197/) | 07 | COMPLETED | 1 | [manifest](runs/22197/artifact-manifest.json) |
| [22200](runs/22200/) | 09 | COMPLETED | 3 | [manifest](runs/22200/artifact-manifest.json) |
| [22219](runs/22219/) | P8-TP4_D8-TP4-EP4 | COMPLETED | 5 | [manifest](runs/22219/artifact-manifest.json) |
| [22220](runs/22220/) | P8-TP2_D8-TP4-EP4 | FAILED | 0 | [manifest](runs/22220/artifact-manifest.json) |
| [22221](runs/22221/) | P8-TP8_D8-TP4-EP4 | FAILED | 0 | [manifest](runs/22221/artifact-manifest.json) |
| [22222](runs/22222/) | P8-TP4_D8-TP8-EP8 | FAILED | 0 | [manifest](runs/22222/artifact-manifest.json) |
| [22231](runs/22231/) | P4-TP4_D12-TP4-EP4 | COMPLETED | 5 | [manifest](runs/22231/artifact-manifest.json) |
| [22232](runs/22232/) | P12-TP4_D4-TP4-EP4 | FAILED | 0 | [manifest](runs/22232/artifact-manifest.json) |
| [22233](runs/22233/) | P8-TP2_D8-TP2-EP2 | COMPLETED | 4 | [manifest](runs/22233/artifact-manifest.json) |
| [22234](runs/22234/) | P8-TP2_D8-TP8-EP8 | FAILED | 0 | [manifest](runs/22234/artifact-manifest.json) |
| [22235](runs/22235/) | P8-TP4_D8-TP2-EP2 | COMPLETED | 4 | [manifest](runs/22235/artifact-manifest.json) |
| [22236](runs/22236/) | P8-TP8_D8-TP2-EP2 | FAILED | 0 | [manifest](runs/22236/artifact-manifest.json) |
| [22238](runs/22238/) | P8-TP8_D8-TP8-EP8 | FAILED | 0 | [manifest](runs/22238/artifact-manifest.json) |
| [22239](runs/22239/) | P4-TP2_D12-TP2-EP2 | COMPLETED | 4 | [manifest](runs/22239/artifact-manifest.json) |
| [22240](runs/22240/) | P4-TP2_D12-TP4-EP4 | FAILED | 0 | [manifest](runs/22240/artifact-manifest.json) |
| [22241](runs/22241/) | P4-TP4_D12-TP2-EP2 | COMPLETED | 4 | [manifest](runs/22241/artifact-manifest.json) |
| [22242](runs/22242/) | P12-TP2_D4-TP2-EP2 | COMPLETED | 4 | [manifest](runs/22242/artifact-manifest.json) |
| [22245](runs/22245/) | P12-TP2_D4-TP4-EP4 | FAILED | 0 | [manifest](runs/22245/artifact-manifest.json) |
| [22246](runs/22246/) | P12-TP4_D4-TP2-EP2 | COMPLETED | 4 | [manifest](runs/22246/artifact-manifest.json) |
| [22270](runs/22270/) | P8-TP2_D8-TP4-EP4 | COMPLETED | 4 | [manifest](runs/22270/artifact-manifest.json) |
| [22271](runs/22271/) | P8-TP8-EP2_D8-TP4-EP4 | FAILED | 0 | [manifest](runs/22271/artifact-manifest.json) |
| [22272](runs/22272/) | P8-TP4_D8-TP8-EP8 | CANCELLED by 3042 | 0 | Chưa: job chưa kết thúc |
| [22273](runs/22273/) | P12-TP4_D4-TP4-EP4 | COMPLETED | 4 | [manifest](runs/22273/artifact-manifest.json) |
| [22274](runs/22274/) | P8-TP2_D8-TP4-EP4 | CANCELLED by 3042 | 0 | Chưa: job chưa kết thúc |
| [22280](runs/22280/) | P8-TP8-EP2_D8-TP4-EP4 | CANCELLED by 3042 | 0 | Chưa: job chưa kết thúc |
| [22294](runs/22294/) | P8-TP8-EP2_D8-TP4-EP4 | COMPLETED | 5 | [manifest](runs/22294/artifact-manifest.json) |
| [22300](runs/22300/) | P8-TP2_D8-TP8-EP8 | CANCELLED by 3042 | 0 | Chưa: job chưa kết thúc |
| [22305](runs/22305/) | P8-TP4_D8-TP8-EP8 | CANCELLED by 3042 | 0 | Chưa: job chưa kết thúc |
| [22413](runs/22413/) | P12-TP4_D4-TP4-EP4 | CANCELLED by 3042 | 0 | Chưa: job chưa kết thúc |
| [22414](runs/22414/) | P8-TP2_D8-TP4-EP4 | COMPLETED | 1 | [manifest](runs/22414/artifact-manifest.json) |
| [22415](runs/22415/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 5 | [manifest](runs/22415/artifact-manifest.json) |
| [22416](runs/22416/) | P12-TP4_D4-TP4-EP4 | COMPLETED | 1 | [manifest](runs/22416/artifact-manifest.json) |
| [22417](runs/22417/) | P8-TP2_D8-TP8-EP8 | COMPLETED | 5 | [manifest](runs/22417/artifact-manifest.json) |
| [22468](runs/22468/) | P8-TP8-EP2_D8-TP2-EP2 | COMPLETED | 4 | [manifest](runs/22468/artifact-manifest.json) |
| [22509](runs/22509/) | P8-TP8-EP2_D8-TP8-EP8 | FAILED | 0 | [manifest](runs/22509/artifact-manifest.json) |
| [22517](runs/22517/) | P4-TP2_D12-TP4-EP4 | COMPLETED | 5 | [manifest](runs/22517/artifact-manifest.json) |
| [22524](runs/22524/) | P8-TP2_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/22524/artifact-manifest.json) |
| [22532](runs/22532/) | P12-TP2_D4-TP4-EP4 | COMPLETED | 5 | [manifest](runs/22532/artifact-manifest.json) |
| [22538](runs/22538/) | P8-TP8-EP2_D8-TP8-EP8 | FAILED | 0 | [manifest](runs/22538/artifact-manifest.json) |
| [22750](runs/22750/) | P8-TP8-EP2_D8-TP8-EP8 | COMPLETED | 2 | [manifest](runs/22750/artifact-manifest.json) |
| [22778](runs/22778/) | P8-TP8-EP2_D8-TP8-EP8 | FAILED | 0 | [manifest](runs/22778/artifact-manifest.json) |
| [22809](runs/22809/) | P8-TP8-EP2_D8-TP8-EP8 | COMPLETED | 5 | [manifest](runs/22809/artifact-manifest.json) |
| [23102](runs/23102/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 2 | [manifest](runs/23102/artifact-manifest.json) |
| [23103](runs/23103/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 2 | [manifest](runs/23103/artifact-manifest.json) |
| [23104](runs/23104/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23104/artifact-manifest.json) |
| [23106](runs/23106/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23106/artifact-manifest.json) |
| [23109](runs/23109/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23109/artifact-manifest.json) |
| [23113](runs/23113/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23113/artifact-manifest.json) |
| [23114](runs/23114/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 2 | [manifest](runs/23114/artifact-manifest.json) |
| [23115](runs/23115/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 2 | [manifest](runs/23115/artifact-manifest.json) |
| [23128](runs/23128/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23128/artifact-manifest.json) |
| [23129](runs/23129/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23129/artifact-manifest.json) |
| [23130](runs/23130/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23130/artifact-manifest.json) |
| [23131](runs/23131/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23131/artifact-manifest.json) |
| [23146](runs/23146/) | Monolithic TP4/EP1 (2 instances) + TP8/EP8 (1 instance); no P/D | COMPLETED | 0 | [manifest](runs/23146/artifact-manifest.json) |
| [23264](runs/23264/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23264/artifact-manifest.json) |
| [23265](runs/23265/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23265/artifact-manifest.json) |
| [23266](runs/23266/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23266/artifact-manifest.json) |
| [23267](runs/23267/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23267/artifact-manifest.json) |
| [23272](runs/23272/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23272/artifact-manifest.json) |
| [23286](runs/23286/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23286/artifact-manifest.json) |
| [23287](runs/23287/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23287/artifact-manifest.json) |
| [23324](runs/23324/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23324/artifact-manifest.json) |
| [23325](runs/23325/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23325/artifact-manifest.json) |
| [23437](runs/23437/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23437/artifact-manifest.json) |
| [23495](runs/23495/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23495/artifact-manifest.json) |
| [23505](runs/23505/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23505/artifact-manifest.json) |
| [23516](runs/23516/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23516/artifact-manifest.json) |
| [23576](runs/23576/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23576/artifact-manifest.json) |
| [23577](runs/23577/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23577/artifact-manifest.json) |
| [23583](runs/23583/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23583/artifact-manifest.json) |
| [23607](runs/23607/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23607/artifact-manifest.json) |
| [23608](runs/23608/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23608/artifact-manifest.json) |
| [23609](runs/23609/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23609/artifact-manifest.json) |
| [23616](runs/23616/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23616/artifact-manifest.json) |
| [23773](runs/23773/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23773/artifact-manifest.json) |
| [23776](runs/23776/) | P8-TP4_D8-TP8-EP8 | FAILED | 0 | [manifest](runs/23776/artifact-manifest.json) |
| [23777](runs/23777/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23777/artifact-manifest.json) |
| [23778](runs/23778/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23778/artifact-manifest.json) |
| [23780](runs/23780/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23780/artifact-manifest.json) |
| [23839](runs/23839/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23839/artifact-manifest.json) |
| [23859](runs/23859/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23859/artifact-manifest.json) |
| [23904](runs/23904/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23904/artifact-manifest.json) |
| [23905](runs/23905/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23905/artifact-manifest.json) |
| [23906](runs/23906/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23906/artifact-manifest.json) |
| [23924](runs/23924/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23924/artifact-manifest.json) |
| [23934](runs/23934/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23934/artifact-manifest.json) |
| [23973](runs/23973/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23973/artifact-manifest.json) |
| [23974](runs/23974/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23974/artifact-manifest.json) |
| [23975](runs/23975/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/23975/artifact-manifest.json) |
| [24009](runs/24009/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24009/artifact-manifest.json) |
| [24131](runs/24131/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24131/artifact-manifest.json) |
| [24174](runs/24174/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24174/artifact-manifest.json) |
| [24175](runs/24175/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24175/artifact-manifest.json) |
| [24189](runs/24189/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24189/artifact-manifest.json) |
| [24190](runs/24190/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24190/artifact-manifest.json) |
| [24235](runs/24235/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24235/artifact-manifest.json) |
| [24236](runs/24236/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24236/artifact-manifest.json) |
| [24263](runs/24263/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24263/artifact-manifest.json) |
| [24272](runs/24272/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24272/artifact-manifest.json) |
| [24281](runs/24281/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24281/artifact-manifest.json) |
| [24282](runs/24282/) | P8-TP4_D8-TP8-EP8 | FAILED | 0 | [manifest](runs/24282/artifact-manifest.json) |
| [24291](runs/24291/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24291/artifact-manifest.json) |
| [24320](runs/24320/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24320/artifact-manifest.json) |
| [24321](runs/24321/) | P8-TP4_D8-TP8-EP8 | FAILED | 0 | [manifest](runs/24321/artifact-manifest.json) |
| [24322](runs/24322/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24322/artifact-manifest.json) |
| [24327](runs/24327/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24327/artifact-manifest.json) |
| [24352](runs/24352/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24352/artifact-manifest.json) |
| [24375](runs/24375/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24375/artifact-manifest.json) |
| [24376](runs/24376/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24376/artifact-manifest.json) |
| [24425](runs/24425/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24425/artifact-manifest.json) |
| [24426](runs/24426/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24426/artifact-manifest.json) |
| [24428](runs/24428/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24428/artifact-manifest.json) |
| [24429](runs/24429/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24429/artifact-manifest.json) |
| [24526](runs/24526/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24526/artifact-manifest.json) |
| [24527](runs/24527/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24527/artifact-manifest.json) |
| [24528](runs/24528/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24528/artifact-manifest.json) |
| [24529](runs/24529/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24529/artifact-manifest.json) |
| [24538](runs/24538/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24538/artifact-manifest.json) |
| [24544](runs/24544/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24544/artifact-manifest.json) |
| [24573](runs/24573/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24573/artifact-manifest.json) |
| [24574](runs/24574/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24574/artifact-manifest.json) |
| [24575](runs/24575/) | P8-TP4_D8-TP8-EP8 | COMPLETED | 1 | [manifest](runs/24575/artifact-manifest.json) |
| [24588](runs/24588/) | P8-TP4_D8-TP8-EP8 | TIMEOUT | 0 | [manifest](runs/24588/artifact-manifest.json) |
| [24589](runs/24589/) | P8-TP4_D8-TP8-EP8 | PENDING | 0 | Chưa: job chưa kết thúc |
| [24639](runs/24639/) | P8-TP4_D8-TP8-EP8 | PENDING | 0 | Chưa: job chưa kết thúc |
| [24640](runs/24640/) | P8-TP4_D8-TP8-EP8 | PENDING | 0 | Chưa: job chưa kết thúc |
| [24641](runs/24641/) | P8-TP4_D8-TP8-EP8 | PENDING | 0 | Chưa: job chưa kết thúc |

## Job 22130

**Mục đích:** Lần đầu chạy đối chứng và client

**Quan sát:** Deployment đã lên, client lỗi tokenizer trước khi có số đo hợp lệ.

**Bài học:** Dùng official tokenizer ID cùng HF cache offline; kiểm tra tokenizer trước benchmark.

[stdout](runs/22130.out) · [stderr](runs/22130.err) · [thư mục artifacts](runs/22130/)

## Job 22131

**Mục đích:** Sweep N16/32/64 và confirm N32

**Quan sát:** N32 confirm đạt 97,84% SLA và 1472,73 good tokens/s; N64 sweep trượt SLA.

**Bài học:** Giữ N32 làm ứng viên; thu hẹp khoảng N32–N64 thay vì chỉ tăng tải.

[stdout](runs/22131.out) · [stderr](runs/22131.err) · [thư mục artifacts](runs/22131/)

**Ghi chú lịch sử file:** benchmark.sh được sửa trước khi client bắt đầu để dùng tokenizer hợp lệ và confirm; summarize.py đã được sửa để loại warmup/exports trùng. Các snapshot này không phải lịch sử bất biến từ lúc submit.

- confirm/N32: 97.84% đạt SLA, 1472.73 good tokens/s, cancelled=0; [raw export](runs/22131/confirm/n32/artifacts/profile_export_aiperf.json).

- sweep/N16: 100.00% đạt SLA, 856.99 good tokens/s, cancelled=0; [raw export](runs/22131/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 100.00% đạt SLA, 1465.35 good tokens/s, cancelled=0; [raw export](runs/22131/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N64: 67.00% đạt SLA, 1509.34 good tokens/s, cancelled=0; [raw export](runs/22131/sweep/n64/artifacts/profile_export_aiperf.json).

## Job 22135

**Mục đích:** Sweep N16/32/64 sau sửa tokenizer

**Quan sát:** Cả 3 điểm trượt SLA; N16 có 14 request bị hủy; logs còn cold KV bootstrap.

**Bài học:** Lưu số liệu nhưng không suy ra speedup nhiều lần từ cold-path run; cần warm đủ từng cặp và confirm dài.

[stdout](runs/22135.out) · [stderr](runs/22135.err) · [thư mục artifacts](runs/22135/)

**Ghi chú lịch sử file:** summarize.py được cập nhật trong quá trình chạy để lọc đúng export chính và thêm thống kê; raw artifacts giữ nguyên.

- sweep/N16: 82.05% đạt SLA, 106.66 good tokens/s, cancelled=14; [raw export](runs/22135/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 58.22% đạt SLA, 321.13 good tokens/s, cancelled=0; [raw export](runs/22135/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N64: 65.37% đạt SLA, 1191.57 good tokens/s, cancelled=0; [raw export](runs/22135/sweep/n64/artifacts/profile_export_aiperf.json).

## Job 22143

**Mục đích:** Thử warm đủ 8 cặp trước confirm N32

**Quan sát:** Gateway tạm trùng cổng Prometheus 29000; lỗi trước benchmark.

**Bài học:** API port riêng chưa đủ; cổng metrics cũng phải riêng cho từng gateway.

[stdout](runs/22143.out) · [stderr](runs/22143.err) · [thư mục artifacts](runs/22143/)

## Job 22147

**Mục đích:** Chạy lại warm từng cặp sau sửa cổng metrics

**Quan sát:** Gateway /health trả OK trước khi worker registration hoàn tất; warmup nhận no-workers HTTP503.

**Bài học:** Readiness phải kiểm tra khả năng phục vụ; retry có giới hạn đúng lỗi chưa có worker.

[stdout](runs/22147.out) · [stderr](runs/22147.err) · [thư mục artifacts](runs/22147/)

## Job 22197

**Mục đích:** Warm 8 cặp có retry registration, confirm N32

**Quan sát:** 809/832 request đạt SLA; 1297,02 good tokens/s. Warmup từng cặp thành công.

**Bài học:** Đối chứng dài hợp lệ; 09/N32 cao hơn 13,55% trong hai lượt đo, cần lặp để đánh giá dao động.

[stdout](runs/22197.out) · [stderr](runs/22197.err) · [thư mục artifacts](runs/22197/)

- confirm/N32: 97.24% đạt SLA, 1297.02 good tokens/s, cancelled=0; [raw export](runs/22197/confirm/n32/artifacts/profile_export_aiperf.json).

## Job 22200

**Mục đích:** Warm 4 cặp; sweep N40/N48; confirm mức tốt nhất qua SLA

**Quan sát:** Hoàn thành: N40 confirm 1026/1049 request đạt SLA (97,81%), 1649,27 good tokens/s, cancelled=0. N48 sweep chỉ 88,17% nên loại.

**Bài học:** N40 cải thiện so N32 trong một deployment; tăng lên N48 đã trượt SLA. Dùng N40 làm mốc trước đợt 17 topology, chưa chứng minh độ ổn định qua nhiều deployment.

[stdout](runs/22200.out) · [stderr](runs/22200.err) · [thư mục artifacts](runs/22200/)

- confirm/N40: 97.81% đạt SLA, 1649.27 good tokens/s, cancelled=0; [raw export](runs/22200/confirm/n40/artifacts/profile_export_aiperf.json).

- sweep/N40: 91.29% đạt SLA, 1411.62 good tokens/s, cancelled=0; [raw export](runs/22200/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 88.17% đạt SLA, 1690.19 good tokens/s, cancelled=0; [raw export](runs/22200/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22219

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái COMPLETED; 5 lượt đã có raw export. Tốt nhất (confirm) N40: 1666.01 good tokens/s, 97.82% SLA.

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22219.out) · [stderr](runs/22219.err) · [thư mục artifacts](runs/22219/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/01-P8-TP4_D8-TP4-EP4/SHA256SUMS; bản sao ở runs/22219/submitted/. Weights/images ngoài payload.

- confirm/N40: 97.82% đạt SLA, 1666.01 good tokens/s, cancelled=0; [raw export](runs/22219/confirm/n40/artifacts/profile_export_aiperf.json).

- sweep/N16: 100.00% đạt SLA, 811.49 good tokens/s, cancelled=0; [raw export](runs/22219/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 100.00% đạt SLA, 1377.22 good tokens/s, cancelled=0; [raw export](runs/22219/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 94.03% đạt SLA, 1488.57 good tokens/s, cancelled=0; [raw export](runs/22219/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 77.50% đạt SLA, 1428.23 good tokens/s, cancelled=0; [raw export](runs/22219/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22220

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái FAILED; 0 lượt đã có raw export. Dấu lỗi trong log: srun: error: Timed out waiting for job step to complete srun: error: Timed out waiting for job step to complete

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22220.out) · [stderr](runs/22220.err) · [thư mục artifacts](runs/22220/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/02-P8-TP2_D8-TP4-EP4/SHA256SUMS; bản sao ở runs/22220/submitted/. Weights/images ngoài payload.

## Job 22221

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái FAILED; 0 lượt đã có raw export. Dấu lỗi trong log: FATAL: worker/router step 1545193 exited before readiness srun: error: Timed out waiting for job step to complete

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22221.out) · [stderr](runs/22221.err) · [thư mục artifacts](runs/22221/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/03-P8-TP8_D8-TP4-EP4/SHA256SUMS; bản sao ở runs/22221/submitted/. Weights/images ngoài payload.

## Job 22222

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái FAILED; 0 lượt đã có raw export. Dấu lỗi trong log: srun: error: Timed out waiting for job step to complete srun: error: g1: task 0: Exited with exit code 1

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22222.out) · [stderr](runs/22222.err) · [thư mục artifacts](runs/22222/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/04-P8-TP4_D8-TP8-EP8/SHA256SUMS; bản sao ở runs/22222/submitted/. Weights/images ngoài payload.

## Job 22231

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái COMPLETED; 5 lượt đã có raw export. Tốt nhất (confirm) N40: 1382.16 good tokens/s, 97.40% SLA.

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22231.out) · [stderr](runs/22231.err) · [thư mục artifacts](runs/22231/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/05-P4-TP4_D12-TP4-EP4/SHA256SUMS; bản sao ở runs/22231/submitted/. Weights/images ngoài payload.

- confirm/N40: 97.40% đạt SLA, 1382.16 good tokens/s, cancelled=0; [raw export](runs/22231/confirm/n40/artifacts/profile_export_aiperf.json).

- sweep/N16: 100.00% đạt SLA, 846.89 good tokens/s, cancelled=0; [raw export](runs/22231/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 100.00% đạt SLA, 1372.49 good tokens/s, cancelled=0; [raw export](runs/22231/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 98.54% đạt SLA, 1641.19 good tokens/s, cancelled=0; [raw export](runs/22231/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 88.21% đạt SLA, 1647.94 good tokens/s, cancelled=0; [raw export](runs/22231/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22232

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái FAILED; 0 lượt đã có raw export. Dấu lỗi trong log: srun: error: Timed out waiting for job step to complete srun: error: g1: task 0: Exited with exit code 1

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22232.out) · [stderr](runs/22232.err) · [thư mục artifacts](runs/22232/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/06-P12-TP4_D4-TP4-EP4/SHA256SUMS; bản sao ở runs/22232/submitted/. Weights/images ngoài payload.

## Job 22233

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái COMPLETED; 4 lượt đã có raw export.

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22233.out) · [stderr](runs/22233.err) · [thư mục artifacts](runs/22233/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/07-P8-TP2_D8-TP2-EP2/SHA256SUMS; bản sao ở runs/22233/submitted/. Weights/images ngoài payload.

- sweep/N16: 80.52% đạt SLA, 545.72 good tokens/s, cancelled=0; [raw export](runs/22233/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 61.81% đạt SLA, 721.04 good tokens/s, cancelled=0; [raw export](runs/22233/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 43.50% đạt SLA, 595.82 good tokens/s, cancelled=0; [raw export](runs/22233/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 46.81% đạt SLA, 693.65 good tokens/s, cancelled=0; [raw export](runs/22233/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22234

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái FAILED; 0 lượt đã có raw export. Dấu lỗi trong log: FATAL: worker/router step 1585227 exited before readiness srun: error: Timed out waiting for job step to complete

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22234.out) · [stderr](runs/22234.err) · [thư mục artifacts](runs/22234/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/08-P8-TP2_D8-TP8-EP8/SHA256SUMS; bản sao ở runs/22234/submitted/. Weights/images ngoài payload.

## Job 22235

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái COMPLETED; 4 lượt đã có raw export.

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22235.out) · [stderr](runs/22235.err) · [thư mục artifacts](runs/22235/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/09-P8-TP4_D8-TP2-EP2/SHA256SUMS; bản sao ở runs/22235/submitted/. Weights/images ngoài payload.

- sweep/N16: 82.35% đạt SLA, 597.15 good tokens/s, cancelled=0; [raw export](runs/22235/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 66.67% đạt SLA, 804.38 good tokens/s, cancelled=0; [raw export](runs/22235/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 32.22% đạt SLA, 454.63 good tokens/s, cancelled=0; [raw export](runs/22235/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 20.79% đạt SLA, 334.37 good tokens/s, cancelled=0; [raw export](runs/22235/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22236

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái FAILED; 0 lượt đã có raw export. Dấu lỗi trong log: FATAL: worker/router step 1599156 exited before readiness srun: error: Timed out waiting for job step to complete

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22236.out) · [stderr](runs/22236.err) · [thư mục artifacts](runs/22236/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/10-P8-TP8_D8-TP2-EP2/SHA256SUMS; bản sao ở runs/22236/submitted/. Weights/images ngoài payload.

## Job 22238

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái FAILED; 0 lượt đã có raw export. Dấu lỗi trong log: FATAL: worker/router step 1602373 exited before readiness srun: error: Timed out waiting for job step to complete

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22238.out) · [stderr](runs/22238.err) · [thư mục artifacts](runs/22238/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/11-P8-TP8_D8-TP8-EP8/SHA256SUMS; bản sao ở runs/22238/submitted/. Weights/images ngoài payload.

## Job 22239

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái COMPLETED; 4 lượt đã có raw export.

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22239.out) · [stderr](runs/22239.err) · [thư mục artifacts](runs/22239/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/12-P4-TP2_D12-TP2-EP2/SHA256SUMS; bản sao ở runs/22239/submitted/. Weights/images ngoài payload.

- sweep/N16: 79.22% đạt SLA, 539.18 good tokens/s, cancelled=0; [raw export](runs/22239/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 75.18% đạt SLA, 803.98 good tokens/s, cancelled=0; [raw export](runs/22239/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 74.23% đạt SLA, 959.15 good tokens/s, cancelled=0; [raw export](runs/22239/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 60.66% đạt SLA, 848.67 good tokens/s, cancelled=0; [raw export](runs/22239/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22240

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái FAILED; 0 lượt đã có raw export. Dấu lỗi trong log: srun: error: Timed out waiting for job step to complete srun: error: Timed out waiting for job step to complete

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22240.out) · [stderr](runs/22240.err) · [thư mục artifacts](runs/22240/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/13-P4-TP2_D12-TP4-EP4/SHA256SUMS; bản sao ở runs/22240/submitted/. Weights/images ngoài payload.

## Job 22241

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái COMPLETED; 4 lượt đã có raw export.

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22241.out) · [stderr](runs/22241.err) · [thư mục artifacts](runs/22241/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/14-P4-TP4_D12-TP2-EP2/SHA256SUMS; bản sao ở runs/22241/submitted/. Weights/images ngoài payload.

- sweep/N16: 82.76% đạt SLA, 610.74 good tokens/s, cancelled=0; [raw export](runs/22241/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 86.00% đạt SLA, 1022.74 good tokens/s, cancelled=0; [raw export](runs/22241/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 65.57% đạt SLA, 971.47 good tokens/s, cancelled=0; [raw export](runs/22241/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 47.49% đạt SLA, 749.54 good tokens/s, cancelled=0; [raw export](runs/22241/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22242

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái COMPLETED; 4 lượt đã có raw export.

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22242.out) · [stderr](runs/22242.err) · [thư mục artifacts](runs/22242/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/15-P12-TP2_D4-TP2-EP2/SHA256SUMS; bản sao ở runs/22242/submitted/. Weights/images ngoài payload.

- sweep/N16: 76.06% đạt SLA, 471.17 good tokens/s, cancelled=0; [raw export](runs/22242/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 14.84% đạt SLA, 154.12 good tokens/s, cancelled=0; [raw export](runs/22242/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 6.49% đạt SLA, 79.69 good tokens/s, cancelled=0; [raw export](runs/22242/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 1.16% đạt SLA, 15.49 good tokens/s, cancelled=0; [raw export](runs/22242/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22245

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái FAILED; 0 lượt đã có raw export. Dấu lỗi trong log: srun: error: Timed out waiting for job step to complete srun: error: g1: task 0: Exited with exit code 1

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22245.out) · [stderr](runs/22245.err) · [thư mục artifacts](runs/22245/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/16-P12-TP2_D4-TP4-EP4/SHA256SUMS; bản sao ở runs/22245/submitted/. Weights/images ngoài payload.

## Job 22246

**Mục đích:** Sweep 17 topology: N16/32/40/48; confirm điểm tốt nhất qua SLA nếu đủ thời gian.

**Quan sát:** Trạng thái COMPLETED; 4 lượt đã có raw export.

**Bài học:** Giữ điểm trượt SLA và lỗi deploy; không xếp điểm chưa qua SLA hoặc bị hủy vào nhóm hiệu năng hợp lệ.

[stdout](runs/22246.out) · [stderr](runs/22246.err) · [thư mục artifacts](runs/22246/)

**Ghi chú lịch sử file:** Payload cố định trước submit, hash ở /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/17-P12-TP4_D4-TP2-EP2/SHA256SUMS; bản sao ở runs/22246/submitted/. Weights/images ngoài payload.

- sweep/N16: 58.33% đạt SLA, 360.17 good tokens/s, cancelled=0; [raw export](runs/22246/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 3.85% đạt SLA, 40.89 good tokens/s, cancelled=0; [raw export](runs/22246/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 0.62% đạt SLA, 7.89 good tokens/s, cancelled=0; [raw export](runs/22246/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 0.52% đạt SLA, 6.85 good tokens/s, cancelled=0; [raw export](runs/22246/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22270

**Mục đích:** Recovery of 22220; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm COMPLETED; 4 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained.

[stdout](runs/22270.out) · [stderr](runs/22270.err) · [thư mục artifacts](runs/22270/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/pilot-07; original failed logs preserved.

- sweep/N16: 91.95% đạt SLA, 676.49 good tokens/s, cancelled=0; [raw export](runs/22270/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 96.08% đạt SLA, 1212.82 good tokens/s, cancelled=0; [raw export](runs/22270/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 96.72% đạt SLA, 1406.54 good tokens/s, cancelled=0; [raw export](runs/22270/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 92.08% đạt SLA, 1540.68 good tokens/s, cancelled=0; [raw export](runs/22270/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22271

**Mục đích:** Recovery of 22221; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm FAILED; 0 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Prefill EP2 is a distinct variant to align FP8 expert shards.

[stdout](runs/22271.out) · [stderr](runs/22271.err) · [thư mục artifacts](runs/22271/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/03-P8-TP8-EP2_D8-TP4-EP4-a1-sweep; original failed logs preserved.

## Job 22272

**Mục đích:** Recovery of 22222; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm CANCELLED; 0 exports. Failure is not a completed benchmark. Pilot 22294 served the actual workload; replace unstarted full-pool transfer retry with on-demand descriptors.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained.

[stdout](runs/22272.out) · [stderr](runs/22272.err) · [thư mục artifacts](runs/22272/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/04-P8-TP4_D8-TP8-EP8-a1-sweep; original failed logs preserved.

## Job 22273

**Mục đích:** Recovery of 22232; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm COMPLETED; 4 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained.

[stdout](runs/22273.out) · [stderr](runs/22273.err) · [thư mục artifacts](runs/22273/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/06-P12-TP4_D4-TP4-EP4-a1-sweep; original failed logs preserved.

- sweep/N16: 100.00% đạt SLA, 742.33 good tokens/s, cancelled=0; [raw export](runs/22273/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 70.62% đạt SLA, 905.91 good tokens/s, cancelled=0; [raw export](runs/22273/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 48.19% đạt SLA, 751.15 good tokens/s, cancelled=0; [raw export](runs/22273/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 15.00% đạt SLA, 272.46 good tokens/s, cancelled=0; [raw export](runs/22273/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22274

**Mục đích:** Recovery of 22220; confirm N[48].

**Quan sát:** Slurm CANCELLED; 0 exports. Failure is not a completed benchmark. User requested cancel and resubmit unchanged pending job to test queue behavior.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained.

[stdout](runs/22274.out) · [stderr](runs/22274.err) · [thư mục artifacts](runs/22274/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/02-P8-TP2_D8-TP4-EP4-a2-confirm; original failed logs preserved.

## Job 22280

**Mục đích:** Recovery of 22221; sweep N[16, 32].

**Quan sát:** Slurm CANCELLED; 0 exports. Failure is not a completed benchmark. Cancelled while PENDING, Start=None, elapsed=0; replaced by job 22294 with tested on-demand NIXL patch. Frozen original retry remains unchanged.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Prefill EP2 is a distinct variant to align FP8 expert shards.

[stdout](runs/22280.out) · [stderr](runs/22280.err) · [thư mục artifacts](runs/22280/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/03-P8-TP8-EP2_D8-TP4-EP4-a2-sweep; original failed logs preserved.

## Job 22294

**Mục đích:** Recovery of 22221; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm COMPLETED; 5 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Prefill EP2 is a distinct variant to align FP8 expert shards. Transport patch: hetero-tp-request-descriptors-v1.

[stdout](runs/22294.out) · [stderr](runs/22294.err) · [thư mục artifacts](runs/22294/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/03-P8-TP8-EP2_D8-TP4-EP4-a3-sweep; original failed logs preserved.

- confirm/N32: 95.87% đạt SLA, 1422.96 good tokens/s, cancelled=0; [raw export](runs/22294/confirm/n32/artifacts/profile_export_aiperf.json).

- sweep/N16: 100.00% đạt SLA, 834.55 good tokens/s, cancelled=0; [raw export](runs/22294/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 98.82% đạt SLA, 1419.14 good tokens/s, cancelled=0; [raw export](runs/22294/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 78.64% đạt SLA, 1292.36 good tokens/s, cancelled=0; [raw export](runs/22294/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 67.90% đạt SLA, 1299.88 good tokens/s, cancelled=0; [raw export](runs/22294/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22300

**Mục đích:** Recovery of 22234; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm CANCELLED; 0 exports. Failure is not a completed benchmark. User requested cancel and resubmit unchanged pending job to test queue behavior.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained. Transport patch: hetero-tp-request-descriptors-v1.

[stdout](runs/22300.out) · [stderr](runs/22300.err) · [thư mục artifacts](runs/22300/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/08-P8-TP2_D8-TP8-EP8-a1-sweep; original failed logs preserved.

## Job 22305

**Mục đích:** Recovery of 22222; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm CANCELLED; 0 exports. Failure is not a completed benchmark. User requested cancel and resubmit unchanged pending job to test queue behavior.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained. Transport patch: hetero-tp-request-descriptors-v1.

[stdout](runs/22305.out) · [stderr](runs/22305.err) · [thư mục artifacts](runs/22305/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/04-P8-TP4_D8-TP8-EP8-a2-sweep; original failed logs preserved.

## Job 22413

**Mục đích:** Recovery of 22232; confirm N[16].

**Quan sát:** Slurm CANCELLED; 0 exports. Failure is not a completed benchmark. User requested cancel and resubmit unchanged pending job to test queue behavior.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained.

[stdout](runs/22413.out) · [stderr](runs/22413.err) · [thư mục artifacts](runs/22413/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/06-P12-TP4_D4-TP4-EP4-a2-confirm; original failed logs preserved.

## Job 22414

**Mục đích:** Recovery of 22220; confirm N[48].

**Quan sát:** Slurm COMPLETED; 1 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained.

[stdout](runs/22414.out) · [stderr](runs/22414.err) · [thư mục artifacts](runs/22414/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/02-P8-TP2_D8-TP4-EP4-a2-confirm; original failed logs preserved.

- confirm/N48: 86.17% đạt SLA, 1479.32 good tokens/s, cancelled=0; [raw export](runs/22414/confirm/n48/artifacts/profile_export_aiperf.json).

## Job 22415

**Mục đích:** Recovery of 22222; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm COMPLETED; 5 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained. Transport patch: hetero-tp-request-descriptors-v1.

[stdout](runs/22415.out) · [stderr](runs/22415.err) · [thư mục artifacts](runs/22415/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/04-P8-TP4_D8-TP8-EP8-a2-sweep; original failed logs preserved.

- confirm/N48: 97.44% đạt SLA, 1912.30 good tokens/s, cancelled=0; [raw export](runs/22415/confirm/n48/artifacts/profile_export_aiperf.json).

- sweep/N16: 100.00% đạt SLA, 910.22 good tokens/s, cancelled=0; [raw export](runs/22415/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 99.42% đạt SLA, 1462.13 good tokens/s, cancelled=0; [raw export](runs/22415/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 95.75% đạt SLA, 1744.23 good tokens/s, cancelled=0; [raw export](runs/22415/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 90.95% đạt SLA, 1788.65 good tokens/s, cancelled=0; [raw export](runs/22415/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22416

**Mục đích:** Recovery of 22232; confirm N[16].

**Quan sát:** Slurm COMPLETED; 1 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained.

[stdout](runs/22416.out) · [stderr](runs/22416.err) · [thư mục artifacts](runs/22416/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/06-P12-TP4_D4-TP4-EP4-a2-confirm; original failed logs preserved.

- confirm/N16: 100.00% đạt SLA, 828.11 good tokens/s, cancelled=0; [raw export](runs/22416/confirm/n16/artifacts/profile_export_aiperf.json).

## Job 22417

**Mục đích:** Recovery of 22234; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm COMPLETED; 5 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained. Transport patch: hetero-tp-request-descriptors-v1.

[stdout](runs/22417.out) · [stderr](runs/22417.err) · [thư mục artifacts](runs/22417/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/08-P8-TP2_D8-TP8-EP8-a1-sweep; original failed logs preserved.

- confirm/N32: 94.21% đạt SLA, 1233.68 good tokens/s, cancelled=0; [raw export](runs/22417/confirm/n32/artifacts/profile_export_aiperf.json).

- sweep/N16: 89.77% đạt SLA, 666.52 good tokens/s, cancelled=0; [raw export](runs/22417/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 91.03% đạt SLA, 1089.79 good tokens/s, cancelled=0; [raw export](runs/22417/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 86.47% đạt SLA, 1202.92 good tokens/s, cancelled=0; [raw export](runs/22417/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 79.38% đạt SLA, 615.97 good tokens/s, cancelled=1; [raw export](runs/22417/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22468

**Mục đích:** Recovery of 22236; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm COMPLETED; 4 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Prefill EP2 is a distinct variant to align FP8 expert shards. Transport patch: hetero-tp-request-descriptors-v1.

[stdout](runs/22468.out) · [stderr](runs/22468.err) · [thư mục artifacts](runs/22468/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/10-P8-TP8-EP2_D8-TP2-EP2-a1-sweep; original failed logs preserved.

- sweep/N16: 80.72% đạt SLA, 574.18 good tokens/s, cancelled=0; [raw export](runs/22468/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 62.60% đạt SLA, 686.56 good tokens/s, cancelled=0; [raw export](runs/22468/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 51.90% đạt SLA, 639.09 good tokens/s, cancelled=0; [raw export](runs/22468/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 39.88% đạt SLA, 569.57 good tokens/s, cancelled=0; [raw export](runs/22468/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22509

**Mục đích:** Recovery of 22238; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm FAILED; 0 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Prefill EP2 is a distinct variant to align FP8 expert shards.

[stdout](runs/22509.out) · [stderr](runs/22509.err) · [thư mục artifacts](runs/22509/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/11-P8-TP8-EP2_D8-TP8-EP8-a1-sweep; original failed logs preserved.

## Job 22517

**Mục đích:** Recovery of 22240; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm COMPLETED; 5 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained. Transport patch: hetero-tp-request-descriptors-v1.

[stdout](runs/22517.out) · [stderr](runs/22517.err) · [thư mục artifacts](runs/22517/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/13-P4-TP2_D12-TP4-EP4-a1-sweep; original failed logs preserved.

- confirm/N16: 98.67% đạt SLA, 837.15 good tokens/s, cancelled=0; [raw export](runs/22517/confirm/n16/artifacts/profile_export_aiperf.json).

- sweep/N16: 91.76% đạt SLA, 691.90 good tokens/s, cancelled=0; [raw export](runs/22517/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 86.39% đạt SLA, 1024.23 good tokens/s, cancelled=0; [raw export](runs/22517/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 80.59% đạt SLA, 1109.96 good tokens/s, cancelled=0; [raw export](runs/22517/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 65.97% đạt SLA, 984.81 good tokens/s, cancelled=0; [raw export](runs/22517/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22524

**Mục đích:** Recovery of 22234; sweep N[48].

**Quan sát:** Slurm COMPLETED; 1 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained. Transport patch: hetero-tp-request-descriptors-v1.

[stdout](runs/22524.out) · [stderr](runs/22524.err) · [thư mục artifacts](runs/22524/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/08-P8-TP2_D8-TP8-EP8-a3-sweep; original failed logs preserved.

- sweep/N48: 62.26% đạt SLA, 785.31 good tokens/s, cancelled=0; [raw export](runs/22524/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22532

**Mục đích:** Recovery of 22245; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm COMPLETED; 5 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Original worker TP/EP arrangement retained. Transport patch: hetero-tp-request-descriptors-v1.

[stdout](runs/22532.out) · [stderr](runs/22532.err) · [thư mục artifacts](runs/22532/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/16-P12-TP2_D4-TP4-EP4-a1-sweep; original failed logs preserved.

- confirm/N16: 100.00% đạt SLA, 776.25 good tokens/s, cancelled=0; [raw export](runs/22532/confirm/n16/artifacts/profile_export_aiperf.json).

- sweep/N16: 91.46% đạt SLA, 640.97 good tokens/s, cancelled=0; [raw export](runs/22532/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 85.61% đạt SLA, 979.41 good tokens/s, cancelled=0; [raw export](runs/22532/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 36.47% đạt SLA, 521.40 good tokens/s, cancelled=0; [raw export](runs/22532/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 18.88% đạt SLA, 299.64 good tokens/s, cancelled=0; [raw export](runs/22532/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 22538

**Mục đích:** Recovery of 22238; sweep N[16, 32].

**Quan sát:** Slurm FAILED; 0 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Prefill EP2 is a distinct variant to align FP8 expert shards.

[stdout](runs/22538.out) · [stderr](runs/22538.err) · [thư mục artifacts](runs/22538/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/11-P8-TP8-EP2_D8-TP8-EP8-a2-sweep; original failed logs preserved.

## Job 22750

**Mục đích:** Recovery of 22238; sweep N[16, 32].

**Quan sát:** Slurm COMPLETED; 2 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Prefill EP2 is a distinct variant to align FP8 expert shards.

[stdout](runs/22750.out) · [stderr](runs/22750.err) · [thư mục artifacts](runs/22750/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/11-P8-TP8-EP2_D8-TP8-EP8-a3-sweep; original failed logs preserved.

- sweep/N16: 97.17% đạt SLA, 906.64 good tokens/s, cancelled=0; [raw export](runs/22750/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 94.08% đạt SLA, 1373.62 good tokens/s, cancelled=0; [raw export](runs/22750/sweep/n32/artifacts/profile_export_aiperf.json).

## Job 22778

**Mục đích:** Recovery of 22238; sweep N[40, 48].

**Quan sát:** Slurm FAILED; 0 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Prefill EP2 is a distinct variant to align FP8 expert shards.

[stdout](runs/22778.out) · [stderr](runs/22778.err) · [thư mục artifacts](runs/22778/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/11-P8-TP8-EP2_D8-TP8-EP8-a4-sweep; original failed logs preserved.

## Job 22809

**Mục đích:** Recovery of 22238; sweep N[16, 32, 40, 48].

**Quan sát:** Slurm COMPLETED; 5 exports. Failure is not a completed benchmark.

**Bài học:** Fixed distinct NCCL ports and bounded cold-path warmup. Prefill EP2 is a distinct variant to align FP8 expert shards. Transport patch: equal-tp8-request-descriptors-v1.

[stdout](runs/22809.out) · [stderr](runs/22809.err) · [thư mục artifacts](runs/22809/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-repair/11-P8-TP8-EP2_D8-TP8-EP8-a5-sweep; original failed logs preserved.

- confirm/N32: 95.38% đạt SLA, 1507.96 good tokens/s, cancelled=0; [raw export](runs/22809/confirm/n32/artifacts/profile_export_aiperf.json).

- sweep/N16: 98.15% đạt SLA, 933.50 good tokens/s, cancelled=0; [raw export](runs/22809/sweep/n16/artifacts/profile_export_aiperf.json).

- sweep/N32: 93.02% đạt SLA, 1393.62 good tokens/s, cancelled=0; [raw export](runs/22809/sweep/n32/artifacts/profile_export_aiperf.json).

- sweep/N40: 89.50% đạt SLA, 1624.14 good tokens/s, cancelled=0; [raw export](runs/22809/sweep/n40/artifacts/profile_export_aiperf.json).

- sweep/N48: 86.06% đạt SLA, 1708.25 good tokens/s, cancelled=0; [raw export](runs/22809/sweep/n48/artifacts/profile_export_aiperf.json).

## Job 23102

**Mục đích:** Repeat N48 and increase N52/N56 using full 60/120/30 measurements; stop raising load after a failed gate.

**Quan sát:** Slurm COMPLETED; 2 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23102.out) · [stderr](runs/23102.err) · [thư mục artifacts](runs/23102/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/control-load

- confirm/N48: 97.46% đạt SLA, 1911.08 good tokens/s, cancelled=0; [raw export](runs/23102/confirm/n48/artifacts/profile_export_aiperf.json).

- confirm/N52: 98.86% đạt SLA, 2096.88 good tokens/s, cancelled=0; [raw export](runs/23102/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23103

**Mục đích:** Decode graphs for every batch 1..64; remove padding to coarse graph sizes. Other workers and model precision unchanged.

**Quan sát:** Slurm COMPLETED; 2 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23103.out) · [stderr](runs/23103.err) · [thư mục artifacts](runs/23103/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/dense-decode-graphs

- confirm/N48: 97.47% đạt SLA, 1933.05 good tokens/s, cancelled=0; [raw export](runs/23103/confirm/n48/artifacts/profile_export_aiperf.json).

- confirm/N52: 98.73% đạt SLA, 2123.30 good tokens/s, cancelled=0; [raw export](runs/23103/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23104

**Mục đích:** Independent N48 repeat, then GPU traces under separate 48-request diagnostic traffic; traces never used as performance scores.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23104.out) · [stderr](runs/23104.err) · [thư mục artifacts](runs/23104/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/profile-control

- confirm/N48: 97.47% đạt SLA, 1910.32 good tokens/s, cancelled=0; [raw export](runs/23104/confirm/n48/artifacts/profile_export_aiperf.json).

## Job 23106

**Mục đích:** Repeat N48 and increase N52/N56 using full 60/120/30 measurements; stop raising load after a failed gate.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23106.out) · [stderr](runs/23106.err) · [thư mục artifacts](runs/23106/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/control-load-retry-2

- confirm/N56: 97.05% đạt SLA, 2057.87 good tokens/s, cancelled=0; [raw export](runs/23106/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 23109

**Mục đích:** Decode graphs for every batch 1..64; remove padding to coarse graph sizes. Other workers and model precision unchanged.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23109.out) · [stderr](runs/23109.err) · [thư mục artifacts](runs/23109/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/dense-decode-graphs-retry-2

- confirm/N56: 96.48% đạt SLA, 2069.20 good tokens/s, cancelled=0; [raw export](runs/23109/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 23113

**Mục đích:** Independent full repeat at N52 after a higher passing goodput in the control load search; confirm stability before promotion.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23113.out) · [stderr](runs/23113.err) · [thư mục artifacts](runs/23113/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/load-best-repeat

- confirm/N52: 97.24% đạt SLA, 1986.39 good tokens/s, cancelled=0; [raw export](runs/23113/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23114

**Mục đích:** Prefill chunk 4096 versus original 8192; keep decode, KV, model, NIXL patch and client protocol unchanged.

**Quan sát:** Slurm COMPLETED; 2 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23114.out) · [stderr](runs/23114.err) · [thư mục artifacts](runs/23114/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/prefill-chunk4096

- confirm/N48: 97.60% đạt SLA, 1962.70 good tokens/s, cancelled=0; [raw export](runs/23114/confirm/n48/artifacts/profile_export_aiperf.json).

- confirm/N52: 98.81% đạt SLA, 2140.10 good tokens/s, cancelled=0; [raw export](runs/23114/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23115

**Mục đích:** Decode DeepGEMM MoE runner versus original auto/Triton; profile MoE kernel fraction up to 29.2%. Separate quality validation required before promotion.

**Quan sát:** Slurm COMPLETED; 2 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23115.out) · [stderr](runs/23115.err) · [thư mục artifacts](runs/23115/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/decode-deepgemm

- confirm/N48: 97.44% đạt SLA, 1904.20 good tokens/s, cancelled=0; [raw export](runs/23115/confirm/n48/artifacts/profile_export_aiperf.json).

- confirm/N52: 98.78% đạt SLA, 2085.67 good tokens/s, cancelled=0; [raw export](runs/23115/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23128

**Mục đích:** Standalone N52 control with the old chunk 8192; measure cold deployment reproducibility.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23128.out) · [stderr](runs/23128.err) · [thư mục artifacts](runs/23128/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/s2-control-n52

- confirm/N52: 97.14% đạt SLA, 1977.08 good tokens/s, cancelled=0; [raw export](runs/23128/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23129

**Mục đích:** Standalone N52 confirmation of the current best chunk 4096.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23129.out) · [stderr](runs/23129.err) · [thư mục artifacts](runs/23129/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/s2-chunk4096-n52

- confirm/N52: 97.39% đạt SLA, 2033.03 good tokens/s, cancelled=0; [raw export](runs/23129/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23130

**Mục đích:** Combine the independently measured chunk 4096 and dense decode graphs; compare with chunk-only at the same N52.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23130.out) · [stderr](runs/23130.err) · [thư mục artifacts](runs/23130/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/s2-chunk4096-dense-n52

- confirm/N52: 97.43% đạt SLA, 2078.96 good tokens/s, cancelled=0; [raw export](runs/23130/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23131

**Mục đích:** Larger prefill chunk 16384 versus 8192/4096; test batching throughput against TTFT and startup time.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23131.out) · [stderr](runs/23131.err) · [thư mục artifacts](runs/23131/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/s2-chunk16384-n52

- confirm/N52: 90.92% đạt SLA, 1741.20 good tokens/s, cancelled=0; [raw export](runs/23131/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23146

**Mục đích:** Unranked diagnostic; not a contest P/D deployment or accuracy gate

**Quan sát:** Slurm COMPLETED; 132 diagnostic responses.

**Bài học:** Output correctness and performance are separate; preserve failed output checks.

[stdout](runs/23146.out) · [stderr](runs/23146.err) · [thư mục artifacts](runs/23146/)

**Ghi chú lịch sử file:** Frozen payload: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/s2-output-monolithic

## Job 23264

**Mục đích:** Matched DeepGEMM control for the DeepEP pilot, chunk 4096, coarse decode graph cap 64.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23264.out) · [stderr](runs/23264.err) · [thư mục artifacts](runs/23264/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/s2-deepgemm-control-n52

- confirm/N52: 97.37% đạt SLA, 2018.01 good tokens/s, cancelled=0; [raw export](runs/23264/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23265

**Mục đích:** FP8 E4M3 KV on both P/D versus matched BF16 chunk-4096 control. Accuracy is required before any promotion.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23265.out) · [stderr](runs/23265.err) · [thư mục artifacts](runs/23265/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/s2-fp8-kv-n52

- confirm/N52: 97.33% đạt SLA, 1996.26 good tokens/s, cancelled=0; [raw export](runs/23265/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23266

**Mục đích:** Independent standalone N52 repeat of s2-chunk4096-dense-n52 after 2078.96 good tokens/s; candidate ranking remains provisional.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23266.out) · [stderr](runs/23266.err) · [thư mục artifacts](runs/23266/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s2-repeat-best

- confirm/N52: 97.43% đạt SLA, 2079.18 good tokens/s, cancelled=0; [raw export](runs/23266/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23267

**Mục đích:** Independent standalone N52 repeat of s2-chunk4096-n52 after 2033.03 good tokens/s; candidate ranking remains provisional.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23267.out) · [stderr](runs/23267.err) · [thư mục artifacts](runs/23267/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s2-repeat-runner

- confirm/N52: 97.39% đạt SLA, 2032.13 good tokens/s, cancelled=0; [raw export](runs/23267/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23272

**Mục đích:** DeepEP low-latency FP8 dispatch versus matched DeepGEMM control; TP/EP and BF16 KV retained.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23272.out) · [stderr](runs/23272.err) · [thư mục artifacts](runs/23272/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/s2-deepep-ll-n52

- confirm/N52: 96.35% đạt SLA, 1957.15 good tokens/s, cancelled=0; [raw export](runs/23272/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23286

**Mục đích:** Independent standalone N52; same twice-measured BF16 chunk4096/dense-graph configuration. Only concurrency changes.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23286.out) · [stderr](runs/23286.err) · [thư mục artifacts](runs/23286/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s3-control-n52

- confirm/N52: 97.42% đạt SLA, 2075.11 good tokens/s, cancelled=0; [raw export](runs/23286/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23287

**Mục đích:** Independent standalone N54; same twice-measured BF16 chunk4096/dense-graph configuration. Only concurrency changes.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23287.out) · [stderr](runs/23287.err) · [thư mục artifacts](runs/23287/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s3-best-n54

- confirm/N54: 97.33% đạt SLA, 2111.91 good tokens/s, cancelled=0; [raw export](runs/23287/confirm/n54/artifacts/profile_export_aiperf.json).

## Job 23324

**Mục đích:** Limit each prefill batch to one request at chunk4096; test completion/TTFT against partially packed two-request batches observed in logs.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23324.out) · [stderr](runs/23324.err) · [thư mục artifacts](runs/23324/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-04/s4-prefill-single-n52

- confirm/N52: 97.44% đạt SLA, 2082.09 good tokens/s, cancelled=0; [raw export](runs/23324/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23325

**Mục đích:** Route prefill round-robin instead of inherited cache_aware policy; test initial burst balance on the cache-busted workload. Decode routing retained.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23325.out) · [stderr](runs/23325.err) · [thư mục artifacts](runs/23325/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-04/s4-prefill-roundrobin-n52

- confirm/N52: 98.93% đạt SLA, 2402.64 good tokens/s, cancelled=0; [raw export](runs/23325/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23437

**Mục đích:** Independent standalone N56; same twice-measured BF16 chunk4096/dense-graph configuration. Only concurrency changes.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23437.out) · [stderr](runs/23437.err) · [thư mục artifacts](runs/23437/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s3-best-n56

- confirm/N56: 97.22% đạt SLA, 2141.20 good tokens/s, cancelled=0; [raw export](runs/23437/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 23495

**Mục đích:** Independent standalone N60; same twice-measured BF16 chunk4096/dense-graph configuration. Only concurrency changes.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23495.out) · [stderr](runs/23495.err) · [thư mục artifacts](runs/23495/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s3-best-n60

- confirm/N60: 94.51% đạt SLA, 2133.30 good tokens/s, cancelled=0; [raw export](runs/23495/confirm/n60/artifacts/profile_export_aiperf.json).

## Job 23505

**Mục đích:** Independent N58 midpoint between N56 and N60; same confirmed BF16 chunk4096/dense-graph serving config.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23505.out) · [stderr](runs/23505.err) · [thư mục artifacts](runs/23505/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s3-midpoint

- confirm/N58: 96.76% đạt SLA, 2157.31 good tokens/s, cancelled=0; [raw export](runs/23505/confirm/n58/artifacts/profile_export_aiperf.json).

## Job 23516

**Mục đích:** Independent confirmation at N58 after 2157.31 good tokens/s in load refinement; no automatic submission promotion.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23516.out) · [stderr](runs/23516.err) · [thư mục artifacts](runs/23516/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s3-best-load-repeat

- confirm/N58: 96.83% đạt SLA, 2159.79 good tokens/s, cancelled=0; [raw export](runs/23516/confirm/n58/artifacts/profile_export_aiperf.json).

## Job 23576

**Mục đích:** Independent repeat of job23325 round-robin prefill at N52; validate the 2402.64 single-point result.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23576.out) · [stderr](runs/23576.err) · [thư mục artifacts](runs/23576/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s5-rr-repeat-n52

- confirm/N52: 98.93% đạt SLA, 2397.72 good tokens/s, cancelled=0; [raw export](runs/23576/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23577

**Mục đích:** Round-robin N50 versus N52: test more ITL headroom with identical serving and official client.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23577.out) · [stderr](runs/23577.err) · [thư mục artifacts](runs/23577/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s5-rr-n50

- confirm/N50: 99.04% đạt SLA, 2350.25 good tokens/s, cancelled=0; [raw export](runs/23577/confirm/n50/artifacts/profile_export_aiperf.json).

## Job 23583

**Mục đích:** Round-robin N54 only after the N52 repeat passes SLA/output research checks; stop advancing after a failure.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23583.out) · [stderr](runs/23583.err) · [thư mục artifacts](runs/23583/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s5-rr-n54

- confirm/N54: 95.34% đạt SLA, 2358.64 good tokens/s, cancelled=0; [raw export](runs/23583/confirm/n54/artifacts/profile_export_aiperf.json).

## Job 23607

**Mục đích:** Fresh full round-robin N52 control, followed by separate 52-request GPU profiling; identify the new decode bottleneck without profiling ranked traffic.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23607.out) · [stderr](runs/23607.err) · [thư mục artifacts](runs/23607/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-06/s6-rr-profile-n52

- confirm/N52: 98.93% đạt SLA, 2400.02 good tokens/s, cancelled=0; [raw export](runs/23607/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23608

**Mục đích:** FP8 E4M3 KV on P and D versus BF16 on the confirmed round-robin N52 configuration; test decode bandwidth/ITL headroom. Accuracy required before any submission use.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23608.out) · [stderr](runs/23608.err) · [thư mục artifacts](runs/23608/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-06/s6-rr-fp8kv-n52

- confirm/N52: 10.75% đạt SLA, 254.47 good tokens/s, cancelled=0; [raw export](runs/23608/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23609

**Mục đích:** Decode DeepGEMM versus auto/Triton on the same round-robin N52 configuration and identical dense graph list; test the fuller decode batch after routing changed.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23609.out) · [stderr](runs/23609.err) · [thư mục artifacts](runs/23609/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-06/s6-rr-deepgemm-n52

- confirm/N52: 84.71% đạt SLA, 2021.39 good tokens/s, cancelled=0; [raw export](runs/23609/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23616

**Mục đích:** Independent N53 midpoint between N52 and N54; same round-robin prefill, BF16 chunk4096/dense-graph serving config.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23616.out) · [stderr](runs/23616.err) · [thư mục artifacts](runs/23616/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s5-rr-midpoint

- confirm/N53: 98.88% đạt SLA, 2433.41 good tokens/s, cancelled=0; [raw export](runs/23616/confirm/n53/artifacts/profile_export_aiperf.json).

## Job 23773

**Mục đích:** Independent confirmation at N53 after 2433.41 good tokens/s in load refinement; no automatic submission promotion.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23773.out) · [stderr](runs/23773.err) · [thư mục artifacts](runs/23773/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s5-rr-best-repeat

- confirm/N53: 98.88% đạt SLA, 2438.47 good tokens/s, cancelled=0; [raw export](runs/23773/confirm/n53/artifacts/profile_export_aiperf.json).

## Job 23776

**Mục đích:** Decode CUTLASS block-FP8 MoE versus auto/Triton. Round-robin N52 profile attributes 27.4% summed decode kernel duration to MoE; actual staged implementation supports SM90 block FP8.

**Quan sát:** Slurm FAILED; 0 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23776.out) · [stderr](runs/23776.err) · [thư mục artifacts](runs/23776/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/s7-rr-cutlass-n52

## Job 23777

**Mục đích:** Decode FlashInfer attention versus FA3, BF16 KV unchanged on both roles. FA3 attention is 19.6% of summed decode kernel duration; leave prefill attention, page size and KV transport unchanged.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23777.out) · [stderr](runs/23777.err) · [thư mục artifacts](runs/23777/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/s7-rr-flashinfer-n52

- confirm/N52: 98.95% đạt SLA, 2440.39 good tokens/s, cancelled=0; [raw export](runs/23777/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23778

**Mục đích:** Decode MNNVL fused allreduce versus auto/TRTLLM. Collectives are 20.1% of summed decode kernel duration; exact staged resolver permits SM90 single-node TP8. No quantized communication.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23778.out) · [stderr](runs/23778.err) · [thư mục artifacts](runs/23778/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/s7-rr-mnnvl-n52

- confirm/N52: 99.01% đạt SLA, 2592.16 good tokens/s, cancelled=0; [raw export](runs/23778/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23780

**Mục đích:** Architecture pilot: decode DP-attention8 (attention TP1), EP8, DeepEP low-latency FP8 dispatch and DeepGEMM. Retain 8+8 P/D split and RR N52 to isolate the architecture package before any 12+4 reallocation or speculation.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23780.out) · [stderr](runs/23780.err) · [thư mục artifacts](runs/23780/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/s8-rr-dpa8-deepep-n52

- confirm/N52: 98.87% đạt SLA, 2549.20 good tokens/s, cancelled=0; [raw export](runs/23780/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23839

**Mục đích:** Repeat isolated decode mnnvl N52 only after at least 2% goodput improvement over both round-robin controls and research output checks.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23839.out) · [stderr](runs/23839.err) · [thư mục artifacts](runs/23839/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s7-mnnvl-repeat-n52

- confirm/N52: 99.01% đạt SLA, 2592.92 good tokens/s, cancelled=0; [raw export](runs/23839/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23859

**Mục đích:** Independent architecture repeat only after at least 2% validated N52 goodput gain over both controls.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23859.out) · [stderr](runs/23859.err) · [thư mục artifacts](runs/23859/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s8-dpa8-repeat-n52

- confirm/N52: 98.87% đạt SLA, 2538.08 good tokens/s, cancelled=0; [raw export](runs/23859/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23904

**Mục đích:** Single additional factor on successful MNNVL N52; compare matched MNNVL, not old auto backend.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23904.out) · [stderr](runs/23904.err) · [thư mục artifacts](runs/23904/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/s9-mnnvl-flashinfer-n52

- confirm/N52: 99.02% đạt SLA, 2631.09 good tokens/s, cancelled=0; [raw export](runs/23904/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23905

**Mục đích:** Single additional factor on successful MNNVL N52; compare matched MNNVL, not old auto backend.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23905.out) · [stderr](runs/23905.err) · [thư mục artifacts](runs/23905/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/s9-mnnvl-chunk2048-n52

- confirm/N52: 98.77% đạt SLA, 2331.35 good tokens/s, cancelled=0; [raw export](runs/23905/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23906

**Mục đích:** Single additional factor on successful MNNVL N52; compare matched MNNVL, not old auto backend.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23906.out) · [stderr](runs/23906.err) · [thư mục artifacts](runs/23906/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/s9-mnnvl-chunk8192-n52

- confirm/N52: 98.87% đạt SLA, 2547.85 good tokens/s, cancelled=0; [raw export](runs/23906/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23924

**Mục đích:** Try decode mnnvl N54 only after reproduced N52 gain, SLA at least 95% and mean ITL at most 19.3 ms.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23924.out) · [stderr](runs/23924.err) · [thư mục artifacts](runs/23924/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s7-mnnvl-n54

- confirm/N54: 98.90% đạt SLA, 2634.03 good tokens/s, cancelled=0; [raw export](runs/23924/confirm/n54/artifacts/profile_export_aiperf.json).

## Job 23934

**Mục đích:** Architecture N54 only after reproduced N52 gain, SLA at least 95% and mean ITL at most 19.3ms.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23934.out) · [stderr](runs/23934.err) · [thư mục artifacts](runs/23934/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/s8-dpa8-n54

- confirm/N54: 98.75% đạt SLA, 2555.42 good tokens/s, cancelled=0; [raw export](runs/23934/confirm/n54/artifacts/profile_export_aiperf.json).

## Job 23973

**Mục đích:** Independent matched replication of small MNNVL+FlashInfer gain; no higher load or engine change.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23973.out) · [stderr](runs/23973.err) · [thư mục artifacts](runs/23973/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-repeat1-n52

- confirm/N52: 99.02% đạt SLA, 2632.06 good tokens/s, cancelled=0; [raw export](runs/23973/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23974

**Mục đích:** Independent matched replication of small MNNVL+FlashInfer gain; no higher load or engine change.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23974.out) · [stderr](runs/23974.err) · [thư mục artifacts](runs/23974/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-mnnvl-control-n52

- confirm/N52: 99.01% đạt SLA, 2594.03 good tokens/s, cancelled=0; [raw export](runs/23974/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 23975

**Mục đích:** Independent matched replication of small MNNVL+FlashInfer gain; no higher load or engine change.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/23975.out) · [stderr](runs/23975.err) · [thư mục artifacts](runs/23975/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-repeat2-long-n52

- confirm/N52: 99.02% đạt SLA, 2632.61 good tokens/s, cancelled=0; [raw export](runs/23975/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 24009

**Mục đích:** One independent full-protocol MNNVL N54 replication after sealed job23924 gained 1.6004% over both N52 controls mean; same load and execution, no N56 or automatic promotion.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24009.out) · [stderr](runs/24009.err) · [thư mục artifacts](runs/24009/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-mnnvl-repeat-n54

- confirm/N54: 98.90% đạt SLA, 2629.51 good tokens/s, cancelled=0; [raw export](runs/24009/confirm/n54/artifacts/profile_export_aiperf.json).

## Job 24131

**Mục đích:** Bounded N54 load extension after three full-protocol N52 combo observations and long12/12 pass; no N56 or automatic promotion

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24131.out) · [stderr](runs/24131.err) · [thư mục artifacts](runs/24131/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-n54

- confirm/N54: 98.91% đạt SLA, 2654.17 good tokens/s, cancelled=0; [raw export](runs/24131/confirm/n54/artifacts/profile_export_aiperf.json).

## Job 24174

**Mục đích:** Fresh N52 comparator for independently replicated combo N54

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24174.out) · [stderr](runs/24174.err) · [thư mục artifacts](runs/24174/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-fresh-n52

- confirm/N52: 99.02% đạt SLA, 2632.96 good tokens/s, cancelled=0; [raw export](runs/24174/confirm/n52/artifacts/profile_export_aiperf.json).

## Job 24175

**Mục đích:** One independent combo N54 replication against fresh N52 and all previous N52/N54 runs

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24175.out) · [stderr](runs/24175.err) · [thư mục artifacts](runs/24175/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-repeat-n54

- confirm/N54: 98.91% đạt SLA, 2658.20 good tokens/s, cancelled=0; [raw export](runs/24175/confirm/n54/artifacts/profile_export_aiperf.json).

## Job 24189

**Mục đích:** N54 control and N56 capacity after two passing N54 measurements; no N58 or automatic promotion

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24189.out) · [stderr](runs/24189.err) · [thư mục artifacts](runs/24189/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-control-n54-v2

- confirm/N54: 98.91% đạt SLA, 2658.55 good tokens/s, cancelled=0; [raw export](runs/24189/confirm/n54/artifacts/profile_export_aiperf.json).

## Job 24190

**Mục đích:** N54 control and N56 capacity after two passing N54 measurements; no N58 or automatic promotion

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24190.out) · [stderr](runs/24190.err) · [thư mục artifacts](runs/24190/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-probe-n56

- confirm/N56: 98.80% đạt SLA, 2671.11 good tokens/s, cancelled=0; [raw export](runs/24190/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24235

**Mục đích:** Confirm N56 or modest N58 probe after full passing N56; noN60 or promotion

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24235.out) · [stderr](runs/24235.err) · [thư mục artifacts](runs/24235/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-repeat-n56

- confirm/N56: 98.80% đạt SLA, 2669.80 good tokens/s, cancelled=0; [raw export](runs/24235/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24236

**Mục đích:** Confirm N56 or modest N58 probe after full passing N56; noN60 or promotion

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24236.out) · [stderr](runs/24236.err) · [thư mục artifacts](runs/24236/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-probe-n58

- confirm/N58: 98.68% đạt SLA, 2667.97 good tokens/s, cancelled=0; [raw export](runs/24236/confirm/n58/artifacts/profile_export_aiperf.json).

## Job 24263

**Mục đích:** Profile new MNNVL+FlashInfer N56 winner after throughput plateau atN58; trace only after full ranked measurement, no profiler in score

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24263.out) · [stderr](runs/24263.err) · [thư mục artifacts](runs/24263/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-profile-n56

- confirm/N56: 98.80% đạt SLA, 2667.46 good tokens/s, cancelled=0; [raw export](runs/24263/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24272

**Mục đích:** Direct H200N50 validation of empirical H100→H200 transfer estimate calibrated atsameN52;notnewbackend

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24272.out) · [stderr](runs/24272.err) · [thư mục artifacts](runs/24272/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-cross-platform-n50

- confirm/N50: 99.13% đạt SLA, 2601.63 good tokens/s, cancelled=0; [raw export](runs/24272/confirm/n50/artifacts/profile_export_aiperf.json).

## Job 24281

**Mục đích:** Test prefill batching or parallelism after N56/N58 ITLplateau and TTFTgrowth;compareunchangedcomboN56,notassumedbottleneck

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24281.out) · [stderr](runs/24281.err) · [thư mục artifacts](runs/24281/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-prefill-single-n56

- confirm/N56: 98.78% đạt SLA, 2621.29 good tokens/s, cancelled=0; [raw export](runs/24281/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24282

**Mục đích:** Test prefill batching or parallelism after N56/N58 ITLplateau and TTFTgrowth;compareunchangedcomboN56,notassumedbottleneck

**Quan sát:** Slurm FAILED; 0 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24282.out) · [stderr](runs/24282.err) · [thư mục artifacts](runs/24282/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-prefill-tp8-n56

## Job 24291

**Mục đích:** Profile-guided prefill-only DeepGEMM trial; decode unchanged

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24291.out) · [stderr](runs/24291.err) · [thư mục artifacts](runs/24291/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-deepgemm-n56

- confirm/N56: 98.82% đạt SLA, 2715.84 good tokens/s, cancelled=0; [raw export](runs/24291/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24320

**Mục đích:** Fresh N56 control / corrected TP8EP2 prefill / prefill weight prefetch, same decode and protocol

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24320.out) · [stderr](runs/24320.err) · [thư mục artifacts](runs/24320/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-combo-control-n56-v3

- confirm/N56: 98.80% đạt SLA, 2670.32 good tokens/s, cancelled=0; [raw export](runs/24320/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24321

**Mục đích:** Fresh N56 control / corrected TP8EP2 prefill / prefill weight prefetch, same decode and protocol

**Quan sát:** Slurm FAILED; 0 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24321.out) · [stderr](runs/24321.err) · [thư mục artifacts](runs/24321/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-tp8ep2-n56

## Job 24322

**Mục đích:** Fresh N56 control / corrected TP8EP2 prefill / prefill weight prefetch, same decode and protocol

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24322.out) · [stderr](runs/24322.err) · [thư mục artifacts](runs/24322/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-prefetch-n56

- confirm/N56: 98.80% đạt SLA, 2665.57 good tokens/s, cancelled=0; [raw export](runs/24322/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24327

**Mục đích:** Replicate reviewed job 24291 (+1.81% versus 24263); compare new control 24320, retain full protocol and quality gates

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24327.out) · [stderr](runs/24327.err) · [thư mục artifacts](runs/24327/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-deepgemm-repeat-n56

- confirm/N56: 98.82% đạt SLA, 2716.79 good tokens/s, cancelled=0; [raw export](runs/24327/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24352

**Mục đích:** New prefill backend may move capacity frontier: one N58 test, not a blind N60 increase. Existing combo N58 plateaued; independent DeepGEMM N56 confirmation remains required.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24352.out) · [stderr](runs/24352.err) · [thư mục artifacts](runs/24352/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-deepgemm-n58

- confirm/N58: 98.71% đạt SLA, 2718.08 good tokens/s, cancelled=0; [raw export](runs/24352/confirm/n58/artifacts/profile_export_aiperf.json).

## Job 24375

**Mục đích:** Repair TP8-to-TP8 warmup timeout using exact previously GPU-validated equal-TP transport patch; no model/kernel/load changes

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24375.out) · [stderr](runs/24375.err) · [thư mục artifacts](runs/24375/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-tp8ep2-equal-n56

- confirm/N56: 2.00% đạt SLA, 28.33 good tokens/s, cancelled=0; [raw export](runs/24375/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24376

**Mục đích:** Measure prefill CUDA graph startup cost versus scored goodput; decode graphs and kernels unchanged

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24376.out) · [stderr](runs/24376.err) · [thư mục artifacts](runs/24376/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-no-graph-n56

- confirm/N56: 98.43% đạt SLA, 2530.83 good tokens/s, cancelled=0; [raw export](runs/24376/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24425

**Mục đích:** Confirmed DeepGEMM backend: test chunk8192 interaction at N56 with graph settings retained. No combination with unresolved graph-off trial.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24425.out) · [stderr](runs/24425.err) · [thư mục artifacts](runs/24425/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-deepgemm-chunk8192-n56

- confirm/N56: 98.94% đạt SLA, 2722.28 good tokens/s, cancelled=0; [raw export](runs/24425/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24426

**Mục đích:** Complete auto/DeepGEMM × prefill-graph-on/off comparison; one flag versus confirmed DeepGEMM N56. Decode unchanged. Separate startup savings and throughput.

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24426.out) · [stderr](runs/24426.err) · [thư mục artifacts](runs/24426/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-deepgemm-no-graph-n56

- confirm/N56: 72.72% đạt SLA, 1590.31 good tokens/s, cancelled=0; [raw export](runs/24426/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24428

**Mục đích:** Bracket confirmed DeepGEMM N56/N58 with N54; do not assume higher concurrency wins

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24428.out) · [stderr](runs/24428.err) · [thư mục artifacts](runs/24428/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-deepgemm-n54

- confirm/N54: 98.93% đạt SLA, 2693.16 good tokens/s, cancelled=0; [raw export](runs/24428/confirm/n54/artifacts/profile_export_aiperf.json).

## Job 24429

**Mục đích:** Profile changed prefill backend after scored N56 benchmark; compare separate N48 diagnostic with prior 24263, 4 prefill/32 decode steps, 16 ranks

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24429.out) · [stderr](runs/24429.err) · [thư mục artifacts](runs/24429/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s10-prefill-deepgemm-profile-n56

- confirm/N56: 98.82% đạt SLA, 2715.55 good tokens/s, cancelled=0; [raw export](runs/24429/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24526

**Mục đích:** Fresh DeepGEMM chunk4096 N56 control for chunk and backend trials

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24526.out) · [stderr](runs/24526.err) · [thư mục artifacts](runs/24526/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s11-dg-control-n56

- confirm/N56: 98.82% đạt SLA, 2715.83 good tokens/s, cancelled=0; [raw export](runs/24526/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24527

**Mục đích:** Independent repeat of the provisional 0.20 percent chunk8192 gain

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24527.out) · [stderr](runs/24527.err) · [thư mục artifacts](runs/24527/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s11-dg-chunk8192-repeat-n56

- confirm/N56: 98.94% đạt SLA, 2718.69 good tokens/s, cancelled=0; [raw export](runs/24527/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24528

**Mục đích:** Test intermediate prefill chunk size; isolate batch geometry while holding backend and load fixed

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24528.out) · [stderr](runs/24528.err) · [thư mục artifacts](runs/24528/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s11-dg-chunk6144-n56

- confirm/N56: 98.94% đạt SLA, 2737.01 good tokens/s, cancelled=0; [raw export](runs/24528/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24529

**Mục đích:** Source-compatible Hopper FP8 HPC-Ops prefill trial; decode unchanged

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24529.out) · [stderr](runs/24529.err) · [thư mục artifacts](runs/24529/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s11-hpc-prefill-n56

- confirm/N56: 98.94% đạt SLA, 2732.46 good tokens/s, cancelled=0; [raw export](runs/24529/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24538

**Mục đích:** H200 decode-only HPC-Ops trial motivated by measured H100 gain; retain confirmed DeepGEMM prefill and compare fresh24526

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24538.out) · [stderr](runs/24538.err) · [thư mục artifacts](runs/24538/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s11-hpc-decode-n56

- confirm/N56: 98.83% đạt SLA, 2733.20 good tokens/s, cancelled=0; [raw export](runs/24538/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24544

**Mục đích:** One bounded N58 chunk8192 trial after two positive N56 chunk observations; compare historical N58 chunk4096 and fresh N56 chunk8192

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24544.out) · [stderr](runs/24544.err) · [thư mục artifacts](runs/24544/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s11-dg-chunk8192-n58

- confirm/N58: 98.85% đạt SLA, 2786.70 good tokens/s, cancelled=0; [raw export](runs/24544/confirm/n58/artifacts/profile_export_aiperf.json).

## Job 24573

**Mục đích:** Independent repetition of provisional 0.78 percent prefill chunk6144 gain; compare new chunk4096 control

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24573.out) · [stderr](runs/24573.err) · [thư mục artifacts](runs/24573/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s12-dg-chunk6144-repeat-n56

- confirm/N56: 98.94% đạt SLA, 2737.41 good tokens/s, cancelled=0; [raw export](runs/24573/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24574

**Mục đích:** Independent repetition of provisional 0.61 percent HPC-Ops prefill gain; compare new DeepGEMM control

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24574.out) · [stderr](runs/24574.err) · [thư mục artifacts](runs/24574/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s12-hpc-prefill-repeat-n56

- confirm/N56: 98.82% đạt SLA, 2728.96 good tokens/s, cancelled=0; [raw export](runs/24574/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24575

**Mục đích:** Fresh confirmed DeepGEMM chunk4096 N56 control to detect drift before interpreting sub-percent gains

**Quan sát:** Slurm COMPLETED; 1 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24575.out) · [stderr](runs/24575.err) · [thư mục artifacts](runs/24575/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s12-dg-fresh-control-n56

- confirm/N56: 98.82% đạt SLA, 2714.10 good tokens/s, cancelled=0; [raw export](runs/24575/confirm/n56/artifacts/profile_export_aiperf.json).

## Job 24588

**Mục đích:** Repeat provisional N58 chunk8192 peak against a new same-load chunk4096 control; do not rely only on historical comparator

**Quan sát:** Slurm TIMEOUT; 0 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24588.out) · [stderr](runs/24588.err) · [thư mục artifacts](runs/24588/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s12-dg-chunk8192-repeat-n58

## Job 24589

**Mục đích:** Fresh DeepGEMM chunk4096 N58 control to isolate chunk effect at the new operating point

**Quan sát:** Slurm PENDING; 0 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24589.out) · [stderr](runs/24589.err) · [thư mục artifacts](runs/24589/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s12-dg-fresh-control-n58

## Job 24639

**Mục đích:** One N58 HPC-Ops decode trial from verified N56 ITL headroom; retain DeepGEMM prefill chunk4096 and compare same-load control24589

**Quan sát:** Slurm PENDING; 0 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24639.out) · [stderr](runs/24639.err) · [thư mục artifacts](runs/24639/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s13-hpc-decode-n58

## Job 24640

**Mục đích:** Combine independently repeated HPC-Ops prefill with independently repeated chunk6144; compare24574 for chunk and24573 for runner effects

**Quan sát:** Slurm PENDING; 0 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24640.out) · [stderr](runs/24640.err) · [thư mục artifacts](runs/24640/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s13-hpc-prefill-chunk6144-n56

## Job 24641

**Mục đích:** Add verified HPC-Ops decode to repeated HPC-Ops prefill at N56; isolate decode against24574 and prefill against24538

**Quan sát:** Slurm PENDING; 0 canonical exports. Failed deployment is not a benchmark result.

**Bài học:** Separate full measurements from diagnostic profiling. Stop increasing load at the first failed latency/error gate.

[stdout](runs/24641.out) · [stderr](runs/24641.err) · [thư mục artifacts](runs/24641/)

**Ghi chú lịch sử file:** Frozen payload before submission: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/s13-hpc-both-n56

## Đã lưu và giới hạn

- Raw logs, scripts/snapshot đang có, worker.sh và config.txt ở `runs/<job>/`; stdout/stderr ở `runs/<job>.out` và `.err`. Job đang chờ có thể chưa có log.
- Lượt đo hoàn thành có `inputs.json`, `profile_export.jsonl`, `profile_export_aiperf.json`, CSV, phase manifest và client logs. Dataset và metrics từng request được giữ; không chỉ giữ điểm tốt nhất.
- `profile_export.jsonl` hiện chứa metadata/timing/metrics; không tuyên bố đã lưu toàn bộ văn bản output của mọi request.
- Job chưa đi tới client có thể không có dataset/export/client versions; job lỗi trước benchmark không có score hợp lệ.
- Images và model weights dùng từ /scratch, chưa được copy thành archive riêng; manifest không đảm bảo external image/checkpoint sẽ không thay đổi.
- Checksum được tạo sau khi job kết thúc, dùng kiểm tra file có đổi sau mốc này; không chứng minh trạng thái nguyên gốc ở lúc submit. Giữ snapshot lỗi cũ, không sửa chúng để giả thành script đã thành công.
- `comparison.json`, `RESULTS.md`, `summary.json` là báo cáo có thể tái tạo từ raw; watcher cập nhật khi có thêm dữ liệu. Manifest không hash các báo cáo dẫn xuất.
- Profiler GPU traces hiện có trong diagnostic-profile/ của các job: 23104, 23607, 24263, 24429; profiling riêng, không dùng làm điểm benchmark. Accuracy của BTC chưa được xác nhận.

Đọc [bảng số đo](RESULTS.md) và [tổng hợp máy đọc được](comparison.json).

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


## Complete retained journey and reasoning records — 2026-10-19T19:25:31.405094+00:00

The user clarified that the request covers the whole journey, not only the last NCCL interpretation: preserve each hypothesis, assessment, result, improvement and next decision. Added a 32-stage source-linked retrospective and a 194-job index, backed by an audit of 247 retained Markdown records. All audited source/archive/Git hashes match at the stated audit commit. 127 jobs have dedicated purpose/observation/lesson sections; an ID mention or plan is not a certified complete review. No claim recovers every unrecorded chat statement. [Entry point](/home/apacsc42/workspace/reports/research-journey-20261019/journal/README.md). New milestones must retain the question, control/change, evidence, units, assessment, next decision and corrections, then capture/commit/push promptly.

This is a documentation and coverage milestone only. Scheduler/credit snapshots remain dated; no job query/submission, model rerun, budget change, authentication, slides or background automation was performed. Existing GPU jobs are left alone.


## Research continuation — 20 October 2026

Reviewed five H200 and three H100 completed full-model runs. H200 N58 HPC-Ops interaction now repeats across three deployments; N60 reaches a new individual 2990.151 good output tokens/s, awaiting treatment repeat. Submitted H200 24912/24913/24914/24915; 24912 fresh auto N60 passes at 2838.853, the other three were Resources-pending at 00:51 UTC. H100 phase-specific inference mode is flat and closed. Three bounded 8-GPU collective screens preserve numerical gates and expose launch-cadence ambiguity, then reject forced one-shot and disabling PDL. Keep native AUTO+PDL; no full-model patch for these losses. New H100 native decode FlashInfer/FA3 pair 222027→222028 was R/H at 00:51–00:52 UTC, with 3072 SU maximum reserve. No attention score yet.

Published Used 34035.199 SU, Balance 29794.134 SU, In Doubt 170.667 SU (08:40 SGT publication); Balance already excludes prepayment. Total unreleased maximum reservation 3413.333 SU, internal headroom 13551.468 SU under unchanged cap/buffer. Existing access reused, no authentication or automation changes. Full official accuracy unverified. [Full hypothesis/control/result/assessment/next-decision entry](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261020-serving-and-collective.md). Earlier states below are historical.


## Reproduced N60 and observed polling submissions — 20 October 2026

H200 24913 passes at 2989.175 good output tokens/s, independently repeating 24738 = 2990.151 and +5.295% above fresh auto control 24912. Auto N62 24914 passes at 2890.878; keep HPC-Ops N62 24915 position. H100 222027/222028 both pass at 2420.945/2401.284: FA3 lowers mean TTFT but loses 0.812% goodput and increases ITL, so retain FlashInfer. Raw scored failures are 22 TTFT breaches per run and zero ITL/error/cancel breaches; all rank CPU/GPU traces inspected, without claiming a large CPU bottleneck.

Submitted three matched off/on/receive-2 pilots per platform: H200 24926/24927/24928 and serial PBS 222048→222049→222050. At 01:43 UTC H200 new group plus old 24915 were Resources-pending; PBS R/H/H. New bounded resource collector and phase markers are deployed in those frozen bundles; actual telemetry coverage and observer overhead are not yet verified. No numerical/workload change. Earlier “collector not implemented” status is historical. Local fixtures and seven source-file hashes agree across both images; control/candidate differ only in polling interval after observation settings match.

Published Used 34972.443 SU, Balance 29027.557 SU; four terminal charges reconcile 937.244 SU. New maximum reserve 4608 SU, internal headroom 11419.557 SU under unchanged cap/buffer. Existing access reused, no authentication, background AI, slides or official accuracy claim. [Full result/insight/next-decision entry](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261020-receive-polling.md). Older states below retain their timestamps.

