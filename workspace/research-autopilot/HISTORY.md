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

## 18 October 2026, 14:34 UTC — H200 running, VPN client expired

H200 24573 is running, other four jobs pending. No new terminal measurement. H100 access failed before SSH: no matching live VPN process. Retained client log shows IKE SA expired at 14:08:45 UTC; tmux session presence does not prove tunnel health. Current PBS queue/results/credit are unknown, not unchanged by assumption. About 24 hours elapsed since last documented VPN restoration, consistent with configured lifetime but not proof of a server limit or cache validity. Preserve authentication cache. No reauthentication/DUO request triggered. PBS jobs are not cancelled merely by a local VPN disconnect. No new submissions or budget reconciliation.

Sanitised evidence: [live status](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1434/STATUS.md). Earlier snapshots are historical; autopilot remains off.

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

# Autonomous research history

- 2026-10-15: user requested autonomous wake-ups; authenticated CLI smoke passed.

## Lượt Qwen — 2026-10-15 15:48 UTC

- **GPU:** Slurm 23778 (MNNVL) và 23780 (attention DP + DeepEP) vẫn `PENDING (Resources)`. Watcher PID 2305942 còn sống, registry tiếp tục cập nhật. PBS không có job đang chờ/chạy; lịch sử chỉ có bốn probe 220453/220454/220456/220457.pbs111 đã kết thúc. Không gửi job mới.
- **Kết quả thực:** xác nhận 23777 đạt 2.440,39 good tokens/s, SLA 98,95%, ITL 18,71 ms, không lỗi/hủy; cả tám rank dùng decode FlashInfer. Chỉ tăng 1,68% so với control N52 và 0,08% so với N53 23773; giữ nguyên ngưỡng tự lặp 2%. Diagnostic 7/8 chưa chứng minh accuracy BTC. 23776 lỗi illegal memory access khi capture CUDA graph qua CUTLASS; chưa có benchmark hợp lệ, chưa xác định kernel gốc.
- **NSCC:** 12/24 shard đã xác minh SHA256 chính thức, chưa có lỗi tải; AIPerf đã xác minh đủ 815.869.952 byte. SGLang image đang chuyển, snapshot có 4,037,541,888 / 26.476.240.896 byte. Hai transfer hiện có tiếp tục chạy; không tạo bản sao.
- **Chuẩn bị:** tăng kiểm tra preflight để chặn model chưa xác minh xong, kiểm kích thước/digest chính thức và SHA256 images; đã cập nhật bản remote. 5/5 ca CPU và kiểm tra PBS placement/payload đóng băng đạt. Preflight remote trả `ready=false`, đúng vì tài sản chưa đủ.
- **Ngân sách:** ledger mới dùng 70,543 SU, còn 63.929,457 SU. Đã lập [nscc-budget.json](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json), tính cả probe trong cap 4.096 SU; còn 4.025,457 SU, chưa giữ chỗ job mới.

Bước tiếp: khi tài sản đủ và preflight đạt, kiểm lại toàn bộ job/credit, ghi dự trù 1.024 SU trước khi gửi duy nhất baseline N32, tối đa 16 GPU/30 phút, giữ ít nhất 13.000 SU. Hiện chỉ còn chờ queue và transfer, không còn chuẩn bị độc lập cần làm trong lượt này; kết thúc sớm sau khoảng 6 phút.

[Chứng cứ và kết quả kiểm tra](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1542UTC/wake-summary.json) · [Phân tích H200](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/PLAN.md). Đã bổ sung sổ hỏi đáp tiếng Việt.

## Lượt Qwen — 2026-10-15 16:03 UTC

- **H200:** Slurm **23778** chuyển sang `RUNNING` lúc 16:01:05 UTC trên g1/g4; cả tám rank đã khởi tạo MNNVL. Đang capture CUDA graph, chưa có benchmark hợp lệ. **23780** vẫn `PENDING (Resources)`. Watcher **2305942** còn sống, giữ lock và cập nhật registry; không tạo watcher/job mới.
- **Kết quả:** chưa có phép đo mới so với lượt trước. Giữ 23777 ở mức một quan sát 2.440,39 good tokens/s, chưa đạt ngưỡng tự lặp 2%; 23776 vẫn là deployment lỗi, không tính là phép đo. Chưa xác minh accuracy BTC.
- **NSCC:** model chính thức đã hoàn tất lúc 15:54:55 UTC: đủ **24/24 shard**, **236.426.193.880 byte** weights, manifest 33 file khớp kích thước và SHA256 LFS chính thức. Preflight thực chỉ còn chặn image SGLang: snapshot 16:01 UTC có **16.029.483.008 / 26.476.240.896 byte (~60,5%)**. AIPerf đã đủ và băm SHA256 đạt. Transfer **2861397** tiếp tục chạy; downloader model đã kết thúc sau khi hoàn tất.
- **PBS/ngân sách:** queue của mình trống; accounting chi tiết vẫn chỉ có bốn probe **220453/220454/220456/220457.pbs111** đã kết thúc. Ledger mốc 00:00:02 Singapore: dùng **70,543 SU**, dư **63.929,457 SU**, không có SU giữ chỗ. Cap commissioning còn **4.025,457 SU**; chưa reserve/gửi baseline.

Đã lưu manifest hoàn tất, preflight thực, accounting, log startup MNNVL và hash chứng cứ; cập nhật README, plan và sổ hỏi đáp. Bước tiếp: watcher thu đầy đủ kết quả/output của 23778; khi SGLang đủ và SHA256 đạt, kiểm lại queue/credit rồi reserve **1.024 SU** trước duy nhất baseline N32 (16 GPU, tối đa 30 phút, giữ dư ít nhất 13.000 SU). Phần chuẩn bị độc lập đã hoàn tất; kết thúc lượt kiểm tra, để watcher và transfer hiện có tiếp tục.

[Chứng cứ](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1600UTC/wake-summary.json) · [Ngân sách](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json).

## Lượt Qwen — 2026-10-15 16:32 UTC

- **Kết quả mới H200:** **23778 (MNNVL)** hoàn tất, đạt **2.592,16 good tokens/s**, SLA **99,01%** (1.595/1.611 request), ITL **17,13 ms**, TTFT **516,28 ms**, không lỗi/hủy. Tăng **8,01%** so với control N52 **23607**, **6,30%** so với N53 **23773**; TTFT tăng **169,44 ms** so với control. Đã đối chiếu export đầy đủ 60/120/30, log tám rank MNNVL và diagnostic 7/8 không có lỗi mới; accuracy BTC chưa xác minh.
- **Queue thực:** **23839** (lặp MNNVL N52 do watcher tự gửi lúc 16:11:17 UTC) và **23780** (attention DP + DeepEP) đều `PENDING (Priority)` tại kiểm tra. Watcher **2305942** còn sống, giữ lock, cập nhật kết quả. Đã xác nhận payload lượt lặp giữ nguyên; N54 vẫn phải qua cổng xác nhận cũ. Không gửi thêm job trong lượt này.
- **NSCC:** transfer hiện có đã hoàn tất lúc **16:14:09 UTC**, hai image khớp SHA256; model trước đó đã đủ 24 shard và manifest chính thức. Tuy nhiên một lần SSH không tương tác trả `Permission denied (password)`. Không thử lại xác thực; chưa chạy được preflight mới, chưa xác minh PBS/credit hiện tại và chưa gửi baseline.
- **Ngân sách:** giữ cap **4.096 SU**, không reserve mới. Ledger thành công gần nhất lúc 16:00 UTC: đã dùng **70,543 SU**, dư **63.929,457 SU**, còn **4.025,457 SU** trong cap; đây là số lịch sử. Đã ghi rõ tình trạng chưa làm mới trong sổ ngân sách.

Đã lưu export, snapshot scheduler/registry, đối chiếu và SHA256 chứng cứ; cập nhật plan, README và sổ hỏi đáp. Bước tiếp: watcher thu lượt lặp **23839**; sau khi phiên SSH NSCC được xác thực lại, chạy preflight, đối soát toàn bộ PBS/credit rồi reserve **1.024 SU** trước duy nhất baseline N32, tối đa 16 GPU/30 phút và giữ dư ít nhất 13.000 SU. Phần chuẩn bị độc lập đã xong; kết thúc sớm vì job H200 đang chờ và NSCC bị chặn xác thực.

[Chứng cứ](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1630UTC/wake-summary.json) · [Đối chiếu MNNVL](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1630UTC/mnnvl-review.json) · [Ngân sách](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json).

## Khôi phục SSH và chạy baseline — 2026-10-15 17:01 UTC

- Lịch tự chạy đã hoàn tất ba lượt15:42,16:00,16:30UTC; không gửi thông báo vào chat gốc.
- H200: MNNVL23778 đạt2592,16 goodtokens/s, SLA99,01%, không lỗi/hủy; cao hơn N53 trước6,30%. Lượt xác nhận23839 và attentionDP23780 còn chờGPU tại16:59UTC.
- NSCC: đã nối lại SSH, đổi ControlPersist sang24giờ (không lưu mật khẩu). Model và hai images hoàn tất, preflight ready=true và frozen checksums đều đạt.
- Đã submit baseline N32 **220486.pbs111**, **RUNNING16H100** lúc17:00:42UTC, walltime tối đa30phút. Đã reserve1024SU, cap commissioning4096SU giữ nguyên; chưa có benchmark Qwen NSCC.
- Next: thu log/benchmark và đối soát chi phí220486; giữ nguyên queueH200. Không gửi thêm PBSjob khi baseline còn chạy.

# Báo cáo Qwen — 2026-10-15 19:15 UTC

- H200: MNNVL23778 vẫn cao nhất2592,16 goodtokens/s, SLA99,01%. DP-attention+DeepEP23780 đạt2549,20, SLA98,87%, không lỗi/hủy. Hai lượt xác nhận23839(MNNVL),23859(DP) cònPENDING Resources tại19:14UTC.
- NSCC220486 lỗi quyền ghi Triton cache; retry220489 đã qua decode CUDA graph nhưng prefill vẫn load checkpoint khi hết readiness600giây, exit1 sau10m10s, không có benchmark export. Raw artifacts mới đã collect vào collected/220489.pbs111/20261015T191428376429Z.
- Credit NSCC: ledger03:00Singapore dùng539,307SU, còn63460,693SU, không khoản giữ trước; capcommissioning4096 còn3556,693SU. Không có PBSjob active.
- Codex wake bị quota limit trong lượt17:01 và17:30/19:00; lượt17:01 đã sửa cache và gửi retry trước khi bị cắt. Controller Slurm vẫn hoạt động độc lập. Sửa wake để lỗi quota sẽ thử lại vào lần kiểm tra sau, không bỏ qua vì queue không đổi.
- Next: xác nhận quota Codex đã mở lại; inspect slow prefill checkpoint load, chuẩn bị retry với readiness phù hợp trong walltime30phút, giữ model/client/protocol. Không coi hai deployment lỗi là kết quả benchmark.



# Báo cáo Qwen — 2026-10-15 19:19 UTC

- Đã đọc POLICY và kiểm tra scheduler thật. H200 **23839** (lặp MNNVL), **23859** (lặp DP) vẫn `PENDING(Resources)`; watcher PID2305942 đang giữ lock, kết quả cũ đã được ghi.
- Đối chiếu export/log **23780**: **2.549,20 good tokens/s**, SLA **98,87%**, ITL16,96ms, TTFT596,44ms, không lỗi/hủy. Log xác nhận DP8/EP8, DeepEP và UCX đủ8rank; diagnostic7/8, chưa phải accuracy BTC. Cao hơn control23607 **6,22%**, thấp hơn MNNVL23778 **1,66%**; chưa có lượt lặp mới.
- NSCC **220489.pbs111** không có benchmark: decode đã ready, prefill vẫn đọc shard khi hết600giây. Đã giữ log/hash, tạo bundle retry chỉ sửa hạn readiness chung1.200giây, router120giây; năm kiểm tra hàm chờ, shell/checksum và preflight asset đều đạt. Model/client/N32/protocol giữ nguyên.
- Đã giữ trước **1.024 SU trước qsub**, gửi đúng một retry **220562.pbs111**,16H100/30phút. PBS lúc19:18UTC báo **Q(aiq2)** vì thiếu bộ nhớ khả dụng; chưa chạy, chưa có số đo H100. Sáu job cũ đều terminal và đã đối soát. Ledger dùng **539,307 SU**, số dư **63.460,693 SU**; trần commissioning4.096 còn **2.532,693 SU sau giữ trước**.
- Bằng chứng: [inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1915UTC/). Đã cập nhật README NSCC, PLAN wave8 và sổ hỏi đáp.
- Tiếp theo: khi220562 chạy, kiểm tra prefill có ready trước1.200giây và collect artifact/export đầy đủ; đối soát chi phí sau khi kết thúc. Giữ nguyên vị trí hai job H200. Các job hiện đều chờ; không còn bước chuẩn bị độc lập cần làm trong lượt này nên kết thúc sớm.


# Báo cáo Qwen — 2026-10-15 19:48 UTC

- **Baseline H100 đầu tiên hoàn tất:** NSCC **220562.pbs111**, exit0,16H100,23phút33giây. N32 đạt **1.565,16 good tokens/s**, SLA **100% (966/966)**, ITL **18,57ms**, TTFT **346,63ms**, không lỗi/hủy; export đúng **60/120/30**,4000/200.
- Đã thu stdout PBS, export, response và hash; checksum payload đạt. Hai đường P/D đều chat HTTP200,16rank khởi tạo NIXL UCX. Diagnostic **7/8**, chỉ lỗi reverse đã biết; **chưa xác nhận accuracy BTC hoặc long-context H100**. Đây là một lượt đo.
- Prefill ready sau1.104/1.105giây, router1.150giây, warm P/D1.193giây. Runtime ghi tải weight prefill851giây, graph115–119giây; chưa xác định nguyên nhân tải chậm. Đã bổ sung Q&A và README bằng số đo thực tế.
- PBS: cả7job của mình đã terminal, không gửi job mới. Ledger03:40Singapore vẫn dùng539,307SU, balance62.436,693SU, In Doubt1.024SU; giữ nguyên dự phòng local1.024SU đến khi accounting cập nhật. Trần4.096SU còn **2.532,693SU sau dự phòng**; không trừ In Doubt lần nữa khỏi balance.
- H200 **23839/23859** vẫn `PENDING(Resources)`; watcher PID2305942 sống và giữ lock, các kết quả cũ đã được ghi. Giữ nguyên vị trí queue.
- Bằng chứng: [baseline review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1930UTC/baseline-review.json), [artifact cuối](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220562.pbs111/20261015T194718195272Z/).
- Tiếp: đối soát ledger sau completion, kiểm tra long-context H100 và xác nhận lại N32 trước khi chọn tải cao hơn. Đã hoàn tất thu/đánh giá baseline; hai job GPU còn lại đều đang chờ, không còn chuẩn bị độc lập cần làm trong lượt này nên kết thúc.

# Báo cáo Qwen — 2026-10-15 20:07 UTC

- Đã gửi NSCC **220575.pbs111**,16H100 tối đa45phút, một lần load model đo N32/34/36/38/40/42 đầy đủ60/120/30; dừng tăng khi failSLA/error. Trạng thái gần nhấtQUEUED.
- H200 đủ5/5slot:23839,23859 giữ nguyên; mới23904(MNNVL+FlashInfer),23905(MNNVLchunk2048),23906(MNNVLchunk8192), đềuN52. CPU/cap/checksum đạt; GPU chưa đo.
- Hai pilotH100 MNNVL04 vàFlashInfer05 đã chuẩn bị, upload và kiểmSHA256, chưasubmit. Có12long-context checks riêng; chỉ gửi từngjob saukhi gate/budget đạt.
- Ledger04:00Singapore:đã dùng1343,147SU, balance62656,853SU trước reservejobmới. Reserve1536SU cho220575. Campaign mở từcommissioning4096 lên16384SU theo yêu cầu tiếp tục tận dụngGPU, giữ ít nhất13000SU dự phòng.
- Cron kiểm tra mỗi5phút, chỉ gọiCodex khi trạng thái đổi hoặc đến kỳresearch; quotaerror nghỉ30phút. HandoffPOLICY đã thay bằng trạng thái hiện tại và các bước có thể submit, tránh dừng khi vẫn còn pilot hợp lệ.
- BaselineH100220562:1565,16goodt/s,SLA100%. H200MNNVL23778:2592,16,SLA99,01%;accuracyBTCchưa xác minh.


# Báo cáo Qwen — 2026-10-15 20:13 UTC

