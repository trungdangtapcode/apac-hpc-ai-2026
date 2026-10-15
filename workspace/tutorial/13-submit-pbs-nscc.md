# Dùng PBS trên NSCC thay cho Slurm ở Firmus

**Có thể submit ở NSCC.** Đã thử thực tế, job **220457.pbs111** dùng hai node,
đủ16 H100; PyTorch trong Singularity tính toán thành công trên cả16 GPU.
Đây là kiểm tra môi trường, chưa phải kết quả benchmark Qwen.

## Khác nhau cần nhớ

| Việc | Firmus hiện tại | NSCC |
|---|---|---|
| Gửi job | `sbatch` | `qsub` |
| Xem job | `squeue` | `qstat` |
| Xem queue | `sinfo` | `qstat -Q` |
| Xem node | `sinfo -N` | `pbsnodes -aSj` |
| Container | Enroot/Pyxis | Singularity |
| GPU mỗi node | 8 H200 | 8 H10080GB |
| Nơi nộp | partition `hpcai` | queue `normal`, PBS chuyển job lớn sang `aiq2` |

Hai cluster **không chung scratch**. File trên `/scratch` của Firmus không tự
xuất hiện ở NSCC, dù dùng cùng tên tài khoản. Cần chuyển model và image.

## Credit

Project thi của mình là **59010042**, được cấp **64.000 SU**. NSCC tính
**128 SU/GPU/giờ**; tương đương500 GPU-giờ, khoảng31,25 giờ chạy đủ16 GPU,
trước khi trừ các lần chạy. CPU đi kèm job GPU không tính thêm phí riêng.
[Nguồn NSCC](https://help.nscc.sg/aspire2aplus/faqs/).

Vì vậy chưa bật kiểu quét hàng loạt cấu hình ở đây. Một job16 GPU chạy tối đa
30 phút có chi phí runtime tối đa1024 SU. Kiểm tra balance bằng `myprojects`.

## Tình trạng hiện tại

- VPN rootless và SSH đã hoạt động.
- PBS đã cấp được hai node,16 H100; driver và GPU trong container đã kiểm tra.
- Đã chuẩn bị script PBS cho cấu hình round-robin, bắt đầu thận trọng ở N32.
- Tokenizer16MiB đã chuyển. Model236GB và hai image chưa chuyển.
- Script submit có preflight: thiếu file thì dừng trước `qsub`, không xin GPU.
- Chưa có điểm Qwen trên H100, chưa thay kết quả tốt nhất H200.
- Giữ nguyên các job Slurm. Job23773 vừa đo lặp N53 xong:
  **2438,47 good tokens/s, 98,88% SLA**, không lỗi request.

[Script, log từng lần thử và kế hoạch chuyển đầy đủ](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/README.md).
