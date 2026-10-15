# Kế hoạch research cho track Qwen

Cập nhật: 15/10/2026. Bạn thi **Qwen**; các thử nghiệm đang chạy chỉ dùng Qwen.

**Sau khi xem lịch sử Slurm công khai của team01:** giới hạn thật của QoS
`normal` là **5 job đang chờ + đang chạy mỗi user**. Con số4 trước đó là giới
hạn mình tự đặt trong controller. Đã nâng các plan đang hoạt động lên5 và gửi
thêm **23780**, thử **attention DP8 + EP8 + DeepEP**. Hiện đủ5 job chờ, gồm
23773 /23776 /23777 /23778 /23780. Thêm job chờ không làm tăng điểm ưu tiên.

Attention DP khác với việc mở tám bản sao nguyên model: mỗi nhóm nhận request
khác nhau cho attention, còn các expert của MoE vẫn chia trên tám GPU và trao
đổi token qua DeepEP. Job mới giữ8 GPU prefill +8 GPU decode để so sánh trước;
chưa đổi ngay sang12+4 và chưa bật speculative decoding.

Từ1/10, team01 có163 lượt submit nhưng chỉ87 trạng tháiCOMPLETED,60 lượt huỷ,
11 lỗi và5 đang chờ. COMPLETED không chứng minh benchmark hay accuracy đạt.
Tên job gợi ý họ đã thử vLLM, DP attention, DeepEP, các tỷ lệ P/D và speculative
decoding. Không xem được điểm của họ từ lịch sử này; N128 không tự có nghĩa
nhanh hơn N53 của mình.

Đã bổ sung ưu tiên speculative decoding với draft EAGLE3 công khai đúng model,
xem lại12+4 sau DP attention, và baseline vLLM độc lập.
[Lịch sử, suy đoán và research mới bằng tiếng Anh](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-public-slurm-2026-10-15/README.md).
[Job23780 và điều kiện tự chạy tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/PLAN.md).

Các con số bốn job trong ghi chú bên dưới thuộc thời điểm trước khi nâng giới hạn.

**Mới nhất:** N53, job **23616**, đạt **2433,41 good tokens/s, 98,88% SLA**,
cao nhất trong một lượt đo hiện tại. Job **23773** đang chờ để đo lặp. N52 đã
đo ba lần: 2402,64 /2397,72 /2400,02, đều khoảng98,93% SLA.

Vòng backend trên router round-robin đã đo xong: FP8 KV chỉ đạt **10,75% SLA**,
DeepGEMM đạt **84,71%**, cả hai trượt yêu cầu90%. Không phải job treo hay lỗi
request; thời gian giữa token vượt ngưỡng khiến điểm goodput giảm. Vì vậy không
chạy tiếp các nhánh phụ thuộc hai phương án này.

Đã gửi tiếp ba job N52, mỗi job chỉ đổi một phần phía decode:

| Job | Thử gì | Mục đích |
|---|---|---|
| **23776** | CUTLASS cho MoE | Thử kernel xử lý các expert khác |
| **23777** | FlashInfer cho attention | Thử kernel đọc KV và tính attention khác |
| **23778** | MNNVL cho all-reduce | Thử cách cộng và đồng bộ kết quả giữa8 GPU decode khác |

Ba hướng này dựa trên profile mới của23607: MoE chiếm khoảng27%, giao tiếp
GPU20%, kernel attention chính20% tổng thời gian kernel decode. Các tỷ lệ này
không có nghĩa chắc chắn tăng tốc được tương ứng. Giữ nguyên model, BF16 KV,
topology và benchmark để đo tác động từng thay đổi. Tổng cộng bốn job đang chờ,
tính cả job lặp N53. Phương án cải thiện≥2% so với cả hai đối chứng N52 thì tự
đo lặp; lặp đạt và còn dư ITL mới thử N54. Chưa xác nhận accuracy99% của BTC.
[Plan vòng7 bằng tiếng Anh](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/PLAN.md).

**Các ghi chú phía dưới là lịch sử, trạng thái queue có thể đã thay đổi.**

