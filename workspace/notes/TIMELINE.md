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

## 18 October 2026, 13:37 UTC — progress clarification and live queue

No additional completed measurement since the 13:27 review. H100 221339 is running; 221340/221341 held. All five H200 jobs remain pending Priority. No new submission because both campaign queue caps are occupied. Confirmed H100 decode gain and provisional prefill/chunk gains are separated in [progress explanation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-1337/PROGRESS.md). Do not add percentages across loads/platforms or treat local output checks as organiser accuracy certification. Earlier snapshots remain historical. Autopilot stays off.

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

# Các mốc cần truy lại

Ngày15/10/2026, giờUTC trừ khi ghi khác. Lịch sử từng wake xemHISTORY, chi tiết
từngjob xemRUNS và artifact. Đây không phải queue trực tiếp.

| Mốc /job | Điều đã biết và bài học |
|---|---|
| HelloGPU20201, trước15/10 | sbatch chạy trêng1, thấy1H200 theoallocation; bash trực tiếp thiếuSLURM_SUBMIT_DIR |
| Topology17ứng viên | Có lần lỗiNIXL/transport; không được tính lỗi là đã benchmarkxong; log được giữ |
| 23616,23773 | N53RR lặp2433,41/2438,47goodt/s |
| ~12:17VPN | snx-rsIPsec/TCPT rootless kết nối, sau đóSSHNSCC thành công |
| 220453–220457PBS | Lỗi cú pháp`pbsdsh --` và environment khi chạy rawSquashFS;220457probe16H100 thành công |
| 23776 | CUTLASSillegal memory access khi capturegraph; chưa có điểmbenchmark |
| 23777 | FlashInferN52:2440,39goodt/s,SLA98,95%; một quan sát, không chứng minh vượtN53 |
| 15:42,16:00,16:30 | Những lượtCodex tự chạy đầu thành công; báo cáo lưufile, không gửi vàochat |
| 16:14 | Checkpoint24shard và haiimagesNSCC đã tải/verify xong |
| 23778 | MNNVLN52:2592,16,SLA99,01%; watcher gửi repeat23839 |
| 23780 | AttentionDP+DeepEPN52:2549,20,SLA98,87%; watcher gửi repeat23859 |
| 220486 | PermissionErrorTritoncache; pbsdsh137 không tự chứng minhOOM; retry dùngprivate/tmp |
| 220489 | Prefill vẫn load khi readiness600s hết; không cóbenchmark; đổi deadline tuyệt đối1200s |
| ~17:08–19:00 | Codexquota làm lượt tự chạy bị cắt/từ chối; Slurmwatcher vẫn sống; sửa retry/backoff |
| 220562 | BaselineH100 thành công,N32:1565,16,SLA100%; startup~20phút,total23m33s |
| 20:03 | Gửi220575PBS45phút, sáu mức tải;23904–23906H200 bổ sung ba slot |
| 20:07 | Campaign16384SU tổng; cron kiểmtra5phút; backendH10004/05 đã chuẩn bị |
| 20:12:38 | Lần xác nhận cuối220575RUNNING trước mấtVPN |
| 20:17:01 | VPNLinux log`IKE SA expired, disconnecting tunnel`,exit0 |
| 20:40:05 | Login lạiVPN thất bạistatus0; chưa rõ nguyên nhân; không phải lỗiSSH |
| 20:47:05 | Login lần tiếp theo cũng thất bại; người dùng nóiWindows vẫn kết nối24giờ |
| Sau kiểmsourcev6.5.1 | Phát hiện defaultIKE28800s; helper cũ bỏ sót. Đổi sang86400s cho kết nối mới; chưa kiểm chứng24giờ |

## Những cách giải thích đã được sửa

- “Khôngsudo thì khôngcàiVPN” đã bị thực nghiệmrootless bác bỏ.
- “24giờ đã chỉnh nghĩaVPN24giờ” sai: thay đổi ban đầu làSSHControlPersist.
- “Chưa biết vì sao hếtIKE” nay có bằng chứng mặc địnhclient8giờ và nhánh tự
  ngắt; vẫn chưa xác định nguyên nhân từ chối login mới.
