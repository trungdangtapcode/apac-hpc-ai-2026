# Bản vá truyền KV theo request

Job kiểm tra đầu tiên: **22294**, topology `P8-TP8-EP2_D8-TP4-EP4`.
Job 22271 cùng topology đã nạp model nhưng warmup timeout 360 giây, chưa có benchmark.
Job 22280 chỉ tăng timeout được hủy khi còn PENDING, chưa dùng compute; payload và lịch sử giữ nguyên.

**Cập nhật 10/10/2026, 07:16 UTC:** job 22294 đã COMPLETED, đo đủ N16/32/40/48 và đo dài N32.
Hai đường P/D làm nóng thành công trong 0,68–0,70 giây mỗi request sau khi server ready.
Lượt đo dài N32 đạt **1.422,96 good tokens/s, 95,87% SLA**, errors = 0, cancelled = 0.
N40/N48 chỉ đạt 78,64%/67,90% SLA nên không được chọn.
Đây là bằng chứng bản vá chạy được trên GPU với topology này; chưa phải accuracy check,
chưa chứng minh mọi topology khác đều hoạt động, cũng chưa vượt mốc 09/N40 1.666,01 good tokens/s.

Trong image BTC, NIXL chuẩn bị descriptor cho mọi token slot của KV cache khi đăng ký một peer khác TP.
Prefill TP8 có 2.148.119 slot và 94 lớp K/V; một source dlist có khoảng **403,8 triệu descriptor** mỗi rank.
Đó là lượng công việc khởi tạo lớn dù prompt warmup rất ngắn. Bản vá đã cho phép job 22294 hoàn tất;
chưa có đo riêng thời gian khởi tạo descriptor của code cũ để kết luận đây là nguyên nhân duy nhất của timeout.

Bản vá chỉ thay hai hàm: chuẩn bị geometry cho cặp khác TP và tạo transfer descriptor.
Nó tạo descriptor cho các trang KV của request đang truyền, và ghép các đoạn liên tiếp khi truyền toàn bộ token ở cả hai đầu.
Nếu chỉ truyền một phần KV head, vẫn giữ stride theo từng token. Địa chỉ, độ dài, GPU ID và notification giữ nguyên ngữ nghĩa.
Đường truyền hai đầu cùng TP, model weights, precision, phép tính model, SLA và workload không đổi.

Đã so sánh byte ranges với code nguyên gốc từ chính image BTC: **720 trường hợp**,
TP2/4/8 hai chiều, KV heads 4/8, page size 1/4/16, nhiều rank và các trang liên tiếp/rời nhau.
Prompt liên tiếp 4.000 token ở TP8→TP4 cần 188 descriptor; kết quả kiểm tra ở [geometry-test.json](geometry-test.json).
Đây là kiểm tra CPU về địa chỉ truyền, **chưa phải accuracy check hoặc bằng chứng NIXL hoạt động trên GPU**.

Job bind mount module đã vá vào container riêng, kiểm tra SHA256 trước khi launch server.
Image và checkpoint dùng chung không bị sửa. Source nguyên gốc đã đối chiếu SHA256 với image đang dùng.

- [Patch dạng text để review](nixl-ondemand.patch).
- [Module đã vá](conn.py), [module nguyên gốc](original-conn.py), [hash và phạm vi](metadata.json).
- [Script tạo patch](../build-nixl-ondemand.py), [kiểm tra geometry](../test-nixl-ondemand.py).
- [Tiến độ GPU và số đo](../RECOVERY_RESULTS.md).

Không đánh dấu sửa thành công chỉ vì submit hoặc worker ready. Cần warmup thực tế thành công,
có benchmark với requests > 0 và không bị client hủy. Số đo dùng bản vá được gắn tên transport patch riêng.

Pipeline chỉ áp dụng bản vá cho các topology khác TP còn thiếu số đo sau khi pilot có một sweep
4000/200 với requests > 0, errors = 0 và cancelled = 0. Nó thay các job retry chưa chạy dưới job ID mới,
giữ payload cũ; không sửa payload đã submit. Các job đã chạy và đường truyền cùng TP được giữ theo kế hoạch riêng.
Job 22272–22274 chờ pilot kết thúc qua dependency `afterany:22294`, tự được gỡ khi pilot kết thúc dù thành công hay lỗi.
