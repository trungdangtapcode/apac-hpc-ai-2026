# EAGLE3: kiểm tra source thực trong image, 16/10/2026

Chỉ nghiên cứu CPU; chưa tải draft weights, chạy model, đặt SU hay gửi job.
Đã trích source từ `/scratch/enroot-images/sglang-harbor.sqsh` bằng 2 CPU;
72 file Python được hash. `server_args.py` vừa trích khớp byte với source có hash
đã lưu ở lượt 15/10 20:07 UTC. Không rehash toàn image 26 GB trong lượt này;
đây không phải kiểm chứng lại image remote NSCC. Model/asset contract giữ nguyên.

## Điều đã xác minh ở source

- `speculative/eagle_worker_common.py:558–588`: chạy target forward với
  `is_verify=True`, rồi đưa logits target vào `eagle_sample`.
- `speculative/eagle_utils.py:723–738`: khi `sampling_info.is_all_greedy`, lấy
  `torch.argmax(next_token_logits)`, gọi greedy tree verifier với draft candidates
  và target token IDs. Nhánh này không truyền acceptance thresholds; hai threshold
  xuất hiện ở nhánh sampling bên dưới. Giữ 1.0 trong thiết kế, nhưng không coi chúng
  là bằng chứng đủ cho mọi sampling mode.
- `eagle_utils.py:371–438`: trên CUDA, dispatcher gọi compiled
  `sgl_kernel.verify_tree_greedy`. Source Triton fallback có trong evidence nhưng
  không phải bằng chứng cho thực thi CUDA. Chưa kiểm kernel native hoặc chạy GPU;
  chưa chứng minh từng token output thực tế giống nonspeculative control.
- `eagle_utils.py:839–871`, `spec_utils.py:389–431`: nếu
  `SGLANG_SIMULATE_ACC_LEN > 0`, simulation thay acceptance sau verifier thật.
  Chế độ `fixed` điền token ID 100; `real-draft-token` ép nhận token draft.
  `environ.py:347` mặc định -1. Thử nghiệm thật phải đặt rõ -1 và ghi giá trị
  hiệu lực bên trong container, từng worker; không dùng kết quả mô phỏng để
  kết luận chất lượng hay tốc độ serving thật. Không có bằng chứng các run cũ
  đã bật simulation; đây là gate cho nhánh EAGLE3 tương lai.
- `arg_groups/speculative_hook.py:540–544,658–665`: nếu không đặt trước,
  EAGLE family đặt max_running_requests=48; topk1 ép draft_tokens=steps+1.
  Thiết kế 3steps/topk1/4tokens nhất quán. Control nonspeculative và candidate
  cần cùng max_running_requests=48, để tránh thêm confounder do default này.
  Hook hiện dùng worker V2; env `SGLANG_ENABLE_SPEC_V2` cũ chỉ còn cảnh báo.
- `models/qwen3_moe.py:1073–1088` có API capture auxiliary hidden states cho
  EAGLE3; explicit layer IDs được chuyển +1. Draft config đã lưu dùng [1,46,90].
  Có API không chứng minh đúng hidden states/shape/token map cho target
  Instruct-2507-FP8; vẫn cần kiểm runtime. Không tự sửa layer IDs/checkpoint.

## Bước thử tiếp theo đã làm rõ

Backend pilots NSCC04→05 và loader06 giữ ưu tiên hiện có. EAGLE3 vẫn DESIGN_ONLY;
không tạo một job H200/PBS mới hay tự lấy slot trống trong lượt này.

Khi đủ quyền truy cập và gate budget/queue, trước hết xác minh draft revision,
weights/token map và memory; chạy monolithic8GPU cùng target FP8, BF16KV,
context8192, memory0.75. Control và candidate cùng max_running_requests48,
flags attention/graph/seed/sampling tương ứng; lưu resolved args vì speculative
mode có thể thay các default khác. Chỉ dùng request greedy temperature0,
repetition_penalty1, không additive penalty/logit_bias/grammar trong phép đối soát
đầu tiên. Không trộn request sampling vào batch kiểm này.

Ghi token IDs thật từ engine cho short/long prompts, gồm boundary và trường hợp
EOS, request settings, target revision, runtime/config/env cùng acceptance length
thật. Đối chiếu từng token với control và điều tra mọi khác biệt; không suy từ
text trông giống hoặc từ API source mà kết luận lossless. FP8/batch/kernel có thể
đổi số học giữa verify và decode thường. Không khẳng định ngưỡng1.0 bảo đảm
phân phối sampling tương đương. Sau chất lượng mới đo full60/120/30 ở cùng tải;
không so trực tiếp monolithic8GPU với goodput PD16GPU. Accuracy BTC vẫn chưa xác minh.

Bằng chứng: [source review JSON](../../inspection/wake-20261016-0055UTC/eagle-source-review.json),
[source audit CPU](../../inspection/wake-20261016-0055UTC/audit-eagle-source.py).
12 kiểm tra cấu trúc source đạt; không phải 12 ca output hoặc GPU test.
