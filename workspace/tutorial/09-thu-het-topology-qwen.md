# Thử hết topology trong đợt này

**CHƯA benchmark xong 17 cấu hình.** Đợt đầu dừng lúc 02:02 UTC ngày 10/10/2026 vì cả 17 job có trạng thái cuối,
nhưng chỉ 8 cấu hình có số đo, 9 lỗi trước benchmark. Đang sửa và chạy lại phần chưa đo; pilot là job 22270.
Đọc [tiến độ phục hồi đang cập nhật](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RECOVERY_RESULTS.md).
**Cập nhật 04:14 UTC:** job 22270 đã đo đủ N16/32/40/48, nâng số cấu hình gốc có benchmark lên **9/17**.
N48 đạt 1540,68 good tokens/s và 92,08% SLA trong sweep ngắn; job 22274 sẽ đo dài để kiểm tra lại.
Cả 8 kết nối P/D đã khởi tạo thành công; các kết nối chậm nhất mất 216–231 giây,
vượt timeout 180 giây của lần cũ. Số liệu đợt đầu bên dưới vẫn được giữ riêng.
Trong 8 cấu hình có số đo, 2 qua SLA ở lượt đo dài,
6 trượt ở các mức N đã thử. Điểm tốt nhất là **09/N40: 1666,01 good tokens/s, 97,82% SLA**.
Controller cũ đã tự thoát với điều kiện dừng không đủ để gọi là hoàn thành yêu cầu. Đọc
[tổng kết và phân loại lỗi](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/TOPOLOGY_REVIEW.md).

## Tại sao có job lỗi?

Có ba loại lỗi khác nhau trong đợt đầu:

- **Không chia được weights FP8 theo TP8/EP1:** một chiều expert có 1536 phần tử. Chia cho 8 còn 192,
  trong khi đường nạp FP8 hiện tại yêu cầu shard chia hết block 128. SGLang dừng trước khi nạp xong model.
  Biến thể prefill EP2 chia phần tensor của expert theo 4, còn 384, chia hết 128.
- **Trùng cổng:** job 22234 có hai tiến trình đụng cổng khởi tạo distributed, báo `EADDRINUSE`.
  Các payload phục hồi đã gán cổng riêng cho từng worker.
- **Timeout làm nóng kết nối P/D:** server đã ready nhưng prompt thử chưa nhận được câu trả lời trước hạn.
  Với 07, các kết nối mất tới 216–231 giây, nên timeout cũ 180 giây cắt quá sớm. Job 22270 đã chạy benchmark được sau khi tăng hạn.

**Cập nhật 05:17 UTC:** biến thể `P8-TP8-EP2_D8-TP4-EP4`, job 22271, đã nạp model và cả ba worker ready,
nhưng cả bước làm nóng chưa hoàn tất trước timeout client 360 giây. Job FAILED, chưa có benchmark.
Như vậy EP2 giải quyết lỗi nạp FP8, chưa giải quyết được kết nối P/D của cấu hình này.
Worker logs ghi request bootstrap/transfer bị hủy lúc client timeout; những dòng hủy này chưa chứng minh nguyên nhân ban đầu.
Hiện chưa phân biệt được khởi tạo KV quá chậm với mắc ở đường truyền TP8 sang TP4.
Job 22280 đang chờ để thử hạn 480 giây và N16/N32 trước; tăng timeout là phép thử, chưa phải bằng chứng lỗi gốc đã được sửa.
Xem [log timeout](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22271/pair-warmup.log).

Job `PENDING (Resources/Priority)` chỉ đang chờ Slurm cấp node, không phải lỗi model hoặc benchmark.