- PhiênWindows của người dùng vẫn tốt; không được suy rộng lỗiLinux thành
  gateway hết phiên hay toàn hệ thống hỏng.
- File ghi “đã kết nốiVPN” ở đầu hướng dẫn cũ là lịch sử thành công, không phải
  trạng thái hiện tại. Luôn kiểm tra tunnel thật.

## 16/10/2026

-00:17:42–00:18:46UTC: người dùng yêu cầu thử lại credential. Lần này helper đã đề xuấtIKE86400s. Gateway từ chối xác thựcstatus0 sau~64s; không có tunnel/SSH. Chưa có phản hồi DUO từ người dùng, không kết luận nguyên nhân.

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

## Queue kiểm trực tiếp — 2026-10-16 14:10 UTC

Người dùng hỏi đã submit tiếp chưa. Không gửi job mới trong lượt kiểm tra này.
Slurm: 23974 COMPLETED/0:0 (13:46:31–13:55:35 UTC); đây là trạng thái scheduler, chưa review phép đo.
23975 và 24009 vẫn PENDING(Resources). Watcher 419440 còn chạy.
PBS `qstat -u apacsc42` qua existing SSH thành công, queue riêng đang rỗng.
Codex autopilot vẫn tắt. Cần review 220721/220722 và matched control trước PBS qsub mới;
combo N54 còn chờ gate repeat/long của 23975, không gửi biến thể tùy tiện.

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

## Cấu hình tốt nhất có dùng chung hai cluster được không? — 2026-10-16 15:02 UTC

Không mặc định chuyển được hiệu năng: Firmus dùng16H200/Slurm, NSCC dùng16H100/PBS. Cùng modelFP8, topology8prefill+8decode (2×TP4EP1 + TP8EP8), RR/NIXL và protocol4000/200,60/120/30; launcher/container paths và tải tối ưu khác nhau. Dữ liệu hiện tại không đủ để quy nguyên nhân chênh lệch cho một thành phần phần cứng cụ thể.
H200: peak đã review MNNVL N54 job23924=2634.03goodtok/s,SLA98.90%, chưa lặp N54. ComboMNNVL+FlashInfer N52 jobs23904/23973=2631.09/2632.06, tín hiệu lặp tốt hơn nhưng23975+long còn chờ. Freshcontrol23974=2594.03.
H100: MNNVL N42 job220720=2041.97goodtok/s,SLA99.06%, mới một lượt; thiếu runtime8rank proof. Cặp220908control→220909repeat đangQ/H để xác nhận. StandaloneFlashInfer N32/34 thấp hơnbaseline1.79/1.40%; không suy comboFlashInfer+MNNVL trênH100 cũng giảm vì chưa đo combo.
Không xếp2634vs2042 thành gain thuật toán: khácGPU/tải. Chọn riêng config từngcluster, so cùngN vớicontrol cùngcluster, kiểmSLA/error/short/long/runtime và lặp. Accuracy99%BTC chưa xác minh.
Queue kiểm trực tiếp:23975/24009 PENDING(Resources);220908 Q,220909 H dependency. Autopilot giữtắt.

## Manual status — 2026-10-16T17:26:55.321610+00:00

23975 completed0:0 at16:54:24UTC; full offline seal/raw/runtime review passes.
ComboN52=2632.6099goodtok/s,SLA99.0226%,TTFT634.415ms,ITL16.2269ms;long12/12PASSED.
Three combo runs mean2631.920vscontrolmean2593.038,+1.4995%;freshcontroldrift+0.0573%. Descriptive replication, not statistical/accuracy proof.
N54 gate met; wrote bounded one-point plan and armed s10-combo-n54 in existing watcher,16H200/17min, same execution plus load52→54. No newAI automation.
24009 still PENDING(Priority).
NSCC existingSSH attempt returns Permission denied(password),exit255. VPN persistent status shows live pane andsnx-tun10.103.62.12. This is SSH authentication failure while tunnel exists, not evidence of VPN expiry; no new auth/DUO attempted.
220908/220909 current states UNKNOWN; previousQ/H only historical. Retain3072SU reservations, no blind retry/newqsub.
Evidence: qwen-experiments/nscc-pbs/inspection/manual-20261016-status/wave10.json.

