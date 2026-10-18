# 3. Lệnh cần nhớ

Chạy các lệnh này trên login node, trừ phần nằm trong job script.

| Việc | Lệnh |
|---|---|
| Xem đang ở máy nào | `hostname` |
| Xem partitions và GPU | `sinfo -o '%P %a %l %D %G'` |
| Xem chính sách partition | `scontrol show partition hpcai` |
| Gửi job | `sbatch examples/hello-gpu.sbatch` |
| Xem job của mình | `squeue -u "$USER"` |
| Xem chi tiết job | `scontrol show job 12345` |
| Xem kết quả job | `sacct -j 12345 --format=JobID,JobName,State,ExitCode,Elapsed` |
| Xem log | `tail -n 80 runs/12345.err` |
| Hủy job | `scancel 12345` |

Thay `12345` bằng mã thật. Với bài tutorial, chạy từ `~/workspace/tutorial`.

## Lỗi thường gặp

**`nvidia-smi: command not found` trên login node**

Không phải phép thử xem cluster có GPU. Dùng job mẫu để kiểm tra trên compute node/container.

**Job `PD (Resources)` hoặc `PD (Priority)`**

Đang đợi tài nguyên hoặc lượt ưu tiên. Không submit thêm nhiều bản giống nhau; chúng cũng chiếm queue.

**Không có file log**

Job có thể chưa chạy. Kiểm tra `squeue`, thư mục hiện tại và việc `runs/` đã tồn tại trước lúc gửi chưa. `scontrol show job` có thể cho biết WorkDir/StdOut/StdErr khi job còn trong controller.

**`FAILED`**

Đọc `.err` và `.out`. Exit code báo thất bại nhưng thông báo trong log mới cho biết nguyên nhân. File `.err` không rỗng chưa chắc job thất bại: nhiều thư viện ghi log thường vào stderr.

**`TIMEOUT`**

Job vượt thời gian đã xin và bị Slurm dừng. Partition hpcai hiện tối đa 17 phút; không thể tự tăng vượt giới hạn bằng cách sửa script. Với model lớn cần tính cả thời gian khởi động, load weights và benchmark.

**`OUT_OF_MEMORY` hoặc `CUDA out of memory`**

RAM hệ thống và VRAM GPU là hai tài nguyên khác nhau. Xin thêm RAM không tự tăng VRAM. Xem loại lỗi trước khi sửa batch size, model hoặc cách chia GPU.

**`ModuleNotFoundError` khi chạy Python trên login node**

Python ở login node có thể khác Python trong container. Bài GPU dùng image BTC đã chuẩn bị. Cài thư viện ở login node không đồng nghĩa container sẽ có thư viện ấy.

**Code chạy được nhưng không đạt điểm benchmark**

Exit code 0 chỉ nói chương trình kết thúc thành công theo logic của script. Qwen còn cần good_request_fraction ≥ 0.90, ràng buộc TTFT/ITL và đúng workload; bài tập phép cộng không đo các điều đó.

## Có thể mở terminal tương tác trên GPU không?

Slurm có hỗ trợ chạy tương tác, nhưng allocation vẫn giữ tài nguyên khi bạn ngồi đọc hoặc quên đóng terminal. Bài hướng dẫn này dùng batch để công việc xong là trả tài nguyên. Không cần SSH trực tiếp vào `g1` hay `g4` để chạy bài tập.

## Các đường dẫn đáng nhớ

- `~/workspace/tutorial`: bài học này.
- `~/workspace/qwen-trials`: bản copy scripts để bạn thử và sửa.
- `/scratch/reference-scripts`: kit gốc BTC; tham khảo và copy, không sửa trực tiếp.
- `/scratch/enroot-images`: container images dựng sẵn.
- `/scratch/models`: model weights dựng sẵn.
- `~/workspace/2026-APAC-HPC-AI`: luật thi; ưu tiên đọc cả Addendum.
