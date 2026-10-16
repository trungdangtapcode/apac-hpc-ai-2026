# Bàn giao hiện hành — 16/10/2026 10:29 UTC

Kiểm scheduler **10:25:28 UTC**: **23934 COMPLETED exit0**, kết thúc 08:11:21,
wall 9m17s. **23973/23974/23975/24009 PENDING(Resources), 4/5 slot**;
watcher 419440 sống. Lượt này không gửi job, sửa payload/watcher hay xác thực mới.

Final audit 23934 đạt: 47 file đã seal, full60/120/30, raw802warmup/1598profiling,
12 file thực thi giống cả hai DP control, 8 rank NIXL và hai P/D warmup.
Không lỗi/hủy request. Tái chấm 132 baseline + 8 candidate: 7/8, chỉ reverse đã biết.
**2555,4232 good tokens/s; SLA98,7484%; TTFT751,9882ms; ITL16,8873ms.**
So DP N52 mean: +0,4633%, TTFT+145,1971ms, ITL−0,0717ms.
So MNNVL23924 cùng N54: −2,9844%, TTFT+151,5435ms, ITL−0,2229ms.
Một điểm/package chưa chứng minh lặp lại, thống kê hay accuracyBTC. Kết thúc
nhánh DP có giới hạn tại N54; không thêm DP repeat/N56. Ưu tiên bốn job đang chờ.
[Phân tích](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/DP_N54_RESULT.md).

**NSCC10:25UTC: helper không thấy phiên VPN sống trước SSH.** Không loginVPN/DUO
mới. **Trạng thái 220720/220721/220722 và credit hiện UNKNOWN**; không suy đã
terminal/cancel vì quá walltime. Giữ **4608SU** dự trù, headroom bảo thủ9394,631SU,
cap16384SU, projectreserve13000SU. Ledger06:17 là lịch sử. BudgetJSON và plan đã
đánh dấu state không fresh; không gửi duplicate hoặc giải phóng reserve trước đối soát.

Đã phục hồi archive220720 của lần thu06:26: tar exit1 vì thư mục n38/confirm đang
thay đổi; đọc đủ102member. Raw/protocol60/120/30/phases/count/latency/length của
N32/34/36 khớp, không lỗi/hủy: **1692,1662/1754,0728/1787,7370goodt/s, SLA100%**.
Đây là **snapshot lịch sử06:26**, chưa terminal seal hay final quality/runtime.
N34 protocol nay đã kiểm. N36+31,8048% so control có SLA82,12% là goodput gain,
không phải raw throughput tăng31,8%. Rolelogs vẫn rỗng; chưa đủ census8rank MNNVL
hoặc BF16KV hiệu dụng. Giữ archive/stderr gốc; không dùng N38 chưa hoàn tất.

Tiếp: H200 dùng review-wave10.py/review-mnnvl-n54-repeat.py sau seal, giữ gate
comboN54 về gain lặp, freshcontrol, SLA95%, ITL19,3ms, không lỗi/newshort,
longPASSED. Không third successful MNNVLrepeat/N56/promotion. Slot thứ5 để trống
khi chưa đủ giả thuyết/gate. H100 thu ba terminal khi existingaccess trở lại;
plan freshcontrol+candidate pair06:28 vẫn có điều kiện, chưa reserve/submit.
POLICY, DECISIONS, tutorial và plan đã đồng bộ. Phần độc lập đã xong; không đợi queue.
Evidence: `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-1025UTC/`.

---

# Các bàn giao trước 10:29 UTC là lịch sử

Quyền tự chủ06:21 vàgiới hạnngânsách vẫn hiệu lực;trạngtháiVPN/PBS/Slurm cũ
không phải live. Mọi mô tả23934pending ởdưới đãđượcfinalaudittrên thaythế.

# Trạng thái bàn giao và các đính chính

Cập nhật kiến thức trước lượt này: **16/10/2026 06:18 UTC**.
Bàn giao đầu file là trạng thái hiện hành theo lần kiểm ghi rõ. Các bàn giao và
đoạn mô tả cũ bên dưới là lịch sử; phải kiểm scheduler lại khi làm tiếp.

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

## Cập nhật live16/10/2026 06:19UTC

220720MNNVLH100 vẫnRUNNING16GPU, đã có **fullN32** export60/120/30:
1692.17goodt/s,SLA100%,0errors/cancel,ITL17.25ms.
So220575cùngN32=1570.21: **+7.77%**. Đây làđiểmđo trongjobđangchạy,
chưa cófinalcandidate/longdiagnostic/accuracyBTC. N34vừa cóexport1754.07goodt/s,SLA100.00%,soN34baseline1625.59tăng7.90%;chưađốisoátfullN34protocol tại lần này;
220721/220722vẫnHdependency. H2005/5PENDINGPriority. VPN/SSHhoạtđộng.
Evidence: nscc-pbs/inspection/live-220720-20261016-0619UTC/snapshot.json.

## Bàn giao hiện hành 16/10/2026 06:18 UTC

PBS kiểm **06:17:25 UTC**: **220720 R**, wall **00:24:39**;
**220721/220722 H** đúng chuỗi afterany. H200 kiểm **06:15:28 UTC**:
23934/23973/23974/23975/24009 đều **PENDING(Priority)**, đủ 5 slot;
sacct chưa Start/End/allocation, watcher419440 sống. VPN/SSH sẵn dùng.
Không gửi job mới, sửa payload queued, auth/DUO hoặc watcher.