17:28UTC watcher confirmed submitted comboN54 24131.

## N54 terminal results — 2026-10-16 23:28 UTC

239/241 queue checked directly: own Slurm queue empty.24009 COMPLETED0:0 at20:38:14UTC;24131 COMPLETED0:0 at21:25:41UTC.
24009 MNNVL N54=2629.5067goodtok/s,SLA98.9004%;independent same-load reviewer MEASURED_SLA_PASS.
24131 comboN54=2654.1720goodtok/s,SLA98.9117%,TTFT736.693ms,ITL16.2688ms,0errors/cancel,long12/12PASSED.
Sealed raw/protocol/runtime/short review and exact execution/runtime comparison vs23975 passed.
Gain+0.8190%vs23975comboN52;N54singleobservation,not repeatability/organiseraccuracy proof. Current highest observed passing goodput.
Existing Slurm watcher PID419440 no longer running after all queued work ended; no restart/automatic newload.
PBS query existingSSH again Permission denied(password);220908/220909 remainUNKNOWN;noauth/DUO,retainreserves.
Evidence:qwen-experiments/nscc-pbs/inspection/manual-20261016-final-n54/. No new job submitted in this status turn;Codexautopilot staysOFF.

## Status 2026-10-17 00:50 UTC

Live Slurm ownqueue empty;24009/24131 remainCOMPLETED0:0. No new benchmark or submission. Best reviewed24131=2654.172goodtok/s,SLA98.9117%. VPN pane alive/interface present; existingSSH againPermission denied(password), no auth/DUO attempted. PBS220908/220909 currentstatesUNKNOWN; keep3072SUreserved. Codexautopilot staysOFF.

## Auth and submissions — 2026-10-17 00:57 UTC

User explicitly requested reauthentication and more GPU submissions. SSH password login succeeded through existing VPN on a2ap-login01; no VPN restart or DUO. Earlier Permissiondenied was batchSSH auth failure; exact cause of old session loss remains unproven. No secrets saved.
220908/220909 both terminalF/exit0,walltimes32:10/42:18;collected/sealed/rawprotocol/short/long reviewed. Freshcontrol N32/34=1563.237/1624.351;MNNVLrepeat1680.796/1758.237,+7.5202/+8.2424%. MNNVLN42=2041.093,SLA99.055%,nearoriginal2041.966. ControlN36SLA30.784% retained.
New tasklogs establish expectedTP/EP/NIXL,BF16KV allocation and MNNVL ranks0..7/world8;both12longPASSED. No claim99%organiseraccuracy.
Submitted H20024174comboN52freshcontrol,24175comboN54repeat;bothPD(Resources) confirmed. Existing deterministicwatcher restartedPID3860355 only for authorisedGPUwork; noAIautopilot.
Submitted H100220998 MNNVLcapacityN42/44/46/48 (R)→afterany220999 MNNVL+FlashInfer interaction sameN (H). Stop-onfailedSLA;16H100/45min each,max1running;dependencyverified.
Budgetpriorused8204.517SU,balance55795.483SU,InDoubt0;new3072SU reserved underlock;campaignheadroom5107.483SU. Previouspair3072SUreservations fullyreconciled fromactualcharges.
Plans/validation/collection/review/submissionevidence:nscc-pbs/inspection/manual-20261017/ andserving-tuning-10/PLAN.md. Codexcron remainsabsent;PAUSED stays.

## Status 2026-10-17 01:20 UTC