- **NSCC 220575 đang chạy** trên 16 H100 từ 20:06:22 UTC. Snapshot 20:12:38 chưa có export benchmark hay output smoke; đã lưu raw artifacts và xác minh checksum payload.
- **H200: cả 5 job vẫn chờ tài nguyên** (23839, 23859, 23904–23906). Watcher hiện có vẫn hoạt động.
- Đã chuẩn bị cục bộ **pilot loader-prefetch-06**, qua kiểm tra cú pháp, checksum và giao thức. Chưa upload/submit/chạy GPU; giữ MNNVL04 và FlashInfer05 ưu tiên trước. Nguồn image xác nhận bật prefetch cũng đổi iterator sang một luồng; nguyên nhân prefill chậm chưa được xác định.
- Đã lưu thiết kế EAGLE3/vLLM cùng nguồn ghim phiên bản. Draft chưa xác nhận tương thích Instruct-2507-FP8; vLLM chưa có image kiểm chứng. Chưa có kết quả GPU mới.
- **Ngân sách:** đã dùng 1.343,147 SU; giữ reserve 1.536 SU cho 220575; còn 13.504,853 SU trong cap 16.384 SU. Đã cập nhật dưới lock, không gửi job mới.
- Tiếp theo: thu kết quả khi 220575 kết thúc; chỉ gửi MNNVL04 khi N32, short checks, queue và budget đạt gate. **Accuracy BTC vẫn chưa xác minh.**

Bằng chứng: [snapshot](../../2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2007UTC/), [phân tích loader](../../2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/LOADER_RESEARCH.md), [thiết kế nhánh tiếp](../../2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/README.md).


# Báo cáo Qwen — 2026-10-15 20:25 UTC

- **H200:** cả 5 job 23839, 23859, 23904–23906 vẫn `PENDING (Resources)`; watcher 3514431 còn sống. Không có phép đo mới.
- **NSCC:** chưa làm mới được trạng thái 220575. Helper không tìm thấy phiên VPN; SSH master còn tồn tại nhưng truy vấn PBS/credit qua kết nối cũ hết hạn sau 20 giây, không trả dữ liệu. Trạng thái xác nhận cuối là **RUNNING lúc 20:12:38 UTC**. Không thử xác thực mới, không gửi job.
- **Tiến triển:** đã chuẩn bị công cụ lấy mẫu CPU/page fault/I/O/NUMA của đúng cây tiến trình worker; kiểm tra CPU cục bộ đạt. Chưa upload, tích hợp hay chạy NSCC; các pilot 04/05/06 giữ nguyên. Source xác nhận expert bị bỏ qua sau khi iterator tạo tensor view; chưa chứng minh giảm I/O.
- **Ngân sách chưa làm mới:** ledger cuối dùng **1.343,147 SU**; tiếp tục giữ **1.536 SU** cho 220575, còn **13.504,853 SU** trong cap 16.384 SU theo số đã biết. Đã ghi trạng thái truy cập và dự phòng dưới lock.
- Tiếp theo: khi truy cập hiện có hoạt động, thu 220575 và làm mới toàn bộ queue/credit; chỉ gửi MNNVL04 rồi FlashInfer05 khi job trước terminal và đủ gate. **Accuracy BTC chưa xác minh.** Phần chuẩn bị độc lập của lượt này đã xong; kết thúc sớm, không chờ rỗng.

[Bằng chứng và lỗi truy cập](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2020UTC/wake-summary.json) · [Công cụ và giới hạn đo](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/STARTUP_SAMPLING.md).

# Báo cáo Qwen — 2026-10-15 20:40 UTC

- H200:23839,23859,23904,23905,23906 vẫnPENDING(Resources) tại20:38:55UTC. Watcher3514431 còn sống; không có phép đo mới.
- NSCC220575: trạng thái xác nhận gần nhấtRUNNING20:12:38UTC; chưa lấy được kết quả cuối do VPN mất phiên.20:39UTC đã thực hiện một lần kết nối lại gateway đúng.sg vớiTLSverification,20:40:05UTC client báoIPsec authentication failed,status0 / Authentication failed. Không cóDUOchallenge hiển thị; chưa xác định nguyên nhân từ chối. Không lặp thử mật khẩu.
- Giữ nguyên dự phòng1536SU cho220575 và không gửi thêmPBSjob khi trạng thái cũ chưa rõ. Không có dữ liệu để cập nhật credit.
- Kết quả tốt nhất đã xác nhận vẫnH200MNNVL2592,16goodt/s,SLA99,01%; H100baselineN32 đạt1565,16,SLA100%. Các pilot tiếp theo và công cụ phân tích startup đã chuẩn bị;accuracyBTCchưa xác minh.


## Đính chính VPN và bộ nhớ sau20:47UTC

Đã lấy log gốc: tunnel cũ ngắt doIKE SA expired lúc20:17:01UTC. Kiểmsource đúng
snx-rs6.5.1 xác nhận defaultIKE28800s, helper cũ khôngoverride; đã sửa helper
request86400s cho kết nối mới. Chưa kiểm chứng24giờ, gateway vẫn có thể ápgiới hạn.
Login thử20:47 cũng trảAuthentication failedstatus0; nguyên nhân xác thực chưa rõ,
không phải lỗiSSH. Người dùng báoWindows vẫn kết nối tốt24giờ. Chưa cóVPNmới.

Bộ nhớ tổng hợp: workspace/notes/README.md vàCURRENT.md; rootAGENTS.md yêu cầu
đọc trước khi tiếp tụcAPAC/VPN. Promptautopilot đã bắt buộc đọc/cập nhật bộ nhớ.


# Báo cáo Qwen — 2026-10-15 20:58 UTC

- **H200:** lúc 20:57:20 UTC, **23839 RUNNING** trên g[1,4], bắt đầu 20:50:37 UTC; **23859, 23904–23906 PENDING (Priority)**. Watcher 3514431 còn sống lúc 20:55:43 UTC. 23839 đang benchmark, chưa có export hoàn chỉnh; chưa có số đo mới.
- **NSCC:** helper lúc 20:55:43 UTC báo không có phiên VPN sống, trước bước SSH. Trạng thái xác nhận cuối của **220575.pbs111** vẫn là RUNNING lúc 20:12:38 UTC; kết quả cuối và credit hiện tại chưa xác minh. Không đăng nhập lại, không qsub.
- **Tiến triển:** hoàn thiện `analyze-startup.py` phân tích CPU/I/O từ log sampler. Kiểm tra offline đạt với PID tái sử dụng, counter thiếu/reset, khoảng lấy mẫu gián đoạn, dòng cuối chưa ghi xong và chống ghi đè. Raw own-child cũ được giữ nguyên; bản phân tích có nhãn kiểm tra CPU cục bộ. Công cụ chưa upload/tích hợp/chạy NSCC; pilot 04/05/06 giữ nguyên.
- **Ngân sách:** giữ dự phòng **1.536 SU** cho 220575. Ledger cuối 04:00 Singapore ghi used **1.343,147 SU**, balance **62.656,853 SU**; headroom sau dự phòng **13.504,853 SU** là số đã biết, không phải số dư live. Đã cập nhật dưới budget.lock; không thêm khoản dự trù.
- Đã cập nhật CURRENT, POLICY, kế hoạch và Q&A; sửa câu Q&A cũ dùng trần 4.096 SU thành mốc lịch sử, campaign hiện hành **16.384 SU**. **Accuracy BTC chưa xác minh.**
- Tiếp: watcher thu 23839 và chỉ mở N54 theo gate hiện có. Khi truy cập NSCC hoạt động, thu 220575, làm mới toàn bộ own queue/credit, rồi gửi MNNVL04 và FlashInfer05 lần lượt khi đủ gate. Hoàn tất phần chuẩn bị độc lập của lượt này; kết thúc sớm, không chờ rỗng.

[Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2055UTC/) · [Hướng dẫn phân tích startup](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/STARTUP_SAMPLING.md).


# Báo cáo Qwen — 2026-10-15 21:03 UTC

- **MNNVL H200 đã lặp độc lập:** 23839 hoàn tất exit0 lúc20:59:45UTC, đạt **2.592,92 goodtokens/s**, SLA99,0074%, ITL17,15ms, không lỗi/hủy. Trung bình với23778: **2.592,54**, chênh0,029%; cao hơn controlN52 8,02%. ITL giảm2,38ms nhưngTTFT tăng165,43ms so control.
- **Bằng chứng:** kiểm tra đầy đủ checksum hai manifest, payload, protocol60/120/30 và cả8rank khởi tạoMNNVL đều đạt. Diagnostic7/8, chỉ reverse đã biết; **accuracy BTC chưa xác minh**.
- **Queue lúc21:01:24UTC:** watcher3514431 còn sống, đã gửi N54 **23924** lúc21:00:05 theo gate cũ.23924,23859,23904–23906 đều **PENDING(Priority)**, đủcap5. Đã chuẩn bị tiêu chí đọcN54/so sánhwave9; không mởN56 hay gửijob trùng.
- **NSCC:** helper21:01:24UTC vẫn thiếu phiênVPN, trướcSSH; trạng thái cuối/kết quả220575 vàcredit chưa xác minh. Không đăng nhập lại/qsub. Giữ **1.536SU** dự trù; ledger04:00SGT used1.343,147SU/balance62.656,853SU là lịch sử, headroom13.504,853SU theo số đã biết. Trầncampaign16.384SU giữ nguyên.
- Đã cập nhật CURRENT, POLICY, kế hoạch, budget dướilock và Q&A. Khi có lại truy cậpNSCC: thu220575, làm mới ownqueue/credit rồi gửi04→05 khi đủgate. Phần độc lập của lượt này hoàn tất; kết thúc sớm, không chờ queue.

[Audit và scheduler](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2100UTC/) · [Kết quả lặp và bướcN54](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/MNNVL_REPEAT_REVIEW.md).


# Báo cáo Qwen — 2026-10-15 21:09 UTC

- **H200:** queue thực lúc **21:08:39UTC** có23859,23904–23906,23924 đều **PENDING(Priority)**, đủcap5. Watcher3514431 còn sống21:05:34UTC; chưa có số đo mới.
- **NSCC:** helper21:05:34UTC báo thiếu phiênVPN trướcSSH. Trạng thái/kết quả220575 vàcredit hiện tại chưa xác minh. Không đăng nhập lại/qsub; giữ **1.536SU** dự trù. Ledger04:00Singapore vàheadroom13.504,853SU là số lịch sử; trầncampaign16.384SU giữ nguyên.
- **Tiến triển:** chuẩn bị bộ đánh giá sweep offline cho220575, xác minh checksum, protocol60/120/30, thời gianphase, SLA/error/cancel và shortoutput so baselineH100. **11ca kiểm tra CPU đạt**. Tái tính1.565,161394goodtokens/s từ dữ liệu220562 cũ; không phải phép đo/repeat mới. Flagoffline không thay gatequeue/credit/budget; accuracyBTC chưa xác minh.
- Đã cập nhật CURRENT, POLICY, kế hoạch, budget dướilock và Q&A. Khi truy cập trở lại: thu220575, làm mới ownqueue/credit, đánh giáN32 rồi gửi04→05 lần lượt khi đủgate. Chuẩn bị độc lập đã xong; kết thúc sớm, không chờqueue.

[Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2105UTC/) · [Hướng dẫn thu và đánh giá sweep](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/LOAD_SWEEP_REVIEW.md).


# Báo cáo Qwen — 2026-10-15 21:52 UTC

- **H200 lúc21:50:29UTC:** 23859,23904–23906,23924 đều **PENDING(Resources)**, đủcap5; watcher3514431 còn sống. Chưa có số đo mới.
- **NSCC:** không có phiênVPN trướcSSH; kết quả/trạng thái220575 vàcredit hiện tại chưa xác minh. Không đăng nhập lại/qsub; giữ **1.536SU** dự trù. Ledger04:00Singapore vàheadroom13.504,853SU là lịch sử; trầncampaign16.384SU giữ nguyên.
- **Tiến triển:** audit3batchscript thực lưu ởSlurm khớp bảnfrozen; checksum vàworker đúng1factor đều đạt. Chuẩn bị bảng đọcwave9 với cả23778/23839, mean2.592,542986goodtokens/s vàTTFT/ITL. Ghi rõ configmetadata kế thừa thiếu/cũ; worker đúng dự kiến, chưa kiểmruntime. Không sửapayload đangqueue; chưa cóbenchmark/accuracy mới.
- Đã cập nhật CURRENT, POLICY, Q&A, kế hoạch vàbudget dướilock. Tiếp: watcher thuH200; khi có lại truy cậpNSCC, thu220575 vàđối soát ownqueue/credit trước04→05. Phần chuẩn bị độc lập đã xong; kết thúc sớm, không chờqueue.

[Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2150UTC/) · [Bảng đối chiếu wave9](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md).

## 2026-10-15 22:05–22:08UTC

- **H200 kiểm tra22:06:58UTC:**23859 RUNNING từ22:02:26 trên g1/g4;23904–23906,23924 PENDING(Resources), đủcap5; watcher còn sống. Chưa có benchmark mới.
- **Tiến triển:** audit repeat23859 khớp23780: checksum/scriptSlurm đạt,12file thực thi giống nhau, runtimeDP8/DeepEP đúng. Đã kiểm lại seal23780 và chuẩn bị [checklistthu/reviewN54](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/REPEAT_REVIEW.md). Weightload xong chưa chứng minh transport/benchmark đạt; snapshot22:06 chưa có export/smoke.
- **NSCC22:05:24UTC:** chưa có phiênVPN;220575/credit hiện tại chưa xác minh. Giữ1.536SU dự trù, trầncampaign16.384SU; không đăng nhập lại/qsub. Ledger04:00Singapore vẫn là lịch sử.
- Đã cập nhật CURRENT,POLICY,Q&A,plan vàbudget dướilock; không đổi payload hay tạo job/lịch. Tiếp: watcher thu23859 và xétgateN54; khi truy cậpNSCC trở lại, thu220575/ownqueue/credit rồi04→05. Hoàn tất phần chuẩn bị độc lập, kết thúc sớm.

[Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2205UTC/).


## Báo cáo Qwen — 2026-10-15 22:14 UTC

- **23859 hoàn tất exit0 lúc 22:11:34 UTC:** 2538,08 good tokens/s, SLA 98,87%, ITL 16,956 ms, không lỗi/hủy. Audit checksum, protocol, 8 rank NIXL, hai đường P/D và output non-regression đều đạt.
- **DP-attention đã lặp độc lập:** trung bình 2543,64 good tokens/s; chênh repeat −0,436%. Hơn control23607 5,98%, thấp hơn MNNVL trung bình 1,89%. So control, TTFT trung bình tăng 259,95 ms và ITL giảm 2,566 ms. Accuracy BTC chưa xác minh.
- **Queue lúc 22:12:35 UTC:** watcher đã gửi 23934 (DP N54) theo gate hiện có. Cả 23904–23906,23924,23934 đều PENDING(Resources), đủ cap5; watcher còn sống. Không gửi job trùng hay mở N56.
- **NSCC lúc 22:10:26 UTC:** chưa có phiên VPN; kết quả220575 và credit hiện tại chưa xác minh. Giữ 1536 SU dự trù, trần campaign16384 SU; không đăng nhập lại/qsub. Pilot04→05 chờ đủ gate truy cập, baseline, queue và credit.
- Đã cập nhật CURRENT, POLICY, Q&A, review, plan/budget dưới lock; lưu bằng chứng và lần audit CPU false-reject do artifact directory trước khi sửa. Phần việc độc lập hoàn tất, kết thúc sớm.

[Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/REPEAT_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2210UTC/).


# Báo cáo Qwen — 2026-10-15 22:17 UTC

- **H200 lúc 22:17:19 UTC:** 23904–23906,23924,23934 đều PENDING(Resources), đủ cap5; watcher còn sống khi kiểm tra22:15:28. Chưa có phép đo mới.
- **Tiến triển:** audit hai payload N54 với cả hai baseline N52 tương ứng đạt: script lưu trên Slurm khớp frozen, checksum đạt, 12file thực thi giống nhau; chỉ đổi tên/path/mục đích và tải52→54. Đã chuẩn bị bảng so sánh và hướng dẫn phân biệt gate mởjob với SLA benchmark; ghi rõ metadata kế thừa. Chưa xác minh runtimeN54 hay accuracyBTC.
- **NSCC lúc22:15:28 UTC:** không có phiênVPN trướcSSH; kết quả220575 và credit hiện tại chưa xác minh. Giữ1536SU dự trù, trầncampaign16384SU; không đăng nhập lại/qsub. Pilot04→05 chờ đủ gate truy cập, baseline, queue và credit.
- Đã cập nhật CURRENT,POLICY,Q&A,plan/budget dưới lock và lưu bằng chứng. Không thêm job/lịch, không mởN56. Phần chuẩn bị độc lập hoàn tất; kết thúc sớm, không chờ queue.

