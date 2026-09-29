# 1. Tại sao không chạy nvidia-smi rồi python luôn?

## Bạn đang ngồi ở đâu?

Bạn gọi máy BTC cấp là VPS. Phần mình kiểm tra được: shell hiện tại nằm trên **login node** tên `login.hpcai2025.smc`. Chưa xác định máy này là máy ảo hay máy vật lý; điều quan trọng là vai trò của nó trong cluster.

Login node là nơi đăng nhập, sửa code, chuẩn bị file và gửi lệnh. GPU nằm trên các **compute nodes** khác: cấu hình Slurm hiện liệt kê `g1` và `g4`, mỗi máy có 8 H200.

```text
Bạn / VS Code / trợ lý
          |
          v
login.hpcai2025.smc       viết code, gửi job, đọc logs
          |
          | sbatch: gửi yêu cầu cho Slurm
          v
       Hàng đợi           đợi tài nguyên và lượt chạy
          |
          | Slurm cấp tài nguyên rồi khởi chạy job
          v
    g1 và/hoặc g4         chạy container, Python, model trên GPU
          |
          v
     File kết quả        bạn mở lại từ login node
```

`hostname` cho biết shell đang chạy trên máy nào. Python chạy ở máy chứa tiến trình Python; file code nằm trên ổ dùng chung không khiến Python tự chuyển sang máy GPU.

## nvidia-smi không phải nút xin GPU

`nvidia-smi` xem GPU mà **máy và môi trường hiện tại nhìn thấy**. Nó không xin tài nguyên, không kết nối sang compute node và không đặt chỗ GPU.

Khi kiểm tra login node này, mình không thấy lệnh `nvidia-smi` trong PATH và không thấy thiết bị `/dev/nvidia*`. Điều đó không có nghĩa cluster không có GPU: Slurm vẫn thấy 16 H200 trên hai compute nodes.

Vì vậy:

```bash
python3 my_program.py
```

chạy trên login node nếu bạn gõ tại đây. Đọc CSV nhỏ, sửa file hay phân tích JSON kết quả có thể làm ở đây; inference Qwen lớn cần tài nguyên compute được cấp qua Slurm.

Sau khi Slurm đã cấp tài nguyên và đưa chương trình lên compute node, **bạn vẫn chạy nvidia-smi và Python bình thường**, thường bên trong container của BTC. Slurm chỉ quản lý nơi chạy, tài nguyên và thời gian; nó không thay Python.

## Slurm làm việc gì?

Nhiều đội dùng chung hai máy GPU. Slurm nhận yêu cầu, xếp hàng, cấp máy/GPU, giới hạn thời gian và thu hồi tài nguyên khi job kết thúc.

- **Node**: một máy trong cluster.
- **GPU**: thiết bị tính toán trên máy đó; một node ở đây có 8 GPU.
- **Job**: một lần yêu cầu tài nguyên và chạy công việc.
- **Job ID**: mã của lần chạy; dùng để xem trạng thái, logs hoặc hủy.
- **Partition**: nhóm tài nguyên cùng chính sách, ở đây có `hpcai` và `shared`. Không suy ra chính sách chỉ từ tên.
- **Task**: một đơn vị tiến trình mà Slurm khởi chạy; không đồng nghĩa với GPU.
- **Job step**: một lần chạy lệnh qua `srun` bên trong job.

Partition `hpcai` hiện có giới hạn 17 phút/job và `OverSubscribe=NO`, `Exclusive=NODE`. Vì vậy yêu cầu 1 GPU không có nghĩa các đội khác chắc chắn được dùng 7 GPU còn lại trên node ấy. Phải xét chính sách partition. Bài tập ở đây dùng `hpcai` giống script mẫu BTC.

## sbatch, srun và bash khác nhau thế nào?

```bash
sbatch examples/hello-gpu.sbatch
```

Gửi job vào hàng đợi. Lệnh thường trả Job ID ngay; chương trình có thể chưa chạy. Slurm đọc các dòng `#SBATCH` để biết tài nguyên cần cấp. Sau khi job đã được nhận, đóng terminal thường không làm job batch dừng.

Trong script, `srun` khởi chạy chương trình bằng tài nguyên job đã được cấp. Một job có thể có nhiều bước: chạy server, router rồi benchmark client.

```bash
bash examples/hello-gpu.sbatch
```

Không tương đương `sbatch`: Bash coi `#SBATCH` là comment và không gửi các yêu cầu đó. Nếu script có `srun`, lệnh này có thể tự xin allocation theo tham số riêng, nhưng sẽ không tự kế thừa các dòng `#SBATCH` mà Bash bỏ qua. Hãy dùng đúng `sbatch` cho bài tập.

## Container và ổ đĩa

BTC đã chuẩn bị môi trường chạy trong các file `.sqsh` tại `/scratch/enroot-images/`. Container chứa thư viện như SGLang/PyTorch; model weights nằm riêng tại `/scratch/models/`.

Script dùng `srun --container-image=...` để khởi chạy trong môi trường ấy. `--container-mounts` làm thư mục code, model và kết quả bên ngoài xuất hiện bên trong container. Không phải copy hoặc cài lại model cho mỗi lần thử.

Thư mục `/home` của phiên này nằm trên filesystem BeeGFS dùng chung; kit mẫu cũng dựa vào các đường dẫn shared `/scratch`. Trong container, vẫn phải mount đường dẫn cần dùng. File dùng chung và GPU là hai thứ khác nhau.

`~/workspace` dùng để giữ code, scripts, logs. Không cần tải lại checkpoint 235B đã có sẵn.
