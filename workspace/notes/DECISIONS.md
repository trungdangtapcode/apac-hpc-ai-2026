## 18 October 2026 — local Git preservation task

The user requested a local backup first, with GitHub CLI/authentication/upload deferred. Created `/home/apacsc42/apac-hpc-ai-research` plus its required sibling `apac-hpc-ai-research-artifacts`. The base capture has 17,570 retained source files, 477 verified unique external objects, about 93.31 GB logical data and 18.83 GB compressed objects. Metadata-backed import groups use real retained dates and current committer dates; no fake daily/month activity. User identity is `trungdangtapcode <tcuong1000@gmail.com>`. Intended later remote is private `trungdangtapcode/apac-hpc-ai-research`.

Authentication/session material is excluded. Two damaged archives are preserved as local-only review objects. Exact local container hashes match the tested contract. Public model weights and uncollected remote H100 results are outside the capture; metadata and reproduction limits are documented. Deep checksum and representative recovery tests pass. Local data is not protected against loss of this machine until copied off-host. Original research directories, queued jobs, VPN and disabled autopilot are untouched. This is an archive copy; later original-directory changes need a new explicit capture.

See [preservation report](../reports/local-repository-backup-20261018/REPORT.md) and the new archive README. Earlier experiment scheduler/credit statements remain dated snapshots, not live observations.

## 18 October 2026, 09:28 UTC — result-driven continuation and three new jobs

Standing user instruction: review each completed job, refine the hypothesis and submit the next justified experiment without waiting for an unrelated batch. Respect runtime/output gates, budget and queue caps. This does not enable Codex autopilot or replacement scheduling.

Fresh H100 control 221275 passes full local review at 2,248.459 good tokens/s. HPC-Ops repeat 221274 remains 2.4739% above this new control; its previous control comparison was +2.6073%. The original pair was +2.7955%. The direction survives a fresh reversed-order control, while first-token latency remains higher and inter-token latency lower. Official full-set accuracy remains unverified.

Submitted and verified 221284 (HPC-Ops N50 score then separate profile) → 221285 (HPC-Ops N50 with prefill chunk8192), after existing running 221276 (N52). New H200 24544 tests DeepGEMM chunk8192 at N58 after two small positive N56 observations. Existing pending H200 jobs retain positions. Full hypotheses, controls and stopping rules: [plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261018-0925/PLAN.md).

Ledger Used 22,072.889 SU, Balance 40,391.111 SU, In Doubt 1,536 SU (17:20:01 SGT). Reconciled 221274 charge 492.658 SU. Terminal 221275 charge 492.089 SU is still pending in ledger, so retain full reservation. New pair reserves 3,072 SU; total conservative outstanding 6,144 SU; planning headroom 22,783.111 SU. Prepayment is not deducted twice. No slide, official package, organiser upload, AI schedule or background Codex change.

Older dated entries below are historical snapshots.

# Yêu cầu và quyết định cần giữ qua các phiên

## Cách làm việc

- Trả lời ngắn, rõ, tiếngViệt. Câu hỏi kiến thức phải ghi vào note cùng lượt.
- Chủ động research→nhận định→submit→đọc kết quả→thử tiếp; tận dụng thời gian
  chờ GPU để chuẩn bị phần không cầnGPU. Không chỉ hứa hoặc chờ người dùng nhắc.
- Giữ mọi thí nghiệm và dữ liệu thô, bao gồm lỗi; không tính lỗi deployment
  như đã đo thành công. Không tự tạo kết quả, không báo queued làrunning.
- Có sửa kết luận cũ phải nói rõ, cập nhật phần hiện hành để không truyền sai
  qua phiên khác. Số liệu động phải kèm thời điểm/jobID.

## Phạm vi cuộc thi và tài liệu

- TrackQwen; không lẫnOpenFOAM. Gói `VNUHCM - TripleU/` gồmPresentation,
  AI_Task/job_scripts,AI_Task/logs,HPC_Task/job_scripts,HPC_Task/logs.