[Hướng dẫn N54](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2215UTC/).


## Báo cáo Qwen — 2026-10-15 22:57 UTC

- **H200 lúc 22:57:45 UTC:** 23904 RUNNING từ22:51:04 trên g1/g4;23905/23906/23924/23934 PENDING(Resources), đủcap5; watcher còn sống.
- **Tiến triển:** audit payload và runtime23904 đạt: scriptSlurm/checksum khớp, đủ8rankMNNVL+FlashInferdecode+NIXL/UCX, hai đườngP/Dwarmup,chunk4096 vàgraph64. So cả23778/23839 chỉ khácbackend attention vàseed engine tự sinh; đã ghi giới hạn seedAIPerf2026 không khóa seedengine. Chưa có sốđo mới/accuracyBTC.
- **NSCC lúc22:55:57 UTC:** chưa có phiênVPN trướcSSH;220575 vàcredit hiện tại chưa xác minh. Giữ1536SU dự trù vàtrần16384SU; khôngauth/qsub. Pilot04→05 chờ đủgate truycập/baseline/queue/credit.
- Đã cậpnhậtCURRENT,POLICY,Q&A,review vàplan/budget dướilock; giữrawlogprefix cùnghash. Không thêmjob/lịch/repeat/N56. Kếtthúc sau phầnviệc độclập; watcher tiếp tục thu kếtquả.

[Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2255UTC/).


## Báo cáo Qwen — 2026-10-16 00:19 UTC

- **23904 — MNNVL + FlashInfer:** **2631,09 goodtokens/s**, SLA 99,02%; hơn trung bình hai baseline **1,49%**. TTFT tăng 122,97 ms, ITL giảm 0,91 ms. Mới có một lượt, chưa xác nhận bằng repeat.
- **23905 — chunk2048:** **2331,35 goodtokens/s**, SLA 98,77%; goodput giảm **10,07%** dù ITL giảm 1,33 ms. TTFT tăng 676,50 ms. Runtime cũng đổi giới hạn graph prefill 4096→2048; chưa thể quy kết riêng cho chunk.
- Cả hai đã đối soát đủ giao thức 60/120/30, không lỗi/hủy; kiểm tra đầu ra 7/8, chỉ lỗi reverse đã biết. Checksum đạt cho 47 file mỗi run, gồm hai baseline và hai candidate. Accuracy BTC chưa xác minh.
- **H200 lúc 00:19:38 UTC:** 23906/23924/23934 PENDING(Resources), dùng 3/5 slot; watcher còn sống. Bước tiếp: thu ba job và kiểm tra graph thực của chunk8192. Không thêm job, repeat hay N56.
- **NSCC lúc 00:15:52 UTC:** chưa có phiên VPN sống; kết quả 220575 và credit hiện tại chưa xác minh. Giữ 1536 SU dự trù, trần campaign 16384 SU; lượt nghiên cứu này không đăng nhập lại hay qsub. Pilot 04→05 chờ đủ điều kiện truy cập, baseline, queue và credit.
- Đã cập nhật CURRENT, POLICY, Q&A, review và budget/plan; giữ artifact cùng các lần audit CPU và đính chính. Lượt này kết thúc sau phần việc độc lập; watcher tiếp tục thu kết quả.

[Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0015UTC/).


## Báo cáo Qwen — 2026-10-16 00:52 UTC

- **H200 kiểm tra 00:50:03 UTC:** 23906/23924/23934 đều PENDING(Resources), 3/5 slot; watcher còn sống. Chưa có số đo GPU mới.
- Đã chuẩn bị **công cụ đối soát N54**: qua 21 ca CPU, rehash và tái tính đúng bốn baseline đã lưu. So từng baseline và trung bình, kiểm tra bằng chứng thô; phân biệt thiếu export với điểm đo đủ nhưng fail SLA. Runtime N54 còn chờ.
- Khi tái tính bốn run cũ, goodput dùng thời gian profiling phase trong manifest; `benchmark_duration` lệch khoảng 2,8–4,0 ms. Đã ghi rõ convention và giữ các prototype/đính chính, không sửa số liệu cũ.
- **NSCC 00:46:05 UTC:** thiếu phiên VPN; 220575/kết quả/credit chưa xác minh. Giữ 1536 SU dự trù, trần campaign 16384 SU, pilot 04→05 chờ các gate hiện hành. Không xác thực mới hay qsub.
- Đã cập nhật CURRENT, POLICY, Q&A, review, budget/plan và HISTORY. Không thêm job/repeat/N56 hay lịch; kết thúc sau phần chuẩn bị, watcher tiếp tục thu ba job.

[Hướng dẫn N54](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0045UTC/).


## Báo cáo Qwen — 2026-10-16 00:59 UTC

- **H200 00:58:48 UTC:** 23906/23924/23934 vẫn PENDING(Resources), 3/5 slot; watcher còn sống. Chưa có số đo GPU mới.
- **Tiến triển CPU:** kiểm source EAGLE3 trong image, 12 kiểm tra cấu trúc đạt, 72 file được hash. Đã làm rõ nhánh target verification, yêu cầu tắt simulation acceptance và đặt cùng giới hạn 48 request cho control/candidate. Thiết kế tiếp theo đã cập nhật; CUDA/output/compatibility Instruct-2507 vẫn chưa kiểm chứng.
- **NSCC 00:55:29 UTC:** thiếu phiên VPN trước SSH; 220575/kết quả/credit chưa xác minh. Giữ 1536 SU dự trù, campaign 16384 SU; pilot 04→05→06 giữ thứ tự và gate. Không xác thực mới/qsub/tải draft.
- Đã cập nhật CURRENT, POLICY, Q&A, plan/budget và giữ bằng chứng. Không thêm job/repeat/N56/lịch; kết thúc sau phần chuẩn bị, watcher tiếp tục thu ba job.

[Review EAGLE3](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/SOURCE_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0055UTC/).


# Báo cáo Qwen — 2026-10-16 01:43 UTC

- **H200 01:43:17 UTC:** 23906 RUNNING từ01:38:03 trên g1/g4; 23924/23934 PENDING(Resources), 3/5 slot; watcher còn sống. Chưa có kết quả benchmark mới.
- **Tiến triển:** audit23906 đạt checksum payload/script; cả8rank MNNVL/NIXL. Hai worker prefill dùng chunk8192 **đồng thời graph prefill tăng4096→8192**, thêm8capture; decodegraph giữ nguyên. So cả hai baseline, chỉ khác chunk/graph và seed tự sinh. Không quy kết riêng cho chunk scheduling.
- Đã ghi checklist thu/đối soát final23906 trong review; log khởi tạo có hash, chưa phải finalseal. P/Dwarmup chưa xong tại audit01:41:56, không coi là lỗi. Watcher tiếp tục thu23906 và hai N54; không thêmjob/repeat/N56/lịch.
- **NSCC01:40:59 UTC:** thiếuVPN trướcSSH;220575/kết quả/credit vẫn chưa xác minh. Giữ1536SU dự trù, campaign16384SU, pilot04→05→06 và các gate. Không xác thực mới/qsub.
- Đã cập nhật CURRENT/POLICY/Q&A/review và budget/plan dưới lock; giữ bằng chứng. Kết thúc sau phần việc độc lập, không chờ queue.

[Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0140UTC/runtime-review.json).


# Báo cáo Qwen — 16/10/2026 01:47:27 UTC

- **H200:** 23906 RUNNING;23924/23934 PENDING(Resources),3/5slot;watcher sống. Chưa có kết quả benchmark hoàn chỉnh mới.
- **Audit mới:** hai P/D paths đã warmup;8rank MNNVL/NIXL và checksum payload/script đạt. Thay thế snapshot01:41 chưa warmup. Chunk8192 cũng tăng graph prefill lên8192; không quy riêng hiệu ứng cho scheduling.
- Đã chuẩn bị công cụ chỉ đọc đối soát final23906 với cả hai baseline/mean; replay seal/rawmetrics hai baseline đạt. Đây là dữ liệu cũ; terminal path còn chờ23906 hoàn chỉnh. Watcher tiếp tục thu; không thêmjob/repeat/N56/lịch.
- **NSCC01:45:30UTC:** thiếuVPN trướcSSH;220575/kết quả/credit chưa xác minh. Giữ1536SUreserve,campaign16384SU và gate04→05→06; không xác thực mới/qsub.
- Đã cập nhật CURRENT/POLICY/review và budget/plan dưới lock; kết thúc sau phần việc độc lập, không chờ queue.

[Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0145UTC/runtime-review.json) · [Công cụ final](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0145UTC/review-chunk8192.py).


# Báo cáo Qwen — 16/10/2026 01:52:34 UTC

- **23906 đã hoàn tất exit0 lúc01:48:16UTC.** Finalaudit đạt:2547,85goodtokens/s,SLA98,87%,TTFT735,56ms,ITL16,32ms;0lỗi/hủy request,short7/8chỉreverseđãbiết.
- **Chunk8192 thấp hơn meanhai baseline1,7238%**;TTFT+223,294ms dùITL−0,8249ms. Rehash47file/mỗi run,full60/120/30,raw789warmup/1589profiling,payload/runtime đềuđạt. Chunkcũngđổigraphprefill;chưa chọncấuhình/accuracyBTC.
- **H200 hiện tại:**23924/23934PENDING(Resources),2/5slot;watcher sống. Cả3wave9 đãfinalaudit;tiếp tục thu haiN54 và dùngreview-n54.py,không thêmjob/repeat/N56/lịch.
- **NSCC01:50:59UTC:**không cóVPN trướcSSH;220575/kết quả/credit chưa xác minh. Giữ1536SUreserve,campaign16384SU vàgate04→05→06;khôngauth/qsub.
- Đã cập nhật CURRENT,POLICY,Q&A,matchedreview,budget/plan dướilock;giữrawartifact và bằngchứng cũ. Kết thúc sauaudit,không chờqueue.

[Bằng chứng final](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0150UTC/chunk8192-final-review.json) · [Scheduler](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0150UTC/final-queue.json).


# Báo cáo Qwen — 16/10/2026 02:10:45 UTC

- **H200 02:09:40 UTC:**23924/23934 PENDING(Priority),2/5slot;watcher sống. Chưa có số đo GPU mới;wave9 đã finalaudit từ lượt trước.
- **Tiến triển CPU:** chuẩn bị công cụ đối chiếu token EAGLE3 và hướng dẫn capture native. 30ca tổng hợp +6kiểm source đạt;giữ input/output IDs,EOS/tail,finish reason. Source image trả output_ids cả nhánh text. Chưa thử HTTP/model/GPU hay xác nhận lossless/accuracy BTC.
- **NSCC 02:06:07 UTC:**thiếu VPN trướcSSH;220575/kết quả/credit chưa xác minh. Giữ1536SU dự trù,campaign16384SU vàgate04→05→06;không xác thực mới/qsub.
- Đã cập nhật CURRENT,POLICY,Q&A,design,budget/plan dưới lock và giữ bằng chứng. Tiếp:watcher thu haiN54 rồi chạy review-n54.py so cả hai baseline/mean. Không thêmjob/repeat/N56/controller/lịch;phần chuẩn bị độc lập đã xong,kết thúc không chờ queue.

[Hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/TOKEN_REVIEW.md) · [CPU/source](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0205UTC/token-review-validation.json) · [Scheduler](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0205UTC/final-queue.json).


# Báo cáo Qwen — 16/10/2026 02:19:28 UTC

- **H200 02:18:09 UTC:**23924/23934 PENDING(Resources),2/5slot;watcher sống. Chưa có số đo GPU mới.
- **Tiến triển CPU:**chuẩn bị bộ thu token nativeHTTP tuần tự,giữ raw request/response/hash và evidence lỗi.35ca HTTP giả lập đạt;chưa thử SGLang/Qwen/GPU,chưa có suite thực hay chứng minh accuracy.
- **NSCC 02:15:33 UTC:**thiếu VPN trướcSSH;220575/result/credit chưa xác minh. Giữ1536SU dự trù,campaign16384SU vàgate04→05→06;không xác thực mới/qsub.
- Đã cập nhật CURRENT,POLICY,Q&A,design,budget/plan và giữ raw evidence. Tiếp:watcher thu haiN54,chạy review-n54.py so cả hai baseline/mean. Không thêmjob/repeat/N56/controller/lịch;kết thúc vì chuẩn bị độc lập đã xong.

[Hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/TOKEN_REVIEW.md) · [CPU/mockHTTP](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0215UTC/attempt02/capture-validation.json) · [Scheduler](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0215UTC/final-queue.json).

# Báo cáo Qwen —16/10/2026 02:36UTC

- Kết quả mới xác nhận23904MNNVL+FlashInfer:2631,09goodt/s,SLA99,02%,ITL16,23ms,0lỗi/hủy; hơnMNNVLmean1,49%,chưa lặp.
-23905chunk2048:2331,35;23906chunk8192:2547,85; cảhai thấp hơnMNNVL,khônglặp.
- Đã gửi23973(comboN52repeat1),23974(freshMNNVLcontrolN52),23975(comboN52repeat2+longretrievalsauđo). Cùng23924/23934N54 hiệnđủ5/5slot,đềuPENDING(Resources). Watcher419440cònhoạtđộng.
- Wave10đãfreeze/checksum/CPUvalidate vàdryrunsharedcap2/4/5; không đổi cácjobqueued cũ hay mởN56. So mọirepeat vàcontrol,khônglấypeaklàmthắng.
- NSCCkhôngxácthựcmới/DUO;220575kếtquảvàcreditmớivẫnchưaxácminh. AccuracyBTCchưađạtchứngnhận.
- v111làtênjobđộikhác,khôngcóđiểmcủahọđểsoaiđanghơn. So tiếntriểncủamìnhbằngfullmeasurementvàrepeat.



# Báo cáo Qwen —16/10/2026 02:46 UTC

- **H200 02:45:04 UTC:**23924/23934/23973/23974/23975 đều PENDING(Resources),5/5slot;watcher419440 sống. Chưa có số đo GPU mới.
- Đã chuẩn bị **review-wave10.py**:so từng combo với3control/mean vàdriftcontrolmới;kiểm seal/raw/protocol/runtime;giữ longpass/fail/deferred/thiếu riêng. 14kiểm source/export/gate và8ca longCPU tổng hợp đạt,không phải thửQwen.
- Stored Slurm script23973–23975 khớp frozen;không sửa payloadqueued haygửi thêmjob. Gain23904 **1,4867%** vẫn là kết quả đơn trước wave10,chưa được lặp xác nhận.
- **NSCC02:41:22UTC:**thiếuVPN trướcSSH;220575/kết quả/credit chưa xác minh. Khôngauth/DUO/qsub;giữ1536SUreserve,campaign16384SU vàgate04→05→06.
- Đã cập nhật CURRENT,POLICY,DECISIONS,Q&A. Tiếp:watcher thu5job;đọc N54bằngreview-n54.py,wave10bằngreview-wave10.py. AccuracyBTC chưa xác minh;khôngN56 haytựpromote. Kết thúc sauchuẩn bị,không chờqueue.

[Hướng dẫn wave10](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/MATCHED_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0240UTC/final-queue.json).


# Báo cáo Qwen —16/10/2026 05:25 UTC

- **23924 MNNVL N54 hoàn tất exit0** lúc04:31:37UTC. Finalaudit đạt: **2634,03goodtokens/s,SLA98,90%,TTFT600,44ms,ITL17,11ms**,0lỗi/hủyrequest;short7/8chỉreverseđãbiết.
- So cảhaiN52control:gain+1,6153%/+1,5855%;so mean **+1,6004%**,TTFT+88,18ms. Seal47file,raw818warmup/1640profiling,full60/120/30,payload/runtime đạt. Một lượtN54;chưa chứng minh gain lặp hayaccuracyBTC.
- Đã mở1điểm xác nhận MNNVL N54 **24009** theo plan mới,giữ12file thực thi;storedSlurm khớp frozen. Dùng watcher419440 hiện có. Kế thừa budget-deferred replacement tối đa3attempt khi chưa đo đủ;giữ mọiattempt,không mở điểm xác nhận thứ3/N56.
- **05:24:11UTC:**23934/23973/23974/23975/24009 đều PENDING(Resources),5/5slot;watcher sống. ComboN52 gain1,4867% vẫn chờrepeat;comboN54 giữgate riêng. Đã chuẩn bị reviewer24009;chưa thử terminalpath job mới.
- **NSCC05:20:46UTC:**thiếuVPN trướcSSH;220575/result/credit chưa xác minh. Khôngauth/DUO/qsub;giữ1536SUreserve,campaign16384SU và04→05→06.
- Đã cập nhật CURRENT,POLICY,DECISIONS,Q&A vàmatchedguides;giữ bằng chứng. Tiếp:thu23934 vàwave10,so24009 với23924 và3N52control;kết thúc không chờqueue.

