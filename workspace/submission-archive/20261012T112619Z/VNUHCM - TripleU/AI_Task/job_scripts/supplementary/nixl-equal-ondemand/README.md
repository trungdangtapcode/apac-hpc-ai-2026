# Thử sửa NIXL cho topology cuối (TP8 → TP8)

## Kết quả GPU đã có — cập nhật 12/10/2026

Job **22809 COMPLETED** lúc **23:18:29 UTC, 11/10**, có xác nhận SHA của
bản vá trong worker log và thông báo bỏ full-pool dlists trên cả 8 rank
prefill. Workers sẵn sàng sau 269 giây, tất cả cặp P/D warm sau 303 giây.
Đã chạy đủ N16/N32/N40/N48 và confirm dài N32: **1.507,96 good tokens/s**,
**95,38% SLA**, 0 lỗi/hủy request. N40/N48 sweep chỉ đạt **89,50% / 86,06%**
SLA, nên không chọn hai mức đó dù đã đo được.

Bản vá đã truyền được KV và phục vụ benchmark thực tế trên GPU. Chưa xác
nhận accuracy full-set hoặc điểm BTC. Metadata `gpu_validated: false` ở
payload cũ là snapshot trước khi gửi job và được giữ nguyên; bằng chứng
sau khi chạy nằm ở `gpu-validation.json`. Những đoạn "chưa xác nhận GPU"
bên dưới mô tả thời điểm thiết kế bản vá trước job.

Toàn bộ search hiện có 14 topology gốc và 3 biến thể EP2 đủ bốn sweep;
ba bản gốc EP1 vẫn được ghi rõ không tương thích block FP8.

Job 22750 đo được N16/N32 nhưng mất khoảng 450 giây để warmup một cặp P/D.
Job 22778 timeout sau 480 giây warmup, chưa tạo số đo N40/N48. Log chưa chứng
minh chính xác thao tác nào gây chờ. Không tính job lỗi là đo xong.

Giả thuyết: chuẩn bị descriptor cho toàn bộ kho KV quá lớn. Với 2.148.119
slot và 188 vùng K/V (94 layer), đường equal-TP gốc lập 403.846.372 descriptor
cho mỗi phía trên một rank, dù request đầu chỉ dùng ít slot.

Bản vá `equal-tp8-request-descriptors-v1` chỉ áp dụng khi TP8 ở cả hai phía,
PP1, MHA, cùng danh sách layer và byte stride, VRAM, không DCP. Nó bỏ bước lập
prepared descriptor cho toàn kho. Đường `_send_kvcache_generic` có sẵn trong
image sẽ lập descriptor cho các trang của request và gộp các trang liền nhau.
Đăng ký bộ nhớ NIXL và toàn bộ mã truyền dữ liệu giữ nguyên. Weights, precision,
phép tính model, ánh xạ head và notification không đổi.

CPU: 936 trường hợp đối chiếu từng đoạn dữ liệu truyền, gồm TP8 với GQA
replication, page size 1/4/16, trang liền/rời và thứ tự ngẫu nhiên; 5 kiểm tra
layout ngoài phạm vi vẫn dùng đường gốc. Với prompt liên tục 4.000 token và
94 layer, đường mới dùng 188 descriptor. **Chưa xác nhận transport trên GPU.**
CPU không thay thế benchmark thực tế hoặc kiểm tra accuracy của BTC.

`conn.py`, diff, metadata, `geometry-test.json` và source helper tham chiếu
được lưu ở đây. Script tạo/kiểm tra nằm ở thư mục cha:

```bash
python3 build-nixl-equal-ondemand.py
/tmp/apac42-nixl-tests/bin/python test-nixl-equal-ondemand.py
```

Chạy lại đủ N16/N32/N40/N48 dưới bản vá; không trộn hai điểm N16/N32 cũ thành
một sweep cùng stack. Controller chỉ tính các điểm có transport label mới
khi đánh dấu cấu hình này hoàn thành. Cho phép tối đa hai sweep bổ sung,
vẫn giữ mọi attempt và payload cũ. Lượt đo dài theo script cũ khi đủ thời gian;
nếu thiếu thời gian thì controller gửi job confirm riêng.
