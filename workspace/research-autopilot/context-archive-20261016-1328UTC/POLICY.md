# Chính sách Qwen hiện hành — 16/10/2026 12:52 UTC

Đọc notes/README.md và notes/CURRENT.md trước. Trạng thái dưới đây là snapshot
có giờ kiểm, phải kiểm lại scheduler khi tiếp tục. Bản trước lưu ở
POLICY-before-20261016-1025UTC.md; missingVPN trước05:43,1queued trước05:53,
trạng thái VPN/PBS06:17 và23934pending là lịch sử.

## Kiểm mới nhất — 16/10/2026 12:52 UTC

Snapshot thực12:50:42UTC:23974/23975/24009PENDING(Resources),3/5slot,
chưaallocation/Start/End;watcher419440sống. Registry12:51 mỗi entry một attempt,
không terminalseal mới. Bản12:49 ghi Priority là lỗi diễn giải; raw12:48 cũng
Resources. Các trạng thái12:15 vàtrước ởdưới là lịch sử,không live.
NSCChelper12:50:42 thiếu liveVPN trướcSSH;220720–220722/creditUNKNOWN,
nguyênnhân ngắtchưabiết. Giữ4608SU/headroom9394,631SU,khôngauth/DUOmới,
release reserve/duplicatejob. Không thay scope/budget/gate/payload/watcher/lịch.
Reviewer chỉ chạy khi cóseal mới; NEXT_STEP tronginspection/wake-20261016-1250UTC/
ghi trigger/lệnh. Không cònviệc độc lập,kếtthúc khôngchờqueue.

## Phạm vi và giới hạn

Tiếp tục research Qwen chủ động theo chỉ dẫn user06:21: nghiên cứu, phân tích,
chuẩn bị và submit khi đủ gate/budget/slot; không chờ nhắc sau mỗi wave.
Mỗi lượt tối đa20phút; không nestedagent/Codex, lịch/controller/watcher mới,
externalmessage/BTCupload, sửa submission/slides, đọc file riêng người khác,
GPU trên login hoặc truy cập authfile/chatcredential. CPU tối đa4threads.
Không lưu password/OTP/session, khôngTLSbypass. HPC_Task giữ rỗng.
Báo cáo tiếng Việt; submission/slides tiếng Anh. Kết thúc khi hết việc độc lập
có ích; không chờqueue/lặp audit bất biến. Scheduled runs là phiên mới qua file
handoff, không tự nhắn chat gốc. QuotaCodex khácGPUcredit.

## NSCC: truy cập và ngân sách hiện chưa xác minh lại

Helper12:15:39UTC báo không tìm thấy liveVPNsession trướcSSH. Không loginVPN/
DUO mới, restart/Ctrl-C phiên cũ hoặc đoán nguyên nhân mất kết nối. User chỉ
cho phép login05:40; thành công05:43–06:26 là bằng chứng lịch sử, không live.
VPN mất không tự hủyPBS.220720/220721/220722 hiện UNKNOWN; lần xác nhận cũ
06:17 làR/H/H theo afteranychain. Không duplicate/release dependency hoặc sửa
frozenpayload. Không qsub mới trước refresh TOÀN BỘ ownqueue/credit và reconcile
các job chưa rõ. Không suy terminal từ walltime đã trôi qua.

Cap16384SU TỔNG gồm probe/job lỗi/job cũ, projectreserve13000SU;max3ownPBS GPUjob
pending/running trong strictafteranychain,max1running16H100. Max45phút/job,
reserve128*GPUs*hours tối đa1536SU/job dưới budget.lock TRƯỚCqsub.
Ledger LỊCH SỬ asof14:00:02Singapore,queried06:17:used2381.369,balance60082.631,
InDoubt1536 đã trừ khỏi balance. Chưa reconcile terminalcharge220720–220722.
Giữ đầy đủ4608SU cho3job,headroom bảo thủ9394.631SU; không giải phóng reserve
vì mấtVPN,không trừ InDoubt lần hai. Tổngused+unreconciledcharge+reserve<=16384.

