# TripleU APAC2026 — slide guide

Data snapshot: 2026-10-12T10:24:13.693598+00:00

English slides; Vietnamese speaker notes. Suggested duration: 15–20 minutes for the main 18 slides. Appendix is for Q&A.

## 01. Serving the full model. Meeting the latency gate.

- Qwen3-235B-A22B / PD disaggregated inference
- VNUHCM - TripleU
- Evidence snapshot  |  12 October 2026
- BEST INTERNAL RESULT
- 1,912.30
- good output tokens/s / 97.44% SLA fraction / N48 / 16 H200

**Ghi chú thuyết trình:** Mở đầu: snapshot mới ngày 12/10. Cấu hình tốt nhất đã đo dài là P8-TP4_D8-TP8-EP8 với bản vá NIXL, N48, 1.912,30 good tokens/s và 97,44% SLA. Đây là số đo local, chưa phải điểm BTC. BTC cung cấp checkpoint, image, cluster và benchmark; đội lựa chọn cấu hình và viết bản vá descriptor. HPC chưa có bằng chứng ở đây.

## 02. Best measured stack, with explicit limits

- GOOD OUTPUT RATE
- 1,912.30
- req/s goodput × 200 / 9.56150 good req/s
- REQUESTS WITHIN BOTH SLAs
- 97.44%
- 1,180 / 1,211 requests / 0 errors; 0 cancellations
- VALIDATION STATUS
- Pending
- Full-set accuracy / Organiser official re-run

**Ghi chú thuyết trình:** Cấu hình tốt nhất đạt 1.912,30 token tốt mỗi giây; 1180/1211 request đạt cả hai SLA, không lỗi hoặc hủy. Đã đo 60/120/30 với bản vá transport. Chưa có accuracy full-set hoặc re-run BTC. Entry point portable trong ZIP vẫn là bản Basic unpatched 09/N40; không tự nhận script mới đã GPU-run.

## 03. Throughput counts only when latency passes

- WORKLOAD
- 4,000 → 200
- Synthetic Shakespeare inputs / Official FP8 checkpoint
- PER-REQUEST SLA
- 3,000 / 20
- TTFT ≤ 3,000 ms / Mean ITL ≤ 20 ms
- POINT ACCEPTANCE
- ≥ 90%
- Requests must pass both / Errors stay in denominator
- Closed-loop load: a completed request is immediately replaced, sustaining N concurrent requests.

**Ghi chú thuyết trình:** Giải thích TTFT là chờ token đầu; ITL là khoảng cách trung bình giữa token của một request. Phải đạt đồng thời 3.000 ms và 20 ms. Ít nhất 90% request đạt; request lỗi vẫn ở mẫu số. Dữ liệu Shakespeare để đo tốc độ khác với các bộ benchmark chấm kiến thức. Không chỉ chạy hết dataset rồi tính raw throughput.

## 04. One platform, one unchanged checkpoint

- COMPUTE
- 2 × HGX H200 nodes / 16 GPUs total
- NETWORK
- InfiniBand NDR between the two nodes
- MODEL
- Qwen3-235B-A22B-Instruct-2507-FP8
- SERVING
- SGLang 0.5.17 / router 0.3.2 / NIXL 1.3.2
- CLIENT
- AIPerf 0.12.0; pinned official tokenizer
- PRECISION
- Published FP8 weights / BF16 KV (auto, verified in logs)

**Ghi chú thuyết trình:** Hai node HGX H200, mỗi node 8 GPU, kết nối InfiniBand. Server dùng SGLang 0.5.17, router 0.3.2 và NIXL 1.3.2; client AIPerf 0.12.0. BF16 KV được xác nhận từ worker log chứ không suy đoán mặc định FP8. Mình dùng image BTC, không dựng image tùy ý khác. Không có draft model.

## 05. Best layout: 2 prefill + 1 decode worker

- NODE 0  /  8 H200
- NODE 1  /  8 H200
- Prefill worker 0  ·  4 GPUs  ·  TP4 / EP1
- Prefill worker 1  ·  4 GPUs  ·  TP4 / EP1
- Decode worker 0 / 8 GPUs  ·  TP8 / EP8
- KV cache / NIXL →
- AIPerf N48 → OpenAI-compatible gateway :8000 → Prefill → Decode → streamed tokens

