# Qwen: tìm cách tăng số token trả lời đúng hạn

## 1. Bài toán bằng lời đơn giản

Một request đưa vào khoảng 4000 tokens và yêu cầu 200 tokens trả lời. Prefill đọc toàn bộ prompt; decode sinh từng token. Luật yêu cầu tách hai giai đoạn lên các workers khác nhau, chạy đủ 16 GPU và benchmark qua gateway.

```text
AIPerf → Gateway → Prefill workers → chuyển KV qua mạng → Decode workers
             ↑                                            |
             └──────────── stream câu trả lời ──────────────┘
```

TTFT là thời gian đợi token đầu tiên. Average ITL là thời gian trung bình giữa các token. Request chỉ tính là good khi **cả hai** đạt TTFT ≤3000 ms và ITL ≤20 ms. Ít nhất 90% request phải good, kể cả lỗi được tính trong mẫu số.

Metric: **good output token/s = goodput (request/s) × 200**. Tổng token/s đẹp nhưng nhiều request trễ không phải cấu hình tốt cho cuộc thi. Ví dụ minh họa: 30 good request/s tương đương 6000 good output token/s; đây không phải kết quả đã đo.

Nguồn quy định: [Qwen Task Rules và Addendum Q1](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md).

## 2. Model nhỏ về compute, lớn về storage

Model có 235B parameters, chỉ khoảng 22B active cho mỗi token; 128 experts, chọn 8 experts/token. Dù mỗi token chỉ dùng một phần experts, vẫn cần chứa toàn bộ checkpoint để xử lý mọi request. [Model card chính thức](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507-FP8).

Config và index tại `/scratch/models/...` xác nhận 94 layers, 4 KV heads, head dimension 128 và tensor data ~220.18 GiB. Vì vậy một replica TP2 có xấp xỉ 110 GiB tensor data/GPU nếu chia đều; TP4 khoảng 55 GiB. Đây là ước lượng storage, không phải tổng bộ nhớ thực tế: còn KV, activations, graph buffers, phần không chia đều và overhead.

**Suy luận cần thử:** nhiều replicas TP2 có thể tăng khả năng xử lý đồng thời nhưng lặp lại weights và giảm headroom. Ít replicas TP4 có thể cho batch lớn hơn, đổi lại thêm communication trong một replica. Không quyết định chỉ từ dung lượng GPU.

## 3. Ưu tiên A: concurrency trước

Concurrency N là số request đang được client giữ đồng thời, không phải số GPU. N thấp có thể để GPU nhàn; N quá cao tạo queue và làm request trễ SLA.

Đề xuất coarse sweep **N = 8, 16, 32, 64**, dừng tăng khi SLA thất bại rõ rệt. Nếu N16 tốt và N32 thất bại, thử N24 thay vì tiếp tục N128. Nếu N64 vẫn tốt, tăng có chủ đích. Đây là điểm khởi đầu do mình đề xuất, không phải giá trị tốt nhất đã đo.

Dùng 10–20 s benchmark để sàng lọc như luật cho phép; giữ ISL/OSL, SLAs và precision để kết quả liên quan đến bài. Short run vẫn có nhiễu và không thay full run. Không chọn chỉ bằng raw throughput: lưu good_fraction, goodput, TTFT và ITL. Khi đo exploratory, vẫn thêm `--goodput` để nhìn thấy đúng metric.

Nên chọn cấu hình có khoảng đệm về SLA và chạy lại ứng viên tốt nhất. Ví dụ đặt mục tiêu nội bộ good_fraction ≥0.95 nếu khả thi; đó là biên dự phòng do mình đề xuất, không thay threshold 0.90 của BTC.