## NSCC: dữ liệu và bước tiếp

220575 terminalF/exit0 đã thu/đối soát:baseline cùngH100 N32=1570.2123goodt/s,
N34=1625.5950,SLA100%;N36=1356.3518,SLA82.1218%fail,0errors/cancel;
short7/8 chỉknownreverse. Baseline thiếu runtime log nên không gán backend
ngoài evidence.04MNNVL/05FlashInfer/06prefetch là3trial độc lập so220575;
04fail không tự loại05/06. Grid32/34/36/38/40/42,full60/120/30,stop-on-fail.

Archive220720 thu06:26 bịtar exit1 do thư mục n38/confirm đang thay đổi.
Lượt10:25 đọc hết102members, giữ nguyênarchive/stderr và phục hồi selectedfiles.
N32/N34/N36 đã đối soát rawcounts/latencies/lengths/goodrequest/phases,fullprotocol,
0errors/cancel:1692.1662/1754.0728/1787.7370goodt/s,SLA100%. Đây là LỊCH SỬ
livecopy,không terminalseal hay finalquality/runtime. Gain so cùngN cũ
+7.7667%/+7.9034%/+31.8048%;N36controlfailSLA nên không gọi31.8%rawthroughputgain.
N38 chưa đủ,không dùng. Rolelogs trongarchive rỗng;reportedMNNVL/FA3 vàautoKV
không chứng minh8rank hoặc BF16 hiệu dụng. AccuracyBTC chưa xác minh.

Khi existingSSH dùng được:collect-run.py cả3job,review-candidate-sweep.py theo
CANDIDATE_SWEEP_REVIEW.md; đọcseal/payload/raw/protocol/short/long/runtime riêng.
Nếu05/06 cònown/R thì single-shot collect-live-runtime.py, khôngnewwatcher.
Tiếp theo NEXT_H100_CONFIRMATION.md: chỉ sau đủterminal/runtime/longPASSED/
no shortregression vàqueue/credit mới chuẩn bị1freshcontrol+1candidate repeat,
max2×1536SU,strictafterany,grid cũ. Chưareserve hayqsub cặp này.
Nếu thiếu rolelogs,logging trực tiếp trongtaskpbsdsh phải chuẩn bị vàreview cho
cảcontrol/candidate tiếp; không sửa3payload cũ. Prefetch đánh giástartup với
caveatnode/cache/time/TP/EP,không quy nguyên nhânI/O từtimings.

## H200 Slurm: kết quả, giới hạn và bước tiếp

Cap5pending/running. Kiểm12:15:39UTC:23973COMPLETEDexit0,kếtthúc12:11:03,
wall9m06s,16H200g1/g4;23974/23975/24009PENDING(Priority),3/5slot.
Watcher419440 sống12:15:39 vàđãthu terminalseal23973. Finalreview47sealedfiles,
14payloadhash,12executionfiles giống23904;raw819warmup/1638profiling,full60/120/30,
1622good,0errors/cancel,8rankMNNVL/FlashInfer/NIXL,2P/Dwarmup,8connectionHTTP200;
ServerArgs chỉ khácrandom_seed. Short7/8knownreverse,no newshort,output199–200.
2632.0649goodt/s,SLA99.0232%,TTFT632.6602ms,ITL16.2395ms;so23904+0.0372%,
sohistoricalMNNVLN52mean+1.5244%. Wave10PARTIAL_RESULTS;chưa gainreproduced
vìthiếu23974/23975+long. Không sửa queuedpayload/duplicatewatcher/hủy vìPriority.
23934 COMPLETED exit0,08:11:21UTC,wall9m17s;finalreview47sealedfiles/raw/protocol/
12executionfiles/runtime so cả23780/23859 đạt.802warmup/1598profiling,
8rankNIXL và2P/Dwarmup,0errors/cancel,short7/8knownreverse;raw132baseline+8case
đã tái chấm.2555.4232goodt/s,SLA98.7484%,TTFT751.9882ms,ITL16.8873ms.
SoDP N52mean:+0.4633%,TTFT+145.1971ms,ITL−0.0717ms;soMNNVL23924 cùngN54:
−2.9844%,TTFT+151.5435ms,ITL−0.2229ms. Một điểm/package,khôngclaim thống kê/
hiệu ứngkernel. Kết thúc boundedDP3point tạiN54;khôngthêmDPrepeat/N56.

