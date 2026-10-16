# Đọc wave10: lặp combo và control mới

Chuẩn bị 16/10/2026; mô tả chưa có runtime lúc viết là lịch sử.
Cập nhật12:13UTC:23973 đã finalreview; xem REPEAT1_RESULT.md và đoạn cuối.
Job ACTIVE trong controller chỉ nghĩa đang theo dõi. Kiểm tra scheduler trực tiếp.

Chạy sau khi watcher đã thu artifact và tạo terminal seal:

```bash
python3 serving-tuning-10/review-wave10.py --out /path/to/new-wave10-review.json
```

Tool chỉ đọc CPU, không gửi job, sửa payload hay tự chọn cấu hình. File output
phải mới. Khi chưa có seal, trả `WAITING_FOR_SEALED_RESULTS`; một phần hoàn tất
thì `PARTIAL_RESULTS`. Seal/transport/output/runtime không hợp lệ trả lý do cụ thể.
SLA dưới 90% với evidence đầy đủ vẫn giữ là `MEASURED_SLA_FAIL`.

- Combo: 23904 gốc, 23973 repeat1, 23975 repeat2. Control MNNVL: 23778,
  23839 và 23974 mới. Không lấy `control_job`/`reference_jobs` kế thừa trong
  config làm baseline. Chúng là metadata lịch sử.
- Đọc từng combo so từng control, mean cả ba mỗi nhóm và drift của 23974 so
  mean hai control cũ. Tool không chọn peak. Cờ gain lặp được là quy tắc mô tả
  thận trọng: tất cả đạt SLA90%, mean combo cao hơn mean control và cả hai
  repeat cao hơn control mới. Không phải kiểm định ý nghĩa thống kê.
- Tái dùng reader N54 để kiểm terminal seal, payload hash, raw export, protocol
  60/120/30, SLA, error/cancel, short non-regression, NIXL/warmup. Kiểm thêm
  8 rank MNNVL, 8 rank FlashInfer ở combo, execution files giống source và
  resolved ServerArgs chỉ khác engine random_seed. Long benchmark phải giữ
  nguyên prefix đo của 23904; phần append có trong frozen payload đã hash.
- Goodput vẫn là good request/giây nhân quy ước 200 tokens; observed lengths
  là diagnostic. Engine seed chưa khóa; seed AIPerf2026 không khóa seed engine.

23975 chạy 12 retrieval sau phép đo. Tool kiểm seal và tái chấm câu trả lời từ
response gốc; giữ riêng `PASSED`, `FAILED`, `DEFERRED`, `INCOMPLETE`, `MISSING`.
Timeout có thể để lại log/marker mà chưa ghi JSON vì script ghi kết quả cuối
cùng; không biến thiếu JSON thành pass. Số token input là tokenizer.encode
prompt trong script, chưa bao gồm chat template; không gọi là chính xác3800.
Nếu failed/deferred, giữ benchmark đã đo và điều tra diagnostic riêng.

Gate viết plan comboN54 cần gain lặp được theo quy tắc trên, cả ba combo
SLA>=95%, meanITL mỗi lượt<=19,3ms, không error/cancel/new short regression,
và long diagnostic PASSED. Cờ này chỉ phục vụ viết plan có giới hạn sau khi
đọc evidence và queue; **không tự submit**, không mở N56. Hai N54 23924/23934
tiếp tục dùng `serving-tuning/review-n54.py` và gate wave7/8 riêng.

Smoke7/8 với reverse thất bại đã biết, hay long12/12, đều không chứng nhận
accuracy99% của BTC. Nếu có sai khác mới thì giữ nguyên câu trả lời và điều tra.

Bằng chứng chuẩn bị: `nscc-pbs/inspection/wake-20261016-0240UTC/`.
Stored Slurm scripts của ba job được giữ lúc còn queue và khớp frozen scripts;
đây là kiểm launcher, chưa chứng minh runtime.

## Mở rộng MNNVL N54 —16/10 05:24UTC

23924 đã finalaudit đạt2634,0344goodt/s,SLA98,9024%,ITL17,1102ms;gain1,6004%
so meanhaiN52 nhưngTTFT+88,1784ms. Đã mở đúng1điểm xác nhận độc lập24009,
không phải comboN54 hayN56. 12file thực thi giống23924; config chỉ đổi
experiment/purpose, launcher đổi tên/path; metadatawave7/matched52 kế thừa,
loadthực trong launcher là54. Payload và storedscript24009 đã kiểm khớp.

Sau seal: `python3 serving-tuning-10/review-mnnvl-n54-repeat.py --out /path/to/new.json`.
Tool so23924,haiN52cũ và23974nếu cóseal;đo drift vàmean riêng theo load,
không trộnN52/N54 vào cùngmean. Chưa thử terminalpath24009 vìjob đang chờ;
chỉ tái dùng reader đã kiểm trên23924 vàkiểm syntax/waitingpath. Nếu watcher
có budget-deferred replacement theo logic hiện có (tối đa3attempt),tool đòi
review tay để giữ toàn bộattempt thay vì tự chọn kết quả đẹp. Không tựsubmit.

## Live runtime23973 —16/10/2026 12:06:28UTC

Scheduler12:06:56:23973RUNNING16H200,từ12:01:57;23974/23975/24009pendingPriority.
Submitted14files khớp frozen/registry,12executionfiles giống23904;storedscript
khớp. Decode census8rankMNNVL/FlashInfer/NIXL-UCX đạt;resolvedServerArgs cả3role
chỉ khácrandom_seed.3serverready;chưa đủpair/connectionwarmup/export/terminalseal
trongprefixsnapshot nên chưa có fullmetric/gain/quality mới. PrefillTriton3.2.0
fallback4line/role cũng có23904,không quy nguyên nhân tốc độ. Giữrawprefix/hash:
`nscc-pbs/inspection/wake-20261016-1205UTC/live-runtime-review.json`.
Không sửa frozenpayload hay gate;terminalreview vẫn bắt buộc qua watcher seal.

## Final repeat1 —16/10/2026 12:13UTC

23973COMPLETEDexit0 lúc12:11:03;47fileterminalseal rehash đạt,fullprotocol/raw/
payload/runtime/shortnonregression đạt.2632.0649goodt/s,SLA99.0232%,ITL16.2395ms;
so23904+0.0372%,so2historicalN52controlmean+1.5244%. Wave10PARTIAL_RESULTS,
23974/23975chưa seal;khônggainreproduced/comboN54gate hoặcaccuracyclaim.
Snapshotlive12:06 ởtrên là lịch sử;pair/connectionwarmup vàexport nayđãđủ.
Xem [phân tích](REPEAT1_RESULT.md);review lại khi cóseal mới,khôngtest bất biến.