Đã thu runtime chỉ đọc **06:16 UTC** từ cả 3 server220720: prefill TP4/EP1 ×2,
decode TP8/EP8, NIXL, FA3; decode báo allreducefusion **mnnvl**, graph1–64.
Hai pairrouter có chat HTTP200 lúc06:12:30; 8 connectionwarmup HTTP200.
N32 đã tạo raw JSONL nhưng tại snapshot06:15 chưa có export cuối; chưa báo gain.
Rolelogs vẫn0byte, stdout chưa hiện; reportedconfig không chứng minh đủ8rank
khởi tạoMNNVL. Mỗi endpoint trả1internalstate, không phải census rank.
`kv_cache_dtype=auto` cũng chưa chứng minh dtype hiệu dụng.

Reported startup: prefill loadweight **842,03/842,82s**, graph **118,92/114,59s**;
decode loadweight **89,74s**, graph **124,69s**. Không quy kết chênh lệch choI/O
hoặc backend. [Collector runtime](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collect-live-runtime.py)
đã chạy thật chỉ đọc,3serverHTTP200,seal và6kiểm đạt; không phải benchmark,
accuracy hay runtime từngrank. Dùng một lần lúc05/06 đangR để giữtimings,
sau terminal vẫn collect-run→review-candidate-sweep với220575 cùngN.

myprojects truy vấn06:17: ledger **14:00:02 Singapore**, used2381,369SU,
balance**60082,631SU**, InDoubt**1536SU** đã trừkhỏibalance. Giữ toàn bộ
**4608SU** campaignreserve cho3pilot; headroom**9394,631SU**, cap16384SU,
projectreserve13000SU; chưa reconcile terminalcharge, không trừprepaid hai lần.
GiữgateH200comboN54,khôngN56/thirdsuccessfulrepeat/promotion.
Bước tiếp đã chuẩn bị: capture runtime05/06 khiR;thu terminal04→05→06,
so từngcandidate vớibaseline,không tựloại05/06 nếu04fail. Kết thúc không chờjob.
[Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0615UTC/).

## Bàn giao lịch sử 16/10/2026 06:01 UTC

PBS kiểm **05:58:02UTC**: **220720 R**,wall00:05:11;**220721/220722 H**
đúngafteranychain. Logrole04 kiểm05:56 còn0byte,chưa cóbenchmark/runtimebackend
mới;không coi pending haypayload là bằng chứng khởi tạoMNNVL.
H200 kiểm **05:55:37UTC**:23934/23973/23974/23975/24009 đềuPENDING(Resources),
đủ5slot,sacct chưaallocation/start/end;watcher419440 sống. VPN/SSH sẵn dùng,
khôngrestart/auth/DUO mới. Không thayqueuedpayload,watcher hay gửijob.

Đã chuẩn bị [reviewcandidateH100](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/CANDIDATE_SWEEP_REVIEW.md):
rehashseal vàpayloadfrozen,so từng04/05/06 độc lập với220575 cùngN32/34/36,
N38+ không cócontrol. Runtime luôn cầnreviewtay;longPASSED/FAILED/DEFERRED/
MISSING được tách rõ;khôngpromotion/accuracyclaim.11kiểmthànhphần và5fixtureCPU
đạt,không phải đo model;giữ2lỗisetupfixture đã sửa(EXDEV,quyền thưmục copy).
Collector cũ chỉglobstdout ởroot,trong khiOutput_Path khai báo trongbundle;
đã bổ sungparsercảđườngxuốngdòng. **Chưa thuđượcstdout mới**, baseline cũng chưa
thấyfile tạiđườngkhai báo;khôngcoilà đãkhôi phục runtime hoặc nguyênnhân duy nhất.

myprojects hỏi05:55 vẫnledgerasof13:40Singapore:used2381,369SU,
balance61618,631SU,InDoubt0;charge220720 chưa reconcile,giữ4608SUreserve.
Campaign16384SU,headroom9394,631SU,projectreserve13000SU,3pending/running nhưng
chỉ1running16GPU nhờafterany. Đãsửatrườngheadroom vàrule1queued cũ,đồngbộPOLICY
hiện hành;policycũarchiveđể khônglẫn lỗiauth05:40 vớitruycập05:43 trởđi.
Tiếp:collectterminal04→05→06 vàđọcseal/protocol/output/runtime;04failkhôngtựloại
05/06. GateH200comboN54,khôngN56/repeatthứ3/promotion giữnguyên. Phầnđộclập đãxong,
kếtthúckhôngđợiqueue. [Evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0555UTC/).

## Bàn giao lịch sử16/10/2026 05:53UTC — chuỗi3jobNSCC đã gửi

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

## Bàn giao lịch sử16/10/2026 05:43UTC — VPN/SSH đã khôi phục

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

## Bàn giao lịch sử 16/10/2026 05:42 UTC

Scheduler kiểm **05:40:37 UTC**: **23934/23973/23974/23975/24009 đều
PENDING(Priority), 5/5 slot**; sacct chưa có Start/End/allocation. Watcher419440
sống. Chưa có số đo GPU mới; snapshot05:36 Resources là lịch sử. Không thêmjob,
sửa queued payload hay watcher. Reviewers/suite CPU đã chuẩn bị; không cần chạy
lại audit hoặc mocktest bất biến khi chưa có seal.

