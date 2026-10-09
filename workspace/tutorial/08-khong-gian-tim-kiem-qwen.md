# Không gian tối ưu Qwen có bao nhiêu chiều?

**Đợt mới theo yêu cầu “thử hết”:** đã xác định 17 topology và bốn mức concurrency mỗi topology,
tức **68 điểm sàng lọc dự kiến**. Ba biến độc lập trong tập này là số GPU prefill,
TP prefill và TP decode; cộng concurrency thành bốn biến. Số worker được suy ra,
decode EP bằng TP. Các tổ hợp phải chia hết GPU và vừa node nên không phải Cartesian
product đầy đủ. Xem [quy trình và kết quả đợt 17 topology](09-thu-het-topology-qwen.md).
Phần “vòng đầu” bên dưới mô tả lịch sử trước đợt này, không phải giới hạn thử nghiệm hiện tại.

Không có một số chiều cố định trước khi chọn những biến nào cho phép thay đổi. Nếu gom thành nhóm quyết định, có thể dùng **8 trục chính** dưới đây. Mỗi nhóm lại chứa nhiều flags; một số lựa chọn là số, một số là loại backend/framework.

| Trục | Ví dụ lựa chọn | Đã khảo sát ở vòng đầu? |
|---|---|---|
| Engine và version/build | SGLang, vLLM, TensorRT-LLM; image/version | Chỉ dùng một image SGLang |
| Topology và placement | Bao nhiêu GPU P/D; bao nhiêu worker; ở node nào | So 07/09, đều 8P+8D |
| Parallelism | TP, EP, DP, PP của mỗi worker | TP prefill thay theo topology; decode cố định |
| KV precision | BF16 hoặc FP8 phù hợp backend/luật | Chưa đổi; dùng auto theo image |
| Compute/communication backend | Attention, MoE GEMM, trao đổi experts | Chưa tune; giữ lựa chọn của image |
| Scheduling, batch và bộ nhớ | Prefill chunk, max running, memory fraction, graph coverage | Giữ flags như kit |
| Routing và KV transfer | Chính sách chọn workers, NIXL, các đường IB | Dùng routing mặc định và NIXL; sửa readiness/warmup |
| Tải client | Concurrency N | Đã thử 16,32,64 |

## Vòng đầu thực sự là không gian 2 chiều

Mình đóng gói số worker và TP prefill thành lựa chọn topology, nên vòng đầu có hai biến:

```text
                  Concurrency N
                  16       32       64
Topology 07       đo       đo       đo
Topology 09       đo       đo       đo
```

**2 topology ×3 concurrency =6 điểm khác nhau.** Lượt đo dài N32 hoặc chạy lại để sửa lỗi không tạo thêm điểm config nếu deployment/flags/N không đổi. Thời lượng, warmup và trạng thái cache vẫn là điều kiện đo phải ghi lại.

Theo cách đếm từng flag, vòng này đồng thời thay số worker P và TP của P. Nhưng chúng không độc lập: với 8 GPU prefill và worker cùng TP, số worker ×TP =8. Vì vậy mình khảo sát một biến topology tổng hợp, chưa phải đo tách riêng đóng góp từng flag.

## Vì sao không quét hết mọi tổ hợp?

Ví dụ minh họa: cho mỗi trục 3 lựa chọn, 8 trục đã có **3⁸ =6561 tổ hợp**. Nếu mỗi job mất 10 phút và chạy tuần tự, riêng thời gian chạy đã khoảng **45,6 ngày**, chưa tính queue. Đây là phép tính minh họa, không phải số config thực đã xác định.

Nhiều tổ hợp còn không hợp lệ hoặc không chạy được:

- Tổng tài nguyên phải phù hợp 16 GPU và layout P/D.
- Một số backend không hỗ trợ cùng KV dtype/TP/model/version.
- Bộ nhớ cần đủ weights, KV và graph buffers.
- Precision/thuật toán phải tuân thủ luật, chất lượng phải được kiểm tra.

Vì vậy cách làm là **cố định phần lớn biến, đo vài lựa chọn có lý do**, rồi dùng logs/profile chọn trục tiếp theo. Đây là tìm kiếm có điều kiện, không mặc định quét toàn bộ Cartesian product.

Ví dụ hiện tại: 09/N32 đạt SLA, N64 trượt. Thử N40/N48 sẽ thu hẹp trục tải client trước khi có bằng chứng cần thay cả engine hoặc phân chia GPU.

Cập nhật sau khi đối chứng hoàn tất: 07/N32 job 22197 đạt **1297,02 good tokens/s, 97,24% request đạt SLA**. 09/N32 đạt **1472,73, 97,84%**; cao hơn 13,55% trong hai lượt đo dài này, chưa phải kết quả đo lặp nhiều deployment. Đã gửi job **22200** thử 09/N40 và 09/N48, rồi đo dài mức tốt nhất qua SLA. Nếu cả hai điểm hoàn tất, số tổ hợp khác nhau đã đo sẽ tăng từ 6 lên 8; vẫn chỉ mở hai trục của vòng này.

Các khả năng kỹ thuật trong bảng là nhóm research, không phải mọi tổ hợp được xác nhận hoạt động trên image hiện tại. Xem [danh sách ứng viên](06-ung-vien-qwen.md) và [luật chính thức](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md).
