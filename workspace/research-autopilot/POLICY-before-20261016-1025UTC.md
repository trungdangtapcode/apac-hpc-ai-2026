# Chính sách Qwen hiện hành — 16/10/2026 06:18 UTC

Đọc notes/README.md và notes/CURRENT.md trước. Chính sách cũ trước khi hợp nhất
được giữ ở POLICY-before-consolidation-20261016-0555UTC.md; các trạng thái
missingVPN/Permissiondenied và quy tắc1queued trong đó là lịch sử, đã được
chỉ dẫn người dùng05:40/05:49 và amendment05:53 thay thế.

## Phạm vi và giới hạn

Tiếp tục research Qwen chủ động, giữ mọi kết quả/lỗi, không chờ nhắc từng bước.
Mỗi lượt tối đa20phút; không nestedagent/Codex, lịch/controller/watcher mới,
externalmessage/BTCupload, sửa submission/slides, đọc file riêng của người khác,
GPU trên login hoặc truy cập authfile/chatcredential. CPU staging tối đa4threads.
Không ghi password/OTP/session vào notes; khôngTLSbypass. HPC_Task giữ rỗng.
Báo cáo tiếngViệt; tài liệu nộp/slides tiếngAnh. Kết thúc ngay khi hết việc độc
lập có ích, không chờqueue hoặc lặp audit bất biến. Lượt scheduled là phiên mới
qua filehandoff; không hứa nhắn tự động vào chat gốc. QuotaCodex khácGPUcredit.

## Truy cập NSCC

Người dùng cho phép login05:40; VPN/SSH đã khôi phục và BatchMode kiểm lại
05:55/05:58 thành công. Giữ VPNtool79786; khôngrestart/Ctrl-C hay xác thực/DUO
mới. Helper đề xuấtIKE86400s nhưng chưa kiểm đủ24h; phiên dùngike-persistfalse,
không cóSAcache đã xác minh. Không suy raDUOfactor hoặc trạng tháiWindows.
VPN mất không tựhủyPBSjob; phải reconcile trước khi thay thế job.

## NSCC H100: chuỗi đang được phép

Kiểm PBS06:17:25UTC:220720(MNNVL04) R, elapsed00:24:39;
220721(FlashInfer05) H afterany220720;220722(loaderprefetch06) H afterany220721.
HELDdo dependency bình thường, khôngqrls/hủy/submitduplicate. Max3ownPBS GPUjob
pending/running chỉ trong chuỗiafterany đã kiểm, max1running và16GPU đồng thời.
Mỗi job45phút tối đa1536SU, thửN32/34/36/38/40/42 với full60/120/30 và dừng
tăng khi điểm trước failSLA/error. Các candidate độc lập so220575;04fail không
tự loại05/06. Nếu lỗi hạ tầng chung thì phân tích và dừng chuỗi có lý do.

Campaign cap16384SU TỔNG gồm probe/job lỗi/job cũ; giữprojectreserve13000SU.
myprojects truy vấn06:17 trả ledgerasof14:00:02Singapore:used2381.369,
balance60082.631,InDoubt1536; balance đã trừ prepaid, không trừ lần hai.
Chưa reconcile charge terminal220720.
Giữ4608SU cho220720–220722; headroom chưa phân bổ9394.631SU. Trước mọiqsub:
refresh TOÀN BỘ ownqueue, credit và job không chắc; dưới budget.lock reserve
128*GPUs*hours tối đa1536SU/job. Tổngused+charge chưa đối soát+reserve<=16384;
không trừ InDoubt vào balance hai lần. Không tăngcap từ chỉ dẫn tận dụngGPU.

220575 terminalF/exit0,wall30:25 đã đối soát ledger và thu fullartifact.
BaselineH100: N32=1570.2123goodt/s,SLA100%;N34=1625.5950,SLA100%;
N36=1356.3518,SLA82.1218% fail;0errors/cancel,short7/8 chỉreverse đã biết.
Không quy kết runtime backend khi thiếu log; khôngcoismoke làaccuracyBTC.
Đã giữpartial60s và hai collection đầy đủ05:45/05:50.