**Ghi chú thuyết trình:** Node 0 có hai prefill worker TP4/EP1, mỗi worker dùng 4 GPU. Node 1 có một decode worker TP8/EP8 dùng 8 GPU. Có hai cặp P/D, truyền KV qua bản vá NIXL do đội viết, model giữ FP8 weights và BF16 KV. TP chia ma trận; EP chia expert trên nhóm decode. Tổng vẫn 16 H200. Đây là stack tốt nhất đã đo; entry portable cũ ở ZIP vẫn là 09/N40 unpatched, được phân biệt rõ.

## 06. Starting layouts establish our measured reference

- Reference layout 07
- Prefill: 4 workers × TP2 / Decode: 2 workers × TP4 / EP4 / Node split: 8 + 8 GPUs / Long run: N32
- Previous best layout 09
- Prefill: 2 workers × TP4 / Decode: 2 workers × TP4 / EP4 / Node split: 8 + 8 GPUs / Long run: N40
- Trade-off: fewer prefill replicas, wider tensor parallelism; measure the balance under the SLA.

**Ghi chú thuyết trình:** 07 và 09 là các ví dụ BTC cung cấp. 07 có bốn prefill TP2; 09 có hai prefill TP4. Decode ở hai layout này đều là hai worker TP4/EP4. 09/N40 là best cũ, còn hiện tại best dùng một decode TP8/EP8 và bản vá descriptor của đội. Không nhận các thư viện hoặc checkpoint của BTC là sản phẩm đội viết. Tăng 14,78% gồm đổi topology, N và transport, không quy riêng cho bản vá.

## 07. A 17-layout search, with measured coverage

- GPU SPLIT P + D
- PREFILL TP
- DECODE TP
- LAYOUTS
- 8 + 8
- 2 / 4 / 8
- 2 / 4 / 8
- 9
- 4 + 12
- 2 / 4
- 2 / 4
- 4
- 12 + 4
- 2 / 4
- 2 / 4
- 4
- 14/17 originals measured
- + 3 measured EP2 variants
- Each completed topology has N16, N32, N40 and N48 actual measurement exports.

**Ghi chú thuyết trình:** Không gian này có 17 topology, không phải mọi cấu hình engine có thể có. Chia GPU P/D theo 8+8, 4+12, 12+4 rồi TP2/4/8 tùy chia hết. Snapshot có 14/17 gốc và 3/3 biến thể EP2 đủ bốn sweep. Ba TP8/EP1 lỗi FP8 nên giữ riêng, không tính giả đã chạy. TP1 không hợp vì weights model lớn hơn bộ nhớ một H200.

## 08. Screen quickly; confirm at the full duration

- Deploy + initialize
- All P/D paths / Separate setup prompts
- Explore
- N16 / 32 / 40 / 48 / 10s + 20s + 30s
- Long confirmation
- Best N48 / latest N32 / 60s + 120s + 30s
- Official timing
- 60s warmup
- 120s measurement
- 30s grace
- A short sweep and a long confirmation use different windows; their difference is not an optimisation gain.

**Ghi chú thuyết trình:** Các sweep 10/20/30 dùng để sàng lọc, không làm kết quả chính. Best mới chọn N48 và đo dài ở job 22415. Job 22809 chọn N32 vì N40/N48 trượt gate. Khởi tạo P/D tách riêng không đổi warmup 60 giây của AIPerf. Entry portable trong ZIP vẫn là 09/N40; chuyển winning stack sang wrapper và chạy lại trên GPU là bước tiếp theo.

## 09. Winner sweeps select N48; the long run confirms it

- N48 sweep: 1,788.65 good tokens/s; 90.95% SLA. Long N48: 1,912.30; 97.44% SLA.

**Ghi chú thuyết trình:** Cả bốn sweep của best mới đều qua 90% SLA. N48 đạt 1.788,65 good tokens/s và 90,95% SLA trong 20 giây. Confirm N48 đạt 1.912,30 và 97,44% trong 120 giây. Không coi chênh lệch giữa hai cửa sổ là speedup. Dùng confirm dài làm kết quả chính; request trượt vẫn nằm trong mẫu số.

## 10. Best long run: +14.78% over the previous best

- Observed gain includes topology, concurrency and transport changes. Repeated matched A/B is still needed.