**Cập nhật 06:06 UTC:** đã có bản vá NIXL để chuẩn bị danh sách truyền theo KV của request,
thay vì chuẩn bị cho toàn bộ cache ở đường truyền khác TP. Kiểm tra CPU 720 trường hợp cho byte ranges khớp code gốc.
Đã gửi **job 22294** kiểm tra trên GPU; chưa xác nhận sửa xong. Job 22280 chỉ tăng timeout đã được thay khi còn chờ.
Ba job 22272–22274 được đặt chạy sau job kiểm tra 22294.
Đọc [giải thích bản vá và bằng chứng kiểm tra](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/README.md).

**Cập nhật 07:16 UTC:** job 22294 đã COMPLETED với bản vá, đủ bốn sweep và confirm N32.
Confirm đạt **1.422,96 good tokens/s, 95,87% SLA**, không có request lỗi hoặc bị hủy.
Hai request khởi tạo đường P/D hoàn tất trong 0,68–0,70 giây sau khi server ready.
Hiện **9/17 cấu hình gốc + 1/3 biến thể EP2** có đủ sweep, chưa thử xong toàn bộ.
Job 22272 chưa chạy được thay bằng 22305 mang bản vá; bốn job 22273, 22274, 22300, 22305 đang chờ GPU.

Bạn đã yêu cầu thử hết. Đợt này xác định **17 topology**, mỗi topology dùng đủ **16 H200 trên hai node**. Đây là toàn bộ tổ hợp trong bảng dưới; các biến như engine, KV precision và kernel backend giữ nguyên.

| GPU P + GPU D | TP của P | TP của D | Số topology |
|---|---|---|---:|
| 8 + 8 | 2, 4, 8 | 2, 4, 8 | 9 |
| 4 + 12 | 2, 4 | 2, 4 | 4 |
| 12 + 4 | 2, 4 | 2, 4 | 4 |

**P** đọc prompt, **D** sinh token. Một worker TP4 dùng 4 GPU. Số worker = số GPU của giai đoạn / TP. Decode EP bằng TP trong đợt này. Mỗi worker nằm trọn trong một node; hai giai đoạn có thể chia sẻ node nhưng mỗi worker có GPU riêng.

Ví dụ `P4-TP4_D12-TP4-EP4` là một worker P dùng 4 GPU và ba worker D, mỗi worker dùng 4 GPU. Node đầu chứa P và một D; node sau chứa hai D. Cấu hình này dành nhiều GPU hơn cho sinh token, nhưng có thể làm bước đọc prompt nghẽn.

`P8-TP8_D8-TP4-EP4` là một worker P dùng cả 8 GPU node đầu, hai worker D dùng node sau. TP lớn chia model rộng hơn và có thể tăng tốc một request, nhưng tăng lượng giao tiếp giữa GPU; phải đo mới biết.

Cấu hình 07 và 09 cũng nằm trong 17 topology, được chạy lại cùng quy trình. TP1 không nằm trong tập này vì weights checkpoint khoảng 220 GiB không vừa một H200. TP8 không dùng cho nhóm 4 hoặc 12 GPU vì không chia hết số GPU khi tất cả worker cùng TP. Chưa khảo sát worker khác TP trong cùng giai đoạn hoặc TP vượt qua hai node.

## Mỗi topology được đo như thế nào?

### EP1 → EP2 là đổi gì?