- HPC_Task để rỗng nếu không có bài; không thêm câu tuyên bố thiếuHPC vào slide.
- Bài nộp và slide phảiEnglish. Tutorial giải thích cho người dùng dùngVietnamese.
- Slide để **thuyết trình kỹ thuật**, không mô tảfolder/README hay nhồi“evidence”.
  Giữ theme hiện có, gradient nhẹ, background ảnh chìm nhưng thấy được, dùng
  ảnh đa dạng; tránh lấy cùng asset làm background và hình chính gây lặp.
- Không tự quảng bá pilot vào submission. Chưa có ghi nhận uploadBTC.

## Thực thi, budget và queue

- H200Slurm sharedcap5 pending/running theoQoS đã kiểm tra. Không hủy/requeue
  chỉ vìPriority; chỉ hủy khi người dùng yêu cầu hoặc có lý do kỹ thuật rõ.
- NSCCPBS tối đa3jobGPU pending/running trong chuỗiafterany đã kiểm, chỉ1job
  running và16GPU đồngthời (amendment16Oct05:53). Nhiều mức tải trong cùng
  allocation giúp tránh lặp20phút startup. Mỗi điểm giữ nguyên protocol.
- Commissioning ban đầu4096SU; sau baseline đạt và chỉ dẫn“tận dụng toàn bộ
  thời gian vàgpu”, đã công bố mở campaign **16384SU tổng**, giữ13000SU dự phòng,
  max45phút/job=1536SU dự trù. Không tiêu toàn bộgrant vì chỉ muốn bậnGPU.
- Lượt tự động phải ghi dự trù trướcqsub, đối soát job chưa chắc trạng thái,
  không nhân đôi khoảnInDoubt đã trừ khỏibalance.
- So candidate cùnghardware/protocol, repeat phương án tốt, kiểm tra output.
  SLA/goodput không phảiquality; smoke không thay fullaccuracy99%reference.

## VPN và quyền truy cập

- Người dùng cho phép cài/thửVPNrootless, kết nốiNSCC, dùngPBS đểresearch.
- Gateway đúng.sg; TLS phảiverify. Không dùngDocker/sudo nếu không cần.
- Không lưu password/OTP vàonotes/config/commandline; không xuất secret qua log.
- Đăng nhập lại khi có chỉ dẫn mới; không lặp thử mù khi gateway từ chối.
- Không yêu cầu người dùng ngắtVPNWindows đang tốt chỉ dựa trên suy đoán.

## Chỉ dẫn lịch sử trước16Oct05:40: xác thực và khôi phục
Người dùng phản đối login khi người giữDUO không có mặt; đã dừng thửxác thực. Yêu cầu tiếp theo là tìm session cũ local, không phải cho phép login mới. Search đã thực hiện, không cósessionblob được tìm thấy; không tự suy ra/serverWindows hết hạn.

## Tiếp tục nghiên cứu16Oct02:36UTC
Sau3wave9hoàntất,đãmởwave10đểđolặpgain1,49% bằng2combo repeat+1freshMNNVLcontrol,gửi23973–23975. Cácdòngno-repeatởsnapshotwave9khôngphảiuserhủy yêu cầu liên tục research. Giữsharedcap5,khôngN56hayVPNauthmới.


## Chuẩn bị đọc wave10 —16/10 02:46UTC
Đã có reviewer CPU vàguide;không thay kế hoạchqueued. Quy tắc review mô tả
thận trọng: so cả3control vàmọirepeat,không chọnpeak;gain chỉ đánh dấu lặp được
khi cảhai repeat hơn controlmới,meancombo hơnmeancontrol,tấtcảfullSLA90%.
Đây là tiêu chí phân tích cục bộ,không phải kiểm định thống kê haychỉ dẫn mới
củaBTC. Long thiếu/deferred/fail không chặn giữ benchmark đã đo nhưng chặn
gate viết plancomboN54;không tựsubmit bằng cờ reviewer.

## Lặp MNNVL N54 có giới hạn —16/10 05:20UTC

