# NIXL là gì?

**NIXL = NVIDIA Inference Xfer Library**, thư viện giúp các tiến trình phục vụ model chuyển dữ liệu nhanh cho nhau. Xem [tài liệu NVIDIA](https://docs.nvidia.com/nixl/getting-started/overview/).

Trong cấu hình Qwen của mình, GPU được chia thành hai nhóm:

1. **P — prefill:** đọc prompt khoảng 4.000 token, tính dữ liệu trung gian gọi là **KV cache**.
2. **NIXL:** chuyển KV cache từ nhóm P sang nhóm D.
3. **D — decode:** dùng cache đó để sinh khoảng 200 token trả lời, không phải tính lại toàn bộ prompt.

```text
Prompt → GPU P đọc prompt → KV cache → NIXL chuyển → GPU D sinh token
```

KV cache là các tensor key/value của attention: dữ liệu model đã tính cho các token trước, giữ trong bộ nhớ để dùng khi sinh token tiếp theo. Nó khác với weights: weights là tham số cố định của model, còn cache phụ thuộc từng request.

| Thành phần | Nhiệm vụ ở đây |
|---|---|
| Slurm | Cấp node/GPU và khởi chạy job |
| SGLang | Nạp model, nhận request, điều phối và tính toán inference |
| NIXL | Chuyển KV cache giữa các worker P/D |

## Vì sao đang sửa phần này?

Ở đường truyền P/D khác TP, code tích hợp SGLang/NIXL đang chuẩn bị danh sách vùng nhớ truyền cho cả KV pool rất lớn. Đây là một nghi vấn gây bước làm nóng quá chậm; chưa chứng minh là nguyên nhân duy nhất.

Bản vá chuyển sang chuẩn bị danh sách cho các trang cache của request cần gửi. Bản vá không sửa weights hay phép tính model. 720 trường hợp kiểm tra CPU đã cho địa chỉ và lượng dữ liệu khớp code gốc; vẫn cần chạy GPU để biết truyền thành công và tốc độ thực tế.

**Trạng thái kiểm tra lúc 07:16 UTC, 10/10/2026:** job 22294 đã `COMPLETED`, chạy đủ bốn mức tải và đo dài N32. Hai đường P/D làm nóng thành công trong 0,68–0,70 giây mỗi request. Lượt đo dài đạt **1.422,96 good tokens/s, 95,87% SLA**, không có request lỗi hay bị hủy.

Bản vá đã chạy được trên GPU với topology này. Chưa kiểm tra accuracy, chưa kết luận mọi topology đều hết lỗi. Có **9/17 cấu hình gốc** và **1/3 biến thể EP2** đủ bốn lượt đo; các biến thể được đếm riêng. Bốn job tiếp theo đang chờ GPU.

Trạng thái mới nhất: [bảng phục hồi](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RECOVERY_RESULTS.md). Chi tiết kỹ thuật: [bản vá NIXL](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/README.md).

## Cập nhật 11/10/2026, 17:24 UTC

Đã đo đủ bốn mức tải cho **14/17 cấu hình gốc và 2/3 biến thể EP2**:
tổng cộng 16 cấu hình sử dụng được. Ba bản gốc TP8/EP1 vẫn không tương thích
block FP8; EP2 là biến thể được ghi riêng.

Còn `P8-TP8-EP2_D8-TP8-EP8`: job 22750 đo được N16/N32, nhưng job 22778
timeout warmup nên chưa có N40/N48. Job lỗi không được tính là hoàn thành.

Đường TP8 → TP8 cũng lập danh sách vùng nhớ cho toàn kho KV. Đang thử một
bản vá riêng, chỉ bỏ bước lập danh sách toàn kho trong layout TP8/PP1/VRAM
đồng nhất, dùng mã truyền từng request vốn có trong image. **936 kiểm tra
vùng nhớ CPU đã qua, chưa xác nhận bản vá này trên GPU.** Giả thuyết này chưa
chứng minh nguyên nhân timeout. Xem [chi tiết bản vá equal-TP](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-equal-ondemand/README.md).

Job **22809** đã gửi để đo lại cả N16/N32/N40/N48 với bản vá, đang chờ
`Resources`. Không ghép hai điểm của image gốc với hai điểm có bản vá thành
một sweep cùng serving stack. Controller sẽ gửi confirm riêng nếu job không
đủ thời gian đo dài. Log và payload các lần cũ vẫn giữ nguyên.

Kết quả đo dài tốt nhất hiện tại vẫn là job **22415**,
`P8-TP4_D8-TP8-EP8` với bản vá heterogeneous-TP: **1.912,30 good tokens/s**,
**97,44% request đạt SLA**, không lỗi/hủy request. Đây là kết quả local;
chưa có accuracy hoặc điểm chấm của BTC.


## Cập nhật 12/10/2026: đã đo đủ 17 layout sử dụng được

Job **22809 đã COMPLETED** lúc 23:18:29 UTC ngày 11/10: đủ N16/N32/N40/N48
và confirm dài N32. Bản vá equal-TP8 đã được xác nhận mount đúng SHA trong log
và phục vụ được benchmark trên GPU. N32 confirm đạt **1.507,96 good tokens/s**,
**95,38% SLA**, không lỗi/hủy. N40/N48 sweep đạt 89,50% / 86,06%, nên trượt
ngưỡng 90%; đo được không đồng nghĩa đạt yêu cầu hiệu năng.

Hiện có **14 cấu hình gốc và 3 biến thể EP2** đủ bốn lượt sweep. Ba bản gốc
TP8/EP1 vẫn được ghi là không tương thích FP8. Không tính job lỗi là đo xong.
Best vẫn là **P8-TP4_D8-TP8-EP8**, job **22415**, N48, bản vá hetero-TP:
**1.912,30 good tokens/s**, **97,44% SLA**, không lỗi/hủy, đo dài 60/120/30.
Accuracy full-set và điểm BTC chưa có.

Slide đã cập nhật với best này và kết quả job cuối; có PowerPoint, PDF và Markdown trong folder submission. Entry portable
`submit.sbatch` của gói cũ vẫn là unpatched 09/N40; payload, bản vá và log
của best mới được ghi riêng. Cần chuyển best sang wrapper portable và chạy
lại trên GPU trước khi coi entry đó đã tái hiện best mới.