23924 MNNVLN54:2634.0344goodt/s,SLA98.9024%,TTFT600.4446ms,ITL17.1102ms,
seal/raw/runtimePASS,0errors/cancel,knownreverse;gain1.6004%vs2N52mean chưa lặp.
24009 là đúng MỘT điểm xác nhậnN54,không successfulrepeat thứ3/N56/promotion.
Kế thừa watcherbudget-deferredreplacement tối đa3attempt cho điểm chưa đo đủ;
giữ mọiattempt vàreviewtay nếu replacement,khôngchọnpeak.

Wave10:23973comboN52repeat1đãfinalreview,23974freshMNNVLN52control,23975comboN52repeat2+
12longchecks. Dùngreview-wave10.py vàreview-mnnvl-n54-repeat.py sau seal.
So mọi repeat với cả3control/mean vàdrift. Combo23904 đơn lẻ2631.0854goodt/s,
SLA99.022%,ITL16.233ms,gain1.4867% chưareproduced. MNNVLN52 lặp2592.16/2592.92;
DP2549.20/2538.08. Chunk2048/8192 thua2331.353/2547.854,khôngrepeatloser.
Chunk đồng thời thayprefillgraph,khôngquy riêng scheduling. AIPerfseed2026
không khóaengine seed. Outputlength199–201 làdiagnostic,metricquyước200.

Full60/120/30,officialFP8checkpoint,BF16KVtheoplan,16H2008+8,RR;phảiđọc runtime.
Cả2combo repeat hơnfreshcontrol,meancombo hơnmeancontrol,tấtcảSLA>=90%,
0errors/cancel,no newshort trước cờgainreproduced;không phải kiểm định thống kê.
Chỉ viết boundedcomboN54plan khi gainlặpđược vàMỖIcomboSLA>=95%,ITL<=19.3ms,
0errors/cancel/no newshort,longPASSED. Missing/deferred/failedlong chặn gateplan,
khôngxóa benchmark. Conditionalnextpoint giữsameexecution,chỉload52→54/labels,
max17phút16H200,source/ownqueue review trướcarming qua watcher hiện có.
Hiện chưa gate,khônggửi job chỉ để lấp slottrống. MNNVLrepeat không bỏ gatecombo.
Accuracy99%referenceBTC chưaxácminh,khôngblindN56/promotion.

## Chuẩn bị ngoàiGPU và báo cáo

EAGLE3 vẫndesign/sourceCPU,bộ14casepintokenizer/template,input+cap<=8085;
chưa model/GPU/EOS/acceptance/compatibility/accuracy. Capture35mockcase,
tokenreview30synthetic/source12checks không phải modelresult. Futureworker:
SGLANG_SIMULATE_ACC_LEN=-1,greedyneutral,max-running-requests48matched.
Khôngdownload draft/upload/job/reserve nhánh này khi chưađủgate;ưu tiên04→05→06.
vLLMdesign,image/runtimechưakiểm. Startup sampler/analyzer local chưaintegrate.

Mỗi lượt ghiLATESTtiếngViệt ngắn,appendHISTORY,cậpnhậtCURRENT/DECISIONS/tutorial
khi có finding/correction. Preserveallrawattempts. Evidence lượt10:25:
nscc-pbs/inspection/wake-20261016-1025UTC/.

## Chuẩn bị logging — 16/10/2026 10:59 UTC

