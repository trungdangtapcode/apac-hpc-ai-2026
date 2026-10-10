# Vì sao job mình chờ lâu dù job mới của đội khác được chạy?

Slurm trên cluster này không xếp hàng chỉ theo thời gian submit. Nó xét priority, tài nguyên cần cấp và khả năng lấp các khoảng trống.

## Kiểm tra thực tế lúc 11:51 UTC, 10/10/2026

| Quan sát | Kết quả |
|---|---|
| Priority của bốn job mình | 188 |
| Priority job 22380 của đội khác, đang chạy g1 | 3962 |
| Priority job 22381/22382 của đội khác, đang chạy g4 | 1509 |
| Trọng số thời gian chờ | `PriorityWeightAge = 0` |
| Trọng số fair-share | `PriorityWeightFairShare = 10000` |
| FairShare của tài khoản mình | 0,018868 |
| Tài nguyên mỗi job benchmark của mình | Cả g1 + g4, tổng 16 GPU, cấp node độc quyền |
| Tài nguyên đang cấp ở g4 | 5/8 GPU, cho job ở partition `shared` |

**Fair-share** là cơ chế ưu tiên dựa trên tài nguyên đã sử dụng so với phần được chia. Tài khoản mình đã chạy nhiều job dùng cả hai node, kể cả những job lỗi vẫn đã chiếm tài nguyên. `sshare` hiện cho LevelFS = 0,292161, dưới 1; đây là dấu hiệu usage cao hơn phần chia tương đối ở cấp này.

`sprio` cho biết điểm priority của bốn job mình hiện đến từ fair-share; điểm age bằng 0. Vì vậy một job mới của tài khoản có fair-share cao hơn có thể vượt job mình đã chờ lâu.

Không phải cứ thấy vài GPU rảnh là job mình chạy được: mỗi topology cần đủ 16 GPU cùng lúc. Hai partition `hpcai` và `shared` cùng dùng g4, nên cần nhìn cả hai khi kiểm tra máy bận.

Job 22273 submit lúc 04:11 UTC, đủ điều kiện chạy sau dependency lúc 06:57 UTC. Tại mốc kiểm tra nó đã chờ khoảng 7 giờ 40 phút từ submit, gần 5 giờ từ lúc dependency được gỡ. Slurm chưa cho giờ bắt đầu dự kiến.

## Có sửa từ tài khoản mình được không?

Gửi lại job không làm fair-share của tài khoản tăng. Sửa tên job cũng không giải quyết việc này.
Giảm xuống một node sẽ thay đổi topology đang đo, nên không còn là phép thử đủ 16 GPU theo kế hoạch.

**Đã thử theo yêu cầu lúc 14:50 UTC, 10/10/2026:** hủy bốn job khi còn PENDING,
submit lại cùng payload và checksum: 22274 → 22414, 22305 → 22415, 22413 → 22416, 22300 → 22417.
Bốn job mới vẫn có priority 188 và `PENDING (Priority)` ngay sau submit; gửi lại chưa cải thiện ưu tiên.
Registry đã lưu ánh xạ job cũ/mới, và bộ điều phối đã chạy lại.
Trong lúc chờ trước đó, job 22273 đã hoàn tất bốn mức sweep, nâng tiến độ lên 10/17 cấu hình gốc + 1 biến thể EP2.

Cấu hình ưu tiên, trọng số age hoặc reservation thuộc quyền quản trị cluster. Nếu muốn đảm bảo có lượt chạy, cần BTC xem xét lịch cấp node hoặc cơ chế ưu tiên; tài khoản mình không tự đặt được lịch đó.

## Các lệnh xem, không làm thay đổi job

### Dòng “Nodes required for job are DOWN, DRAINED or reserved ...”

Đây là thông báo gộp nhiều khả năng. Không thể chỉ đọc dòng này rồi kết luận máy đã hỏng,
bị DRAIN hoặc có partition ưu tiên cao hơn; cần kiểm tra trạng thái node và queue.

**Kiểm tra 15:52 UTC, 10/10/2026:** g1 và g4 đều `ALLOCATED`, không có cờ DOWN/DRAIN.
Job 22434 của tài khoản apacsc11 đang dùng cả hai node trong chính partition hpcai.
`scontrol show reservation` báo không có reservation quản trị; cả hpcai và shared đều PriorityTier = 1.
Job 22414 vẫn PENDING, dependency trống, priority hiện 566. Chưa có dấu hiệu lỗi script từ thông báo này.

Kết luận kiểm tra được: hai node đang bận và job mình chưa được cấp tài nguyên.
Chưa xác định riêng quyết định giữ tài nguyên nội bộ của scheduler chỉ từ dòng reason này.

```bash
squeue -u apacsc42
sprio -u apacsc42 -l
sshare -u apacsc42 -l
squeue -t RUNNING -o '%.18i %.12u %.12P %.10M %.10l %.25N'
squeue --start -u apacsc42
scontrol show config | rg 'PriorityWeight|PriorityDecayHalfLife'
```

Usage fair-share trên cluster có chu kỳ giảm một nửa 2 ngày (`PriorityDecayHalfLife = 2-00:00:00`). Điều này không có nghĩa chắc chắn sau 2 ngày sẽ được chạy: priority còn phụ thuộc usage và job của các tài khoản khác.
