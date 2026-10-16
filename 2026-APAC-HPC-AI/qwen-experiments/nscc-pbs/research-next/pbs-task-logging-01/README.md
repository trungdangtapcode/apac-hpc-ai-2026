# Chuẩn bị log bên trong PBS task — 16/10/2026 10:59 UTC

Chỉ là bản chuẩn bị CPU cục bộ. Chưa upload, tích hợp vào allocation, reserve SU
hay submit. Không sửa load-sweep-03 hoặc ba bundle 04/05/06 đã gửi.

Archive220720 lịch sử06:26 có role logs rỗng dù serverinfo đã phản hồi. Source
hiện tại redirect stdout/stderr của tiến trình pbsdsh ở phía launcher. Chưa xác
minh vì sao output task không vào role log; chưa được kết luận PBS spool là
nguyên nhân duy nhất. Bản này giảm phụ thuộc vào đường chuyển output đó bằng
cách mở file ngay trong task trên compute node, trước module/container startup.

`pbs-task-log.sh` tạo file riêng mode0600 bằng mktemp trong run directory hiện
có, redirect cả stdout/stderr rồi exec nguyên command. Không in argv/environment.
Khôi phục umask của task sau khi mở log; giữ mã thoát và tín hiệu của command.
Lỗi tạo log chặn command. Header chỉ có UTC/host/PID/path, không phải marker job
terminal. SIGKILL/walltime có thể làm log thiếu; vẫn phải kiểm scheduler/seal.

`pbs-shim.sh` là bản staging từ load-sweep-03, chỉ thay lời gọi pbsdsh để đi qua
wrapper; diff và SHA source được giữ. GPU offset/CPU count/container args không
đổi. Log nằm ở `runs/JOB/task-prefill-0-node0.*.log`,
`task-prefill-1-node0.*.log`, `task-decode-0-node1.*.log`; task CPU dùng
`task-aux-node0.*.log`, tên ngẫu nhiên tránh ghi đè giữa router/warmup/aiperf.
Role log launcher cũ vẫn giữ output/spool nếu có. collect-run.py đã thu toàn bộ
run directory nên không cần thêm đường archive. Khi review phải đọc sidecar
mới, không chỉ các role logs cũ. Wrapper không thêm sampler hoặc request model.

Trước cặp freshcontrol+candidate trong NEXT_H100_CONFIRMATION.md: thu terminal
cả ba job cũ và reconcile ownqueue/credit, review quality/runtime/long như policy.
Nếu vẫn cần bổ sung quan sát, copy HAI file này vào CẢ HAI bundle mới, giữ đúng
cùng bản/hashes, review toàn bộ source và tạo lại SHA256SUMS. Không dùng staging
này để sửa bundle đã queued. Chưa chọn candidate, chưa có hai bundle hoàn chỉnh.
Dùng cùng logging trên hai nhánh để tránh thay đổi quan sát chỉ ở candidate.

Kiểm tra cuối: 12/12 ca CPU với fake pbsdsh/container, không gọi scheduler/GPU:
stdout+stderr/argv nguyên dạng, mode0600, exit23, log unique, fail khi thiếu thư
mục, reject prefix tương đối, giữ umask/SIGTERM, mapping offset của hai prefill,
decode và aux. Bản đầu 11 ca đạt; review thêm phát hiện umask077 sẽ truyền xuống
command nên đã khôi phục umask và thêm ca kiểm, giữ cả hai thư mục evidence.
Không suy kết quả CPU thành PBS fd propagation thực, MNNVL census8rank, dtypeKV,
startup/performance/accuracy. Lần allocation được phép tiếp theo vẫn phải xác
minh log rank thực, NIXL/pair warmup, resolvedServerArgs và KV hiệu dụng; nếu
thiếu thì gate runtime còn thiếu. Không chạy job riêng chỉ để thử logging.

Evidence: `../../inspection/wake-20261016-1055UTC/logging-cpu-v2/validation.json`.
Provenance và SHA256SUMS trong thư mục này; đây không phải một PBS bundle để gửi.