Tiếp: thu terminal04→05→06, xem nscc-pbs/CANDIDATE_SWEEP_REVIEW.md và
review-candidate-sweep.py. Seal/frozenpayload/protocol/short,long vàruntime
phải đọc riêng. Collector đã bổ sung schedulerOutput_Path/Error_Path, chỉ lấy
file khi có; chưa thu stdout mới. Logrole04 kiểm06:15 còn rỗng. /get_server_info06:16 HTTP200 cả3server,
decode báo mnnvl/FA3,TP8EP8,graph1–64; đây là reported runtime config,
chưa có log khởi tạo cả8rank. Hai pairrouter có HTTP200 lúc06:12:30.
Dùng collect-live-runtime.py lúc05/06 đangR để giữ startup/config; single-shot,
không tạo watcher. autoKVdtype chưa chứng minh BF16 hiệu dụng. Không suy từ
payload thành runtime; không gán gain giữa hardware khác nhau. Giữ mọi attempt,
so cùngN/cùngH100 và ghi plan tiếp dựa dữ liệu, không tạo hàng loạtconfig.

## H200 Slurm: giới hạn và bước tiếp

Cap5pending/running; kiểm06:15:28UTC:23934/23973/23974/23975/24009 đều
PENDING(Priority),sacct chưa allocation/start/end. Watcher419440 sống.
Không sửa frozenqueuedpayload, duplicatewatcher hay hủy/requeue vìPriority.
serving-tuning-10/PLAN.md,prepared-pilots.json giữ nguyên.

23924 MNNVLN54 finalseal/raw/runtime PASS:2634.0344goodt/s,SLA98.9024%,
TTFT600.4446ms,ITL17.1102ms,0errors/cancel,short7/8knownreverse;
hơnmean haiN52control1.6004%,một quan sát chưa xác nhận lặp.
24009 là đúng MỘT repeat xác nhậnN54, không successfulrepeat thứ3/N56/promotion.
Kế thừa watcherbudget-deferredreplacement tối đa3attempt cho điểm chưa đo đủ;
giữ mọi attempt,review tay nếu replacement,không chọnpeak.

23934DP+DeepEPN54: dùngserving-tuning/review-n54.py so cả2control vàmean;
giữ gatewave7/8. Wave10 gồm23973comboN52repeat1,23974freshMNNVLN52control,
23975comboN52repeat2+12longchecks. Dùngreview-wave10.py và
review-mnnvl-n54-repeat.py sauseal. So mọirepeat với cả3control/mean vàdrift.
Combo23904 đơnlẻ2631.0854goodt/s,SLA99.022%,ITL16.233ms,hơnmeanMNNVL1.4867%;
chưa coi reproduced. MNNVLN52 đã lặp2592.16/2592.92;DP2549.20/2538.08.
Chunk2048/8192 thua2331.353/2547.854,khôngrepeat loser. Chunk đồng thời thay
prefillgraph; không quy kết riêng scheduling. Engine randomseed có thể khác,
AIPerfseed2026 không khóa engine seed. Giữ outputlength diagnostic199–201.

Fullprotocol60/120/30,officialFP8checkpoint,BF16KV,16H2008+8,RR.
Cảhai combo repeat phải hơnfreshcontrol,meancombo hơnmeancontrol,tấtcảSLA>=90%,
0errors/cancel,no newshort trước cờ reproduced; khôngcoi đây là thống kê đủ.
Chỉ viết plancomboN54 khi gain lặp được và MỖIcomboSLA>=95%,ITL<=19.3ms,
0errors/cancel,no newshort,longPASSED. Missing/deferred/failedlong chặn gate đó,
không xóa benchmark. MNNVLrepeat không bỏ gatecombo. KhôngblindN56/promotion.
Accuracy99%reference củaBTC vẫn chưa xác minh.

## Chuẩn bị ngoàiGPU và báo cáo

EAGLE3 chỉdesign/sourceCPU: bộ14case token đã pin tokenizer/template,
inputretrieval3788/7885,input+cap<=8085. Chưa model/GPU/EOS thật/acceptance/
compatibility/accuracy. Capture35mockcase,tokenreview30syntheticcase,source12
checks không phải modelresult. Tắt simulation trong worker
SGLANG_SIMULATE_ACC_LEN=-1,greedy neutral,max-running-requests48matched khi
nhánh này được phép. Khôngdownload draft/upload/job/reserve mới trong lượt.
vLLM cũng mớidesign,image/runtime chưa kiểm. Startup sampler/analyzer local
chưa integrate; không để việc chuẩn bị đổi ưu tiên04→05→06.

Mỗi lượt ghi LATEST.md tiếngViệt ngắn,appendHISTORY.md và cập nhật CURRENT,
DECISIONS hoặc tutorial khi có tìm hiểu/sửa kết luận. Giữ rawartifact và thời
điểm, không trình snapshot cũ như live. Evidence lượt này:
nscc-pbs/inspection/wake-20261016-0615UTC/.

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
