# Benchmark Qwen: API, concurrency và dataset

Đúng: job dựng API phục vụ Qwen, rồi **AIPerf đóng vai nhiều client** gửi request và đo câu trả lời streaming.

## 1. Ai chạy phần nào?

```text
Slurm cấp 2 compute node /16 GPU
          ↓
Script bật SGLang workers và gateway
          ↓
AIPerf gửi HTTP POST /v1/chat/completions
          ↓
Gateway chọn prefill → chuyển KV → decode
          ↓
Token trả về qua streaming; AIPerf ghi timing và metrics
```

Gateway là API tương thích OpenAI, chạy nội bộ trên cluster. Qwen chạy trên GPU BTC; đây không phải gọi model của OpenAI. AIPerf là chương trình client, không cần GPU.

## 2. Concurrency 32 hoạt động thế nào?

Hình dung client có **32 vị trí cho request đang chạy**:

```text
Vị trí 1: request A ─── xong → request mới ─── xong → request mới
Vị trí 2: request B ───────── xong → request mới
...
Vị trí 32: request Z ───── xong → request mới
```

AIPerf giữ tải bằng cách thay ngay request kết thúc bằng request mới. Các vị trí hoạt động độc lập. Trong một thời điểm, request có thể đang chờ queue, prefill, truyền KV hoặc decode; concurrency đếm request đang xử lý từ phía client, không phải số GPU.

