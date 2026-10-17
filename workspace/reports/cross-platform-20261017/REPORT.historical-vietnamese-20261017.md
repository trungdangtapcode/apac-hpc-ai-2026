# So sánh H100/H200 và ước lượng chuyển nền tảng

Ngày lập: 17/10/2026 UTC. Trạng thái: **đã có một điểm kiểm chứng độc lập N50; chưa đủ để bảo đảm quy đổi tổng quát**. Đây là báo cáo nghiên cứu nội bộ; không phải điểm quy đổi của BTC hoặc thay thế benchmark.

## Kết luận được dữ liệu hiện có hỗ trợ

H100 tốt nhất đã đo là **2.229,83 good output tokens/s**, job **221058.pbs111**, combo MNNVL + FlashInfer, **N50**, SLA **98,5684%**, không lỗi/hủy. Lượt độc lập 221052 đạt 2.218,03; trung bình hai lượt **2.223,93**. Cả hai đã kiểm tra artifact seal, protocol, payload, runtime, short nonregression và long retrieval12/12. Chưa xác minh accuracy99% của BTC.

H200 combo N56 có hai lượt 2.671,11 và 2.669,80, trung bình **2.670,46**. So con số này với H100 N50 chỉ mô tả hai điểm vận hành trên hai hệ thống; **không chứng minh một tối ưu nhanh hơn 20%**, vì GPU và concurrency đều khác.

## Điều kiện để ghép cặp

Dùng **cùng cấu hình combo, cùng N52** làm điểm nối. Không ghép baseline H100 N34 với best H200 N56, không gom CUTLASS/DeepGEMM/FA3/FlashInfer thành một cấu hình.

| Biến | H100 và H200 tại điểm nối | Bằng chứng |
|---|---|---|
| Model | Qwen3-235B-A22B-Instruct-2507-FP8 | config/ServerArgs; model identity từ staging records |
| Tổng GPU |16,hai node| placement.tsv/job launch |
| Prefill |hai worker,mỗi worker TP4/EP1,chunk4096| resolved ServerArgs/log |
| Decode |một worker TP8/EP8| resolved ServerArgs/log |
| Backend |FlashInfer decode attention + MNNVL collective| resolved flags và log khởi tạo rank |
| KV |BF16; config request auto| log cấp phát KV; không suy BF16 từ chữ auto |
| CUDA Graph |dense decode batch1–64| resolved runtime config |
| Routing/KV transfer |round-robin/NIXL; cùng patch geometry| source payload và patch digest |
| Concurrency |52 cho cả hai| export AIPerf |
| Benchmark |closed-loop,4000/200,60warmup/120measure/30grace;seed2026| normalized input_config bằng nhau |
| SLO |TTFT≤3000ms,meanITL≤20ms,≥90%request;errors trong mẫu số| export/raw review |
| Serving/client image |cùng staged image artifacts| SHA256/transfer records bên dưới |

[matched-anchor-audit.json](matched-anchor-audit.json) lưu các trường runtime, normalized benchmark config, nguồn log/export và SHA256. Trên các trường đã kiểm, khác biệt được ghi nhận là **engine random seed** giữa các tiến trình. AIPerf dataset seed2026 vẫn giống nhau. Điều này KHÔNG đồng nghĩa toàn bộ hệ thống chỉ khác GPU.

**Khác biệt chưa loại bỏ:** H100 vs H200; node/CPU/NIC/IB/driver/power/clock; PBS+Singularity vs Slurm+Enroot; host CUDA driver libraries; node placement, cache, time drift; engine seed không cố định. Không có thiết kế hoán đổi ngẫu nhiên phần cứng giữa cùng hai node. Vì vậy tỷ lệ đo được là **tỷ lệ giữa hai hệ thống triển khai**, không phải tác động nhân quả riêng của H200.

Image contract được staging trước đó xác minh, không hash lại toàn bộ26GB image trong lượt này:

- SGLang image: `b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5`.
- AIPerf image: `58fc1cbc2aec897fe39bf74d8f38f055b63c3690429162134f818d9597d22c0a`.
- [asset-contract.json](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/asset-contract.json), [transfer-status.json](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/transfer-status.json).

## Các phép đo được dùng — không chọn riêng peak

Đơn vị tất cả các giá trị là good output tokens/s. Chỉ dùng đúng combo và protocol trên; không gộp cấu hình khác vào trung bình.

| Platform | N | Job IDs | Từng lượt | Trung bình | Vai trò |
|---|---:|---|---|---:|---|
| H100 |52|221052,221058|2215,247;2215,673|2215,460|Calibration |
| H200 |52|23904,23973,23975,24174|2631,085;2632,065;2632,610;2632,964|2632,181|Calibration |
| H100 |50|221052,221058|2218,032;2229,827|2223,930|Input cho prediction |
| H200 |50|24272|2601,629|2601,629 (một lượt)|Holdout đã đo, KHÔNG đưa ngược vào calibration |
| H200 |56|24190,24235|2671,109;2669,803|2670,456|Best vận hành riêng, KHÔNG calibration |

