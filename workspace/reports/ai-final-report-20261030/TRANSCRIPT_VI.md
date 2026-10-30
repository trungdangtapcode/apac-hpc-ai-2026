# Transcript và hướng dẫn hiểu từng slide — Tiếng Việt

Đây là **lời thuyết trình mẫu và tài liệu học**, không phải bản chép lại một buổi nói đã diễn ra. Tài liệu đi theo đúng 40 slide của bản trình chiếu hiện tại. Bản tiếng Việt được tạo theo yêu cầu riêng của bạn; mã nguồn và các báo cáo khác vẫn dùng tiếng Anh.

**Cách dùng:** mở slide, đọc phần “Slide muốn nói gì”, nhìn hình theo “Cách đọc”, rồi luyện phần “Lời nói mẫu”. Các phần còn lại giúp chuẩn bị trả lời câu hỏi. Không cần đọc toàn bộ hướng dẫn thành tiếng. Hãy dùng “chúng tôi quan sát”, “giả thuyết của chúng tôi”, và “chưa xác định được” đúng với mức bằng chứng.

- **Slide 1–24:** phần AI chính. Dùng [kế hoạch 15–20 phút](PRESENTATION_PLAN.md); không đọc hết 24 lời nói mẫu nếu vượt thời gian.
- **Slide 25–32:** phần AI dự phòng khi được hỏi. Slide 31–32 vẫn thuộc nhóm dự phòng dù tiêu đề không có chữ Appendix.
- **Slide 33–40:** giải thích phần HPC đang có trong cùng deck, chỉ đọc và diễn giải. Trạng thái job trên các slide này là **ảnh chụp ngày 23/10**, không phải trạng thái trực tiếp ngày 30/10. Hướng dẫn này không cập nhật hay xác nhận kết quả HPC mới. Thời lượng AI không bao gồm mặc định phần HPC.
- Màu sắc có ý nghĩa **theo từng slide**. Cam không luôn là “thắng” hay “thua”. Ảnh nền, gradient và đường trang trí cuối slide không biểu diễn dữ liệu.
- **↑ / ↓** thường là hướng mong muốn tối ưu, không khẳng định số liệu thực tế đã tăng/giảm. “Không có trục” nghĩa là sơ đồ/bảng/card, không cần tự suy ra trục X/Y.
- Nghiên cứu đã dừng theo yêu cầu. Các việc “tiếp theo” trong slide là đề xuất hoặc câu chuyện tại thời điểm đó, không phải job mới đã chạy.

Nguồn: [PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), [PDF](../../submission-review/ai-journey-update-20261030/TripleU_APAC2026_Presentation.pdf), [bản tiếng Anh](TRANSCRIPT_EN.md). SHA-256 của PowerPoint: `b2e1c88aba8d5a3d5ec181e3fccc6b95bb6ea12c29f214e7c3c964619dc81616`. Đây là transcript của phiên bản này; đổi deck thì cần kiểm tra lại hướng dẫn.

## Từ vựng dùng xuyên suốt

| Ký hiệu / thuật ngữ | Hiểu đơn giản |
|---|---|
| request | Một prompt gửi đến dịch vụ và câu trả lời được sinh ra. |
| token | Đơn vị trong từ vựng của model: có thể là từ, mảnh từ hoặc dấu câu; không nhất thiết là một từ. |
| prefill / decode | Prefill xử lý prompt đầu vào; decode lặp lại việc sinh token tiếp theo. |
| TTFT | Thời gian chờ token đầu tiên, đơn vị mili giây (ms). Bao gồm thời gian chờ quan sát được trước token đầu tiên. |
| ITL | Độ trễ giữa các token. Ngưỡng ở đây áp dụng cho khoảng thời gian trung bình giữa các token trong từng request, đơn vị ms. |
| SLO / SLA fraction | Mục tiêu độ trễ / tỷ lệ trên toàn bộ request đồng thời đạt cả hai ngưỡng độ trễ. Đây không phải độ chính xác của model. |
| goodput | Số request đạt chuẩn mỗi giây. Điểm hiển thị chính thức bằng số này nhân 200 token đầu ra cho mỗi request. |
| N / concurrency | Số request benchmark tối đa đang được xử lý đồng thời trong tải vòng kín; không phải số GPU. |
| closed-loop | Duy trì tối đa N request đang hoạt động; một request kết thúc thì gửi request mới. Không có tốc độ gửi request cố định riêng. |
| p50 / median; p95; max | Trung vị: một nửa mẫu không vượt mức đó. p95: 95% mẫu không vượt mức đó. Max: giá trị lớn nhất quan sát được. Mean là trung bình cộng, một thống kê khác. |
| TP / EP / replica | TP chia phép tính của model; EP phân phối các expert của model MoE; replica là một bản worker khác. |
| MoE | Model có nhiều mạng expert; mỗi token được định tuyến đến một số expert thay vì kích hoạt toàn bộ expert. |
| KV cache | Key và value của attention đã lưu, biểu diễn ngữ cảnh được xử lý để dùng khi sinh các token tiếp theo. |
| NIXL | Lớp truyền dữ liệu được dùng ở đây để chuyển KV từ worker prefill sang worker decode. |
| FP8 / BF16 | Định dạng số thực 8 bit / bfloat 16 bit. Trọng số, activation và KV có thể dùng định dạng khác nhau. |
| FI / FA3 / DG / HPC-Ops | FlashInfer / FlashAttention 3 / DeepGEMM / triển khai kernel HPC-Ops được tái sử dụng. HPC-Ops không phải track HPC OpenFOAM. |
| kernel / GEMM | Một chương trình tính toán trên GPU / phép nhân ma trận tổng quát. Kernel riêng lẻ nhanh hơn chưa chắc làm cả dịch vụ nhanh hơn. |
| MNNVL / collective | Đường giao tiếp Multi-node NVLink / phép giao tiếp có nhiều rank cùng tham gia. Cần kiểm tra đường thực thi thực tế được bật. |
| CUDA graph / bucket | Đồ thị thực thi GPU được capture / một kích thước thực thi được chọn để capture. Số bucket không phải concurrency. |
| baseline / control / candidate | Cấu hình mốc / nhánh đối chứng / cấu hình thử thay đổi. Mỗi phần trăm tăng giảm cần chỉ rõ mốc so sánh. |
| matched trial / repeat | So sánh giữ các yếu tố dự định, chỉ đổi yếu tố cần thử / lần cấp tài nguyên khác để kiểm tra tái lập. Cả hai không tự động chứng minh quan hệ nhân quả. |
| ms / s / tokens/s / req/s | 1.000 ms = 1 giây. tokens/s là token mỗi giây; req/s là request mỗi giây. |
| % / percentage points | Từ 90% lên 95% là tăng 5 điểm phần trăm, hoặc tăng tương đối 5,56% so với 90%; hai cách nói khác nhau. |
| 2,989.175 / 2.989,175 | Slide dùng kiểu Anh: dấu phẩy tách hàng nghìn, dấu chấm tách phần thập phân. 2,989.175 trên slide tương đương 2.989,175 theo cách viết Việt; không phải hai kết quả khác nhau. |
| MPI rank / affinity / NUMA | Một tiến trình MPI / gắn tiến trình vào lõi CPU / kiến trúc bộ nhớ CPU có chi phí truy cập gần và xa khác nhau. Rank trong HPC CPU khác với rank serving GPU. |
| Scotch / Hierarchical / graph cut | Các phương pháp chia lưới / một phương pháp chia lưới khác / chỉ số đại diện cho biên giữa các phần chia. Cut nhỏ hơn không tự động có thời gian chạy nhanh hơn. |

## Mục lục theo slide