[Finalaudit23924](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0520UTC/n54-23924-review.json) · [Scheduler vàscript24009](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0520UTC/final-queue.json) · [Plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/PLAN.md).


## Lượt Qwen —16/10/2026 05:38 UTC

- **05:36:58 UTC:** 23934/23973/23974/23975/24009 đều **PENDING(Resources), 5/5 slot**. Watcher 419440 sống lúc 05:30:29. Chưa có số đo GPU mới; gain N54 1,6004% của 23924 vẫn chưa lặp xác nhận.
- Đã chuẩn bị **bộ đầu vào EAGLE3 14 ca** bằng tokenizer/template đúng revision. Retrieval có 3.788/7.885 token gồm template; input+cap tối đa 8.085/8.192.
- Preflight bộ thu, seal và dựng lại 5 file giống byte đều đạt. Chỉ chuẩn bị CPU; chưa có HTTP/output model/EOS thật, compatibility, acceptance hay accuracy. Giữ các attempt/probe lỗi và bản sửa API Transformers.
- **NSCC 05:30:29 UTC:** thiếu VPN trước SSH; 220575/result/credit chưa xác minh. Không auth/DUO/qsub; giữ dự trù **1.536 SU**, campaign 16.384 SU và 04→05→06. Không thêm job hoặc sửa payload đang queue.
- Đã cập nhật CURRENT, POLICY, Q&A, design và metadata kiểm truy cập trong budget. Tiếp: thu seal qua watcher, review 23934/wave10/24009 bằng các công cụ hiện có. Phần độc lập đã xong; kết thúc không chờ queue.

[Suite](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/token-suite-v1/suite.json) · [Hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/TOKEN_REVIEW.md) · [Kiểm CPU](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0530UTC/suite-validation.json) · [Scheduler](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0530UTC/final-queue.json).


# Báo cáo Qwen —16/10/2026 05:42 UTC

- **05:40:37 UTC:**23934/23973/23974/23975/24009 đều **PENDING(Priority),5/5slot**;watcher419440 sống. Chưa có số đo GPU mới; không thêmjob/sửa payload.
- **NSCC đổi tầng lỗi:** đã có snx-tun UP/route qua tunnel lúc05:40:56;ssh-batch tới SSH nhưng bị `Permission denied (password)`. Chưa truy cập PBS/credit, không kết luận password sai hay phiên24h đã đạt.
- Không loginVPN/DUO mới, không cấpcredential/thử lặpSSH/qsub.220575/result/credit vẫn chưa xác minh; giữ **1536SU** reserve,campaign **16384SU**,04→05→06.
- Đã chuẩn bị phiếu bước tiếp với lệnh reviewseal23934/wave10/24009 và các gate; đồng bộ CURRENT,POLICY,budget,continuous-plan,Q&A. Metadata EAGLE3 đã phản ánh suite14caCPU; chưa outputmodel/acceptance/accuracy.
- Reviewers vàinputsuite đã sẵn; không còn việc độc lập cần làm. Kết thúc không chờqueue; giữ giới hạnrepeat,gatecomboN54 vàkhôngN56/promotion.

[Bằng chứng scheduler](../../2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0540UTC/slurm-queue.json) · [Phiếu bước tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0540UTC/NEXT_STEP.md).

## Bàn giao hiện hành16/10/2026 05:43UTC — VPN/SSH đã khôi phục

Người dùng chủ động cho phép thửDUO/login lúc05:40. TunnelIPsec/TCPT lên
05:40:20UTC,IP10.103.62.11/24; SSH đãđăngnhậpthànhcông,a2ap-login01.
**KiểmtralạiBatchMode05:42:43UTC thànhcông**, khôngphải chỉcóIP/TCP.
Các ghi chúmissingVPN/Permissiondenied ởwake05:40 là snapshottrướcxácthựchoàn tất.
Giữ nguyênVPNtool79786, khôngCtrl-C/restart. Không cóchallengeDUOtext, chưa
có phản hồiđiệnthoại; chỉxácnhậnVPN/SSHđạt,không đoánfactor. HelperđềxuấtIKE24h,
chưakiểmđủ24h. Phiênnày vẫnkhởiđộngvớiike-persistfalse,**chưa lưuSAtrêndisk**;
khôngđược tuyênbốđãcache hayrestartđểthayconfig.
PBS220575đãterminalF/exit0,wall30m25s;khôngownPBSjobactive. Ledger13:40Singapore:
used2381,369SU,balance61618,631SU,InDoubt0; khoảnjobđãđốisoát.
Collect-run.py lần05:41 bịtimeout60s khi tarstream, **chưareviewfullbenchmark**.
Giữpartial/log, tăng timeoutstream hợp lý trướcthu lại,khôngnhânđôicopyđangchạy.
Resume research04→05→06chỉsauđủgatefullartifact/queue/credit;khôngauthmới.
[Bằngchứng](/home/apacsc42/workspace/vpn-rootless/inspection/login-success-20261016-0540UTC.json).


## Bàn giao hiện hành16/10/2026 05:53UTC — chuỗi3jobNSCC đã gửi

User yêu cầu“submit nhiều vào,tận dụng thời gian”. Đã reviewbaseline220575:
fullartifact đãthu, frozenpayloadđạt,protocol60/120/30 ởN32/34/36đạt;
N32=1570,21,SLA100%;N34=1625,59,SLA100%;N36=1356,35,SLA82,12%thấtbại,
0errors/cancel ởcảba; short7/8chỉreverseđãbiết. Đãdừngtăngở36đúnggate.
PBSstdout chuyển về khôngcótrongarchive,khôngquy kết runtimebackendngoàibằngchứng;
khôngcoismokelàaccuracyBTC. Collectlần600s05:45đãđủ, bảncompressed05:50cũngđủ,
partial60strướcđượcgiữ. Đãsửacollector gzip đểgiảmtraffic quaVPN.

**220720.pbs111(MNNVL04) RUNNING16H100**;**220721.pbs111(FlashInfer05) HELD**
`afterany220720`;**220722.pbs111(loaderprefetch06) HELD**`afterany220721`.
DependencyđãđọclạitừPBS,đảm bảo1job16GPUchạymỗilúc. HELDdo dependency làđúng,
khôngqrls/hủy/jobduplicate. Mỗi allocation45phút, fullgridN32/34/36/38/40/42,
dừngtăngkhipointtrướcSLA/errorfail.04/05/06độclậpso baseline220575;
04failkhôngtựkếtluận05/06vôgiátrị. Nếulỗihạtầngchungcầnphân tíchdừngchuỗicóreason.

Budgetledger13:40Singaporeused2381,369,balance61618,631trướcjobmới;
reserve3×1536=4608SU,cap16384còn9394,631SUchưaphânbổ. Max3PBSjobpending/running,
max1running16GPU,giữ13000SUprojectreserve. Đây là amendment thayquytắc1queued
đểtận dụngthờigian,theo yêucầumớicủauser;khôngnângcapcampaign.
H20023934/23973/23974/23975/24009đủ5slot,đềuPENDING(Resources)05:52UTC.

VPNtool79786vàSSHđanghoạtđộng,giữphiênkhôngrestart/auth/DUOthêm.
Tiếp: thu vàphân tích04kếtthúc,khôngsubmitduplicate05/06đãqueued;so cácđiểm
cùngN/cùngH100baseline,kiểm12longretrieval nếuđủthờigian. Tựchuẩn bịbướcnext
basedondata khiđượcslot;khôngđua sốversion/tạo hàngloạtconfigvôcăn cứ.
[Bằngchứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/chain-20261016-0551UTC/chain.json).



# Research Qwen — 16/10/2026 06:01 UTC

- PBS kiểm05:58:02UTC: **220720 R** (00:05:11,16H100 yêu cầu), **220721/220722 H**
  đúngafteranychain; chưa có benchmark mới. Logrole04 kiểm05:56 còn0byte,
  chưa chứng minh runtimeMNNVL. Khôngsubmit/đổiqueuedpayload/watcher/auth mới.
- H200 kiểm05:55:37UTC: **23934/23973/23974/23975/24009 PENDING(Resources)**,
  đủ5slot,sacct chưaallocation/start/end;watcher419440 sống.
- Chuẩn bị [review-candidate-sweep.py](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/review-candidate-sweep.py)
  và [hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/CANDIDATE_SWEEP_REVIEW.md):
  rehashseal/frozenpayload,so từngcandidate với220575 ởcùngN,táchlong vàruntime.
  11kiểm thành phần +5kiểm fixtureCPU đạt; fixture dùng exportbaseline, không
  phải kết quảcandidate. Hai lỗi setupfixture(EXDEV/quyền thưmục) đãgiữ vàsửa.
- Sửa collector đọc schedulerOutput_Path/Error_Path bêntrongbundle, ngoài glob
  cũ ởroot; chưa thu đượcstdout mới. Filebaseline cũng chưa thấy tại đường
  khai báo; không kết luận đây là nguyên nhân duy nhất thiếu log.
- myprojects hỏi05:55 vẫn trả ledger**13:40Singapore**:used2381,369SU,
  balance61618,631,InDoubt0;giữreserve4608SU,headroom9394,631SU.
  Đãsửa rule1queued/headroomcũ trongbudget,đồngbộPOLICY/CURRENT/DECISIONS.

Tiếp: thu vàreview04khi terminal,rồi05/06;so cùngH100/cùngN,đọc runtime và12long
riêng. Không thêmjob khiđủslot/đợiqueue tronglượt. GatecomboN54 vàkhôngN56/
repeatthứ3/promotion giữnguyên;accuracyBTC vẫn chưa xácminh.

[Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0555UTC/).
Kết thúc sau khoảng6phút vì phần chuẩn bị độc lập đã xong;job còn khởi động/chờ.


## Qwen — 16/10/2026 06:18 UTC

- PBS kiểm06:17:25:220720 R,wall24:39;220721/220722 H đúngafteranychain.
  H200 kiểm06:15:28:5/5PENDING(Priority),chưaallocation;watcher419440 sống.
- Thu serverinfo cả3worker220720 và2pairrouterHTTP200. Decode báoMNNVL/FA3,
  TP8EP8,graph1–64;rolelogs vẫn0byte,chưa đủbằngchứng khởi tạo8rank.
  N32đãbắtđầu,chưareviewterminal/gain/accuracy. Prefillload842,03/842,82s,
  decodeload89,74s làreportedstartup,chưa quy nguyênnhânI/O.
- Đã thêm collector runtime single-shot chỉđọc cho05/06khiR,chạy thật220720,
  6kiểm/capturesealđạt. Khôngnewwatcher,auth,job hay sửaqueuedpayload.
- Ledger14:00:02Singapore:used2381,369SU,balance60082,631,InDoubt1536đãtrừ.
  Giữ4608SUcampaignreserve,headroom9394,631,cap16384,reserveproject13000.
- Tiếp:capture runtime05/06khiR,thu terminal04→05→06 vàso220575 cùngN;
  H200thu seal qua watcher rồireviewN54/wave10/repeat. GiữgatecomboN54,
  khôngN56/thirdsuccessfulrepeat/promotion. Phầnđộc lập đãxong,kết thúc khôngchờ.

Evidence: `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0615UTC/`.
CURRENT/POLICY/DECISIONS,budget,plan vàtutorial đãđồngbộ; snapshotcũ làlịchsử.

## Cập nhật live16/10/2026 06:19UTC

220720MNNVLH100 vẫnRUNNING16GPU, đã có **fullN32** export60/120/30:
1692.17goodt/s,SLA100%,0errors/cancel,ITL17.25ms.
So220575cùngN32=1570.21: **+7.77%**. Đây làđiểmđo trongjobđangchạy,
chưa cófinalcandidate/longdiagnostic/accuracyBTC. N34đangđo tại06:19;
220721/220722vẫnHdependency. H2005/5PENDINGPriority. VPN/SSHhoạtđộng.
Evidence: nscc-pbs/inspection/live-220720-20261016-0619UTC/snapshot.json.


## User away —16Oct2026 06:21UTC: tiếp tục tự chủ

Người dùng cóviệcbận vàyêucầutựchạytiếp,khôngđợi nhắctừnglần. CronVPS đãkiểm
đangbật5phút,watcherH200vàVPN79786cònsống. Cơchếhiệnkhôngtựtrigger đúngchatgốc;
cácwake làphiênCLIriêngđọcfilehandoff,khôngđược hứađãsendmessage/notification.
Đượctiếptục research→phântích→chuẩnbị→submit trongphạmviQwenvàngânsáchhiệnhành,
khônghỏilạichỉvìkếtthúcmộtwave. Giữ16384SUtotal,13000SUreserve,max16GPUH100
running,3queued/runningPBSbằngdependencychain,H200cap5. Khôngsửapayloadđangqueue.
Tiếp04→05→06vàcollectfullartifacts/quality/runtime,so cùngN/H100baseline;
chọnpilot/repeat/loadkếtiếp theo dữliệu vàghi concreteplan. Mỗi jobmới phải
reserve,maxwalltime vàreviewedsource; khôngchờusernhắckhiđủgate/cònngânsách/slot.
Các dòng“không thêmjob/download tronglượt”ởsnapshotcũ khôngphảicấmvĩnhviễn
researchđãusergiao. Vẫngiữcácgatebenchmark/quality,khôngN56mùhaytựpromotion.
**KhôngloginVPN/DUOmới**,giữphiênhiệntại; nếuaccessmất,ghirõ vàlàmH200/CPUđộc lập.
KhônguploadBTC/nhắnngườikhác. CậpnhậtLATEST/HISTORY/CURRENTđểuserxemkhiquaylại.

LiveN32của22072006:19:1692.166goodt/s,SLA100%,ITL17.247ms,+7.77%vscontrol;
N34export1754.073,SLA100%,+7.90%vscontrol,N34protocolchưareviewđộclập.
JobvẫnR,đâylàkếtquảtạmtrongjob,chưafinalquality/accuracy;khôngbáopilotdone.


## 16/10/2026 10:29 UTC — Hoàn tất review DP N54, phục hồi evidence H100

Đọc README/CURRENT/POLICY và plan liên quan. Scheduler10:25:23934 COMPLETED
exit0(08:11:21UTC,9m17s);23973/23974/23975/24009 PENDING(Resources),4/5slot;
watcher419440 sống. Reviewer thật23934 đạt47sealedfiles,802warmup/1598profiling,
full60/120/30, payload12file và runtime so cảDPcontrol,8rankNIXL/2P/Dwarmup,
0errors/cancel; tái chấm132baseline+8candidate vẫn7/8, reverse đã biết.
2555,4232goodt/s,SLA98,7484%,TTFT751,9882ms,ITL16,8873ms. SoDP N52mean:
+0,4633%,TTFT+145,1971ms; soMNNVL cùngN54−2,9844%. Đóng nhánh DP có giới hạn
ởN54, không thêmrepeat/N56; ưu tiên bốn job xác nhận/combo/control/long.

NSCChelper không thấy liveVPN trướcSSH; khôngauth/DUO mới. Ba PBSjob/credit
UNKNOWN; giữ4608SUreserve,headroom bảo thủ9394,631SU, khôngqsub/release reserve.
Tìm thấy attempt06:26: tar exit1 do thư mục n38/confirm đang đổi. Archive gốc
353828103byte vẫn đọc đủ102member; phục hồi chọn lọc18file và kiểm raw/phases/
protocol/count/latency/length/goodrequest củaN32/34/36:1692,1662/1754,0728/
1787,7370goodt/s,SLA100%,0errors/cancel. Đây là bản chụp lịch sử đang chạy,
không terminalseal/finalquality/runtime; N38 loại khỏi phân tích. Giữ nguyên
archive/stderr. Không coi lỗi collection là mất toàn bộ dữ liệu hay GPUjobfail.

Đã cập nhật CURRENT/POLICY/DECISIONS/tutorial, NSCCbudget/continuousplan và các
hướng dẫnN54/planwave10/H100confirmation. Lưu bản policy/LATEST cũ trước ghi mới.
Không sửa frozenqueuedpayload, watcher, schedules, submission; không nestedagent,
newjob/download/auth/message. Không còn việc độc lập cần làm; kết thúc không chờ.
Evidence: nscc-pbs/inspection/wake-20261016-1025UTC/.


## 16/10/2026 10:59 UTC — pending và chuẩn bị logging H100