24174 complete0:0/fullsealedreviewpass,2632.9636goodtok/s,SLA99.0226%,longPASSED.24175running5m39s,workersreadyandconfirmN54started,notresult. H100220998running22m22s,HTTP200prefilllogs;noexportsummaryyet.220999helddependency. ExistingSSHsucceeds. Ledgerused8204.517,balance54259.483,InDoubt1536alreadydeducted;localmaxpairreserve3072unchanged. No new submissions;Codexautopilotoff.

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

## Tận dụng hai cluster — 2026-10-17 09:20 UTC

User explicitly requests submitting on BOTH servers to optimise elapsed researchtime. Keep useful independent experiments queued on SlurmH200 and PBSH100 concurrently when budgets/resources/gatespermit. Do not interpret this as increasing campaigncap or authorisingAIautopilot. CurrentH100remaining847.075SU cannot cover observedstartup+full16GPUbenchmark;do not spend beyond16384SUcap. H200workcontinues;resumeH100submissionsonlyifnewplanfitsremainingbudgetoruserexplicitlyincreasesbudget. Do notpromisebothqueuesalwaysactivewhencreditblocksone.

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

## Tài liệu phải dễ đọc — 2026-10-17 10:01 UTC

Người dùng phản hồi PLAN.md khó đọc. Đã viết lại serving-tuning-10/next-evidence/PLAN.md bằng tiếng Việt có khoảng trắng đầy đủ, giải thích thuật ngữ, tách hai job, giả thuyết, khả năng xấu, control và điều kiện giữ/loại. Bản cũ giữ ở PLAN.original-20261017.md để truy lịch sử. Không đổi script, cấu hình hoặc queue.

Từ nay tài liệu người dùng đọc phải viết bằng câu rõ ràng, không dính từ hoặc nén thành chuỗi viết tắt. Ưu tiên mục tiêu/kết luận trước, bảng ngắn để so sánh; link bằng chứng kỹ thuật thay vì nhồi vào phần giải thích.

## Language policy — 2026-10-17 10:10 UTC

The user clarified: **Vietnamese for chat only. English for the codebase and all work artifacts**, including code, comments, documentation, research plans, reports, notes, tutorials, and submission materials. This supersedes earlier permission to write tutorials or learning notes in Vietnamese. Use readable English with normal spacing and explain unfamiliar terms. Do not translate immutable raw logs or historical experiment evidence.

The current prefill experiment plan has been rewritten in English. Existing Vietnamese historical documents remain historical; this update does not claim they have all been translated.

## Live status — 2026-10-17 10:18 UTC

Slurm24263N56benchmark/profile is RUNNING on g1/g4, elapsed6m19s at observation.24272N50holdout remainsPENDING with resourceavailability/reservationreason;24281batchlimit and24282TP8prefill remainPENDING(Priority). No new terminal result. Preserve queuepositions;no new submission or invalid benchmark/forecastclaim. Codexautopilot remainsdisabled.

## Benchmark/profile review and next trial — 2026-10-17 10:58 UTC

Job 24263 completed with exit 0. The sealed full benchmark, payload, runtime and short-output review passed: 2,667.465 good tokens/s, SLA 98.7995%, TTFT 856.622 ms, ITL 16.257 ms, zero errors/cancellations, and 12/12 long checks. This is another N56 control, not a new gain.

The separate diagnostic used 48 concurrent requests, not the 52 stated in older plans. All 16 expected rank traces contain kernels (4+4+8); all 415 diagnostic requests succeeded. Per-rank mean MoE shares of summed kernel time were 42.84%/42.77% for prefill and 27.99% for decode. These are not wall-time fractions or predicted speedups. Prefill/decode trace windows cover 4/32 steps and must not be compared as absolute phase times.

The start API returned HTTP 200 but the client failed to parse its response as JSON. Explicit stop calls returned HTTP 500 because profiling was no longer in progress. Keep these warnings. The traces are usable; no extra allocation is warranted solely to remove control warnings. The initial reviewer assumed EP appeared in every trace filename and failed before mutation; it was corrected to handle prefill filenames without EP.