**EP = Expert Parallelism:** chia các expert của model MoE giữa các nhóm GPU.
Qwen này có 128 expert ở mỗi lớp MoE, chọn 8 expert cho mỗi token.
TP chia ma trận của một expert; EP chia danh sách expert. [Tài liệu SGLang](https://docs.sglang.io/docs/advanced_features/expert_parallelism).

Trong worker prefill vẫn dùng **8 GPU, TP8**, chỉ đổi EP:

| | TP8 + EP1 | TP8 + EP2 |
|---|---|---|
| Phân bổ expert | Một nhóm, có đủ 128 expert; mỗi expert chia tensor trên 8 GPU | Hai nhóm expert, mỗi nhóm 64 expert; mỗi expert chia tensor trên 4 GPU |
| Số phần tensor cho mỗi expert | 8 | 4 = TP/EP |
| Một chiều shard expert | 1536 / 8 = 192 | 1536 / 4 = 384 |
| Hợp block FP8 128 trong đường nạp hiện tại? | Không: 192 không chia hết 128 | Có: 384 = 3 × 128 |

Đổi EP2 để **nạp được checkpoint** với image hiện tại. EP1 không bị lỗi nói chung;
vấn đề là tổ hợp TP8/EP1 và cách chia block FP8 này.
Giữ đủ 128 expert, số expert được chọn cho token và weights gốc; đổi cách phân bố chúng trên GPU.
Số GPU prefill vẫn là 8, tổng job vẫn là 16; phần decode giữ TP4/EP4.
Đây là biến thể cấu hình nên ghi riêng, không tính là cấu hình EP1 gốc đã đo.

EP2 có thể thay đổi chi phí giao tiếp và tốc độ; phải benchmark mới biết.
Job 22294 đã chạy được với EP2 **và bản vá truyền NIXL**, chưa chạy accuracy check.

### Các bước đo

1. Slurm cấp hai node. Khởi động tất cả worker và gateway P/D.
2. Dùng gateway tạm cho từng cặp P/D, gửi prompt ngắn riêng để khởi tạo đường truyền KV. Tắt gateway tạm trước benchmark. Không dùng dataset hay seed benchmark cho bước này.
3. Thử **N16, N32, N40, N48**, mỗi mức warmup 10 giây, đo 20 giây, grace 30 giây. Đây là đo nhanh để chọn tải.
4. Chọn mức có goodput cao nhất trong các mức qua SLA và không có request bị hủy. Nếu còn đủ thời gian job, đo dài **60 giây warmup, 120 giây đo, 30 giây grace**.

Giới hạn mỗi job là 17 phút. Nếu không đủ thời gian đo dài, file `confirm-needed.txt` ghi mức N cần đo tiếp; không coi sweep ngắn là điểm đo dài. Nếu worker OOM hoặc topology không được image hỗ trợ, giữ log lỗi và ghi nguyên nhân; đó không phải điểm tốc độ 0.

Mỗi request cần TTFT ≤3000 ms và ITL trung bình ≤20 ms. Cần ít nhất 90% request đạt cả hai, tính cả lỗi trong mẫu số. Điểm so sánh là goodput ×200. Lượt trượt SLA được lưu nhưng không chọn làm điểm hiệu năng hợp lệ.

## Tôi đọc kết quả ở đâu?

- [Bảng 17 topology, job ID, trạng thái và số đo tự cập nhật](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/TOPOLOGY_RESULTS.md).
- [Kết quả phục hồi các cấu hình chưa đo](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RECOVERY_RESULTS.md).
- [Registry toàn bộ config và checksum trước submit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-sweep/registry.json).
- [Sổ tất cả lần chạy, kể cả lỗi](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RUNS.md).
- [CSV mỗi lượt đo](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/topology-experiments.csv).

Controller chạy trên login và tự gửi tiếp topology chưa gửi khi còn chỗ. Giữ tối đa 4 job chờ/chạy, thấp hơn giới hạn 5 của tài khoản. Hai node cấp độc quyền nên các benchmark của mình chạy lần lượt; thời gian chờ còn phụ thuộc job các đội khác.

Script của mỗi cấu hình được đóng băng trước submit trong `topology-sweep/<số>-<tên>/`. Job kiểm tra SHA256 trước khi chạy, rồi lưu bản sao vào `runs/<job>/submitted/`. Weights và container images vẫn dùng từ `/scratch`, không nằm trong payload được hash này. Raw logs, dataset và timing/metrics từng request được giữ; chưa lưu toàn bộ văn bản output hoặc chạy accuracy check.

Mốc trước đợt này: **09/N40 đạt 1649,27 good tokens/s, 97,81% SLA**, job 22200, đo dài 60/120/30. N48 chỉ đạt 88,17% SLA nên bị loại. Mốc này là số đo nội bộ, chưa phải điểm BTC.
