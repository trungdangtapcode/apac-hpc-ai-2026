# Combo N52 repeat1 — 16/10/2026 12:13 UTC

23973 COMPLETED exit0, bắt đầu12:01:57, kết thúc12:11:03 UTC, wall9m06s,
16H200 trên g1/g4. Watcher đã thu terminal seal; review-wave10.py trả
PARTIAL_RESULTS, riêng23973 MEASURED_SLA_PASS. Chỉ một attempt, không replacement.

- 47 file sealed rehash đạt; 14 file submitted khớp registry/frozen, 12 file
  thực thi giống23904; storedSlurm script đã kiểm khớp ở lượt12:06.
- Full60/120/30; raw819warmup/1638profiling,1622good; count/length/meanlatency
  khớp export,0errors/cancel. Observedlength199–200, metric vẫn quyước200tokens.
- Đủ8rank MNNVL/FlashInferdecode/NIXL-UCX;2P/Dwarmup và8connectionHTTP200.
  ServerArgs cả3role chỉ khác random_seed so23904. Seed engine chưa khóa.
- Short7/8, chỉ reverse đã biết; không regression mới. Không accuracyBTC claim.
- **2632,0649 goodtokens/s; SLA99,0232%; TTFT632,6602ms; ITL16,2395ms.**
  So23904: **+0,0372%**, TTFT−2,5729ms, ITL+0,0060ms.
  So mean2MNNVLcontrol N52 cũ: **+1,5244%**, TTFT+120,3939ms, ITL−0,9014ms.

Hai điểm combo2631,0854/2632,0649 gần nhau; chưa đạt gate gainreproduced của
wave10 vì23974freshcontrol và23975repeat2+12long vẫn chưa cóseal. Không trộn
N54 vào meanN52, không gọi đây là ý nghĩa thống kê hay promotion. Không mở
comboN54 trước đủ cảgain/SLA95%/ITL19,3ms/noerror/newshort/longPASSED.

Scheduler12:12:41UTC:23974/23975/24009 PENDING(Priority),3/5slot.
Không thêmjob chỉ đểlấpslot; khôngN56/thirdsuccessfulMNNVLrepeat.
NSCChelper12:10:43 thiếu liveVPN trướcSSH;3job/creditUNKNOWN, giữ4608SU,
headroom9394,631SU,cap16384SU/projectreserve13000SU. Khôngauth/DUOmới.

Evidence: `nscc-pbs/inspection/wake-20261016-1210UTC/` gồm terminalseal copy,
wave10-final-review.json, payloadcheck, rawreview và scheduler/access snapshots.
Các export/rawreview lúc12:11–12:12 trướcseal được giữ như tiền kiểm lịch sử;
review cuối qua seal thay thế kết luận pendingseal. Raw gốc ởruns/23973 giữ nguyên.