**NSCC đã đổi tầng lỗi:** ssh-batch lúc05:40:37 đi qua namespace hiện có và
nhận `Permission denied (password)` từ SSH, khác lỗi thiếu VPN lúc05:30.
Kiểm chỉ đọc05:40:56 xác nhận interface snx-tun UP và route tới10.103.71.15
qua tunnel. Đây là bằng chứng mạng VPN hiện có, chưa phải SSH/PBS/credit thành
công, không xác minh ai tạo phiên/thời điểm bắt đầu/lifetime24h. Không đọc
credential/session blob, không connect/login VPN mới, không cấp password/DUO,
không lặp SSH hoặc qsub. Không kết luận password sai từ BatchMode không có
master xác thực dùng được. Các câu thiếuVPN dưới đây là snapshot lịch sử.
220575/result/credit vẫn chưa xác minh; giữ **1536SU** reserve và cap16384SU.

Đã chuẩn bị [phiếu bước tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0540UTC/NEXT_STEP.md):
thu seal qua watcher rồi review23934/wave10/24009; khi SSH xác thực sẵn dùng
được thì thu220575 và reconcile ownqueue/credit trước04→05→06. Giữ mọiattempt,
gatecomboN54 vàkhôngN56/thirdrepeat/promotion. Bộ14ca EAGLE3 vẫn chỉinputCPU,
chưamodel/GPU/accuracy. Đã đồng bộ metadata continuous-plan với suite hiện có.
Không còn việc độc lập cần làm trong lượt; kết thúc không chờqueue.
Bằng chứng: `nscc-pbs/inspection/wake-20261016-0540UTC/`.

## Bàn giao lịch sử 16/10/2026 05:38 UTC

Scheduler kiểm **05:36:58 UTC**: **23934/23973/23974/23975/24009 đều
PENDING(Resources), đủ 5/5 slot**. Watcher 419440 sống lúc 05:30:29 UTC.
Chưa có số đo GPU mới. Kết quả 23924 và các gate wave10/N54 ở bàn giao 05:25
vẫn áp dụng; các câu chưa có seal 23924/chưa xác minh N54 bên dưới là lịch sử.
Không thêm job, sửa payload đang queue hoặc khởi watcher mới.

Đã chuẩn bị [bộ đầu vào EAGLE3 14 ca](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/token-suite-v1/suite.json)
bằng tokenizer của đúng target revision đã pin; 6 file nhỏ khớp cache commit/ETag.
Lưu hash chat template, messages, rendered prompts và IDs. Có cap 1/3/4/5/200
trên cùng prompt, EOS probe, Việt/Trung/code/multiturn, retrieval 3 vị trí với
3.788 token và một ca 7.885 token, đều gồm chat template; input+cap tối đa
8.085/8.192. Preflight bộ thu và seal đạt; dựng lại 5 file giống từng byte.
Đây chỉ là đầu vào CPU, chưa có capture/output model, EOS thật, compatibility,
acceptance hay accuracy. Không tải draft, upload hoặc chạy GPU.

Transformers 5.14.1 trả BatchEncoding mặc định; đã đặt `return_dict=False`, giữ
prototype false-reject. Một attempt CPU chậm đã dừng, giữ source/log rồi giảm
kiểm vocab/encode lặp. Dùng thư viện trích từ aiperf với CPU, chưa xác minh
container runtime GPU; các probe container thất bại cũng được giữ.
[Hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/TOKEN_REVIEW.md).

NSCC helper kiểm **05:30:29 UTC** thiếu VPN trước SSH; 220575/result/credit
vẫn chưa xác minh. Không auth/DUO/qsub; giữ dự trù **1.536 SU**, campaign
16.384 SU và thứ tự 04→05→06. Tiếp: thu seal qua watcher rồi dùng
review-n54.py, review-wave10.py và review-mnnvl-n54-repeat.py. Khi nhánh EAGLE3
được phép chạy, so control tự lặp trước candidate. Phần chuẩn bị độc lập đã xong;
kết thúc không chờ queue. Bằng chứng: `nscc-pbs/inspection/wake-20261016-0530UTC/`.

## Bàn giao lịch sử 16/10/2026 05:25 UTC

**23924 MNNVL N54 COMPLETED exit0 lúc04:31:37UTC.** Finalaudit seal47file,
raw818warmup/1640profiling,full60/120/30,12file thực thi vàruntime so cả23778/
23839đạt;8rankMNNVL/NIXL,2P/Dwarmup,short7/8chỉreverseđãbiết,0lỗi/hủyrequest.
Đạt **2634,0344goodtokens/s,SLA98,9024%,TTFT600,4446ms,ITL17,1102ms**.
Hơn từngN52control1,6153%/1,5855%,hơnmean **1,6004%**,TTFT+88,1784ms,
ITL−0,0307ms. Đây là1lượtN54,chưa lặp xác nhận;không so comboN52 để gán
hiệu ứng kernel. AccuracyBTC vẫn chưa xác minh. Các câu chưaN54 bên dưới
là snapshot lịch sử,được thay bởi finalaudit này.

