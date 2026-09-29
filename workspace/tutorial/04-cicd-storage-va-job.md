# 4. CI/CD, storage dùng chung và job đang chạy

Phần này ghi lại các câu hỏi sau khi đọc bài đầu. Thông tin cấu hình dựa trên lần kiểm tra máy ngày 27/09/2026.

## Có giống GitHub commit rồi chạy CI/CD không?

**Giống ở quy trình gửi công việc → chờ máy → chạy → xem logs.** Nhưng ở đây bạn gọi `sbatch` để kích hoạt. Git commit hoặc push không tự gửi job, trừ khi bạn chủ động thiết lập tích hợp đó.

| GitHub Actions | Slurm trên cluster này |
|---|---|
| Workflow YAML | Script `.sbatch` |
| Runner | Compute node được cấp |
| Chờ runner | Chờ tài nguyên và ưu tiên trong queue |
| Workflow chạy các bước | Job chạy các lệnh, có thể gọi `srun` |
| Logs và artifacts | File log/kết quả do Slurm và chương trình ghi |
| Trigger như push hoặc bấm Run | Gọi `sbatch` |

Slurm không tự checkout Git hay lưu toàn bộ kết quả thành artifact như một workflow đã cấu hình sẵn. Script của bạn quyết định đọc code nào và ghi kết quả ở đâu.

**Điểm dễ nhầm:** `sbatch` lưu bản script được gửi, nhưng không tự chụp lại toàn bộ các file Python mà script sẽ đọc. Nếu bạn sửa Python khi job còn chờ, lúc chạy nó có thể đọc bản mới. Muốn so sánh các lần thử rõ ràng, nên giữ riêng code/config cho từng thử nghiệm hoặc dùng một checkout cố định cho mỗi lần chạy.

## Có phải mount ổ VPS qua compute node không?

**Đúng ở ý hai bên thấy cùng file.** Kiến trúc ở đây là login node và compute nodes truy cập storage dùng chung. Compute node không cần lấy ổ đĩa từ login node của bạn.

```text
                  STORAGE DÙNG CHUNG
            code, model weights, logs, kết quả
                      /          \
                     /            \
              LOGIN NODE       COMPUTE NODES
              sửa code         đọc code và weights
              gửi job          chạy Python trên GPU
              đọc logs         ghi kết quả
```

Ví dụ:

1. Bạn lưu `~/workspace/my_run.py` từ VS Code trên login node.
2. Bạn gửi một job để chạy file ấy.
3. Slurm cấp compute node và chương trình đọc file qua filesystem dùng chung.
4. Chương trình ghi kết quả vào thư mục dùng chung.
5. Bạn mở kết quả ngay từ login node, không cần tải file từ compute node về.

`/home` trên login node đã được xác minh là BeeGFS. Kit BTC dùng các đường dẫn `/scratch` cho images và weights. Đó là cơ sở của các ví dụ này; không phải mọi thư mục trên mọi máy đều dùng chung.

## Code, weights và thư viện ở đâu?

| Loại dữ liệu | Vị trí trong môi trường này |
|---|---|
| Code và scripts của bạn | `~/workspace/` |
| Model weights BTC chuẩn bị | `/scratch/models/` |
| Image chứa môi trường chạy | `/scratch/enroot-images/` |
| Kit scripts gốc BTC | `/scratch/reference-scripts/` |
| Bản copy để bạn thử và sửa | `~/workspace/qwen-trials/` |
| Logs/kết quả của scripts mẫu | `~/workspace/qwen-trials/runs/` |

Checkpoint lớn đã có tại:

```text
/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8
```

Không cần tải lại checkpoint cho mỗi job. Khi khởi động, chương trình đọc weights từ ổ dùng chung và nạp chúng vào bộ nhớ để tính toán trên GPU.

```text
Weights trên ổ đĩa → chương trình load model → weights trong bộ nhớ GPU
        vẫn còn                             giải phóng khi job kết thúc
```