N50 và N52 trên H100 được đo trong cùng allocation: các điểm trong một allocation không phải những replicate độc lập. Đơn vị replicate là allocation/job; ở H100 chỉ có hai job. Các job H200 thực hiện vào thời điểm khác, không có matched-time control cross-platform.

## Phạm vi cấu hình — không quy đổi toàn bộ nghiên cứu

| Nhánh | Đã có H200 | Đã có H100 | Đủ cho hệ số chuyển nền tảng? |
|---|---|---|---|
| MNNVL+FlashInfer, N52 |4job|2job|Chỉ đủ calibration tại mộtN; cần holdout |
| MNNVL riêng |N52/N54|N32–48, có fail ở48|Chưa có matched passingN52; không dùngk52combo |
| FlashInfer riêng |N52|N32–38|Khác tải; không quy đổi trực tiếp |
| Baseline FA3/collective mặc định |N50–60 và các lượt trước|N32–36|Không có cặp benchmark cùngN trong bảng này |
| DeepGEMM/CUTLASS/FP8KV/DP-attention/chunk variants |Có các nhánh H200|Không có phép đo H100 tương ứng đủ ở đây|Không thể suy hệ số riêng |

Nhiều thử nghiệm đã chạy riêng trên từng hệ thống. Không giả định mọi nhánh có cặp đối chứng; chỉ dựng estimate cho một nhánh chung đủ bằng chứng runtime. Việc giữ backend labels và N trong tên đường cong là bắt buộc để tránh gộp cấu hình khác nhau.

## Công thức và mức độ chắc chắn

Định nghĩa giả thuyết cục bộ: với cùng config và tải gần điểm nối, tỷ lệ throughput giữa hai hệ thống thay đổi không quá lớn.

```
k52 = mean(H200, combo, N52) / mean(H100, combo, N52)
    = 2632.180931 / 2215.459986
    = 1.188096805

predicted(H200, combo, N50)
    = mean(H100, combo, N50) × k52
    = 2223.929512 × 1.188096805
    = 2642.243548 good output tokens/s
```

**Đây là mô hình do chúng ta đề xuất, không phải công thức đã được NVIDIA/BTC chứng nhận cho Qwen này.** Các reference bên dưới giải thích vì sao phải kiểm soát workload và kiểm chứng prediction; chúng không chứng minh tỷ lệ1.1881.

Hiện chỉ có **một concurrency được ghép cặp: N52**. Có nhiều lượt lặp tại N52 nhưng không có nhiều điểm tải calibration. Vì vậy chưa ước lượng được k(N), bias theo tải hoặc prediction interval có độ phủ95%.

Nếu chỉ thay giá trị min/max của các lượt đã quan sát, prediction trải khoảng **2633,89–2650,29**. Đây chỉ là **phân tích nhạy cảm của input**, không phải confidence interval, prediction interval hoặc cam kết kết quả thực sẽ nằm trong khoảng này. Nó bỏ sót sai số mô hình, biến thiên chưa quan sát và thay đổi bottleneck khi đổi tải.

SLA là ngưỡng phi tuyến: gầnITL20ms, một thay đổi nhỏ có thể làm nhiều request mất điểm. Không nhân tỷ lệ này vào SLA, TTFT, ITL hoặc các cấu hình khác. Không dùng hệ số dung lượng VRAM/TensorFLOPS/băng thông để nhân trực tiếp goodput.

## Kiểm chứng ngoài dữ liệu calibration — khai báo trước kết quả

Đã submit **24272**, chỉ thay concurrency sangN50 trên H200, cùng source combo, model, protocol và diagnostics. Job này không được đưa vào calibration N52 và chưa có kết quả khi đóng băng prediction. Hiện job đã hoàn tất; kết quả được bổ sung bên dưới, không sửa hệ số ban đầu.

Khi terminal/sealed:

1. Kiểm fullprotocol, payload/runtime, errors/cancel, short/long trước khi xem prediction là hợp lệ.
2. Báo cả dự đoán2642,244 và số đo thực, cùng sai số có dấu và sai số tuyệt đối tương đối.
3. Ngưỡng nghiên cứu quy ước **2%** cho kiểm tra ban đầu, đặt trước khi có số đo. Đây là ngưỡng vận hành do nhóm chọn, không phải độ tin cậy thống kê hoặc luậtBTC.
4. Nếu sai số>2%, hoặc quality/protocol không đạt: đánh dấu giả thuyết quy đổi này không được hỗ trợ ởN50; không thay hệ số/đổi tập calibration để giấu kết quả âm.
5. Nếu sai số≤2%: chỉ nói phép quy đổi phù hợp với điểm kiểmN50 này. Một holdout không đủ bảo đảm mọi tải/cấu hình/GPU.

Muốn dùng cho dự báo rộng hơn: cần ít nhất ba concurrency ghép cặp trải vùng quan tâm, replicate ở mỗi nền tảng, giữ lại một hoặc nhiều điểm ngoài calibration, báo residual/biến thiên và kiểm tương tác platform×config. Đây là kế hoạch nghiên cứu, chưa phải dữ liệu đã có.