Trong phạm vi research liên tục,đã mở thêm1điểm xác nhận MNNVL N54 theo
[plan có giới hạn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/PLAN.md):
watcher419440 gửi **24009**,12file thực thi giống23924;storedscript khớp frozen.
Không sửa queuedpayload/khởi watcher mới;metadatawave7/matched52 kế thừa,
launcher thực54. Kế thừa budget-deferred replacement của watcher tối đa3attempt
khi chưa đo đủ,giữ mọiattempt;không thêm điểm xác nhận thành công thứ3/N56.

Scheduler kiểm **05:24:11UTC**: **23934/23973/23974/23975/24009 đều
PENDING(Resources),5/5slot**;watcher419440 sống. Wave10combo chưa có số đo mới,
gainFlashInfer1,4867% vẫn chưa lặp. ComboN54 giữ gate repeat+freshcontrol+long
riêng;MNNVLrepeat không bỏ gate đó. Tiếp:review-n54.py23934,review-wave10.py
vàreview-mnnvl-n54-repeat.py cho24009,so23924 và3N52control;toolrepeat chưa
chạy terminalpath mới,nếu replacement thì đòi review tay,không tự chọn peak.

NSCC helper kiểm **05:20:46UTC** thiếuVPN trướcSSH;220575/result/credit vẫn
chưa xác minh. Khôngauth/DUO/qsub;giữ1536SUreserve,campaign16384SU và04→05→06.
Bằng chứng:`nscc-pbs/inspection/wake-20261016-0520UTC/`.
Phần độc lập lượt này xong;kết thúc không chờ queue.

## Bàn giao lịch sử 16/10/2026 02:46 UTC

Scheduler kiểm **02:45:04 UTC**: 23924/23934/23973/23974/23975 đều
**PENDING(Resources)**, đủ5/5 slot; watcher419440 sống. Chưa có export/runtime
N54 hoặc wave10 và chưa có số đo GPU mới trong lượt này. Snapshot2/5slot cùng
các câu không thêmjob/repeat ở wave9 bên dưới là lịch sử, đã thay bởi POLICY
và wave10plan lúc02:36; không suy thành cấm tiếp tục research.

Đã chuẩn bị [review-wave10.py](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/review-wave10.py)
và [hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/MATCHED_REVIEW.md).
Tool đọc seal/raw/protocol/runtime, so từng combo với cả3control và mean,
đo drift control mới; tách long PASSED/FAILED/DEFERRED/INCOMPLETE/MISSING.
14kiểm source/export/gate và8ca long tổng hợpCPU đạt; không phải chạy model.
Stored Slurm script23973–23975 khớp frozen; chưa chứng minh runtime. Không sửa
payloadqueued, watcher, submission hay gửi thêmjob. Tool chưa có seal để đọc.

Quy tắc review mô tả thận trọng: cả hai repeat phải hơn control mới, meancombo
hơn meancontrol và fullSLA90% trước cờ gain reproduced; không khẳng định ý nghĩa
thống kê. Gate viết plancomboN54 thêm mỗi comboSLA95%,ITL<=19,3ms và longpass,
0error/cancel/no newshort; cờ không tựsubmit. Giữ gate N54wave7/8 và khôngN56.

NSCC kiểm **02:41:22 UTC**: helper thiếuVPN trướcSSH;220575/result/credit vẫn
chưa xác minh. Khôngauth/DUO/qsub;giữ1536SUreserve,campaign16384SU và04→05→06.
Tiếp:watcher thu5job;dùngreview-n54.py cho23924/23934 vàreview-wave10.py cho
23973–23975. Phần chuẩn bị độc lập lượt này xong;kết thúc không chờ queue.
Bằng chứng:`nscc-pbs/inspection/wake-20261016-0240UTC/`.

## Bàn giao lịch sử 16/10/2026 02:19:28 UTC

Scheduler kiểm lúc 02:18:09 UTC: **23924/23934 PENDING(Resources)**, 2/5 slot;
watcher3514431 sống. Snapshot02:09PENDING(Priority) là lịch sử. Chưa có runtime/
export N54 hay số đo GPU mới; cả ba wave9 đã finalaudit, kết quả giữ nguyên.

Đã chuẩn bị local `nscc-pbs/research-next/eagle3-01/capture-native-tokens.py`:
thu tuần tự native /generate vào thư mục mới, kiểm suite/hash tokenizer trước
khi gửi, giữ request/response bytes và hash/journal, dừng khi lỗi, không retry.
**35 ca HTTP giả lập/CPU đạt**, gồm EOS, token khác, count/IDs/finish sai,
redirect, body thiếu và bảo toàn evidence; không phải thử SGLang/Qwen/GPU.
Chưa có suite/capture model thực; tool không chứng thực target/runtime/accuracy.
Giữ attempt34ca lịch sử; final thêm chặn Content-Length thiếu dù JSON hợp lệ.
Hướng dẫn ở TOKEN_REVIEW.md; chưa tải draft/upload/đổi frozen payload.

NSCC kiểm lúc 02:15:33 UTC: helper thiếu VPN trước SSH;220575/result/credit vẫn
chưa xác minh. Giữ1536SU dự trù,campaign16384SU,ưu tiên04→05→06 và các gate.
Không xác thực mới/qsub,thêm job/repeat/N56/controller/schedule. Tiếp:watcher
thu haiN54 rồi chạy review-n54.py so cả hai baseline/mean. Phần chuẩn bị độc lập
đã xong,kết thúc không chờ queue. Bằng chứng:`nscc-pbs/inspection/wake-20261016-0215UTC/`.