**Ghi chú thuyết trình:** Best mới 1.912,30 cao hơn best cũ 1.666,01 khoảng 14,78%. Mọi hàng trong đồ thị là confirm dài qua SLA trên 16 H200. Topology, concurrency và transport khác nhau; chưa tách riêng tác động của bản vá. Chưa có A/B lặp ngẫu nhiên. Baseline là số đo local của đội, không phải điểm tham chiếu BTC.

## 11. Check the gate per request, not from averages

- 1,180 / 1,211
- requests pass both limits
- Mean TTFT: 1,482.22 ms / Mean ITL: 16.79 ms / P95 TTFT: 2,456.56 ms / P95 ITL: 17.99 ms

**Ghi chú thuyết trình:** Đối chiếu JSONL có 1.180 request tốt trên 1.211, khớp 97,44% của export AIPerf. Có 31 request trượt, không lỗi hoặc hủy. Mỗi request tốt phải có TTFT ≤ 3.000 ms và ITL trung bình của chính request ≤ 20 ms. Trung bình toàn lượt đo không quyết định gate. Accuracy là bài kiểm tra khác.

## 12. Failures remain evidence; actual exports count

- FP8 sharding
- TP8 / EP1 gives a 192-wide expert shard; FP8 block size is 128.
- Use a distinct EP2 variant; keep the EP1 original incompatible.
- Cold P/D transfer
- 22778 timed out before measurement; patched 22809 completes.
- Request-scoped descriptors; setup deadlines do not relax benchmark SLAs.
- Distributed ports
- A deployment hit EADDRINUSE before producing metrics.
- Assign explicit distinct ports; preserve the failed logs and source.

**Ghi chú thuyết trình:** Có ba nhóm lỗi: shard FP8 không khớp block 128, timeout khởi tạo KV, và trùng cổng. Job 22778 thất bại trước benchmark, không được tính là đo xong. Job 22809 với bản vá equal-TP đã đo đủ bốn N và confirm N32. Thành công sau sửa chưa chứng minh một nguyên nhân duy nhất. Giữ mọi attempt lỗi để học và kiểm tra.

## 13. EP2 makes TP8 compatible with FP8 blocks

- TP8 / EP1
- 128 experts / 1 expert group / 1536 ÷ 8 = 192 / 192 is not divisible by 128
- TP8 / EP2
- 64 experts / group × 2 groups / 1536 ÷ 4 = 384 / 384 = 3 × 128
- All 3 EP2 replacements are measured. All experts and weights are retained; the originals stay labelled.

**Ghi chú thuyết trình:** TP chia ma trận trong expert; EP chia danh sách expert. TP8/EP1 trên 8 GPU cho 1536/8 = 192, không khớp block 128. EP2 chia 128 expert thành hai nhóm 64; effective TP4 cho 384 = 3 × 128. Không bỏ expert hay đổi weights; đây là variant, không giả đã đo EP1. Cả ba variant EP2 đã đủ bốn N. Best hiện tại có prefill TP4/EP1 và decode TP8/EP8.

## 14. NIXL: two request-scoped transport patches

- Full-pool descriptor plan
- ≈ 403.8 million source entries / rank
- Request-scoped plan
- 188 entries: contiguous TP8→TP4 or TP8→TP8
- Byte ranges, head mapping and notifications retained.
- 720 + 936
- CPU range cases / Both patches GPU-tested
- 1,507.96
- latest equal-TP / N32 / 95.38% SLA; no errors

**Ghi chú thuyết trình:** Đội sửa tích hợp NIXL, không viết lại thư viện. Bản hetero-TP có 720 trường hợp kiểm tra CPU; best job 22415 dùng TP4 → TP8. Bản equal-TP8 bỏ prepared handle cho toàn pool ở layout TP8/PP1/MHA/VRAM cùng layer và stride, dùng generic transfer gốc; có 936 trường hợp và 5 kiểm tra guard. Job 22809 xác nhận mount SHA và bỏ dlists trên cả 8 rank, có đủ sweep và confirm. Ví dụ 4.000 token liên tục TP8 → TP4 hoặc TP8 → TP8 cần 188 descriptor; không áp con số này cho mọi geometry TP4 → TP8. CPU geometry không thay accuracy.

## 15. Measured winner and portable replay are distinct