Đọc README/CURRENT/POLICY và plan liên quan. Kiểm10:55:37UTC cả bốn H20023973/
23974/23975/24009 PENDING(Priority),4/5slot,sacct chưa allocation;watcher419440
sống. HelperNSCC không tìm thấy liveVPN trướcSSH;ba jobPBS/credit vẫnUNKNOWN,
giữ4608SUreserve/headroom9394,631SU. Khôngauth/DUO,submit,download,externalmessage,
nestedagent,schedule/controller hoặc sửa frozenpayload.

ViệcCPU có ích: staging pbs-task-logging-01 riêng cho cặp H100 tương lai, mởlog
trongcompute task trước module/container thay vì chỉ trông vào redirection của
launcher. Chưa xác định nguyên nhân log cũrỗng. Uniqueprivate sidecar vàexec giữ
stdout/stderr/argv/status/signals;review bảnđầu phát hiện umask077 sẽ truyền vào
command nên khôi phục umask và thêm ca kiểm. Lầnđầu11/11, cuối12/12CPUstub đạt,
shellsyntax đạt;giữ cả evidence. Chưa upload/integrate/GPU/PBS thật, không suy
8rank/BF16KV/accuracy. Cùng hai file/hash phải áp dụng cho CẢ control/candidate
mới sau đủ gate;collector hiện thu toàn run nên không cần sửa,reviewer cần đọc
sidecar. Cậpnhật CURRENT/POLICY/DECISIONS/tutorial và budget/continuousplan,
NEXT_H100_CONFIRMATION; giữ cap/gate cũ và raw artifacts. Phần độc lập đã xong;
kết thúc không đợi queue. Evidence: `nscc-pbs/inspection/wake-20261016-1055UTC/`.

## Qwen — 16/10/2026 11:06 UTC

- **11:05:33 UTC:** 23973/23974/23975/24009 vẫn **PENDING(Resources)**,
  **4/5 slot**, chưa Start/End/allocation. Watcher419440 sống; chưa số đo GPU mới.
- NSCC helper không thấy liveVPN trướcSSH. **220720/220721/220722 và credit
  UNKNOWN**; không auth/DUO mới. Giữ **4608SU** reserve, headroom bảo thủ
  **9394,631SU**, cap16384SU; ledger06:17 và dữ liệu06:26 chỉ là lịch sử.
- Đã ghi [bước thu/review tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-1105UTC/NEXT_STEP.md): H200 review sau terminalseal;
  H100 refresh ownqueue/credit rồi thu ba terminal, review riêng từng trial.
  Logging12/12CPU đã chuẩn bị giữ nguyên; chưa upload/tích hợp/chọn candidate.
- Không job/reservation/payload/watcher/lịch mới. Giữ gate comboN54 và cặp H100
  có điều kiện; không N56/thirdsuccessfulrepeat/promotion. CURRENT/POLICY và
  metadata freshness budget/plan đã đồng bộ, không đổi số credit/reserve.
  Kết thúc sớm vì bước tiếp phụ thuộc dữ liệu/access mới; không đợi queue.

Evidence: `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-1105UTC/`.


# Qwen — 16/10/2026 12:07 UTC

- Scheduler **12:06:56 UTC**: **23973 RUNNING**, bắt đầu12:01:57, 16H200 trên g1/g4, wall4m59s; **23974/23975/24009 PENDING(Priority)**. Tổng4/5slot; watcher419440 sống tại12:05:35.
- Audit live23973 lúc12:06:28: toàn bộ14file submitted khớp registry/frozen; 12file thực thi giống23904, storedSlurm script khớp. Đủ8rank MNNVL/FlashInferdecode/NIXL-UCX; resolvedServerArgs chỉ khác random_seed. Ba server ready, nhưng snapshot chưa đủ2P/Dwarmup, connectionwarmup/export/terminalseal; **chưa có phép đo đầy đủ hoặc gain mới**. Giữ logprefix/hash. Prefill Triton fallback cũng có ở23904, không quy nguyên nhân slowdown.
- NSCC12:05:35: helper thiếu liveVPN trướcSSH;220720–220722/credit **UNKNOWN**. Không auth mới; giữ **4608SU**, headroom9394,631SU, cap16384SU/projectreserve13000SU. Không release/duplicate.
- Không gửi/sửa job, payload, watcher hay lịch. Tiếp: terminalseal23973→review-wave10.py; giữ mọi attempt và chờ23974/23975+long để xét gatecomboN54.24009→review-mnnvl-n54-repeat.py. Không N56/thirdsuccessfulrepeat/promotion. NSCC theo NEXT_STEP khi existingaccess trở lại.

Phần độc lập đã hoàn tất; kết thúc không chờ job. Evidence: `nscc-pbs/inspection/wake-20261016-1205UTC/`.


# Qwen — 16/10/2026 12:13 UTC

- **23973 COMPLETED exit0** lúc12:11:03UTC,wall9m06s. Finalreview47sealedfiles,
  payload/raw/full60/120/30/runtime đạt;0errors/cancel,short7/8chỉknownreverse.
  **2632,06goodtokens/s;SLA99,023%;TTFT632,66ms;ITL16,239ms**.
- Repeat1 hơn23904 **0,037%**, hơnmean2controlN52cũ **1,524%**. Wave10 vẫn
  **PARTIAL_RESULTS**: cầnfreshcontrol23974 vàrepeat2+long23975 trướcgainreproduced/
  gatecomboN54. Chưastatistics/accuracyBTC/promotion.
- Scheduler**12:12:41UTC**:23974/23975/24009PENDING(Priority),3/5slot. Watcher
  sống12:10:43 vàđãseal23973. Khônggửijobchỉđểlấpslot;khôngN56/repeatthứ3.
- NSCC12:10:43 thiếuliveVPN trướcSSH:3job/creditUNKNOWN,giữ**4608SU** vàheadroom
  9394,631SU. Khôngauth/DUO,release reserve hoặcduplicatejob.
- ĐãcậpnhậtCURRENT/POLICY/tutorial vàREPEAT1_RESULT;giữraw/cảtiềnkiểmtrướcseal.
  Tiếp:seal23974/23975→review-wave10.py;seal24009→review-mnnvl-n54-repeat.py;
  NSCCexistingaccess→thu3terminal/đốisoátcredit. Khôngsửa payload/watcher/lịch.

Việc độc lập đãxong; kếtthúc khôngđợiqueue.
Evidence: `nscc-pbs/inspection/wake-20261016-1210UTC/`.

## 16/10/2026 12:16 UTC — kiểm thực tế, chưa có trigger nghiên cứu mới

12:15:39UTC:23974/23975/24009PENDING(Priority),3/5slot,chưaallocation;
23973COMPLETEDexit0 giữ kết quả finalreview12:13. Watcher419440 sống,
registry mỗi entry một attempt, chỉ23973 cóseal;không chạy lại reviewer/test.
NSCChelper thiếu liveVPN trướcSSH;220720–220722/creditUNKNOWN,giữ4608SU,
headroom9394,631SU/cap16384SU/projectreserve13000SU. Khôngauth/DUO,release reserve,
duplicatejob hoặc allocation mới. Đãlưu queue/accounting/helper/registry/budget,
terminal-trigger-check và NEXT_STEP; cập nhậtCURRENT/POLICY/LATEST,giữraw cũ.
GatecomboN54 chưa mở;khôngN56/thirdsuccessfulrepeat/promotion. Việc độc lập đã
xong,kếtthúc ngay khôngchờqueue;khôngsửa payload/watcher/lịch.
Evidence:`nscc-pbs/inspection/wake-20261016-1215UTC/`.

## Bàn giao hiện hành16/10/2026 12:49UTC

Kiểm trực tiếp12:48UTC:H20023974/23975/24009PENDINGPriority,watcher419440sống.
23924MNNVLN54đãđo2634,03goodt/s,SLA98,90%,mộtlượt;repeat24009cònchờ.
23934DP N54đo2555,42,SLA98,75%.23973comboN52repeatđo2632,06,SLA99,02%,
sát23904=2631,09;vẫncầnfreshcontrol23974vàrepeat2+long23975theowave10gate.
Cácjobđãđotrênđềuexit0và0errors/canceltheoexport/report,khôngtựclaimaccuracyBTC.

NSCC:helperhiệnkhôngcònliveVPNtrướcSSH;đọcphiên79786trảUnknownprocessid,
khônglấyđượclogcuối,**chưabiếtnguyênnhânngắt**,khôngđổchoIKE/24giờ.
Khôngthửauth/DUOmới.220720–220722đãqueuedchain,chưalấykếtquảcuối/creditlive;
khôngtựsuystatustừwalltimehaygửitrùng. Giữ4608SUdựphòngđếnđốisoát.
Evidence:nscc-pbs/inspection/status-20261016-1248UTC/.



# Qwen — 16/10/2026 12:52 UTC

- Kiểm trực tiếp **12:50:42 UTC**: **23974/23975/24009 PENDING(Resources)**,
  3/5 slot, chưa Start/End/allocation; watcher419440 sống. Registry kiểm12:51
  vẫn một attempt mỗi entry; chưa có terminal seal mới. Kết quả23973 và các
  benchmark đã review giữ nguyên; không chạy lại reviewer/test bất biến.
- **Đính chính bản12:49:** artifact `status-20261016-1248UTC/h200-queue.txt`
  ghi Resources, không phải Priority như lời bàn giao. Bản đó là lịch sử;
  trạng thái Resources hiện đã được kiểm trực tiếp lại, không có số đo GPU mới.
- NSCC helper **12:50:42 UTC** thiếu liveVPN trướcSSH. **220720–220722 và credit
  UNKNOWN**; nguyên nhân VPN ngắt chưa biết. Không auth/DUO mới. Giữ **4608SU**,
  headroom bảo thủ9394,631SU, cap16384SU/projectreserve13000SU; ledger06:17
  là lịch sử. Không suy terminal từ walltime, gửi trùng hoặc release reserve.
- Bước tiếp đã sẵn: seal23974/23975→`review-wave10.py`; seal24009→
  `review-mnnvl-n54-repeat.py`; NSCC existingaccess→thu/review3terminal và đối
  soát queue/credit. GatecomboN54 vẫn đóng; không N56/thirdsuccessfulrepeat/
  promotion. Không thêm job, reservation, sửa payload, watcher hoặc lịch.

Không còn việc độc lập hữu ích trước dữ liệu/access mới; kết thúc không chờ queue.
Evidence: `nscc-pbs/inspection/wake-20261016-1250UTC/`.

## VPN forensic/fix16Oct — no new authentication

OldVPNstillhadtraffic06:26UTC. Userjournal shows SSHdisconnects06:28:59/06:29:27.
OriginalVPNwas aninteractive managedPTY with no detached terminal/durableexitlog.
Terminal/SSHlifecycle loss is plausible, **not proven**, no signal/finalVPNlog.
Do not claim24h/IKEexpiry. No newlogin/DUO attempted during investigation.
Prepared `workspace/vpn-rootless/vpn-persistent.sh` for NEXT USER-AUTHORIZED login:
tmuxownsPTY,privatepane/exitlogs,attach/detach,statusdoesnotlogin. Helpernow
ike-persisttrue andbindsprivate-cache to/var/cache INSIDE namespace only;
state0700/0600,notinnotes,keychainfalse. Prioroldsessionswere NOT recovered.
Local realPTY/mockinput andnamespacebindprobes passed, not realVPN/24htest.
Do NOT runconnect without userauthorization. Existing credentialwas successful
05:40UTC; current validity/DUOrequirements not freshlytested, don't discloseit.
Evidence workspace/vpn-rootless/inspection/vpn-drop-forensics-20261016.json.


## Bàn giao hiện hành16/10/2026 13:24UTC — VPN đã khôi phục bằngtmux

Usercho phép loginmộtlần. VPNIPsec/TCPT lên13:23:15UTC,IP10.103.62.12/24,
helperIKE86400s,ike-persisttrue. Tmuxsessionnscc-vpn đãdetachthật,
**tunnel vẫnUPsaukhiđóngattachclient**,SSHthànhcônga2ap-login02 lúc13:24:04UTC.
PrivateSQLiteđãcó1IKEsession,DB0600/cache0700;chỉkiểmcount/perms,khôngcopy
key/token/password vào notes. Đây làlầnđầutiênpersistenceđãverifythật,
khôngcònápdụngcâuchưa lưuSA ởsnapshotcũ. Chưakiểm24h/khôiphụcsauhardexpiry.

Giữ nguyên tmuxVPN,khôngkill/restart/helperconnect/auth/DUOmới. Nếuattach,
Ctrl-B rồiD đểdetach,khôngCtrl-C. ClientkhônghiệnchallengeDUOtext,khôngsuy
factorđượcduyệt. LogINFO/exit đượcgiữprivate; logpathởrun/current-log-path.
Rawqueue/accounting/summary/short/long/credit3jobNSCCđãthuở
nscc-pbs/inspection/access-restored-20261016-1324UTC/pbs-and-credit.json.
Cầnreviewterminalartifact/source/protocol trướcchọncandidate vàqsubtiếp;
khôngduplicate220720/21/22,chưacoichargecũlàliveđếnđốisoátbudget.
Evidence workspace/vpn-rootless/inspection/login-success-20261016-1323UTC.json.


## 16Oct13:30UTC — Codexquota audit/fix
Userreportedrapidusage. Last24h133starts/35complete/95quotaerrors;
43.49Minputincl40.64Mcached,442203output incompletedlogs,not billing/%conversion.
Fixedmissingrgbackoff,semanticjobtriggers,andgrowinghandoff68.8KB→7.8KB;
archivedfullhistory,unchangedmodel/GPU/VPN. See research-autopilot/USAGE_AUDIT.md
andusage-fix-validation.json.

# Qwen — 16/10/2026 13:37 UTC

- Bước đã hoàn tất: review terminal **220720 MNNVL04** từ seal
  `collected/220720.pbs111/20261016T132540573992Z`, không thu lại run đã đủ.
  Payload/seal hợp lệ; sáu N32–42 đủ60/120/30,0error/cancel;
  short không thêm lỗi so baseline, long12/12 PASSED.
- Goodput tok/s (SLA): N32 **1692,17 (100%)**, N34 **1754,07 (100%)**,
  N36 **1787,74 (100%)**, N38 **1860,03 (99,39%)**,
  N40 **1965,23 (99,10%)**, N42 **2041,97 (99,06%)**.
  So220575 cùngN: +7,77%/+7,90%/+31,80% tạiN32/34/36;
  controlN36 chỉ82,12%SLA. N38+ chưa có matchedcontrol.
  Một candidate so control cũ, chưa phải reproducedgain hay accuracy99%.
- Runtime vẫn chưa đủ: rolelogs0byte, archive không có PBSstdout/stderr;
  serverinfo cũ không chứng minh8rank thực thiMNNVL. Không promotion/newqsub.
- Kiểm13:35UTC: H200 **23974/23975/24009 PENDING(Resources)**, watcher419440
  sống; existingVPN/SSH hoạt động, PBS ownactivequeue rỗng.
  Credit đọc lại vẫn ledger13:20:07UTC: used5662,721SU, balance58337,279SU,
  InDoubt0. Budget đã reconcile13:27: không reserve treo,
  headroomcampaign10721,279SU; chưa phải quyền bỏ qua quality/runtimegate.
- Tiếp:220721 đã seal, chưa review;220722 collection bị ngắt, chưa seal.
  Không lặp seal220720 khi chưa có evidence mới. Không GPU mới/auth/lịch/agent.

Evidence: `nscc-pbs/inspection/wake-20261016-1335UTC/`.


## Codex autopilot đã tắt — 2026-10-16 13:42:29 UTC

Theo yêu cầu người dùng: dừng tự gọi Codex để giảm tiêu hao quota.
Đã gỡ cron `ap42-qwen-autopilot`, tạo `PAUSED`, xóa trigger `FORCE` nếu có.
Không tự bật lại, tạo lịch thay thế hoặc gọi Codex nền nếu chưa được yêu cầu rõ ràng.
Giữ nguyên VPN, job GPU đã gửi và watcher Slurm không gọi AI.
Các hướng dẫn tự chạy bên dưới chỉ là lịch sử; không phải quyền tiếp tục autopilot.


## Manual continuation — 2026-10-16T14:59:20.914804+00:00

