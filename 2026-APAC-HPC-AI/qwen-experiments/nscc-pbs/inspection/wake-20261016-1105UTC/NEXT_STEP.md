# Bước tiếp sau kiểm 16/10/2026 11:05 UTC

Hiện bốn job H200 pending Resources; chưa có số đo mới. Các reviewer và logging
đã chuẩn bị ở lượt trước; không chạy lại waiting-path hoặc test bất biến.

1. Khi watcher thu terminal seal mới vào runs/<job>/artifact-manifest.json,
   từ qwen-experiments chạy lệnh tương ứng, output đặt trong thư mục evidence
   MỚI của lượt thu đó (file chưa tồn tại):

   ```bash
   python3 serving-tuning-10/review-wave10.py --out /path/to/new-wave10-review.json
   python3 serving-tuning-10/review-mnnvl-n54-repeat.py --out /path/to/new-n54-review.json
   ```

   Đọc registry/attempts trước; replacement cần review tay, giữ mọi attempt.
   Wave10 so 23973/23975 với freshcontrol23974 và cả hai control cũ/mean;
   23975 long phải PASSED. Chỉ viết plan comboN54 khi toàn bộ gate POLICY đạt.
   24009 là một điểm xác nhận đã có; không third successful repeat/N56/promotion.
2. Khi existingaccess NSCC dùng được, refresh toàn bộ ownqueue + qstat -xf
   220720/220721/220722 + myprojects trước. Không login VPN/DUO mới. Nếu có
   own/R05/06 và endpoint ready, dùng collect-live-runtime.py single-shot.
   Thu từng terminal bằng collect-run.py <job>.pbs111 --stream-timeout 600,
   tuần tự và giữ mọi archive/partial/stderr; sau đó dùng
   CANDIDATE_SWEEP_REVIEW.md + review-candidate-sweep.py cho từng trial độc lập.
   Không dùng archive live06:26 như terminalseal. Review raw/protocol/quality/
   long/runtime và đối soát credit dưới budget.lock trước mọi reservation mới.
3. Nếu terminal thiếu rolelogs, bản task logging đã CPU-validated tại
   research-next/pbs-task-logging-01 là đầu vào cho CẢ freshcontrol/candidate
   theo NEXT_H100_CONFIRMATION.md. Chưa chọn candidate hay tích hợp/upload;
   không sửa payload04/05/06. Giữ mọi gate runtime/quality/credit hiện có.

Không còn bước độc lập hữu ích cần thực thi trước dữ liệu/access mới. Slot5
H200 không tự mở giả thuyết mới; giữ nguyên queue, watcher và4608SU dự trù.