Đây là bài inference: model dùng weights để trả lời, không tự huấn luyện hoặc cập nhật weights chỉ vì bạn chạy benchmark. Kết quả thường là log, số đo throughput/latency và file JSON.

## Container có thêm một lớp mount

Compute node nhìn thấy file chưa có nghĩa container tự thấy mọi đường dẫn ấy. Script dùng `--container-mounts` để đưa thư mục cần thiết vào container.

```text
Storage dùng chung
       |
       v
Compute node nhìn thấy thư mục
       |
       | --container-mounts
       v
Container nhìn thấy code/model và chạy Python
```

Ví dụ `--container-mounts=/scratch:/scratch` có nghĩa là đưa `/scratch` bên ngoài vào đường dẫn `/scratch` bên trong container. Hai tên đường dẫn có thể khác nhau; ví dụ tutorial đưa thư mục bài học vào `/tutorial`.

Container cung cấp môi trường thư viện. Mount cung cấp quyền truy cập đường dẫn theo quyền hiện có của bạn. Mount không tự sao chép cả checkpoint và cũng không cấp thêm GPU.

## Job xong thì thứ gì còn, thứ gì mất?

| Thứ đang dùng | Sau khi job kết thúc |
|---|---|
| Tiến trình Python/server thuộc job | Dừng |
| Bộ nhớ GPU mà tiến trình sử dụng | Được giải phóng |
| Weights nguồn trong `/scratch/models/` | Vẫn trên ổ đĩa |
| Code và kết quả đã ghi vào thư mục dùng chung | Vẫn còn, theo chính sách lưu trữ của cluster |
| File trong `/tmp` hoặc lớp ghi tạm của container | Không nên dựa vào để giữ kết quả |

`/tmp` thường riêng từng máy. `/scratch` dùng chung cũng không đồng nghĩa được lưu vĩnh viễn hoặc có backup. Với bài tập, ghi kết quả vào thư mục workspace của mình như scripts mẫu.

## Job chạy rồi có SSH vào được không?

Một số cluster cho SSH vào compute node được cấp, nhưng **chưa xác minh chính sách SSH của BTC ở đây**. Không cần SSH để đọc logs: logs nằm trên thư mục dùng chung.

Nếu cần shell để kiểm tra trong allocation đang chạy, Slurm có cơ chế mở một job step tương tác, ví dụ:

```bash
srun --jobid=12345 --overlap -N1 -n1 --pty bash
```

`12345` là ví dụ, phải thay bằng Job ID đang chạy của chính bạn. Đây là cú pháp minh họa, chưa thử trong allocation thật tại cluster này; việc chạy được còn phụ thuộc chính sách và tài nguyên job.

- Lệnh tạo **một shell mới** trong allocation, không gắn vào tiến trình Python đang chạy.
- Nó không tự vào đúng container của server. Python/thư viện shell nhìn thấy có thể khác server.
- Với job nhiều nodes, cần chọn đúng node nếu muốn kiểm tra một worker cụ thể.
- `--overlap` cho phép step chia sẻ tài nguyên; không tạo thêm GPU. Chạy tác vụ nặng để debug có thể ảnh hưởng benchmark.
- Gõ `exit` để thoát shell mới. Khi allocation kết thúc, shell thuộc allocation cũng không được giữ máy tiếp.

Khi mới học, đọc `.out` và `.err` thường đủ để biết lỗi. Chỉ cần vào shell khi thông tin trong log chưa giải thích được vấn đề.

## Một ví dụ từ đầu đến cuối

Bạn sửa script chạy Qwen trên login node. Script trỏ vào weights có sẵn và image BTC. Bạn gọi `sbatch`. Slurm chờ đủ tài nguyên rồi chạy script trên compute nodes. Các workers load model, router nhận request và AIPerf đo hiệu năng. Kết quả được ghi vào `runs/<JOBID>/`. Job kết thúc, GPU được trả lại, còn bạn đọc file kết quả từ login node để chọn lần tối ưu tiếp theo.

Đọc tiếp: [thực hành gửi job](02-thuc-hanh.md) hoặc [tra lệnh và lỗi](03-lenh-va-loi.md).