User: submit more jobs; this authorizes the current manual GPU research, not re-enabling Codex autopilot.
Submitted PBS220908.pbs111 fresh control (Q) → afterany220909.pbs111 MNNVL repeat (H, dependency verified).
Each16H100/45min; max3072SU reserved before qsub under budget.lock. Used5662.721SU, projectbalance58337.279SU, InDoubt0; campaignheadroom7649.279SU after reserves.
Identical task-side logging integrated in both to resolve old empty logs. Runtime eight-rank/KV gate remains unresolved until actual new task logs; no promotion or99%accuracy claim.
Full60/120/30, N32/34/36/38/40/42 stop-on-failedSLA unchanged. Plan and remote checksums: nscc-pbs/inspection/manual-20261016-continue/.
220721 reviewed: FlashInfer N32/34=1542.05/1602.84 (−1.79/−1.40% baseline), N38SLA24.37%; long12/12.
220722 fully collected/reviewed: prefetch N32/34=1565.66/1622.77 (−0.29/−0.17%), N36SLA79.75%; long12/12. No new short regression in either.
23974 raw/seal review PASSED:2594.03goodt/s,SLA99.01%; combo23973 remains+1.47%vsfreshcontrol.23975/24009 still PENDING(Resources).
Initial new control copy inherited read-only files and failed PermissionError; fixed permissions only on new copies, originals unchanged; execution parity and syntax pass.
Codex cron remains absent/PAUSED present. Existing VPN and Slurm watcher untouched.

## Manual status — 2026-10-16T17:26:55.321610+00:00

23975 completed0:0 at16:54:24UTC; full offline seal/raw/runtime review passes.
ComboN52=2632.6099goodtok/s,SLA99.0226%,TTFT634.415ms,ITL16.2269ms;long12/12PASSED.
Three combo runs mean2631.920vscontrolmean2593.038,+1.4995%;freshcontroldrift+0.0573%. Descriptive replication, not statistical/accuracy proof.
N54 gate met; wrote bounded one-point plan and armed s10-combo-n54 in existing watcher,16H200/17min, same execution plus load52→54. No newAI automation.
24009 still PENDING(Priority).
NSCC existingSSH attempt returns Permission denied(password),exit255. VPN persistent status shows live pane andsnx-tun10.103.62.12. This is SSH authentication failure while tunnel exists, not evidence of VPN expiry; no new auth/DUO attempted.
220908/220909 current states UNKNOWN; previousQ/H only historical. Retain3072SU reservations, no blind retry/newqsub.
Evidence: qwen-experiments/nscc-pbs/inspection/manual-20261016-status/wave10.json.

## N54 terminal results — 2026-10-16 23:28 UTC

239/241 queue checked directly: own Slurm queue empty.24009 COMPLETED0:0 at20:38:14UTC;24131 COMPLETED0:0 at21:25:41UTC.
24009 MNNVL N54=2629.5067goodtok/s,SLA98.9004%;independent same-load reviewer MEASURED_SLA_PASS.
24131 comboN54=2654.1720goodtok/s,SLA98.9117%,TTFT736.693ms,ITL16.2688ms,0errors/cancel,long12/12PASSED.
Sealed raw/protocol/runtime/short review and exact execution/runtime comparison vs23975 passed.
Gain+0.8190%vs23975comboN52;N54singleobservation,not repeatability/organiseraccuracy proof. Current highest observed passing goodput.
Existing Slurm watcher PID419440 no longer running after all queued work ended; no restart/automatic newload.
PBS query existingSSH again Permission denied(password);220908/220909 remainUNKNOWN;noauth/DUO,retainreserves.
Evidence:qwen-experiments/nscc-pbs/inspection/manual-20261016-final-n54/. No new job submitted in this status turn;Codexautopilot staysOFF.

## Auth and submissions — 2026-10-17 00:57 UTC

User explicitly requested reauthentication and more GPU submissions. SSH password login succeeded through existing VPN on a2ap-login01; no VPN restart or DUO. Earlier Permissiondenied was batchSSH auth failure; exact cause of old session loss remains unproven. No secrets saved.
220908/220909 both terminalF/exit0,walltimes32:10/42:18;collected/sealed/rawprotocol/short/long reviewed. Freshcontrol N32/34=1563.237/1624.351;MNNVLrepeat1680.796/1758.237,+7.5202/+8.2424%. MNNVLN42=2041.093,SLA99.055%,nearoriginal2041.966. ControlN36SLA30.784% retained.
New tasklogs establish expectedTP/EP/NIXL,BF16KV allocation and MNNVL ranks0..7/world8;both12longPASSED. No claim99%organiseraccuracy.
Submitted H20024174comboN52freshcontrol,24175comboN54repeat;bothPD(Resources) confirmed. Existing deterministicwatcher restartedPID3860355 only for authorisedGPUwork; noAIautopilot.
Submitted H100220998 MNNVLcapacityN42/44/46/48 (R)→afterany220999 MNNVL+FlashInfer interaction sameN (H). Stop-onfailedSLA;16H100/45min each,max1running;dependencyverified.
Budgetpriorused8204.517SU,balance55795.483SU,InDoubt0;new3072SU reserved underlock;campaignheadroom5107.483SU. Previouspair3072SUreservations fullyreconciled fromactualcharges.
Plans/validation/collection/review/submissionevidence:nscc-pbs/inspection/manual-20261017/ andserving-tuning-10/PLAN.md. Codexcron remainsabsent;PAUSED stays.

## Status 2026-10-17 01:42 UTC

H20024175 completed0:0, sealedraw/protocol/runtime/shortreviewpass,2658.1953goodtok/s,SLA98.9130%,TTFT734.655ms,ITL16.2491ms,0errors/cancel,long12/12PASSED. VersusfreshcomboN52/24174+0.9583%;vsfirstN54/24131+0.1516%. N54twoobservationsmean2656.1836. OwnSlurmqueueempty.
H100220998terminalF/exit0 walltime35:15;remotesummaryN42=2039.062SLA99.21%,N44=2105.100SLA98.93%,N46=2166.463SLA98.89%,N48=1759.132SLA80.49%(FAIL);0errors/cancel. ThesePBSvalues are terminalsummary only pendinglocalfullsealreview. Collectionstarted in toolsession66882,stdout/stderr inspection/manual-20261017/collect-220998.*;preservepartialifinterrupted.
220999RUNNING8m37s,SSHworks. No newsubmission this status turn,autopilotoff.

## Status 2026-10-17 01:58 UTC

220999RUNNING24m22s;liveN42summary2038.120goodtok/s,SLA99.1318%,0errors/cancel;onlyliveexport,notterminal/qualityresult. SameN2209982039.062,delta−0.0462%,noevidentgainatN42. Higherloadsawait. SSHworking.
220998collectioncomplete;terminalseal/fullprotocol/short/payloadreviewpass,longPASSED;N46=2166.463,SLA98.8897%,N48SLA80.4896%FAIL. Runtimeadditionalrankreviewstillmanual.
ReviewerCLIrestrictedtooldpilots,rejectednewIDwithoutmutation;calledexistingcomparefunctionwhichchecksnewfrozenplanID/hashes. No sourcepatch or rerunaudit.
H200queueempty;watchercompleted01:24:18UTC. Best2658.195goodtok/s remains. No newsubmission/autopilot.

## Terminal combo H100 — 2026-10-17 02:19 UTC

DirectPBS220999F/exit0,walltime34:53;ownPBS/Slurmqueuesempty. Remote terminalsummary comboN42/44/46/48goodtok/s2038.120/2088.851/2166.992/2204.528;SLA99.1318/98.9247/98.8897/98.7663%;0errors/cancel. Longremotelog12/12PASSED. Theseareterminalsummary/log,notyetlocalfullseal/runtime/shortreview. Collectorstarted220999,artifactsandstdout/stderr inmanual-20261017;preservepartial.
N48combo passeswhereMNNVLalone220998SLA80.49%failed;candidatehypothesis,pendingrepeatandfullreview. N46nearidentical2166.99vs2166.46,no meaningfulsame-loadgainthere. BestH100observedpassing2204.528,newconfigsingleobservation;notorganiseraccuracyproof.
Ledger10:00SGTused9407.717SU,balance53056.283,InDoubt1536stillpresentdespitejobterminal;doNOTrelease220999maxreserveuntilreconciled. No newjobsubmitted/statusonly;autopilotoff.

## Keep useful GPU work queued — 2026-10-17 02:24 UTC

User explicitly reiterates: do not wait for reminders; when results, budget and resources permit, analyse then submit next useful jobs. CodexautopilotOFF only forbids automatic AIinvocations/cron, not ongoing authorisedGPUresearch. Prior decisions saying a turn ended do not revoke continuation.
Submitted andverifiedH20024189freshcomboN54control+24190comboN56probe,bothPD(Resources);boundedN56amendmentaftertwopassingN54runs,notblindloadincrease. Watcher4024591,nonAI. NoN58/promotion.
SubmittedandverifiedH100221020MNNVLN46/48R→afterany221021comboN46/48H,16GPU45mineach;stopfirstfailedload. Independent matchedfrontierreplication ofN48fail/pass,notnewrandomconfig.
220999sealedraw/fullprotocol/short/payloadpass,long12/12;actualtasklogsconfirmMNNVLranks0..7,FlashInferattentionranks0..7,BF16KV. N48=2204.528SLA98.7663%;priorMNNVLN48failed80.4896%.
Freshledger10:20SGTused10598.401,balance53401.599,InDoubt0;old09/10actualcharges2393.884SU reconciled;new3072SUmaxreservedbeforeqsubunderlock. Campaignheadroom2713.599SUaftermaxreserve,projectretain13000safe.
Evidence/plan/validation/submission:nscc-pbs/inspection/manual-20261017-next/. No Codexcron/backgroundmodelenabled.

## Continue — 2026-10-17 06:52 UTC

User asks continue. SSHbatchauthfailed;authorisedpasswordreauthsucceededthroughunchangedVPN,noDUO/noVPNrestart.
H20024189N54=2658.547,SLA98.9137%;24190N56=2671.109,SLA98.8002%,TTFT847.849ms,ITL16.2875ms. Bothsealedfullprotocol/runtime/short/long12pass;singleN56peaknotreplication.
H100221020/221021terminalexit0;collectedfullseals,payload,protocol,short,long12/12,runtimeTP/EP/NIXL/BF16/MNNVL8rankandcomboFlashInfer8rankreviewpass. ControlN46=2182.281,N48=1399.174SLA64.2113%FAIL;comboN46=2143.069,N48=2190.538SLA98.7591%. ComboN48passesrepeated;N46doesnotimprove,notuniversalspeedup.
SubmittedH20024235N56repeat+24236N58probe,afterboundedplanamendmentfromnewpassingN56. Sameexecution16H20017min,cap5,noN60. Watcher245859nonAI.
SubmittedH100221051MNNVLN47midpoint→afterany221052combo48/50/52,16H10045mineach,stoploadincreaseonfail;dependencyverified. NootherPBSjobqueued.
Freshledger14:40SGTused12487.681SU,balance51512.319SU,InDoubt0. Old1889.280SUchargesreconciled. New3072SUmaxreserveleaves824.319SUcampaignheadroom. Noanother45minH100allocationbeforebudgetreconcile,notpermissiontospendbeyond16384SU.
Evidence:nscc-pbs/inspection/manual-20261017-0650/PLAN.md,validation.json,reviews/submissionreceipts. Cron/CodexautopilotremainsOFF.

## Continue — 2026-10-17 07:30 UTC

Slurm24235N56repeatRUNNING,24236N58probePENDING(Resources). PBS221051terminalF/exit0,25:45;collectedandsealedprotocol/short/payloadreviewpass,long12/12. N47=2101.237,SLA96.7164%,0errors/cancel;weakerthanN46controls,closemidpointbranch.221052combo48/50/52RUNNING,noexportyet. SSHworks.
Usefulindependentcombofrontierreplicationqueued221058.pbs111 afterany221052verified. Samebackend/model/precision/fullprotocol,grid48/50/52,stopfirstfailedSLA.16H10040minmax1365.334SU;internaldeadline45→40minmatchedandhashesverified. Slowerstartupmaydeferchecks;mustlabelincompleteifso.
Freshcreditused12487.681,unpostedconfirmed221051chargeconservative878.934,active221052max1536,newmax1365.334;sum16267.949SU<16384,headroom116.051SU. Terminalpendingchargeandreservationretaineduntilledgerreconciles;InDoubt1536alreadydeductedbalance,notdoublecounted. NoadditionalH100jobfitswithoutactualcostreconcile.
Initialsubmissionhelperhadupdated_utc=nowfunctionJSONerrorbeforeanybudgetwrite/qsub;fixednow(),rerunonlyafterconfirmedpresubmitfailure.221058receiptrecordedimmediatelyanddependencyverified.
Evidence:nscc-pbs/inspection/manual-20261017-0728/PLAN.md,repeat-validation.json,repeat-pre/post-submit,review-midpoint.json. CodexautopilotOFF,noVPNchange.

## Continue — 2026-10-17 09:01 UTC

H20024235N56repeat2669.803/SLA98.801%;24236N58=2667.966/SLA98.6826%,TTFT991.136ms. Bothsealedprotocol/runtime/shortpass,long12/12. N56two-runmean2670.456;N58plateau,noN60.
SubmittedH20024263sameN56fullbenchmarkthenpostmeasurementprofile52diagnosticrequests/all16ranks;one17minallocation,notprofilinginscore. Watcher545414;PD(Resources→Priority). Neednewprofilebecauselast23607predatesMNNVL/FlashInfer.
SSHfirsthungonexistingmaster;separateTCPSSHrespondedauth,VPNpane/tunnelstilllive. Reauthsucceededusingnewshortcontrolsocketq-%C;firstlongernamefailedUnixsocketpathlength,noVPNrestart/DUO. Helpernowusesauthenticatedq-%C+ServerAlive10s/2,syntaxpassed;oldhungclient541433terminatedonly,VPNuntouched.
PBS221052/221058Fexit0,32:22/31:13. TerminalsummaryN50=2218.032/2229.827,N52=2215.247/2215.673,N48=2191.114/2197.808;allSLA97.8–98.8%,0errors/cancel. Fullcollectionsandreviewinprogress,summariesnotyetfullreviewclaim.
AllPBSchargesreconciled3049.244SUincludingmidpoint;freshledger16:40SGTused15536.925SU,balance48463.075SU,InDoubt0,noactivereserves. Campaignremaining847.075SU(not116,actualcostrelease). Insufficientforobserved~25+minute16GPUstartup+fullbenchmark;nonewPBSjob,continueH200separateallocation.
Qualityruleclarification:99%ofBTCownunchangedFP8referenceonfullsuite;notnecessarilyMMLUPro/GPQAonly. Existing8smoke/12retrievalcannotprove99%. Priorresearchpercentagesweresubjectiveestimates,notmeasuredcompletion.
Evidence:nscc-pbs/inspection/manual-20261017-0858/;qualitynext.md. CodexautopilotOFF.

2026-10-17 09:02 UTC: H100221052/221058fullreviewfinished: seals,payload,protocol,runtimeTP/EP/NIXL/BF16/MNNVL+FlashInfer8ranks,shortnonregression,long12/12 allpass. MeanN48/50/52=2194.461/2223.930/2215.460;N50winsbothruns. RESULTS.mdstoredinmanual-20261017-0858. No furtherPBSqsub;H20024263pendingPriority.

## Cross-platform evidence and forecast — 2026-10-17 09:17 UTC

User explicitly requests objective report withreferences/configmatching,notmisleadingcrossserverbestplots. Reportatworkspace/reports/cross-platform-20261017/REPORT.md;matched-comparison.png/svg;matched-anchor-audit.json,data.json,references.json,build.py. Oldcomparison.pngisexploratoryhistorical,notproof.
AuditresolvedperformancefieldsforH20023904/23973/23975/24174andH100221052/221058atN52: sameTP/EP/precision/backend/graph/memory/context/chunk/transportandnormalisedbenchmarkconfig;recordedruntimefielddiffengineseeds. Hostdriver/runtime/CPU/NIC/nodes/clock/timeconfounded,notGPU-onlycausality. Sameimagehashstagingrecordsreferenced,notrehash26GB.
MatchedcomboN52H200mean2632.1809,H100mean2215.4600→k1.188096805. H100winningN50mean2223.9295→conditionalH200N50prediction2642.2435. OnlyONEconcurrencyanchor;inputminmaxsensitivity2633.887–2650.293isNOTCI/predictioninterval/guarantee;noallconfigtransfer.
H100bestpeak2229.827job221058,N50,SLA98.5684%;mean2223.930. Nopeakcherrypickingformeans.
SubmittedH20024272samecomboN50,heldoutfromN52calibration;PENDING(Resources)verified. Prediction/operational2%toleranceandinputhashesfrozenBEFOREresultinpre-registered-prediction.json. Mustreportfailure/errorwithoutretuning;onepassvalidatesonlylocalpointnotuniversalfactor. Existingprofile24263preserved,noH100qsub/budgetchange,AIautopilotOFF.
PrimaryrefsNVIDIAperformanceoverview+H200specs,NISTpredictionuncertainty+handbook. Refssupportmethodprinciples,notquantitative1.188factor;localrawdataisthequantitativeevidence. Needmulticoncurrency+repeatedpairedtrialsformoregeneralisablemodel.
Initialplotenvlackedpip/matplotlib;isolated/tmpvenvinstalledmatplotlib,notmodelruntimechanged.