23924 đo đủ vàfinalaudit đạt2634,0344goodt/s,SLA98,9024%,ITL17,1102ms,
0lỗi/hủyrequest;hơnmean2N52 1,6004%,TTFT+88,1784ms. Trong phạm vi tiếp tục
research, mở đúng1repeat MNNVL N54 vào slot vừa trống, giữ12file thực thi và
protocol, dùng watcher hiện có. Kế hoạch cụ thể ởserving-tuning-10/PLAN.md;
đây là mở rộng mới sau số đo, không suy từ cờ reviewer hay gatewave7 cũ.
So repeat với23924 và3N52control kể cả23974 để thấy drift;khôngrepeat thứ3,
khôngN56/promotion;comboN54 vẫn chờ gate riêng. Không sửa payloadqueued.
Watcher419440 đã gửi24009;05:24:11UTC đủ5/5PENDING(Resources). Một điểm xác
nhận độc lập vẫn kế thừa budget-deferred retry hiện có của watcher, tối đa
3attempt nếu chưa đo đủ;không thêm gate retry. Giữ mọi attempt;reviewer yêu
cầu đọc tay nếu có replacement,không tự chọn điểm cao nhất.

## 16Oct05:53UTC: queueNSCC3job nốiđuôi
Theo yêucầusubmitnhiều,tăngsốpending/runningPBS1→3 nhưng chỉ1job16GPUrunning bằngafteranychain;khôngđổicampaign16384SU/reserve13000. Gửi220720→220721→220722,đãreserve4608SUtrướckhiqsub. HELDdependencylàbìnhthường,khôngreleaseđểchạycùnglúc.


## 16Oct06:01UTC: đồng bộ hiện hành và chuẩn bị reviewH100

Quyềnlogin05:40 đã dẫn đếnVPN/SSHthànhcông;không cóquyền choauth/DUOmới liên tục.
Giữphiên79786,chưa xácminh24h/SAcache. POLICYđược hợpnhất đểphầncurrentkhôngcòn
nóiSSHunavailable/220575unknown; bảncũ lưuarchive. Sửa nscc-budget submissionrule
còn1queued vàtrườngheadroomafterreserved14002,631→9394,631SU;khôngđổi cap hoặc
thêmreserve. Ledgerasof13:40Singapore vẫntrễso220720,giữtoàn bộ4608SU.
ReviewH100 so04/05/06độc lập với220575 cùngN;khônggánruntime từhashpayload,
khôngsuycompatibility/accuracy từsmoke. Collector bổsung PBSdeclaredoutputpaths,
chưa cóstdoutmới. ToolCPU mới có11+5kiểm đạt,kèm2lỗifixturesetupđãgiữ;không phải
candidateGPUresult. Khôngthay jobpayload hoặc tạoauthorization/promotion mới.


## 16Oct06:18UTC: thu runtime khi job còn chạy

220720 có serverinfo thực và2pairHTTP200 nhưng rolelogs rỗng;không suy đủ8rank
MNNVL từbackendflag hoặc1internalstate/endpoint. Chuẩn bị collector single-shot
chỉ đọc collect-live-runtime.py chojobown/R trongplan,khôngnewwatcher/modelrequest.
Giữ reportedstartup/config của05/06 trướcterminal đểso loader;khôngquy startup
choI/O từtiming. KVauto chưa phải dtype hiệu dụng. myprojects14:00Singapore đã
trừ1536SUInDoubt khỏibalance60082,631;giữ4608SUcampaignreserve/headroom9394,631,
khôngdoublecountprepaid. Không thaycap,queue hoặc quality/promotion gate.

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


## 16/10/2026 10:29 UTC — DP N54 và NSCC chưa truy cập được

23934 finalreview đạt2555.4232goodt/s,SLA98.7484%;soDP N52mean chỉ+0.4633%
vớiTTFT+145.1971ms,soMNNVLcùngN54−2.9844%. Kếtthúc boundedDPbranch3point,
khôngmởthêmDPrepeat/N56;ưu tiên4job hiệncó23973/23974/23975/24009.
Cap5khôngbuộcphảilấpslot bằngconfigchưađủgate;plancomboN54 vẫnchờgainlặp,
freshcontrol vàlongPASSED. Đây làquyếtđịnhphântích trongresearchđãgiao,
khôngphảichỉdẫnmớicủaBTC hoặcchứngnhậnaccuracy.

