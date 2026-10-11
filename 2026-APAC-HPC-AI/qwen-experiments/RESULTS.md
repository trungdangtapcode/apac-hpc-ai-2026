# Kết quả thử Qwen trên 16 H200

Cập nhật UTC: 2026-10-11T23:18:30.132361+00:00

**Phạm vi:** model chính thức Qwen3-235B-A22B-Instruct-2507-FP8; cùng images SGLang/AIPerf, workload 4000 input /200 output, seed 2026. Đây là benchmark nội bộ, chưa phải điểm BTC hoặc kiểm tra chất lượng.

## Trạng thái job

| Job | Mục đích | Trạng thái | Thời gian chạy |
|---|---|---|---|
| 22130 | Lần đầu lỗi tokenizer | FAILED | 00:06:16 |
| 22131 | 09: sweep và đo dài | COMPLETED | 00:13:08 |
| 22135 | 07: sweep | COMPLETED | 00:12:05 |
| 22143 | 07: lỗi cổng metrics trước khi đo | FAILED | 00:06:37 |
| 22147 | 07: lỗi worker registration trước khi đo | FAILED | 00:05:40 |
| 22197 | 07: chờ worker registration, đo dài N32 | COMPLETED | 00:10:47 |
| 22200 | 09: thử N40/N48, đo dài điểm tốt nhất | COMPLETED | 00:12:48 |

- **07:** 4 prefill worker × TP2; 2 decode worker × TP4/EP4.
- **09:** 2 prefill worker × TP4; 2 decode worker × TP4/EP4.
- `sweep`: warmup 15s /đo 30s /grace 30s, dùng để chọn concurrency.
- `confirm`: warmup 60s /đo 120s /grace 30s. 09 chọn N32 từ sweep; 07 được gửi đo thêm N32 ở job 22197 với warmup đủ 8 cặp P/D.
- SLA: mỗi request cần TTFT ≤3000ms và ITL trung bình ≤20ms; ít nhất 90% request đạt cả hai, tính cả lỗi vào mẫu số.
- Good tokens/s = giá trị `goodput` trong export ×200.

| Job | Cấu hình | Lượt | N | Request đạt chuẩn | Good tokens/s | TTFT TB ms | ITL TB ms | Qua SLA | Request bị hủy |
|---|---|---|---:|---:|---:|---:|---:|---|---:|
| 22135 | baseline07 | sweep | 16 | 82.1% | 106.66 | 1294.99 | 12.42 | Không | 14 |
| 22135 | baseline07 | sweep | 32 | 58.2% | 321.13 | 7880.47 | 15.62 | Không | 0 |
| 22135 | baseline07 | sweep | 64 | 65.4% | 1191.57 | 2792.93 | 18.01 | Không | 0 |
| 22197 | baseline07 | confirm | 32 | 97.2% | 1297.02 | 1470.29 | 16.37 | Có | 0 |
| 22131 | candidate09 | confirm | 32 | 97.8% | 1472.73 | 891.68 | 16.68 | Có | 0 |
| 22131 | candidate09 | sweep | 16 | 100.0% | 856.99 | 688.89 | 14.74 | Có | 0 |
| 22131 | candidate09 | sweep | 32 | 100.0% | 1465.35 | 939.73 | 16.57 | Có | 0 |
| 22131 | candidate09 | sweep | 64 | 67.0% | 1509.34 | 1506.80 | 18.81 | Không | 0 |
| 22200 | candidate09 | confirm | 40 | 97.8% | 1649.27 | 1246.71 | 17.14 | Có | 0 |
| 22200 | candidate09 | sweep | 40 | 91.3% | 1411.62 | 1485.59 | 17.09 | Có | 0 |
| 22200 | candidate09 | sweep | 48 | 88.2% | 1690.19 | 948.48 | 18.51 | Không | 0 |

## Nhận xét từ số đo

Ở lượt đo dài tốt nhất đã hoàn thành, 07 đạt **1297.02** good tokens/s tại N=32; 09 đạt **1649.27** tại N=40. Chênh lệch 09 so với 07: **+27.16%**.
Đây là so sánh mức tốt nhất đã thử của mỗi cấu hình; concurrency khác nhau nên không tách riêng tác động topology.
Các dòng “Không” bị loại dù throughput có thể cao. ITL/TTFT trung bình toàn bộ request dưới ngưỡng vẫn chưa đủ: ngưỡng SLA được xét từng request rồi tính tỷ lệ đạt chuẩn.

## Log và giới hạn

- [Log sweep đối chứng 22135](runs/22135.out), [log đo dài đối chứng 22197](runs/22197.out), [log ứng viên 22131](runs/22131.out).
- [Số liệu JSON kèm đường dẫn raw export, request count, lỗi và p95](comparison.json).
- Job 22130 lỗi tokenizer trước khi đo; loại khỏi so sánh. Đã sửa bằng official tokenizer ID và cache offline; không đổi weights.
- Job 22143 lỗi gateway warmup trước benchmark: các gateway trùng cổng Prometheus 29000. Đã đặt cổng riêng cho từng gateway, kiểm tra bằng parser trong đúng image và gửi lại thành 22147. Lỗi này không phải số đo hiệu năng.
- Job 22147 lỗi 503 trước benchmark: gateway healthy nhưng workers chưa đăng ký xong. Đã thêm retry có giới hạn cho lỗi no-workers, kiểm tra tình huống này trên CPU cho 8 cặp và gửi lại job 22197; job đó đã hoàn thành đo dài 07.
- Chỉ đọc export chính ở `artifacts/profile_export_aiperf.json`; không cộng trùng bản sao ở `phases/profiling/` hoặc lấy warmup làm kết quả.
- Chưa có chuỗi đối chứng lặp A/B qua nhiều deployment; startup/cache và bước khởi tạo đường truyền trước benchmark có thể khác nhau. Lượt confirm đều giữ warmup 60s và thời lượng đo 120s.
- Lượt sweep N16 của 07 còn chịu khởi tạo các đường truyền KV: log có request chờ bootstrap và client kết thúc grace khi còn request đang chạy. Không dùng số thấp ở lượt này để khẳng định 09 tăng tốc nhiều lần; ưu tiên so các lượt confirm đã warmup.
- Cột tỷ lệ đạt chuẩn giữ nguyên giá trị từ export BTC yêu cầu. Request bị client hủy khi hết grace được ghi riêng; lượt bị hủy không được dùng để kết luận hiệu năng ổn định.
- Chưa chạy accuracy check theo yêu cầu BTC. Không suy rộng kết quả sang topology hoặc concurrency chưa đo.
