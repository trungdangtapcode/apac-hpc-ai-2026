# 2. Gửi job GPU đầu tiên

Mục tiêu: thấy chương trình chạy trên compute node, thấy GPU và tính một phép cộng bằng PyTorch. Bài này không load model và không phải benchmark tính điểm.

## Bước 1: đứng đúng thư mục

```bash
cd ~/workspace/tutorial
mkdir -p runs container-home
hostname
```

Lúc này `hostname` là tên login node. `runs/` phải tồn tại **trước** khi gửi job: Slurm cần mở file log ngay khi job bắt đầu.

## Bước 2: xem script

```bash
cat examples/hello-gpu.sbatch
cat examples/hello_gpu.py
```

Các dòng quan trọng:

| Dòng | Ý nghĩa |
|---|---|
| `#SBATCH --partition=hpcai` | Chọn partition giống kit mẫu BTC |
| `#SBATCH --nodes=1` | Xin một compute node |
| `#SBATCH --ntasks=1` | Một task |
| `#SBATCH --gres=gpu:1` | Xin một GPU trên node |
| `#SBATCH --time=00:05:00` | Giới hạn tối đa 5 phút chạy, không tính thời gian đợi queue |
| `#SBATCH --output=runs/%j.out` | Stdout; `%j` được thay bằng Job ID |
| `#SBATCH --error=runs/%j.err` | Stderr; có thể chứa cả log thông tin, không chỉ lỗi |

Giới hạn thời gian không bắt job phải chạy đủ 5 phút. Chương trình xong thì job kết thúc sớm.

Trong script, `SLURM_SUBMIT_DIR` là thư mục bạn đứng lúc gọi `sbatch`, nên cần `cd ~/workspace/tutorial` như trên. `SLURM_JOB_ID` là mã Slurm cấp tự động.

## Bước 3: gửi job

```bash
sbatch examples/hello-gpu.sbatch
```

Ví dụ Slurm trả `Submitted batch job 12345`. **12345 chỉ là ví dụ**; dùng mã thật của bạn trong các lệnh sau.

## Bước 4: xem trạng thái

```bash
squeue -u "$USER"
```

- `PD`: đang chờ; xem cột lý do. Chưa phải lỗi chương trình.
- `R`: đang chạy.
- Job không còn trong `squeue`: kiểm tra lịch sử, vì nó có thể đã xong hoặc thất bại.

```bash
sacct -j 12345 --format=JobID,JobName,State,ExitCode,Elapsed
```

`COMPLETED` và `0:0` thường là thành công về thực thi. Với benchmark thật, còn phải xem chất lượng và SLA, không chỉ exit code. Dữ liệu `sacct` có thể cập nhật chậm một chút.

## Bước 5: đọc kết quả

```bash
cat runs/12345.out
cat runs/12345.err
```

Hoặc theo dõi khi đang chạy:

```bash
tail -f runs/12345.out runs/12345.err
```

`Ctrl+C` ở đây chỉ dừng **xem log**, không hủy job. Khi job còn chờ queue, file log có thể chưa tồn tại.

Trong `.out` mong đợi có tên compute node, thông tin `nvidia-smi`, `CUDA available: True`, và kết quả `[2.0, 3.0, 4.0]`. Đây là kết quả mong đợi; bài tập chưa được chạy kiểm chứng trên GPU.

## Bước 6: nếu muốn hủy

```bash
scancel 12345
```

Hủy đúng Job ID của mình, kể cả khi đang chờ hoặc đang chạy.

## Sau bài đầu: tiến tới benchmark Qwen

Bộ mẫu BTC đã được copy vào `~/workspace/qwen-trials`. Chạy từng bước, đọc logs và xác nhận thành công rồi mới sang bước sau:

```bash
cd ~/workspace/qwen-trials
sbatch 01-smoke-image.sbatch
# Xem logs: container/GPU/import có hoạt động không?

sbatch 02-smoke-serve.sbatch
# Xem logs: server Qwen nhỏ có trả health thành công không?

sbatch 03-smoke-serve-aiperf.sbatch
# Xem logs: benchmark client có gọi server được không?
```

Đây là các lệnh riêng cho các bước khác nhau, đừng dán cả khối để chạy đồng thời.

Sau khi đường đi cơ bản hoạt động, script `07-pd-235b-8plus8.sbatch` là ví dụ model thật dùng hai nodes/16 GPU. Nó có benchmark rút ngắn và quét concurrency, chưa phải lệnh chấm chính thức mới nhất. Đọc script và quy định trước khi dùng.

AIPerf đóng vai người dùng gửi request tới server Qwen, đo tốc độ và độ trễ rồi ghi kết quả. `sbatch` chỉ đưa cả quy trình ấy lên compute nodes; nó không tự gửi bài lên leaderboard của BTC.
