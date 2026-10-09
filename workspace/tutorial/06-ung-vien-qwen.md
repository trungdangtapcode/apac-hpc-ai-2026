# Ứng viên Qwen là gì? Dùng SGLang và các bộ tăng tốc ở đâu?

Cập nhật 09/10/2026. Các kết quả job mới nhất ở [báo cáo thực nghiệm](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RESULTS.md).

## 1. Một ứng viên là một cách triển khai có thể chạy lại

Model là Qwen3-235B-A22B-Instruct-2507-FP8 theo luật BTC. Một ứng viên mô tả **cách phục vụ model đó**:

```text
Ứng viên = engine + image/version + chia GPU + worker flags
         + KV/communication backend + gateway/routing + concurrency N
```

Ví dụ tên “09” chỉ mô tả topology: 2 prefill worker ×4 GPU và 2 decode worker ×4 GPU. **09 tại N32** mới là một điểm benchmark cụ thể; 09 tại N64 là điểm khác, có thể trượt SLA dù cùng deployment.

Config có thể nằm trong flags hoặc file YAML/JSON. Bộ config được thực thi bằng script Slurm: xin máy, bật workers và gateway, rồi gọi AIPerf. Khi chọn bài làm cuối, cần cả script và hướng dẫn dựng đúng stack để BTC chạy lại.

Một job ID là một lần chạy, không phải một phương pháp mới. Job 22143/22147 vẫn dùng topology 07; sửa warmup/cổng metrics là sửa quy trình triển khai và đo.

## 2. Những cấu hình đã chạy

| Tên | Engine | Prefill | Decode | Kết quả hiện có |
|---|---|---|---|---|
| **07 — đối chứng** | SGLang | 4 worker × TP2 =8 GPU | 2 worker × TP4/EP4 =8 GPU | Sweep N16/32/64 chưa qua SLA, còn ảnh hưởng khởi tạo KV. Job 22147 được gửi để đo dài N32 sau warmup từng cặp. |
| **09 — ứng viên hiện có kết quả hợp lệ** | SGLang | 2 worker × TP4 =8 GPU | 2 worker × TP4/EP4 =8 GPU | Đo dài N32: **1472,73 good tokens/s; 97,8% đạt SLA**. N64 đo ngắn: 67,0%, trượt SLA. |

TP2/TP4: chia tensor của một worker qua 2/4 GPU. EP4: chia các experts của model MoE qua 4 GPU trong nhóm decode. Chỉ đặt EP4 chưa có nghĩa đã bật DeepEP.

07 và 09 cùng checkpoint, image, decode layout, context 8192, memory fraction 0.90 và NIXL. Khác chính ở số worker và TP của prefill. Cần kết quả đo dài đối chứng để định lượng chênh lệch.

## 3. Các biến thể đề xuất tiếp theo

Bảng này là danh sách research; **chưa phải các cấu hình đã triển khai hoặc chứng minh tăng tốc**.

| Tên hướng thử | Thay đổi gì? | Mức thay đổi | Khi nào ưu tiên? |
|---|---|---|---|
| **09-N40** | Giữ deployment 09, tăng concurrency lên 40 | Tham số benchmark | Thu hẹp khoảng giữa N32 đạt SLA và N64 trượt. |
| **09-N48** | Giữ deployment 09, concurrency 48 | Tham số benchmark | Sau khi biết kết quả N40; không mặc định N càng lớn càng tốt. |
| **FP8 KV** | Dùng FP8 cho KV cache thay dtype hiện tại nếu backend/PD hỗ trợ | Flags dữ liệu trung gian | Khi cache/transfer/capacity đáng khảo sát; kiểm tra dtype thực trước và kiểm chất lượng sau. |
| **MoE kernel / DeepEP** | Tune kernel MoE, hoặc thử backend trao đổi experts phù hợp | Backend; có thể cần đổi image/build | Khi profile cho thấy compute MoE hoặc dispatch/combine tốn thời gian. Hai thay đổi này phải thử riêng. |
| **Graph / scheduling** | Tune graph coverage, giới hạn batch/request hoặc prefill chunk | Flags engine | Khi log/profile cho thấy launch overhead hoặc scheduling nghẽn; CUDA graphs hiện đã hoạt động. |
| **08 — 12P+4D** | 6 prefill worker × TP2; 1 decode worker × TP4/EP4 | Chia lại GPU và placement | Chỉ khi prefill thiếu capacity và decode còn dư. Hiện chưa có bằng chứng ưu tiên hướng này. |
| **vLLM PD** | Thay SGLang bằng vLLM, dựng lại P/D và gateway | Đổi serving stack | Research sau đối chứng ổn định; phải xác minh checkpoint FP8, connector, parallelism và version trên H200. |
| **TensorRT-LLM PD** | Thay engine bằng TensorRT-LLM và hệ phục vụ disaggregated | Đổi serving stack/build | Tương tự vLLM; phải đo cả chi phí triển khai và hiệu năng thật. |
| **Lossless speculative decoding** | Draft đề xuất token, target Qwen xác minh | Đổi cơ chế inference | Ưu tiên thấp: cần draft tương thích, kiểm tính đúng và chất lượng; chưa có draft được chọn. |