## Continue pending-path preparation — 2026-10-17 09:50 UTC

LiveSlurm24263(profileN56)/24272(holdoutN50)bothPENDING(Priority);nonewmeasurement. SSHexistingauthworks,ownPBSqueueempty. Freshmyprojects17:40SGTused15536.925,balance48463.075,InDoubt0,847.075SUcampaignremaining;nonewPBSqsub.
Implementedofflinevalidate-holdout.py next to cross-platform REPORT.md. Usesfrozenpre-resultprediction2642.2435and2%operationalthreshold;firstrequiressealedfullprotocol/payload/runtime/SLA/short/long,includingMNNVL+FlashInfer8ranks. Writesexplicit WAITING/INCOMPLETE/LOCAL_SUPPORTED/LOCAL_NOT_SUPPORTED states, signed+absoluteerrors;noauto-fit/retuning/universalclaim. Cachesoneimmutableterminalsealreview;nonewscheduler/AIautomation. Executedrealpendingpath→WAITING_FOR_TERMINAL_SEAL;terminalpathnotyetexercisedonreal24272,notclaimedvalidated.
ThisturnpreparesreviewwithoutburningGPUoropeningunsupportedvariants. Nextnewinformationmustcome24272resultor24263all16ranktraces;keepqueuepositions. Noautomaticchatnotificationpromise. CodexautopilotOFF.

## Additional evidence-based H200 pilots — 2026-10-17 09:58 UTC

User challenges waitingforprofileasnotonlyusefulwork. Re-examinedexistingoutputs:comboN52→N56→N58ITL~16.23→16.27→16.27ms,TTFT~634→850→991ms,goodputplateau. Wholeprefilllogs multi-sequencestepfractionsforprefill0/1:23975=36.09/11.07%,24235=98.23/87.41%,24236=98.15/97.35%. Thesearemixedstartup/warmup/measure/long,notisolatedphaseorcausalproof.
Submittedandverified24281single-requestprefillbatches(--prefill-max-requests1),same2xTP4;24282oneTP8EP1prefillreplaces2xTP4EP1,decodeTP8EP8fixed. BothN56/16H20017min/fullprotocol+short+12long,0newH100credit. Queue4/5:24263/24272/24281/24282allPD(Resources). Preserveallpositions.
Hypotheses:batchfragment/latencytradeoffandphase-specificparallelismafterfasterdecode;counterhypotheseslostMoEbatching/replicathroughputandTPcommunication. Oldsingleprefill23324wasbatchlimitnotTP8,andonly0.34%gainunderOLDcacheawarerouting;currentcombinationwithRR+MNNVL+FlashInferhasnotbeentested. Do notrepeatknownlosingchunk2048/8192orassertbottleneckfromTTFTalone.
Freshcontrol24263officialN56windowbeforeprofiler,plus24190/24235controls. Runtime/qualitygatesbeforeclaim,anywinnerneedsindependentrepeat. SingleTP8reviewmustexpectoneprefilllog/onewarmuppair,notoldhardcoded2workerchecker. EqualTPNIXLpathunchanged;GPUcompatibilitynotyetvalidated.
Exactstagedimage server_args.pydeclaresprefill_max_requestsOptional[int],defaultNone;sourceextractedwithlegacyunsquashfs-p2afterunsupported-cat/wrongrouterpathattempts(noGPUspent). Shellsyntax/payloadinvariants/16GPUplacementvalidated,noruntimeclaim.
Primaryrefs:https://arxiv.org/abs/2401.09670v3 andhttps://docs.sglang.io/docs/advanced_features/hyperparameter_tuning supporthypotheses/principles,notspeedupguarantee. Plan/evidence:serving-tuning-10/next-evidence/PLAN.md,prefill-observations.json,pilot-validation.json,staged-source/. AIautopilotOFF.

## Benchmark/profile review and next trial — 2026-10-17 10:58 UTC

Job 24263 completed with exit 0. The sealed full benchmark, payload, runtime and short-output review passed: 2,667.465 good tokens/s, SLA 98.7995%, TTFT 856.622 ms, ITL 16.257 ms, zero errors/cancellations, and 12/12 long checks. This is another N56 control, not a new gain.

The separate diagnostic used 48 concurrent requests, not the 52 stated in older plans. All 16 expected rank traces contain kernels (4+4+8); all 415 diagnostic requests succeeded. Per-rank mean MoE shares of summed kernel time were 42.84%/42.77% for prefill and 27.99% for decode. These are not wall-time fractions or predicted speedups. Prefill/decode trace windows cover 4/32 steps and must not be compared as absolute phase times.

The start API returned HTTP 200 but the client failed to parse its response as JSON. Explicit stop calls returned HTTP 500 because profiling was no longer in progress. Keep these warnings. The traces are usable; no extra allocation is warranted solely to remove control warnings. The initial reviewer assumed EP appeared in every trace filename and failed before mutation; it was corrected to handle prefill filenames without EP.

The new evidence motivated one prefill-only DeepGEMM trial: job 24291 was submitted and verified PENDING(Resources). It changes only the prefill MoE backend at N56, keeping both TP4/EP1 workers and unchanged TP8/EP8 decode with MNNVL+FlashInfer. The old losing DeepGEMM trial changed decode; it does not establish the effect on larger prefill batches. The exact image source supports the backend and a standard-layout path, but GPU startup and quality remain unverified.

Queue snapshot: 24272 (N50 holdout), 24281 (prefill batch limit), 24282 (single TP8 prefill), and 24291 (prefill DeepGEMM) are all pending. No H100 job or additional H100 credit used. Codex autopilot remains disabled.

Readable evidence and plan: serving-tuning-10/profile-review-24263/RESULTS.md. Detailed profile audit: profile-review.json. Pre-submission payload/syntax checks: pilot-validation.json. Benchmark audit: nscc-pbs/inspection/manual-20261017-1054/benchmark-review.json.

## Held-out measurement reviewed — 2026-10-17 11:58 UTC

Job 24272 completed with exit 0 at11:45:28UTC. The frozen-forecast validator ran on its real terminal seal and passed raw/protocol/payload/runtime/SLA/short/long checks. Measured H200N50:2,601.6289goodtokens/s, SLA99.1326%, TTFT505.178ms, ITL16.3670ms, zero errors/cancel, long12/12.

The original prediction was2,642.2435, so signed error is−1.5371%. It passes the predeclared2% operational check for this single held-out point. It falls OUTSIDE the prior input-only sensitivity range2633.887–2650.293, illustrating missing model error. Keep both facts; do not claim general conversion accuracy or a95% prediction interval. Actual N50 system ratio1.169834 differs from N52 calibration1.188097. Frozen input hashes were checked unchanged after updating the plots; the holdout was not fitted into calibration.

Updated cross-platform REPORT.md and matched-comparison.png/svg with forecast versus measured holdout. The report is now fully English; its previous Vietnamese version is retained as historical text. No contest submission or slide changed.

At11:58UTC,24281 was RUNNING~6minutes with workers ready;24282/24291 remainedPENDING(Resources). No new trial submitted because two existing hypotheses still await results. H100 budget remains847.075SU; no new H100 allocation.

## Single-request prefill result — 2026-10-17 12:27 UTC

Job24281 completed and passed sealed raw/protocol/payload/runtime/short/long review. Intended prefill_max_requests=1 was confirmed; decode settings and both backend rank censuses remained unchanged. Result2621.292goodtokens/s,SLA98.7805%,zero errors/cancel,long12/12. Versus fresh control24263:goodput−1.731%,TTFT+79.989ms,ITL−0.0668ms. Versus all three N56 controls mean2669.459:goodput-1.80%.

Close the batch-limit branch; no repeat of this measured loser. This is a valid negative result, not a failed job or universal causal statement. The whole-log multi-sequence counts confirm the intended effect but mix non-benchmark traffic, so they are descriptive only.

24282(singleTP8prefill) and24291(prefill-onlyDeepGEMM) remainPENDING(Resources), confirmed directly. Preserve queue positions. No new variant is justified merely to fill slots before these independent results; H100 remains within the existing budget constraint.

Readable result:serving-tuning-10/prefill-pilot-reviews/24281_RESULT.md. Full review script supports predeclared two-worker changes; its real24281 terminal path passed. The24291 terminal path remains unexercised until actual data arrives. Codex autopilot remains off.

## Pending pilots: layout-aware review prepared — 2026-10-17 13:54 UTC

Direct scheduler queries confirm24282 and24291 remainPENDING(Resources), with no start times or new measurements. No GPU trial was added merely to fill a slot.

Prepared review-tp8.py for the frozen24282 layout: one TP8/EP1 prefill worker, one TP8/EP8 decode worker, and one warmup path. The shared point reviewer now accepts an explicit prefill-role tuple, checks that it matches the hashed/sealed placement, and preserves all raw/protocol/payload/output checks. Existing callers retain the original two-worker default.

Meaningful CPU checks used real sealed24263 evidence: default two-worker metrics and sealed-file count exactly match the prior saved review, and falsely requesting a one-worker layout is rejected. The real single-worker24282 terminal path is NOT validated yet because the job has not run. Running its pending path returns WAITING_FOR_TERMINAL_SEAL. This changes review tooling only, not GPU scripts, configurations, forecast inputs or queues.

Evidence:serving-tuning-10/prefill-pilot-reviews/layout-reviewer-validation.json. After24282 seals, run review-tp8.py; inspect any unexpected derived runtime changes manually rather than broadening allowlists blindly. For24291 use review-two-worker.py with a fresh output path.

Codex autopilot remains off. H100 campaign budget is unchanged;847.075SU does not fund another known startup plus full benchmark.

## H100 access check — 2026-10-17 13:57 UTC

The user asked about the other cluster. A fresh PBS/credit query could not run: the helper found no live VPN session. The persistent tmux pane is dead with exit0. A filtered lifecycle log shows `2026-10-17T13:23:05.957922Z ... IKE SA expired, disconnecting tunnel`, approximately24hours after the16October13:23 login. This replaces earlier snapshots showing a live tunnel; do not blame the current failure on SSH alone.

Current PBS queue and credit are UNKNOWN, not verified empty. The last reconciled budget remains15,536.925SUused out of the16,384SUcampaign cap,847.075SUremaining; last projectbalance48,463.075SU. Distinguish the campaign limit from total projectcredit. The remaining campaign allowance does not cover observed16GPUstartup+fullbenchmark. No new authentication, DUO or qsub was attempted during this status check; no claim that a new login would restore the budget.

## VPN and SSH restored — 2026-10-17 14:09 UTC

The user explicitly requested another login. Confirmed the old VPN tmux pane was exited before removing only that dead terminal. Old private cache and raw private logs were preserved. Restarted the existing persistent launcher, submitted the previously provided credentials interactively, and established a new tunnel at10.103.62.13. No authentication/session contents were saved in notes. The terminal did not require additional MFA input from the assistant; do not infer what happened on a phone.

SSH password authentication then succeeded on a2ap-login02. A fresh PBS query showed no own active jobs. myprojects ledger22:00:02SGT:used15,536.925SU,balance48,463.075SU,InDoubt0. This is the project balance, not the internal campaign remainder847.075SU. The numeric16,384SUcampaign allowance was a planning limit, not BTC exhaustion or an amount explicitly specified by the user.

Detached the tmux client with its detach sequence. The VPN remains owned by persistent tmux, independent of the tool PTY. A subsequent status and batchSSH check succeeded after detachment. No new GPU job, budget amendment or Codex automation was requested or performed in this login turn.

## 2026-10-17 14:18 UTC — submissions on both clusters

The user requested continued submissions on both servers and clarified that the Slurm server is not credit limited. Three H100 jobs (221151, 221152, 221153) were submitted and verified in an afterany chain; three H200 jobs (24320, 24321, 24322) were submitted by the existing watcher. They test fresh controls, phase-specific compute/layout changes and prefill weight prefetch. Full plan and receipts: qwen-experiments/nscc-pbs/inspection/manual-20261017-1410/PLAN.md.

Corrected the budget interpretation: project balance is 48,463.075 SU, not 847.075 SU. The latter was the old internal campaign remainder. The user authorised continuation after this clarification. The revised 51,000 SU planning bound retains a 13,000 SU buffer; neither amount is an organiser quota. The batch reserves at most 4,608 SU.

H200 job 24282 failed before measuring because TP8/EP1 produces a 192-element MoE weight partition incompatible with FP8 block 128. TP8/EP2 gives 384; corrected job 24321 tests that layout. H200 job 24291 passed protocol/runtime/SLA/short/12-long review at 2,715.842 good tokens/s, +1.8136% versus 24263. An independent repeat is armed. Its first reviewer rejection was an overly narrow runtime delta allowlist; the revised review explicitly checks both main and speculative runner values and that speculative decoding remains disabled. Preserve both review files.

Autopilot remains disabled. GPU submissions do not authorise background Codex scheduling. No submission slides or BTC upload changed.

## 2026-10-17 14:50 UTC — complete research slide update

The user explicitly authorised updating the presentation with research from the beginning through the latest results. Replaced Presentation/TripleU_APAC2026_Presentation.pptx with a 32-slide English Metropolis deck: 24 main slides and eight appendices. It covers the initial topology search, NIXL descriptor patch, FP8/EP compatibility, research protocol, H200 serving and kernel progression, H100 independent tuning, matched cross-platform calibration and frozen holdout, failed branches, metric records, run configurations, accuracy limits and submitted next tests. All slides have distinct sourced backgrounds and native gradient tint; speaker notes are included. No folder-tour or empty-HPC disclaimer appears on presentation slides.

H200 headline is the locally reviewed 24291 candidate at 2,715.842 good tokens/s (+1.8136% versus 24263), explicitly awaiting replication and official accuracy. Raw request scatter rechecked 1,674 of 1,694 passing both limits. H100 peak remains 2,229.827, with independent N50 mean 2,223.930. Calibration is kept separate from unrelated platform peaks; held-out prediction error −1.5371% and the inadequate old sensitivity range are retained.

Review materials: workspace/submission-review/research-update-2026-10-17 contains PPTX, PDF, slide images, overview, frozen data with 41 source hashes, source-linked speaker notes, visual provenance and validation. Generated previews were inspected; text and shape bounds, English text, all background images, raw SLA counts and package checksums passed. PDF uses shared explicit drawing coordinates, not an Office rendering.

The team ZIP and checksums were refreshed. Prior deck/ZIP/manifests are backed up under submission-archive/before-research-deck-20261017T144946Z. AI job scripts are byte-for-byte unchanged and still target the historical validated N48 deployment; this is a presentation research update, not a new official configuration promotion. HPC_Task/job_scripts and logs remain empty. No external submission, GPU job mutation or autopilot activation occurred. Fresh queue check before publication: H200 24320/24321/24322/24327 pending Priority; H100 221151 queued and 221152/221153 held on expected dependencies.

## 2026-10-17 16:59 UTC — reviewed controls and new submissions on both systems

Fresh H200 N56 control 24320 passed sealed protocol/payload/runtime/SLA/short/long review: 2,670.321 good tokens/s, TTFT 851.827 ms, ITL 16.267 ms, joint SLA 98.8002%. Fresh H100 N50 combo control 221151 passed full protocol/payload/runtime/short/12-long checks: 2,231.429 good tokens/s, TTFT 495.915 ms, ITL 19.386 ms, SLA 98.4286%. This exceeds the old H100 peak by only about 0.072% with the same configuration; it is repeat variation, not an established new optimisation. Updated the all-history metric report and added later-control context to the cross-platform report without refitting frozen calibration or prediction.

H100 DeepGEMM job 221152 failed before scoring at the global 1,200-second worker readiness deadline. No scored export exists. Representative prefill logs reported load_weight=912.66s and prefill CUDA graphs=161.62s, and reached engine startup/local warmup near the timeout. No backend incompatibility traceback was found; successful benchmark operation remains unverified. Collected both completed H100 allocations and preserved raw evidence.

Submitted H100 retry 221177.pbs111 after queued prefetch 221153, verifying the afterany dependency. Only the worker readiness deadline changes from 1,200 to 1,800 seconds; total allocation remains 45 minutes and all benchmark/SLA/quality settings remain fixed. Submitted H200 DeepGEMM prefill N58 job 24352 through the existing non-AI watcher. This tests whether the new prefill backend shifts the load frontier; compare historical same-load combo 24236 with time-drift caveats, and pending independent N56 repeat 24327. No automatic N60 or repeated failed startup campaign is authorised by this plan.