The new evidence motivated one prefill-only DeepGEMM trial: job 24291 was submitted and verified PENDING(Resources). It changes only the prefill MoE backend at N56, keeping both TP4/EP1 workers and unchanged TP8/EP8 decode with MNNVL+FlashInfer. The old losing DeepGEMM trial changed decode; it does not establish the effect on larger prefill batches. The exact image source supports the backend and a standard-layout path, but GPU startup and quality remain unverified.

Queue snapshot: 24272 (N50 holdout), 24281 (prefill batch limit), 24282 (single TP8 prefill), and 24291 (prefill DeepGEMM) are all pending. No H100 job or additional H100 credit used. Codex autopilot remains disabled.

Readable evidence and plan: serving-tuning-10/profile-review-24263/RESULTS.md. Detailed profile audit: profile-review.json. Pre-submission payload/syntax checks: pilot-validation.json. Benchmark audit: nscc-pbs/inspection/manual-20261017-1054/benchmark-review.json.

## Queue check — 2026-10-17 11:18 UTC

Direct squeue and sacct queries confirm jobs 24272, 24281, 24282 and 24291 are all PENDING(Resources), with no start times or new measurements. Preserve their queue positions. No new job submitted in this status check. Codex autopilot remains off.

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

## Credit communication correction — 2026-10-17 14:06 UTC

The user questioned apparent rapid exhaustion of64,000SU. The last reconciled ledger shows15,536.925SUused(24.2764%) and48,463.075SUremaining(75.7236%), not847SUremaining in the project.847.075SU is only the remainder of the internally planned16,384SUresearch campaign. It is not a BTC quota or exhaustion of the original grant.

The campaign record maps the broad instruction to continue using GPU time to a16,384SUlimit; that numeric amount was a planning choice, not a numeric budget explicitly stated by the user in that record. Do not present it as an organiser-imposed cap or say the project cannot afford another benchmark. Keep budget changes distinct from this explanatory turn; no new credit query was possible after VPN expiry and no new job/cap change was made.

## VPN and SSH restored — 2026-10-17 14:09 UTC

The user explicitly requested another login. Confirmed the old VPN tmux pane was exited before removing only that dead terminal. Old private cache and raw private logs were preserved. Restarted the existing persistent launcher, submitted the previously provided credentials interactively, and established a new tunnel at10.103.62.13. No authentication/session contents were saved in notes. The terminal did not require additional MFA input from the assistant; do not infer what happened on a phone.

SSH password authentication then succeeded on a2ap-login02. A fresh PBS query showed no own active jobs. myprojects ledger22:00:02SGT:used15,536.925SU,balance48,463.075SU,InDoubt0. This is the project balance, not the internal campaign remainder847.075SU. The numeric16,384SUcampaign allowance was a planning limit, not BTC exhaustion or an amount explicitly specified by the user.

Detached the tmux client with its detach sequence. The VPN remains owned by persistent tmux, independent of the tool PTY. A subsequent status and batchSSH check succeeded after detachment. No new GPU job, budget amendment or Codex automation was requested or performed in this login turn.

## 2026-10-17 14:18 UTC — submissions on both clusters

The user requested continued submissions on both servers and clarified that the Slurm server is not credit limited. Three H100 jobs (221151, 221152, 221153) were submitted and verified in an afterany chain; three H200 jobs (24320, 24321, 24322) were submitted by the existing watcher. They test fresh controls, phase-specific compute/layout changes and prefill weight prefetch. Full plan and receipts: qwen-experiments/nscc-pbs/inspection/manual-20261017-1410/PLAN.md.

Corrected the budget interpretation: project balance is 48,463.075 SU, not 847.075 SU. The latter was the old internal campaign remainder. The user authorised continuation after this clarification. The revised 51,000 SU planning bound retains a 13,000 SU buffer; neither amount is an organiser quota. The batch reserves at most 4,608 SU.

