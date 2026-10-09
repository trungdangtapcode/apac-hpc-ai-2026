# Nghiên cứu tối ưu APAC HPC-AI 2026

Ngày nghiên cứu: **09/10/2026**. Luật đã cập nhật đến commit `fb0378f` ngày 07/10. Số tham chiếu của BTC và giả thuyết tối ưu được ghi riêng.

**Cập nhật thực nghiệm:** bạn xác nhận thi track Qwen. Đã đo topology 07/09 trên 16 H200; 09 có lượt đo dài đạt SLA, sweep 07 còn bị khởi tạo KV ảnh hưởng. Job 22143 lỗi gateway warmup trước benchmark; đã sửa cổng metrics và gửi lại thành 22147 để đo dài 07. Xem [kế hoạch riêng cho Qwen](../tutorial/05-ke-hoach-research-qwen.md), [danh sách ứng viên](../tutorial/06-ung-vien-qwen.md) và [báo cáo cập nhật](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RESULTS.md). Phần OpenFOAM bên dưới là tài liệu research trước đó, không có job OpenFOAM được chạy.

Đọc theo thứ tự:

1. [Qwen: cách tăng goodput trên 16 H200](01-qwen.md).
2. [OpenFOAM: cách giảm thời gian mỗi step](02-openfoam.md).
3. [Kế hoạch thử nghiệm, ưu tiên và hồ sơ cần lưu](03-ke-hoach.md).

Có [bảng theo dõi thử nghiệm](experiments.csv) và [lệnh AIPerf chính thức](official-aiperf.sh) được trích từ luật hiện hành. File AIPerf chỉ là bước benchmark, không deploy model, không thay thế job submission script.

## Khuyến nghị chính

**AI:** bắt đầu từ kit SGLang có sẵn; dựng một Basic, đo SLA, tìm concurrency tốt, rồi so sánh topology 07/09. Chỉ thử 12+4 nếu prefill thực sự nghẽn. Đừng kỳ vọng một bộ flags tối ưu cho mọi workload.

**HPC:** trên Gadi thử `scotch` trước, rồi rank count/affinity. Trên ASPIRE-2A ưu tiên sửa lỗi MPI shutdown đúng cách và đo lặp; đừng lấy chênh lệch một lần chạy làm speedup chắc chắn. Tách bước serial để tiết kiệm SU khi còn cần thử nhiều lần.

**Điểm:** mỗi task 50 điểm = Basic do giám khảo chấm 20 + Bonus 15 + performance/re-verification 15. Tối ưu Basic có lý giải và số đo cũng có thể nhận Bonus; không cần sửa thuật toán để có thêm điểm. [Luật chấm](https://github.com/hpcac/2026-APAC-HPC-AI#r4-scoring).

**Thời gian:** website vẫn ghi nộp code/slides trước 09/10. Hôm nay đã là 09/10; chưa xác nhận được giờ chốt hoặc thông báo gia hạn riêng. Đây là hạn chế thực tế khi chọn quy mô thử nghiệm, không phải xác nhận rằng vẫn còn thời gian nộp. [Lịch](https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/).

## Những gì đã kiểm tra

- Workspace có kit Qwen, bài học Slurm và log GPU test `20201`; benchmark model thật đang được lưu riêng tại `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/`. Chưa có kết quả OpenFOAM của đội.
- BTC có images SGLang/AIPerf và checkpoint FP8 tại `/scratch`; có cả image mang tên `sglang-v0.5.20.sqsh`. Tên file không đủ xác nhận version thực bên trong.
- Model index trên storage báo tensor data tổng cộng 236,416,915,456 bytes (~220.18 GiB). Đã đọc metadata/config, không load model.
- Repo mới có hướng dẫn/baseline/logs Gadi và ASPIRE-2A. Ghi chú cũ trong bản research tháng 9 về việc thiếu các file này đã lỗi thời; nay đọc trực tiếp các tài liệu mới.
- Đã đọc nguồn chính thức Qwen, SGLang, NVIDIA, bài báo DistServe và luật BTC. Tài liệu framework online có thể mới hơn image hiện cài; phải kiểm tra `--help`/version trong image trước khi dùng flags.

Kết luận hiệu năng của đội nằm trong báo cáo thực nghiệm ở trên; không coi giả thuyết tối ưu trong tài liệu research là speedup đã được chứng minh.