NSCChelper10:25 khôngcóliveVPNsession trướcSSH:khôngauth/DUOmới,khôngsuy
jobterminal từelapsedtime. Đánh dấu3jobUNKNOWN,giữ4608SU vàcreditledgercũlịchsử.
Archive06:26tar exit1 do thưmụcđangbiếnđộng vẫnđọcđủ102member;phụchồi3point
đãxong vàkiểmraw/protocolkhớp. Khônggắnterminalseal/finalqualitychobảnlivecopy,
khôngsửagốc. N34protocolđãkiểmởlượtnày;N36+31.8%làgoodputvớicontrolfailSLA,
khôngrawthroughputgain. N38khôngdùng. Xeminspection/wake-20261016-1025UTC/.


## 16/10/2026 10:59 UTC — chuẩn bị quan sát H100, không thêm allocation

Bốn H200 vẫnPENDING(Priority),NSCC chưa existingaccess;giữ4608SU và mọi gate.
Chuẩn bị riêng research-next/pbs-task-logging-01 để mởlog bên trong task trước
container;CPU12/12 đạt, chưa chứng minh trênPBS hoặc chữa nguyên nhân log rỗng.
Nếu ba terminal còn thiếu rolelogs, dùng cùng wrapper/shim/hash trên CẢ control
vàcandidate mới,review source và tạo seal trước reserve/submit; không sửa bundle
đãgửi,không chạy job riêng đểthửlogging. Cặp kế tiếp vẫn cần terminal/quality/
runtime/long/queue/credit gates. Khôngthaycap hoặc quyềnpromotion.

## 16Oct13:30UTC — Codexquota audit/fix
Userreportedrapidusage. Last24h133starts/35complete/95quotaerrors;
43.49Minputincl40.64Mcached,442203output incompletedlogs,not billing/%conversion.
Fixedmissingrgbackoff,semanticjobtriggers,andgrowinghandoff68.8KB→7.8KB;
archivedfullhistory,unchangedmodel/GPU/VPN. See research-autopilot/USAGE_AUDIT.md
andusage-fix-validation.json.

## Codex autopilot đã tắt — 2026-10-16 13:42:29 UTC

Theo yêu cầu người dùng: dừng tự gọi Codex để giảm tiêu hao quota.
Đã gỡ cron `ap42-qwen-autopilot`, tạo `PAUSED`, xóa trigger `FORCE` nếu có.
Không tự bật lại, tạo lịch thay thế hoặc gọi Codex nền nếu chưa được yêu cầu rõ ràng.
Giữ nguyên VPN, job GPU đã gửi và watcher Slurm không gọi AI.
Các hướng dẫn tự chạy bên dưới chỉ là lịch sử; không phải quyền tiếp tục autopilot.


2026-10-16T14:59:20.914804+00:00: Người dùng yêu cầu submit thêm. Gửi cặp control/MNNVL để xác nhận và sửa thiếu log; vẫn giữ Codex autopilot TẮT. Không mở lại cron hay Codex nền.

2026-10-17 00:57 UTC: User authorised auth+submit. SSHreauth only succeeded,noVPNrestart/DUO. NewboundedH200N52/N54pair andH100capacity/interactionpair;CodexautopilotstaysOFF.

## Keep useful GPU work queued — 2026-10-17 02:24 UTC

User explicitly reiterates: do not wait for reminders; when results, budget and resources permit, analyse then submit next useful jobs. CodexautopilotOFF only forbids automatic AIinvocations/cron, not ongoing authorisedGPUresearch. Prior decisions saying a turn ended do not revoke continuation.
Submitted andverifiedH20024189freshcomboN54control+24190comboN56probe,bothPD(Resources);boundedN56amendmentaftertwopassingN54runs,notblindloadincrease. Watcher4024591,nonAI. NoN58/promotion.
SubmittedandverifiedH100221020MNNVLN46/48R→afterany221021comboN46/48H,16GPU45mineach;stopfirstfailedload. Independent matchedfrontierreplication ofN48fail/pass,notnewrandomconfig.
220999sealedraw/fullprotocol/short/payloadpass,long12/12;actualtasklogsconfirmMNNVLranks0..7,FlashInferattentionranks0..7,BF16KV. N48=2204.528SLA98.7663%;priorMNNVLN48failed80.4896%.
Freshledger10:20SGTused10598.401,balance53401.599,InDoubt0;old09/10actualcharges2393.884SU reconciled;new3072SUmaxreservedbeforeqsubunderlock. Campaignheadroom2713.599SUaftermaxreserve,projectretain13000safe.
Evidence/plan/validation/submission:nscc-pbs/inspection/manual-20261017-next/. No Codexcron/backgroundmodelenabled.