- 01
- Current winner
- Job 22415 / N48; source, patch, worker logs and canonical exports.
- 02
- Portable entry
- submit.sbatch still replays unpatched 09 / N40, job-22219 layout.
- 03
- Frozen audit trail
- All historical attempts and source hashes; raw measurements unchanged.
- 04
- Next replay step
- Port the winning patch/layout and GPU-validate the packaged entry.

**Ghi chú thuyết trình:** Slide cập nhật best 1.912,30 và ZIP có log, source và bản vá thật. Entry portable submit.sbatch vẫn là unpatched 09/N40 đóng gói từ job 22219. Không tuyên bố entry này chạy best mới. Payload 22415 trong archive có đường dẫn account gốc nên là bằng chứng, không phải script portable. Chuyển best sang wrapper và chạy GPU vẫn còn phải làm. Metadata gpu_validated:false là snapshot trước job; gpu-validation.json ghi bằng chứng sau job.

## 16. Correctness claims follow the available evidence

- Published FP8 weights and BF16 KV, unchanged
- Worker logs / source
- Plain PD on 16 GPUs; no speculative decoding
- Configured / local logs
- Best long run / N48 latency gate
- 97.44% pass fraction
- Full-set accuracy ≥ 99% of reference
- Not yet tested
- Organiser reconstruction + official scored re-run
- Pending
- Local latency evidence is available. Official acceptance and any Bonus validation remain pending.

**Ghi chú thuyết trình:** Weights FP8 chính thức, KV BF16, plain PD, không draft hoặc bỏ phép tính. Bản vá chỉ đổi descriptor, nhưng CPU geometry và latency benchmark không chứng minh accuracy full-set. 97,44% của best là latency gate, không phải mức đúng MMLU-Pro hoặc GPQA. Cả quality 99% và re-run BTC đang chờ. Không tự nhận Bonus đã xác thực.

## 17. Topology coverage complete; submission work remains

- Measured coverage
- 14 original + 3 EP2 layouts / All four concurrency sweeps / Winning long-run evidence / Both NIXL patches and logs
- Still outstanding
- Full-set accuracy check / Portable winning-stack replay / HPC/OpenFOAM evidence / Official upload and re-run

**Ghi chú thuyết trình:** Hiện 14 cấu hình gốc và 3 variant EP2 có đủ bốn N, tổng 17 layout sử dụng được. Ba bản gốc EP1 vẫn không tương thích FP8, nên không nói 17 gốc đã chạy. Đo đủ và đạt SLA khác nhau; một số layout vẫn trượt. Workspace chỉ làm Qwen, chưa có script/log HPC. Chưa upload BTC. Accuracy, portable winning replay và dữ liệu HPC thật là phần còn lại; không còn thiếu sweep trong search này.

## 18. Current winner: TP4 prefill + TP8 / EP8 decode

- 1,912.30
- good output tokens per second
- 97.44% request SLA fraction  ·  N48 / 16 H200  ·  Official FP8 model
- Accuracy and organiser re-verification remain pending.

**Ghi chú thuyết trình:** Best local là 1.912,30 good tokens/s và 97,44% SLA, dùng model FP8 chính thức trên 16 H200. BTC cung cấp model, image, cluster và benchmark; đội chọn layout/tải và viết bản vá tích hợp. Kết quả chưa được BTC chấm. Toàn search sử dụng được đã đo; bước tiếp theo là accuracy và portable winning replay.

## 19. Appendix: the final repaired layout and selection

- Final layout
- P8-TP8-EP2_D8-TP8-EP8; job 22809 completed.
- N32 long run
- 1,507.96 good tokens/s; 95.38% SLA; no errors/cancels.
- N40 / N48 short sweeps
- 89.50% / 86.06% SLA: both miss the 90% gate.
- Selection
- Job 22415 remains the best passing long measurement.
- Interpretation
- Measured coverage does not mean every layout passes SLA.

**Ghi chú thuyết trình:** Job 22809 chạy đủ bốn N và confirm N32, không lỗi hoặc hủy. N40 sweep đạt 89,50% và N48 đạt 86,06%, trượt ngưỡng 90%, nên không chọn dù tốc độ cao. N32 confirm đạt 1.507,96 và 95,38%, qua SLA nhưng không vượt best 1.912,30. Lịch sử N16/N32 unpatched của job 22750 vẫn giữ riêng, không ghép vào sweep có bản vá. Giữ byte geometry không thay thế accuracy hoặc A/B speedup.