**Cách chạy tiếp theo yêu cầu của bạn:** không chờ hết một vòng mới chuẩn bị
vòng sau. Nhận định và script độc lập đủ căn cứ thì gửi trước để lấy chỗ queue,
giữ tối đa bốn job đang chờ/chạy. Job phụ thuộc kết quả vẫn phải chờ đúng điều kiện.

N54 **23583** vẫn chờ. Đã gửi thêm **23607** (đo N52 round-robin rồi lấy profile
riêng), **23608** (FP8 KV trên round-robin), **23609** (DeepGEMM trên round-robin).
Hai backend từng thử ở router cũ, khi tải decode khác, nên chưa thể loại chúng
ở cấu hình hiện tại. Benchmark và model giữ nguyên; mỗi job đổi một yếu tố.

Backend nào nhanh hơn ít nhất **2%** so với cả đối chứng round-robin cũ và
đối chứng mới thì tự gửi job đo lặp. Lặp lại được cải thiện, SLA≥95% và ITL
trung bình≤19,3ms thì tự thử N54 của backend đó. Không phải đợi bạn nhắc mới gửi.
Đây vẫn là nghiên cứu; chưa xác nhận accuracy99% của BTC.
[Plan vòng 6](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-06/PLAN.md).

**Có hướng cải thiện rõ:** round-robin prefill, job **23325**, đạt **2402,64 good
tokens/s, 98,93% SLA** ở N52. So với control N52 mới 2075,11 là hơn **15,78%**,
nhưng mới một lượt đo. TTFT trung bình giảm từ 1437,63 xuống 333,25 ms; số request
trượt TTFT giảm từ 34 còn 16. Đổi lại ITL trung bình lên 19,57 ms, sát giới hạn
20 ms, nên cần đo lặp và thử N50 để xem độ ổn định.

Vòng tải của router cũ đã xong: N58 đo được **2157,31** rồi **2159,79**. Không
chuyển thẳng N58 sang router mới vì router mới đã làm thay đổi tải phía decode.
Plan mới: lặp round-robin N52, thử N50; N52 đạt mới thử N54, rồi chọn và đo lặp
điểm tốt nhất. [Plan vòng 5](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-05/PLAN.md).

Đã gửi **23576** (lặp round-robin N52) và **23577** (round-robin N50).

Các cập nhật phía dưới là lịch sử.

**Cập nhật sau bài prefill/decode:** đã đọc bài bạn gửi và đếm lại metrics từng
request. Hai lượt tốt nhất đều có **34 request trượt TTFT, 0 request trượt ITL**.
Cả 34 request bắt đầu trong **30 ms đầu của cửa sổ đo**. Vì vậy bổ sung hai hướng
kiểm tra: router chia đều request cho hai prefill worker bằng round-robin, và mỗi
batch prefill chỉ nhận một request. Chưa biết hướng nào tốt hơn; phải đo riêng.
Benchmark, warmup và các request đầu bị trượt vẫn giữ nguyên.

Đã gửi **23324** (mỗi batch prefill một request) và **23325** (router prefill
round-robin), so với cấu hình đã đo lặp và job đối chứng N52 **23286**.
Hai job mới giữ cùng 16 H200, model, KV BF16, chunk 4096 và decode CUDA graph;
mỗi job chỉ đổi một yếu tố. Các job này vẫn phải đợi Slurm cấp tài nguyên.

Ở hệ thống của ta, prefill và decode đã dùng GPU riêng, nên lời giải thích
"prefill dài chặn decode trên cùng GPU" trong blog không áp nguyên xi. TTFT còn
bao gồm chờ hàng, router và chuyển KV; chưa thể kết luận cứ TTFT cao là kernel
prefill chậm. Prefix caching ít có ích với benchmark này vì có cache-bust.
[Research và plan chi tiết bằng tiếng Anh](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-04/RESEARCH.md).

**Vòng 2 đã đo xong:** chunk 4096 + CUDA graph đạt **2078,96** rồi **2079,18
good tokens/s** trong hai lần khởi động riêng; cả hai khoảng **97,43% SLA**.
Chunk-only lặp lại được **2032,13**. FP8 KV được **1996,26**, DeepEP được
**1957,15**, đều thấp hơn đối chứng phù hợp nên chưa chọn.