## Tận dụng hai cluster — 2026-10-17 09:20 UTC

User explicitly requests submitting on BOTH servers to optimise elapsed researchtime. Keep useful independent experiments queued on SlurmH200 and PBSH100 concurrently when budgets/resources/gatespermit. Do not interpret this as increasing campaigncap or authorisingAIautopilot. CurrentH100remaining847.075SU cannot cover observedstartup+full16GPUbenchmark;do not spend beyond16384SUcap. H200workcontinues;resumeH100submissionsonlyifnewplanfitsremainingbudgetoruserexplicitlyincreasesbudget. Do notpromisebothqueuesalwaysactivewhencreditblocksone.

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

## Credit communication correction — 2026-10-17 14:06 UTC

The user questioned apparent rapid exhaustion of64,000SU. The last reconciled ledger shows15,536.925SUused(24.2764%) and48,463.075SUremaining(75.7236%), not847SUremaining in the project.847.075SU is only the remainder of the internally planned16,384SUresearch campaign. It is not a BTC quota or exhaustion of the original grant.

The campaign record maps the broad instruction to continue using GPU time to a16,384SUlimit; that numeric amount was a planning choice, not a numeric budget explicitly stated by the user in that record. Do not present it as an organiser-imposed cap or say the project cannot afford another benchmark. Keep budget changes distinct from this explanatory turn; no new credit query was possible after VPN expiry and no new job/cap change was made.

## 2026-10-17 14:18 UTC — submissions on both clusters

The user requested continued submissions on both servers and clarified that the Slurm server is not credit limited. Three H100 jobs (221151, 221152, 221153) were submitted and verified in an afterany chain; three H200 jobs (24320, 24321, 24322) were submitted by the existing watcher. They test fresh controls, phase-specific compute/layout changes and prefill weight prefetch. Full plan and receipts: qwen-experiments/nscc-pbs/inspection/manual-20261017-1410/PLAN.md.

Corrected the budget interpretation: project balance is 48,463.075 SU, not 847.075 SU. The latter was the old internal campaign remainder. The user authorised continuation after this clarification. The revised 51,000 SU planning bound retains a 13,000 SU buffer; neither amount is an organiser quota. The batch reserves at most 4,608 SU.

H200 job 24282 failed before measuring because TP8/EP1 produces a 192-element MoE weight partition incompatible with FP8 block 128. TP8/EP2 gives 384; corrected job 24321 tests that layout. H200 job 24291 passed protocol/runtime/SLA/short/12-long review at 2,715.842 good tokens/s, +1.8136% versus 24263. An independent repeat is armed. Its first reviewer rejection was an overly narrow runtime delta allowlist; the revised review explicitly checks both main and speculative runner values and that speculative decoding remains disabled. Preserve both review files.

Autopilot remains disabled. GPU submissions do not authorise background Codex scheduling. No submission slides or BTC upload changed.

## 2026-10-17 — self-contained metric report and explicit units

The user corrected that the Markdown report must explain the metrics at least as fully as chat, and explicitly state every unit. Expanded reports/all-history-metric-records-20261017/REPORT.md with TTFT (ms), mean ITL (ms per token interval), goodput (requests/s and the reported conversion to good output tokens/s), joint SLA pass rate (%), concurrency N (requests), thresholds, worked examples, average-versus-per-request distinctions, quality versus latency, configuration labels, raw sources and historical evidence limits. Added REPORT.template.md and updated build.py so regeneration preserves explanations and units. Existing raw artifacts remain unchanged. This is an ongoing documentation requirement: reports must stand alone without reading chat.

## 2026-10-17 17:54 UTC — transport repair and prefill graph trials