- [Slide 01 — Qwen serving: from topology to reproduced performance](#slide-01)
- [Slide 02 — Highest observation and strongest recommendation](#slide-02)
- [Slide 03 — Optimise useful throughput under a latency gate](#slide-03)
- [Slide 04 — One workload, two deployment systems](#slide-04)
- [Slide 05 — Separate prompt processing from token generation](#slide-05)
- [Slide 06 — Topology search established the serving layout](#slide-06)
- [Slide 07 — Make KV-transfer setup scale with the request](#slide-07)
- [Slide 08 — FP8 block geometry constrains parallelism](#slide-08)
- [Slide 09 — A repeatable experiment loop](#slide-09)
- [Slide 10 — H200 journey: recover, specialise, then reproduce](#slide-10)
- [Slide 11 — Backend combinations matter](#slide-11)
- [Slide 12 — H200: the N62-to-N64 step survives a full repeat](#slide-12)
- [Slide 13 — Profile the deployed interaction](#slide-13)
- [Slide 14 — The N60 gain survives an independent deployment](#slide-14)
- [Slide 15 — The reproduced N64 service still loses first-token tails](#slide-15)
- [Slide 16 — H100 has its own operating point and uncertainty](#slide-16)
- [Slide 17 — FA3: faster first token does not guarantee goodput](#slide-17)
- [Slide 18 — Test the cost hypothesis, then reverse the order](#slide-18)
- [Slide 19 — A local N52 calibration, not a universal multiplier](#slide-19)
- [Slide 20 — Freeze the forecast, then test it on H200](#slide-20)
- [Slide 21 — Use source evidence to test one small hypothesis](#slide-21)
- [Slide 22 — Latency acceptance is separate from model accuracy](#slide-22)
- [Slide 23 — EAGLE3: follow the failed hypothesis through its repairs](#slide-23)
- [Slide 24 — Topology → transport → kernels → replication](#slide-24)
- [Slide 25 — Appendix · diagnose performance drift with controlled cells](#slide-25)
- [Slide 26 — Appendix · profiles and source also close attractive detours](#slide-26)
- [Slide 27 — Appendix · the selected AI deployment is N64](#slide-27)
- [Slide 28 — Appendix · sparse graphs save memory, not goodput](#slide-28)
- [Slide 29 — Appendix · what the benchmark actually measures](#slide-29)
- [Slide 30 — Appendix · larger prefill chunks did not help](#slide-30)
- [Slide 31 — A real replay can invalidate a static deployment claim](#slide-31)
- [Slide 32 — What the evidence supports next](#slide-32)
- [Slide 33 — The task: same 65-million-cell airflow calculation](#slide-33)
- [Slide 34 — The whole required pipeline comes before the score](#slide-34)
- [Slide 35 — A smaller partition cut did not make the solver faster](#slide-35)
- [Slide 36 — Observed scaling changed which decomposition led](#slide-36)
- [Slide 37 — At four nodes, the winner depends on ranks per node](#slide-37)
- [Slide 38 — Keep the slow step in the mean; inspect the tail](#slide-38)
- [Slide 39 — A reproducible candidate needs more than a fast log](#slide-39)
- [Slide 40 — What we learned — and the next measurement](#slide-40)

---

<a id="slide-01"></a>

## Slide 01 — Qwen serving: from topology to reproduced performance

![Slide 01](../../submission-review/ai-journey-update-20261030/slides/assets/slide-01.png)

### Slide muốn nói gì

Mở đầu câu chuyện nghiên cứu AI và xác định phạm vi: biến một cấu hình Qwen phân tán thành phép đo dịch vụ có thể tái lập. Bài trình bày đi từ bố trí hệ thống, truyền trạng thái, tối ưu theo giai đoạn đến đo lặp; tiêu đề không khẳng định đã thắng cuộc thi hay chứng nhận chất lượng mô hình.

### Nhìn thấy gì trên slide

Ảnh nền là lối đi giữa các tủ máy chủ, được làm nhạt để dễ đọc. Màu xanh đậm dùng cho tiêu đề, màu cam cho nhãn nhiệm vụ và đường kẻ, màu xám cho ngày tháng. Đây là màu của giao diện trình bày, không mã hóa nhóm dữ liệu. Slide không có biểu đồ, trục số hay chú giải.

### Thuật ngữ và ký hiệu

- **Qwen:** Dòng mô hình ngôn ngữ dùng trong bài toán; nghiên cứu phục vụ checkpoint Qwen3-235B được chỉ định.
- **APAC HPC-AI 2026:** Bối cảnh cuộc thi của nghiên cứu, không đồng nghĩa với giải thưởng hay được ban tổ chức chấp nhận.
- **30 October 2026:** Ngày của bản cập nhật nghiên cứu; các kết quả được trình bày là ghi nhận đến ngày này.
- **VNUHCM - TripleU:** Tên nhóm trình bày.

### Cách đọc hình, trục, đơn vị và màu

- Đọc tiêu đề như hành trình từ bố trí hệ thống đến phép đo có thể lặp lại.
- Ảnh phòng máy chỉ làm nền minh họa, không phải bằng chứng về nơi triển khai đã kiểm chứng.
- Slide mở đầu không có đơn vị hoặc số đo.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Công việc đi từ khôi phục kiến trúc phục vụ hai nút và truyền KV đến thử nghiệm backend theo từng giai đoạn và các phép đo đầy đủ được lặp lại.
- **Giả thuyết:** Muốn tối ưu kernel có ý nghĩa, trước hết phải làm cho đường triển khai và phép đo đầu cuối hoạt động đúng.
- **Kết luận được hỗ trợ:** Bài trình bày sẽ đưa ra cấu hình vận hành được đo lặp và các lựa chọn có căn cứ, đồng thời tách chúng khỏi điểm cao đơn lẻ và việc xác minh accuracy chính thức.
- **Chưa biết / giới hạn:** Accuracy trên toàn bộ bộ đánh giá chính thức vẫn chưa được xác minh; kết quả cục bộ không phải thứ hạng chính thức của cuộc thi.

### Lời nói mẫu

Xin chào, chúng tôi là VNUHCM–TripleU. Đây là cập nhật nghiên cứu phục vụ Qwen đến ngày 30 tháng 10 năm 2026. Câu hỏi của chúng tôi không chỉ là làm sao để một lần chạy cho ra con số lớn hơn. Trước tiên, chúng tôi phải dựng được dịch vụ hai nút, truyền dữ liệu của yêu cầu đúng giữa xử lý prompt và sinh token, rồi đo các thay đổi backend có kiểm soát dưới những giới hạn dịch vụ. Tôi sẽ trình bày kết quả nào lặp lại được, thay đổi hấp dẫn nào không giúp ích, và điều gì dữ liệu hiện có chưa thể khẳng định. Ảnh phòng máy ở đây chỉ là nền minh họa, không phải ảnh lắp đặt thi đấu đã xác minh.

### Điều không nên nói

Không gọi đây là chiến thắng, được ban tổ chức chấp nhận, hay đã chứng nhận accuracy. Ngày tháng giới hạn kết luận ở bản cập nhật này.

### Câu chuyển slide

Trước hết, tôi sẽ nói rõ thế nào là kết quả hữu ích và cách đọc các con số chính.

---

<a id="slide-02"></a>

## Slide 02 — Highest observation and strongest recommendation

![Slide 02](../../submission-review/ai-journey-update-20261030/slides/assets/slide-02.png)

### Slide muốn nói gì

Phân biệt điểm cao nhất trong một lần chạy đầy đủ đã được rà soát với cấu hình có bằng chứng lặp lại tốt hơn. Slide nhấn mạnh rằng điểm cực đại và khuyến nghị đáng tin cậy nhất không nhất thiết là cùng một kết quả.

### Nhìn thấy gì trên slide

Hai con số lớn đặt cạnh nhau trên nền ảnh phòng máy đã làm nhạt. Nhãn màu cam phân biệt hai nhóm bằng chứng được gọi tên ở slide này; số liệu dùng màu xanh đậm. Dòng chú thích màu xám nêu điểm thô phục hồi từ thử nghiệm portable. Màu sắc không hàm ý đạt/trượt và không phải chú giải chung. Không có trục số.

### Thuật ngữ và ký hiệu

- **3,048.45 good output tokens/s:** Số đã làm tròn của một lần chạy đầy đủ qua các cổng cục bộ, job 27378; số đã rà soát chính xác là 3048.446289.
- **+0.24%:** Chênh lệch làm tròn trong cặp thử nghiệm cache prefill, chính xác +0.240921% so với đối chứng mới 27376; thấp hơn ngưỡng lợi ích dự kiến 1%.
- **3,044.40 good output tokens/s:** Trung bình của ba lần chạy N64 đầy đủ trong lịch sử; đây là chuỗi lặp riêng biệt.
- **3,055.33:** Kết quả thô portable phục hồi từ job 27145; job scheduler gốc FAILED sau khi đã đo GPU, nên không phải job phân bổ đầy đủ hoàn tất thành công.
- **tokens/s:** Số token đầu ra hữu ích mỗi giây: thông lượng tổng hợp từ các yêu cầu đạt đồng thời cổng độ trễ theo từng yêu cầu.

### Cách đọc hình, trục, đơn vị và màu

- Ô bên trái là một lần chạy đầy đủ, không phải trung bình nhiều lần.
- Ô bên phải là trung bình ba phép đo N64 đầy đủ trong lịch sử, không phải số được ghép cặp trực tiếp với lần chạy bên trái.
- Chú thích dưới cùng nói dữ liệu thô portable đã được phục hồi dù job gốc thất bại sau khi đo.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** 27378 đạt 3048.446289 good output tokens/s và qua các cổng cục bộ; mức tăng trong cặp cache so sánh là 0.240921%. Trung bình chuỗi N64 lịch sử là 3044.400475. Dữ liệu thô portable phục hồi đạt 3055.330517, nhưng job gốc mang trạng thái FAILED.
- **Giả thuyết:** Chỉ nên chọn điểm cao làm kết quả chính khi thay đổi đạt ngưỡng lợi ích đã định trước và được lặp độc lập trong so sánh phù hợp.
- **Kết luận được hỗ trợ:** Giữ N64 có kết quả lặp lại làm khuyến nghị vững hơn. Giữ 27378 là điểm cao nhất của một lần chạy đầy đủ cục bộ đã rà soát, không phải tối ưu có ích đã được chứng minh.
- **Chưa biết / giới hạn:** Riêng slide này không so sánh hai ô trong cùng điều kiện runtime; điểm raw portable cũng không phải kết quả hoàn tất đầu cuối của một phân bổ thành công.

### Lời nói mẫu

Ở đây tôi tách hai khái niệm dễ nhầm. Bên trái là điểm cao nhất trong một lần chạy đầy đủ cục bộ đã được rà soát: 3.048,45 good output tokens mỗi giây. Thay đổi trong so sánh cache tương ứng chỉ tăng 0,24%, thấp hơn ngưỡng lợi ích một phần trăm mà chúng tôi đặt ra. Bên phải là trung bình 3.044,40 của ba lần chạy N64 đầy đủ trong lịch sử. Kết quả lặp lại đó là cơ sở khuyến nghị tốt hơn dù không phải con số đơn cao nhất. Một lần chạy portable có dữ liệu raw phục hồi ở mức 3.055,33, nhưng job ban đầu thất bại sau khi đo. Chúng tôi giữ lại bằng chứng ấy mà không gọi nó là một lần triển khai thành công.

### Điều không nên nói

Không xếp hạng hai ô như thể chúng là một thử nghiệm ghép cặp. 3055,33 phục hồi không phải job scheduler đã qua và không chứng minh triển khai portable đầu cuối lặp lại được.

### Câu chuyển slide

Để hiểu thông lượng good output tokens mỗi giây, cần xem workload và cổng độ trễ ở từng yêu cầu.

---

<a id="slide-03"></a>

## Slide 03 — Optimise useful throughput under a latency gate

![Slide 03](../../submission-review/ai-journey-update-20261030/slides/assets/slide-03.png)

### Slide muốn nói gì

Định nghĩa mục tiêu benchmark trước khi bàn về thay đổi hệ thống: tối đa hóa thông lượng dịch vụ đạt chuẩn, đồng thời đủ yêu cầu riêng lẻ phải thỏa cả hai giới hạn độ trễ. Nhờ vậy không nhầm tốc độ sinh thô hay độ trễ trung bình với quy tắc chấm.

### Nhìn thấy gì trên slide

Mô tả workload nằm phía trên bảng bốn hàng. Đầu bảng xanh đậm nêu chỉ số, ý nghĩa và giới hạn/đơn vị; chữ cam nhấn mạnh cách tính. Không có biểu đồ, trục số hay chú giải màu.

### Thuật ngữ và ký hiệu

- **4,000 input tokens → 200 output tokens:** Kích thước yêu cầu tổng hợp cố định: prompt 4.000 token và yêu cầu sinh 200 token đầu ra.
- **TTFT ↓:** Time to first token, thời gian đến token đầu tiên; càng thấp càng tốt, giới hạn cho mỗi yêu cầu là 3.000 mili giây.
- **Mean ITL ↓:** Mean inter-token latency, độ trễ trung bình giữa các token được sinh trong một yêu cầu; càng thấp càng tốt, giới hạn 20 mili giây.
- **Joint SLA ↑:** Tỷ lệ tất cả yêu cầu được đánh giá đồng thời đạt hai giới hạn độ trễ; mục tiêu ít nhất 90%. Lỗi vẫn nằm trong mẫu số.
- **Goodput ↑:** Tốc độ yêu cầu đạt chuẩn. Nhân số yêu cầu đạt chuẩn mỗi giây với 200 để tính good output tokens mỗi giây.
- **ms:** Mili giây, bằng một phần nghìn giây; đơn vị độ trễ.
- **req/s × 200:** Số yêu cầu đạt chuẩn mỗi giây nhân với 200 token đầu ra được yêu cầu trên mỗi yêu cầu.

### Cách đọc hình, trục, đơn vị và màu

- Mũi tên chỉ hướng mong muốn: độ trễ giảm, tỷ lệ đạt và goodput tăng.
- Một yêu cầu phải đồng thời đạt TTFT và mean ITL mới được tính là đạt chuẩn.
- Ngưỡng 90% áp dụng trên toàn bộ yêu cầu được đánh giá, không chỉ yêu cầu thành công.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Benchmark cố định kích thước yêu cầu và áp dụng quy tắc độ trễ kết hợp theo từng yêu cầu; lỗi vẫn bị tính. Goodput dựa trên các yêu cầu qua cả hai giới hạn.
- **Giả thuyết:** Hệ thống sinh nhiều token thô hơn vẫn có thể kém hơn nếu quá nhiều yêu cầu vi phạm thời gian token đầu hoặc khoảng cách token.
- **Kết luận được hỗ trợ:** Chúng tôi đánh giá cấu hình bằng throughput đạt chuẩn cùng các cổng độ trễ và đầu ra, không chỉ bằng một giá trị trung bình hay lượng token thô.
- **Chưa biết / giới hạn:** Bảng định nghĩa giao thức nhưng không có số đo của ứng viên nào; nó không cho biết phân bố độ trễ thực tế của từng cấu hình.

### Lời nói mẫu

Mục tiêu của chúng tôi là thông lượng hữu ích dưới một cổng độ trễ. Mỗi yêu cầu tổng hợp có 4.000 token đầu vào và yêu cầu 200 token đầu ra. Một yêu cầu chỉ đạt nếu thời gian đến token đầu tiên không quá 3.000 mili giây và khoảng cách token trung bình không quá 20 mili giây. Ít nhất 90% tất cả yêu cầu được đánh giá phải đồng thời đạt hai giới hạn; lỗi cũng bị tính. Goodput là số yêu cầu đạt chuẩn mỗi giây, nhân với 200 sẽ thành good output tokens mỗi giây được trình bày. Vì vậy độ trễ trung bình riêng lẻ không thể cho biết dịch vụ có qua hay không: quyết định được tính ở từng yêu cầu.

### Điều không nên nói

Không suy ra tỷ lệ đạt theo từng yêu cầu từ một giá trị trung bình tổng hợp. Không bỏ lỗi khỏi mẫu số và không thay 200 bằng độ dài đầu ra khác.

### Câu chuyển slide

Khi đã cố định mục tiêu đo, slide tiếp theo cho thấy vì sao mọi so sánh phải đi cùng thông tin nền tảng.

---

<a id="slide-04"></a>

## Slide 04 — One workload, two deployment systems

![Slide 04](../../submission-review/ai-journey-update-20261030/slides/assets/slide-04.png)

### Slide muốn nói gì

Trình bày hai môi trường phần cứng dùng trong các nghiên cứu nền tảng riêng biệt và đặt nguyên tắc: mỗi so sánh phải nêu nền tảng, topology, backend và tải. Dùng chung workload và checkpoint không làm hai cụm tương đương nhau.

### Nhìn thấy gì trên slide

Bảng hai cột so sánh Firmus với NSCC ASPIRE 2A+. Đầu bảng xanh đậm phân biệt cột; dòng kết luận màu cam nhấn mạnh quy tắc so sánh. Ảnh phòng máy nhạt chỉ làm nền. Không có trục số hay chú giải.

### Thuật ngữ và ký hiệu

- **2 × 8 H200:** Hai nút, mỗi nút có tám GPU NVIDIA H200; tổng cộng mười sáu GPU trong phân bổ Firmus.
- **2 × 8 H100 80GB:** Hai nút NSCC ASPIRE 2A+, mỗi nút có tám GPU H100 bộ nhớ 80 gigabyte. Đây là thế hệ GPU và môi trường khác.
- **Slurm / PBS:** Hai bộ lập lịch cụm khác nhau dùng để yêu cầu và quản lý tài nguyên tính toán.
- **Pyxis / native Enroot:** Đường khởi chạy container trên Firmus. NSCC dùng Singularity.
- **SGLang / AIPerf:** Engine phục vụ và client benchmark của nghiên cứu; cùng các image đã staging được dùng trên hai hệ thống.
- **Qwen3-235B FP8:** Mô hình/checkpoint và độ chính xác trọng số được giữ chung trong thiết lập so sánh nền tảng.
- **80GB:** Dung lượng bộ nhớ GPU danh định mỗi H100 như bảng ghi; đây không phải đơn vị hiệu năng.

### Cách đọc hình, trục, đơn vị và màu

- Các hàng mô tả phân bổ GPU, scheduler, công cụ chạy container, serving/client và mô hình.
- Bảng ghi cùng image và checkpoint đã staging, nhưng GPU và phần mềm triển khai khác nhau.
- Dòng màu cam cuối slide là nguyên tắc nghiên cứu, không phải kết quả biểu đồ.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Cả hai hệ thống đều cấp mười sáu GPU trên hai nút và dùng cùng image serving/client cùng checkpoint, nhưng khác phần cứng, scheduler và bộ khởi chạy container.
- **Giả thuyết:** Giữ workload và mô hình giống nhau là cần thiết, nhưng khác biệt phần cứng và phần mềm vẫn có thể làm thay đổi hiệu năng.
- **Kết luận được hỗ trợ:** Luôn gắn nền tảng, topology, backend và tải với từng kết quả; không quy đổi điểm H100 thành H200 chỉ dựa vào tên GPU.
- **Chưa biết / giới hạn:** Slide không định lượng ảnh hưởng riêng của từng khác biệt nền tảng và không đưa ra công thức đổi điểm H100 sang H200 tổng quát.

### Lời nói mẫu

Chúng tôi làm việc trên hai hệ thống triển khai. Firmus có hai nút, mỗi nút tám GPU H200, được quản lý bằng Slurm và chạy qua Pyxis hoặc Enroot. NSCC ASPIRE 2A+ có hai nút H100 tám GPU, mỗi GPU 80 gigabyte, dùng PBS và Singularity. Chúng tôi staging cùng image phục vụ và client, đồng thời dùng cùng checkpoint Qwen, nhưng máy và stack triển khai vẫn khác. Vì vậy mỗi phép so sánh cần ghi rõ nền tảng, topology, backend và tải. Tên GPU hay dung lượng bộ nhớ không phải hệ số đổi hiệu năng.

### Điều không nên nói

Không gộp phép đo H100 và H200 thành một chuỗi hoặc cho rằng hiệu năng tương đương chỉ vì số GPU và image phần mềm giống nhau.

### Câu chuyển slide

Tiếp theo, ta xem topology H200 mười sáu GPU đã chọn và lần theo yêu cầu trong hệ thống.

---

<a id="slide-05"></a>

## Slide 05 — Separate prompt processing from token generation

![Slide 05](../../submission-review/ai-journey-update-20261030/slides/assets/slide-05.png)

### Slide muốn nói gì

Giải thích thiết kế serving tách rời: dành một nút cho prefill prompt và nút còn lại cho decode tự hồi quy, sau đó truyền trạng thái KV của từng yêu cầu giữa hai vai trò. Hình nối vị trí phần cứng với các thử nghiệm layout và truyền dữ liệu tiếp theo.

### Nhìn thấy gì trên slide

Hai khung trên Node 0 chứa worker prefill P0 và P1; khung lớn trên Node 1 chứa worker decode D0. Bốn dấu GPU màu cam trong mỗi khung P và tám dấu xanh đậm trong D0 thể hiện phân bổ GPU ghi trong hình. Mũi tên cam có nhãn KV state/NIXL đi từ prefill đến decode. Ảnh nền chỉ trang trí. Đây là sơ đồ, không phải biểu đồ số, nên không có trục hay chú giải; màu chỉ phân biệt vai trò trong sơ đồ này.

### Thuật ngữ và ký hiệu

- **Prefill:** Giai đoạn xử lý prompt. Nó đọc token đầu vào và tạo trạng thái KV cần cho quá trình sinh.
- **Decode:** Giai đoạn sinh token tự hồi quy. Nó dùng trạng thái KV của prompt để tạo token đầu ra được yêu cầu.
- **P0 / P1 / D0:** Tên hai worker prefill và một worker decode; đây là nhãn worker, không phải mã GPU.
- **TP4 / TP8:** Tensor parallelism trên bốn hoặc tám GPU trong một worker. TP là cách chia mô hình.
- **EP1 / EP8:** Expert parallelism trên một hoặc tám phân vùng expert của mô hình mixture-of-experts.
- **KV state:** Dữ liệu key/value attention được tạo trong prefill và cần để tiếp tục decode cùng yêu cầu.
- **NIXL:** Cơ chế truyền dùng ở đây để chuyển dữ liệu KV giữa phía prefill và decode.
- **2 × 4 + 1 × 8 = 16 GPUs:** Hai worker prefill, mỗi worker bốn GPU, cộng một worker decode tám GPU; tổng cộng mười sáu GPU.

### Cách đọc hình, trục, đơn vị và màu

- Đọc từ trái sang phải: yêu cầu vào một trong hai P0/P1 để prefill, rồi trạng thái KV được chuyển sang D0 để sinh đầu ra.
- Mỗi worker prefill dùng TP4/EP1; worker decode dùng TP8/EP8. Nhóm TP nằm trong cùng nút.
- Các ô vuông và mũi tên cam chỉ vai trò trong sơ đồ này, không phải thước đo lưu lượng hay quy ước màu chung.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Layout được chọn bố trí hai worker prefill TP4/EP1 ở Node 0 và một worker decode TP8/EP8 ở Node 1; trạng thái KV của yêu cầu phải đi qua giữa hai vai trò.
- **Giả thuyết:** Tách xử lý prompt khỏi sinh token có thể cho mỗi giai đoạn topology phù hợp hơn, nhưng bổ sung đường truyền nhạy với độ đúng và thời gian khởi động.
- **Kết luận được hỗ trợ:** Bộ định tuyến round-robin phân yêu cầu cho worker prefill; decode sinh mọi token đầu ra. Sơ đồ mô tả kiến trúc thí nghiệm, tự nó chưa chứng minh lợi ích hiệu năng.
- **Chưa biết / giới hạn:** Hình không định lượng băng thông mạng, độ trễ truyền, mức sử dụng tài nguyên hay lợi thế nhân quả so với triển khai thống nhất.

### Lời nói mẫu

Đây là cấu hình tách rời trên mười sáu GPU. Nút bên trái chạy hai worker prefill, P0 và P1, mỗi worker dùng bốn GPU với TP4 và EP1. Nút bên phải chạy một worker decode trên tám GPU với TP8 và EP8. Yêu cầu được gửi đến một worker prefill để xử lý prompt và tạo trạng thái key/value, hay KV. NIXL chuyển trạng thái của yêu cầu đó sang worker decode, nơi sinh toàn bộ token đầu ra. Các ô và mũi tên cam đánh dấu phía prefill và đường truyền trong hình; chúng không biểu thị lượng dữ liệu đo được. Tách hai vai trò tạo topology để khảo sát, nhưng cũng khiến độ đúng và thời gian sẵn sàng của đường truyền trở thành một phần của dịch vụ.

### Điều không nên nói

Thông số TP/EP chỉ đúng cho từng worker trong cấu hình cụ thể này. Không xem mỗi ô vuông là mức sử dụng GPU đo được và không nói sơ đồ đã chứng minh tăng tốc.

### Câu chuyển slide

Slide tiếp theo cho thấy các thử nghiệm topology ban đầu dẫn đến cách chia này, đồng thời tách bạch thất bại với cấu hình thay thế.

---

<a id="slide-06"></a>

## Slide 06 — Topology search established the serving layout

![Slide 06](../../submission-review/ai-journey-update-20261030/slides/assets/slide-06.png)

### Slide muốn nói gì

Cho thấy một số kết quả tìm kiếm topology và giải thích cấu hình được chọn đến từ các thử nghiệm đo được, dùng được. Chú thích phía dưới bảo toàn lịch sử: cấu hình thay thế là thử nghiệm mới, không phải sửa hồi tố cho lần thất bại ban đầu.

### Nhìn thấy gì trên slide

Bảng liệt kê mã layout, cách bố trí prefill, cách bố trí decode, N và good tokens/s. Đầu bảng và chữ dùng xanh đậm; dòng tổng kết in đậm đếm cấu hình, bên dưới là lưu ý màu xám. Ảnh nền đã làm nhạt chỉ để trang trí. Không có trục số, điểm dữ liệu đồ họa hay chú giải màu.

### Thuật ngữ và ký hiệu

- **07 / 09:** Mã định danh của các thử nghiệm layout đầu tiên, không phải phiên bản phần mềm.
- **4 × TP2 / 2 × TP4:** Bốn worker prefill với tensor parallelism bằng hai; hàng kế tiếp dùng hai worker prefill với tensor parallelism bằng bốn.
- **TP4/EP4:** Worker decode cấu hình tensor parallelism bốn và expert parallelism bốn.
- **Selected split: 2 × TP4; 1 × TP8/EP8:** Hai worker prefill, mỗi worker TP4, và một worker decode TP8/EP8.
- **N:** Concurrency của client: mục tiêu số yêu cầu được giữ đang xử lý đồng thời, không phải số GPU hoặc token.
- **good tokens/s:** Thông lượng token đầu ra đạt chuẩn theo cổng độ trễ từng yêu cầu.
- **14 + 3 = 17 usable configurations:** Mười bốn layout gốc đã đo cộng ba cấu hình thay thế EP2 đã đo trong sổ phục hồi.

### Cách đọc hình, trục, đơn vị và màu

- So sánh mỗi hàng theo topology của hai vai trò, concurrency N và good output tokens mỗi giây.
- N tăng từ 32 lên 40 rồi 48 trong các hàng minh họa; tải và lịch sử truyền dữ liệu cũng khác nhau.
- Con số tổng kết đếm cấu hình đo được và dùng được; nó không nói mọi layout thử đều thành công.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Trong mẫu topology ban đầu, cách chia được chọn đạt 1912,30 good tokens/s ở N48; các cấu hình hiển thị tại N32 và N40 lần lượt đạt 1297,02 và 1666,01. Sổ phục hồi đếm tổng cộng 14 layout gốc cộng ba cấu hình thay thế EP2.
- **Giả thuyết:** Phân bổ cân bằng giữa số worker prefill và mức song song decode có thể phục vụ tốt hơn mức concurrency đã chọn.
- **Kết luận được hỗ trợ:** Các thử nghiệm tạo ra kiến trúc có thể tiếp tục phát triển. Đây là các điểm vận hành ban đầu, chưa phải thứ hạng nhân quả sạch vì tải và lịch sử truyền khác nhau.
- **Chưa biết / giới hạn:** Slide không liệt kê đủ 17 cấu hình hoặc khoảng tin cậy; không thể tách riêng thay đổi topology nào gây ra chênh lệch điểm.

### Lời nói mẫu

Bảng này cho ba mốc trong quá trình tìm topology. Layout 07 dùng bốn worker prefill TP2 và hai worker decode TP4/EP4; tại concurrency 32, nó đạt 1.297 good tokens mỗi giây. Layout 09 mở rộng prefill thành hai worker TP4 và đạt 1.666 ở concurrency 40. Cách chia được chọn dùng hai worker prefill TP4 và một worker decode TP8/EP8, đạt 1.912 ở concurrency 48. Tải và lịch sử truyền không giống nhau, vì vậy hãy xem đây là các mốc kiến trúc, không phải phép quét nhân quả có kiểm soát. Sổ phục hồi có 14 layout gốc đã đo và ba cấu hình thay thế EP2 đã đo. Cấu hình thay thế là một phép thử khác; layout gốc thất bại vẫn được ghi là thất bại.

### Điều không nên nói

Không hiểu 07 hay 09 là phiên bản phần mềm. Không quy toàn bộ tăng thông lượng cho topology đang hiển thị vì N và lịch sử thử nghiệm cũng khác.

### Câu chuyển slide

Trở ngại kế tiếp không chỉ là chọn mức song song: khởi động lạnh đã xử lý metadata KV nhiều hơn nhu cầu của một yêu cầu rất nhiều.

---

<a id="slide-07"></a>

## Slide 07 — Make KV-transfer setup scale with the request

![Slide 07](../../submission-review/ai-journey-update-20261030/slides/assets/slide-07.png)

### Slide muốn nói gì

Giải thích vì sao khởi tạo KV khi chạy lạnh được thiết kế lại theo các trang mà yêu cầu thật sự truyền. So sánh số liệu là hình học descriptor, cho thấy quy mô liệt kê metadata; slide chủ ý không trình bày đây là mức tăng tốc suy luận.

### Nhìn thấy gì trên slide

So sánh hai cột: “Whole KV pool” bên trái màu xanh đậm và “Request pages only” bên phải màu cam. Giá trị trái là 403,8 triệu source entries mỗi rank; bên phải là 188 mục đã gộp liên tục cho mỗi yêu cầu. Dòng cuối biểu diễn chuỗi xác minh. Ảnh nền chỉ trang trí. Không có trục số hay cột dữ liệu; màu cam chỉ nhấn mạnh cục bộ, không phải chú giải đạt/trượt.

### Thuật ngữ và ký hiệu

- **KV pool:** Toàn bộ không gian địa chỉ cache key/value được cấp cho một rank, phần lớn không cần truyền cho một yêu cầu cụ thể.
- **403.8 million source entries per rank:** Số gần đúng entry nguồn của descriptor được liệt kê cho hình học toàn pool trong ví dụ TP8 đại diện.
- **188 coalesced entries per request:** Số dải descriptor liên tục sau khi gộp các trang kề nhau trong hình học yêu cầu 4.000 token minh họa.
- **rank:** Một tiến trình/phân vùng mô hình phân tán tham gia triển khai song song; không phải thứ hạng cuộc thi.
- **descriptor:** Metadata mô tả các dải bộ nhớ cho lớp truyền; bản thân nó không phải nội dung tensor KV.
- **coalescing:** Gộp các dải bộ nhớ liền kề thành ít mô tả dải lớn hơn.
- **CPU range tests → GPU transfer → response checks:** Chuỗi xác minh nhiều lớp: kiểm tra tính toán địa chỉ, thử truyền thật trên GPU, rồi kiểm tra ý nghĩa phản hồi yêu cầu.

### Cách đọc hình, trục, đơn vị và màu

- Số bên trái là liệt kê nguồn cho cả pool trên mỗi rank; số bên phải là các dải đã gộp cho một yêu cầu. Phạm vi hai số khác nhau.
- Đơn vị của số liệu là số descriptor, không phải giây, byte mỗi giây hay điểm benchmark.
- Chuỗi cuối slide là các cổng bằng chứng tiếp nối. Ánh xạ CPU đúng chưa đủ; vẫn cần thử truyền GPU thật và kiểm tra phản hồi.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Serving tách rời khi khởi động lạnh bị chậm ở bước chuẩn bị descriptor cho toàn bộ pool KV. Phiên bản theo yêu cầu tạo dải cho các trang thật sự truyền và gộp dải liên tục; ví dụ TP8 cho thấy khoảng 403,8 triệu entry pool so với 188 entry cho một yêu cầu.
- **Giả thuyết:** Liệt kê trang theo yêu cầu thay vì toàn pool sẽ giảm khối lượng chuẩn bị mà không làm đổi ánh xạ KV của yêu cầu.
- **Kết luận được hỗ trợ:** Tính đúng của dải được kiểm tra trên CPU, sau đó thử bằng truyền GPU thật và kiểm tra phản hồi. Một đường EP2 sau đó trông như chạy được nhưng vẫn trượt kiểm tra đầu ra ngắn; khởi động thành công là điều kiện cần, chưa đủ.
- **Chưa biết / giới hạn:** Số descriptor không đo thời gian khởi động, thông lượng suy luận, bộ nhớ tiết kiệm hay mức tăng tốc hai triệu lần. Ví dụ hình học không phải tỷ lệ phổ quát cho mọi yêu cầu hay topology.

### Lời nói mẫu

Điều tra khởi động lạnh cho thấy bước chuẩn bị truyền KV đang liệt kê descriptor cho toàn bộ pool cache, trong khi một yêu cầu chỉ chạm đến một phần nhỏ. Với hình học TP8 đại diện, có khoảng 403,8 triệu source entries mỗi rank, so với 188 dải đã gộp cho một yêu cầu 4.000 token. Đây là số lượng mô tả truyền, không phải thời gian và không phải tăng tốc suy luận hai triệu lần. Chúng tôi sửa để chỉ mô tả các trang mà yêu cầu cần rồi gộp các dải liền kề. Chúng tôi kiểm tra ánh xạ trên CPU, sau đó xác minh truyền GPU thật và phản hồi. Một đường EP2 sau đó có vẻ chạy nhưng vẫn không tạo đủ phản hồi hợp lệ. Bài học là chuẩn bị hiệu quả và truyền thành công vẫn chưa chứng minh đầu ra dịch vụ đúng.

### Điều không nên nói

Không chia hai số rồi gọi kết quả là tăng tốc suy luận. Phạm vi đếm khác nhau và hình không đưa ra độ trễ hay thông lượng. Truyền hoàn tất không đồng nghĩa phản hồi hợp lệ.

### Câu chuyển slide

Lần khôi phục EP2 cũng làm lộ một điều kiện tiên quyết khác: các block trọng số FP8 phải khớp với cách chia mô hình.

---

<a id="slide-08"></a>

## Slide 08 — FP8 block geometry constrains parallelism

![Slide 08](../../submission-review/ai-journey-update-20261030/slides/assets/slide-08.png)

### Slide muốn nói gì

Giải thích một lỗi triển khai cụ thể do căn chỉnh block FP8 và thay đổi hình học dùng để khôi phục một cách chia tương thích. Bài học là tương thích cho phép thử tải, nhưng chưa chứng minh dịch vụ hay chất lượng chạy thành công.

### Nhìn thấy gì trên slide

Slide so sánh TP8/EP1 bên trái với TP8/EP2 bên phải. Phân vùng bên trái được vẽ thành block xanh đậm ghi 128 cộng block đỏ ghi 64, cho thấy phần block FP8 không đầy; bên phải có ba block màu cam ghi 128. Màu đỏ chỉ phía lỗi và màu cam chỉ các block đầy trong sơ đồ này. Đây là màu giải thích cục bộ, không phải chú giải chung. Không có trục.

### Thuật ngữ và ký hiệu

- **FP8:** Định dạng trọng số dấu phẩy động 8-bit của checkpoint; trọng số được tổ chức thành block có độ rộng cố định trong đường kernel liên quan.
- **1,536:** Kích thước chiều trung gian MoE dùng trong phép tính phân vùng này.
- **128:** Độ rộng block FP8 trong đường triển khai này; một phần đầy tương thích gồm 128 phần tử.
- **TP8 / EP1:** Tensor parallelism tám phần với một expert partition; tensor parallelism MoE hiệu dụng là tám, cho 1536 ÷ 8 = 192 phần tử mỗi phân vùng.
- **128 + 64:** Phân vùng 192 phần tử chứa một block đầy 128 và phần dư 64, không phải block FP8 đầy đủ.
- **TP8 / EP2:** Tensor parallelism tám phần với hai expert partition; tensor parallelism MoE hiệu dụng là bốn, cho 1536 ÷ 4 = 384 phần tử.
- **3 × 128 = 384:** Phân vùng EP2 khớp ba block 128 phần tử đầy đủ. Đây là đổi bố trí, không loại bỏ expert hay trọng số.
- **SLA:** Thỏa thuận mức dịch vụ: quy tắc chấp nhận độ trễ kết hợp theo yêu cầu đã nêu ở slide trước.

### Cách đọc hình, trục, đơn vị và màu

- Đọc hai phép tính trước: 1536 ÷ 8 = 192 và 1536 ÷ 4 = 384.
- Các khối trái biểu thị 128 cộng 64; phần đỏ là block chưa đầy và gây lỗi tải trong đường đã thử.
- Các khối phải là ba đoạn 128 đầy đủ. Chân trang liệt kê các cổng còn phải kiểm tra: startup, SLA và chất lượng đầu ra.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Phân vùng prefill TP8/EP1 có 192 phần tử, bằng 128 cộng 64 và không căn với block FP8 rộng 128. Với EP2, tensor parallelism MoE hiệu dụng là bốn và mỗi phân vùng có 384 phần tử, tức ba block đầy.
- **Giả thuyết:** Đổi cách chia expert có thể làm tensor tương thích yêu cầu block FP8 của kernel mà vẫn giữ toàn bộ trọng số và expert.
- **Kết luận được hỗ trợ:** Cấu hình thay thế EP2 sửa hình học block trong đường đã thử và cho phép thử triển khai tương thích. Đây là thay đổi kết hợp của layout, không phải tăng tốc TP đơn lẻ; tương thích chỉ là điều kiện cần.
- **Chưa biết / giới hạn:** Chỉ căn chỉnh đúng chưa chứng minh khởi động thành công, đạt SLA theo yêu cầu, chất lượng đầu ra hay tăng hiệu năng. Hình là phép tính kích thước, không phải so sánh throughput đo được.

### Lời nói mẫu

Đây là lý do một cấu hình prefill thất bại trước khi đo hiệu năng. Chiều trung gian MoE của mô hình là 1.536 và đường FP8 này cần block 128 phần tử. Với TP8 và EP1, mỗi phân vùng có 1.536 chia 8, tức 192 phần tử. Kết quả là một block đủ 128 cộng phần dư 64, nên kernel không tải được block chưa đầy. Với TP8 và EP2, tensor parallelism MoE hiệu dụng là bốn. Mỗi phân vùng có 384 phần tử, đúng ba block 128. Cách này vẫn giữ các trọng số và expert, nhưng đổi cách chia mô hình. Vì vậy phía bên phải cho thấy hình học tương thích, không phải chiến thắng hiệu năng. Startup, độ trễ dịch vụ và chất lượng đầu ra vẫn phải kiểm tra riêng.

### Điều không nên nói

Số đỏ 64 là phần dư của phân vùng trọng số, không phải 64 GPU hay token. EP2 làm đổi cấu hình; không gọi đây là tăng tốc tensor parallelism đơn lẻ hoặc kết quả throughput.

### Câu chuyển slide

Khi đường triển khai đã khả thi, slide kế tiếp mô tả cách biến mỗi lời giải thích như vậy thành thử nghiệm có kiểm soát.

---

<a id="slide-09"></a>

## Slide 09 — A repeatable experiment loop

![Slide 09](../../submission-review/ai-journey-update-20261030/slides/assets/slide-09.png)

### Slide muốn nói gì

Mô tả kỷ luật bằng chứng dùng để quyết định ý tưởng nào đáng chạy và nhánh nào nên đóng. Slide nối các câu chuyện kỹ thuật ban đầu với kết quả backend đo sau đó, đồng thời ghi rõ các pha đo đầy đủ.

### Nhìn thấy gì trên slide

Bốn giai đoạn đánh số chạy từ trái sang phải: giả thuyết, thử nghiệm có kiểm soát, xác minh, rồi lặp lại hoặc đóng. Số màu cam chỉ dẫn thứ tự; chữ xanh đậm mô tả giai đoạn. Đường kẻ phân cách quy trình với thời lượng 60/120/30 và workload. Không có trục hay chú giải biểu đồ.

### Thuật ngữ và ký hiệu

- **01–04:** Số thứ tự của bốn bước thí nghiệm, không phải điểm số hay mã job.
- **60 s warmup:** Một phút khởi động theo giao thức đo trước cửa sổ tính điểm.
- **120 s measurement:** Cửa sổ tính điểm hai phút của giao thức đo đầy đủ được trình bày.
- **30 s grace:** Khoảng chờ sau phép đo để yêu cầu đang xử lý hoàn tất; không phải một giai đoạn steady-state tính điểm khác.
- **closed loop:** Client giữ số yêu cầu đang xử lý ở mức mục tiêu và thay yêu cầu mới khi một yêu cầu hoàn tất.
- **4,000 / 200 tokens:** Kích thước cố định của token đầu vào và đầu ra được yêu cầu như slide trước.
- **SLA accounting:** Đánh giá độ trễ và thành công theo từng yêu cầu, kể cả tính yêu cầu lỗi vào mẫu số.

### Cách đọc hình, trục, đơn vị và màu

- Bước 1 dùng log, trace và source để hình thành giả thuyết; bước 2 thay một yếu tố được xác định rõ.
- Bước 3 xác minh giao thức, runtime thực sự kích hoạt, SLA và đầu ra; bước 4 xác nhận lợi ích có ý nghĩa hoặc đóng nhánh thua.
- Thời lượng bên dưới tính bằng giây, không phải mili giây. Cửa sổ đo kéo dài 120 giây.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Quy trình lưu lại cả giao thức benchmark và các cổng runtime/đầu ra, đồng thời phân biệt job đã kết thúc với kết quả hợp lệ đã được rà soát.
- **Giả thuyết:** Thay đổi giới hạn rõ, có đối chứng và quy tắc dừng sẽ tạo bằng chứng dễ diễn giải hơn so với quét rộng hoặc lặp mù.
- **Kết luận được hỗ trợ:** Ứng viên cần kiểm tra thực tế việc kích hoạt và lặp lại độc lập trước khi chọn; job thiếu bản xuất hợp lệ hoặc không đạt cổng chưa chứng minh được kết quả.
- **Chưa biết / giới hạn:** Sơ đồ chỉ tóm tắt quy trình; không cho thấy thử nghiệm, chi phí, tỷ lệ lỗi hay thống kê lặp cụ thể nào.

### Lời nói mẫu

Quy trình của chúng tôi có bốn bước. Đầu tiên, dùng log, trace và source để hình thành giả thuyết. Thứ hai, thay đổi một yếu tố xác định so với đối chứng. Thứ ba, xác nhận đúng thiết lập đã thực sự chạy, rồi kiểm tra giao thức, SLA theo từng yêu cầu và đầu ra. Cuối cùng, lặp độc lập kết quả có ích hoặc đóng nhánh. Giao thức đầy đủ trên slide dùng 60 giây warmup, 120 giây đo và 30 giây grace để yêu cầu còn lại hoàn tất. Grace không phải thời gian steady-state tính điểm bổ sung. Kỷ luật này giúp giữ lại job thất bại, phân biệt trạng thái terminal với kết quả hợp lệ, và dừng những thay đổi có thật nhưng quá nhỏ để chọn dùng.

### Điều không nên nói

Sơ đồ bốn bước không chứng minh mọi thử nghiệm lịch sử đều dùng một giao thức giống hệt. Mỗi kết quả cần dẫn đúng giao thức và hồ sơ job của nó.

### Câu chuyển slide

Tiếp theo, tôi tóm tắt tiến trình H200, đồng thời lưu ý đây không phải một thí nghiệm tích lũy duy nhất.

---

<a id="slide-10"></a>

## Slide 10 — H200 journey: recover, specialise, then reproduce

![Slide 10](../../submission-review/ai-journey-update-20261030/slides/assets/slide-10.png)

### Slide muốn nói gì

Tóm lược theo lịch sử goodput H200 khi hệ thống được khôi phục, dùng backend theo từng giai đoạn, rồi đạt các điểm vận hành có phép đo lặp. Đây là bản đồ để định hướng cho bằng chứng chi tiết ở các slide sau, không phải biểu đồ ablation nhân quả.

### Nhìn thấy gì trên slide

Biểu đồ cột đứng có chín nhãn phân loại trên trục hoành: Initial 07 N32; Initial 09 N40; PD split N48; FI + MNNVL N52; Prefill DG N56; DG + HPC N58; N60 repeated; N62 repeated; N64 three repeats. Trục tung là Good output tokens/s, có vạch 0, 500, 1000, 1500, 2000, 2500 và 3000; đơn vị là good output tokens mỗi giây. Nhãn cột được làm tròn: 1.297; 1.666; 1.912; 2.631; 2.716; 2.939; 2.989; 3.023; 3.044. Ba cột đầu màu xám, hai cột kế xanh đậm, bốn cột cuối màu cam để chia giai đoạn chủ đề; màu không biểu thị đạt/trượt và không có ý nghĩa chung ngoài biểu đồ này. Slide không vẽ chú giải. Chân trang nói rõ tải và thiết lập runtime thay đổi.

### Thuật ngữ và ký hiệu

- **H200:** Nền tảng GPU của các mốc này; không gộp các giá trị với kết quả H100.
- **Trục hoành: milestones và N:** Các giai đoạn thí nghiệm dạng phân loại và concurrency của client, không phải thời gian đã trôi qua hay biến liên tục. N là số yêu cầu mục tiêu đang xử lý đồng thời.
- **Trục tung: Good output tokens/s:** Thông lượng token đầu ra đạt chuẩn theo cổng độ trễ kết hợp; nhãn cột đã làm tròn.
- **FI:** FlashInfer, backend attention trong giai đoạn có nhãn tương ứng.
- **MNNVL:** Backend collective/truyền thông dùng trong tổ hợp phía decode.
- **DG:** DeepGEMM, dùng cho prefill ở các mốc có nhãn này.
- **HPC:** Backend decode HPC-Ops trong mốc “DG + HPC”.
- **N60 / N62 / N64 repeated:** Các điểm vận hành đầy đủ về sau có phép đo lặp; cột N64 ở 3.044 tóm tắt trung bình ba lần chạy đầy đủ lịch sử.

### Cách đọc hình, trục, đơn vị và màu

- Đọc trục hoành như chuỗi mốc lịch sử có tên; khoảng cách không phải thời gian hoặc khoảng đều nhau.
- Đọc trục tung theo good output tokens mỗi giây, càng lên cao giá trị càng lớn; nhãn số đã làm tròn.
- Màu xám, xanh đậm và cam chỉ phân nhóm chủ đề trong biểu đồ này. Chúng không chỉ đạt/trượt.
- Chân trang nhắc tải và runtime thay đổi giữa các mốc; cột cao hơn về sau tự nó không phải quan hệ nhân quả.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Biểu đồ đi từ layout ban đầu N32–N48 sang chuyên biệt hóa backend và các điểm N60, N62, N64 được đo lặp về sau. Nhãn N64 3.044 là trung bình đã làm tròn của ba lần chạy đầy đủ lịch sử.
- **Giả thuyết:** Sau khi khôi phục split và đường truyền dùng được, tinh chỉnh attention, collective và prefill theo từng giai đoạn có thể tăng throughput đạt chuẩn.
- **Kết luận được hỗ trợ:** Biểu đồ ghi lại tiến trình và dẫn đến các so sánh ghép cặp cùng phép lặp ở slide sau; nó là bản đồ mốc nghiên cứu, không chứng minh mức tăng nhân quả tích lũy đơn điệu.
- **Chưa biết / giới hạn:** Tải, runtime và điều kiện quan sát lịch sử thay đổi. Biểu đồ không thể quy toàn bộ mức tăng cho một thay đổi, tính độ bất định thống kê hay xác định tối ưu toàn cục.

### Lời nói mẫu

Biểu đồ này là bản đồ hành trình nghiên cứu H200, không phải một ablation tích lũy duy nhất. Trục ngang liệt kê các mốc thí nghiệm phân loại và concurrency N, từ layout đầu tiên ở N32 và N40, split được chọn ở N48, các thử nghiệm backend, đến N60, N62 và N64 sau này. N là số yêu cầu mục tiêu được giữ đang xử lý; không phải thời gian. Trục đứng là good output tokens mỗi giây. Chúng tôi khôi phục split, kết hợp attention FlashInfer với MNNVL, đưa DeepGEMM vào prefill, rồi thử decode HPC-Ops. N60, N62 và N64 có bằng chứng lặp; cột N64 làm tròn thành 3.044 từ ba lần chạy đầy đủ lịch sử. Màu xám, xanh và cam chỉ phân nhóm chủ đề. Vì tải và runtime thay đổi, các cột tăng dần không chứng minh từng thay đổi gây ra toàn bộ mức tăng.

### Điều không nên nói

Trục hoành là phân loại chứ không phải thời gian. Không nội suy giữa các mốc hoặc xem màu là chú giải đạt/trượt. Không gọi đây là ablation nhân quả hay tối ưu toàn cục.

### Câu chuyển slide

Slide tiếp theo phóng to một so sánh có kiểm soát hơn: tổ hợp backend attention và collective ở cùng mức tải H200.

---

<a id="slide-11"></a>

## Slide 11 — Backend combinations matter

![Slide 11](../../submission-review/ai-journey-update-20261030/slides/assets/slide-11.png)

### Slide muốn nói gì

Giới thiệu kết quả tương tác backend chi tiết đầu tiên: tổ hợp attention và collective vượt các lựa chọn riêng trong so sánh H200 N52 cùng tải. Bài học thiết kế là phải đo trực tiếp tương tác, không cộng số học các mức tăng riêng lẻ.

### Nhìn thấy gì trên slide

Bảng bốn hàng ghi cấu hình, mã job, good tokens/s và SLA ở H200, N52. Đầu bảng xanh đậm; câu kết màu cam nhấn mạnh cần đo tổ hợp trực tiếp. Ảnh nền chỉ trang trí. Không có trục số, cột biểu đồ hay chú giải màu.

### Thuật ngữ và ký hiệu

- **H200 · N52:** Nền tảng GPU và concurrency của client trong so sánh này. N52 là mục tiêu giữ 52 yêu cầu đang xử lý.
- **FlashInfer decode only:** Đường attention decode dùng FlashInfer trong khi cấu hình collective giữ ở thiết lập đối chứng.
- **MNNVL decode only:** Đường collective/truyền thông decode dùng MNNVL, chưa kết hợp FlashInfer như hàng cuối.
- **MNNVL fresh control:** Phép đo đối chứng mới ở thiết lập MNNVL, dùng để giảm phụ thuộc vào một điểm so sánh cũ.
- **MNNVL + FlashInfer:** Tổ hợp backend được đo trực tiếp trong job 23904.
- **good tokens/s:** Token đầu ra đạt chuẩn mỗi giây theo cổng độ trễ cấp yêu cầu.
- **SLA:** Tỷ lệ phần trăm yêu cầu đồng thời đạt TTFT và mean ITL; các giá trị hiển thị là đo cục bộ.
- **job:** Mã hồ sơ scheduler liên kết hàng với bằng chứng lần chạy; không phải thứ hạng.

### Cách đọc hình, trục, đơn vị và màu

- So sánh 23777 (2.440,39), 23778 (2.592,16) và tổ hợp 23904 (2.631,09) như bằng chứng thăm dò cùng tải.
- Đối chứng MNNVL mới 23974 đạt 2.594,03, là so sánh liên quan hơn với tổ hợp; chênh lệch khoảng 1,43%.
- Mọi giá trị SLA đều là phần trăm. Bảng không có trục; thứ tự hàng không biểu diễn thời gian hay xếp hạng thống kê.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Ở H200 N52, decode FlashInfer đơn đạt 2440.386 good tokens/s; decode MNNVL đạt 2592.162; đối chứng MNNVL mới đạt 2594.028; tổ hợp đạt 2631.085. So với đối chứng mới, tổ hợp cao hơn khoảng 1,43%; SLA xấp xỉ 99%.
- **Giả thuyết:** Lựa chọn kernel attention có thể tương tác với lựa chọn collective, vì vậy cần thử hiệu năng dịch vụ của chúng như một cấu hình kết hợp thay vì cộng các mức tăng riêng.
- **Kết luận được hỗ trợ:** Tổ hợp là một điểm vận hành đáng nghiên cứu và cho thấy nên đo cùng lúc attention với truyền thông. Kiểm tra runtime và phép lặp sau bổ sung bằng chứng, nhưng riêng bảng này không tạo quy tắc backend phổ quát.
- **Chưa biết / giới hạn:** Mức tăng nhỏ và các điểm đơn lẻ không xác lập tác động nhân quả rộng, khoảng tin cậy hay tính cộng tuyến tính của từng thành phần. SLA không đại diện cho accuracy mô hình chính thức.

### Lời nói mẫu

Bảng này so sánh các lựa chọn backend trên H200 ở concurrency N52. FlashInfer decode riêng đạt khoảng 2.440 good tokens mỗi giây. MNNVL riêng đo được khoảng 2.592, còn đối chứng MNNVL mới đạt 2.594. Tổ hợp MNNVL và FlashInfer được đo trực tiếp đạt khoảng 2.631, cao hơn đối chứng mới khoảng 1,43% trong các phép đo này. SLA theo yêu cầu đều gần 99%. Bài học không phải là cộng các mức tăng riêng lẻ. Attention và collective tương tác với nhau, nên chúng tôi đo tổ hợp như một cấu hình riêng. Kiểm tra kích hoạt runtime và phép lặp về sau bổ sung bằng chứng cho vùng vận hành này, nhưng riêng bảng không tạo khẳng định phổ quát cho mọi workload hay backend.

### Điều không nên nói

Không cộng hai thay đổi riêng để dự đoán điểm của tổ hợp. Đây không phải phân bố nhiều lần chạy, và SLA độ trễ không chứng nhận accuracy mô hình.

### Câu chuyển slide

Các slide tiếp theo kiểm tra sâu hơn các kết quả backend này, gồm bằng chứng profile và phép lặp ghép cặp của xử lý N60.

---

<a id="slide-12"></a>

## Slide 12 — H200: the N62-to-N64 step survives a full repeat

![Slide 12](../../submission-review/ai-journey-update-20261030/slides/assets/slide-12.png)

### Slide muốn nói gì

Giải thích vì sao chọn N64: so sánh đầy đủ và lần lặp độc lập ủng hộ mức tăng vừa phải; tín hiệu tốt từ phép thử N68 ngắn không còn đáng kể khi đo đầy đủ.

### Nhìn thấy gì trên slide

Đọc bảng từ trái sang phải: control N62 đầy đủ, run N64 nguồn và lần lặp N64 độc lập. Các hàng là goodput, SLA đồng thời, TTFT trung bình, ITL trung bình và lỗi/hủy.

### Thuật ngữ và ký hiệu

- **N62/N64:** Mức concurrency client được cấu hình; không phải số GPU hay batch decode.
- **Good tokens/s:** Tốc độ request đủ điều kiện nhân mục tiêu output cố định 200 token.
- **SLA đồng thời:** Tỷ lệ request đạt cả TTFT và ITL trung bình/request.
- **60/120/30:** Số giây warmup / đo điểm / grace.
- **N68:** Sàng lọc concurrency cao hơn nhưng gain giảm ở cặp đầy đủ.

### Cách đọc hình, trục, đơn vị và màu

- Lần triển khai N64 độc lập 25373 lặp lại ở 3.044,075, thấp hơn nguồn chỉ 0,014%. Đọc lần lượt các cột goodput, SLA đồng thời, TTFT trung bình, ITL trung bình và lỗi/hủy. Throughput tăng nhưng TTFT trung bình nhích lên và SLA giảm nhẹ. Protocol gồm warmup 60 giây, đo 120 giây, grace 30 giây. Sàng lọc ngắn N68 gợi ý +2,27%, nhưng cặp đầy đủ chỉ còn +0,083%; phép chạy ngắn để sàng lọc, không thay thế phép đo chính. Hai lần N64 dùng cùng tập GPU UUID được lấy mẫu, nên chỉ hỗ trợ khả năng lặp cục bộ, không tạo khoảng tin cậy hay optimum toàn cục. Giả thuyết: concurrency vừa phải cải thiện sử dụng pipeline. Kết luận: giữ N64 tại operating point đã đo. Chưa biết riêng đóng góp của hàng đợi, truyền dữ liệu và tính toán.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** N64 tăng 1,083% và lặp trong khoảng 0,014%; TTFT nhích lên, SLA giảm nhẹ.
- **Giả thuyết:** Concurrency client tăng vừa phải có thể cải thiện sử dụng pipeline.
- **Kết luận được hỗ trợ:** Giữ N64 đã lặp lại tại điểm đo này.
- **Chưa biết / giới hạn:** Chưa biết riêng đóng góp queue, transfer, compute và optimum toàn cục.

### Lời nói mẫu

“N62 đạt khoảng 3.012 good output token mỗi giây. N64 đạt 3.044 và một lần triển khai độc lập lặp lại gần như vậy. Đây là mức tăng khoảng 1,08% trong protocol đầy đủ. TTFT tăng nhẹ, ITL quanh 15 mili giây. Sàng lọc N68 có vẻ tốt hơn nhưng kết quả đầy đủ gần như mất lợi thế. Chúng tôi giữ N64 nhờ có đối chứng đầy đủ và lần lặp, không gọi đây là tối ưu toàn cục.”

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

“Tiếp theo dùng trace để chọn câu hỏi chẩn đoán.”

---

<a id="slide-13"></a>

## Slide 13 — Profile the deployed interaction

![Slide 13](../../submission-review/ai-journey-update-20261030/slides/assets/slide-13.png)

### Slide muốn nói gì

Giải thích cách dùng profile để đặt câu hỏi có thể kiểm chứng tiếp theo, đồng thời tách tỷ trọng kernel trong phép chẩn đoán khỏi hiệu năng dịch vụ đầu cuối.

### Nhìn thấy gì trên slide

Bảng ba hàng liệt kê thành phần decode, tỷ trọng tổng thời lượng kernel đã ghi và câu hỏi nghiên cứu tương ứng. Đây là bảng, không phải biểu đồ thanh. Phần trăm mô tả tổng thời lượng kernel, không phải tỷ trọng thời gian đầu cuối.

### Thuật ngữ và ký hiệu

- **GEMM:** Phép nhân ma trận tổng quát trong kernel tính toán.
- **MNNVL:** Backend giao tiếp qua NVIDIA NVLink.
- **RMSNorm:** Phép chuẩn hóa căn bậc hai trung bình bình phương.
- **Kernel duration:** Thời lượng kernel GPU được ghi; không phải wall time đầu-cuối.
- **N48/N58:** Hai mức concurrency tách biệt cho diagnostic và deployment lặp.

### Cách đọc hình, trục, đơn vị và màu

- Các nhóm decode được nêu là HPC group GEMM 21,642%, MNNVL collective/RMSNorm 23,479%, và FlashInfer paged attention 15,064% tổng kernel duration đã ghi. Đây là tổng mô tả, không phải tỷ trọng wall time đầu cuối: kernel có thể chạy chồng lấp và trace chỉ ghi hoạt động có coverage. GEMM là phép nhân ma trận; MNNVL là backend giao tiếp; RMSNorm chuẩn hóa activation; rank là một tiến trình phân tán. Ba nhóm gợi ý câu hỏi về MoE, chiến lược giao tiếp và attention theo pha. Chúng không dự đoán mức tăng tương ứng, chứng minh FLOP saturation, hay giải thích nhân quả kết quả dịch vụ N58/N60. Cần tách N48 diagnostic khỏi lần lặp N60. Giả thuyết: nhóm kernel lớn đáng khảo sát. Kết luận: dùng trace để thiết kế phép thử dịch vụ có đối chứng. Chưa biết tỷ lệ latency từng pha cho mỗi request.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Ba nhóm kernel chiếm tỷ lệ đã nêu trong tổng kernel duration được ghi.
- **Giả thuyết:** Nhóm có tỷ lệ ghi nhận lớn có thể gợi ý thí nghiệm tiếp.
- **Kết luận được hỗ trợ:** Dùng profile để đặt giả thuyết, không giải thích toàn bộ dịch vụ.
- **Chưa biết / giới hạn:** Tỷ trọng wall time, chồng lấp, FLOP saturation và quan hệ nhân quả chưa biết.

### Lời nói mẫu

“Các tỷ lệ profile giúp chỉ ra câu hỏi tiếp theo. Đây là tổng kernel duration trong diagnostic N48 riêng, không phải phần thời gian của request. Kernel có thể chồng lấp. Chúng tôi dùng trace để chọn thí nghiệm có đối chứng, không coi tỷ lệ này là mức tăng tốc có thể đạt.”

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

“Một so sánh N60 đầy đủ kiểm tra tương tác backend.”

---

<a id="slide-14"></a>

## Slide 14 — The N60 gain survives an independent deployment

![Slide 14](../../submission-review/ai-journey-update-20261030/slides/assets/slide-14.png)

### Slide muốn nói gì

Chứng minh một đánh đổi backend có lần lặp: thông lượng hữu ích và khoảng token tốt hơn vẫn có thể đi cùng thời gian chờ token đầu xấu hơn.

### Nhìn thấy gì trên slide

So sánh control auto-decode N60 đầy đủ với lần lặp decode HPC-Ops. Goodput và ITL cải thiện trong khi TTFT trung bình tăng.

### Thuật ngữ và ký hiệu

- **HPC-Ops:** Decode runner/backend được cung cấp trong treatment.
- **DeepGEMM:** Backend nhân ma trận prefill được giữ cố định.
- **TTFT:** Thời gian tới token đầu, tính bằng mili giây.
- **ITL:** Độ trễ giữa token; ở đây là trung bình theo request.
- **N60:** Mức concurrency client trong phép so sánh đầy đủ.

### Cách đọc hình, trục, đơn vị và màu

- Cả hai giữ DeepGEMM prefill và chunk 8192 tại full N60. TTFT trung bình tăng 125,335 ms (822,292 lên 947,627), còn ITL trung bình của request giảm 1,644 ms (16,579 xuống 14,934). SLA đồng thời là 98,7599% so với 98,8178%. Treatment ban đầu 24738 đạt 2.990,151; lần lặp 24913 thấp hơn 0,033%. Lần lặp gần bằng củng cố tính tái lập của tương tác này. HPC-Ops là backend được cung cấp, không phải kernel do nhóm phát minh. TTFT là thời gian tới token đầu; ITL là khoảng giữa token; SLA đồng thời cần đạt cả hai giới hạn. Kết luận: bằng chứng dịch vụ đầy đủ hỗ trợ cấu hình này, không chứng minh HPC-Ops luôn hơn. Chất lượng full-set official chưa xác minh; không suy ra nguyên nhân kernel cụ thể.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Goodput tăng 5,295%, ITL giảm, TTFT trung bình tăng 125,335 ms; treatment lặp gần bản đầu.
- **Giả thuyết:** Tương tác backend decode có thể tăng throughput hữu ích tại N60.
- **Kết luận được hỗ trợ:** Bằng chứng hỗ trợ cấu hình ghép cặp này, không phải ưu thế phổ quát.
- **Chưa biết / giới hạn:** Nguyên nhân kernel chính xác và quality full-set official chưa biết.

### Lời nói mẫu

“Goodput tăng khoảng 5,30%, và lần lặp gần như trùng treatment ban đầu. Nhưng TTFT xấu hơn khoảng 125 mili giây trong khi ITL cải thiện. Đây là tradeoff được lặp lại tại N60, không phải tuyên bố phổ quát.”

### Điều không nên nói

Mũi tên xuống ở hàng TTFT chỉ hướng mong muốn; TTFT thực tế tăng trong cặp này. Không nói mọi chỉ số độ trễ đều tốt hơn hoặc nhóm tự phát minh HPC-Ops.

### Câu chuyển slide

“Biểu đồ tiếp theo cho thấy miss theo từng request thay vì trung bình.”

---

<a id="slide-15"></a>

## Slide 15 — The reproduced N64 service still loses first-token tails

![Slide 15](../../submission-review/ai-journey-update-20261030/slides/assets/slide-15.png)

### Slide muốn nói gì

Cho thấy cần xem từng request: hiệu năng trung bình cao vẫn có những request chờ token đầu quá lâu; số trung bình không giải thích được nguyên nhân của phần đuôi này.

### Nhìn thấy gì trên slide

Mỗi chấm là một request. X là TTFT (ms), Y là ITL trung bình mỗi request (ms). Đường đỏ dọc/ngang lần lượt đánh dấu TTFT 3.000 ms và ITL 20 ms. Teal đậm (#23373B; có thể nhìn xanh lam-lục) đạt cả hai; cam (#EB811B; có thể nhìn vàng) trượt ít nhất một. Vùng xanh nhạt chỉ đánh dấu TTFT. Chấm đậm do chồng điểm/alpha, không phải nhóm mới.

### Thuật ngữ và ký hiệu

- **TTFT:** Thời gian từ khi request bắt đầu tới token đầu, mili giây.
- **Request-mean ITL:** Khoảng cách trung bình token của request đó, mili giây.
- **Đạt đồng thời:** TTFT ≤ 3.000 ms VÀ ITL trung bình ≤ 20 ms.
- **Đạt/tổng:** 1.875 request đạt cả hai trên toàn bộ 1.902 request.
- **Alpha overlap:** Điểm chồng làm vùng đậm hơn; không phải lớp kết quả riêng.

### Cách đọc hình, trục, đơn vị và màu

- Trục X là TTFT mili giây; Y là ITL trung bình mỗi request. Hai đường đỏ dọc/ngang đánh dấu 3.000 ms và 20 ms. Request chỉ đạt nếu ở bên trái và phía dưới cả hai đường. Điểm teal đạt đồng thời; cam trượt ít nhất một điều kiện. Vùng xanh nhạt chỉ biểu diễn TTFT, không xác nhận ITL. Cụm đậm hơn là chồng alpha, không phải nhóm thứ ba. Kết quả: 1.875/1.902, tức 98,580%, đạt đồng thời; 27 trượt TTFT, không trượt ITL, không lỗi/hủy request. TTFT trung bình/p95 là 1.108,869/1.311,693 ms; ITL trung bình/p95 là 15,0075/15,1930 ms. Mọi miss bắt đầu trong 13,004 ms từ lúc mở admission đo; đây chỉ là tương quan. Giả thuyết: nhóm request đầu có thể chịu một hiệu ứng khởi đầu. Kết luận: mọi miss SLA quan sát được trong run này chỉ thuộc TTFT. Chưa biết nguyên nhân và phân tách queue/prefill/transfer/compute.
- Đi sang trái là chờ token đầu ít hơn; đi xuống là khoảng token trung bình ngắn hơn. Vùng đạt nằm bên trái hoặc ngay trên đường x = 3000 VÀ bên dưới hoặc ngay trên đường y = 20; bằng ngưỡng vẫn đạt. Chấm cam được vẽ to hơn để dễ thấy lỗi, không có nghĩa request lớn hơn hay nhiều token hơn.
- Đây là phân bố các request trong một lần chạy, không phải đường biên tối ưu giữa nhiều cấu hình. Hình không tách được thời gian chờ hàng đợi, tính prefill, truyền KV và decode.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** 1.875/1.902 cùng đạt; 27 chỉ trượt TTFT và không có lỗi request.
- **Giả thuyết:** Hiệu ứng nhóm request đầu có thể góp phần gây miss TTFT.
- **Kết luận được hỗ trợ:** Dạng miss quan sát trong run này được xác định là chỉ trượt TTFT.
- **Chưa biết / giới hạn:** Thời điểm admission chỉ là tương quan; nguyên nhân theo pha chưa rõ.

### Lời nói mẫu

“Mỗi chấm là một request. Nó chỉ đạt nếu TTFT không quá 3.000 ms và ITL không quá 20 ms. Teal đạt cả hai; cam trượt ít nhất một. Có 1.875 trên 1.902 đạt; cả 27 miss đều do TTFT. Thời điểm gần admission đáng khảo sát nhưng không chứng minh startup là nguyên nhân.”

### Điều không nên nói

Dải xanh chỉ đánh dấu TTFT, không phải vùng đạt đồng thời. Giữ mọi request trong mẫu số.

### Câu chuyển slide

“Tiếp theo xem H100 như operating point riêng.”

---

<a id="slide-16"></a>

## Slide 16 — H100 has its own operating point and uncertainty

![Slide 16](../../submission-review/ai-journey-update-20261030/slides/assets/slide-16.png)

### Slide muốn nói gì

Tách điểm vận hành H100, cài đặt backend và biến động giữa các lần chạy khỏi các tuyên bố trên H200.

### Nhìn thấy gì trên slide

Đỉnh đơn lẻ lịch sử H100 và control N54 đầy đủ mới được đặt cạnh settings backend và song song hóa H100.

### Thuật ngữ và ký hiệu

- **H100/H200:** Hai hệ thống GPU với operating point được đo riêng.
- **N54:** Concurrency client của so sánh H100.
- **TP8:** Tensor parallelism trên tám GPU.
- **EP8:** Expert parallelism trên tám phân vùng.
- **Chunk 4096:** Kích thước chunk prefill của cấu hình H100 này.

### Cách đọc hình, trục, đơn vị và màu

- Control đầy đủ mới 225227 đạt 2.399,186728 với SLA đồng thời 98,015873%, không lỗi/hủy. H100 dùng HPC-Ops cho prefill và decode, chunk 4096, TP8/EP8; H200 dùng DeepGEMM prefill và chunk 8192. Vì vậy đây không phải so sánh phần cứng ghép cặp hay hệ số quy đổi. Giữ cả đỉnh và control mới vì chúng trả lời câu hỏi khác nhau. TP là tensor parallelism; EP là expert parallelism. EAGLE truyền dữ liệu chức năng được không đồng nghĩa có kết quả hiệu năng aggregate được chấp nhận. Giả thuyết: mỗi họ phần cứng cần settings riêng. Kết luận: báo riêng điểm H100 cùng cấu hình thật. Chưa biết hiệu ứng nhân quả giữa thế hệ GPU hay hệ số phổ quát.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Đỉnh đơn lẻ lịch sử cao hơn control đầy đủ mới; cấu hình khác H200.
- **Giả thuyết:** Mỗi họ phần cứng có thể cần cấu hình riêng.
- **Kết luận được hỗ trợ:** Báo H100 như operating point riêng.
- **Chưa biết / giới hạn:** Chưa xác lập hiệu ứng thế hệ ghép cặp hay hệ số phổ quát.

### Lời nói mẫu

“Đỉnh H100 lịch sử khoảng 2.433, còn control N54 đầy đủ mới khoảng 2.399 và đạt 98,016 phần trăm SLA đồng thời. Recipe H100 khác H200 nên đây là quan sát riêng, không phải phép quy đổi phần cứng.”

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

“Trong H100, một thay đổi attention decode kiểm tra liệu token đầu nhanh hơn có cải thiện toàn request không.”

---

<a id="slide-17"></a>

## Slide 17 — FA3: faster first token does not guarantee goodput

![Slide 17](../../submission-review/ai-journey-update-20261030/slides/assets/slide-17.png)

### Slide muốn nói gì

Dùng phép thử decode FA3 không thành công để giải thích vì sao chỉ tối ưu thời gian token đầu có thể làm mục tiêu thông lượng cuối cùng xấu đi.

### Nhìn thấy gì trên slide

Bảng H100 N54 so FlashInfer với FA3 về goodput, TTFT trung bình, ITL trung bình và latency request trung bình.

### Thuật ngữ và ký hiệu

- **FlashInfer:** Backend attention decode của control.
- **FA3:** Backend attention decode treatment; prefill vẫn dùng FA3.
- **Goodput:** Số output token đủ điều kiện trên giây.
- **Request latency:** Thời lượng request đầu-cuối, gồm sinh token.
- **Cặp ghép:** Hai run đầy đủ chỉ khác yếu tố attention decode định thử.

### Cách đọc hình, trục, đơn vị và màu

- FlashInfer so với FA3: good tokens/s 2.420,945 và 2.401,284; TTFT trung bình 713,199 và 594,276 ms; ITL 18,214 và 18,988 ms; latency request 4.337,853 và 4.372,813 ms. FA3 giảm 118,922 ms tới token đầu, nhưng ITL tăng 0,773 ms; khoảng 199 khoảng token làm phát sinh xấp xỉ 154 ms. Latency request tăng và goodput giảm 0,812%. Giữ FlashInfer cho decode setting này; FA3 vẫn dùng ở prefill. Một cặp không thể xếp hạng backend phổ quát hay chỉ ra chính xác nhân quả kernel.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** FA3 giảm TTFT nhưng làm xấu ITL/latency request và mất 0,812% goodput.
- **Giả thuyết:** Lựa chọn attention làm thay đổi chi phí startup và từng token khác nhau.
- **Kết luận được hỗ trợ:** Giữ FlashInfer cho decode này; FA3 vẫn dùng cho prefill.
- **Chưa biết / giới hạn:** Một cặp không xếp hạng backend chung hay xác định nhân quả kernel.

### Lời nói mẫu

“FA3 giảm TTFT nhưng khoảng token dài hơn. Trên toàn đầu ra, phần tăng này lớn hơn khoản tiết kiệm ban đầu: latency request tăng, goodput giảm. Chúng tôi giữ FlashInfer cho cấu hình decode này.”

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

“Tiếp theo đánh giá thay đổi chi phí startup với ngưỡng đặt trước.”

---

<a id="slide-18"></a>

## Slide 18 — Test the cost hypothesis, then reverse the order

![Slide 18](../../submission-review/ai-journey-update-20261030/slides/assets/slide-18.png)

### Slide muốn nói gì

Giải thích giá trị của việc đảo thứ tự thử và giữ ngưỡng chấp nhận đã đặt trước, thay vì chọn kết quả thuận lợi đầu tiên.

### Nhìn thấy gì trên slide

Hai cặp đầy đủ H100 cho thấy walltime off/read-first, mức tiết kiệm, thay đổi goodput và cổng chi phí định trước.

### Thuật ngữ và ký hiệu

- **Read-first:** Treatment startup đọc dữ liệu checkpoint prefill trước.
- **Walltime:** Thời gian chạy scheduler đo bằng giây.
- **Đảo thứ tự:** Phép xác nhận chạy hai arm theo thứ tự ngược.
- **Cổng chi phí:** Điều kiện định trước tiết kiệm walltime tối thiểu 10%.
- **Thay đổi goodput:** Chênh throughput đủ điều kiện so với control ghép cặp.

### Cách đọc hình, trục, đơn vị và màu

- Cặp đầy đủ đầu: off/read-first 934/759 giây, tiết kiệm 18,74%, goodput −0,66%. Cặp xác nhận đảo thứ tự: 854/770 giây, tiết kiệm 9,84%, goodput −0,33%. Cổng định trước yêu cầu tiết kiệm ít nhất 10% và goodput giảm không quá 2%; phép xác nhận đạt điều kiện throughput nhưng trượt ngưỡng walltime nên không promote. Cache chưa rõ trạng thái và node khác nhau nên không thể quy nguyên nhân cho cold storage. Walltime là thời lượng scheduler, không phải throughput ổn định.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Lần đầu tiết kiệm 18,74%; xác nhận đảo thứ tự 9,84%, dưới cổng 10%.
- **Giả thuyết:** Read-first có thể giảm walltime startup.
- **Kết luận được hỗ trợ:** Đóng nhánh, không promote vì phép xác nhận trượt cổng.
- **Chưa biết / giới hạn:** Cache và khác biệt node không cho phép quy cho cold storage.

### Lời nói mẫu

“Cặp đầu tiết kiệm 18,74%, nhưng đảo thứ tự chỉ còn 9,84%, thấp hơn cổng 10% đã công bố. Goodput chỉ đổi nhẹ. Vì phép xác nhận trượt ngưỡng, chúng tôi đóng nhánh thay vì promote kết quả thuận lợi đầu tiên.”

### Điều không nên nói

Không chỉ báo cặp đầu thuận lợi. Cache chưa rõ nên diễn giải nhân quả bị giới hạn.

### Câu chuyển slide

“Một câu hỏi riêng là liệu tỷ số phần cứng cục bộ dự báo được tải gần kề không.”

---

<a id="slide-19"></a>

## Slide 19 — A local N52 calibration, not a universal multiplier

![Slide 19](../../submission-review/ai-journey-update-20261030/slides/assets/slide-19.png)

### Slide muốn nói gì

Đặt một cầu nối đo được nhưng có phạm vi giữa hai hệ thống, và giải thích vì sao đây không phải quy tắc đổi mọi kết quả H100 sang H200.

### Nhìn thấy gì trên slide

Trung bình full protocol của H100 và H200 ở cùng combo N52 tạo thành một tỷ số quan sát không đơn vị.

### Thuật ngữ và ký hiệu

- **N52:** Concurrency client của điểm calibration này.
- **Allocation:** Một lần phân bổ tài nguyên/run theo lịch.
- **Tỷ số hệ thống:** Goodput trung bình H200 chia H100 trong phép đo này.
- **Không đơn vị:** Tỷ số không mang đơn vị vật lý.
- **Điểm calibration:** Một tải/cấu hình, không phải đường quy đổi đã xác thực.

### Cách đọc hình, trục, đơn vị và màu

- Tỷ số H200/H100 quan sát là 1,188096805, không đơn vị. Nó chỉ mô tả điểm đo này. Lặp ở một tải không định nghĩa hàm quy đổi hay prediction interval; không áp dụng tỷ số cho TTFT, ITL, SLA hay nhánh backend khác. Allocation là lần phân bổ tài nguyên, không phải thế hệ phần cứng độc lập. Giả thuyết: calibration cục bộ có thể hỗ trợ dự báo held-out gần kề. Kết luận: chỉ dùng làm đầu vào dự báo có phạm vi. Chưa biết biến thiên theo tải/cấu hình và uncertainty.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.
- Hai trung bình in trên slide là 2.215,460 và 2.632,181 good output tokens/s, lần lượt từ hai lần cấp tài nguyên H100 và bốn lần H200. Tỷ số 1,188096805 không có đơn vị; tại điểm đo này nó tương ứng thông lượng hệ thống cao hơn khoảng 18,81%, không phải tăng 18,81 điểm phần trăm SLA.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Trung bình N52 cho tỷ số H200/H100 cục bộ 1,188096805.
- **Giả thuyết:** Calibration cục bộ có thể hỗ trợ điểm held-out gần kề.
- **Kết luận được hỗ trợ:** Xem là tỷ số giới hạn, không phải quy luật đổi phần cứng.
- **Chưa biết / giới hạn:** Biến thiên theo tải, settings và metric latency chưa biết.

### Lời nói mẫu

“Ở cùng combo N52, goodput H200 chia H100 là 1,1881. Đây là liên hệ hệ thống cục bộ, không phải hệ số quy đổi phổ quát. Slide sau kiểm tra một dự báo đã khóa tại N50.”

### Điều không nên nói

Tỷ số chỉ áp dụng cho tải/cấu hình nêu; không phải phần trăm hay hệ số đổi latency.

### Câu chuyển slide

“Giờ kiểm tra dự báo được cố định trước khi thấy dữ liệu H200 held-out.”

---

<a id="slide-20"></a>

## Slide 20 — Freeze the forecast, then test it on H200

![Slide 20](../../submission-review/ai-journey-update-20261030/slides/assets/slide-20.png)

### Slide muốn nói gì

Minh họa kiểm tra dự báo minh bạch: khóa dự báo trước, thử một điểm chưa dùng để hiệu chỉnh, rồi báo cả việc đạt dung sai lẫn phần bất định còn thiếu.

### Nhìn thấy gì trên slide

Dự báo được khóa trước kết quả được so với phép đo H200 N50 held-out, sai số có dấu và dung sai.

### Thuật ngữ và ký hiệu

- **Held-out:** Quan sát để riêng kiểm tra dự báo đã khóa.
- **Sai số có dấu:** Chênh lệch tương đối; âm nghĩa là đo thấp hơn dự báo.
- **Dung sai ±2%:** Cổng vận hành định trước, không phải khoảng tin cậy 95%.
- **Sensitivity range:** Phạm vi biến thiên đầu vào trước đó, ở đây thiếu model error.
- **N50:** Concurrency client của phép kiểm tra dự báo.

### Cách đọc hình, trục, đơn vị và màu

- Job held-out 24272 đo 2.601,629; sai số có dấu −1,5371%, trong dung sai vận hành định trước ±2%. Kết quả nằm ngoài sensitivity range cũ vì phạm vi đó bỏ sót model error. Dung sai không phải khoảng tin cậy 95% hay thanh sai số đo. Không fit lại tỷ số sau khi thấy điểm này. Một phép held-out đạt chỉ hỗ trợ kiểm tra cục bộ, không chứng minh độ đúng dự báo rộng.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.
- Dấu âm nghĩa là phép đo thấp hơn dự báo: 2.601,629 so với 2.642,244 good output tokens/s. Sai số có dấu bằng (đo − dự báo) / dự báo × 100; ký hiệu ± là dung sai cho phép hai phía, không phải thanh sai số của phép đo.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Sai số held-out −1,5371%, trong ±2% nhưng ngoài sensitivity range thiếu sót.
- **Giả thuyết:** Calibration N52 có thể dự báo throughput N50 gần kề.
- **Kết luận được hỗ trợ:** Một cổng cục bộ đạt; vẫn ghi rõ thiếu model error.
- **Chưa biết / giới hạn:** Độ chính xác rộng và uncertainty đầy đủ chưa biết.

### Lời nói mẫu

“Dự báo được khóa trước khi có kết quả. H200 đo 2.601,629 so với 2.642,244 dự đoán, sai số −1,5371%. Kết quả trong dung sai vận hành định trước, nhưng ngoài sensitivity range cũ chưa đầy đủ. Chúng tôi giữ cả hai phát hiện và không fit lại.”

### Điều không nên nói

±2% là dung sai vận hành, không phải khoảng tin cậy. Không fit lại sau khi thấy held-out.

### Câu chuyển slide

“Tiếp theo so sánh các giả thuyết nhỏ dựa trên source bằng outcome đầy đủ.”

---

<a id="slide-21"></a>

## Slide 21 — Use source evidence to test one small hypothesis

![Slide 21](../../submission-review/ai-journey-update-20261030/slides/assets/slide-21.png)

### Slide muốn nói gì

Giải thích cách giữ hoặc đóng ý tưởng có cơ sở từ source sau phép đo đầy đủ; đường code hợp lý hay mức tăng nhỏ chưa đủ để đưa vào cấu hình chính.

### Nhìn thấy gì trên slide

Các hàng nối từng giả thuyết dựa trên source với quan sát đầy đủ và quyết định giữ hay đóng.

### Thuật ngữ và ký hiệu

- **Bằng chứng source:** Code và runtime xác nhận đường nào được chọn/kích hoạt.
- **Exact-ID preflight:** Kiểm tra batching tokenizer giữ đúng token ID.
- **p95 TTFT:** Phân vị 95 TTFT; thước đo phần đuôi.
- **Cổng useful-gain:** Ngưỡng định trước để promote.
- **Prefill/decode:** Xử lý prompt / sinh token tự hồi quy.

### Cách đọc hình, trục, đơn vị và màu

- Source và runtime activation xác nhận code path chạy, không chứng minh bottleneck. Mỗi quyết định dựa trên kết quả full có control và ngưỡng useful-gain. p95 là đuôi phân vị 95, không phải trung bình. Không cộng phần trăm giữa các nhánh.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Gain nhỏ không đạt ngưỡng; tail cache hoặc goodput attention xấu hơn.
- **Giả thuyết:** Settings có cơ sở source có thể cải thiện một metric dịch vụ.
- **Kết luận được hỗ trợ:** Chỉ promote thay đổi đã kích hoạt, ghép cặp và có gain đầy đủ hữu ích.
- **Chưa biết / giới hạn:** Chưa xác lập bottleneck chung hay hiệu ứng ở cấu hình khác.

### Lời nói mẫu

“Flag chạy được mới chỉ là khởi đầu. Chúng tôi xác nhận activation, chạy protocol đầy đủ và so với control. Gain nhỏ dưới ngưỡng không được promote; ITL tốt hơn nhưng mất 6,39% goodput cũng không phải cải thiện.”

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

“Latency dịch vụ và độ chính xác model là hai câu hỏi chấp nhận riêng.”

---

<a id="slide-22"></a>

## Slide 22 — Latency acceptance is separate from model accuracy

![Slide 22](../../submission-review/ai-journey-update-20261030/slides/assets/slide-22.png)

### Slide muốn nói gì

Tách dịch vụ nhanh khỏi chất lượng trả lời đúng: sanity check nhỏ và việc đạt độ trễ không chứng nhận yêu cầu chất lượng chính thức trên bộ đánh giá đầy đủ.

### Nhìn thấy gì trên slide

Ba dải bằng chứng tách chấp nhận latency dịch vụ, sanity check cục bộ nhỏ và chất lượng model official chưa xác minh.

### Thuật ngữ và ký hiệu

- **SLA:** Tiêu chí latency dịch vụ ở cấp request.
- **Smoke:** Bộ kiểm tra nhỏ về hành vi cơ bản/regression.
- **Retrieval:** Sanity check retrieval cục bộ, không phải benchmark quality official.
- **99% reference:** Ngưỡng chất lượng model official, hiện chưa xác minh.
- **FP8/BF16:** Trọng số FP8; activation và KV cache BF16.

### Cách đọc hình, trục, đơn vị và màu

- Smoke cục bộ là 7/8, không regression mới; retrieval là 12/12. Các kiểm tra nhỏ này không chứng nhận yêu cầu chất lượng official tối thiểu 99% reference. Primary giữ trọng số FP8 và activation/KV BF16; không dùng KV lượng tử hóa hay speculative decoding. SLA là chấp nhận latency dịch vụ; reference là chuẩn so chất lượng của organiser. Kết luận: báo riêng hiệu năng dịch vụ và ghi rõ quality official chưa xác minh.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** SLA latency và sanity check nhỏ đạt; chất lượng model official chưa xác minh.
- **Giả thuyết:** Giữ model trong khi đánh giá serving riêng với quality.
- **Kết luận được hỗ trợ:** Báo latency và quality official như hai kết quả riêng.
- **Chưa biết / giới hạn:** Ngưỡng full-set 99% reference vẫn chưa xác minh.

### Lời nói mẫu

“Dịch vụ đạt ngưỡng latency cục bộ, các sanity check nhỏ không có regression mới. Đánh giá chất lượng official ở mức 99% reference chưa được xác minh, nên chúng tôi không tuyên bố chứng nhận hay ranking.”

### Điều không nên nói

Smoke và retrieval không phải chứng nhận accuracy đầy đủ.

### Câu chuyển slide

“Case EAGLE3 cho thấy cần báo cáo giả thuyết thất bại và công cụ được sửa như thế nào.”

---

<a id="slide-23"></a>

## Slide 23 — EAGLE3: follow the failed hypothesis through its repairs

![Slide 23](../../submission-review/ai-journey-update-20261030/slides/assets/slide-23.png)

### Slide muốn nói gì

Giữ toàn bộ chuỗi lỗi và sửa của speculative decoding, rồi giải thích vì sao sửa được tích hợp vẫn chưa chứng minh có tăng tốc.

### Nhìn thấy gì trên slide

Bốn giai đoạn EAGLE3 theo thời gian cho thấy lỗi vị trí draft, lỗi validator và cách sửa, retry ngắn và run đầy đủ.

### Thuật ngữ và ký hiệu

- **EAGLE3:** Phương pháp speculative decoding đề xuất draft token.
- **Vị trí draft:** Vai trò worker chạy draft model.
- **KV region:** Vùng bộ nhớ KV cache gắn với một role.
- **Protocol ngắn:** Phép thử giới hạn, không phải benchmark hoàn chỉnh.
- **Protocol đầy đủ:** Workload, warmup, cửa sổ đo và grace hoàn chỉnh.

### Cách đọc hình, trục, đơn vị và màu

- Thử nghiệm decode-only 25988 bị validator từ chối sai vì áp số KV region của draft lên prefill target-only. Sửa validator theo role nhưng vẫn giữ lỗi cũ. Retry ngắn 25998 qua protocol giới hạn nhưng mất 4,74% goodput so với control target-only. Thử nghiệm shallow full riêng 27238 đạt 2.971,628430 so với control 26949 ở 3.034,761104, giảm 2,080318%. Truyền draft chức năng không đồng nghĩa tăng tốc; telemetry acceptance thấp không phải phân tích thời gian nhân quả. EAGLE3 là speculative decoding; KV là key/value cache; full protocol là workload hoàn chỉnh; short protocol là phép thử giới hạn. Kết luận: đóng các arm đã đo và giữ lịch sử lỗi/sửa. Chưa biết cấu hình khác và quality official.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Sửa check cho phép chạy lại; nhánh decode-only và shallow đều mất goodput.
- **Giả thuyết:** Đổi vị trí draft hoặc cấu hình shallow có thể phục hồi TTFT.
- **Kết luận được hỗ trợ:** Đóng các cấu hình đã đo, giữ provenance lỗi và sửa.
- **Chưa biết / giới hạn:** Settings khác, timing nhân quả và quality official chưa biết.

### Lời nói mẫu

“Lần đầu trượt latency. Một lỗi tooling sau đó từ chối lần decode-only; chúng tôi sửa validator nhưng giữ lỗi cũ. Retry ngắn chạy nhưng mất goodput, thử nghiệm full riêng cũng giảm. Các settings đã thử được đóng; không kết luận phương pháp này không bao giờ hữu ích.”

### Điều không nên nói

Không xóa lỗi validator hoặc nhầm protocol ngắn với đầy đủ.

### Câu chuyển slide

“Tổng kết quay lại N64 được lặp lại và kết quả cache nhỏ không được promote.”

---

<a id="slide-24"></a>

## Slide 24 — Topology → transport → kernels → replication

![Slide 24](../../submission-review/ai-journey-update-20261030/slides/assets/slide-24.png)

### Slide muốn nói gì

Kết phần AI chính bằng cấu hình có bằng chứng lặp lại và giới hạn của kết luận, thay vì chọn một đỉnh điểm riêng lẻ.

### Nhìn thấy gì trên slide

Trung bình N64 lịch sử được lặp lại đặt cạnh gain cache nhỏ và một run native-runtime được báo riêng.

### Thuật ngữ và ký hiệu

- **Trung bình ba run:** Trung bình các run N64 đầy đủ lịch sử 25366/25373/25487.
- **Native runtime:** Đường runtime riêng của job 26766.
- **Cặp cache:** Control mới 27376 so với candidate 27378.
- **+0,240921%:** Gain candidate, thấp hơn cổng useful-gain định trước.
- **Quality official:** Yêu cầu accuracy full-set, chưa xác minh ở đây.

### Cách đọc hình, trục, đơn vị và màu

- Job native-runtime sau đó 26766 đạt độc lập 3.045,501509 và SLA đồng thời 98,580442%; cần báo riêng vì runtime path khác. Kết quả cache full cao nhất 27378 đạt 3.048,446289, chỉ +0,240921% so với control mới 27376, dưới ngưỡng useful-gain. Các replay hợp lệ thấp hơn quanh 2.802–2.831 vẫn được lưu. Lặp lại hỗ trợ chọn N64, không chứng minh optimum toàn cục. Không tuyên bố speculative speedup, chứng nhận quality official hay speedup nhân quả của native runtime.
- Slide này không có trục số X/Y. Đọc các hàng, cột hoặc ô thông tin được in; đầu mục xanh đậm tổ chức nội dung, chữ cam nhấn mạnh thông điệp. Các màu này không tạo thêm một nhóm dữ liệu đạt/trượt riêng.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Trung bình N64 lịch sử được lặp; cache tăng 0,240921%; runtime native báo riêng.
- **Giả thuyết:** Điểm được lặp lại đáng chọn hơn một đỉnh đơn độc.
- **Kết luận được hỗ trợ:** Giữ N64; không promote gain cache nhỏ.
- **Chưa biết / giới hạn:** Optimum toàn cục, quality official và khác biệt runtime nhân quả chưa biết.

### Lời nói mẫu

“Điểm được chọn là trung bình N64 lịch sử đã lặp lại. Kết quả native sau đó tương tự nhưng báo riêng. Đỉnh cache chỉ hơn control 0,24% nên không promote. Chúng tôi giữ cả run thấp hợp lệ. Đây là operating point đo được, không phải optimum toàn cục; quality official vẫn cần xác minh.”

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

“Phần tiếp theo đổi chủ đề sang nghiên cứu HPC CPU/OpenFOAM.”

---

<a id="slide-25"></a>

## Slide 25 — Appendix · diagnose performance drift with controlled cells

![Slide 25](../../submission-review/ai-journey-update-20261030/slides/assets/slide-25.png)

**Phần dự phòng AI: chỉ mở khi cần giải thích sâu hơn.**

### Slide muốn nói gì

Giải thích chênh lệch giữa kết quả N64 đầy đủ đã lặp lại và một đối chứng ngắn mới hơn, nhưng không gán nguyên nhân chưa được xác lập.

### Nhìn thấy gì trên slide

Các cột lần lượt là quan sát/phép thử, cài đặt giữ hoặc đổi, và kết quả. Các hàng gồm lần đầy đủ lịch sử, đối chứng ngắn, phát lại cấu hình cũ, các ô thử có kiểm soát và lần native riêng. Điểm là token đầu ra tốt/giây. N64 là concurrency của client, không phải số GPU. Slide không có trục đồ thị hay mã màu điểm dữ liệu.

### Thuật ngữ và ký hiệu

- **N64:** Mức đồng thời mục tiêu của client là 64 yêu cầu đang xử lý.
- **chính sách graph:** Quy tắc chọn hình dạng yêu cầu decode nào được thực thi bằng đồ thị GPU đã capture.
- **giới hạn yêu cầu:** Ngưỡng cấu hình tối đa cho số yêu cầu đang chạy mà engine phục vụ chấp nhận.
- **runtime native:** Đường thực thi serving ở lần đo đầy đủ riêng biệt về sau.
- **KV:** Trạng thái key-value của attention được chuyển từ xử lý prompt sang sinh token.

### Cách đọc hình, trục, đơn vị và màu

- Trung bình ba lần N64 đầy đủ lịch sử là 3,044.400475. Đối chứng ngắn đạt khoảng 2,560 nhưng khác quy trình, chính sách graph và giới hạn yêu cầu.
- Phát lại đầy đủ cấu hình cũ hợp lệ đạt 2,830.923547. Các đối chứng mới không tách được một nguyên nhân hữu ích. Lần native đầy đủ 26766 đạt 3,045.501509 trong chuỗi riêng.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Kết quả đầy đủ lịch sử và native gần 3,044–3,046 token đầu ra tốt/giây; đối chứng ngắn và phát lại cũ thấp hơn.
- **Giả thuyết:** Chính sách graph và giới hạn yêu cầu đang chạy có thể giải thích một phần độ lệch.
- **Kết luận được hỗ trợ:** Thử nghiệm không xác lập nguyên nhân hữu ích duy nhất; giữ lại lần phát lại thấp nhưng hợp lệ.
- **Chưa biết / giới hạn:** Biến động còn lại, gồm khác biệt harness và cách quan sát, vẫn chưa rõ.

### Lời nói mẫu

Kết quả đầy đủ lịch sử và đối chứng ngắn về sau chênh lệch đáng kể. Nhóm kiểm tra cấu hình thực tế, phát lại cấu hình cũ rồi tách riêng các cài đặt mới. Các phép thử chưa tìm ra một nguyên nhân hữu ích duy nhất. Lần native đầy đủ gần mức lịch sử, nhưng chưa giải thích vì sao đối chứng ngắn thấp hơn.

### Điều không nên nói

Không gọi đối chứng ngắn là lần đầy đủ tương đương, không quy phục hồi cho một cờ, và không bỏ lần phát lại thấp nhưng hợp lệ.

### Câu chuyển slide

Tiếp theo là các hướng kiến trúc và kernel, xét theo đúng phạm vi bằng chứng.

---

<a id="slide-26"></a>

## Slide 26 — Appendix · profiles and source also close attractive detours

![Slide 26](../../submission-review/ai-journey-update-20261030/slides/assets/slide-26.png)

### Slide muốn nói gì

Cho thấy ý tưởng kiến trúc và kernel chỉ là đầu mối thử nghiệm giới hạn, chưa chứng minh serving đầy đủ nhanh hơn.

### Nhìn thấy gì trên slide

Các cột là hướng nghiên cứu, bằng chứng và quyết định; các hàng là nhánh riêng, không phải xếp hạng chung. Gói attention-DP đổi nhiều yếu tố ở N52; Triton chỉ thử trên dạng đại diện; kiểm tra SM có giới hạn. Compile mô hình thật dừng ở assertion, không có điểm. Fixture CPU không đo serving. Slide không có trục đồ thị hay mã màu điểm dữ liệu.

### Thuật ngữ và ký hiệu

- **DP:** Data parallelism, tức song song dữ liệu: nhiều bản sao hoặc phân vùng xử lý các yêu cầu riêng; ở đây là cấu hình attention.
- **FP8:** Định dạng số dấu phẩy động 8 bit dùng cho trọng số trong cấu hình được giữ lại.
- **Triton:** Hệ thống lập trình và biên dịch kernel GPU; kết quả probe chỉ áp dụng cho hình dạng đã thử.
- **SM:** Streaming multiprocessor, một đơn vị thực thi GPU; ngân sách SM giới hạn số đơn vị kernel được dùng.
- **torch.compile:** Đường biên dịch của PyTorch để chuyển các phép toán mô hình thành thực thi đã biên dịch.
- **RoPE:** Rotary positional embedding, phép mã hóa vị trí dạng xoay được mô hình sử dụng.
- **C++:** Ngôn ngữ biên dịch được dùng trong các probe cache và API riêng biệt.

### Cách đọc hình, trục, đơn vị và màu

- Gói attention-DP với DeepGEMM/DeepEP đạt 2,549.20 ở N52, thấp hơn điểm MNNVL được giữ lại; nhiều thay đổi cùng lúc nên không thể quy cho một cờ.
- Probe FP8 Triton đại diện thua DeepGEMM. Ngân sách SM 80, 96 và 120 pha trộn hoặc thiếu ổn định. torch.compile mô hình thật gặp assertion RoPE/fused-KV; fixture C++ chỉ chạy trên CPU.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Bằng chứng gồm điểm thấp hơn ở cấu hình nhiều yếu tố, probe kernel thua, kiểm tra SM pha trộn và assertion compile không có điểm.
- **Giả thuyết:** Bố trí attention, kernel, ngân sách, biên dịch hoặc đường cache khác có thể giúp serving đầy đủ.
- **Kết luận được hỗ trợ:** Chỉ kết luận trong phạm vi đã thử; các dạng Triton thử không vượt DeepGEMM và compile không có điểm.
- **Chưa biết / giới hạn:** Dạng chưa thử và đường compile tương thích có thể khác; fixture CPU không xác nhận serving mô hình đầy đủ.

### Lời nói mẫu

Các ý tưởng chỉ được kiểm tra trong phạm vi bằng chứng cho phép. Gói attention đổi nhiều yếu tố, probe kernel gồm dạng đại diện, còn compile mô hình thật dừng trước khi có điểm. Fixture CPU có thể xác nhận một đường C++ nhỏ nhưng không chứng minh tích hợp GPU. Tên thư viện hay profile chỉ gợi ý phép thử, chưa chứng minh tăng tốc.

### Điều không nên nói

Không coi thay đổi ghép là thử một yếu tố, khái quát probe cho mọi dạng, gọi fixture CPU là serving đạt, hay tự gán điểm cho compile lỗi.

### Câu chuyển slide

Tiếp theo là cấu hình H200 được giữ lại và điểm vận hành H100 riêng.

---

<a id="slide-27"></a>

## Slide 27 — Appendix · the selected AI deployment is N64

![Slide 27](../../submission-review/ai-journey-update-20261030/slides/assets/slide-27.png)

### Slide muốn nói gì

Tóm tắt triển khai H200 N64 được chọn và cấu hình H100 riêng được giữ lại.

### Nhìn thấy gì trên slide

Các hàng nêu cài đặt; hai cột phải ghi giá trị H200 và H100. Concurrency client là 64 so với 54. Prefill, decode, phân bổ TP và độ chính xác số nằm riêng; dòng cuối ghi thành phần chung. Đây là mô tả cấu hình, không phải so sánh phần cứng khớp điều kiện. Slide không có trục đồ thị hay mã màu điểm dữ liệu.

### Thuật ngữ và ký hiệu

- **H200 / H100:** Hai mẫu GPU khác nhau; cấu hình và kết quả được báo cáo riêng.
- **N64:** Mục tiêu đồng thời 64 yêu cầu đang xử lý; cấu hình H100 giữ mức 54.
- **prefill:** Xử lý prompt đầu vào trước khi sinh câu trả lời.
- **decode:** Sinh lần lượt từng token đầu ra.
- **TP:** Tensor parallelism, tức chia phép toán tensor giữa nhiều GPU.
- **EP:** Expert parallelism, tức phân phối các expert của mô hình mixture-of-experts qua nhiều GPU.
- **FP8 / BF16:** Trọng số dấu phẩy động 8 bit; BF16 là brain floating point 16 bit, dùng cho activation và trạng thái KV.
- **FlashInfer:** Cách triển khai attention GPU dùng cho decode trong cấu hình được giữ lại.
- **MNNVL:** Backend giao tiếp collective được chọn cho các nhóm GPU liên quan.
- **HPC-Ops:** Backend thao tác GPU của runtime, dùng cho decode và cả prefill trên H100.

### Cách đọc hình, trục, đơn vị và màu

- H200 dùng hai worker prefill TP4 với DeepGEMM, chunk 8.192, và một worker decode TP8/EP8 với HPC-Ops. H100 dùng hai worker prefill TP4 với HPC-Ops, chunk 4.096, và decode TP8/EP8.
- Cả hai dùng trọng số FP8, activation và KV BF16, FlashInfer cho decode attention, MNNVL và định tuyến vòng tròn. Reader qua kiểm tra compute-only trên dữ liệu thật, nhưng chưa phát lại GPU đầy đủ sau sửa.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** H200 và H100 khác concurrency và prefill; cả hai giữ độ chính xác số và thành phần chung đã nêu.
- **Giả thuyết:** Dịch vụ target-only N64 đã lặp lại là cấu hình chính thực tế.
- **Kết luận được hỗ trợ:** Báo cáo H200 và H100 riêng; bảng không xếp hạng mẫu GPU.
- **Chưa biết / giới hạn:** Độ chính xác chính thức và phát lại portable đầy đủ sau sửa reader chưa được xác minh.

### Lời nói mẫu

Cấu hình H200 xử lý prompt trên hai worker TP4 và sinh token trên một worker TP8/EP8. H100 có concurrency thấp hơn, backend prefill và chunk khác. Cả hai giữ trọng số FP8 cùng activation và KV BF16. Bản sửa reader được kiểm tra trên dữ liệu thật, nhưng chưa phát lại toàn bộ GPU allocation sau đó.

### Điều không nên nói

Không kết luận trực tiếp tốc độ H100 so với H200 và không nói job portable đầy đủ đã qua sau sửa.

### Câu chuyển slide

Tiếp theo là so sánh capture graph dày và thưa theo mục tiêu dịch vụ.

---

<a id="slide-28"></a>

## Slide 28 — Appendix · sparse graphs save memory, not goodput

![Slide 28](../../submission-review/ai-journey-update-20261030/slides/assets/slide-28.png)

### Slide muốn nói gì

Giải thích vì sao graph decode thưa giảm bộ nhớ capture theo log nhưng không cải thiện goodput đo được.

### Nhìn thấy gì trên slide

Các cột là đại lượng đo, đối chứng dày và ứng viên thưa; mỗi hàng so sánh hai cấu hình. Bucket đếm dạng yêu cầu được capture, không phải concurrency hay số GPU. Bộ nhớ là GB mỗi rank theo log native, không phải tổng VRAM hay GiB; thời gian là pha capture, không phải tổng thời gian job. Slide không có trục đồ thị hay mã màu điểm dữ liệu.

### Thuật ngữ và ký hiệu

- **bucket graph decode:** Nhóm dạng yêu cầu mà engine serving capture thành đồ thị thực thi GPU.
- **rank:** Một tiến trình worker phân tán, trong cấu hình này thường gắn với một GPU.
- **GB:** Gigabyte theo log native; không tự đổi nhãn thành GiB hay tổng VRAM.
- **goodput:** Tốc độ yêu cầu đạt đồng thời các giới hạn độ trễ; điểm hiển thị lấy số yêu cầu tốt mỗi giây từ client nhân với 200 token đầu ra yêu cầu.
- **ITL:** Inter-token latency, độ trễ giữa các token sinh ra; giá trị trung bình trên slide là mili giây.
- **compile off:** Biên dịch graph mô hình bị tắt trong phép thử; capture thành công không xác nhận hỗ trợ mô hình đã biên dịch.

### Cách đọc hình, trục, đơn vị và màu

- Đối chứng capture 64 bucket; ứng viên capture 12 trên cả tám rank khi compile tắt. Bộ nhớ giảm từ 1.15 xuống 0.36 GB/rank; thời gian capture đổi từ 101.46–101.49 xuống 95.98–96.05 giây.
- Goodput đối chứng 27376 là 3,041.119598, ứng viên 27510 là 3,029.861122, giảm 0.370208%. Mean request ITL tăng từ 14.991 lên 15.136 ms; TTFT tốt hơn.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Ứng viên giảm bộ nhớ capture theo log và rút ngắn pha này chút ít, nhưng goodput đo được thấp hơn.
- **Giả thuyết:** Ít dạng graph hơn có thể tiết kiệm bộ nhớ mà không hại mục tiêu dịch vụ.
- **Kết luận được hỗ trợ:** Giữ graph dày cho triển khai này; mục tiêu dịch vụ đo được không cải thiện.
- **Chưa biết / giới hạn:** Một đối chứng trước và seed khác nhau hạn chế kết luận nhân quả; bộ nhớ capture không phải tổng bộ nhớ GPU.

### Lời nói mẫu

Ứng viên thưa giảm bucket graph từ 64 xuống 12 và bộ nhớ capture trong log từ 1.15 xuống 0.36 GB mỗi rank. Pha capture chỉ nhanh hơn vài giây. Goodput đầy đủ thấp hơn đối chứng trước 0.370208 phần trăm, còn ITL trung bình tăng nhẹ. Nhóm giữ graph dày; so sánh đơn lẻ này không xác định nguyên nhân.

### Điều không nên nói

Không gọi bucket là concurrency, bộ nhớ là tổng VRAM hay GiB, hoặc thời gian capture là toàn bộ thời gian job. Slide này không đo độ chính xác.

### Câu chuyển slide

Tiếp theo, tách phép đo serving tổng hợp khỏi đánh giá chất lượng mô hình.

---

<a id="slide-29"></a>

## Slide 29 — Appendix · what the benchmark actually measures

![Slide 29](../../submission-review/ai-journey-update-20261030/slides/assets/slide-29.png)

### Slide muốn nói gì

Làm rõ benchmark serving đo gì và tách nó khỏi đánh giá chất lượng mô hình.

### Nhìn thấy gì trên slide

Ba ý mô tả yêu cầu tổng hợp 4.000 token đầu vào/200 token đầu ra, tải client vòng kín, và kiểm tra chất lượng chính thức riêng. Thời gian gồm warmup 60 giây, profiling 120 giây được chấm điểm, và grace 30 giây. Grace cho request đang chạy hoàn tất, không phải thời gian tính điểm bổ sung. Slide này không có bảng, trục hay mã màu điểm dữ liệu.

### Thuật ngữ và ký hiệu

- **AIPerf:** Công cụ client và đo benchmark gửi yêu cầu serving rồi xuất chỉ số hiệu năng.
- **vòng kín:** Kiểu tải giữ mục tiêu số yêu cầu đang chạy bằng cách thay mỗi yêu cầu vừa hoàn tất bằng một yêu cầu mới.
- **concurrency:** Số yêu cầu client mục tiêu hoạt động cùng lúc; workload chính N64 đặt mục tiêu 64.
- **warmup:** Pha khởi động worker và đường serving trước khi đo tải client chính thức.
- **cửa sổ profiling:** Khoảng cố định 120 giây dùng để tính điểm hiệu năng.
- **grace:** Khoảng 30 giây cho các yêu cầu còn đang chạy hoàn tất sau cửa sổ được chấm điểm.
- **ngưỡng chất lượng 99%:** Yêu cầu chính thức: chất lượng trên toàn bộ tập đạt ít nhất 99% điểm tham chiếu FP8 của ban tổ chức.

### Cách đọc hình, trục, đơn vị và màu

- AIPerf giữ mức concurrency mục tiêu bằng cách thay các request đã xong. Worker và đường serving được làm nóng bằng lưu lượng riêng.
- Chỉ cửa sổ được chấm điểm đóng góp vào hiệu năng báo cáo. Độ dài yêu cầu và token thực có thể khác; chưa xác lập việc cắt cụt vật lý.
- Chất lượng chính thức cần ít nhất 99% điểm tham chiếu FP8 của ban tổ chức và vẫn chưa được xác minh.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Workload serving này dùng yêu cầu tổng hợp 4.000/200 token và lịch warmup/profiling/grace 60/120/30 giây.
- **Giả thuyết:** Workload và thời gian cố định hỗ trợ so sánh khi cấu hình và quy trình khớp nhau.
- **Kết luận được hỗ trợ:** Goodput mô tả hiệu năng serving ở đây, không phải độ chính xác; không chia mọi request hoàn tất cho 120.
- **Chưa biết / giới hạn:** Token ID/lượng dùng thực và chất lượng toàn tập chính thức vẫn chưa biết.

### Lời nói mẫu

Benchmark này đo serving với prompt tổng hợp, không phải bộ đánh giá chất lượng chính thức. Client thay request hoàn tất để giữ concurrency. Sau warmup, 120 giây được tính điểm rồi grace cho request còn lại kết thúc. Goodput lấy theo cách tính của AIPerf; không nên tính lại bằng cách chia mọi request hoàn tất cho 120 giây.

### Điều không nên nói

Không tính grace là thời gian chấm, không đồng nhất token yêu cầu với token thực, và không nói đã đạt tiêu chí chất lượng 99%.

### Câu chuyển slide

Tiếp theo, so sánh kích thước chunk theo cùng quy trình đầy đủ.

---

<a id="slide-30"></a>

## Slide 30 — Appendix · larger prefill chunks did not help

![Slide 30](../../submission-review/ai-journey-update-20261030/slides/assets/slide-30.png)

### Slide muốn nói gì

So sánh ba kích thước chunk prefill theo protocol N64 đầy đủ; chunk lớn hơn không cải thiện mục tiêu dịch vụ trong các lần đo này.

### Nhìn thấy gì trên slide

Các cột là số token mỗi chunk, token đầu ra tốt/giây, tỷ lệ SLA chung và p95 TTFT mili giây. Mỗi hàng là một lần chạy. Cả ba dùng lịch 60/120/30 giây, yêu cầu 4.000/200 token, seed 2026, prefix lạnh, cùng mô hình và runtime. Slide không có trục đồ thị hay mã màu điểm dữ liệu.

### Thuật ngữ và ký hiệu

- **chunk prefill:** Số token prompt được worker prefill xử lý cùng nhau trong một đơn vị lập lịch.
- **good output tokens/s:** Tốc độ request tốt được báo cáo nhân với 200 token đầu ra yêu cầu cho mỗi request.
- **SLA:** Service-level agreement: tỷ lệ mọi request đạt đồng thời hai ngưỡng độ trễ.
- **p95:** Phân vị 95: 95% yêu cầu đo được có giá trị bằng hoặc nhỏ hơn con số này.
- **TTFT:** Time to first token, độ trễ từ lúc bắt đầu request đến token đầu tiên được sinh.
- **seed 2026:** Seed workload được cấu hình; nó không khiến seed do engine tạo ra giống hệt giữa các lần khởi chạy.

### Cách đọc hình, trục, đơn vị và màu

- Chunk 8.192: 3,045.501509 token đầu ra tốt/giây, SLA 98.580%, p95 TTFT 1,311.69 ms.
- Chunk 10.240: 3,034.088251, SLA 98.524%, p95 1,518.87 ms. Chunk 12.288: 3,020.943099, 98.310%, 1,624.12 ms. Cả ba qua kiểm tra nội bộ; mỗi mức chỉ có một lần chạy.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Goodput giảm và p95 TTFT tăng khi chunk lớn hơn trong các lần đo này.
- **Giả thuyết:** Batch prefill nhiều token hơn có thể tăng thông lượng.
- **Kết luận được hỗ trợ:** Giữ 8.192 cho cấu hình này và khép nhánh chunk lớn hơn có giới hạn.
- **Chưa biết / giới hạn:** Mỗi nhánh chỉ có một quan sát nên chưa xác định tối ưu toàn cục.

### Lời nói mẫu

Nhóm thử ba kích thước chunk trong các lần chạy đầy đủ với cùng workload và runtime. Khi chunk tăng từ 8.192 lên 12.288, goodput giảm và p95 độ trễ token đầu xấu hơn. Tất cả qua kiểm tra nội bộ, nhưng mỗi mức chỉ có một quan sát. Nhóm giữ 8.192 cho cấu hình này, không khẳng định tối ưu phổ quát.

### Điều không nên nói

Phân biệt đơn vị chunk, goodput, SLA và p95 TTFT. Qua kiểm tra nội bộ không đồng nghĩa có lợi ích hay chứng minh tối ưu toàn cục.

### Câu chuyển slide

Tiếp theo, phát lại portable thật làm lộ lỗi reader mà kiểm tra tĩnh bỏ sót.

---

<a id="slide-31"></a>

## Slide 31 — A real replay can invalidate a static deployment claim

![Slide 31](../../submission-review/ai-journey-update-20261030/slides/assets/slide-31.png)

### Slide muốn nói gì

Giải thích cách đầu ra portable thật làm lộ hai lỗi reader mà kiểm tra tĩnh và giả lập đã bỏ sót.

### Nhìn thấy gì trên slide

Các cột là bước, điều đã xảy ra và thay đổi. Các hàng đi từ kiểm tra tĩnh/giả lập qua lần phát lại GPU đầu, lần thứ hai và xác minh compute-only. Cả hai client GPU hoàn tất trước khi reader lỗi. Đây là chuỗi sửa lỗi, không phải xu hướng hiệu năng. Slide không có trục đồ thị hay mã màu điểm dữ liệu.

### Thuật ngữ và ký hiệu

- **portable replay:** Chạy quy trình serving và benchmark đã đóng gói trên môi trường triển khai portable riêng.
- **GPU client:** Lần chạy client benchmark gửi yêu cầu đến hệ thống serving GPU đã triển khai.
- **AIPerf 0.12:** Phiên bản benchmark client được lưu; lần chạy thật đầu đặt export trong thư mục con trực tiếp.
- **đường dẫn canonical:** Đường dẫn tuyệt đối đã chuẩn hóa, xử lý các bí danh như liên kết tượng trưng.
- **đường dẫn dạng chữ:** Chuỗi đường dẫn được ghi nguyên dạng, chưa phân giải bí danh hoặc liên kết tượng trưng.
- **compute-only:** Job xác minh reader trên CPU không cấp phát GPU; nó không phát lại serving.
- **scheduler FAILED:** Job ban đầu vẫn mang trạng thái thất bại thực tế, dù sau đó có thể đọc được đầu ra thô.

### Cách đọc hình, trục, đơn vị và màu

- Job 27136 hoàn tất hai đường ngữ nghĩa và client chính thức, rồi lỗi vì export AIPerf 0.12 nằm trong thư mục con. Bản sửa đầu xử lý cấu trúc đó.
- Job 27145 hoàn tất client nhưng phần tổng hợp lỗi vì bí danh /scratch/home và /home ở dạng đường dẫn khác nhau. Chuẩn hóa gốc đầu vào đã sửa lỗi. Job không GPU 27152 qua cả hai reader trên cả hai bộ dữ liệu thật.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Hai lỗi reader xảy ra: export nằm trong thư mục con và đường dẫn canonical không khớp bí danh dạng chữ. Reader đã sửa qua dữ liệu thật trong kiểm tra compute-only.
- **Giả thuyết:** Lỗi reader gây ra trạng thái thất bại sau khi client hoàn tất.
- **Kết luận được hỗ trợ:** Bản sửa hẹp đã được xác minh, nhưng các job GPU ban đầu vẫn FAILED.
- **Chưa biết / giới hạn:** Không có lần phát lại GPU toàn allocation sau cả hai bản sửa.

### Lời nói mẫu

Kiểm tra tĩnh đều qua, nhưng chạy portable thật tìm ra hai lỗi reader sau khi client GPU kết thúc: export lồng thư mục, rồi bí danh của cùng đường dẫn không nhất quán. Job compute-only xác minh cả hai bản sửa trên dữ liệu thật. Job GPU ban đầu vẫn thất bại và chưa phát lại portable đầy đủ sau sửa.

### Điều không nên nói

Không đổi trạng thái job gốc, không gọi kiểm tra compute-only là phát lại serving, và không trình bày goodput khôi phục như triển khai sửa xong thành công.

### Câu chuyển slide

Cuối cùng, tách kết luận hiện có khỏi đề xuất xác minh trong tương lai.

---

<a id="slide-32"></a>

## Slide 32 — What the evidence supports next

![Slide 32](../../submission-review/ai-journey-update-20261030/slides/assets/slide-32.png)

### Slide muốn nói gì

Kết thúc bằng kết luận có bằng chứng và phân biệt đề xuất xác minh tương lai với công việc đã hoàn thành.

### Nhìn thấy gì trên slide

Slide nêu ba khuyến nghị: giữ dịch vụ đã tái lập, xác nhận đường thực thi mới và hoàn tất kiểm định độc lập. Không có bảng định lượng hay biểu đồ. Các kiểm tra còn mở là chất lượng mô hình chính thức và phát lại portable đầy đủ sau sửa reader. Slide không có trục đồ thị hay mã màu điểm dữ liệu.

### Thuật ngữ và ký hiệu

- **target-only:** Chỉ serving mô hình đích, không thêm mô hình draft sinh token dự đoán.
- **N64:** Mức đồng thời mục tiêu đã chọn là 64 yêu cầu đang xử lý.
- **EAGLE:** Phương pháp speculative decoding đề xuất token draft để mô hình đích xác minh; nhánh đầy đủ thử ở cấu hình nông làm giảm hiệu năng.
- **tương thích RoPE/KV:** Tương thích giữa phép quay vị trí RoPE của mô hình và giao diện cache key-value mà đường thực thi đã biên dịch cần dùng.
- **độ chính xác chính thức:** Điểm chất lượng mô hình trên toàn tập của ban tổ chức, so với ngưỡng tham chiếu FP8 bắt buộc.
- **end-to-end:** Lần chạy hoàn chỉnh qua triển khai đóng gói, client, xử lý đầu ra và xem xét kết quả.

### Cách đọc hình, trục, đơn vị và màu

- Giữ target-only N64: thay đổi cache, cap và polling chưa có lợi ích; nhánh EAGLE nông đầy đủ đã thử bị giảm điểm. Graph thưa thấp hơn đối chứng trước 0.370208%.
- Trước khi chấm đường mới, xác minh backend hoạt động, KV chuyển đúng và đầu ra hợp lệ. Độ chính xác chính thức và phát lại portable đầy đủ sau sửa còn mở; compile cần giải pháp tương thích RoPE/KV.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** N64 có bằng chứng qua nhiều lần chạy đầy đủ; thay đổi riêng lẻ chưa cho lợi ích hữu ích. Chưa có kết quả chất lượng chính thức hay phát lại portable sau sửa.
- **Giả thuyết:** Xác minh riêng việc kích hoạt, truyền trạng thái, đầu ra và kiểm tra độc lập có thể tăng độ tin cậy triển khai.
- **Kết luận được hỗ trợ:** Giữ cấu hình target-only N64 đã tái lập; các kiểm tra liệt kê là yêu cầu tương lai, chưa phải việc hoàn tất.
- **Chưa biết / giới hạn:** Độ chính xác mô hình chính thức và hành vi end-to-end sau sửa reader vẫn chưa biết.

### Lời nói mẫu

Dịch vụ target-only N64 đã lặp lại vẫn là lựa chọn được bằng chứng hỗ trợ; một điểm riêng cao hơn chưa đủ để thay thế. Đường mới cần chứng minh backend hoạt động, KV được chuyển và đầu ra hợp lệ trước khi chấm. Chất lượng toàn tập chính thức và phát lại portable đầy đủ sau sửa reader vẫn còn mở. Đây là ưu tiên xác minh, chưa phải việc đã lên lịch hay thực hiện.

### Điều không nên nói

Không nói đã đạt độ chính xác chính thức, portable đã xác minh đầy đủ, graph thưa tăng goodput, hay compile đã được sửa tương thích.

### Câu chuyển slide

Kết thúc phụ lục; khi trả lời, tách quan sát, kết luận có căn cứ và điều chưa biết.

---

<a id="slide-33"></a>

## Slide 33 — The task: same 65-million-cell airflow calculation

![Slide 33](transcript-assets/slide-33.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Xác định khối lượng tính toán CPU cố định và đại lượng hiệu năng cần tối ưu. Phép so sánh giữ nguyên bài toán được quy định, rồi xem cụm máy thực hiện nó hiệu quả đến đâu.

### Nhìn thấy gì trên slide

Slide nêu lưới 65,3 triệu ô, bốn nút, 512 MPI rank (128 rank mỗi nút), và 150 bước bộ giải, trong đó 149 bước được tính giờ. Chỉ số là số giây đã trôi qua trung bình cho mỗi bước; thấp hơn là tốt hơn. Màu cam nhấn số ô lưới và điều kiện chạy ở dòng cuối. Slide không có trục đồ thị hay chuỗi dữ liệu.

### Thuật ngữ và ký hiệu

- **65,3 triệu:** Số làm tròn từ lưới chính xác gồm 65.334.765 ô.
- **MPI rank:** Một tiến trình bộ giải phân tán; 512 rank tổng cộng tương ứng 128 rank mỗi nút.
- **s/step:** Giây thời gian thực trên mỗi vòng lặp bộ giải, không phải giây thời gian lái xe mô phỏng.

### Cách đọc hình, trục, đơn vị và màu

- Đọc đây là định nghĩa khối lượng công việc, chưa phải so sánh kết quả: cùng lưới và cùng lượng tính toán bắt buộc trên bốn nút CPU.
- 149 mẫu tính giờ bắt đầu sau bước bộ giải đầu tiên; toàn bộ lần chạy vẫn thực hiện đủ 150 bước.
- Mục tiêu là giảm thời gian nhờ sử dụng CPU tốt hơn, không phải giảm kích thước lưới hoặc lượng tính toán.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Lần chạy cố định có nhiều công việc song song: khoảng 65,3 triệu ô được phân cho 512 rank.
- **Giả thuyết:** Phân phối và đặt công việc hiệu quả hơn có thể giảm thời gian mỗi bước.
- **Kết luận được hỗ trợ:** Slide xác lập cách đo; riêng nó không báo cáo cải thiện do tinh chỉnh.
- **Chưa biết / giới hạn:** Slide không chỉ ra nút thắt hay chứng minh một cải thiện nhân quả.

### Lời nói mẫu

Chúng tôi tối ưu phép tính luồng khí OpenFOAM đã được quy định, không thay đổi toán học của nó. Lưới có 65,3 triệu ô. Trên bốn nút, 512 MPI rank thực hiện đủ 150 bước bộ giải. Bước đầu tiên không tính giờ, nên còn 149 bước được đo. Chúng tôi so sánh số giây thời gian thực trung bình mỗi bước; thấp hơn là tốt hơn. Đây là bài toán hiệu quả CPU với khối lượng công việc cố định.

### Điều không nên nói

Không gọi 65,3 triệu là số chính xác tuyệt đối; không nói chỉ chạy 149 bước; không xem định nghĩa bài toán là bằng chứng tăng tốc. Hệ số lực cản được lưu lại chỉ là kiểm tra hợp lý về vật lý, không phải chỉ số hiệu năng này.

### Câu chuyển slide

Tiếp theo, trình bày các bước chuẩn bị cần giữ nguyên để một lần chạy đầu-cuối hợp lệ.

---

<a id="slide-34"></a>

## Slide 34 — The whole required pipeline comes before the score

![Slide 34](transcript-assets/slide-34.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Giải thích vì sao chỉ số hiệu năng chỉ có ý nghĩa khi giữ nguyên toàn bộ quy trình bắt buộc, đồng thời phân biệt phân rã lưới với gán tiến trình vào CPU.

### Nhìn thấy gì trên slide

Năm ô trắng nối từ trái sang phải bằng mũi tên cam: decomposePar gán ô lưới cho các rank; renumberMesh sắp xếp lại dữ liệu cục bộ; potentialFoam khởi tạo trường dòng chảy; applyBoundaryLayer áp dụng lớp biên được quy định; simpleFoam chạy đủ 150 bước bộ giải. Hai nhãn bên dưới giải thích phân rã là quyết định quyền sở hữu ô, còn CPU affinity là quyết định CPU nào chạy mỗi rank. Không có trục số; mũi tên biểu thị trình tự bắt buộc.

### Thuật ngữ và ký hiệu

- **MPI:** Message Passing Interface; các rank riêng biệt trao đổi dữ liệu, đặc biệt ở ranh giới phân vùng.
- **decomposePar:** Tiện ích OpenFOAM chia ô lưới cho các rank.
- **CPU affinity:** Gắn tiến trình hoặc rank với tài nguyên CPU; khác với việc gán ô lưới.

### Cách đọc hình, trục, đơn vị và màu

- Đi theo mũi tên cam từ các bước chuẩn bị tới bộ giải; phép đo cuối không thể thay thế các bước đó.
- Phân rã trả lời rank sở hữu ô nào. Affinity trả lời rank chạy trên CPU nào.
- Trình tự là toàn bộ khâu chuẩn bị bắt buộc và lần giải 150 bước, không phải danh sách bước tùy chọn.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Quy trình gồm thiết lập dữ liệu, khởi tạo, xử lý điều kiện biên rồi giải lặp.
- **Giả thuyết:** Có thể thay đổi cách phân rã và đặt tiến trình để ảnh hưởng thời gian thực thi mà vẫn giữ nguyên bài toán.
- **Kết luận được hỗ trợ:** So sánh hợp lệ phải giữ mọi bước bắt buộc và xác nhận chúng hoàn tất thành công.
- **Chưa biết / giới hạn:** Sơ đồ này không đo chi phí từng giai đoạn và không chứng minh ánh xạ nào nhanh hơn.

### Lời nói mẫu

Trước khi so sánh thời gian bộ giải, chúng tôi giữ toàn bộ quy trình bắt buộc: gán ô cho MPI rank, sắp xếp lại dữ liệu cục bộ, khởi tạo dòng chảy, áp dụng lớp biên quy định và chạy đủ 150 bước simpleFoam. Phân rã quyết định mỗi rank sở hữu ô nào. CPU affinity quyết định rank chạy trên CPU nào. Đây là hai quyết định khác nhau; lần chạy hợp lệ phải giữ mọi bước chuẩn bị cùng bước giải.

### Điều không nên nói

Không nói ảnh nền là cụm máy dự thi. Slide chỉ cho trình tự, không cho thời gian từng giai đoạn và cũng không xác nhận affinity đã được đo hay tối ưu trong một kết quả cụ thể.

### Câu chuyển slide

Khi khối lượng và quy trình đã cố định, slide tiếp theo kiểm tra liệu một chỉ số cục bộ có dự báo được thời gian bộ giải hay không.

---

<a id="slide-35"></a>

## Slide 35 — A smaller partition cut did not make the solver faster

![Slide 35](transcript-assets/slide-35.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Trình bày giả thuyết NUMA về tính cục bộ không thành công và giải thích vì sao chỉ số đại diện của đồ thị phân vùng không thể thay phép đo thời gian chạy.

### Nhìn thấy gì trên slide

Slide đặt mức giảm graph cut −10,63% màu cam cạnh mức bộ giải chậm hơn +3,4416% màu đỏ, ngăn bởi dấu không bằng. Không có trục hay chuỗi dữ liệu. Phép so sánh thời gian được nêu là 13,881 so với 14,359 giây mỗi bước. Dòng kết luận nói proxy đồ thị không phải runtime và liệt kê các nguyên nhân chưa đo: MPI wait, băng thông, tần số, công suất và vị trí trang bộ nhớ.

### Thuật ngữ và ký hiệu

- **NUMA:** Truy cập bộ nhớ không đồng nhất: chi phí truy cập có thể phụ thuộc socket CPU hoặc vùng cục bộ sở hữu bộ nhớ.
- **graph cut:** Chỉ số proxy về số hoặc trọng số kết nối phân vùng đi qua ranh giới được chọn; không đo trực tiếp thời gian trao đổi.
- **−10,63%:** Proxy graph cut giảm 10,63% ở cấu hình này.
- **+3,4416%:** Thời gian trung bình bộ giải tăng, tức chậm hơn 3,4416% trong quan sát so sánh.

### Cách đọc hình, trục, đơn vị và màu

- Màu cam biểu thị proxy cải thiện; màu đỏ biểu thị thời gian bộ giải đo được xấu hơn. Dấu và màu cho thấy sự không tương ứng.
- Proxy nhỏ hơn vẫn có thể đi cùng thời gian chạy dài hơn vì thuộc tính phân vùng khác và hiệu ứng lúc chạy cũng quan trọng.
- Slide nói rõ nguyên nhân chưa được đo; đây là ứng viên bị loại, không phải chẩn đoán nguyên nhân.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Graph cut giảm 10,63%, trong khi thời gian trung bình tăng từ 13,881 lên 14,359 giây mỗi bước.
- **Giả thuyết:** Nhóm công việc theo vị trí bộ nhớ có thể giảm chi phí truy cập xa và trao đổi qua giao diện.
- **Kết luận được hỗ trợ:** Nhánh NUMA không đổi đã được đóng; riêng graph cut không dự báo tốc độ bộ giải.
- **Chưa biết / giới hạn:** Chưa đo MPI wait, băng thông, tần số, công suất, vị trí trang bộ nhớ và các nguyên nhân khả dĩ khác.

### Lời nói mẫu

Chúng tôi thử ý tưởng NUMA: nhóm công việc theo vị trí có thể giảm chi phí bộ nhớ xa hoặc giao diện. Proxy graph cut giảm 10,63%, nhưng thời gian trung bình bộ giải tăng từ 13,881 lên 14,359 giây mỗi bước, chậm hơn 3,4416%. Vì vậy, chúng tôi đóng ứng viên này. Proxy đồ thị mô tả cách phân vùng; nó không phải runtime đo được và không chứng minh thời gian trao đổi giảm.

### Điều không nên nói

Phép so sánh còn thay đổi thuộc tính phân vùng khác, vì vậy không quy chậm hơn cho một cơ chế duy nhất. Một ánh xạ ngoại tuyến khác có proxy giảm 4,5741% nhưng chưa chạy bộ giải, nên không phải bằng chứng hiệu năng. Hai phần trăm này không phải các đại lượng nghịch đảo.

### Câu chuyển slide

Tiếp theo, ta xem cách phân rã quan sát tốt hơn có thay đổi theo số nút hay không.

---

<a id="slide-36"></a>

## Slide 36 — Observed scaling changed which decomposition led

![Slide 36](transcript-assets/slide-36.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

So sánh thời gian trung bình quan sát được của Scotch và hierarchical trên các cấp phát một, hai và bốn nút, đồng thời giới hạn kết luận vì điểm kết thúc công việc và cấp phát khác nhau.

### Nhìn thấy gì trên slide

Ba cặp thanh ngang được ghi 1 node · 40 steps, 2 nodes · 80 steps và 4 nodes · 150 steps. Thanh cam là Scotch; thanh xanh đậm là Hierarchical, theo nhãn đi kèm. Giá trị là giây mỗi bước bộ giải: 14,451 so với 14,366; 7,463 so với 7,170; 3,678 so với 3,820. Thanh dài biểu thị nhiều giây hơn, tức thời gian trung bình chậm hơn. Không có nhãn trục riêng hay khoảng bất định.

### Thuật ngữ và ký hiệu

- **Scotch:** Phương pháp phân rã lưới dựa trên đồ thị trong quy trình OpenFOAM.
- **Hierarchical:** Phương pháp phân rã lưới chia không gian theo cấu trúc phân cấp.
- **s/step:** Số giây thời gian thực trung bình trên mỗi vòng lặp bộ giải được tính giờ; thấp hơn là tốt hơn.

### Cách đọc hình, trục, đơn vị và màu

- Ở một nút, hierarchical thấp hơn một chút; ở hai nút, hierarchical thấp hơn; ở bốn nút, Scotch thấp hơn.
- Số bước kết thúc được hiển thị không giống nhau và mỗi kết quả đến từ một cấp phát riêng.
- Đây là bằng chứng mô tả các giá trị trung bình quan sát, không phải đường cong strong-scaling có kiểm soát.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Hierarchical dẫn ở cặp hai nút; Scotch dẫn ở cặp bốn nút; trung bình một nút gần nhau và hierarchical thấp hơn.
- **Giả thuyết:** Phương án phân vùng phù hợp có thể phụ thuộc vào số nút, mật độ rank và điều kiện riêng của lần cấp phát.
- **Kết luận được hỗ trợ:** Không có một phương pháp thắng trong mọi quan sát; kết quả Scotch bốn nút đáng được xem xét kỹ hơn.
- **Chưa biết / giới hạn:** Cấp phát và điểm kết thúc khác nhau nên không thể quy chênh lệch chỉ cho số nút hay tuyên bố hiệu quả mở rộng nhân quả.

### Lời nói mẫu

Phương án dẫn đầu thay đổi theo cấp phát. Hierarchical có trung bình một nút thấp hơn chút và dẫn ở hai nút, còn Scotch dẫn ở bốn nút. Giá trị tính bằng giây mỗi bước bộ giải. Tuy nhiên, đây là các lần chạy được cấp phát riêng với điểm kết thúc quy định khác nhau—40, 80 và 150 bước—nên chúng mô tả xu hướng chứ không phải so sánh nhân quả có kiểm soát. Cần đánh giá cấu hình ở đúng số nút và mật độ rank dự định.

### Điều không nên nói

Không tính hoặc tuyên bố tăng tốc lý tưởng từ các giá trị này. Thanh chỉ biểu thị trung bình, không có khoảng bất định; cấp phát riêng và số bước chạy khác nhau đều quan trọng. Slide không chứng minh ưu thế phổ quát của phương pháp nào.

### Câu chuyển slide

Có thể tách kết quả bốn nút theo số rank mỗi nút; đó là phép so sánh kế tiếp.

---

<a id="slide-37"></a>

## Slide 37 — At four nodes, the winner depends on ranks per node

![Slide 37](transcript-assets/slide-37.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Cho thấy thứ hạng phân rã trên bốn nút thay đổi theo mật độ tiến trình và xác định giá trị trung bình thấp nhất đã được xem xét, nhưng không nâng nó thành tối ưu phổ quát.

### Nhìn thấy gì trên slide

Sáu thanh ngang so sánh Scotch và Hierarchical tại 64, 96 và 128 rank mỗi nút. Màu cam là Scotch; xanh đậm là Hierarchical. Giá trị ở cuối thanh là giây mỗi bước: Scotch/Hierarchical lần lượt là 10,310/4,489 ở 64; 7,146/4,922 ở 96; và 3,678/3,820 ở 128. Giá trị thấp hơn hiện thành thanh ngắn hơn và nghĩa là bước trung bình quan sát nhanh hơn. Không thấy trục số hay khoảng bất định.

### Thuật ngữ và ký hiệu

- **ranks per node:** Số tiến trình MPI đặt trên mỗi nút; trên bốn nút, các cấu hình hiển thị tương ứng 256, 384 và 512 rank.
- **s/step:** Số giây thời gian thực trung bình được đo trên mỗi bước bộ giải.
- **lowest reviewed mean:** Trung bình nhỏ nhất trong nhóm quan sát đã xem xét, không phải bằng chứng tối ưu toàn cục.

### Cách đọc hình, trục, đơn vị và màu

- Ở 64 và 96 rank mỗi nút, hierarchical thấp hơn; ở 128, Scotch thấp hơn khoảng 0,142 giây mỗi bước.
- Kết luận được nhấn mạnh là Scotch-128 đạt 3,677906731 giây mỗi bước, trung bình thấp nhất trong các hồ sơ đã xem xét.
- Mỗi thanh tóm tắt một cấp phát riêng; số CPU yêu cầu cũng khác ở một vài cấu hình.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Phương pháp thấp hơn đổi ở mật độ rank cao nhất; Scotch-128 có trung bình quan sát nhỏ nhất trong sáu log này.
- **Giả thuyết:** Chất lượng phân rã có thể tương tác với mật độ rank trên mỗi nút.
- **Kết luận được hỗ trợ:** Chọn theo số nút và mật độ rank đã đo; chỉ tên phương pháp không dự báo được bên thắng.
- **Chưa biết / giới hạn:** Cấp phát riêng và số CPU yêu cầu khác nhau khiến ta không thể quy chênh lệch chỉ cho phương pháp phân rã hoặc mật độ.

### Lời nói mẫu

Trên bốn nút, mật độ rank làm thay đổi phương pháp có trung bình quan sát thấp hơn. Hierarchical dẫn ở 64 và 96 rank mỗi nút. Ở mức 128, Scotch đạt 3,678 giây mỗi bước so với 3,820 của hierarchical. Đây là trung bình thấp nhất trong sáu quan sát đã xem xét. Chúng tôi xem nó là ứng viên cần xác nhận, không phải hiệu ứng nhân quả hay phương pháp tốt nhất phổ quát, vì đây là các cấp phát riêng và số CPU yêu cầu có chỗ khác nhau.

### Điều không nên nói

Các số thập phân là giây mỗi bước, không phải hệ số tăng tốc. Biểu đồ không có trục tường minh hay thanh sai số; không suy ra ý nghĩa thống kê từ độ dài thanh. Slide chưa chứng minh khả năng lặp lại ổn định.

### Câu chuyển slide

Slide kế tiếp xem phân bố thời gian đầy đủ của trung bình Scotch-128, đặc biệt là phần đuôi chậm.

---

<a id="slide-38"></a>

## Slide 38 — Keep the slow step in the mean; inspect the tail

![Slide 38](transcript-assets/slide-38.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Giải thích vì sao mọi vòng lặp được tính giờ, kể cả bước chậm cực độ, vẫn nằm trong trung bình số học kiểu chính thức; đồng thời phân biệt quan sát với chẩn đoán nguyên nhân.

### Nhìn thấy gì trên slide

Ba thống kê ở đầu slide: trung vị 3,298742 s, phân vị thứ 95 là 3,795740 s, và cực đại 35,883552 s tại solver Time 119. Vạch dọc cam nhỏ biểu thị trung vị; vạch đỏ cao hơn nhiều nhấn mạnh cực đại. Slide không có thang trục số, vì vậy đọc giá trị in sẵn thay vì ước lượng vị trí bằng mắt. Nội dung ghi giữ lại 149/149 mẫu và trung bình số học gồm mọi bước được đo.

### Thuật ngữ và ký hiệu

- **median:** Giá trị ở giữa sau khi sắp xếp 149 mẫu tính giờ.
- **95th percentile (p95):** Giá trị mà xấp xỉ 95% mẫu nằm tại hoặc dưới đó, theo quy ước phân vị sử dụng.
- **maximum:** Mẫu lớn nhất được ghi nhận; ở đây là 35,883552 giây tại solver Time 119.
- **Time 119:** Chỉ số thời gian/vòng lặp bộ giải được báo cáo, không phải 119 giây thời gian thực.

### Cách đọc hình, trục, đơn vị và màu

- Trung vị và p95 ở khoảng 3,3–3,8 giây, nhưng một bước được giữ lại mất khoảng 35,9 giây.
- Cả 149 mẫu vẫn nằm trong trung bình số học; bỏ ngoại lệ sẽ làm thay đổi chỉ số hiệu năng đã nêu.
- Màu đỏ đánh dấu cực đại, không biểu thị một cơ chế lỗi đã biết.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Một bước chậm bất thường xuất hiện ở chỉ số 119, trong khi vùng trung tâm và p95 thấp hơn nhiều.
- **Giả thuyết:** Một sự kiện thoáng qua ở hệ thống hoặc ứng dụng có thể gây ra đột biến, nhưng cần telemetry để kiểm tra.
- **Kết luận được hỗ trợ:** Giữ lại phần đuôi và điều tra; không cắt điểm chậm hay đổi điểm kết thúc bắt buộc.
- **Chưa biết / giới hạn:** Chưa đo đủ MPI wait, băng thông, tần số CPU, công suất và vị trí trang bộ nhớ để xác định nguyên nhân.

### Lời nói mẫu

Bước trung vị mất 3,299 giây và phân vị 95 mất 3,796 giây, nhưng cực đại lên tới 35,884 giây tại solver Time 119. Chúng tôi giữ cả 149 mẫu tính giờ trong trung bình số học. Bước chậm đó thuộc lần chạy đã đo, không thể bỏ chỉ vì bất tiện. Dấu vết xác nhận có đột biến, nhưng không giải thích lý do. Cần thiết bị đo bổ sung và các lần lặp độc lập để nghiên cứu nguyên nhân và độ ổn định.

### Điều không nên nói

Không gọi solver Time 119 là 119 giây; đó là chỉ số thời gian/vòng lặp được báo cáo. Không nhầm trung vị hay p95 với trung bình số học chính thức. Nguyên nhân được ghi rõ là chưa biết: thiếu telemetry không chứng minh MPI, bộ nhớ hay phần cứng hoạt động bình thường.

### Câu chuyển slide

Sự bất định đó dẫn tới yêu cầu ở slide sau: chạy lặp độc lập với bằng chứng đầy đủ.

---

<a id="slide-39"></a>

## Slide 39 — A reproducible candidate needs more than a fast log

![Slide 39](transcript-assets/slide-39.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Phân biệt thời gian ứng viên đã được xem xét với kết quả chính thức được chấp nhận, đồng thời liệt kê bằng chứng cần có từ lần xác nhận độc lập.

### Nhìn thấy gì trên slide

Cột trái ghi trung bình ứng viên đã xem xét: 3,677906731 giây mỗi bước cho Scotch-128 với 149 mẫu. Cột phải ghi lần lặp độc lập, job 25940700, hàng đợi Q/q5 lúc 15:06 UTC, trạng thái “Not running: node_pool insufficient” và “No result.” Sáu mục dấu vuông cam nêu gói đầu vào 54 tệp đã đóng băng, toàn bộ khởi tạo cộng 150 bước, mã trả về tường minh cho từng giai đoạn, 512 lõi vật lý trên bốn máy, và dấu niêm phong nguồn/lưới/đầu ra. Không có trục đồ thị; hai cột đối chiếu bằng chứng hiện có với bằng chứng đang chờ.

### Thuật ngữ và ký hiệu

- **Q/q5:** Nhãn hàng đợi/trạng thái bộ lập lịch trong quan sát đã ghi; slide nói job đang chờ, không phải đang chạy.
- **Scotch-128:** Phân rã Scotch với 128 MPI rank mỗi nút trên bốn nút.
- **seal:** Bằng chứng ghi nhận danh tính/tính toàn vẹn của tệp nguồn, lưới hoặc đầu ra; đây là kiểm tra yêu cầu, chưa phải kiểm tra đã hoàn tất.

### Cách đọc hình, trục, đơn vị và màu

- Ứng viên có thời gian trung bình và 149 mẫu đã đo, nhưng riêng điều đó không chứng minh được chấp nhận chính thức.
- Job độc lập đang chờ và chưa có kết quả trong ảnh chụp trạng thái được hiển thị.
- Danh sách là bằng chứng cần thu từ lần xác nhận đang chờ, không phải khẳng định các kiểm tra đã đạt.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Ứng viên tốt nhất đã xem xét là 3,677906731 giây mỗi bước; job xác nhận độc lập đang chờ vì thiếu tài nguyên node_pool.
- **Giả thuyết:** Lần chạy mới, đóng băng và đầy đủ quy trình có thể kiểm tra khả năng lặp lại, nguồn gốc và bố trí tài nguyên.
- **Kết luận được hỗ trợ:** Báo cáo số hiện có là quan sát ứng viên, không phải điểm chính thức được chấp nhận; cần xem xét lần lặp trước khi chọn tiếp.
- **Chưa biết / giới hạn:** Slide không cung cấp kết quả, bằng chứng trạng thái kết thúc của bộ lập lịch hay xác minh đã hoàn tất cho job 25940700.

### Lời nói mẫu

Ứng viên Scotch-128 đã được xem xét đạt trung bình 3,677906731 giây mỗi bước trên 149 mẫu. Đây là quan sát ứng viên, không phải điểm chính thức được chấp nhận. Chúng tôi gửi job 25940700 để xác nhận độc lập, nhưng trạng thái bộ lập lịch tại thời điểm ghi trên slide vẫn là đang chờ do thiếu tài nguyên node-pool, nên chưa có kết quả. Lần xác nhận phải giữ nguyên gói đầu vào, chạy khởi tạo và đủ 150 bước, ghi mã thoát từng giai đoạn, chứng minh 512 lõi vật lý trên bốn máy, rồi niêm phong nguồn, lưới và đầu ra.

### Điều không nên nói

Mọi trạng thái bộ lập lịch là ảnh chụp lịch sử lúc 15:06 UTC trên slide; không trình bày như trạng thái trực tiếp hiện nay. Danh sách là yêu cầu bằng chứng, không phải xác nhận đã hoàn thành. Một log nhanh chưa đủ chứng minh tái lập đầy đủ hoặc được chấp nhận.

### Câu chuyển slide

Slide cuối tổng kết nguyên tắc bằng chứng và quyết định xem xét tiếp theo, không tuyên bố kết quả mới.

---

<a id="slide-40"></a>

## Slide 40 — What we learned — and the next measurement

![Slide 40](transcript-assets/slide-40.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Khép lại phần HPC bằng bốn nguyên tắc đo lường và điểm quyết định tiếp theo: xem xét bằng chứng xác nhận đầy đủ trước khi chọn cấu hình khác.

### Nhìn thấy gì trên slide

Bốn cột đánh số nêu: đo toàn bộ job; tin bằng chứng runtime; giữ mọi mẫu; xác nhận độc lập. Giải thích ngắn nhấn mạnh giữ khâu chuẩn bị và nguồn gốc, phân biệt graph cut với tốc độ, điều tra phần đuôi bằng thiết bị đo, và xem lại job 25940700. Dòng trạng thái có ngày ghi 23 Oct 15:06 UTC, vẫn Q/q5, thiếu node_pool, chưa có kết quả. Màu cam nhấn hành động kế tiếp: xem phần đuôi, bằng chứng kết thúc và các mẫu phần cứng có giới hạn. Không có đồ thị số.

### Thuật ngữ và ký hiệu

- **terminal proof:** Bằng chứng job đã tới trạng thái kết thúc xác định trong bộ lập lịch, đi cùng đầu ra đầy đủ và mã trả về.
- **bounded hardware samples:** Các mẫu đo phần cứng có phạm vi và giới hạn được hoạch định, không phải phiên profiling không giới hạn.
- **Q/q5:** Hàng đợi/trạng thái trong ảnh chụp đã ghi, không phải truy vấn hiện tại.

### Cách đọc hình, trục, đơn vị và màu

- Bốn nguyên tắc nối tính hợp lệ, runtime đo được, bảo toàn ngoại lệ và khả năng tái lập độc lập.
- Bước tiếp theo là xem xét bằng chứng, không tuyên bố cải thiện hiệu năng từ job đang chờ.
- Dòng trạng thái đóng băng thông tin biết được vào 23 October 15:06 UTC: lần xác nhận chưa có kết quả.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Dữ liệu bốn nút đã xem xét thu hẹp lựa chọn và cho thấy Scotch-128 có trung bình thấp nhất trong sáu quan sát, trong khi hồ sơ cùng ngày cho biết lần xác nhận còn chờ.
- **Giả thuyết:** Xem bằng chứng kết thúc đầy đủ, phần đuôi và lấy mẫu phần cứng giới hạn có thể làm rõ độ ổn định trước lựa chọn tiếp theo.
- **Kết luận được hỗ trợ:** Công việc thu hẹp ứng viên và cải thiện yêu cầu bằng chứng; nó chưa xác lập tối ưu toàn cục hay điểm được chấp nhận.
- **Chưa biết / giới hạn:** Slide không cho biết điều gì xảy ra sau đó với job 25940700 hoặc nguyên nhân của đột biến thời gian.

### Lời nói mẫu

Chúng tôi rút ra bốn bài học: đo toàn bộ job, tin runtime đo được hơn proxy phân vùng, giữ mọi mẫu thời gian và xác nhận độc lập. Trung bình Scotch-128 đã xem xét giúp thu hẹp lựa chọn, nhưng chưa phải tối ưu toàn cục được chứng minh hay điểm được chấp nhận. Vào thời điểm ghi nhận—23 October lúc 15:06 UTC—job 25940700 vẫn chờ tài nguyên node-pool và chưa có kết quả. Bước tiếp theo là xem bằng chứng kết thúc và phần đuôi thời gian, rồi lấy mẫu phần cứng có giới hạn trước khi chọn phép đo khác.

### Điều không nên nói

Đây là mốc bàn giao có ngày, không phải trạng thái bộ lập lịch hiện tại. Không suy ra job thành công hay thất bại sau đó; cũng không nói rằng việc lấy mẫu giới hạn đã được thực hiện. Bài trình bày tóm lược bằng chứng đã công bố, không chứng nhận phép đo mới.

### Câu chuyển slide

Phần slide HPC kết thúc tại đây; quay lại kết luận tổng thể của bài trình bày kết hợp.