H200 job 24282 failed before measuring because TP8/EP1 produces a 192-element MoE weight partition incompatible with FP8 block 128. TP8/EP2 gives 384; corrected job 24321 tests that layout. H200 job 24291 passed protocol/runtime/SLA/short/12-long review at 2,715.842 good tokens/s, +1.8136% versus 24263. An independent repeat is armed. Its first reviewer rejection was an overly narrow runtime delta allowlist; the revised review explicitly checks both main and speculative runner values and that speculative decoding remains disabled. Preserve both review files.

Autopilot remains disabled. GPU submissions do not authorise background Codex scheduling. No submission slides or BTC upload changed.

Independent H200 DeepGEMM confirmation is now submitted as job 24327 (pending for resources at 14:18 UTC). Four new H200 jobs and three new H100 jobs have confirmed scheduler IDs.

## 2026-10-17 — comparison by individual metric

Saved reports/metric-comparison-20261017/REPORT.md and data.json. Comparison scope is explicitly the recent reviewed H200 shortlist (same-load N56 plus N50 reference) and latest H100 combo sweep, not exhaustive all-history latency records. DeepGEMM leads H200 N56 goodput/TTFT/SLA in observed runs; batch limit one has lower ITL but worse goodput. H100 N50 leads goodput, N48 leads TTFT/SLA and N52 leads ITL in sweep 221058. Small SLA differences are descriptive; official reference accuracy remains unverified.

## 2026-10-17 — independent historical records for each metric

The user clarified that they want the best recorded value for each metric across history, not just the current shortlist. The previous response was too narrow. Saved a reproducible scan at reports/all-history-metric-records-20261017/build.py, records.json and REPORT.md. Only full 60/120/30 protocol, 4000/200 tokens, reported SLA pass and zero request errors/cancellations are ranked; short sweeps are excluded. H200 records: goodput 2715.842 (24291, N56); mean TTFT 328.900 ms (23773, N53); mean ITL 13.494545 ms (22517, N16); SLA 100% with multiple ties. H100 records: goodput 2229.827 (221058, N50); mean TTFT 303.288 ms (220720, N32, historical runtime proof unresolved); mean ITL 17.138286 ms (220909, N32); SLA 100% with multiple ties. These are independent observations, not one configuration achieving all records. Official reference accuracy remains unverified.

## 2026-10-17 — self-contained metric report and explicit units

The user corrected that the Markdown report must explain the metrics at least as fully as chat, and explicitly state every unit. Expanded reports/all-history-metric-records-20261017/REPORT.md with TTFT (ms), mean ITL (ms per token interval), goodput (requests/s and the reported conversion to good output tokens/s), joint SLA pass rate (%), concurrency N (requests), thresholds, worked examples, average-versus-per-request distinctions, quality versus latency, configuration labels, raw sources and historical evidence limits. Added REPORT.template.md and updated build.py so regeneration preserves explanations and units. Existing raw artifacts remain unchanged. This is an ongoing documentation requirement: reports must stand alone without reading chat.

## 2026-10-17 — explain every record-holding job

At the user's request, expanded reports/all-history-metric-records-20261017/REPORT.md with source-linked cards for all 13 unique record-holding jobs, including every SLA tie. Cards include GPU layout, prefill/decode workers, TP/EP, concurrency, all four measured metrics with units, configured flags, inherited submitted worker flags, representative runtime fields where available, optimisation rationale and evidence limits. Added job-details.json and run_details.py; build.py regenerates the full document without discarding explanations. Explicitly separate measured gains from hypotheses and preserve the unresolved runtime status of 220720. Added matched reviewer references for 24291, 221058 and 220909/220908. No raw artifacts or scheduler jobs changed in this documentation task.

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

## 19 October 2026 — live queues, restored PBS access and recovered results