research-next/pbs-task-logging-01 có wrapper/shim staging,12/12CPUstub đạt;
chưa upload/integrate/PBS thật. Nếu thiếu log sau thu3terminal, dùng cùngsource/
hash trênCẢ freshcontrol/candidate mới; reviewfullbundle/tạolạiSHA256SUMS trước
reserve/submit theo gatecũ. Không sửa04/05/06 hoặc chạyallocation riêng đểtestlog.
Collector đãthu cảrun;runtime review phảiđọc task-*.log vàcensus rankthực;CPUtest
không chứng minh backend/KV hay nguyên nhân rolelog rỗng. Giữ umask/exit/signals.
Snapshot10:25 ở đoạn cũ là lịch sử;freshcheck10:55 vẫn khôngaccess/credit mới.
Evidence: `nscc-pbs/inspection/wake-20261016-1055UTC/`.

## Kiểm lịch sử — 16/10/2026 11:06 UTC

11:05:33UTC cả4H200 vẫn pendingResources, chưaStart/End/allocation;watcher419440
sống. HelperNSCC vẫn thiếu liveVPN trướcSSH;3job/creditUNKNOWN,giữ4608SU.
Không gửi/sửa job,auth mới hay chạy lại auditCPU bất biến. NEXT_STEP của lượt
inspection/wake-20261016-1105UTC/ ghi trigger và lệnh thu/review đã có; chờ
dữ liệu/access mới, kết thúc ngay. Các snapshot10:55 ở trên là lịch sử.

## Bàn giao lịch sử —16/10/2026 12:07UTC

23973 đã RUNNING như snapshot ở trên;mọi mô tả cả4pending11:05 là lịch sử.
Evidence inspection/wake-20261016-1205UTC/ giữ logprefix vàlive-runtime-review.
Không terminalseal/fullmeasurement mới,không chạywaiting-path/test bất biến.
Dùngreview-wave10.py sau seal23973;chờfreshcontrol/comborepeat2+long để xétgate.
NSCCcheck12:05:35 vẫn thiếuVPN trướcSSH,giữ4608SU/UNKNOWN,khôngauth mới.
NEXT_STEP lượt11:05 vẫn áp dụng cho trigger thu/review;khôngcònviệc độc lập,
kết thúc ngay không chờjob. Không đổi scope/budget/gate hoặc lịch/watcher.

## Bàn giao mới —16/10/2026 12:13UTC

23973 đãCOMPLETED vàfinalreview như trên;mọi mô tảRUNNING/chưaexport/seal ở
bàn giao12:07 là lịch sử. Evidence inspection/wake-20261016-1210UTC/ giữ cả
snapshottrướcseal vàwave10-final-review.json cuối. Không chạy lại audit/test
bất biến;reviewer chỉ chạy lại khi23974/23975 hoặc24009 cóseal mới. ComboN54
vẫnchờ đủgate;khôngthêmallocation hoặc lấpslot3/5. NSCC vẫnUNKNOWN/4608SU.
Khôngđổi scope/budget/watcher/lịch;phần độc lập đãxong,kếtthúc khôngđợiqueue.

## Kiểm lịch sử — 16/10/2026 12:16 UTC

Scheduler12:15:39UTC:23974/23975/24009PENDING(Priority),3/5slot,khôngallocation;
watcher419440sống. Registry mỗi entry một attempt; không có terminalseal mới.
23973finalreview12:13 giữ nguyên; không chạy lại reviewer/audit bất biến.
NSCChelper12:15:39 vẫn thiếu liveVPN trướcSSH;3job/creditUNKNOWN,giữ4608SU.
NEXT_STEP tại inspection/wake-20261016-1215UTC/ đã ghi trigger và bước thu/review;
không còn việc độc lập, kết thúc không chờqueue. Scope/budget/gate không đổi.

## Access lịch sử12:48UTC
VPNhelper found no live session; oldtool79786unknown, no finaldisconnectlog. Causeunknown. No newauth/DUO. PBSchain remains unverified; do not infer completion or release reserves. H2003pending,combo repeat2632.06 confirmed;seeCURRENT.

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

