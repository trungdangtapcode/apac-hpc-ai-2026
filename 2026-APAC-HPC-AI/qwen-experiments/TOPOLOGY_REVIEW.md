# Tổng kết đợt 17 topology Qwen

**Đính chính: CHƯA đo xong 17 cấu hình.** Chỉ 8 cấu hình có benchmark; 9 cấu hình chưa có số đo.
Việc 17 job có trạng thái cuối không có nghĩa nhiệm vụ đo 17 cấu hình đã hoàn thành.
Đang sửa lỗi và chạy lại; pilot 07 là **job 22270**. Các số liệu bên dưới là đợt đầu.
Theo dõi [số đo chạy lại](RECOVERY_RESULTS.md). Pipeline phục hồi chỉ đánh dấu đã đo khi có đủ
bốn export sweep với request thực tế và không bị client hủy; job FAILED/TIMEOUT không đủ.
Ba cấu hình prefill TP8/EP1 lỗi block FP8 được ghi không tương thích với image/flags gốc;
biến thể dùng prefill EP2 có tên và kết quả riêng, không tính giả thành bản gốc đã benchmark.

Cập nhật phục hồi lúc 04:10 UTC: job 22270 đã khởi tạo thành công cả 8 đường P/D.
Bốn đường mất 216–231 giây, vượt timeout client cũ 180 giây. Đây là bằng chứng timeout cũ
cắt sớm ở các đường đó; chưa đủ để kết luận toàn bộ chín lỗi đã được giải quyết.
Xem [log warmup chạy lại](runs/22270/pair-warmup.log) và số đo ở trang phục hồi.

Cập nhật 05:17 UTC: job 22271 (biến thể prefill TP8/EP2, decode TP4/EP4) đã nạp model thành công,
nhưng warmup client timeout 360 giây, kết thúc FAILED lúc 05:01:54 UTC, chưa có số đo.
EP2 đã tránh lỗi block FP8; đường bootstrap/transfer P/D chưa được chứng minh hoạt động.
Worker logs ghi AbortReq/abort notification khi client hủy request; chưa xác định nguyên nhân ban đầu.
Job 22280 thử tiếp với timeout 480 giây và N16/N32, hiện chờ tài nguyên.
Xem [log client warmup](runs/22271/pair-warmup.log), [prefill](runs/22271/prefill-0.log), [decode](runs/22271/decode-0.log).

Kiểm tra lúc 03:12 UTC ngày 10/10/2026. Tất cả 17 job đã kết thúc; job cuối kết thúc lúc **02:02:15 UTC**. Queue của tài khoản trống. Controller tự thoát bình thường sau khi tất cả job có trạng thái cuối, không bị treo.

| Kết quả | Số cấu hình | Ý nghĩa |
|---|---:|---|
| Có số đo và confirm qua SLA | 2 | Có phép đo dài 60/120/30 hợp lệ, cancelled=0 |
| Có số đo, trượt SLA ở cả bốn mức N | 6 | Đã thử N16/32/40/48; chưa tìm được mức đạt 90% |
| Lỗi trước benchmark | 9 | Có log deploy/warmup, chưa có điểm hiệu năng |

Tổng cộng **34 lượt đo hoàn thành**, gồm 32 sweep và 2 confirm. Cả 17 job có manifest checksum cho artifacts đã lưu. Đọc [bảng đầy đủ](TOPOLOGY_RESULTS.md), [registry](topology-sweep/registry.json) và [sổ các lần chạy](RUNS.md).

## Hai điểm đo dài hợp lệ

| Topology | Job | N | Good tokens/s | Request đạt SLA | TTFT TB ms | ITL TB ms |
|---|---|---:|---:|---:|---:|---:|
| 09: P8-TP4_D8-TP4-EP4 | 22219 | 40 | **1666,01** | **97,82%** | 1229,46 | 17,11 |
| P4-TP4_D12-TP4-EP4 | 22231 | 40 | 1382,16 | 97,40% | 2399,38 | 15,74 |

09/N40 vẫn là điểm đo dài tốt nhất đã có. So với lượt trước ở job 22200 (1649,27), lượt này cao hơn khoảng **1,02%**; chênh lệch nhỏ này chưa chứng minh có cải tiến vì cùng topology và chưa phân tích độ dao động.

P4+D12 có sweep N40 đạt 1641,19 nhưng confirm chỉ 1382,16. Vì vậy dùng confirm khi so điểm dài; không lấy số sweep cao hơn thay cho confirm. Cả hai đều dùng đúng model FP8, 16 H200 và workload 4000/200; chưa chạy accuracy check hoặc nhận điểm BTC.

## Chín job chưa có điểm hiệu năng

| Nhóm quan sát từ log | Job | Bằng chứng và giới hạn kết luận |
|---|---|---|
| Prefill TP8 lỗi nạp weights FP8 | 22221, 22236, 22238 | `ValueError`: kích thước shard gate/up là 192, không chia hết block quantization 128. Đây là lỗi của đường nạp model với cấu hình/image đang dùng, chưa đo được tốc độ TP8. |
| Trùng cổng distributed initialization | 22234 | `torch.distributed.DistNetworkError`, `EADDRINUSE`, cổng 46725 đã được dùng. Lỗi xảy ra ở prefill-1 trước khi workers ready, không phải kết quả tốc độ hoặc OOM. |
| Timeout warmup qua cặp P/D | 22220, 22222, 22232, 22240, 22245 | Workers đã ready nhưng lời gọi warmup không hoàn tất trong timeout 180 giây. Chưa xác định đầy đủ nguyên nhân; không coi đó là bằng chứng topology có goodput bằng 0 hoặc chắc chắn không chạy được. |

Bằng chứng trực tiếp:

- [Lỗi block FP8 ở 22221](runs/22221/prefill-0.log).
- [Lỗi cổng ở 22234](runs/22234/prefill-1.log).
- [Timeout warmup ở 22220](runs/22220/pair-warmup.log), [log prefill bootstrap](runs/22220/prefill-0.log).

Các dòng `srun ... Timed out waiting for job step to complete` cuối worker logs còn có thể xuất hiện khi cleanup job lỗi. Phân loại trên đọc exception ở giai đoạn đầu và warmup, không dùng riêng dòng cleanup để đoán nguyên nhân.

Đợt đầu dừng khi tất cả job đã kết thúc, trong khi **chỉ 8/17 cấu hình có số đo hiệu năng**. Đây là điều kiện dừng sai so với yêu cầu đo hết. Chín cấu hình còn lại phải được sửa/chạy lại hoặc ghi rõ không tương thích kèm bằng chứng; không đưa lỗi deploy vào số cấu hình đã benchmark. Giữ nguyên snapshots và logs của đợt đầu.