## Nguồn tham khảo và phạm vi chứng minh

1. [BTC Qwen3 Task Rules](/home/apacsc42/2026-APAC-HPC-AI/1.%20Qwen3%20AI%20Task%20Rules.md): hai platform được phép, raw throughput không được so trực tiếp giữa nền tảng trong xếp hạng; protocol/SLA/accuracy99%. Đây là nguồn quy định, không cung cấp công thức quy đổi.
2. [NVIDIA TensorRT-LLM performance overview](https://nvidia.github.io/TensorRT-LLM/latest/developer-guide/perf-overview.html): GPU/model, batch size, parallelism và các lựa chọn tuning ảnh hưởng performance. Dùng làm nguyên tắc kiểm soát workload, KHÔNG chuyển số TensorRT-LLM sangSGLang.
3. [NVIDIA H200 specifications](https://www.nvidia.com/en-au/data-center/h200/): H200141GB/4.8TB/s, khoảng1.4× băng thôngH100. Chỉ chứng minh phần cứng khác, không chứng minh Qwen goodput tăng1.4×.
4. [NIST: Prediction uncertainty for a single response](https://www.itl.nist.gov/div898/handbook/pmd/section5/pmd512.htm): phân biệt uncertainty của response dự báo và ước lượng trung bình; không biến khoảng min/max vài lượt thành prediction interval.
5. [NIST: Extrapolation and confirmatory data](https://www.itl.nist.gov/div898/handbook/toolaids/pff/E-Handbook.pdf): prediction ra ngoài thiết kế đo cần dữ liệu thực để kiểm chứng. Ở đây N50 nằm ngoài tập calibration concurrency chỉ cóN52.

Web sources truy cập17/10/2026UTC; website latest có thể thay đổi. Reference hỗ trợ nguyên tắc phương pháp; **bằng chứng định lượng là raw experiments của nhóm**, không phải thông số marketing.

## Cách dùng biểu đồ trong báo cáo

Dùng `matched-comparison.png`: panel cùngN52 là comparison có điều kiện ghép cặp; panel normalized trên từng platform giữ N52=100; prediction và holdout đo thực có nhãn riêng. Không lấy hai best khácN để chú thích “speedup do tối ưu”.

Biểu đồ cũ `comparison.png` là exploratory overview, lưu để truy lịch sử; không dùng riêng nó như chứng minh tính chính xác của phép quy đổi. File/data/method đều giữ nguyên để kiểm tra.

[Raw derived data](data.json) · [Runtime/config audit](matched-anchor-audit.json) · [Script tạo biểu đồ](build.py) · [Protocol/quality reviews](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/manual-20261017-0858/RESULTS.md).

## Công cụ kiểm chứng đã chuẩn bị

[validate-holdout.py](validate-holdout.py) giữ nguyên prediction/threshold đã khai báo, kiểm seal/protocol/runtime/SLA/short/long rồi báo sai số. [holdout-validation.json](holdout-validation.json) đã ghi kết quả LOCAL_HOLDOUT_SUPPORTED theo ngưỡng vận hành 2% đã khai báo. Nhánh terminal đã chạy trên dữ liệu thật; điều này không chứng minh mô hình quy đổi tổng quát. Script không gọi model hay submit GPU job.

## Held-out validation result — 17 October 2026, 11:56 UTC

The forecast was frozen while job 24272 was still pending. Its original calibration inputs and tolerance remain unchanged.

| Quantity | Value |
|---|---:|
| Frozen H200 N50 prediction | 2,642.244 good tokens/s |
| Measured H200 N50, job 24272 | 2,601.629 good tokens/s |
| Signed error, (measured − predicted) / predicted | −1.5371% |
| Absolute error | 1.5371% |
| Predeclared operational tolerance | 2% |
| Measured SLA | 99.1326% |
| Mean TTFT / ITL | 505.178 ms / 16.367 ms |
| Long retrieval checks | 12/12 passed |

The sealed raw/protocol/payload/runtime and short-output checks passed. The result passes the predeclared 2% operational check at this one held-out point. **This does not establish 95% prediction coverage or validate transfer to other configurations.**

The measurement is **outside the previous input-only sensitivity range of 2,633.887–2,650.293**. This directly demonstrates why that narrow range must not be presented as a prediction interval: it did not include load-dependent model error.

The observed system ratio at N50 is about **1.1698×**, versus the N52 calibration ratio **1.1881×**. The ratio is not exactly constant across load. Keep this discrepancy visible. Do not refit the frozen ratio using the holdout and then report its training error as a validation result.

The next step for a general transfer model would be additional matched loads and independent repeats with another untouched validation set. This one result supports only a rough local forecast. It is not an official converted score or a GPU-only causal speedup.

[Full validation record](holdout-validation.json) · [Frozen preregistration](pre-registered-prediction.json) · [Validation code](validate-holdout.py).