**Vòng 3 đã gửi:** **23286** đối chứng N52 và **23287** thử N54 trên cùng cấu hình
chunk 4096 + CUDA graph, KV vẫn BF16. N54 đạt thì tự thử N56, rồi N60 nếu N56 đạt.
Nếu trượt SLA, thử một mức giữa lượt đạt và lượt trượt; không coi lỗi deploy là
bằng chứng tải quá cao. Nếu có điểm mới nhanh hơn ít nhất 2%, tự đo lặp điểm đó.
[Plan vòng 3](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-03/PLAN.md).

Các cập nhật phía dưới là lịch sử.

**Kết quả mới nhất:** bốn lượt N52 chạy riêng đã xong. Control: **1977,08**;
chunk 4096: **2033,03**; chunk 4096 + CUDA graph: **2078,96**; chunk 16384:
**1741,20 good tokens/s**. Cấu hình kết hợp tốt nhất lượt này, hơn control **5,15%**,
nhưng vẫn cần đo lặp để biết có ổn định không.

Job đối chứng 23146 chạy model thường, không qua NIXL: **120/132** câu đúng,
12 câu sai đều là câu đảo chuỗi, giống trường hợp sai ở bốn cấu hình P/D.
Các câu còn lại, gồm 36 câu lấy thông tin trong context dài, đều đúng.
Điểm smoke của bốn cấu hình vẫn là **7/8**; chưa chứng minh accuracy 99% của BTC.
Bộ tự động ban đầu dừng vì yêu cầu 8/8. Nay chỉ cho **tiếp tục nghiên cứu** khi
không xuất hiện câu sai mới so với đối chứng, vẫn giữ mọi câu trả lời sai trong logs.

Đã gửi **23264** (DeepGEMM control), **23265** (FP8 KV), **23266** (đo lặp
chunk 4096 + CUDA graph) và **23267** (đo lặp chunk 4096). DeepEP chờ đối chứng
DeepGEMM đo xong. Chưa đổi script nộp bài theo một lượt đo đơn lẻ.
[Đánh giá vòng N52](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/STANDALONE_ASSESSMENT.md)
· [Kết quả đang cập nhật](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/SERVING_TUNING_RESULTS.md).

Các đoạn dưới là lịch sử các vòng trước.

**Vòng tiếp theo:** đợt 8 job vừa rồi đã xong, điểm tốt nhất một lượt là **2140,10
good tokens/s, 98,81% SLA** với chunk 4096/N52. Đã gửi **23128–23131**: đối chứng
N52 chạy riêng, lặp chunk 4096, ghép chunk 4096 + CUDA graph, và chunk 16384.
Sau đó tự thử DeepEP/FP8 KV khi đối chứng hợp lệ và queue có chỗ, cùng hai lượt
đo lặp cấu hình tốt nhất. Chỉ giữ tối đa bốn job đang chạy/chờ. Tám câu hỏi kiểm
tra output ngắn không thay được accuracy check 99% của BTC.
[Plan vòng 2](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/PLAN.md).
Đây vẫn là bước 5: tối ưu theo bottleneck, đồng thời bắt đầu phần xác nhận của bước 6.

**Cập nhật 11:33 UTC:** control 23128 đo được **1977,08 good tokens/s, 97,14%
SLA**, không lỗi benchmark. Nhưng kiểm tra output chỉ đạt **7/8**: câu đảo chuỗi
trả lời thừa ký tự. Chưa rõ nguyên nhân. Đã gửi **23146** kiểm tra cùng model
chạy thường, không chuyển KV qua NIXL, trên TP4 và TP8. Đây là job chẩn đoán,
không đưa vào bảng tốc độ cuộc thi. Ba job 23129–23131 vẫn chờ tài nguyên.
[Theo dõi kiểm tra output](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-02/OUTPUT_DIAGNOSTIC.md).

**Vòng cải tiến hiện tại:** đã đo 17 cấu hình dùng được (14 cấu hình gốc +3 biến thể
EP2). Tốt nhất là **TP4 prefill → TP8/EP8 decode, N48: 1912,30 good tokens/s,
97,44% SLA**, job 22415. Tiếp tục plan bằng ba job mới: **23102** đo lặp và thử
N48/52/56; **23103** thử CUDA graph cho từng batch 1..64; **23104** đo lặp N48 rồi
lấy trace GPU riêng cho prefill/decode. Chưa có số đo mới lúc gửi job.