Job 24321 failed before benchmark: both TP8/EP2 workers became ready (all workers ready at 280s), then one P/D warmup request hit the 480s HTTP timeout. Summary is empty. Corrected the preparation mistake: this equal-TP8 layout reused the heterogeneous-TP patch, leaving equal-TP whole-pool descriptor setup active. Its sole role in the stall is not directly profiled; cancellation aborts are secondary. Reused the exact equal-TP patch previously validated on GPU in 22809, rechecked 936 byte-range cases and five fallback guards in an isolated copy, and submitted corrected H200 job 24375. Require all-rank equal-TP activation and full scoring/output checks; do not retry unchanged 24321 or extend timeouts blindly.

Engine startup logs show prefill CUDA graph setup taking 106.51–161.62 seconds. Exact staged source provides --disable-prefill-cuda-graph without disabling decode graphs. Submitted one-factor graph ablations: H200 24376 at N56 versus 24320; H100 221181 at N50 versus 221151. Both retain auto prefill MoE and existing decode kernels. Faster startup may cost throughput; evaluate the two separately, account for loading/cache/node confounds, and do not select a slower ranked configuration just for cheaper startup. Full plan and source-bound validation: qwen-experiments/research-followup-20261017-1755/PLAN.md.

Fresh H100 balance remains 46,924.800 SU (used 17,075.200; In Doubt 0), ledger as of 18 October 01:40:02 SGT. Three queued jobs 221153 → 221177 → 221181 have verified afterany dependencies and reserve at most 4,608 SU total. Internal operating headroom after reservations: 29,316.800 SU. H200 queue contains 24322, 24327, 24352, 24375, 24376, all pending at the recorded snapshot. No new benchmark winner is claimed. Autopilot remains OFF; no slides or official package scripts changed.

## 2026-10-17 23:43 UTC — gain confirmed, platform difference, invalid topology closed

Reviewed H200 24327: 2,716.787 good tokens/s, +1.7401% versus fresh 24320, full protocol/runtime/short/long pass. Together with 24291, N56 DeepGEMM averages 2,716.315. N58 24352 passes at 2,718.080 but adds only 0.048% versus N56 repeat with higher TTFT; no automatic higher load. H200 prefetch 24322 passes at 2,665.572 (−0.178%), with no demonstrated startup benefit.

Equal-TP repair 24375 successfully warmed its P/D path and reached measurement, then FAILED acceptance: SLA 1.9978%, goodput 28.329, short 0/8 with seven new failed cases, long 11/12. Quarantine the candidate and retain all outputs. Updated nixl-equal-ondemand/VALIDATION_STATUS.md: CPU range tests and old GPU execution do not establish complete model correctness; exact root cause is not isolated. No unchanged retry.

Reviewed H100 prefetch 221153: 2,241.336 (+0.444%), walltime 15:45, full checks pass. Observed prefill weight loading ~306s versus ~921s control; cache/node/order remain confounded. Reviewed DeepGEMM repair 221177: 2,232.720 (+0.0579%), walltime 25:28, full checks pass. Its H200 gain does not establish an H100 improvement.

Submitted H200 24425 (DeepGEMM/chunk8192, graph-on retained) and 24426 (DeepGEMM/graph-off, decode unchanged). The old graph-review precedence was an unnecessary self-imposed dependency; the two tests keep changes separate and DeepGEMM is now independently confirmed. Submitted reverse-order H100 pair 221194 prefetch → 221195 control after graph trial 221181, identical readiness bounds, max 3072 SU new reserve. Dependencies verified; uncertainty rules and active-job caps retained.

Ledger as of 18 October 07:20:01 SGT: Used 17,612.800, Balance 44,851.200, In Doubt 1536 SU. 221153 is reconciled. Completed 221177 remains conservatively reserved until its terminal charge reaches Used. Total outstanding reserves including ledger lag and new pair: 6144 SU; internal-limit headroom 27,243.200 SU. Balance already excludes prepayment; no double deduction. Updated current metric records and cross-platform report while retaining frozen calibration. Full results, receipts, validators and decisions: research-followup-20261017-2335/RESULTS.md. No new AI scheduling, slides or official package scripts changed.

## 2026-10-19 — active sources and archive workflow clarification