Both own queues are empty. At the user’s explicit request, restored the existing tmux VPN and authenticated SSH without exposing or changing the private cache. No client MFA code requested; phone-side DUO unknown. H200 24647 passes at 2780.483 good tokens/s, +2.2688% versus fresh 24589. Recovered H100 221341 N52 passes at 2398.728, independent N52 repeat outstanding. N50 221346 passes at 2375.807. Fresh balance 36800.853 SU; reconciled three completed PBS jobs. No new submission or AI schedule. Full source-linked report: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-0400/RESULTS.md. Archive capture is a separate explicit local operation; no GitHub upload.

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



## Latest queue check — 19 October 2026, 11:26 UTC

No new result since the 11:11 UTC review below. H200 24733/24736/24737/24738 still pending for Priority; both hpcai nodes allocated. PBS queue empty; existing VPN/SSH access works without authentication or restart. Balance remains 34608.356 SU (ledger 19:20:02 SGT), Used 29391.644, In Doubt zero. No new allocation, budget change or schedule. Preserve H200 positions; no unchanged Tree retry or automatic H100 load increase. [Raw status evidence and interpretation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1125/RESULTS.md). Highest observations and verification limits are unchanged.


## Latest queue check — 19 October 2026, 11:45 UTC

No new result. H200 24733/24736/24737/24738 remain pending; reason changed from Priority to Resources while both hpcai nodes remain allocated. This does not establish queue rank or start time. PBS queue empty; existing VPN/SSH works. Balance remains 34608.356 SU (ledger 19:40:02 SGT), Used 29391.644 and In Doubt zero. No new allocation or research decision. Preserve queue positions and prior branch stopping rules. [Dated evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1144/RESULTS.md).

## Continue research and submitted batch — 2026-10-19T12:02:20.997548+00:00

The user explicitly corrected idle research: during active authorised work, review results, research the next distinct hypothesis and submit when capacity/budget permit without another reminder. Losing N56 or Tree is not a global stop. Actual new jobs: PBS **221827 → 221828 → 221829** (N54 fresh control/profile, HPC-Ops chunk6144, prefill Simple protocol/profile); H200 **24819** (N58 winning interaction repeat/profile), preserving four older queued jobs. Five active H200 jobs and three serial PBS jobs. New PBS maximum reserve 4608 SU; pre-submit Balance 34608.356, Used 29391.644, In Doubt zero; internal headroom 17000.356 SU under unchanged cap/buffer. New jobs have no measurements yet. Full plan, references, hashes and receipts: [research continuation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1200/RESULTS.md). Review each completion and continue justified work. No blind duplicates, unchanged loss retries, automatic load growth, AI schedules or background Codex. Highest observations/accuracy limits unchanged.


## Research continuation — 2026-10-19T14:27:36.052008+00:00

At the 14:18 UTC check all three preceding PBS allocations finished and H200's five jobs remained pending Priority. Submitted **221880.pbs111** for the already prepared dense FlashInfer-prefill N54 trial, source/fresh control 221827 passing at 2413.802 good tokens/s. The other completed trials show no clear throughput gain; preserve their separate reviews. Scoped Simple activation is unverified because separate N48 traces still show Ring LL. Chunk6144's derived prefill graph settings are now strictly checked against the exact runtime source. Published Balance 33270.898 SU, Used 30729.102, In Doubt zero; terminal charges 1337.458 SU reconciled. New maximum reserve 1536 SU; internal headroom 18734.898 SU. Continue researching and using available PBS slots within caps. [Submission and budget evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1418/SUBMISSION.md). No new peak, official accuracy, scheduler automation or slide claim.


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



## N62 accepted and research talk refreshed — 20 October 2026

Terminal H200 24915 passes all local review gates at 3022.035 good output tokens/s, +4.537% vs auto N62, with 1860/1884 qualifying requests. This is a single treatment observation; N60 is independently reproduced. Separate 16-rank diagnostic and missing continuous hardware telemetry are explicitly recorded. The owner requested the English presentation update. [Full reasoning and scope](../reports/research-journey-20261019/journal/entries/20261020-n62-presentation.md). No new GPU submission, PBS output review or official accuracy claim in this pass.
