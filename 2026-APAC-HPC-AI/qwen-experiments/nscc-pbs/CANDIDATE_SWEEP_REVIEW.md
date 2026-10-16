# Đọc chuỗi H100 04/05/06 — 16/10/2026

Thu snapshot terminal bằng `collect-run.py JOB`; giữ mọi attempt. Collector hiện
đọc thêm Output_Path/Error_Path của PBS (kể cả đường dẫn bị xuống dòng), chỉ lấy
file đúng job nằm trong cây thí nghiệm. Nếu file chưa tồn tại thì không lấy;
không coi việc thiếu log là backend đã lỗi hoặc đã hoạt động. Sửa này chưa thu
được stdout mới trong lượt05:55; baseline220575 hiện không thấy file ở đường
scheduler khai báo. Các log role220720 quan sát05:56 còn0byte.

Từ thư mục qwen-experiments, thay SNAPSHOT và PILOT cho từng job:

```bash
python3 nscc-pbs/collect-run.py 220720.pbs111
python3 nscc-pbs/review-candidate-sweep.py SNAPSHOT \
  --baseline nscc-pbs/collected/220575.pbs111/20261016T054555388584Z \
  --baseline-smoke nscc-pbs/collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json \
  --pilot h100-mnnvl-04 --out FRESH-REVIEW.json
```

Job220721 dùng h100-flashinfer-05;220722 dùng h100-loader-prefetch-06. Reviewer
chỉ nhận đúng job trong continuous-plan, rehash seal và toàn bộ payload frozen.
Job thay thế cần review tay. Mỗi candidate so độc lập với220575 ở cùng N32/34/36;
N38+ không có control cùng tải. Giữ điểm failSLA, tách thay đổi goodput/TTFT/ITL,
không chỉ chọn peak. Candidate chỉ một lần đo với control cũ, chưa chứng minh
lặp lại hoặc tách được drift giữa node/thời điểm.

Long diagnostic có PASSED/FAILED/DEFERRED/MISSING/UNSEALED/INCONSISTENT. Missing,
deferred hay failed không xóa benchmark đã hoàn tất nhưng không đủ quality gate.
Đọc runtime riêng: resolved ServerArgs, log8rank MNNVL hoặc backendFlashInfer,
NIXL/UCX, pairwarmup và loader startup. Hash payload chỉ chứng minh input code;
reviewer luôn để runtime MANUAL_REVIEW_REQUIRED và không cho promotion.
8case short và12case retrieval không chứng minh accuracy99% củaBTC.

Validation CPU:11kiểm parser/seal/long và baseline thật;5kiểm fixture terminal
(dùng export220575 giả lập candidate, KHÔNG phải kết quả220720). Hai attempt fixture lỗiEXDEV(/tmp khác filesystem) và permission thư mục frozen;
đã sửa chỗ tạo fixture cùng filesystem/quyền bản copy, không sửa artifact gốc. Bằng chứng:inspection/wake-20261016-0555UTC/. Chưa có terminal
candidate thật để kiểm chứng trọn pipeline thu→review04/05/06.

Bước sau: đọc kết quả04,05,06 theo dữ liệu;04fail không tự loại05/06. Không thêm
job khi chuỗi đang đủ3slot, khôngrelease dependency. Reconcile queue/credit và
reserve dưới budget.lock trước mọiqsub tiếp. Chỉ viết plan lặp candidate tốt khi
có fullprotocol, runtime và output đủ; không mở thêm config không có giả thuyết.


Bổ sung06:18UTC: lúc job cònR, thu một snapshot runtime nhẹ qua existingSSH:

```bash
python3 nscc-pbs/collect-live-runtime.py 220721.pbs111 --out FRESH-RUNTIME-DIR
```

Chỉ nhận job trongplan, kiểm own/R trước đọc endpoint, tắt HTTPproxy, không gửi
inference/auth hoặc tạowatcher. Lưu allowlistconfig/startuptimes/internalstate,
pairrouterlogs,accounting vàseal;khônglưu authfields từserverinfo. Đã chạy thật
220720 và6kiểm đạt ởwake-20261016-0615UTC/runtime-capture-validation.json.
Một internalstate/endpoint không phải một rank; backendmnnvl báo từserverinfo
chưa chứng minh logkhởi tạo8rank. KVdtypeauto chưa chứng minhBF16 hiệu dụng.
Timings làreportedstartup,không suy nguyênnhânI/O,không dùnglastthroughput làm
benchmark. Collector này không thay terminalcollect/seal/review/runtimegate.