The two existing directories, `/home/apacsc42/2026-APAC-HPC-AI` and `/home/apacsc42/workspace`, remain the active sources. `/home/apacsc42/apac-hpc-ai-research` is a separate local snapshot repository, not an automatic mirror. No incremental synchronizer or scheduled backup is installed. Work should be edited once in its active source directory, then explicitly captured into the archive and committed at a completed milestone. Large retained evidence belongs in the sibling artifact store with its indexes and hashes; a Git commit alone does not preserve those external objects. Do not manually maintain three independent versions or claim later source edits are already archived. This explanatory note is a source update after the completed snapshot and has not itself been imported into that snapshot. GitHub installation and upload remain deferred.

## 2026-10-19 — archive workflow persisted in AGENTS.md

At the user's explicit request, `/home/apacsc42/AGENTS.md` now records the two active source directories and the separate Git archive. Future completed milestones should explicitly capture relevant safe changes and evidence, verify the capture and commit it while keeping external artifact indexes and recovery metadata consistent. No automatic synchronization, background Codex, GitHub setup or upload was enabled. The existing archive and its history were not modified in this documentation turn; these new source instructions and notes await the next explicit capture.

## 19 October 2026 — requested status and VPN login

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


## Illustrated journey — 2026-10-19T06:39:43.899360+00:00

The user requested an overall diagram of the research and improvement journey and explicitly emphasised that it must illustrate the process. Created a source-linked English visual with GPU groups, phase-specific kernels, chunk budgets, the measured H200 trajectory, rejected branches, a separate H100 lane and the research validation loop. Preserve SVG/PNG/PDF and the reproducible vector builder under workspace/reports/research-journey-20261019/diagram/. The plot uses selected observations rather than elapsed time or causal ablations. Highest H200 interaction remains a single local observation; own repeat and official accuracy remain unverified at the 06:14 UTC report cutoff. No new job, credit, VPN, slide or schedule action. Commit this completed reporting milestone with the `report` category and the existing explicit capture/verify/push workflow.

## Status review — 2026-10-19T11:15:15.315162+00:00

Live checks at 11:11 UTC: H200 24733/24736/24737/24738 remain pending for Priority; two hpcai nodes allocated. Highest H200 observation remains 2938.628 good tokens/s; its own interaction repeat has not run. All three PBS jobs completed and pass full local protocol/SLA/runtime/output checks: N54 repeat 221645 = 2418.588; N56 221646 = 2407.364; forced prefill Tree 221669 = 2160.946 good tokens/s. Tree execution is proved on all eight prefill ranks in 16 sealed diagnostic traces (355/355 successful requests); it loses 10.65% versus fresh N54 and is closed. N56 has no observed gain; no automatic N58. Highest H100 individual observation remains 2430.891. Official accuracy unverified. PBS queue empty; VPN/SSH usable without restart or authentication. Balance 34608.356 SU; three terminal charges reconcile, zero remaining reservations and internal headroom 21608.356 SU under the unchanged cap/buffer. No new GPU job, schedule, slide or submission change. [Full report and raw evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/status-review-20261019-1111/RESULTS.md). This supersedes earlier queue and credit snapshots below.


## Continue research and submitted batch — 2026-10-19T12:02:20.997548+00:00

The user explicitly corrected idle research: during active authorised work, review results, research the next distinct hypothesis and submit when capacity/budget permit without another reminder. Losing N56 or Tree is not a global stop. Actual new jobs: PBS **221827 → 221828 → 221829** (N54 fresh control/profile, HPC-Ops chunk6144, prefill Simple protocol/profile); H200 **24819** (N58 winning interaction repeat/profile), preserving four older queued jobs. Five active H200 jobs and three serial PBS jobs. New PBS maximum reserve 4608 SU; pre-submit Balance 34608.356, Used 29391.644, In Doubt zero; internal headroom 17000.356 SU under unchanged cap/buffer. New jobs have no measurements yet. Full plan, references, hashes and receipts: [research continuation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261019-1200/RESULTS.md). Review each completion and continue justified work. No blind duplicates, unchanged loss retries, automatic load growth, AI schedules or background Codex. Highest observations/accuracy limits unchanged.

