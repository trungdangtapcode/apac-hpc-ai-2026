# Kế hoạch thực nghiệm gọn

## 1. Quyết định theo trạng thái hiện tại

Trong workspace chỉ thấy bài kiểm tra H200, chưa thấy full-model result. Vì ngày hiện tại trùng mốc nộp công bố, ưu tiên tối đa 2–3 cấu hình có lý do, dành chỗ cho clean rerun và hồ sơ. Nếu BTC đã gia hạn thì dùng kế hoạch mở rộng ở cuối. Không mặc định hiện tại vẫn còn quyền truy cập máy hay queue giống tháng 9; kiểm tra lúc chạy.

### AI: vòng đầu

1. Kiểm tra smoke 02/03; version SGLang/AIPerf và help đúng image. Ghi model checksum/ID/config, image và flags. Không load 235B chỉ để hỏi version.
2. Baseline topology 07 với N16. Nếu fail health/memory/IB, sửa đường chạy trước khi đo throughput.
3. Đo N8/16/32/64 có điều kiện, dừng tăng khi latency hỏng. Short benchmarks 10–20 s cho ranking sơ bộ, không phải score chính thức.
4. So topology 09 tại một N đã biết để tách ảnh hưởng topology; sau đó tune N riêng nếu nó khả quan.
5. Chỉ thử 08 khi logs cho thấy prefill nghẽn và decode còn dư. Chỉ thử FP8 KV khi dtype hiện tại là BF16 hoặc có bottleneck capacity/transfer.
6. Cấu hình tốt nhất: một N duy nhất, official protocol 60/120/30, threshold 90%, command nguyên như luật. Lưu JSON, logs và entrypoint tái lập.

Một lần deploy dùng model thật có thể tốn vài phút load/compile; short benchmark không đồng nghĩa job ngắn 20 giây. Nếu gom nhiều phép đo trong một deployment để tiết kiệm load, phải giữ output từng run riêng và không chạy benchmark clients song song trên cùng workers. Để đủ 17 phút phải đo startup thực rồi tính budget, không dựa vào comment của script.

### HPC: vòng đầu

1. Xác nhận quyền vào Gadi hoặc ASPIRE và số SU còn lại.
2. Chạy Basic đúng module/method/ranks/case của máy, lưu full chain và Cd.
3. Ưu tiên một thay đổi: decomposition hoặc ranks/placement. Đừng đổi cả compiler/MPI/decomposition một lúc vì không biết phần nào có tác dụng.
4. Khi chọn được candidate, full 1/2/4 nodes với 40/80/150 steps và slides về scaling.
5. Với ASPIRE, clean MPI shutdown trước, rồi report vài lần 4-node thay vì khẳng định speedup từ một run.

## 2. Trường dữ liệu cần ghi

| AI | HPC |
|---|---|
| Job ID, nodes, image/version | Job ID, nodes, module/compiler |
| Topology P/D, TP/EP, KV dtype, N | Decomposition method/coefs, ranks, binding |
| Warmup/duration/grace và client flags | Prep chain, steps, input files |
| Good request fraction, goodput ×200 | Average seconds/step, Cd |
| TTFT/ITL distributions, errors | Rank imbalance/MPI profiling nếu có |
| Raw worker logs + AIPerf JSON | Raw solver logs + coefficient.dat |

[experiments.csv](experiments.csv) đã có mẫu ưu tiên. Status `planned` là chưa đo, không phải job đã gửi. Giá trị metrics để trống cho tới khi có logs. So một biến/lần; khi framework/backend đổi thì thêm kiểm tra correctness.

## 3. Gọi command chính thức

`official-aiperf.sh` chứa đúng command từ code block Task Rules. Chỉ là bước client: gateway phải đang chạy và script phải được gọi trong cùng job deploy. Ví dụ bên trong container AIPerf của job:

```bash
# Ví dụ, cần thay gateway host thực tế:
bash /path/to/official-aiperf.sh compute-host:8000 qwen 16
```

Không chạy lệnh minh họa này trên login node nếu gateway chưa có. N có thể do đội chọn; HOST và MODEL là endpoint/model ID thật. Official tokenizer vẫn là Instruct-2507 như luật, dù served checkpoint là bản FP8.

Script không cài thư viện, không tải weights, không gửi kết quả cho BTC. Làm việc trong thư mục output riêng để các exports không ghi đè. Việc build/container mounts/tokenizer cache là phần deploy phải chuẩn bị.

## 4. Dàn slides có thể dùng

1. Bài toán và ràng buộc: goodput/SLA cho AI; 4-node seconds/step cho HPC.
2. Baseline thật và lý do chọn nó.
3. Bottleneck có logs/trace minh họa.
4. Các thay đổi và before/after, kể cả thử nghiệm không cải thiện.
5. Accuracy/Cd và giới hạn Basic/Bonus.
6. Cấu hình cuối, scaling, rerun instructions và hạn chế/noise.

70% là giám khảo, nên log chứng minh cách tìm bottleneck và lý do lựa chọn là phần bài làm quan trọng. Basic tuning tốt được xét Bonus; đừng bỏ hồ sơ để chỉ săn một con số cao nhất.

## 5. Nếu có thêm thời gian

AI: profile riêng P/D, graph/batch/backend, EP communication, lossless draft có sẵn và kiểm chất lượng. Duy trì một Basic ổn định làm đối chứng. HPC: profiler MPI, thiết kế hierarchical theo mesh/NUMA, rebuild an toàn, rồi Bonus renumbering/decomposition khác có self-proof. Chỉ broad sweep khi dữ liệu cho thấy không gian tìm kiếm còn triển vọng.

Không có phương pháp trong danh sách được đảm bảo tăng tốc trên máy hiện tại trước khi đo.