Đây là **closed-loop**. Server xử lý nhanh hơn thì các vị trí được thay request thường xuyên hơn, nên hoàn thành nhiều request trong cửa sổ đo. BTC yêu cầu cơ chế này và cho đội chọn N. [Luật benchmark](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md#task-rules).

## 3. Có dataset không?

Có: **dataset synthetic do AIPerf sinh** từ các đoạn văn Shakespeare. AIPerf dùng tokenizer để tạo prompt theo độ dài cấu hình; không cần đội tự soạn từng câu hỏi. [Cơ chế sinh dataset của AIPerf](https://docs.nvidia.com/aiperf/tutorials/datasets-inputs/synthetic-dataset-generation).

Trong script đang chạy của mình, các tham số là:

| Tham số | Giá trị |
|---|---|
| Input length | 4000 token; stddev 0 |
| Output length | 200 token; stddev 0 |
| Số entry sinh sẵn | 12800 |
| Random seed | 2026 |
| Tokenizer | Qwen/Qwen3-235B-A22B-Instruct-2507 |
| Cache bust | first_turn_prefix |

Đây là các giá trị từ lệnh BTC, cũng có trong [benchmark.sh](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/benchmark.sh). Cache-bust làm thay đổi prefix của request nhằm hạn chế việc lấy lợi thế từ prefix cache trùng lặp.

**12800 là số entry tạo sẵn, không phải số request bắt buộc hoàn thành.** Trong cửa sổ đo có bao nhiêu request hoàn thành phụ thuộc tốc độ server và concurrency.

Mình đã kiểm tra artifact thật của job 22131 tại `confirm/n32/artifacts/inputs.json`: nó chứa 12800 entries. Mỗi entry có session ID và payload chat với model `qwen`, `stream=true`, giới hạn output 200, temperature 0 và `ignore_eos=true`. File này khoảng 228 MB; không cần mở toàn bộ để học cơ chế.

Payload minh họa rút gọn:

```json
{
  "model": "qwen",
  "messages": [{"role": "user", "content": "<prompt AIPerf tạo theo độ dài 4000 token>"}],
  "stream": true,
  "max_tokens": 200,
  "min_tokens": 200,
  "ignore_eos": true,
  "temperature": 0
}
```

Đo độ dài dùng tokenizer chung theo lệnh. Chat template và token đặc biệt của engine cũng phải vừa context window; không suy ra log nội bộ nhất thiết hiển thị đúng số 4000 ở mọi bước.

## 4. Vì sao trả lời streaming?

Streaming trả nội dung thành từng phần trong lúc model đang sinh. AIPerf quan sát thời điểm nhận dữ liệu để tính thời gian chờ token đầu tiên và tốc độ sinh tiếp. Một chunk mạng có thể chứa nhiều token; không đồng nhất một chunk với một token.

TTFT đo từ phía client, nên phản ánh cả thời gian queue và phục vụ request. Cùng model/GPU nhưng routing, batch hoặc truyền KV khác nhau vẫn có thể tạo độ trễ khác nhau. [AIPerf](https://github.com/ai-dynamo/aiperf) là công cụ đo hiệu năng của hệ phục vụ model.

## 5. Một lượt đo diễn ra thế nào?

| Giai đoạn trong lệnh BTC | Vai trò |
|---|---|
| Warmup 60 giây | Chạy tải trước cửa sổ tính điểm |
| Measurement 120 giây | Phát request và thu số liệu để chấm |
| Grace tối đa 30 giây | Cho request đang chạy hoàn tất |

Thời gian load model, compile và khởi tạo kết nối trước lệnh AIPerf là thời gian khác. Vì vậy tổng wall time của job dài hơn cửa sổ đo. [Protocol BTC](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md#task-rules).

Mình đọc kết quả ở `profile_export_aiperf.json` và đối chiếu log từng request trong `profile_export.jsonl`. Warmup và profiling được phân biệt trong metadata; không cộng warmup vào số liệu measurement.

Ví dụ đo thật **09/N32, job 22131**:

- 928 request hoàn thành trong phase profiling; không có request bị hủy trong phase này.
- 908 request đạt SLA → tỷ lệ **97,84%**.
- AIPerf báo goodput **7,3636 request/s** → nhân 200 thành **1472,73 good output tokens/s**.

Đọc goodput do AIPerf export; không tự thay nó bằng phép chia số request cho 120 giây, vì công cụ có cách xác định cửa sổ timing và xử lý drain. [Số liệu của job](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22131/summary.json).

Dataset prompt ở đây dùng đo tốc độ và độ trễ. Kiểm tra chất lượng đầu ra theo luật là một bước khác do BTC thực hiện. [Quy định chất lượng](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md#q1-basic-vanilla).

## 6. Có phải chỉ cần chạy hết dataset, output thế nào cũng được?

Mục tiêu hiệu năng là **hoàn thành nhiều request đạt SLA mỗi giây trong cửa sổ đo**, không phải chạy hết 12800 entries. Output phải thật sự được model yêu cầu sinh ra; không thể trả văn bản giả hoặc thay bằng model nhỏ hơn để đạt tốc độ.

Cần phân biệt hai cửa kiểm tra:

| Cửa kiểm tra | Đánh giá gì? |
|---|---|
| Performance / SLA | Request sinh 200 token nhanh đến đâu; TTFT/ITL có đạt ngưỡng không? Chữ “good” ở goodput chỉ việc đạt SLA, không xác nhận câu trả lời đúng. |
| Accuracy | Chất lượng model trên bộ benchmark của BTC; score phải ít nhất 99% score tham chiếu từ checkpoint FP8 chính thức. |

Ví dụ minh họa: nếu reference score là 80 điểm thì ngưỡng là 79,2 điểm. “99% reference” không có nghĩa 99% token hoặc câu trả lời phải giống từng chữ. BTC nói rõ so benchmark scores, không so output token-by-token; SGLang/vLLM có thể cho output hơi khác do thứ tự tính toán floating point mà không tự động vi phạm.

Quantization có thể làm thay đổi giá trị số và token được chọn, rồi ảnh hưởng các token sau. Nhưng luật không cho tự quantize lại model: **phải phục vụ checkpoint Instruct-2507-FP8 đã công bố**, không quantize bản BF16 để thay thế, không requantize xuống INT4/FP4. KV được dùng FP8 hoặc cao hơn; INT8/INT4/FP4 KV không được phép. Kernel/framework khác vẫn phải giữ phép tính của model và qua kiểm tra chất lượng.

Ngưỡng accuracy không cho phép cố ý bỏ layer/experts/token hoặc dùng xấp xỉ chỉ vì vẫn đạt 99% reference. Các kỹ thuật đó bị cấm riêng. Xem [Q1 — model và accuracy](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md#q1-basic-vanilla), [Q3 — các kỹ thuật bị cấm](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md#q3-prohibited-in-every-tier) và [Q4 — khác biệt output giữa engines](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md#q4-short-answers).

## 7. Metric nào dùng cho ngưỡng 99% chất lượng?

**Chưa có một metric accuracy duy nhất được xác định trong tài liệu công khai mình đã kiểm tra.** BTC nói dùng full-set accuracy check, gồm nhưng không giới hạn ở benchmarks trên model card và các checks của AIPerf. Luật chưa ghi rõ bộ evaluation cuối, phiên bản, lệnh/harness, hay cách gộp score và áp ngưỡng 99% cho từng benchmark hoặc tổng hợp. Không được tự giả định là MMLU-only, trung bình tất cả benchmark, BLEU/ROUGE hoặc so logits.

Model card có các benchmark như MMLU-Pro/GPQA (kiến thức và khoa học), AIME25 (toán), LiveCodeBench (code), IFEval (làm theo chỉ dẫn). Đây là ví dụ trong model card, không phải danh sách test cuối của BTC đã được xác nhận. [Model card — Performance](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507#performance).

Một metric là cách quy kết quả thành con số, chẳng hạn tỷ lệ câu đúng với bộ câu hỏi có đáp án, hoặc tỷ lệ lời giải code qua kiểm thử. Mỗi benchmark có protocol và cách chấm riêng. Số reference phải là lần BTC chạy **FP8 chính thức**, không lấy điểm BF16 in trên model card làm ngưỡng.

Nếu một score reference là 80 thì `0.99 ×80 =79.2` là ví dụ hiểu ngưỡng; ví dụ đó chưa nói BTC sẽ gộp nhiều score như thế nào. Muốn kiểm tra trước chính xác cần BTC cung cấp **evaluation script, datasets/versions, settings, reference scores và cách áp ngưỡng**.

Các job AIPerf mình đã chạy hiện chỉ xác nhận hiệu năng/SLA; 97,8% trong report là tỷ lệ request nhanh đủ chuẩn, **không phải accuracy 97,8%**. [Luật chất lượng và cách so reference](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md#q1-basic-vanilla).