## Điều cần nhớ trước tiên

- Người dùng thi **Qwen**, không phải OpenFOAM. Tiếp tục research và submit job
  hữu ích, không đợi người dùng nhắc từng lần; giữ dữ liệu của cả lần lỗi.
- Hai cụm riêng: H200 ban đầu dùng Slurm; NSCC H100 dùng PBS qua CheckPointVPN.
  “Firmus” là cách trợ lý gọi cụm ban đầu, không phải scheduler hay tên lệnh.
- Thử nghiệm chưa đồng nghĩa nộp bài BTC. Chưa xác minh đầy đủ accuracy99%reference.

## VPN: diễn biến lịch sử; trạng thái mới nhất xem bàn giao đầu file

**Tìm lại phiên cũ16/10 theo yêu cầu người dùng:** đã kiểm tra đường lưu chuẩn
`/var/cache/snx-rs/ike-sessions.db`, cache/config/data người dùng, thư mụcnamespace,
socketSSH, tiến trình còn sống vàfd liên quan. Không tìm thấy sessionblob/DB hay
process cũ giữ phiên. Sourcev6.5.1 chỉsave khi`ike_persist=true`; launcher ban
đầu đã dùng`false`. Không có dữ liệu local để resume phiên cũ theo cơ chế của
client; trạng thái phiên server chưa kiểm chứng. Không đọc/trích phiênWindows.
**Không thử login mới; người dùng đang yêu cầu tìm phiên cũ và đã phản đối thử
xác thực khi người giữDUO không có mặt.** Chỉ tìm local, không gửiDUOpush.
[Bằng chứng](/home/apacsc42/workspace/vpn-rootless/inspection/session-recovery-search-20261016.json).


**Cập nhật mới16/10/2026 00:18:46UTC:** theo yêu cầu người dùng, thử lại cùng
credential với helper đã đặtIKE86400s. Gateway trả`Authentication failed,status0`
sau khoảng64giây; không tạoVPNtunnel, chưa tớiSSH. Không suy ra mật khẩu sai hay
nguyên nhânDUO từ mã0. Câu hỏiDUO của lần07:17giờVN đã gửi, chưa có trả lời.
Không thử lại liên tục. [Bằng chứng](/home/apacsc42/workspace/vpn-rootless/inspection/login-attempt-20261016-0017UTC.json).


1. Client cài trên VPS là **snx-rs6.5.1**, dự án cộng đồng, **không phải client
   CheckPoint chính thức**. Người dùng báo client Windows của họ vẫn kết nối tốt,
   phiên24giờ; đây là thông tin người dùng cung cấp, không được phủ nhận bằng logLinux.
2. PhiênLinux đầu kết nối được khoảng12:17UTC, đã SSH/chạy PBS/download thành công.
   Log cuối chính xác20:17:01UTC: `IKE SA expired, disconnecting tunnel`, sau đó
   `Tunnel disconnected`, exit0. Không phải bằng chứng server/VPNWindows hết phiên.
3. Đã đọc đúng sourcev6.5.1, revision
   `86aa48031888050f957af7b6adf2c2e39d4745fd`: mặc định
   **ike-lifetime28800giây=8giờ**, helper cũ không override. Client đề xuất giá trị
   này khi tạo SA, dùng lifetime đã đàm phán để tự ngắt khi hết hạn. Đây là điểm
   cấu hình bỏ sót phù hợp thời điểm ngắt; không phải kết luận server chỉ cho8giờ.
4. Helper hiện đã sửa **`--ike-lifetime86400` (24giờ)** cho kết nối IPsec mới.
   Đã thử login với86400s ngày16/10 nhưng xác thực thất bại; **tại mốc00:18 chưa có phiên mới thành công với
   cấu hình này. Mốc05:40 đã quan sát tunnel hiện có nhưng chưa xác minh nguồn
   khởi tạo/cấu hình/lifetime; chưa chứng minh giữ được24giờ**.
5. Đã thử login lại hai lần được ghi nhận,20:40 và20:47UTC: gateway trả
   `IPsec authentication failed,status0` / `Authentication failed`. Đây là
   **lỗi xác thực VPN**, xảy ra trước SSH. Chưa xác định do mật khẩu, DUO, chính
   sách hay nguyên nhân khác. Không tự kết luận mật khẩu sai hoặc hết phiên.
   Lần20:47 bắt đầu trước khi helper được sửa; không tính là phép thử24giờ.
6. Câu hỏi DUO đã gửi người dùng: điện thoại đội trưởng có yêu cầu khớp lần login
   hay không. Chưa có câu trả lời tại mốc ghi này. Không tự phê duyệt DUO.
7. **ControlPersist86400 là SSH**, không phải VPN lifetime.
   **ike-persist là lưu/khôi phục SA lên đĩa**, không đồng nghĩa tự rekey.
8. VPN mất không tự hủy job PBS đã nhận. Chưa kết nối được thì chưa biết trạng
   thái/kết quả cuối của job; không gửi job thay thế trùng lặp.

