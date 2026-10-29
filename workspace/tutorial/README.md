# Học Slurm ngay trên máy BTC cấp

**Bộ nhớ xuyên phiên:** [điểm tra cứu](../notes/README.md) · [trạng thái và đính chính hiện tại](../notes/CURRENT.md) · [quyết định](../notes/DECISIONS.md) · [các mốc lịch sử](../notes/TIMELINE.md).

**Tra cứu câu hỏi đã trao đổi:** [Sổ tay hỏi–đáp: hai cụm máy, Slurm/PBS, storage, benchmark và tối ưu Qwen](14-so-tay-hoi-dap.md). Sổ phân biệt kiến thức với trạng thái job theo ngày và được bổ sung khi có câu hỏi mới.

**Research tự chạy:** [báo cáo mới nhất](../research-autopilot/LATEST.md) · [cách hoạt động và tạm dừng](../research-autopilot/README.md).

Đọc theo thứ tự:

1. [Máy này hoạt động thế nào?](01-may-va-slurm.md)
2. [Gửi job đầu tiên và xem kết quả](02-thuc-hanh.md)
3. [Các lệnh cần nhớ và lỗi thường gặp](03-lenh-va-loi.md)
4. [Giống CI/CD không? Storage, weights và vào job đang chạy](04-cicd-storage-va-job.md)
5. [Nghiên cứu bài thi và kế hoạch tối ưu Qwen/OpenFOAM](../research-optimization/README.md)
6. [Kế hoạch research riêng cho track Qwen](05-ke-hoach-research-qwen.md)
7. [Danh sách ứng viên: config, serving engine và các bộ tăng tốc](06-ung-vien-qwen.md)
8. [Cơ chế benchmark: API, concurrency và dataset](07-co-che-benchmark-qwen.md)
9. [Không gian tìm kiếm: các trục và những biến đã thử](08-khong-gian-tim-kiem-qwen.md)
10. [Sổ từng job: thành công, lỗi, dữ kiện và bài học](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RUNS.md)
11. [Thử hết 17 topology Qwen: đọc tên cấu hình và xem kết quả](09-thu-het-topology-qwen.md)
12. [NIXL là gì? Vì sao prefill phải gửi cache cho decode?](10-nixl-la-gi.md)
13. [Vì sao job mình chờ lâu dù job mới của đội khác chạy?](11-tai-sao-job-cho-lau.md)
14. [Check Point VPN để vào NSCC: điều kiện và tình trạng máy hiện tại](12-vpn-nscc.md)
15. [Submit PBS trên NSCC: GPU, credit và chuyển từ Slurm](13-submit-pbs-nscc.md)

Có sẵn bài tập nhỏ: [script Slurm](examples/hello-gpu.sbatch) gọi [chương trình Python](examples/hello_gpu.py). Job kiểm tra GPU 20201 đã chạy thành công. Các job benchmark Qwen được ghi riêng trong kế hoạch ở trên.

Điều cần nhớ: **viết code trên login node → xin máy GPU qua Slurm → Python chạy trên máy GPU → đọc kết quả từ file.**

Các thông tin máy dưới đây được kiểm tra ngày 27/09/2026; trạng thái queue có thể thay đổi. Hướng dẫn này dành cho cluster GPU đang truy cập, không phải hướng dẫn OpenFOAM trên Gadi.

- [SSH, Slurm/PBS, MPI and OpenFOAM](hpc-openfoam-and-schedulers.md).

- [Requested workload, client-reported token counts and the fixed official multiplier](20-requested-and-reported-token-counts.md).