[vLLM có tài liệu PD](https://docs.vllm.ai/en/latest/features/disagg_prefill/), [TensorRT-LLM có tài liệu disaggregated serving](https://nvidia.github.io/TensorRT-LLM/features/disagg-serving.html). Việc framework có PD chưa xác nhận toàn bộ checkpoint/flags cần dùng đã hoạt động trong image hiện có. Chưa chạy hai engine này.

FP8 KV và EP/backends là những khả năng SGLang có tài liệu, nhưng phải đối chiếu version trong image: [Quantized KV](https://docs.sglang.io/docs/advanced_features/quantized_kv_cache), [Expert Parallelism](https://docs.sglang.io/docs/advanced_features/expert_parallelism).

## 4. Stack hiện tại đã có những gì?

```text
AIPerf → SGLang gateway → SGLang prefill
                              ↓ KV qua NIXL/UCX/InfiniBand
                         SGLang decode → stream trả lời

Workers chạy trên GPU H200; Slurm cấp máy và quản lý vòng đời job.
```

| Thành phần | Vai trò | Bằng chứng hiện tại |
|---|---|---|
| **H200** | Accelerator phần cứng, chạy tính toán GPU | Job được cấp 16 H200. |
| **SGLang** | Serving engine: chạy model, quản lý request/KV/batch và P/D | Scripts gọi `sglang.launch_server`, gateway gọi `sglang_router.launch_router`. |
| **FP8 weights** | Định dạng weights của checkpoint BTC | Load đúng thư mục checkpoint FP8. |
| **FlashAttention-3 (FA3)** | Kernel attention | Worker server args báo `attention_backend='fa3'`. |
| **DeepGEMM / Triton MoE** | Các thành phần tính toán GEMM/MoE | Log có JIT warmup DeepGEMM và cấu hình kernel MoE Triton. Không suy ra mọi phép tính đều dùng DeepGEMM. |
| **CUDA graphs** | Giảm overhead khi lặp lại chuỗi thao tác GPU | Log decode báo `cuda graph: True` với batch thực. |
| **NIXL / UCX / InfiniBand** | Truyền KV giữa worker ở hai node | Script chọn NIXL và phát hiện thiết bị IB active trên từng node. [SGLang PD](https://docs.sglang.io/docs/advanced_features/pd_disaggregation). |
| **DeepEP** | Backend phục vụ trao đổi experts | Chưa bật riêng; log decode hiện báo MoE all-to-all backend `none`. EP4 và DeepEP là hai khái niệm khác nhau. |

Log cảnh báo thiếu một số cấu hình MoE kernel theo GPU/shape, nên kernel tuning là một giả thuyết đáng kiểm tra. Cảnh báo đó chưa chứng minh đây là bottleneck lớn nhất.

## 5. “Accelerate” và “optimizer” có cần không?

Nếu bạn nói tới **Hugging Face Accelerate**, thư viện này có tính năng load và chạy inference cho model lớn. Trong các job hiện tại, SGLang quản lý việc chạy workers phân tán; mình chưa thêm Accelerate vào entrypoint. Việc thêm một thư viện không tự tạo ra speedup — cần một chức năng cụ thể và số đo. [Accelerate Big Model Inference](https://huggingface.co/docs/accelerate/en/usage_guides/big_modeling).

Nếu “optimizer” là **Adam/AdamW**, đó là thuật toán cập nhật weights khi train. Công việc hiện tại là inference với checkpoint cố định. Các tối ưu đang xét nằm ở kernels, batch/scheduling, parallelism, KV và truyền dữ liệu.

**Thứ tự hiện tại:** sửa và hoàn tất đối chứng 07 → so đo dài với 09 → chọn deployment có dữ liệu tốt → thử concurrency giữa 32 và 64 → dùng profile để chọn thay đổi backend/kernel. Chưa có lý do đổi đồng thời engine, KV, EP và concurrency.