Nguồn: [chẩn đoán và revision](/home/apacsc42/workspace/vpn-rootless/inspection/ike-lifetime-diagnosis.json),
[log phiên cũ](/home/apacsc42/workspace/vpn-rootless/inspection/vpn-disconnect-20261015.json),
[tài liệu đúng phiên bản](https://github.com/ancwrd1/snx-rs/blob/v6.5.1/docs/options.md).

## Research: các dữ kiện đã xác nhận

**Cập nhật02:36UTC:** đã mởwave10 vàgửi23973/23974/23975, cùng23924/23934đềuPENDING(Resources),đủ5/5slot. WatcherđãkhởiđộnglạivớiPID419440. Hai comboN52repeatvàfreshMNNVLcontrol kiểmchứnggain1,4867%;23975cólongcheckriêngsauđo. Các câu“không thêmrepeat/job”ởbàn giao wave9là quyếtđịnhđóngwavecũ, được thay bằng[wave10plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/PLAN.md) trong phạmvi user yêu cầu liên tục research. KhôngmởN56,bảo toàn gateN54cũ,khôngVPNauth/DUO.

| Môi trường | Job | Kết quả |
|---|---|---|
| H200, RR,N53 | 23616 /23773 | 2433,41 /2438,47 goodtokens/s; đã lặp độc lập |
| H200,MNNVL,N52 | 23778 /23839 | **2592,16 /2592,92**, SLA99,01%, không lỗi/hủy; đã lặp độc lập |
| H200,DP-attention+DeepEP,N52 | 23780 /23859 | **2549,20 /2538,08**, SLA98,87%, không lỗi/hủy; đã lặp độc lập |
| H200,MNNVL+FlashInfer,N52 | 23904 | **2631,09**, SLA99,02%, ITL16,23ms; một lượt |
| H200,MNNVL+chunk2048,N52 | 23905 | **2331,35**, SLA98,77%, ITL15,81ms; một lượt |
| H200,MNNVL+chunk8192,N52 | 23906 | **2547,85**, SLA98,87%, ITL16,32ms; một lượt |
| NSCC16H100,N32 | 220562.pbs111 | **1565,16**, SLA100%, ITL18,57ms, không lỗi/hủy; một lượt |

H200 MNNVL N52 đã lặp độc lập: trung bình **2592,54 goodtokens/s**, chênh0,029%;
tăng8,02% so controlN52 23607 và6,32% so N53 23773. ITL giảm2,38ms nhưng
TTFT tăng165,43ms so23607. Chưa chứng minh SOTA toàn cuộc thi.
Không xếp hạng H100/H200 như cùng phần cứng. Tất cả chưa có chứng nhận accuracyBTC.

H200 **23839 COMPLETED** exit0 lúc20:59:45UTC; export và artifact checksum
đã kiểm tra ở lượt21:01. Cả8decode rank khởi tạoMNNVL; payload giữ nguyên,
chỉ đổi tên/mục đích. Diagnostic7/8, chỉ reverse đã biết. Gate hiện có mởN54
**23924** (MNNVL) và **23934** (DP; watcher gửi22:12:24UTC sau repeat đạt).
Snapshot lịch sử **16/10 00:58:48UTC**: **23906/23924/23934 PENDING(Resources)**,
3/5slot; watcher3514431 còn sống. **23904 COMPLETED exit0 lúc15/10 23:01:10UTC;
23905 COMPLETED exit0 lúc16/10 00:05:14UTC**, finalaudit đạt. Snapshot23904RUNNING
22:57 vàcả5PENDING22:17 là lịch sử.23859 **COMPLETED exit0 lúc22:11:34UTC**.
Các snapshot23859RUNNING22:06 vàallPENDING21:50 là lịch sử.
[Review MNNVL](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/MNNVL_REPEAT_REVIEW.md).
DP mean2lượt **2543,64**, repeat−0,436%; hơncontrol23607 **5,98%**, thấp hơn
MNNVLmean **1,89%**. MeanTTFT606,79ms tăng259,95ms so23607; meanITL16,959ms
giảm2,566ms. Không quy kết hiệu ứng riêng cho một kernel.

NSCC220575 và mô tả mấtVPN của mục cũ là lịch sử trước05:43UTC16/10.
220575 đã terminal/thu đủ;chuỗi220720→220721→220722 đã gửi05:52UTC.
Xem bàn giao đầu file và POLICY cho trạng thái/credit hiện hành.

## Credit và bước tiếp

Credit và bước tiếp hiện hành xem bàn giao đầu file, POLICY và budgetJSON;
không dùng ledger04:00Singapore hoặc câu220575unknown/missingVPN từ các mốc cũ.
Các mô tả chuẩn bị/audit dưới đây giữ làm lịch sử, không phải trạng thái job live.

Đã hoàn thiện `nscc-pbs/analyze-startup.py` cho log sampler cục bộ: rates theo
monotonic time vàPID/start-time; đánh dấu thiếucounter/PIDchurn/gap/reset thay
vì coi là0. Kiểm traoffline và rawown-child cũ đạt; chưa upload/tích hợp/chạyNSCC.
Các pilot04/05/06 giữ nguyên. Bằng chứng mới:
`nscc-pbs/inspection/wake-20261015-2055UTC/`. AuditMNNVL mới:
`nscc-pbs/inspection/wake-20261015-2100UTC/`.

Đã chuẩn bị `nscc-pbs/review-load-sweep.py` và [hướng dẫn thu/đánh giá220575](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/LOAD_SWEEP_REVIEW.md).
Kiểm tra CPU cục bộ đạt11ca, tái tính1565,161394goodtokens/s từ snapshot220562
cũ; **không phải phép đo/repeat mới**. Tool xác minh seal, protocol và thời gian
phase, error/cancel, short non-regression; tải cao fail không tự chặnN32đạt.
Flag offline không thay ownqueue/credit/budget/runtime gates;04/05/06 giữ nguyên.
Export thành công220562 bỏ metricerror_request_count; chỉ chấp nhận vắng metric
khi error_summary, manifest và log cùng xác nhận không lỗi. Bản phát triển đầu
bị false-reject đã đánh dấu lịch sử trong guide; finalreview và11ca tại
`nscc-pbs/inspection/wake-20261015-2105UTC/`.

Đã audit wave9 lúc21:51UTC: cả3stored batch script từSlurm khớp bản frozen,
SHA256SUMS/registryhash đạt, worker chỉ thay đúng1factor. Metadataconfig có
trường kế thừa: graphflags không ghi đủ ở23904; prefill_extra_flags vẫn4096 ở
23905/23906. Worker thực giữgraph64 và dùngchunk2048/8192 đúng dự kiến; chưa
có bằng chứngruntime tại snapshot21:51 vì cả3cònPENDING (lịch sử). Không sửa payload đangqueue.
Bảng so sánh dùng **23778 và23839**, không lấycontrol_job/reference_jobs cũ
làm matchedbaseline: [hướng dẫnwave9](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md).
Bằng chứng mới: `nscc-pbs/inspection/wake-20261015-2150UTC/`.

Đã audit cuối DP-repeat23859 lúc22:12UTC: seals23780/23859 rehashđạt,
12file thực thi giống nhau, config chỉ khác tên/mụcđích. Full60/120/30 vàthờigian
phaseđạt;791warmup/1586measured,0lỗi/hủy;8rankNIXL/UCX và2P/Dwarmupđạt.
Short7/8, chỉreverseđãbiết; recomputeđốichiếu132responsebaselineđạt.
[Review vàbướcđọc23934](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/REPEAT_REVIEW.md)
so với cả23780/23859; gateN54đãmở23934,không tựmởN56. Snapshot22:06chưaNIXL/export
là lịch sử. AuditCPUđầu false-reject vìartifactdirtheojobđãsửa, giữattempt01;
khôngsửapayload. Bằngchứng:`nscc-pbs/inspection/wake-20261015-2210UTC/`.

Đã audit CPU cả hai N54 (23924/23934), bằng chứng mới22:15UTC: script thực
Slurm khớp frozen, SHA256SUMS/registryhash đạt; với CẢ HAI baseline tương ứng,
12file thực thi giống nhau, config chỉ khác tên/mục đích/concurrency52→54.
Launcher chỉ khác tên/path/load. `matched_concurrency=52` và source/control cũ
là metadata kế thừa; launcher đặt54, chưa có export runtime để xác nhận load.
[Bảng và hướng dẫn N54](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md)
phân biệt gateN52 để mởjob (SLA95%,meanITL19,3ms) với SLA benchmark90% sốrequest
đạt TTFT3000ms/ITL20ms. N54 phải so mỗi baseline và mean; tải cao hơn chưa chứng
minh goodput tốt hơn. Không mởN56 hay tự gửi repeat. Bằng chứng:
`nscc-pbs/inspection/wake-20261015-2215UTC/`.


Đã audit runtime23904 lúc22:56:40UTC: checksum frozen/copied payload và script
thựcSlurm đạt;8rank cùng khởi tạo MNNVL+FlashInferdecode vàNIXL/UCX,2P/Dwarmup
đạt,2prefillchunk4096,decodegraph1–64 đúng. So resolvedServerArgs với CẢ23778/23839:
chỉ khácdecode_attention_backend vàrandom_seed engine tự sinh. SeedAIPerf2026
không khóa seedengine; giữ caveat này khi đọc repeat, không tự đổi payload.
Tại snapshot22:56 chưa có full export/smoke; đây là audit lịch sử, đã được
thay bằng finalaudit16/10 bên dưới. AccuracyBTC vẫn chưa xácnhận.
Logprefix được giữ/hash riêng, chưa phải finalseal. Bằngchứng:
`nscc-pbs/inspection/wake-20261015-2255UTC/`. Bước chờ23904 tại mốcđó đã hoàn tất;
không thêmrepeat/N56. NSCC04→05 vẫn cần truycập,terminal220575,baseline,queue,credit.


Đã finalaudit23904/23905 lúc16/10 00:19:38UTC, so với CẢ23778/23839:
seals47file/mỗi run vàpayloadđạt,full60/120/30 vàrawphaseđạt;0lỗi/hủy,
8rankMNNVL/NIXL và2P/Dwarmup,short7/8chỉreverseđãbiết.23904đạt2631,0854goodt/s,
SLA99,0220%,TTFT635,2331ms,ITL16,2334ms; hơnmeanMNNVL **1,4867%**,TTFT+122,9668ms,
ITL−0,9075ms. Đây là một lượt cải thiện tạmthời, chưarepeat/chọncấuhình.
23905đạt2331,3530,SLA98,7697%,TTFT1188,7699ms,ITL15,8064ms; thấp hơnmean
**10,0747%**,TTFT+676,5036ms dùITL−1,3345ms. ĐủSLA nhưnggoodputkém,khôngphảijoblỗi.

Đínhchínhgiớihạn“mộtfactor”: CLIchunk2048 đồngthời làm resolvedprefillbreakable
CUDAgraphmax_bs4096→2048 vàrútgọndanh sáchcapture ởcảhaiworker; khôngđượcquy
kết riêngchunk scheduling haynóigraph giữnguyên. Decodegraphkhôngđổi.
Tại snapshot lịch sử00:19,23906cònchờ; đã finalaudit01:52 (xemPOLICY).
Runtime chunk8192/prefillgraph8192 đã xác minh,không quy kết riêng scheduling.
Outputobserved23904:199–201,23905:199–200tokens; rawcount/sum/min/maxkhớp,
goodput vẫnquyước200tokens nhưbaseline,khôngkhẳngđịnhmọiresponseđúng200.
Giữattempt01CPUfalse-rejectmax200 vàattempt02 phát hiệngraph; khôngsửapayload.
[Review hiện hành](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md).
Bằngchứng:`nscc-pbs/inspection/wake-20261016-0015UTC/`. Khôngthêmrepeat/N56;NSCCvẫnthiếuVPN,
giữ1536SUreservevàgate04→05. Các snapshottrướcđó làlịchsử.


Đã chuẩn bị công cụ CPU `serving-tuning/review-n54.py` để đọc hai job hiện có
23924/23934 sau khi watcher thu xong. Kiểm tra offline qua **21 ca**, rehash bốn
N52 baseline và tái tính đúng goodput cũ; **không có số đo GPU mới**. Tool so cả
hai baseline/mean, kiểm tra seal/payload/protocol, raw count/length/good/mean latency,
NIXL/warmup, resolved ServerArgs và phân biệt thiếu bằng chứng với đo đủ nhưng
fail SLA. Tại snapshot00:45UTC cả hai N54 chưa có terminal seal; nay23924 đã finalaudit
và24009 là repeat xác nhận (xem bàn giao đầu file),23934 cần kiểm lại scheduler.
Không tự mở job/repeat/N56 và không thay watcher hay frozen payload.

Phát hiện khi đối soát bốn export N52: goodput dùng số good request chia khoảng
profiling phase trong manifest; `benchmark_duration` ngắn hơn khoảng 2,8–4,0 ms.
Đã giữ đúng convention hiện có, không sửa số liệu cũ hay suy ra nguyên nhân clock.
DP original/repeat cũng có max observed length 200/201; extrema là diagnostic,
không phải điều kiện phải giống hệt. Các prototype false-reject được giữ cùng
đính chính. [Hướng dẫn N54](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md).
Bằng chứng: `nscc-pbs/inspection/wake-20261016-0045UTC/`. Snapshot 00:19 là lịch sử;
00:50:03 vẫn ba job PENDING(Resources), watcher sống; NSCC 00:46:05 thiếu VPN,
220575/credit vẫn chưa xác minh, giữ 1536 SU và gate 04→05. Không xác thực mới.

## Chuẩn bị EAGLE3 mới — 16/10 00:59 UTC

Đã kiểm tra source thực trong image bằng CPU: target forward→greedy argmax→
compiled verifier được xác minh ở tầng gọi Python, chưa chạy CUDA/model.
Hai threshold1.0 không nằm ở nhánh greedy và không tự chứng minh output giống
control. Source có simulation ghi đè acceptance/token sau verifier; future worker
phải đặt và ghi `SGLANG_SIMULATE_ACC_LEN=-1` bên trong container. Không có bằng
chứng run cũ bật simulation, không sửa kết quả cũ.

Hook EAGLE mặc định max_running_requests48 khi chưa đặt; thiết kế local đã đặt
rõ48 và yêu cầu control giống vậy. Kiểm output đầu dùng toàn request greedy,
neutral penalties, không grammar/logitbias; lưu token IDs thật, điều tra khác biệt
FP8/batching/kernel trước mọi quality/performance claim. Qwen có API capture aux
hidden states nhưng compatibility Instruct-2507, token map, memory và native CUDA
vẫn chưa xác minh. 12 kiểm tra source đạt,72 file được hash; không phải GPU test.
Không tải draft, không job/reservation mới;04→05→06 và mọi gate hiện có giữ nguyên.
[Review EAGLE3](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/SOURCE_REVIEW.md).

Snapshot lịch sử00:58:48UTC:23906/23924/23934 PENDING(Resources),watcher sống;
00:55:29UTC helper thiếuVPN trướcSSH,220575/result/credit chưa xác minh.
Giữ1536SUreserve,campaign16384SU;khôngauth/qsub. Snapshot00:50/00:46 ở trên là
lịch sử,không phải lần kiểm mới. Bằng chứng:`nscc-pbs/inspection/wake-20261016-0055UTC/`.

## Tự động hóa và bộ nhớ

Cron kiểm tra5phút, gọiCodex khi trạng thái thay đổi hoặc tới kỳresearch,
mỗi lượt tối đa20phút, có lock; quotaerror nghỉ30phút. LượtCodex là **phiên mới**,
không tự thấy nguyên chat này. Nó phải đọc README/CURRENT/POLICY và báo cáo.
Không tự nhắn được vào chat gốc. QuotaCodex và creditGPU là hai ngân sách riêng.