Nghiên cứu [DistServe](https://arxiv.org/abs/2401.09670) hỗ trợ cách tiếp cận phân bổ tài nguyên và parallelism riêng theo từng giai đoạn để tối ưu goodput. Không chuyển speedup trong bài báo thành kỳ vọng tốc độ cho Qwen/H200 này.

## 4. Ưu tiên B: topology từ kit BTC

| Kit | Prefill | Decode | Tổng | Giả thuyết để đo |
|---|---|---|---|---|
| 07 | 4 workers × TP2 | 2 workers × TP4, EP4 | 8P+8D GPU | Baseline đơn giản, nhiều prefill replicas |
| 09 | 2 workers × TP4 | 2 workers × TP4, EP4 | 8P+8D GPU | Prefill rộng hơn, ít lặp weights |
| 08 | 6 workers × TP2 | 1 worker × TP4, EP4 | 12P+4D GPU | Thêm prefill nếu TTFT/queue P nghẽn và decode còn dư |

Đây là topology trong `/scratch/reference-scripts`, không phải kết quả cuộc thi của đội. Giữ cùng image, KV dtype và N khi so sánh bước đầu; sau đó tìm N tốt nhất riêng cho từng topology. N tối ưu không nhất thiết giống nhau.

Các workers của 07/09 nằm trọn một node; KV phải chuyển giữa nodes. 08 phân bố khác nên số P/D pairs và đường truyền khác. Không tăng TP qua hai nodes ngay từ đầu: phải đo communication và bộ nhớ, không mặc định nhiều GPU cho một replica luôn nhanh hơn.

Một recipe NVIDIA cũng mô tả Qwen3-235B FP8 trên 16 Hopper GPUs với PD serving. Tuy nhiên checkpoint trong recipe là Qwen3-235B-A22B-FP8, khác bản Instruct-2507-FP8 bắt buộc. Chỉ dùng làm tham khảo thiết kế; không copy model ID hoặc chuyển qua Kubernetes để chạy bài Slurm. [NVIDIA Dynamo recipe](https://docs.nvidia.com/dynamo/dev/recipes/qwen3-235b-a22b-fp8).

## 5. Ưu tiên C: precision KV và bộ nhớ

Kit không đặt rõ `--kv-cache-dtype`, nên cần xác nhận dtype thực trong logs của image. **Không suy ra KV đã FP8 chỉ vì weights là FP8.**

KV là dữ liệu trung gian dùng để tiếp tục sinh token. Với config đã đọc, một ước lượng logical KV ở FP8:

```text
2 (K,V) × 94 layers × 4 KV heads × 128 dimension × 1 byte
= 96,256 bytes/token ≈ 94 KiB/token

4000 input tokens ≈ 367 MiB/request
4200 input+output tokens ≈ 386 MiB/request
```

Đây là phép tính của mình từ config, trước scale metadata/alignment, sharding/replication, thời điểm allocation và copy ở hai phía P/D. Với BF16, phần dữ liệu này gấp đôi. Không lấy lượng logical KV chia bandwidth danh nghĩa để khẳng định bottleneck mạng: cần đo thời gian transfer thực.

Nếu image/backend hỗ trợ FP8 KV đúng cho model và đường truyền PD, thử so với BF16 ở cùng topology/N. FP8 được luật cho phép, nhưng vẫn phải đạt accuracy; không xem giảm một nửa logical storage như đảm bảo tăng gấp đôi goodput. [SGLang Quantized KV Cache](https://docs.sglang.io/docs/advanced_features/quantized_kv_cache).

Giữ context 8192 như kit làm starting point; không dùng default context 256K nếu nó tốn graph/buffer không cần thiết. Bất kỳ giảm context nào phải đủ template +4000 input +200 output, không được cắt prompt.

Về scheduling, SGLang có knobs cho memory fraction, prefill chunk, running requests và CUDA graph. Mình đề xuất chỉ thử memory fraction 0.85/0.90 sau khi logs cho thấy thiếu headroom/retractions; tăng batch limit chỉ khi ITL còn tốt. Chunk 4096 so với 8192 chỉ có ích nếu chunking/batch là bottleneck thực. Đừng dùng lời khuyên batch lớn cho offline inference một cách máy móc: workload thi có SLA. [Hướng dẫn tuning SGLang](https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning).

## 6. Chọn thay đổi theo triệu chứng

| Quan sát thực tế | Giả thuyết | Thay đổi đầu tiên |
|---|---|---|
| TTFT cao, P queue tăng, D còn nhẹ | Prefill thiếu capacity | So 07/09, rồi 12+4 nếu phù hợp |
| ITL cao, decode batch lớn | Decode quá tải | Giảm N; giữ/thêm capacity D |
| Cả hai latency tốt nhưng GPU nhàn | Chưa cấp đủ request hoặc client nghẽn | Tăng N vừa phải, kiểm tra client CPU/workers |
| P xong nhưng D đợi lâu | KV transfer hoặc routing | Đo NIXL/UCX và từng pair; kiểm tra IB |
| OOM/retraction | KV/activation/graph headroom thiếu | Xác minh KV dtype, giảm N/batch hoặc memory fraction |
| Chỉ request đầu bị stall | Kết nối/compile/graphs lạnh | Warm-up phù hợp trước official benchmark |

TTFT gồm cả queue, prefill, transfer và bước decode đầu; ITL cao cũng chưa đủ chứng minh memory bottleneck. Cần ghép metric client với worker logs/profiler.

SGLang hỗ trợ PD qua NIXL/Mooncake và có profiling riêng cho P/D. Kit đã dùng NIXL và phát hiện IB active qua sysfs. Giữ cách phát hiện theo từng node; không hardcode tên mlx5 từ một máy khác. [SGLang PD](https://docs.sglang.io/docs/advanced_features/pd_disaggregation).

Nếu cần debug NCCL, dùng logging có mục tiêu; `NCCL_IB_HCA` chọn RDMA interfaces của NCCL, không thay `UCX_NET_DEVICES` cho NIXL/UCX. Không áp hàng loạt env vars không có bằng chứng. [NCCL environment variables](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html).

## 7. EP/DeepEP, CUDA graphs và speculative decoding

EP chia experts, TP chia tensor; EP không phải cứ tăng là nhanh. Decode của kit có EP4 nhưng chưa đủ chứng minh backend truyền thông nào đang dùng. Nếu trace cho thấy all-to-all/dispatch/combine chiếm thời gian, thử backend được image hỗ trợ và so bằng goodput. [SGLang EP](https://docs.sglang.io/docs/advanced_features/expert_parallelism) mô tả DeepEP, grouped GEMM và overlap; các ví dụ DeepSeek không phải cấu hình được xác nhận cho checkpoint Qwen này.

CUDA graphs có thể giảm launch overhead ở decode; kiểm tra log cho biết graph có đang được dùng với batch thực. Tăng graph coverage tiêu thụ thêm memory và thời gian startup. Tên flag của docs online có thể khác image; kiểm tra help trước.

Lossless speculative decoding được Basic cho phép nếu target xác minh mọi token. Tuy nhiên cần draft tương thích đúng checkpoint, accuracy và thời gian kiểm chứng. Với trạng thái hiện tại chưa có full-model baseline và đã tới ngày nộp, không đặt nó làm bước đầu. Không tự mặc định checkpoint này có MTP head.

## 8. Những kỹ thuật không dùng cho bài này

Không thay checkpoint bằng model nhỏ hơn; không prune input/layers/experts; không INT4/FP4 KV hoặc weights; không approximate attention bỏ bớt input; không cho decode worker xử lý prefill trong Basic. Prefix cache không được lợi dụng thay workload: official command cache-bust prefix nên chiến thuật dựa trên prompt trùng cần xem lại.

Warm-up compiler/CUDA graphs và vài request ngoài dataset để lập đường truyền từng P/D pair được Addendum Q1 cho phép. Không thay 60 s warmup của official command hay train draft trên benchmark data.

## 9. Lệnh benchmark phải được sửa trước khi tuyên bố kết quả chính thức

Kit 07/08/09 dùng shortened durations, sweep N và thiếu các flags metric như `--goodput`, `--workers-max`. Chúng hữu ích để học nhưng không phải entrypoint chấm chính thức.

[official-aiperf.sh](official-aiperf.sh) trích nguyên command từ Task Rules, chỉ đưa N/HOST/MODEL thành ba tham số. Phải gọi sau khi gateway healthy, trong cùng Slurm/PBS job deploy. Tokenizer Hugging Face ID cần có cache/network phù hợp trong môi trường judges; checkpoint path đã sẵn không tự đảm bảo ID tokenizer được resolve offline.

Lưu version/image/build recipe, worker flags, topology, N, logs và JSON. Nộp cách dựng lại stack cho account BTC, không chỉ trỏ vào một thư mục riêng của đội.