Fresh ledger as of 18 October 00:40:02 SGT: used 17,075.200 SU, balance 46,924.800 SU, In Doubt 0. Charges for 24:51 control and 20:13 failed startup reconcile to the ledger increment within 0.01 SU. Their reservations are released into accounted usage. Prefetch 221153 and retry 221177 reserve 3,072 SU maximum total; headroom under the unchanged internal 51,000 SU planning limit is 30,852.800 SU.

Reviewers are prepared for corrected TP8/EP2 job 24321, DeepGEMM repeat 24327 and N58 job 24352. Existing 24281/24291 reviews passed regression checks; pending jobs correctly return WAITING. Files and full plan: qwen-experiments/nscc-pbs/inspection/manual-20261017-continue-1655/. No AI autopilot, slides, official scripts or external submission were changed in this research turn. The previously built presentation keeps a frozen copy of its historical-record input for reproducibility.

## 2026-10-17 17:54 UTC — transport repair and prefill graph trials

Job 24321 failed before benchmark: both TP8/EP2 workers became ready (all workers ready at 280s), then one P/D warmup request hit the 480s HTTP timeout. Summary is empty. Corrected the preparation mistake: this equal-TP8 layout reused the heterogeneous-TP patch, leaving equal-TP whole-pool descriptor setup active. Its sole role in the stall is not directly profiled; cancellation aborts are secondary. Reused the exact equal-TP patch previously validated on GPU in 22809, rechecked 936 byte-range cases and five fallback guards in an isolated copy, and submitted corrected H200 job 24375. Require all-rank equal-TP activation and full scoring/output checks; do not retry unchanged 24321 or extend timeouts blindly.

Engine startup logs show prefill CUDA graph setup taking 106.51–161.62 seconds. Exact staged source provides --disable-prefill-cuda-graph without disabling decode graphs. Submitted one-factor graph ablations: H200 24376 at N56 versus 24320; H100 221181 at N50 versus 221151. Both retain auto prefill MoE and existing decode kernels. Faster startup may cost throughput; evaluate the two separately, account for loading/cache/node confounds, and do not select a slower ranked configuration just for cheaper startup. Full plan and source-bound validation: qwen-experiments/research-followup-20261017-1755/PLAN.md.

Fresh H100 balance remains 46,924.800 SU (used 17,075.200; In Doubt 0), ledger as of 18 October 01:40:02 SGT. Three queued jobs 221153 → 221177 → 221181 have verified afterany dependencies and reserve at most 4,608 SU total. Internal operating headroom after reservations: 29,316.800 SU. H200 queue contains 24322, 24327, 24352, 24375, 24376, all pending at the recorded snapshot. No new benchmark winner is claimed. Autopilot remains OFF; no slides or official package scripts changed.

## 2026-10-17 18:33 UTC — raw-request tail diagnosis while queues are full

Direct scheduler checks: H200 24322, 24327, 24352, 24375 and 24376 are pending Priority. H100 221153 is queued; 221177 and 221181 have expected sequential dependency holds. Project balance remains 46,924.800 SU, used 17,075.200, In Doubt 0 (ledger as of 18 October 02:20:01 SGT). No new job was submitted or GPU credit spent in this turn.

Reconciled raw profiling requests with exports for H200 24291/24320/24236 and H100 221151. In the three H200 runs all 20/20/22 misses are TTFT-only, with zero ITL misses. Every TTFT-missing request started in the first approximately 30 ms of the scored phase. H100 has 19 TTFT-only and three ITL-only misses; all its TTFT misses also started in that initial burst. The first second contains exactly the configured concurrency: 56/56/58/50 requests. No recorded warmup request overlaps the first profiling request in any of these journals, rejecting the specific hypothesis that unfinished warmup doubled the initial decode load in these observations. This timing association does not uniquely identify prefill, router or KV delivery as the cause. Keep every initial request in the score and do not alter locked warmup/seed/thresholds.

At unchanged total request throughput, eliminating existing misses in 24291 offers only about 1.2% additional goodput. That is a fixed-rate counterfactual, not an achievable speedup prediction. Larger gains require improved service rate too. Full data, raw hashes, timing bins, formulas and caveats: qwen-experiments/research-followup-20261017-1830/RESULTS.md, tail-analysis.json and burst-analysis.json.

Prepared but deliberately NOT ARMED OR SUBMITTED: s10-prefill-deepgemm-chunk8192-n56. This changes only chunk4096 to chunk8192 relative to the DeepGEMM N56 candidate and keeps all other execution files identical. It tests a backend/batch-size interaction; old auto-runner chunk8192 lost and must remain a negative result. Conditional-candidate.json requires reviewing pending DeepGEMM confirmation 24327 and graph ablation 24376, then a free queue slot, before submission. Shell/hash validation passed. No new schedule, background Codex, slide update or official script promotion.

## 2026-10-17 19:44 UTC — queue check and H100 reviewer ready

All five H200 jobs remain pending Resources. Direct sinfo shows both hpcai nodes g1/g4 allocated; squeue --start gives no ETA. This is lack of available resources, not a new measured deployment failure. H100 221153 remains queued and 221177/221181 retain expected afterany holds. Credit unchanged: balance 46,924.800 SU, used 17,075.200 SU, In Doubt 0 (ledger as of 18 October 03:40:01 SGT). No queue positions changed or jobs submitted.

Completed nscc-pbs/review-current-prefill.py for the three H100 trials. It checks terminal status, sealed frozen payload, full N50 protocol, task-side runtime activation for prefetch/DeepGEMM/prefill graphs, BF16 KV and eight-rank MNNVL/FlashInfer decode proof, short and long quality, and compares to fresh 221151. Startup diagnostics remain separate. All pending jobs return WAITING. Three real-control rejection checks correctly fail if the candidate setting is absent. Details: qwen-experiments/research-followup-20261017-1945/STATUS.md. This prepares review; it does not establish new GPU results. Autopilot remains OFF.

## 2026-10-17 23:43 UTC — gain confirmed, platform difference, invalid topology closed

Reviewed H200 24327: 2,716.787 good tokens/s, +1.7401% versus fresh 24320, full protocol/runtime/short/long pass. Together with 24291, N56 DeepGEMM averages 2,716.315. N58 24352 passes at 2,718.080 but adds only 0.048% versus N56 repeat with higher TTFT; no automatic higher load. H200 prefetch 24322 passes at 2,665.572 (−0.178%), with no demonstrated startup benefit.

Equal-TP repair 24375 successfully warmed its P/D path and reached measurement, then FAILED acceptance: SLA 1.9978%, goodput 28.329, short 0/8 with seven new failed cases, long 11/12. Quarantine the candidate and retain all outputs. Updated nixl-equal-ondemand/VALIDATION_STATUS.md: CPU range tests and old GPU execution do not establish complete model correctness; exact root cause is not isolated. No unchanged retry.

Reviewed H100 prefetch 221153: 2,241.336 (+0.444%), walltime 15:45, full checks pass. Observed prefill weight loading ~306s versus ~921s control; cache/node/order remain confounded. Reviewed DeepGEMM repair 221177: 2,232.720 (+0.0579%), walltime 25:28, full checks pass. Its H200 gain does not establish an H100 improvement.

Submitted H200 24425 (DeepGEMM/chunk8192, graph-on retained) and 24426 (DeepGEMM/graph-off, decode unchanged). The old graph-review precedence was an unnecessary self-imposed dependency; the two tests keep changes separate and DeepGEMM is now independently confirmed. Submitted reverse-order H100 pair 221194 prefetch → 221195 control after graph trial 221181, identical readiness bounds, max 3072 SU new reserve. Dependencies verified; uncertainty rules and active-job caps retained.

Ledger as of 18 October 07:20:01 SGT: Used 17,612.800, Balance 44,851.200, In Doubt 1536 SU. 221153 is reconciled. Completed 221177 remains conservatively reserved until its terminal charge reaches Used. Total outstanding reserves including ledger lag and new pair: 6144 SU; internal-limit headroom 27,243.200 SU. Balance already excludes prepayment; no double deduction. Updated current metric records and cross-platform report while retaining frozen calibration. Full results, receipts, validators and decisions: research-followup-20261017-2335/RESULTS.md. No new AI scheduling, slides or official package scripts changed.

## 2026-10-17 23:55 UTC — two additional Slurm jobs submitted

At the user's explicit “submit” request, verified three existing Slurm jobs and the full three-job PBS chain. Submitted and verified H200 24428 (confirmed DeepGEMM with N54 load, bracketing N56/N58) and 24429 (same DeepGEMM N56 benchmark, followed by a separate N48 diagnostic profile). Each is 16 H200 / at most 17 minutes; all original model, backend, chunk, graph and score settings remain fixed except the stated load/profile switch. Profile code matches the previous audited 48-concurrency, 4-prefill/32-decode-step diagnostic and runs after scoring. Initial preparation validation failed on an incorrect source-text anchor before arming; corrected the anchor and passed checks before submission. Full own Slurm queue now has five pending jobs; no queue positions replaced.

No new PBS job because 221181 → 221194 → 221195 already fills the three-job active cap. Fresh ledger as of 18 October 07:40:01 SGT: Used 18,482.062 SU, Balance 45,517.938 SU, In Doubt 0. The 221177 terminal charge (869.262 SU) is now reconciled and its extra conservative reservation released. Three pending jobs reserve 4,608 SU; internal 51,000 SU limit headroom is 27,909.938 SU. No double prepayment deduction.

Full plan, validation, scheduler IDs and fresh PBS ledger: research-followup-20261017-2355/. Scored-result reviewers include new job IDs; profile coverage still needs a separate all-rank trace review after completion. No BTC upload, slide update, official-script promotion or new AI scheduling.

## Live status update — 19 October 2026

This user-requested status/login check supersedes older queue, VPN and credit snapshots below. Both own queues are empty; VPN and SSH restored at 04:01 UTC with private cache retained. Five H200 runs and three recovered PBS runs pass local protocol/SLA/output checks. H200 24647 repeats 2780.483 good tokens/s; H100 221341 N52 reaches 2398.728, awaiting an independent N52 repeat. Fresh PBS balance is 36800.853 SU, In Doubt 0; all three terminal reservations reconciled. No new job or AI schedule was submitted. Full report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0400/RESULTS.md. Autopilot remains OFF. Older access restrictions describe their historical checks; this login was explicitly requested by the user.


## Manual continuation — 19 October 2026

Four H200 trials 24721–24724 and two serial PBS trials 221589→221590 were explicitly submitted after user continuation, source review and live queue/credit checks. New maximum reserve 3072 SU, internal headroom 20728.853 SU; no budget increase. No new score yet. Latest report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0412/RESULTS.md. This supersedes scheduler/access/budget snapshots below; standing safety and acceptance rules continue. Autopilot remains OFF and no background watcher was started.


## Manual result review and next batch — 2026-10-19T05:32:52.311985+00:00

H200 24722 N60 passes at 2839.532 good tokens/s (+2.1266% vs fresh 24721); H100 221590 N54 passes at 2430.891 good tokens/s (+0.8123% vs fresh N52 repeat 221589). All local terminal/protocol/runtime/short/long gates pass; official accuracy unverified. Submitted H200 24732 N60 repeat and 24733 N62; PBS 221645 N54 repeat → 221646 N56, new maximum 3072 SU. Older 24723/24724 keep positions. Conservative internal headroom 18814.542 SU; no budget increase. Full readable report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0527/RESULTS.md. Autopilot remains OFF. This supersedes older queue/measurement/credit snapshots below.


## Private GitHub publication and history correction — 2026-10-19T05:48:14.782568+00:00

The owner authenticated GitHub CLI and requested repository creation, at least 60 commits and natural conventional subjects instead of generic import categories. Created private `https://github.com/trungdangtapcode/apac-hpc-ai-research` and verified the initial 50-commit push. Rewrote 57 existing subjects and aligned dated reconstructed record committer dates to their retained author dates; every per-commit tree is unchanged. The mapping preserves old IDs, subjects and date policy. Later publication/recovery/handoff commits contain real current changes. Use force-with-lease only for this explicitly requested correction; ordinary future milestone pushes are regular. GitHub credentials remain outside the archive. The sibling artifact store has not been uploaded, and no new scheduler, VPN, GPU or budget action was performed here. See ../reports/github-publication-20261019/REPORT.md.

## Manual optimisation — 2026-10-19T06:04:59.145550+00:00

H200 24724 passes at 2938.628 good tokens/s, +5.6907% versus fresh same-N58 control 24721. Chunk-12288 job 24723 passes but loses 2.3789%; close it. Submitted H200 24736/24737/24738 for fresh control, independent interaction repeat and N60. Existing 24732 running, 24733 pending. Submitted one source-checked H100 N54 prefill Tree trial 221669 after 221646, preserving 221645→221646→221669 serial chain. Total PBS max reserve 4608 SU; ledger Balance 36024.320 SU, internal headroom 18416.320 SU, no budget increase. Full local gates and actual Tree trace activation required. Report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0600/RESULTS.md. No official accuracy claim, slides, organiser upload or AI schedule; autopilot OFF. Supersedes older snapshots below.


## Research journey report and commit category — 2026-10-19T06:19:11.447795+00:00

The user requested a self-contained Markdown explanation of how performance improved, whether the latest point is best, and when to change direction; commit category must be `report`. Created workspace/reports/research-journey-20261019/REPORT.md with units, exact request/count/time arithmetic, a source-linked H200 trajectory, matched comparisons, failures, evidence limits and prioritised future decisions. The historical scan finds 99 eligible H200 and 61 H100 full-protocol observations; this is not a fresh quality audit of every old run. Reviewed completed 24732 at 2836.531 good tokens/s with all local gates; it repeats the different auto-decode N60 source and does not validate 24724's HPC-Ops interaction. 24724 remains the best locally accepted H200 observation, pending its independent repeat and official accuracy. New top results do not establish a global optimum or contest ranking. No new GPU job, budget or VPN/AI action.

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


## Extended run inspection — 20 October 2026

The user asked for utilization, resource usage, log and insight inspection for each run. Existing raw request/runtime/output/cost checks and selected CPU/GPU diagnostics do not establish uniform resource coverage. Added six sealed H200 extended inspections: all have TTFT p99 above 3000 ms while passing the existing joint fraction; 24738 has TTFT p99 3230.452 ms and ITL p99 15.720 ms. Sparse whole-run prefill queue peaks and decode KV token occupancy are observations, not phase-aligned causes. AIPerf telemetry endpoints are empty; no continuous GPU utilization/power/VRAM claim. Found 24819 start-profile HTTP 200 responses misclassified by unconditional JSON parsing, plus stop HTTP 500; 16 sealed traces still exist. Prepared a derived HTTP fix with six local fixture checks, not deployed to frozen jobs. Full report: [extended inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md); [reasoning entry](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261020-observability.md).

Every completed-run review should distinguish collected, inspected, findings, limits and next hypothesis. Include tail/error/concurrency, role queue/batch/KV, runtime/diagnostic and cost evidence; mark missing data explicitly. Future derived bundles need bounded matched hardware/server telemetry and phase markers after interface/overhead validation. Those collectors are not implemented/deployed by this audit. No GPU job, queue/credit refresh, authentication, slide or automation change.


## Reproduced N60 and observed polling submissions — 20 October 2026

H200 24913 passes at 2989.175 good output tokens/s, independently repeating 24738 = 2990.151 and +5.295% above fresh auto control 24912. Auto N62 24914 passes at 2890.878; keep HPC-Ops N62 24915 position. H100 222027/222028 both pass at 2420.945/2401.284: FA3 lowers mean TTFT but loses 0.812% goodput and increases ITL, so retain FlashInfer. Raw scored failures are 22 TTFT breaches per run and zero ITL/error/cancel breaches; all rank CPU/GPU traces inspected, without claiming a large CPU bottleneck.

Submitted three matched off/on/receive-2 pilots per platform: H200 24926/24927/24928 and serial PBS 222048→222049→222050. At 01:43 UTC H200 new group plus old 24915 were Resources-pending; PBS R/H/H. New bounded resource collector and phase markers are deployed in those frozen bundles; actual telemetry coverage and observer overhead are not yet verified. No numerical/workload change. Earlier “collector not implemented” status is historical. Local fixtures and seven source-file hashes agree across both images; control/candidate differ only in polling interval after observation settings match.

Published Used 34972.443 SU, Balance 29027.557 SU; four terminal charges reconcile 937.244 SU. New maximum reserve 4608 SU, internal headroom 11419.557 SU under unchanged cap/buffer. Existing access reused, no authentication, background AI, slides or official accuracy claim. [Full result/insight/next-decision entry](/home/apacsc42/workspace/reports/research-journey-20261019/journal/entries/20261020-receive-polling.md). Older states below retain their timestamps.