[Plan tiếp theo theo từng trục](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/PLAN.md)
· [Kết quả cập nhật](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/SERVING_TUNING_RESULTS.md).
Sau profiling mới chọn MoE kernel, DeepEP, chunk prefill hoặc FP8 KV để thử có lý do.
Các đoạn bên dưới ghi lại kế hoạch và diễn biến từ vòng đầu ngày 09/10.

**Trạng thái mới nhất:** 22200 hoàn tất; 09/N40 đạt **1649,27 good tokens/s,
97,81% SLA**, không có request bị hủy. N48 sweep trượt SLA.
Theo yêu cầu “thử hết”, đã mở đợt **17 topology ×4 mức concurrency**;
bốn job đầu là 22219–22222, controller tự gửi tiếp khi queue còn chỗ.
Xem [giải thích đợt 17 topology](09-thu-het-topology-qwen.md) và
[bảng trạng thái/kết quả tự cập nhật](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/TOPOLOGY_RESULTS.md).
Các mốc ở phần dưới là lịch sử vòng đầu.

## Mục tiêu cần hiểu

Đây là yêu cầu của BTC trong [luật Qwen — Task Workload and Input / Task Rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md#task-rules). Workload benchmark quy định **4.000 input token và 200 output token**, với stddev = 0. Mình cần phục vụ nhiều request, nhưng vẫn trả lời đủ nhanh.

- **TTFT:** thời gian chờ token đầu tiên, phải ≤ 3.000 ms.
- **ITL:** thời gian trung bình giữa các token trong một request, phải ≤ 20 ms.
- Ít nhất **90% request** phải đạt cả hai điều kiện, tính cả request lỗi trong mẫu số.
- **Goodput:** số request đạt chuẩn mỗi giây. Nhân với 200 để ra good output tokens/giây dùng so hiệu năng.

Ví dụ: một cấu hình sinh nhiều token nhưng chỉ 67% request đạt chuẩn thì không vượt qua ngưỡng 90%. Không chọn nó chỉ vì throughput cao.

## Vì sao thử cấu hình 07 và 09 trước?

Qwen ở đây tách thành hai phần:

- **Prefill (P):** đọc prompt và tạo KV cache.
- **Decode (D):** nhận KV cache rồi sinh token trả lời.

Cả hai cấu hình dùng đúng model FP8 của BTC và tổng cộng **16 H200 trên hai compute node**:

| Cấu hình | GPU làm prefill | GPU làm decode |
|---|---|---|
| 07 — đối chứng | 4 worker, mỗi worker dùng 2 GPU | 2 worker, mỗi worker dùng 4 GPU |
| 09 — ứng viên | 2 worker, mỗi worker dùng 4 GPU | 2 worker, mỗi worker dùng 4 GPU |

Một worker là một nhóm tiến trình phục vụ model. TP2/TP4 nghĩa là chia model qua 2/4 GPU của worker đó. Mình thay cách tổ chức prefill, giữ phía decode và tổng tài nguyên giống nhau, để xem hai worker lớn có tốt hơn bốn worker nhỏ hay không.

## Các bước thực hiện

1. **Chạy được trước:** kiểm tra model, image, tokenizer, GPU, InfiniBand và gateway. Có lỗi deploy thì sửa, không coi log lỗi là số đo hiệu năng.
2. **Đo nhanh:** lần lượt concurrency 16, 32, 64; mỗi lượt warmup 15 giây, đo 30 giây, grace 30 giây. Concurrency là số request được giữ đồng thời; tăng nó thường tăng throughput nhưng cũng tăng độ trễ.
3. **Đo dài:** lấy mức concurrency đạt SLA có goodput cao nhất của mỗi cấu hình; warmup 60 giây, đo 120 giây, grace 30 giây. Hai loại lượt đo được lưu riêng.
4. **So kết quả:** xem goodput, tỷ lệ đạt SLA, TTFT/ITL, lỗi và log worker. So cả cùng concurrency để đánh giá topology, lẫn mức tốt nhất đã thử của từng topology.
5. **Chọn thử nghiệm tiếp theo từ bottleneck:** chỉ đổi một yếu tố mỗi lần. Nếu prefill nghẽn mới cân nhắc đổi số GPU P/D; nếu KV cache hoặc truyền cache có vấn đề mới thử FP8 KV; nếu kernel tốn thời gian mới profile và tune kernel. Chưa có bằng chứng thì chưa mở một sweep lớn.
6. **Kiểm tra lại ứng viên cuối:** lặp phép đo có ích để đánh giá dao động, kiểm tra chất lượng theo yêu cầu BTC, chuẩn bị script tái chạy và slides giải thích kết quả.

Lượt đo dài dùng thời lượng giống protocol BTC; bản thân việc chạy job này **chưa phải gửi bài cho BTC**, cũng chưa hoàn thành kiểm tra chất lượng model.

## File nằm ở đâu?

- [Thư mục thực nghiệm](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/README.md): scripts và cách chạy.
- [Bảng kết quả đang cập nhật](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RESULTS.md).
- [Log ứng viên 09](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22131.out).
- [Log đối chứng 07](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22135.out).
- [Log đo dài 07 sau khi warm đủ các cặp worker](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22143.out).
- [Log chạy lại đo dài 07 sau khi sửa cổng metrics](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22147.out).

Job 22130 bị lỗi tokenizer trước khi đo và được loại khỏi so sánh. Job 22131 là cấu hình 09; job 22135 là cấu hình 07 chạy lại sau khi sửa tokenizer. Các số liệu gốc nằm trong `runs/<job-id>/sweep/` và `runs/<job-id>/confirm/`; file ở `artifacts/phases/warmup/` không được dùng làm kết quả đo chính.

**Điều chỉnh theo số đo:** sweep của 07 còn gặp đường truyền KV chưa được khởi tạo, và không có mức N nào đạt SLA. Vì vậy gửi thêm job 22143: dùng 8 gateway tạm, mỗi gateway nối đúng một cặp P/D, gửi một câu ngắn để warm cặp đó, rồi tắt gateway tạm. Sau đó đo dài N32 qua gateway chính. Không đổi model hoặc số GPU; bước này nhằm tránh kết luận nhầm do warmup thiếu. Các request warm cặp worker không dùng dataset/seed benchmark; warmup 60 giây của benchmark vẫn giữ nguyên.

Một lần chạy tốt chưa đủ chứng minh speedup ổn định. Chỉ kết luận trong phạm vi cấu hình và concurrency đã thực sự đo.

**Cập nhật:** job 22143 lỗi trước benchmark vì các gateway tạm trùng cổng metrics mặc định. Đã sửa mỗi gateway dùng cổng metrics riêng và gửi lại job 22147. Đây là lỗi script warmup, không phải kết quả hiệu năng của 07.

Đọc tiếp: [Danh sách ứng viên và các lớp tối ưu](06-ung-vien-qwen.md).

**Trạng thái kiểm tra lúc 20:16 UTC, 09/10/2026:** 09/N32 vẫn là điểm duy nhất có lượt đo dài đạt SLA: 1472,73 good tokens/s, 97,84% request đạt chuẩn. Job 22147 lỗi 503 trước khi đo vì gateway `/health` thành công trong khi đăng ký workers còn chạy nền. Đã sửa warmup để retry có giới hạn đúng lỗi chưa có worker, kiểm tra tình huống này trên CPU và gửi job đối chứng 22197 (đang PENDING). Chưa chứng minh speedup của 09 so với 07; chưa thử FP8 KV/DeepEP/kernel tuning hoặc accuracy check. Báo cáo RESULTS.md được theo dõi tự động; không có job nào khác được watcher tự gửi.

**Cập nhật 20:34 UTC:** job 22197 đã hoàn tất đo dài: 07/N32 đạt 1297,02 good tokens/s và 97,24% đạt SLA. 09/N32 cao hơn 13,55% trong hai lượt đo dài; chưa có chuỗi đo lặp A/B. Gửi tiếp job 22200 để thử 09/N40 và 09/N48, giữ engine, topology, KV và backend. Báo cáo kết quả tiếp tục được watcher cập nhật.
