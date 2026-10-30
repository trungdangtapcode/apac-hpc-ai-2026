# Transcript và hướng dẫn hiểu từng slide — Tiếng Việt

Đây là **lời thuyết trình mẫu và tài liệu học**, không phải bản chép lại một buổi nói đã diễn ra. Tài liệu đi theo đúng 40 slide của bản trình chiếu hiện tại. Bản tiếng Việt được tạo theo yêu cầu riêng của bạn; mã nguồn và các báo cáo khác vẫn dùng tiếng Anh.

**Cách dùng:** mỗi slide mở đầu bằng **“Nói nhanh · 10–20 giây”**, có thể nói ngay: ý chính, số liệu nổi bật và ý nghĩa của chúng. Các từ cần thiết được giải thích ngay trong đoạn ngắn, ví dụ “repeated” là chạy lại benchmark để kiểm tra kết quả có tái lập. Thời lượng là mục tiêu để luyện, không phải bản ghi đã bấm giờ. Khi cần hiểu sâu hoặc trả lời câu hỏi, đọc tiếp “Slide muốn nói gì”, phần lập luận, thuật ngữ và lời nói mẫu dài bên dưới.

- **Slide 1–24:** phần AI chính. Dùng [kế hoạch 15–20 phút](PRESENTATION_PLAN.md); không đọc hết 24 lời nói mẫu nếu vượt thời gian.
- **Slide 25–32:** phần AI dự phòng khi được hỏi. Slide 31–32 vẫn thuộc nhóm dự phòng dù tiêu đề không có chữ Appendix.
- **Slide 33–40:** giải thích phần HPC đang có trong cùng deck, chỉ đọc và diễn giải. Trạng thái job trên các slide này là **ảnh chụp ngày 23/10**, không phải trạng thái trực tiếp ngày 30/10. Hướng dẫn này không cập nhật hay xác nhận kết quả HPC mới. Thời lượng AI không bao gồm mặc định phần HPC.
- Màu sắc có ý nghĩa **theo từng slide**. Cam không luôn là “thắng” hay “thua”. Ảnh nền, gradient và đường trang trí cuối slide không biểu diễn dữ liệu.
- **↑ / ↓** thường là hướng mong muốn tối ưu, không khẳng định số liệu thực tế đã tăng/giảm. “Không có trục” nghĩa là sơ đồ/bảng/card, không cần tự suy ra trục X/Y.
- Nghiên cứu đã dừng theo yêu cầu. Các việc “tiếp theo” trong slide là đề xuất hoặc câu chuyện tại thời điểm đó, không phải job mới đã chạy.

Nguồn: [PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), [PDF](../../submission-review/ai-journey-update-20261030/TripleU_APAC2026_Presentation.pdf), [bản tiếng Anh](TRANSCRIPT_EN.md). SHA-256 của PowerPoint: `b2e1c88aba8d5a3d5ec181e3fccc6b95bb6ea12c29f214e7c3c964619dc81616`. Đây là transcript của phiên bản này; đổi deck thì cần kiểm tra lại hướng dẫn.

## Những cách gọi cần hiểu trước khi thuyết trình

**“Nhóm tự đo” thay cho “chạy cục bộ”:** benchmark chạy trên cluster được cấp, gồm các compute node H200 hoặc H100 nêu ở từng kết quả. Nhóm tự gửi job và kiểm tra dữ liệu. Chữ “local” trong bản cũ nói về phạm vi xác minh của nhóm; nó không có nghĩa chạy trên laptop, trên login node hay chỉ một node. Kết quả trên hạ tầng được cấp vẫn chưa tự động thành điểm BTC chấm và xác nhận.

**“Phép đo đầy đủ”:** trong chiến dịch này là 60 giây warmup để dịch vụ hoạt động trước, 120 giây profiling để thu số đo, và 30 giây grace cho request còn lại hoàn tất. “Đầy đủ” phân biệt với phép thử ngắn dùng sàng lọc ý tưởng. Nó không có nghĩa đã chạy mọi bài đánh giá chất lượng hay mọi request đều đạt. Theo luật, ít nhất 90% request phải đồng thời đạt hai giới hạn độ trễ.

**“Đã kiểm tra đạt”:** nhóm kiểm tra dữ liệu theo những điều kiện đã triển khai cho lần chạy đó, chẳng hạn protocol, cấu hình thực sự được bật, độ trễ/lỗi và kiểm tra đầu ra nhỏ. Cần đọc điều kiện cụ thể của từng run; việc scheduler ghi COMPLETED chỉ cho biết script trả mã thành công. Cả hai chưa thay thế đánh giá chất lượng chính thức ≥99% điểm tham chiếu của BTC; yêu cầu đó vẫn chưa được xác minh.

**“Đối chứng” và “ứng viên”:** đối chứng là cấu hình giữ để làm mốc; ứng viên là cấu hình đổi yếu tố muốn thử. Ví dụ cache mới 27378 phải so với đối chứng mới 27376. So nó với trung bình lịch sử của một chuỗi khác sẽ trộn thay đổi cần thử với khác biệt thời điểm và môi trường.

**“Lặp lại” và “cải thiện có ích”:** chạy lại bằng job khác cho kết quả gần nhau làm bằng chứng chắc hơn một đỉnh đơn lẻ, nhưng vẫn có thể dùng lại GPU cũ. Nhóm đặt ngưỡng tăng >1% cho các phép thử gần cuối để chọn nhánh đáng chạy xác nhận; đây là quy tắc quyết định của nhóm, không phải quy định BTC. Kết quả tăng 0,24% chưa đạt quy tắc đó và chưa chứng minh tách được khỏi biến động giữa các lần chạy.

**“Quan sát”, “giả thuyết”, “kết luận”:** “TTFT tăng” là số đã đo; “do hàng đợi dài hơn” là giả thuyết nếu chưa tách thời gian chờ khỏi thời gian tính; “giữ cấu hình cũ vì ứng viên chưa vượt ngưỡng đã đặt” là quyết định được dữ liệu hỗ trợ. Nêu rõ điều chưa đo giúp giải thích trung thực, thay vì biến một suy đoán hợp lý thành nguyên nhân đã chứng minh.

**Ví dụ job có số nhưng vẫn lỗi:** GPU/client có thể đo xong và lưu JSON, rồi script đọc/tổng hợp JSON lỗi khiến cả job FAILED. Sửa chương trình đọc giúp lấy lại số từ dữ liệu cũ; nó không biến job gốc thành thành công, cũng không thay thế việc chạy lại toàn bộ triển khai sau sửa.

## Từ vựng dùng xuyên suốt

| Ký hiệu / thuật ngữ | Hiểu đơn giản |
|---|---|
| cluster / node / job | Cluster là cụm máy tính kết nối với nhau; node là một máy trong cụm. Job là công việc xin tài nguyên qua scheduler rồi chạy lệnh trên máy được cấp. Job ID nhận diện lần thực thi, không phải thứ hạng hiệu năng. |
| allocation | Một lần scheduler cấp máy, CPU/GPU và thời gian chạy. Lần cấp mới có thể vẫn dùng đúng những GPU cũ; không tự động là kiểm tra trên phần cứng khác. |
| serving / inference | Inference là tính câu trả lời bằng model. Serving giữ model trong bộ nhớ, mở API nhận request và điều phối nhiều request; benchmark ở đây đo dịch vụ đó. |
| Qwen3-235B-A22B | Model có khoảng 235 tỷ tham số tổng cộng và khoảng 22 tỷ tham số hoạt động cho mỗi token. Vẫn phải lưu trọng số của model; số tham số hoạt động không phải tổng bộ nhớ cần chứa model. |
| checkpoint / container image | Checkpoint chứa tham số đã học của model. Container image chứa môi trường phần mềm và thư viện để chạy model. Đổi checkpoint và đổi image là hai thay đổi khác nhau. |
| runtime / backend / native | Runtime là phần mềm/đường thực thi chạy dịch vụ. Backend là cách triển khai được chọn cho một phép tính, như attention. Native trong tài liệu chỉ đường thực thi tích hợp của phiên bản phần mềm đã dùng; không có nghĩa chạy máy cá nhân hoặc mặc nhiên nhanh hơn. |
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
| attention | Phép tính giúp token hiện tại sử dụng những phần ngữ cảnh trước đó có liên quan. Lưu key/value giúp không phải tính lại từ đầu các biểu diễn đã lưu ở mỗi bước decode. |
| batch / queue / in-flight | Batch gom công việc cho một lượt thực thi của engine. Queue chứa công việc đang chờ. In-flight là request đã gửi nhưng chưa xong. Concurrency của client không nhất thiết bằng kích thước batch GPU ở một thời điểm. |
| NIXL | Lớp truyền dữ liệu được dùng ở đây để chuyển KV từ worker prefill sang worker decode. |
| FP8 / BF16 | Định dạng số thực 8 bit / bfloat 16 bit. Trọng số, activation và KV có thể dùng định dạng khác nhau. |
| FI / FA3 / DG / HPC-Ops | FlashInfer / FlashAttention 3 / DeepGEMM / triển khai kernel HPC-Ops được tái sử dụng. HPC-Ops không phải track HPC OpenFOAM. |
| kernel / GEMM | Một chương trình tính toán trên GPU / phép nhân ma trận tổng quát. Kernel riêng lẻ nhanh hơn chưa chắc làm cả dịch vụ nhanh hơn. |
| profiling / GPU utilization | Profiling ghi một số sự kiện thực thi để điều tra thời gian và công việc. GPU activity cho biết GPU có hoạt động trong khoảng lấy mẫu; 100% hoạt động không chứng minh đạt FLOPs tối đa, bị nghẽn tính toán hay không phải chờ giao tiếp. |
| MNNVL / collective | Đường giao tiếp Multi-node NVLink / phép giao tiếp có nhiều rank cùng tham gia. Cần kiểm tra đường thực thi thực tế được bật. |
| CUDA graph / bucket | Đồ thị thực thi GPU được capture / một kích thước thực thi được chọn để capture. Số bucket không phải concurrency. |
| baseline / control / candidate | Cấu hình mốc / nhánh đối chứng / cấu hình thử thay đổi. Mỗi phần trăm tăng giảm cần chỉ rõ mốc so sánh. |
| matched trial / repeat | So sánh giữ các yếu tố dự định, chỉ đổi yếu tố cần thử / lần cấp tài nguyên khác để kiểm tra tái lập. Cả hai không tự động chứng minh quan hệ nhân quả. |
| gate / promotion / close a branch | Gate là điều kiện cần đạt. Promotion là chọn ứng viên thay cấu hình đang giữ. Đóng một nhánh là quyết định không lặp tiếp cùng cài đặt không có ích; các từ này không có nghĩa BTC phê duyệt. |
| 99% of reference | Yêu cầu chất lượng tương đối so với điểm tham chiếu, tách biệt tỷ lệ request đạt độ trễ. Ví dụ tính toán: nếu điểm tham chiếu là 80 thì 99% của nó là 79,2 điểm; không có nghĩa phải trả lời đúng 99% câu hỏi. Ví dụ này không phải kết quả đo của cuộc thi. |
| cold prefix / cold startup | Cold prefix nghĩa là request không dùng lại KV prompt từ request trước. Cold startup là dịch vụ mới khởi động; cache tệp của hệ điều hành vẫn có thể chứa dữ liệu. Không được coi các trạng thái này là một. |
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

### Nói nhanh · 10–20 giây

Chúng tôi tối ưu dịch vụ Qwen trên 16 GPU, từ cách chia model đến truyền dữ liệu và chọn cách thực thi. Trọng tâm là tìm cấu hình chạy đúng, nhanh và cho kết quả gần nhau khi đo lại, thay vì chỉ chọn một lần có điểm cao.

![Slide 01](../../submission-review/ai-journey-update-20261030/slides/assets/slide-01.png)

### Slide muốn nói gì

Mở đầu câu chuyện nghiên cứu AI và xác định phạm vi: biến một cấu hình Qwen phân tán thành phép đo dịch vụ có thể tái lập. Bài trình bày đi từ bố trí hệ thống, truyền trạng thái, tối ưu theo giai đoạn đến đo lặp; tiêu đề không khẳng định đã thắng cuộc thi hay chứng nhận chất lượng mô hình.

### Giải thích kết quả và lập luận

Tiêu đề tóm tắt thứ tự giải quyết bài toán: chọn cách chia model lên các GPU, bảo đảm truyền trạng thái prompt đúng, tối ưu các phần tính toán, rồi chạy lại để kiểm tra kết quả. “Reproduced performance” nghĩa là chạy lại với cấu hình đã nêu vẫn thu được mức hiệu năng tương tự; không có nghĩa BTC đã chứng nhận kết quả.

### Thuật ngữ và ký hiệu cần hiểu

- **Qwen:** Dòng mô hình ngôn ngữ dùng trong bài toán; nghiên cứu phục vụ checkpoint Qwen3-235B được chỉ định.
- **APAC HPC-AI 2026:** Bối cảnh cuộc thi của nghiên cứu, không đồng nghĩa với giải thưởng hay được ban tổ chức chấp nhận.
- **30 October 2026:** Ngày của bản cập nhật nghiên cứu; các kết quả được trình bày là ghi nhận đến ngày này.
- **VNUHCM - TripleU:** Tên nhóm trình bày.

### Cách diễn giải số liệu hoặc sơ đồ

- Thứ tự trong tiêu đề cũng là thứ tự lập luận: hệ thống phải chạy đúng trước, sau đó mới có ý nghĩa khi so tốc độ.
- “Tái lập” ở đây là kết quả gần nhau khi chạy lại, không phải khẳng định kết quả đúng trên mọi máy hoặc mọi workload.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Công việc đi từ khôi phục kiến trúc phục vụ hai nút và truyền KV đến thử nghiệm backend theo từng giai đoạn và các phép đo đầy đủ được lặp lại.
- **Giả thuyết:** Muốn tối ưu kernel có ý nghĩa, trước hết phải làm cho đường triển khai và phép đo đầu cuối hoạt động đúng.
- **Kết luận được hỗ trợ:** Bài trình bày sẽ đưa ra cấu hình vận hành được đo lặp và các lựa chọn có căn cứ, đồng thời tách chúng khỏi điểm cao đơn lẻ và việc xác minh accuracy chính thức.
- **Chưa biết / giới hạn:** Accuracy trên toàn bộ bộ đánh giá chính thức vẫn chưa được xác minh; kết quả nhóm tự đo không phải thứ hạng chính thức của cuộc thi.

### Lời nói mẫu

Xin chào, chúng tôi là VNUHCM–TripleU. Đây là cập nhật nghiên cứu phục vụ Qwen đến ngày 30 tháng 10 năm 2026. Câu hỏi của chúng tôi không chỉ là làm sao để một lần chạy cho ra con số lớn hơn. Trước tiên, chúng tôi phải dựng được dịch vụ hai nút, truyền dữ liệu của yêu cầu đúng giữa xử lý prompt và sinh token, rồi đo các thay đổi backend có kiểm soát dưới những giới hạn dịch vụ. Tôi sẽ trình bày kết quả nào lặp lại được, thay đổi hấp dẫn nào không giúp ích, và điều gì dữ liệu hiện có chưa thể khẳng định.

### Điều không nên nói

Không gọi đây là chiến thắng, được ban tổ chức chấp nhận, hay đã chứng nhận accuracy. Ngày tháng giới hạn kết luận ở bản cập nhật này.

### Câu chuyển slide

Trước hết, tôi sẽ nói rõ thế nào là kết quả hữu ích và cách đọc các con số chính.

---

<a id="slide-02"></a>

## Slide 02 — Highest observation and strongest recommendation

### Nói nhanh · 10–20 giây

Ở mức 64 request đồng thời, nhóm chạy lại ba lần đo đầy đủ, đạt trung bình khoảng 3.044 token đầu ra đạt chuẩn mỗi giây. Điểm đơn cao nhất là 3.048,45, nhưng chỉ tăng 0,24% so với đối chứng. Nhóm giữ cấu hình có bằng chứng tái lập tốt hơn.

![Slide 02](../../submission-review/ai-journey-update-20261030/slides/assets/slide-02.png)

### Slide muốn nói gì

Phân biệt điểm cao nhất trong một lần chạy đầy đủ đã được rà soát với cấu hình có bằng chứng lặp lại tốt hơn. Slide nhấn mạnh rằng điểm cực đại và khuyến nghị đáng tin cậy nhất không nhất thiết là cùng một kết quả.

### Giải thích kết quả và lập luận

Slide tách “số đo đơn lẻ lớn nhất” khỏi “cấu hình có bằng chứng đủ chắc để khuyến nghị”. Kết quả bên trái do nhóm tự chạy trên cluster 16 H200 được cấp, không phải máy cá nhân và chưa phải điểm BTC chấm. Bên phải là trung bình ba lần đo N64 đầy đủ. Con số lớn hơn ở chú thích đến từ job đã tạo dữ liệu benchmark nhưng lỗi ở bước xử lý kết quả; mức hoàn tất của nó khác với job thành công từ đầu đến cuối.

### Thuật ngữ và ký hiệu cần hiểu

- **Nhóm tự đo / local result:** Nhóm khởi chạy benchmark trên cluster được cấp và đọc log để tự đánh giá. “Local” chỉ phạm vi kiểm chứng của nhóm, không chỉ vị trí máy cá nhân; BTC chưa xác nhận điểm.
- **Full run / phép đo đầy đủ:** Theo protocol của chiến dịch: warmup 60 giây, profiling 120 giây và grace 30 giây. Không có nghĩa chạy mọi dataset đánh giá chất lượng, và cũng không có nghĩa 100% request đều đạt.
- **Reviewed pass / đã kiểm tra đạt:** Nhóm xem dữ liệu và kiểm tra những điều kiện đã triển khai cho lần chạy: protocol, cấu hình thực chạy, độ trễ/lỗi và kiểm tra đầu ra nhỏ. Job 27378 có smoke 7/8 không thêm lỗi so với đối chứng và retrieval 12/12; đây chưa phải chứng nhận độ chính xác chính thức.
- **3,048.45; +0.24%:** Job 27378 đạt chính xác 3048.446289 good output tokens/s, hơn đối chứng 27376 là 0.240921%. Đây là một quan sát đơn lẻ.
- **Ngưỡng 1%:** Quy tắc nhóm đặt trước để quyết định mức tăng nào đáng chạy xác nhận tiếp, không phải quy định điểm chuẩn của BTC.
- **3,044.40; N64:** Trung bình 3044.400475 good output tokens/s từ ba lần chạy đầy đủ; client duy trì tối đa 64 request đang hoạt động.
- **Recovered raw 3,055.33:** Benchmark GPU đã lưu dữ liệu, nhưng chương trình đọc/tổng hợp kết quả lỗi. Sửa reader giúp lấy lại điểm 3055.330517; không thay đổi việc job gốc FAILED.

### Cách diễn giải số liệu hoặc sơ đồ

- Đọc 3.048,45 là một lần đo, 3.044,40 là trung bình ba lần đo. Hai con số không tạo thành cặp đối chứng trực tiếp vì khác nhánh và thời điểm.
- Muốn đánh giá thay đổi cache, phải so 27378 với đối chứng 27376, không lấy trung bình lịch sử 3.044,40 làm mốc.
- Mức tăng nhỏ có thể lẫn với biến động giữa các lần chạy; một số đo cao hơn chưa đủ để chọn thay cấu hình đã lặp lại. Ở đây chưa có bằng chứng tăng vượt ngưỡng nhóm đặt ra.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** 27378 đạt 3048.446289 good output tokens/s và qua các kiểm tra do nhóm thực hiện; mức tăng trong cặp cache so sánh là 0.240921%. Trung bình chuỗi N64 lịch sử là 3044.400475. Dữ liệu thô portable phục hồi đạt 3055.330517, nhưng job gốc mang trạng thái FAILED.
- **Giả thuyết:** Chỉ nên chọn điểm cao làm kết quả chính khi thay đổi đạt ngưỡng lợi ích đã định trước và được lặp độc lập trong so sánh phù hợp.
- **Kết luận được hỗ trợ:** Giữ N64 có kết quả lặp lại làm khuyến nghị vững hơn. Giữ 27378 là điểm cao nhất của một lần chạy đầy đủ do nhóm tự chạy và kiểm tra trên cluster H200 được cấp, không phải tối ưu có ích đã được chứng minh.
- **Chưa biết / giới hạn:** Riêng slide này không so sánh hai ô trong cùng điều kiện runtime; điểm raw portable cũng không phải kết quả hoàn tất đầu cuối của một phân bổ thành công.

### Lời nói mẫu

Slide này phân biệt số đo cao nhất với cấu hình nên chọn để nộp. Nhóm tự chạy job 27378 trên 16 H200 của cluster được cấp, dùng 60 giây warmup, 120 giây đo và 30 giây chờ request còn lại. Benchmark và các bước kiểm tra của nhóm hoàn tất, cho 3.048,45 token đầu ra đạt chuẩn mỗi giây. Nhưng thay cache chỉ tăng 0,24% so với đối chứng mới, chưa tới ngưỡng 1% mà nhóm tự đặt để coi là cải tiến đáng theo đuổi. Vì vậy chúng tôi giữ N64 với trung bình ba lần đo khoảng 3.044,40: số thấp hơn một chút nhưng có bằng chứng chạy lại. Cả hai đều là kết quả nhóm tự đo, chưa được BTC xác nhận. Con số 3.055,33 ở dưới được đọc lại từ dữ liệu của job lỗi bước tổng hợp; nó không phải một job hoàn tất thành công.

### Điều không nên nói

Không xếp hạng hai ô như thể chúng là một thử nghiệm ghép cặp. 3055,33 phục hồi không phải job scheduler đã qua và không chứng minh triển khai portable đầu cuối lặp lại được.

### Câu chuyển slide

Để hiểu thông lượng good output tokens mỗi giây, cần xem workload và điều kiện độ trễ ở từng yêu cầu.

---

<a id="slide-03"></a>

## Slide 03 — Optimise useful throughput under a latency gate

### Nói nhanh · 10–20 giây

Một request phải chờ token đầu không quá 3.000 mili giây và có khoảng cách token trung bình không quá 20 mili giây; ít nhất 90% request phải đạt cả hai. Điểm chỉ tính thông lượng của request đạt chuẩn, nên sinh nhiều token nhưng trả lời quá chậm vẫn không có lợi.

![Slide 03](../../submission-review/ai-journey-update-20261030/slides/assets/slide-03.png)

### Slide muốn nói gì

Định nghĩa mục tiêu benchmark trước khi bàn về thay đổi hệ thống: tối đa hóa thông lượng dịch vụ đạt chuẩn, đồng thời đủ yêu cầu riêng lẻ phải thỏa cả hai giới hạn độ trễ. Nhờ vậy không nhầm tốc độ sinh thô hay độ trễ trung bình với quy tắc chấm.

### Giải thích kết quả và lập luận

Goodput chỉ tính các request vừa hoàn tất vừa đủ nhanh. Dịch vụ có thể sinh rất nhiều token tổng cộng nhưng vẫn có điểm thấp nếu nhiều người dùng phải chờ quá ngưỡng. Trung bình độ trễ của tất cả request tốt chưa đủ: phải kiểm tra hai giới hạn cho từng request rồi mới đếm tỷ lệ đạt.

### Thuật ngữ và ký hiệu cần hiểu

- **4,000 input tokens → 200 output tokens:** Kích thước yêu cầu tổng hợp cố định: prompt 4.000 token và yêu cầu sinh 200 token đầu ra.
- **TTFT ↓:** Time to first token, thời gian đến token đầu tiên; càng thấp càng tốt, giới hạn cho mỗi yêu cầu là 3.000 mili giây.
- **Mean ITL ↓:** Mean inter-token latency, độ trễ trung bình giữa các token được sinh trong một yêu cầu; càng thấp càng tốt, giới hạn 20 mili giây.
- **Joint SLA ↑:** Tỷ lệ tất cả yêu cầu được đánh giá đồng thời đạt hai giới hạn độ trễ; mục tiêu ít nhất 90%. Lỗi vẫn nằm trong mẫu số.
- **Goodput ↑:** Tốc độ yêu cầu đạt chuẩn. Nhân số yêu cầu đạt chuẩn mỗi giây với 200 để tính good output tokens mỗi giây.
- **ms:** Mili giây, bằng một phần nghìn giây; đơn vị độ trễ.
- **req/s × 200:** Số yêu cầu đạt chuẩn mỗi giây nhân với 200 token đầu ra được yêu cầu trên mỗi yêu cầu.

### Cách diễn giải số liệu hoặc sơ đồ

- Mũi tên chỉ hướng mong muốn: độ trễ giảm, tỷ lệ đạt và goodput tăng.
- Một yêu cầu phải đồng thời đạt TTFT và mean ITL mới được tính là đạt chuẩn.
- Ngưỡng 90% áp dụng trên toàn bộ yêu cầu được đánh giá, không chỉ yêu cầu thành công.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Benchmark cố định kích thước yêu cầu và áp dụng quy tắc độ trễ kết hợp theo từng yêu cầu; lỗi vẫn bị tính. Goodput dựa trên các yêu cầu qua cả hai giới hạn.
- **Giả thuyết:** Hệ thống sinh nhiều token thô hơn vẫn có thể kém hơn nếu quá nhiều yêu cầu vi phạm thời gian token đầu hoặc khoảng cách token.
- **Kết luận được hỗ trợ:** Chúng tôi đánh giá cấu hình bằng throughput đạt chuẩn cùng các điều kiện độ trễ và đầu ra, không chỉ bằng một giá trị trung bình hay lượng token thô.
- **Chưa biết / giới hạn:** Bảng định nghĩa giao thức nhưng không có số đo của ứng viên nào; nó không cho biết phân bố độ trễ thực tế của từng cấu hình.

### Lời nói mẫu

Mục tiêu của chúng tôi là thông lượng hữu ích dưới một điều kiện độ trễ. Mỗi yêu cầu tổng hợp có 4.000 token đầu vào và yêu cầu 200 token đầu ra. Một yêu cầu chỉ đạt nếu thời gian đến token đầu tiên không quá 3.000 mili giây và khoảng cách token trung bình không quá 20 mili giây. Ít nhất 90% tất cả yêu cầu được đánh giá phải đồng thời đạt hai giới hạn; lỗi cũng bị tính. Goodput là số yêu cầu đạt chuẩn mỗi giây, nhân với 200 sẽ thành good output tokens mỗi giây được trình bày. Vì vậy độ trễ trung bình riêng lẻ không thể cho biết dịch vụ có qua hay không: quyết định được tính ở từng yêu cầu.

### Điều không nên nói

Không suy ra tỷ lệ đạt theo từng yêu cầu từ một giá trị trung bình tổng hợp. Không bỏ lỗi khỏi mẫu số và không thay 200 bằng độ dài đầu ra khác.

### Câu chuyển slide

Khi đã cố định mục tiêu đo, slide tiếp theo cho thấy vì sao mọi so sánh phải đi cùng thông tin nền tảng.

---

<a id="slide-04"></a>

## Slide 04 — One workload, two deployment systems

### Nói nhanh · 10–20 giây

Chúng tôi đo trên hai hệ thống, mỗi hệ thống 16 GPU: H200 tại Firmus và H100 tại NSCC. Phần cứng và môi trường chạy khác nhau, nên phải tối ưu và ghi kết quả riêng. Cùng model không có nghĩa lấy hai điểm so trực tiếp là công bằng.

![Slide 04](../../submission-review/ai-journey-update-20261030/slides/assets/slide-04.png)

### Slide muốn nói gì

Trình bày hai môi trường phần cứng dùng trong các nghiên cứu nền tảng riêng biệt và đặt nguyên tắc: mỗi so sánh phải nêu nền tảng, topology, backend và tải. Dùng chung workload và checkpoint không làm hai cụm tương đương nhau.

### Giải thích kết quả và lập luận

Hai hệ thống dùng cùng model và workload dự định, nhưng số đo còn phụ thuộc bộ nhớ GPU, truyền thông, phần mềm thực thi và vị trí tiến trình. Slurm/PBS cấp tài nguyên compute node, không chạy phép suy luận thay SGLang. Container mang môi trường phần mềm; SGLang thực thi model; AIPerf gửi request và đo thời gian. Vì vậy chuyển cấu hình sang cluster khác vẫn phải đo lại.

### Thuật ngữ và ký hiệu cần hiểu

- **2 × 8 H200:** Hai nút, mỗi nút có tám GPU NVIDIA H200; tổng cộng mười sáu GPU trong phân bổ Firmus.
- **2 × 8 H100 80GB:** Hai nút NSCC ASPIRE 2A+, mỗi nút có tám GPU H100 bộ nhớ 80 gigabyte. Đây là thế hệ GPU và môi trường khác.
- **Slurm / PBS:** Hai bộ lập lịch cụm khác nhau dùng để yêu cầu và quản lý tài nguyên tính toán.
- **Pyxis / native Enroot:** Đường khởi chạy container trên Firmus. NSCC dùng Singularity.
- **SGLang / AIPerf:** Engine phục vụ và client benchmark của nghiên cứu; cùng các image đã staging được dùng trên hai hệ thống.
- **Qwen3-235B FP8:** Mô hình/checkpoint và độ chính xác trọng số được giữ chung trong thiết lập so sánh nền tảng.
- **80GB:** Dung lượng bộ nhớ GPU danh định mỗi H100 như bảng ghi; đây không phải đơn vị hiệu năng.

### Cách diễn giải số liệu hoặc sơ đồ

- Các hàng mô tả phân bổ GPU, scheduler, công cụ chạy container, serving/client và mô hình.
- Bảng ghi cùng image và checkpoint đã staging, nhưng GPU và phần mềm triển khai khác nhau.
- Mỗi kết quả quan trọng cần gắn với GPU, bố trí worker, backend, mức tải và thời lượng đo; cùng tên model không đủ để coi hai lần đo là tương đương.

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

### Nói nhanh · 10–20 giây

Trên 16 GPU, hai nhóm bốn GPU xử lý prompt, còn một nhóm tám GPU sinh câu trả lời. Dữ liệu ngữ cảnh KV được chuyển giữa hai giai đoạn. Cách tách này cho phép tối ưu riêng từng phần, nhưng cũng thêm công truyền dữ liệu cần kiểm tra.

![Slide 05](../../submission-review/ai-journey-update-20261030/slides/assets/slide-05.png)

### Slide muốn nói gì

Giải thích thiết kế serving tách rời: dành một nút cho prefill prompt và nút còn lại cho decode tự hồi quy, sau đó truyền trạng thái KV của từng yêu cầu giữa hai vai trò. Hình nối vị trí phần cứng với các thử nghiệm layout và truyền dữ liệu tiếp theo.

### Giải thích kết quả và lập luận

Một request đi qua hai giai đoạn trên hai nhóm GPU khác nhau. Một trong hai worker prefill bốn GPU đọc prompt và tạo trạng thái KV của attention; NIXL chuyển trạng thái đó sang worker decode tám GPU để sinh câu trả lời. Thứ được chuyển là trạng thái ngữ cảnh, không phải toàn bộ trọng số model. Tách hai giai đoạn cho phép chọn cách tính phù hợp riêng cho xử lý prompt và sinh token, đổi lại phải trả chi phí truyền và điều phối.

### Thuật ngữ và ký hiệu cần hiểu

- **Prefill:** Giai đoạn xử lý prompt. Nó đọc token đầu vào và tạo trạng thái KV cần cho quá trình sinh.
- **Decode:** Giai đoạn sinh token tự hồi quy. Nó dùng trạng thái KV của prompt để tạo token đầu ra được yêu cầu.
- **P0 / P1 / D0:** Tên hai worker prefill và một worker decode; đây là nhãn worker, không phải mã GPU.
- **TP4 / TP8:** Tensor parallelism trên bốn hoặc tám GPU trong một worker. TP là cách chia mô hình.
- **EP1 / EP8:** Expert parallelism trên một hoặc tám phân vùng expert của mô hình mixture-of-experts.
- **KV state:** Dữ liệu key/value attention được tạo trong prefill và cần để tiếp tục decode cùng yêu cầu.
- **NIXL:** Cơ chế truyền dùng ở đây để chuyển dữ liệu KV giữa phía prefill và decode.
- **2 × 4 + 1 × 8 = 16 GPUs:** Hai worker prefill, mỗi worker bốn GPU, cộng một worker decode tám GPU; tổng cộng mười sáu GPU.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

Nhóm thử nhiều cách chia GPU và chọn hai nhóm xử lý prompt, mỗi nhóm bốn GPU, cùng một nhóm sinh token tám GPU. Mốc này đạt khoảng 1.912 token đạt chuẩn mỗi giây ở 48 request đồng thời; tải giữa các mốc khác nhau nên chưa tách riêng tác dụng của bố trí.

![Slide 06](../../submission-review/ai-journey-update-20261030/slides/assets/slide-06.png)

### Slide muốn nói gì

Cho thấy một số kết quả tìm kiếm topology và giải thích cấu hình được chọn đến từ các thử nghiệm đo được, dùng được. Chú thích phía dưới bảo toàn lịch sử: cấu hình thay thế là thử nghiệm mới, không phải sửa hồi tố cho lần thất bại ban đầu.

### Giải thích kết quả và lập luận

Topology là cách bố trí tài nguyên: có bao nhiêu worker model và mỗi worker chia việc lên bao nhiêu GPU. Đổi từ bốn worker prefill nhỏ sang hai worker rộng hơn làm thay đổi cả cách nhiều GPU xử lý một request lẫn số worker có thể nhận request. Các hàng còn dùng concurrency khác nhau, nên bảng ghi lại những bố trí đã thử có ích; nó không tách riêng mức tăng do một thay đổi topology.

### Thuật ngữ và ký hiệu cần hiểu

- **07 / 09:** Mã định danh của các thử nghiệm layout đầu tiên, không phải phiên bản phần mềm.
- **4 × TP2 / 2 × TP4:** Bốn worker prefill với tensor parallelism bằng hai; hàng kế tiếp dùng hai worker prefill với tensor parallelism bằng bốn.
- **TP4/EP4:** Worker decode cấu hình tensor parallelism bốn và expert parallelism bốn.
- **Selected split: 2 × TP4; 1 × TP8/EP8:** Hai worker prefill, mỗi worker TP4, và một worker decode TP8/EP8.
- **N:** Concurrency của client: mục tiêu số yêu cầu được giữ đang xử lý đồng thời, không phải số GPU hoặc token.
- **good tokens/s:** Thông lượng token đầu ra đạt chuẩn theo điều kiện độ trễ từng yêu cầu.
- **14 + 3 = 17 usable configurations:** Mười bốn layout gốc đã đo cộng ba cấu hình thay thế EP2 đã đo trong sổ phục hồi.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

Cách cũ chuẩn bị mô tả vùng nhớ cho toàn bộ kho KV, khoảng 403,8 triệu mục mỗi tiến trình GPU. Cách sửa chỉ mô tả vùng của một request, còn 188 dải đã gộp. Đây là giảm công chuẩn bị truyền, không phải bằng chứng suy luận nhanh hơn theo cùng tỷ lệ.

![Slide 07](../../submission-review/ai-journey-update-20261030/slides/assets/slide-07.png)

### Slide muốn nói gì

Giải thích vì sao khởi tạo KV khi chạy lạnh được thiết kế lại theo các trang mà yêu cầu thật sự truyền. So sánh số liệu là hình học descriptor, cho thấy quy mô liệt kê metadata; slide chủ ý không trình bày đây là mức tăng tốc suy luận.

### Giải thích kết quả và lập luận

Trước khi gửi các byte KV, lớp truyền cần danh sách các vùng nhớ phải đọc. Cách cũ chuẩn bị mô tả cho cả vùng KV đã dành trước; cách sửa chỉ mô tả các trang thuộc request hiện tại rồi gộp những vùng liền nhau. Danh sách ngắn hơn có thể giảm công chuẩn bị, nhưng hai số đếm trên slide khác phạm vi và không đo băng thông hay tốc độ đầu cuối. Trước hết phải kiểm tra địa chỉ đúng; danh sách ít mục nhưng đọc nhầm bộ nhớ vẫn là lỗi.

### Thuật ngữ và ký hiệu cần hiểu

- **KV pool:** Toàn bộ không gian địa chỉ cache key/value được cấp cho một rank, phần lớn không cần truyền cho một yêu cầu cụ thể.
- **403.8 million source entries per rank:** Số gần đúng entry nguồn của descriptor được liệt kê cho hình học toàn pool trong ví dụ TP8 đại diện.
- **188 coalesced entries per request:** Số dải descriptor liên tục sau khi gộp các trang kề nhau trong hình học yêu cầu 4.000 token minh họa.
- **rank:** Một tiến trình/phân vùng mô hình phân tán tham gia triển khai song song; không phải thứ hạng cuộc thi.
- **descriptor:** Metadata mô tả các dải bộ nhớ cho lớp truyền; bản thân nó không phải nội dung tensor KV.
- **coalescing:** Gộp các dải bộ nhớ liền kề thành ít mô tả dải lớn hơn.
- **CPU range tests → GPU transfer → response checks:** Chuỗi xác minh nhiều lớp: kiểm tra tính toán địa chỉ, thử truyền thật trên GPU, rồi kiểm tra ý nghĩa phản hồi yêu cầu.

### Cách diễn giải số liệu hoặc sơ đồ

- Số bên trái là liệt kê nguồn cho cả pool trên mỗi rank; số bên phải là các dải đã gộp cho một yêu cầu. Phạm vi hai số khác nhau.
- Đơn vị của số liệu là số descriptor, không phải giây, byte mỗi giây hay điểm benchmark.
- Chuỗi cuối slide là các bước xác minh tiếp nối. Ánh xạ CPU đúng chưa đủ; vẫn cần thử truyền GPU thật và kiểm tra phản hồi.

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

### Nói nhanh · 10–20 giây

Lỗi đến từ cách chia trọng số: mỗi phần có 192 phần tử, không chia hết cho block 128 mà cách thực thi yêu cầu. Đổi cách phân phối expert cho 384 phần tử, vừa ba block. Điều này sửa tính tương thích để thử tiếp, chưa chứng minh hiệu năng tăng.

![Slide 08](../../submission-review/ai-journey-update-20261030/slides/assets/slide-08.png)

### Slide muốn nói gì

Giải thích một lỗi triển khai cụ thể do căn chỉnh block FP8 và thay đổi hình học dùng để khôi phục một cách chia tương thích. Bài học là tương thích cho phép thử tải, nhưng chưa chứng minh dịch vụ hay chất lượng chạy thành công.

### Giải thích kết quả và lập luận

Đường triển khai bị lỗi yêu cầu mỗi phần trọng số chứa các block FP8 nguyên vẹn. Chia chiều liên quan cho tám được 192 phần tử: một block 128 và dư 64. Trong đường TP8/EP2 đã thử, mức chia tensor hiệu dụng của MoE là bốn, cho 384 phần tử, vừa ba block đầy. EP2 đổi cách phân phối expert; không cắt bỏ nửa model và không tiếp tục giảm độ chính xác số.

### Thuật ngữ và ký hiệu cần hiểu

- **FP8:** Định dạng trọng số dấu phẩy động 8-bit của checkpoint; trọng số được tổ chức thành block có độ rộng cố định trong đường kernel liên quan.
- **1,536:** Kích thước chiều trung gian MoE dùng trong phép tính phân vùng này.
- **128:** Độ rộng block FP8 trong đường triển khai này; một phần đầy tương thích gồm 128 phần tử.
- **TP8 / EP1:** Tensor parallelism tám phần với một expert partition; tensor parallelism MoE hiệu dụng là tám, cho 1536 ÷ 8 = 192 phần tử mỗi phân vùng.
- **128 + 64:** Phân vùng 192 phần tử chứa một block đầy 128 và phần dư 64, không phải block FP8 đầy đủ.
- **TP8 / EP2:** Tensor parallelism tám phần với hai expert partition; tensor parallelism MoE hiệu dụng là bốn, cho 1536 ÷ 4 = 384 phần tử.
- **3 × 128 = 384:** Phân vùng EP2 khớp ba block 128 phần tử đầy đủ. Đây là đổi bố trí, không loại bỏ expert hay trọng số.
- **SLA:** Thỏa thuận mức dịch vụ: quy tắc chấp nhận độ trễ kết hợp theo yêu cầu đã nêu ở slide trước.

### Cách diễn giải số liệu hoặc sơ đồ

- Đọc hai phép tính trước: 1536 ÷ 8 = 192 và 1536 ÷ 4 = 384.
- Các khối trái biểu thị 128 cộng 64; phần đỏ là block chưa đầy và gây lỗi tải trong đường đã thử.
- Các khối phải là ba đoạn 128 đầy đủ. Chân trang liệt kê các điều kiện còn phải kiểm tra: startup, SLA và chất lượng đầu ra.

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

### Nói nhanh · 10–20 giây

Mỗi ý tưởng được so với cấu hình đối chứng, kiểm tra chạy đúng rồi đo lại nếu có lợi. Phép đo đầy đủ gồm 60 giây chạy làm nóng, 120 giây thu số liệu và 30 giây chờ request còn lại. Job kết thúc chưa đủ để kết luận có cải tiến.

![Slide 09](../../submission-review/ai-journey-update-20261030/slides/assets/slide-09.png)

### Slide muốn nói gì

Mô tả kỷ luật bằng chứng dùng để quyết định ý tưởng nào đáng chạy và nhánh nào nên đóng. Slide nối các câu chuyện kỹ thuật ban đầu với kết quả backend đo sau đó, đồng thời ghi rõ các pha đo đầy đủ.

### Giải thích kết quả và lập luận

Quy trình giúp tránh biến một ý tưởng hợp lý thành lời khẳng định hiệu năng quá sớm. Nêu nguyên nhân muốn kiểm tra, giữ cấu hình đối chứng, đổi yếu tố cần thử, kiểm tra đúng đường code đã chạy và đầu ra còn hợp lệ, rồi mới so điểm. Mức tăng có ích cần được chạy lại trước khi chọn. Một job kết thúc bằng lỗi có thể cho bài học tích hợp, nhưng chưa trở thành phép đo hiệu năng hợp lệ.

### Thuật ngữ và ký hiệu cần hiểu

- **01–04:** Số thứ tự của bốn bước thí nghiệm, không phải điểm số hay mã job.
- **60 s warmup:** Một phút khởi động theo giao thức đo trước cửa sổ tính điểm.
- **120 s measurement:** Cửa sổ tính điểm hai phút của giao thức đo đầy đủ được trình bày.
- **30 s grace:** Khoảng chờ sau phép đo để yêu cầu đang xử lý hoàn tất; không phải một giai đoạn steady-state tính điểm khác.
- **closed loop:** Client giữ số yêu cầu đang xử lý ở mức mục tiêu và thay yêu cầu mới khi một yêu cầu hoàn tất.
- **4,000 / 200 tokens:** Kích thước cố định của token đầu vào và đầu ra được yêu cầu như slide trước.
- **SLA accounting:** Đánh giá độ trễ và thành công theo từng yêu cầu, kể cả tính yêu cầu lỗi vào mẫu số.

### Cách diễn giải số liệu hoặc sơ đồ

- Bước 1 dùng log, trace và source để hình thành giả thuyết; bước 2 thay một yếu tố được xác định rõ.
- Bước 3 xác minh giao thức, runtime thực sự kích hoạt, SLA và đầu ra; bước 4 xác nhận lợi ích có ý nghĩa hoặc đóng nhánh thua.
- Thời lượng bên dưới tính bằng giây, không phải mili giây. Cửa sổ đo kéo dài 120 giây.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Quy trình lưu lại cả giao thức benchmark và các điều kiện về đường thực thi và đầu ra, đồng thời phân biệt job đã kết thúc với kết quả hợp lệ đã được rà soát.
- **Giả thuyết:** Thay đổi giới hạn rõ, có đối chứng và quy tắc dừng sẽ tạo bằng chứng dễ diễn giải hơn so với quét rộng hoặc lặp mù.
- **Kết luận được hỗ trợ:** Ứng viên cần kiểm tra thực tế việc kích hoạt và lặp lại độc lập trước khi chọn; job thiếu bản xuất hợp lệ hoặc không đạt điều kiện chưa chứng minh được kết quả.
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

### Nói nhanh · 10–20 giây

Hành trình H200 đi từ khoảng 1.297 lên 3.044 token đầu ra đạt chuẩn mỗi giây. “Repeated” ở các mốc sau nghĩa là đã chạy lại để kiểm tra kết quả. Các mốc thay cả cấu hình lẫn tải, nên biểu đồ cho thấy tiến trình, không tách riêng đóng góp từng tối ưu.

![Slide 10](../../submission-review/ai-journey-update-20261030/slides/assets/slide-10.png)

### Slide muốn nói gì

Tóm lược theo lịch sử goodput H200 khi hệ thống được khôi phục, dùng backend theo từng giai đoạn, rồi đạt các điểm vận hành có phép đo lặp. Đây là bản đồ để định hướng cho bằng chứng chi tiết ở các slide sau, không phải biểu đồ ablation nhân quả.

### Giải thích kết quả và lập luận

Đọc các cột như lịch sử các điểm vận hành, không phải một phép thử chỉ cộng thêm từng tối ưu. Các nhóm ở trục ngang thay đổi bố trí, backend và concurrency client; chiều cao là token đầu ra đạt chuẩn độ trễ mỗi giây. Xu hướng tăng cho thấy quá trình tìm được cấu hình đo tốt hơn, nhưng không cho biết riêng mỗi thay đổi đóng góp bao nhiêu.

### Thuật ngữ và ký hiệu cần hiểu

- **H200:** Nền tảng GPU của các mốc này; không gộp các giá trị với kết quả H100.
- **Trục hoành: milestones và N:** Các giai đoạn thí nghiệm dạng phân loại và concurrency của client, không phải thời gian đã trôi qua hay biến liên tục. N là số yêu cầu mục tiêu đang xử lý đồng thời.
- **Trục tung: Good output tokens/s:** Thông lượng token đầu ra đạt chuẩn theo điều kiện độ trễ kết hợp; nhãn cột đã làm tròn.
- **FI:** FlashInfer, backend attention trong giai đoạn có nhãn tương ứng.
- **MNNVL:** Backend collective/truyền thông dùng trong tổ hợp phía decode.
- **DG:** DeepGEMM, dùng cho prefill ở các mốc có nhãn này.
- **HPC:** Backend decode HPC-Ops trong mốc “DG + HPC”.
- **N60 / N62 / N64 repeated:** Các điểm vận hành đầy đủ về sau có phép đo lặp; cột N64 ở 3.044 tóm tắt trung bình ba lần chạy đầy đủ lịch sử.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

Kết hợp FlashInfer cho attention với MNNVL cho giao tiếp đạt khoảng 2.631 token đạt chuẩn mỗi giây, hơn đối chứng giao tiếp MNNVL khoảng 1,43%. Hai cách thực thi dùng chung tài nguyên nên phải đo tổ hợp trực tiếp, không cộng mức tăng từ các phép thử riêng.

![Slide 11](../../submission-review/ai-journey-update-20261030/slides/assets/slide-11.png)

### Slide muốn nói gì

Giới thiệu kết quả tương tác backend chi tiết đầu tiên: tổ hợp attention và collective vượt các lựa chọn riêng trong so sánh H200 N52 cùng tải. Bài học thiết kế là phải đo trực tiếp tương tác, không cộng số học các mức tăng riêng lẻ.

### Giải thích kết quả và lập luận

Backend attention thực hiện phép attention; backend collective truyền hoặc kết hợp dữ liệu giữa các tiến trình GPU đang hợp tác. Chúng cùng dùng tài nguyên tính toán và giao tiếp, nên đổi cả hai có thể tạo tương tác. Phép đo MNNVL riêng được chạy mới để có đối chứng gần hơn khi đánh giá tổ hợp. Lợi ích của tổ hợp được đo trực tiếp, không tính bằng cộng mức tăng của các phép thử riêng.

### Thuật ngữ và ký hiệu cần hiểu

- **H200 · N52:** Nền tảng GPU và concurrency của client trong so sánh này. N52 là mục tiêu giữ 52 yêu cầu đang xử lý.
- **FlashInfer decode only:** Đường attention decode dùng FlashInfer trong khi cấu hình collective giữ ở thiết lập đối chứng.
- **MNNVL decode only:** Đường collective/truyền thông decode dùng MNNVL, chưa kết hợp FlashInfer như hàng cuối.
- **MNNVL fresh control:** Phép đo đối chứng mới ở thiết lập MNNVL, dùng để giảm phụ thuộc vào một điểm so sánh cũ.
- **MNNVL + FlashInfer:** Tổ hợp backend được đo trực tiếp trong job 23904.
- **good tokens/s:** Token đầu ra đạt chuẩn mỗi giây theo điều kiện độ trễ cấp yêu cầu.
- **SLA:** Phần trăm request đồng thời đạt TTFT và mean ITL trong benchmark nhóm tự chạy trên cluster; chưa được BTC xác nhận.
- **job:** Mã hồ sơ scheduler liên kết hàng với bằng chứng lần chạy; không phải thứ hạng.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

Tăng số request đồng thời từ 62 lên 64 giúp thông lượng đạt chuẩn tăng 1,08%. Chạy lại bằng một job đầy đủ khác vẫn đạt khoảng 3.044 token mỗi giây. Đây là ý nghĩa của “repeat”: kiểm tra kết quả có tái lập, thay vì chọn một lần đo cao.

![Slide 12](../../submission-review/ai-journey-update-20261030/slides/assets/slide-12.png)

### Slide muốn nói gì

Giải thích vì sao chọn N64: so sánh đầy đủ và lần lặp độc lập ủng hộ mức tăng vừa phải; tín hiệu tốt từ phép thử N68 ngắn không còn đáng kể khi đo đầy đủ.

### Giải thích kết quả và lập luận

Cột trái là control N62, giữa là lần chạy N64 đầy đủ đầu tiên, phải là lần triển khai N64 mới. Trước hết so goodput, sau đó kiểm tra tỷ lệ request đạt, độ trễ và lỗi để xem chúng có làm thay đổi cách hiểu về mức tăng throughput hay không.

### Thuật ngữ và ký hiệu cần hiểu

- **N62/N64:** Mức concurrency client được cấu hình; không phải số GPU hay batch decode.
- **Good tokens/s:** Request đủ điều kiện mỗi giây nhân mục tiêu output cố định 200 token.
- **SLA đồng thời:** Tỷ lệ request đạt cả TTFT ≤ 3.000 ms và ITL trung bình/request ≤ 20 ms.
- **60/120/30:** Số giây wnhánh thử nghiệmup / đo điểm / grace.
- **N68:** Sàng lọc concurrency cao hơn nhưng gain giảm ở cặp đầy đủ.
- **Protocol đầy đủ 60/120/30:** Làm nóng dịch vụ 60 giây, tính request trong 120 giây, rồi chờ 30 giây để request đang chạy kết thúc. Grace không tính vào throughput.
- **Lần triển khai độc lập:** Một lần scheduler cấp tài nguyên và chạy lại setting N64. Đây là allocation lặp, không chứng minh GPU khác loại; hai run N64 lấy mẫu cùng tập GPU UUID.
- **N62 / N64 / N68:** Mức concurrency request đang chờ của client, không phải số GPU hay batch decode.

### Cách diễn giải số liệu hoặc sơ đồ

- Lần triển khai N64 độc lập 25373 lặp lại ở 3.044,075, thấp hơn nguồn chỉ 0,014%. Đọc lần lượt các cột goodput, SLA đồng thời, TTFT trung bình, ITL trung bình và lỗi/hủy. Throughput tăng nhưng TTFT trung bình nhích lên và SLA giảm nhẹ. Protocol gồm wnhánh thử nghiệmup 60 giây, đo 120 giây, grace 30 giây. Sàng lọc ngắn N68 gợi ý +2,27%, nhưng cặp đầy đủ chỉ còn +0,083%; phép chạy ngắn để sàng lọc, không thay thế phép đo chính. Hai lần N64 dùng cùng tập GPU UUID được lấy mẫu, nên chỉ hỗ trợ khả năng lặp do nhóm tự chạy, không tạo khoảng tin cậy hay optimum toàn cục. Giả thuyết: concurrency vừa phải cải thiện sử dụng pipeline. Kết luận: giữ N64 tại operating point đã đo. Chưa biết riêng đóng góp của hàng đợi, truyền dữ liệu và tính toán.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.
- Nhãn run đầy đủ ở đây chỉ protocol cố định: 60 giây làm nóng dịch vụ, 120 giây tính request và 30 giây grace để request còn chạy kết thúc. Allocation lặp nghĩa scheduler khởi chạy run khác; không có nghĩa kiến trúc GPU khác. Hai run N64 này lấy mẫu cùng tập GPU UUID, nên lần lặp hỗ trợ khả năng tái lập setting, nhưng không chứng minh phần cứng đa dạng hay tạo khoảng tin cậy.

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

### Nói nhanh · 10–20 giây

Profile ghi lại hoạt động GPU để tìm hướng thử tiếp. Nhóm giao tiếp và chuẩn hóa chiếm khoảng 23,48% tổng thời lượng kernel đã ghi. Đây là đầu mối điều tra, không phải 23,48% thời gian chờ của request, vì các kernel có thể chạy chồng lấp.

![Slide 13](../../submission-review/ai-journey-update-20261030/slides/assets/slide-13.png)

### Slide muốn nói gì

Giải thích cách dùng profile để đặt câu hỏi có thể kiểm chứng tiếp theo, đồng thời tách tỷ trọng kernel trong phép chẩn đoán khỏi hiệu năng dịch vụ đầu cuối.

### Giải thích kết quả và lập luận

Đọc mỗi tỷ lệ là phần thời lượng kernel đã ghi thuộc nhóm được nêu trong các trace chẩn đoán riêng. Đây không phải phần thời gian request: kernel GPU có thể chạy chồng lấp, còn wall time của request gồm cả hàng đợi và công việc chưa được profile. Dùng các hàng để chọn phép thử tiếp theo, không để dự đoán mức tăng tốc.

### Thuật ngữ và ký hiệu cần hiểu

- **GEMM:** Phép nhân ma trận tổng quát trong kernel tính toán.
- **MNNVL:** Backend giao tiếp qua NVIDIA NVLink.
- **RMSNorm:** Phép chuẩn hóa căn bậc hai trung bình bình phương.
- **Kernel duration:** Thời lượng kernel GPU được ghi; không phải wall time đầu-cuối.
- **N48/N58:** Hai mức concurrency tách biệt cho diagnostic và deployment lặp.
- **Profile:** Run chẩn đoán ghi thời lượng một số kernel GPU và tín hiệu runtime khi dịch vụ xử lý workload.
- **Tỷ trọng thời gian kernel:** Phần của tổng thời lượng kernel đã ghi thuộc một nhóm. Kernel GPU có thể chồng lấp, nên đây không phải phần walltime request đã trôi qua.
- **Diagnostic N48 và lần lặp N58:** Hai giai đoạn riêng trong job 24819: N58 lặp deployment; N48 thu trace profile. Không gán tỷ trọng kernel N48 cho hành vi dịch vụ N58.
- **MNNVL / RMSNorm:** MNNVL là đường giao tiếp collective qua NVLink; RMSNorm chuẩn hóa activation của model.

### Cách diễn giải số liệu hoặc sơ đồ

- Các nhóm decode được nêu là HPC group GEMM 21,642%, MNNVL collective/RMSNorm 23,479%, và FlashInfer paged attention 15,064% tổng kernel duration đã ghi. Đây là tổng mô tả, không phải tỷ trọng wall time đầu cuối: kernel có thể chạy chồng lấp và trace chỉ ghi hoạt động có coverage. GEMM là phép nhân ma trận; MNNVL là backend giao tiếp; RMSNorm chuẩn hóa activation; rank là một tiến trình phân tán. Ba nhóm gợi ý câu hỏi về MoE, chiến lược giao tiếp và attention theo pha. Chúng không dự đoán mức tăng tương ứng, chứng minh FLOP saturation, hay giải thích nhân quả kết quả dịch vụ N58/N60. Cần tách N48 diagnostic khỏi lần lặp N60. Giả thuyết: nhóm kernel lớn đáng khảo sát. Kết luận: dùng trace để thiết kế phép thử dịch vụ có đối chứng. Chưa biết tỷ lệ latency từng pha cho mỗi request.
- Profile là phép ghi đo: công cụ lưu một số hoạt động khi workload chạy. Các tỷ lệ cộng thời lượng kernel trên những rank/GPU được ghi. Vì kernel có thể chồng lấp, đồng thời hàng đợi, CPU, khoảng chờ giao tiếp và hoạt động không được ghi cũng chiếm thời gian trôi qua, không thể đọc tỷ lệ này thành phần thời gian request dành cho từng thành phần. Diagnostic N48 tách biệt với lần lặp deployment N58.

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

### Nói nhanh · 10–20 giây

Đổi cách thực thi decode giúp thông lượng đạt chuẩn tăng 5,30%, và một lần triển khai khác cho kết quả gần như cũ. Tuy nhiên, token đầu chậm thêm khoảng 125 mili giây, còn khoảng cách token ngắn hơn. Đây là đánh đổi đã đo, không phải mọi chỉ số đều tốt hơn.

![Slide 14](../../submission-review/ai-journey-update-20261030/slides/assets/slide-14.png)

### Slide muốn nói gì

Chứng minh một đánh đổi backend có lần lặp: thông lượng hữu ích và khoảng token tốt hơn vẫn có thể đi cùng thời gian chờ token đầu xấu hơn.

### Giải thích kết quả và lập luận

So sánh control và treatment ở cùng tải N60. Throughput tăng và khoảng cách giữa token ngắn lại, nhưng token đầu đến muộn hơn trung bình. Đây là đánh đổi dịch vụ được đo trong một lần triển khai mới, không phải khẳng định backend luôn có kết quả như vậy.

### Thuật ngữ và ký hiệu cần hiểu

- **HPC-Ops:** Decode runner được cung cấp để thử nghiệm; nhóm đánh giá nó chứ không nhận là tác giả.
- **DeepGEMM:** Backend nhân ma trận prefill được giữ cố định.
- **TTFT:** Thời gian tới token đầu, tính bằng mili giây.
- **ITL:** Độ trễ giữa token; ở đây là trung bình theo request.
- **N60:** Mức concurrency client trong phép so sánh đầy đủ.
- **Lần lặp độc lập:** Deployment mới chạy lại treatment. Nó xác nhận điểm tương tự trong thiết lập này, không có nghĩa dùng thế hệ phần cứng khác.
- **TTFT / ITL trung bình request:** Thời gian tới token đầu / khoảng thời gian trung bình giữa các token trong một request.
- **Goodput:** Ở đây là request AIPerf đủ điều kiện mỗi giây × mục tiêu cố định 200 output token.
- **Protocol đầy đủ 60/120/30:** Làm nóng 60 giây, đo dịch vụ trong 120 giây, rồi chờ 30 giây cho request còn chạy kết thúc; chỉ khoảng giữa được tính điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- Cả hai giữ DeepGEMM prefill và chunk 8192 tại full N60. TTFT trung bình tăng 125,335 ms (822,292 lên 947,627), còn ITL trung bình của request giảm 1,644 ms (16,579 xuống 14,934). SLA đồng thời là 98,7599% so với 98,8178%. Treatment ban đầu 24738 đạt 2.990,151; lần lặp 24913 thấp hơn 0,033%. Lần lặp gần bằng củng cố tính tái lập của tương tác này. HPC-Ops là backend được cung cấp, không phải kernel do nhóm phát minh. TTFT là thời gian tới token đầu; ITL là khoảng giữa token; SLA đồng thời cần đạt cả hai giới hạn. Kết luận: bằng chứng dịch vụ đầy đủ hỗ trợ cấu hình này, không chứng minh HPC-Ops luôn hơn. Chất lượng full-set official chưa xác minh; không suy ra nguyên nhân kernel cụ thể.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.
- “Triển khai độc lập” nghĩa là một lần chạy mới do scheduler cấp cho cùng treatment, không phải thử nghiệm trên thế hệ GPU khác. Lần lặp 2.989,175 thấp hơn treatment ban đầu 24738 đạt 2.990,151 chỉ 0,033%. Điều này hỗ trợ tính lặp tại operating point này. Goodput cao hơn không xóa mức tăng TTFT trung bình; cấu hình dịch vụ có thể đánh đổi thời gian token đầu với khoảng cách giữa các token sau.

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

### Nói nhanh · 10–20 giây

Mỗi chấm là một request: xanh đạt cả hai giới hạn độ trễ, cam trượt ít nhất một. Tổng cộng 98,58% đạt; cả 27 request trượt đều chờ token đầu quá lâu. Vì vậy điểm trung bình cao vẫn cần xem phần request chậm nhất.

![Slide 15](../../submission-review/ai-journey-update-20261030/slides/assets/slide-15.png)

### Slide muốn nói gì

Cho thấy cần xem từng request: hiệu năng trung bình cao vẫn có những request chờ token đầu quá lâu; số trung bình không giải thích được nguyên nhân của phần đuôi này.

### Giải thích kết quả và lập luận

Mỗi điểm là một request, không phải một token. Request chỉ đạt khi nằm bên trái ngưỡng TTFT đỏ dọc tại 3.000 ms và dưới ngưỡng ITL trung bình/request đỏ ngang tại 20 ms. Teal đậm (#23373B; có thể nhìn xanh lam-lục) biểu thị đạt cả hai; cam (#EB811B; có thể nhìn vàng) biểu thị trượt ít nhất một điều kiện. Dải xanh nhạt chỉ biểu thị TTFT, không phải đạt đồng thời. Cụm đậm hơn là các điểm chồng alpha, không phải lớp request thứ ba.

### Thuật ngữ và ký hiệu cần hiểu

- **TTFT:** Thời gian từ khi request bắt đầu tới token đầu, mili giây.
- **Request-mean ITL:** Khoảng cách trung bình token của request đó, mili giây.
- **Đạt đồng thời:** Cả hai giới hạn áp dụng cho cùng request. Dưới đường TTFT vẫn có thể trượt nếu trên đường ITL.
- **Đạt/tổng:** 1.875 request đạt cả hai trên toàn bộ 1.902 request.
- **Alpha overlap:** Điểm chồng làm vùng đậm hơn; không phải lớp kết quả riêng.
- **Native runtime:** Đường thực thi server gốc dùng trong job 26766, khác đường portable replay. Đây là khác biệt phần mềm chạy, không phải khác model GPU.
- **ITL trung bình/request:** Khoảng cách trung bình giữa các token liên tiếp trong một request; khác latency đầu-cuối của request.
- **P95:** Phân vị 95: 95% request quan sát có giá trị không vượt mức này; mô tả phần đuôi, không phải trung bình.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- Trục X là TTFT mili giây; Y là ITL trung bình mỗi request. Hai đường đỏ dọc/ngang đánh dấu 3.000 ms và 20 ms. Request chỉ đạt nếu ở bên trái và phía dưới cả hai đường. Teal đậm (#23373B; có thể nhìn xanh lam-lục) đạt đồng thời; cam (#EB811B; có thể nhìn vàng) trượt ít nhất một điều kiện. Vùng xanh nhạt chỉ biểu diễn TTFT, không xác nhận ITL. Cụm đậm hơn là chồng alpha, không phải nhóm thứ ba. Kết quả: 1.875/1.902, tức 98,580%, đạt đồng thời; 27 trượt TTFT, không trượt ITL, không lỗi/hủy request. TTFT trung bình/p95 là 1.108,869/1.311,693 ms; ITL trung bình/p95 là 15,0075/15,1930 ms. Mọi miss bắt đầu trong 13,004 ms từ lúc mở admission đo; đây chỉ là tương quan. Giả thuyết: nhóm request đầu có thể chịu một hiệu ứng khởi đầu. Kết luận: mọi miss SLA quan sát được trong run này chỉ thuộc TTFT. Chưa biết nguyên nhân và phân tách queue/prefill/transfer/compute.
- Đi sang trái là chờ token đầu ít hơn; đi xuống là khoảng token trung bình ngắn hơn. Vùng đạt nằm bên trái hoặc ngay trên đường x = 3000 VÀ bên dưới hoặc ngay trên đường y = 20; bằng ngưỡng vẫn đạt. Chấm cam được vẽ to hơn để dễ thấy lỗi, không có nghĩa request lớn hơn hay nhiều token hơn.
- Đây là phân bố các request trong một lần chạy, không phải đường biên tối ưu giữa nhiều cấu hình. Hình không tách được thời gian chờ hàng đợi, tính prefill, truyền KV và decode.
- Đây là profile request từ native server runtime, không phải benchmark kernel tổng hợp. TTFT đo thời gian chờ token đầu; ITL trung bình/request tóm tắt các khoảng token sau khi sinh bắt đầu. P95 mô tả phần chậm của phân bố. 27 miss bắt đầu trong 13,004 ms sau admission của profile, nhưng thời điểm đó không cho biết hàng đợi, prefill, truyền KV hay tính toán gây ra chúng.

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

### Nói nhanh · 10–20 giây

H100 có cấu hình tối ưu riêng: điểm cao nhất từng đo khoảng 2.433 token đầu ra đạt chuẩn mỗi giây; lần đối chứng đầy đủ mới khoảng 2.399. Hai số cho thấy có biến động giữa lần chạy, và không thể lấy thẳng để kết luận tối ưu H200 tốt hơn bao nhiêu.

![Slide 16](../../submission-review/ai-journey-update-20261030/slides/assets/slide-16.png)

### Slide muốn nói gì

Tách điểm vận hành H100, cài đặt backend và biến động giữa các lần chạy khỏi các tuyên bố trên H200.

### Giải thích kết quả và lập luận

Kết quả lịch sử cao và control đầy đủ mới trả lời hai câu hỏi khác nhau: một bên là quan sát đơn lẻ cao nhất còn lưu, bên kia là run hoàn chỉnh mới cùng kết quả đạt điều kiện. H100 dùng settings prefill/decode khác H200, nên các số này không cô lập được tác động của thế hệ GPU.

### Thuật ngữ và ký hiệu cần hiểu

- **H100/H200:** Hai hệ thống GPU với operating point được đo riêng.
- **N54:** Concurrency client của so sánh H100.
- **TP8:** Tensor parallelism trên tám GPU.
- **EP8:** Expert parallelism trên tám phân vùng.
- **Chunk 4096:** Kích thước chunk prefill của cấu hình H100 này.
- **Allocation:** Một lần scheduler cấp tài nguyên và chạy. Số allocation là số lần chạy, không phải số loại GPU hay chắc chắn số thiết bị vật lý riêng biệt.
- **Đỉnh đơn lẻ được lưu:** Quan sát cao nhất trong chuỗi lịch sử nêu ra; không phải control mới hay ước lượng phân bố.
- **TP8 / EP8:** Tensor parallelism trải trên tám GPU; expert parallelism phân phối expert trên tám phân vùng.
- **Operating point:** Kết quả gắn với cấu hình phần cứng, phần mềm, tải và backend cụ thể.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- Control đầy đủ mới 225227 đạt 2.399,186728 với SLA đồng thời 98,015873%, không lỗi/hủy. H100 dùng HPC-Ops cho prefill và decode, chunk 4096, TP8/EP8; H200 dùng DeepGEMM prefill và chunk 8192. Vì vậy đây không phải so sánh phần cứng ghép cặp hay hệ số quy đổi. Giữ cả đỉnh và control mới vì chúng trả lời câu hỏi khác nhau. TP là tensor parallelism; EP là expert parallelism. EAGLE truyền dữ liệu chức năng được không đồng nghĩa có kết quả hiệu năng aggregate được chấp nhận. Giả thuyết: mỗi họ phần cứng cần settings riêng. Kết luận: báo riêng điểm H100 cùng cấu hình thật. Chưa biết hiệu ứng nhân quả giữa thế hệ GPU hay hệ số phổ quát.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.
- Allocation là một run/lần cấp tài nguyên theo lịch; H100 so với H200 mới là khác biệt họ phần cứng. Mức cao được lưu là một run đã quan sát; control mới là phép đo hoàn chỉnh mới. H100 dùng HPC-Ops cho cả hai pha và chunk 4.096 token, còn H200 dùng backend prefill và chunk 8.192 khác; vì vậy không thể chia hai số để tạo hệ số thế hệ GPU.

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

### Nói nhanh · 10–20 giây

FA3 giúp token đầu tới sớm hơn khoảng 119 mili giây, nhưng khoảng cách token dài hơn tích lũy suốt câu trả lời. Thông lượng đạt chuẩn giảm 0,81%. Vì mục tiêu tổng thể xấu đi, chúng tôi giữ FlashInfer cho cấu hình decode này.

![Slide 17](../../submission-review/ai-journey-update-20261030/slides/assets/slide-17.png)

### Slide muốn nói gì

Dùng phép thử decode FA3 không thành công để giải thích vì sao chỉ tối ưu thời gian token đầu có thể làm mục tiêu thông lượng cuối cùng xấu đi.

### Giải thích kết quả và lập luận

FA3 rút ngắn thời gian tới token đầu, nhưng khoảng cách token trung bình dài hơn lặp lại qua phần output dài. Hãy dùng hàng latency request và goodput đo được làm căn cứ đầu-cuối; không chọn backend chỉ dựa trên TTFT.

### Thuật ngữ và ký hiệu cần hiểu

- **FlashInfer:** Backend attention decode của control.
- **FA3:** Backend attention decode treatment; prefill vẫn dùng FA3.
- **Goodput:** Số output token đủ điều kiện trên giây.
- **Request latency:** Thời lượng request đầu-cuối, gồm sinh token.
- **Cặp ghép:** Hai run đầy đủ chỉ khác yếu tố attention decode định thử.
- **Latency request trung bình:** Thời lượng đầu-cuối trung bình của request, gồm chờ token đầu và thời gian sinh phần output còn lại.
- **Vì sao TTFT có thể gây hiểu nhầm:** Tiết kiệm trước token đầu có thể nhỏ hơn phần chậm thêm trên mỗi token lặp qua câu trả lời dài.
- **Thay đổi ghép cặp:** Trong cặp H100 N54 này chỉ attention decode thay đổi; prefill vẫn dùng FA3 ở cả hai nhánh.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- FlashInfer so với FA3: good tokens/s 2.420,945 và 2.401,284; TTFT trung bình 713,199 và 594,276 ms; ITL 18,214 và 18,988 ms; latency request 4.337,853 và 4.372,813 ms. FA3 giảm 118,922 ms tới token đầu, nhưng ITL tăng 0,773 ms; khoảng 199 khoảng token làm phát sinh xấp xỉ 154 ms. Latency request tăng và goodput giảm 0,812%. Giữ FlashInfer cho decode setting này; FA3 vẫn dùng ở prefill. Một cặp không thể xếp hạng backend phổ quát hay chỉ ra chính xác nhân quả kernel.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.
- Latency request trung bình đo được tăng 34,960 ms (4.372,813 − 4.337,853), còn goodput giảm 0,812%. Chênh lệch ITL nhỏ trên từng khoảng nhưng lặp qua câu trả lời dài; đây là cách diễn giải hợp lý tradeoff, không phải phép đo nhân quả kernel riêng. So sánh chỉ hỗ trợ giữ FlashInfer cho setting decode H100 đã thử.

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

### Nói nhanh · 10–20 giây

Đọc trọng số trước lúc khởi động ban đầu tiết kiệm 18,74% thời gian job. Nhưng khi đảo thứ tự chạy để kiểm tra lại, mức tiết kiệm chỉ còn 9,84%, dưới ngưỡng 10% nhóm đã đặt. Vì vậy nhóm không chọn cách này chỉ dựa vào cặp đo thuận lợi đầu tiên.

![Slide 18](../../submission-review/ai-journey-update-20261030/slides/assets/slide-18.png)

### Slide muốn nói gì

Giải thích giá trị của việc đảo thứ tự thử và giữ ngưỡng chấp nhận đã đặt trước, thay vì chọn kết quả thuận lợi đầu tiên.

### Giải thích kết quả và lập luận

So sánh cặp thứ hai sau khi đảo điều kiện chạy trước. Mức tiết kiệm walltime 18,74% ở cặp đầu không lặp lại: cặp đảo thứ tự chỉ tiết kiệm 9,84%, thấp hơn ngưỡng 10% đã định trước. Walltime scheduler gồm khởi động và dọn dẹp, nên khác với goodput ổn định.

### Thuật ngữ và ký hiệu cần hiểu

- **Read-first:** Đọc checkpoint prefill trước khi chạy dịch vụ đo để thử giả thuyết giảm chi phí startup.
- **Walltime:** Thời gian chạy scheduler đo bằng giây.
- **Đảo thứ tự:** Phép xác nhận chạy hai nhánh thử nghiệm theo thứ tự ngược.
- **Ngưỡng chi phí:** Điều kiện định trước tiết kiệm walltime tối thiểu 10%.
- **Thay đổi goodput:** Chênh throughput đủ điều kiện so với control ghép cặp.
- **Walltime scheduler:** Thời gian allocation trôi qua gồm startup và cleanup; khác cửa sổ phục vụ 120 giây được tính điểm và khác goodput.
- **Cold prefix và cold OS cache:** Cold prefix nghĩa là tiền tố prompt chưa được tái sử dụng từ cache prefix/KV của model. Cold OS page cache nghĩa là dữ liệu tệp chưa có sẵn trong cache hệ điều hành. Thí nghiệm không xác nhận OS cache lạnh nên không thể khẳng định nguyên nhân là đọc lưu trữ lạnh.
- **Xác nhận đảo thứ tự:** Lặp cặp với thứ tự chạy ngược để xem chênh lệch đầu tiên có do thứ tự hoặc cache ấm không.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- Cặp đầy đủ đầu: off/read-first 934/759 giây, tiết kiệm 18,74%, goodput −0,66%. Cặp xác nhận đảo thứ tự: 854/770 giây, tiết kiệm 9,84%, goodput −0,33%. Ngưỡng định trước yêu cầu tiết kiệm ít nhất 10% và goodput giảm không quá 2%; phép xác nhận đạt điều kiện throughput nhưng trượt ngưỡng walltime nên không đưa vào cấu hình chính. Cache chưa rõ trạng thái và node khác nhau nên không thể quy nguyên nhân cho cold storage. Walltime là thời lượng scheduler, không phải throughput ổn định.
- Ý tưởng read-first liên quan việc nạp checkpoint prefill lúc khởi động. “Cold prefix” nói model có tái sử dụng mục cache tiền tố prompt/KV hay không; nó không mô tả cache tệp của hệ điều hành. OS cache lạnh nghĩa là các trang checkpoint phải được đọc từ lưu trữ thay vì cache bộ nhớ. Vì trạng thái cache chưa xác nhận và node khác nhau, không thể quy chênh lệch walltime cho lưu trữ lạnh. Kết quả đảo thứ tự không đạt ngưỡng định trước nên nhóm không áp dụng thay đổi.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Lần đầu tiết kiệm 18,74%; xác nhận đảo thứ tự 9,84%, dưới ngưỡng 10%.
- **Giả thuyết:** Read-first có thể giảm walltime startup.
- **Kết luận được hỗ trợ:** Đóng nhánh, không đưa vào cấu hình chính vì phép xác nhận không đạt ngưỡng.
- **Chưa biết / giới hạn:** Cache và khác biệt node không cho phép quy cho cold storage.

### Lời nói mẫu

“Cặp đầu tiết kiệm 18,74%, nhưng đảo thứ tự chỉ còn 9,84%, thấp hơn ngưỡng 10% đã công bố. Goodput chỉ đổi nhẹ. Vì phép xác nhận trượt ngưỡng, chúng tôi đóng nhánh thay vì đưa vào cấu hình chính kết quả thuận lợi đầu tiên.”

### Điều không nên nói

Không chỉ báo cặp đầu thuận lợi. Cache chưa rõ nên diễn giải nhân quả bị giới hạn.

### Câu chuyển slide

“Một câu hỏi riêng là liệu tỷ số phần cứng do nhóm tự chạy dự báo được tải gần kề không.”

---

<a id="slide-19"></a>

## Slide 19 — A local N52 calibration, not a universal multiplier

### Nói nhanh · 10–20 giây

Ở cùng cấu hình và 52 request đồng thời, thông lượng H200 đo được bằng khoảng 1,188 lần H100. Nhóm dùng tỷ số này làm mốc thử dự báo ở tải gần đó. Nó không phải hệ số đổi mọi kết quả H100 sang H200, nhất là khi cấu hình khác.

![Slide 19](../../submission-review/ai-journey-update-20261030/slides/assets/slide-19.png)

### Slide muốn nói gì

Đặt một cầu nối đo được nhưng có phạm vi giữa hai hệ thống, và giải thích vì sao đây không phải quy tắc đổi mọi kết quả H100 sang H200.

### Giải thích kết quả và lập luận

Tỷ số là goodput trung bình H200 chia cho H100 với cùng model/cấu hình tại N52. Hai và bốn allocation là số lần chạy được scheduler cấp tài nguyên; không có nghĩa là có hai và bốn loại GPU khác nhau, cũng không chứng minh mọi allocation dùng phần cứng duy nhất. Một tỷ số này là điểm hiệu chuẩn, không phải quy luật quy đổi.

### Thuật ngữ và ký hiệu cần hiểu

- **N52:** Concurrency client của điểm calibration này.
- **Allocation:** Một lần phân bổ tài nguyên/run theo lịch.
- **Tỷ số hệ thống:** Goodput trung bình H200 chia H100 trong phép đo này.
- **Không đơn vị:** Tỷ số không mang đơn vị vật lý.
- **Điểm calibration:** Một tải/cấu hình, không phải đường quy đổi đã xác thực.
- **Allocation là số lần chạy, không phải phần cứng độc lập:** Hai allocation H100 và bốn H200 là các lần chạy do scheduler cấp. Chỉ riêng số lượng không chứng minh máy riêng, GPU vật lý riêng hay đa dạng phần cứng.
- **Tỷ số 1,188096805:** Trung bình H200 2.632,181 ÷ H100 2.215,460 ở combo N52 này. Tỷ số không đơn vị và chỉ áp dụng cho phép so này.
- **Calibration:** Điểm tham chiếu được đo để lập một ước lượng cụ thể; không phải hàm quy đổi đã xác thực qua workload.
- **Phần cứng độc lập:** Loại accelerator khác nhau (H100 với H200), không chỉ là một allocation scheduler khác cùng loại.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- Tỷ số H200/H100 quan sát là 1,188096805, không đơn vị. Nó chỉ mô tả điểm đo này. Lặp ở một tải không định nghĩa hàm quy đổi hay prediction interval; không áp dụng tỷ số cho TTFT, ITL, SLA hay nhánh backend khác. Allocation là lần phân bổ tài nguyên, không phải thế hệ phần cứng độc lập. Giả thuyết: calibration do nhóm tự chạy có thể hỗ trợ dự báo held-out (phép đo được giữ riêng để kiểm tra dự báo) gần kề. Kết luận: chỉ dùng làm đầu vào dự báo có phạm vi. Chưa biết biến thiên theo tải/cấu hình và uncertainty.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.
- Hai trung bình in trên slide là 2.215,460 và 2.632,181 good output tokens/s, lần lượt từ hai lần cấp tài nguyên H100 và bốn lần H200. Tỷ số 1,188096805 không có đơn vị; tại điểm đo này nó tương ứng thông lượng hệ thống cao hơn khoảng 18,81%, không phải tăng 18,81 điểm phần trăm SLA.
- Hai allocation H100 và bốn H200 là số lần lặp run được scheduler cấp. Chúng không chứng minh có hai so với bốn thiết bị phần cứng riêng, cũng không phải bốn quần thể phần cứng độc lập. “Phần cứng độc lập” ở đây nghĩa là họ accelerator khác nhau, H100 so với H200. Lặp tại một tải giúp mô tả điểm vận hành đó, nhưng không xác lập hàm quy đổi ở concurrency hay backend khác.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Trung bình N52 cho tỷ số H200/H100 do nhóm tự chạy 1,188096805.
- **Giả thuyết:** Calibration do nhóm tự chạy có thể hỗ trợ điểm held-out (phép đo được giữ riêng để kiểm tra dự báo) gần kề.
- **Kết luận được hỗ trợ:** Xem là tỷ số giới hạn, không phải quy luật đổi phần cứng.
- **Chưa biết / giới hạn:** Biến thiên theo tải, settings và metric latency chưa biết.

### Lời nói mẫu

“Ở cùng combo N52, goodput H200 chia H100 là 1,1881. Đây là liên hệ hệ thống do nhóm tự chạy, không phải hệ số quy đổi phổ quát. Slide sau kiểm tra một dự báo đã khóa tại N50.”

### Điều không nên nói

Tỷ số chỉ áp dụng cho tải/cấu hình nêu; không phải phần trăm hay hệ số đổi latency.

### Câu chuyển slide

“Giờ kiểm tra dự báo được cố định trước khi thấy dữ liệu H200 held-out (phép đo được giữ riêng để kiểm tra dự báo).”

---

<a id="slide-20"></a>

## Slide 20 — Freeze the forecast, then test it on H200

### Nói nhanh · 10–20 giây

Nhóm ghi dự báo trước khi thấy phép đo: khoảng 2.642 token đạt chuẩn mỗi giây, thực tế khoảng 2.602. Sai lệch âm 1,54% nằm trong dung sai 2% đã đặt. Tuy nhiên, khoảng bất định trước đó còn thiếu; một lần dự báo gần đúng chưa chứng minh quy đổi luôn đúng.

![Slide 20](../../submission-review/ai-journey-update-20261030/slides/assets/slide-20.png)

### Slide muốn nói gì

Minh họa kiểm tra dự báo minh bạch: khóa dự báo trước, thử một điểm chưa dùng để hiệu chỉnh, rồi báo cả việc đạt dung sai lẫn phần bất định còn thiếu.

### Giải thích kết quả và lập luận

Dự báo được ghi lại trước khi xem kết quả H200 held-out (phép đo được giữ riêng để kiểm tra dự báo). Sai số có dấu −1,5371% nằm trong dung sai vận hành ±2% đã định trước. Sensitivity range trước đó chỉ thay đổi một số đầu vào và bỏ qua sai số mô hình, nên không phải khoảng bất định dự báo đầy đủ; việc kết quả nằm ngoài phạm vi ấy là hạn chế thật, không phải lý do để sửa dự báo đã khóa.

### Thuật ngữ và ký hiệu cần hiểu

- **Held-out:** Phép đo không dùng để hiệu chuẩn, chỉ xem sau khi ghi dự báo; nó kiểm tra khả năng chuyển sang quan sát mới.
- **Sai số có dấu:** (đo được − dự báo) chia theo dự báo; âm nghĩa là goodput đo được thấp hơn.
- **Dung sai ±2%:** Ngưỡng vận hành định trước, không phải khoảng tin cậy 95%.
- **Sensitivity range:** Khoảng tạo ra khi thay đổi một số đầu vào. Đây không phải tổng bất định dự báo nếu thiếu sai số mô hình, biến thiên giữa run hoặc yếu tố chưa mô hình hóa.
- **N50:** Concurrency client của phép kiểm tra dự báo.
- **Dung sai vận hành:** Khoảng đạt thực dụng ±2% đã định trước; không phải khoảng tin cậy 95% hay thanh sai số đo.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- Job held-out (phép đo được giữ riêng để kiểm tra dự báo) 24272 đo 2.601,629; sai số có dấu −1,5371%, trong dung sai vận hành định trước ±2%. Kết quả nằm ngoài sensitivity range cũ vì phạm vi đó bỏ sót model error. Dung sai không phải khoảng tin cậy 95% hay thanh sai số đo. Không fit lại tỷ số sau khi thấy điểm này. Một phép held-out (phép đo được giữ riêng để kiểm tra dự báo) đạt chỉ hỗ trợ kiểm tra do nhóm tự chạy, không chứng minh độ đúng dự báo rộng.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.
- Dấu âm nghĩa là phép đo thấp hơn dự báo: 2.601,629 so với 2.642,244 good output tokens/s. Sai số có dấu bằng (đo − dự báo) / dự báo × 100; ký hiệu ± là dung sai cho phép hai phía, không phải thanh sai số của phép đo.
- Dự báo được kiểm tra held-out (phép đo được giữ riêng để kiểm tra dự báo) vì kết quả H200 N50 không được dùng để tính nó. Khoảng ±2% là quy tắc chấp nhận vận hành chọn trước phép đo. Khoảng sensitivity hỏi phép tính đổi thế nào khi thay một số đầu vào; chỉ có thể gọi là khoảng bất định dự báo nếu nó còn phản ánh các sai số và biến thiên quan trọng. Phạm vi cũ bỏ qua sai số mô hình, nên quan sát held-out (phép đo được giữ riêng để kiểm tra dự báo) phát hiện hạn chế dù vẫn qua dung sai thực dụng.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Sai số held-out (phép đo được giữ riêng để kiểm tra dự báo) −1,5371%, trong ±2% nhưng ngoài sensitivity range thiếu sót.
- **Giả thuyết:** Calibration N52 có thể dự báo throughput N50 gần kề.
- **Kết luận được hỗ trợ:** Một tiêu chí vận hành do nhóm áp dụng đạt; vẫn ghi rõ thiếu model error.
- **Chưa biết / giới hạn:** Độ chính xác rộng và uncertainty đầy đủ chưa biết.

### Lời nói mẫu

“Dự báo được khóa trước khi có kết quả. H200 đo 2.601,629 so với 2.642,244 dự đoán, sai số −1,5371%. Kết quả trong dung sai vận hành định trước, nhưng ngoài sensitivity range cũ chưa đầy đủ. Chúng tôi giữ cả hai phát hiện và không fit lại.”

### Điều không nên nói

±2% là dung sai vận hành, không phải khoảng tin cậy. Không fit lại sau khi thấy held-out (phép đo được giữ riêng để kiểm tra dự báo).

### Câu chuyển slide

“Tiếp theo so sánh các giả thuyết nhỏ dựa trên source bằng outcome đầy đủ.”

---

<a id="slide-21"></a>

## Slide 21 — Use source evidence to test one small hypothesis

### Nói nhanh · 10–20 giây

Đọc source giúp biết thay đổi nào thực sự được thực thi; benchmark mới cho biết có ích không. Đổi cache chỉ tăng 0,24%, còn một thay đổi attention làm mất 6,39% thông lượng đạt chuẩn. Vì vậy bật được tính năng hay cải thiện một chỉ số chưa đủ để thay cấu hình chính.

![Slide 21](../../submission-review/ai-journey-update-20261030/slides/assets/slide-21.png)

### Slide muốn nói gì

Giải thích cách giữ hoặc đóng ý tưởng có cơ sở từ source sau phép đo đầy đủ; đường code hợp lý hay mức tăng nhỏ chưa đủ để đưa vào cấu hình chính.

### Giải thích kết quả và lập luận

Với mỗi hàng, hỏi ba điều: kiểm tra source có dự đoán đúng đường code không, bằng chứng runtime có xác nhận đường đó đang hoạt động không, và run đầy đủ ghép cặp có cải thiện dịch vụ đủ đáng kể không? Các tỷ lệ nhỏ thuộc những thí nghiệm riêng, không được cộng dồn.

### Thuật ngữ và ký hiệu cần hiểu

- **Bằng chứng source:** Code và runtime xác nhận đường nào được chọn/kích hoạt.
- **Exact-ID preflight:** Kiểm tra batching tokenizer giữ đúng token ID.
- **p95 TTFT:** Phân vị 95 của thời gian token đầu; có thể xấu hơn dù trung bình cải thiện.
- **Ngưỡng mức tăng hữu ích:** Ngưỡng định trước để đưa vào cấu hình chính.
- **Prefill/decode:** Xử lý prompt / sinh token tự hồi quy.
- **Kiểm tra source:** Đọc phần cài đặt để biết nhánh code dự kiến chạy; bằng chứng runtime phải xác nhận nhánh đó thực sự hoạt động.
- **Kiểm tra trước exact token ID:** Kiểm tra tính đúng: batching phải giữ nguyên token ID trước khi đo tốc độ.
- **Mức tăng hữu ích:** Mức cải thiện tối thiểu đặt trước để đáng đổi cấu hình phục vụ; số dương rất nhỏ chưa chắc hữu ích.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- Source và runtime activation xác nhận code path chạy, không chứng minh bottleneck. Mỗi quyết định dựa trên kết quả full có control và ngưỡng useful-gain. p95 là đuôi phân vị 95, không phải trung bình. Không cộng phần trăm giữa các nhánh.
- Kiểm tra source và xác nhận runtime trả lời implementation dự định có được dùng không; run đầy đủ ghép cặp trả lời nó có giúp ích không. Đây là các bước bằng chứng riêng. Thay đổi dương nhỏ có thể nằm trong biến thiên hoặc quá nhỏ để hữu ích; một metric tốt hơn vẫn có thể đi cùng phần đuôi xấu hơn hay goodput thấp hơn. Vì vậy bảng giữ cả nhánh âm và dưới ngưỡng thay vì cộng dồn các gain nổi bật.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Gain nhỏ không đạt ngưỡng; tail cache hoặc goodput attention xấu hơn.
- **Giả thuyết:** Settings có cơ sở source có thể cải thiện một metric dịch vụ.
- **Kết luận được hỗ trợ:** Chỉ đưa vào cấu hình chính thay đổi đã kích hoạt, ghép cặp và có gain đầy đủ hữu ích.
- **Chưa biết / giới hạn:** Chưa xác lập bottleneck chung hay hiệu ứng ở cấu hình khác.

### Lời nói mẫu

“Flag chạy được mới chỉ là khởi đầu. Chúng tôi xác nhận activation, chạy protocol đầy đủ và so với control. Gain nhỏ dưới ngưỡng không được đưa vào cấu hình chính; ITL tốt hơn nhưng mất 6,39% goodput cũng không phải cải thiện.”

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

“Latency dịch vụ và độ chính xác model là hai câu hỏi chấp nhận riêng.”

---

<a id="slide-22"></a>

## Slide 22 — Latency acceptance is separate from model accuracy

### Nói nhanh · 10–20 giây

Dịch vụ nhanh và câu trả lời đúng là hai việc phải kiểm tra riêng. Các bộ kiểm tra nhỏ đạt 7/8 và 12/12, nhưng chưa chứng nhận yêu cầu ít nhất 99% điểm chất lượng tham chiếu của BTC. Vì vậy nhóm chỉ báo điều đã đo, chưa khẳng định đạt chất lượng chính thức.

![Slide 22](../../submission-review/ai-journey-update-20261030/slides/assets/slide-22.png)

### Slide muốn nói gì

Tách dịch vụ nhanh khỏi chất lượng trả lời đúng: sanity check nhỏ và việc đạt độ trễ không chứng nhận yêu cầu chất lượng chính thức trên bộ đánh giá đầy đủ.

### Giải thích kết quả và lập luận

Chấp nhận latency hỏi request được phục vụ nhanh đến đâu; chất lượng model hỏi câu trả lời đạt điểm reference của ban tổ chức hay không. Smoke 7/8 và retrieval 12/12 là kiểm tra regression nhỏ do nhóm chạy, không phải đánh giá accuracy official trên toàn bộ tập. Đạt ngưỡng latency không chứng minh đạt tối thiểu 99% điểm reference.

### Thuật ngữ và ký hiệu cần hiểu

- **SLA:** Tiêu chí latency dịch vụ ở cấp request.
- **Smoke:** Bộ kiểm tra nhỏ về hành vi cơ bản/regression.
- **Retrieval:** Sanity check retrieval do nhóm tự chạy, không phải benchmark quality official.
- **99% reference:** Ngưỡng chất lượng model official, hiện chưa xác minh.
- **FP8/BF16:** Trọng số FP8; activation và KV cache BF16.
- **Hiệu năng dịch vụ:** Đo tốc độ/độ trễ và tỷ lệ request đạt; tự nó không nói câu trả lời đúng về nghĩa hay không.
- **Chất lượng model official:** Đánh giá riêng của ban tổ chức, so câu trả lời với reference trên tập kiểm tra đầy đủ quy định; yêu cầu ở đây là ít nhất 99% reference.
- **Smoke / retrieval check:** Kiểm tra nhỏ do nhóm tự chạy về regression và retrieval; không thay thế bài kiểm tra quality official.
- **Trọng số FP8, activation/KV BF16:** Định dạng trọng số khác định dạng activation và KV cache; đây là định dạng số, không phải điểm chất lượng.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.
- **Sanity check do nhóm tự chạy:** Một số kiểm tra nhỏ do nhóm chạy trên môi trường được cấp để tìm regression; đây không phải đánh giá chất lượng full-set theo quy trình của ban tổ chức.

### Cách diễn giải số liệu hoặc sơ đồ

- Smoke do nhóm tự chạy là 7/8, không regression mới; retrieval là 12/12. Các kiểm tra nhỏ này không chứng nhận yêu cầu chất lượng official tối thiểu 99% reference. Primary giữ trọng số FP8 và activation/KV BF16; không dùng KV lượng tử hóa hay speculative decoding. SLA là chấp nhận latency dịch vụ; reference là chuẩn so chất lượng của organiser. Kết luận: báo riêng hiệu năng dịch vụ và ghi rõ quality official chưa xác minh.
- Kết quả latency là kết quả hiệu năng: đo thời gian phục vụ request và tỷ lệ đạt giới hạn. Yêu cầu 99% reference là kết quả chất lượng: so câu trả lời sinh ra với bài đánh giá reference do ban tổ chức chỉ định. Smoke và retrieval kiểm tra số trường hợp hạn chế, không ước lượng điểm quality toàn tập. Vì vậy chúng chỉ hỗ trợ kết luận “không phát hiện regression trong bộ kiểm tra nhỏ”, không phải “đã đạt accuracy official”.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** SLA latency và sanity check nhỏ đạt; chất lượng model official chưa xác minh.
- **Giả thuyết:** Giữ model trong khi đánh giá serving riêng với quality.
- **Kết luận được hỗ trợ:** Báo latency và quality official như hai kết quả riêng.
- **Chưa biết / giới hạn:** Ngưỡng full-set 99% reference vẫn chưa xác minh.

### Lời nói mẫu

“Dịch vụ đạt ngưỡng latency do nhóm tự chạy, các sanity check nhỏ không có regression mới. Đánh giá chất lượng official ở mức 99% reference chưa được xác minh, nên chúng tôi không tuyên bố chứng nhận hay ranking.”

### Điều không nên nói

Smoke và retrieval không phải chứng nhận accuracy đầy đủ.

### Câu chuyển slide

“Case EAGLE3 cho thấy cần báo cáo giả thuyết thất bại và công cụ được sửa như thế nào.”

---

<a id="slide-23"></a>

## Slide 23 — EAGLE3: follow the failed hypothesis through its repairs

### Nói nhanh · 10–20 giây

EAGLE3 dùng model phụ đề xuất token để model chính kiểm tra. Nhóm sửa lỗi triển khai để chạy được, nhưng cấu hình đo đầy đủ vẫn giảm 2,08% thông lượng đạt chuẩn. Bài học là tích hợp thành công chưa đồng nghĩa tăng tốc; nhóm không chọn nhánh đã đo này.

![Slide 23](../../submission-review/ai-journey-update-20261030/slides/assets/slide-23.png)

### Slide muốn nói gì

Giữ toàn bộ chuỗi lỗi và sửa của speculative decoding, rồi giải thích vì sao sửa được tích hợp vẫn chưa chứng minh có tăng tốc.

### Giải thích kết quả và lập luận

Theo dõi đúng trình tự. Đầu tiên, đặt draft worker ở mọi nơi làm trượt ngưỡng latency kết hợp. Sau đó validator nhầm lẫn yêu cầu vùng KV của draft trên prefill chỉ chạy target; sửa bộ kiểm tra cho phép retry hợp lệ nhưng không làm hiệu năng thay đổi. Cả retry ngắn lẫn run đầy đủ sau đó đều giảm goodput, nên các cấu hình đã thử được dừng thử nghiệm.

### Thuật ngữ và ký hiệu cần hiểu

- **EAGLE3:** Phương pháp speculative decoding đề xuất draft token.
- **Vị trí draft:** Vai trò worker chạy draft model.
- **KV region:** Vùng bộ nhớ KV cache gắn với một role.
- **Protocol ngắn:** Phép thử giới hạn, không phải benchmark hoàn chỉnh.
- **Protocol đầy đủ:** Workload, wnhánh thử nghiệmup, cửa sổ đo và grace hoàn chỉnh.
- **Speculative decoding EAGLE3:** Model draft đề xuất token; model target xác minh. Truyền draft đúng là kết quả chức năng, không chứng minh dịch vụ đầu-cuối nhanh hơn.
- **Validator nhận biết role:** Bộ kiểm tra chỉ đòi KV draft ở role worker thực sự chạy draft. Prefill chỉ chạy target không có vùng KV draft.
- **Run ngắn và run đầy đủ:** Pass ngắn chỉ xác nhận hành vi giới hạn; cần run workload cố định đầy đủ để so goodput dịch vụ.
- **Mất goodput:** Tốc độ output token đủ điều kiện thấp hơn control target-only ghép cặp.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- Thử nghiệm decode-only 25988 bị validator từ chối sai vì áp số KV region của draft lên prefill target-only. Sửa validator theo role nhưng vẫn giữ lỗi cũ. Retry ngắn 25998 qua protocol giới hạn nhưng mất 4,74% goodput so với control target-only. Thử nghiệm shallow full riêng 27238 đạt 2.971,628430 so với control 26949 ở 3.034,761104, giảm 2,080318%. Truyền draft chức năng không đồng nghĩa tăng tốc; telemetry acceptance thấp không phải phân tích thời gian nhân quả. EAGLE3 là speculative decoding; KV là key/value cache; full protocol là workload hoàn chỉnh; short protocol là phép thử giới hạn. Kết luận: đóng các nhánh thử nghiệm đã đo và giữ lịch sử lỗi/sửa. Chưa biết cấu hình khác và quality official.
- Lỗi validator là sai sót ở công cụ/giao diện, không phải bằng chứng model tự lỗi. Validator sau sửa áp kiểm tra theo vai trò worker: prefill chỉ chạy target không bị yêu cầu sở hữu KV draft. Sau sửa, retry decode-only ngắn mất 4,74% goodput; run shallow đầy đủ sau đó mất 2,080318%. Truyền speculative token đúng chức năng và pass run ngắn không đủ để đổi cấu hình phục vụ khi goodput đầy đủ thấp hơn.

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

“Tổng kết quay lại N64 được lặp lại và kết quả cache nhỏ không được đưa vào cấu hình chính.”

---

<a id="slide-24"></a>

## Slide 24 — Topology → transport → kernels → replication

### Nói nhanh · 10–20 giây

Cấu hình 64 request đồng thời đạt trung bình khoảng 3.044 token đầu ra đạt chuẩn mỗi giây qua ba lần đo đầy đủ. “Repeated” nghĩa là đã chạy lại benchmark để kiểm tra khả năng tái lập. Nhóm ưu tiên bằng chứng này thay vì một điểm cao đơn lẻ; chất lượng chính thức vẫn chưa xác minh.

![Slide 24](../../submission-review/ai-journey-update-20261030/slides/assets/slide-24.png)

### Slide muốn nói gì

Kết phần AI chính bằng cấu hình có bằng chứng lặp lại và giới hạn của kết luận, thay vì chọn một đỉnh điểm riêng lẻ.

### Giải thích kết quả và lập luận

Mốc được chọn là trung bình của ba run N64 lịch sử đầy đủ. Run native-runtime sau đó là phép đo riêng vì dùng môi trường thực thi server khác; không gộp hai nhóm như thể chúng thuộc cùng một chuỗi kiểm soát. Candidate cache có số cao nhất, nhưng gain 0,240921% thấp hơn ngưỡng lợi ích đã đặt ra.

### Thuật ngữ và ký hiệu cần hiểu

- **Trung bình ba run:** Trung bình các run N64 đầy đủ lịch sử 25366/25373/25487.
- **Native runtime:** Job 26766 dùng môi trường thực thi server native, khác runtime lịch sử. Runtime là stack phần mềm khởi chạy/chạy server, không phải phần cứng GPU.
- **Cặp cache:** Control mới 27376 so với candidate 27378.
- **+0,240921%:** Gain candidate, thấp hơn ngưỡng lợi ích hữu ích định trước.
- **Quality official:** Yêu cầu accuracy full-set, chưa xác minh ở đây.
- **Chuỗi N64 lịch sử:** Ba run đầy đủ 25366/25373/25487 trung bình 3.044,400475 good output tokens/s.
- **Control cache mới:** Job 27376 so với candidate 27378; chênh điểm +0,240921% thấp hơn ngưỡng lợi ích hữu ích.
- **Run do nhóm review:** Run do nhóm chạy trên cluster được cấp và kiểm tra bằng raw output/runtime gate nội bộ. Đây không phải ranking hay chứng nhận quality do ban tổ chức cấp.
- **Protocol đầy đủ 60/120/30:** Với benchmark này: warmup 60 giây, đo tính điểm 120 giây và grace 30 giây cho request đang chạy; grace không tính điểm.
- **Do nhóm chạy và review:** Nhóm chạy phép đo trên cluster được cấp và kiểm tra raw request, runtime cùng các điều kiện bắt buộc. “Review” không phải chứng nhận của ban tổ chức, ranking contest, hay chạy trên máy cá nhân.

### Cách diễn giải số liệu hoặc sơ đồ

- Job native-runtime sau đó 26766 đạt độc lập 3.045,501509 và SLA đồng thời 98,580442%; cần báo riêng vì runtime path khác. Kết quả cache full cao nhất 27378 đạt 3.048,446289, chỉ +0,240921% so với control mới 27376, dưới ngưỡng useful-gain. Các replay hợp lệ thấp hơn quanh 2.802–2.831 vẫn được lưu. Lặp lại hỗ trợ chọn N64, không chứng minh optimum toàn cục. Không tuyên bố speculative speedup, chứng nhận quality official hay speedup nhân quả của native runtime.
- Good output tokens/s là đơn vị thông lượng (mong muốn cao hơn); độ trễ dùng mili giây (mong muốn thấp hơn); joint SLA là phần trăm request, không phải độ chính xác model. N là request đồng thời ở client, không phải GPU. Chỉ đọc những đại lượng thực sự có trên slide.
- Trung bình lịch sử và điểm native-runtime đều là phép đo nhóm chạy, đã review đầy đủ trên cluster accelerator được cấp; “review” nghĩa raw request và runtime đã được kiểm tra, không phải ban tổ chức chứng nhận thứ hạng hay quality. Native runtime là môi trường phần mềm thực thi, không phải thế hệ GPU mới. Giữ số 3.045,501509 riêng với trung bình lịch sử ba run vì runtime path khác nhau. Không chọn kết quả cache cao hơn về số học khi gain dưới ngưỡng thay đổi hữu ích đã định trước.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Trung bình N64 lịch sử được lặp; cache tăng 0,240921%; runtime native báo riêng.
- **Giả thuyết:** Điểm được lặp lại đáng chọn hơn một đỉnh đơn độc.
- **Kết luận được hỗ trợ:** Giữ N64; không đưa vào cấu hình chính gain cache nhỏ.
- **Chưa biết / giới hạn:** Optimum toàn cục, quality official và khác biệt runtime nhân quả chưa biết.

### Lời nói mẫu

“Điểm được chọn là trung bình N64 lịch sử đã lặp lại. Kết quả native sau đó tương tự nhưng báo riêng. Đỉnh cache chỉ hơn control 0,24% nên không đưa vào cấu hình chính. Chúng tôi giữ cả run thấp hợp lệ. Đây là operating point đo được, không phải optimum toàn cục; quality official vẫn cần xác minh.”

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

“Phần tiếp theo đổi chủ đề sang nghiên cứu HPC CPU/OpenFOAM.”

---

<a id="slide-25"></a>

## Slide 25 — Appendix · diagnose performance drift with controlled cells

### Nói nhanh · 10–20 giây

Ba lần đo đầy đủ với 64 request đồng thời đạt khoảng 3.044 token đạt chuẩn mỗi giây; một đối chứng ngắn sau đó chỉ khoảng 2.560. Nhưng thời lượng và cài đặt khác nhau. Nhóm thử lại để tìm nguyên nhân, chưa chứng minh một thay đổi riêng nào giải thích chênh lệch.

![Slide 25](../../submission-review/ai-journey-update-20261030/slides/assets/slide-25.png)

**Phần dự phòng AI: chỉ mở khi cần giải thích sâu hơn.**

### Slide muốn nói gì

Giải thích vì sao độ lệch điểm quan sát được chưa chỉ ra nguyên nhân, và vì sao lần chạy đầy đủ về sau là tái lập kết quả chứ chưa chứng minh phục hồi do một thay đổi cụ thể.

### Giải thích kết quả và lập luận

Hãy đọc điểm theo ba loại bằng chứng. Trung bình lịch sử đến từ ba lần N64 đầy đủ. Đối chứng khoảng 2,560 là phép đo ngắn, đồng thời khác chính sách graph, giới hạn yêu cầu và điều kiện harness/cách quan sát; vì vậy chênh lệch trộn lẫn thay đổi quy trình lẫn cấu hình. Lần phát lại cấu hình cũ đạt 2,830.923547 trong một lần chạy đầy đủ hợp lệ. Lần native đạt 3,045.501509 trong một đường thực thi về sau. Hai kết quả gần nhau không chứng minh cài đặt nào đã khôi phục hiệu năng.

### Thuật ngữ và ký hiệu cần hiểu

- **N64:** Client nhắm duy trì 64 request đang xử lý; đây là mức tải request, không phải 64 GPU.
- **protocol đầy đủ và ngắn:** Protocol đầy đủ gồm warmup 60 giây, profiling 120 giây và grace 30 giây. Đối chứng ngắn có thời gian đo ngắn hơn nên không so điểm trực tiếp với lần đầy đủ.
- **độ lệch điểm:** Khác biệt giữa các lần đo đặt ra câu hỏi; tự nó không chỉ ra nguyên nhân.
- **runtime native:** Đường thực thi serving riêng về sau dùng ở lần đầy đủ 26766. Tên gọi xác định đường đã thử; tự nó không có nghĩa nhanh hơn và không giải thích vì sao điểm đổi.
- **phục hồi nhân quả:** Bằng chứng cho thấy một thay đổi cụ thể khôi phục điểm, thường cần so sánh có kiểm soát và cô lập thay đổi đó.
- **giới hạn request / chính sách graph:** Giới hạn request chặn số request đang chạy; chính sách graph chọn dạng decode nào dùng GPU graph đã capture. Cả hai đã đổi ở đối chứng về sau.

### Cách diễn giải số liệu hoặc sơ đồ

- Một lần chạy đầy đủ có warmup 60 giây, cửa sổ profiling được tính điểm 120 giây và grace 30 giây. Đối chứng ngắn không có cùng cửa sổ quan sát, nên điểm của nó báo hiệu độ lệch nhưng không phải so sánh khớp quy trình đầy đủ.
- Phát lại cấu hình cũ đạt 2,830.923547; lần native đầy đủ về sau đạt 3,045.501509. So sánh graph/tiếp nhận không tìm ra một nguyên nhân hữu ích duy nhất. Giữ lại cả hai kết quả hợp lệ.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** N64 đầy đủ lịch sử trung bình 3,044.400475; đối chứng ngắn khoảng 2,560; phát lại đầy đủ hợp lệ đạt 2,830.923547; lần native 26766 đạt 3,045.501509.
- **Giả thuyết:** Thay đổi graph prefill, giới hạn request đang chạy hoặc điều kiện harness có thể góp phần tạo độ lệch.
- **Kết luận được hỗ trợ:** Lần chạy đầy đủ về sau tái lập gần mức lịch sử trong một chuỗi runtime riêng; chưa chứng minh một cài đặt nào gây ra chênh lệch.
- **Chưa biết / giới hạn:** Chưa tách được mức đóng góp của graph, giới hạn request, độ dài protocol, harness và biến động quan sát.

### Lời nói mẫu

Ba lần chạy đầy đủ lịch sử với tải mục tiêu 64 request đồng thời đạt trung bình khoảng 3,044 token đầu ra tốt mỗi giây. Đối chứng ngắn về sau khoảng 2,560, nhưng đo ít thời gian hơn và đổi cài đặt graph cùng giới hạn request. Phát lại cấu hình cũ đầy đủ cho điểm thấp hơn; một lần chạy qua đường serving khác về sau gần mức lịch sử. Đó là lần tái lập riêng, chưa chứng minh cài đặt nào gây phục hồi.

### Điều không nên nói

Không coi đối chứng ngắn là lần đầy đủ tương đương, không quy điểm về sau cho một cài đặt, và không bỏ lần phát lại cấu hình cũ hợp lệ nhưng thấp hơn.

### Câu chuyển slide

Tiếp theo, phân biệt probe thành phần tiềm năng với bằng chứng serving toàn mô hình.

---

<a id="slide-26"></a>

## Slide 26 — Appendix · profiles and source also close attractive detours

### Nói nhanh · 10–20 giây

Gói attention mới đạt khoảng 2.549 token đạt chuẩn mỗi giây ở 52 request đồng thời, nhưng đổi nhiều yếu tố nên không tách được nguyên nhân. Các thử nghiệm tính toán nhỏ chưa chứng minh cả model nhanh hơn; lần biên dịch model thật bị lỗi trước khi có điểm.

![Slide 26](../../submission-review/ai-journey-update-20261030/slides/assets/slide-26.png)

### Slide muốn nói gì

Cho thấy thử nghiệm thành phần và đọc mã nguồn có thể loại bỏ hướng thử mà chưa chứng minh mô hình đầy đủ chạy nhanh hơn.

### Giải thích kết quả và lập luận

Mỗi hàng trả lời một câu hỏi khác nhau. Điểm attention-DP là quan sát end-to-end ở N52, nhưng nhiều cài đặt đổi cùng lúc nên không thể xác định yếu tố nào làm giảm điểm. Kết quả Triton là probe kernel trên một số dạng đại diện: nó kiểm tra thành phần, không chạy trọn đường serving Qwen. Lần torch.compile đi vào mã mô hình thật nhưng dừng ở assertion RoPE/fused-KV trước khi có điểm. Fixture C++ chỉ chạy helper trên CPU. Các mức bằng chứng đó giải thích vì sao quyết định thận trọng.

### Thuật ngữ và ký hiệu cần hiểu

- **probe:** Phép thử nhỏ, cô lập một thành phần hoặc vài dạng dữ liệu. Nó cho biết thành phần hoạt động ra sao trong phép thử đó, không dự đoán toàn bộ dịch vụ.
- **fixture:** Dữ liệu thử nhỏ để kiểm tra helper hoặc API. Fixture CPU qua không đồng nghĩa có lần serving GPU.
- **đọc mã nguồn:** Kiểm tra code để biết cài đặt có được hỗ trợ hoặc sử dụng không. Đây là bằng chứng khả năng, không chứng minh mô hình đã chạy theo đường đó.
- **thử nghiệm toàn mô hình:** Khởi động mô hình phân tán thật, phục vụ request và đo đầu ra. Lần compile ở đây dừng trước bước chấm điểm.
- **DP / FP8:** DP là song song dữ liệu, cách phân phối công việc request/mô hình. FP8 là số dấu phẩy động 8 bit dùng cho trọng số.
- **Triton / DeepGEMM:** Các hệ thống kernel GPU được thử trên dạng đại diện; kết luận chỉ áp dụng cho những probe đó.
- **ngân sách SM:** Giới hạn số streaming multiprocessor GPU mà kernel được dùng; kết quả kernel chưa chắc chuyển thành hiệu năng dịch vụ end-to-end.
- **RoPE / fused-KV:** RoPE mã hóa vị trí token. Đường mô hình compile gặp assertion khi phép này tương tác với giao diện cache key-value hợp nhất.

### Cách diễn giải số liệu hoặc sơ đồ

- Gói attention-DP với DeepGEMM/DeepEP đạt 2,549.20 ở N52, thấp hơn điểm MNNVL được giữ lại; nhiều cài đặt đi cùng nhau nên không thể kết luận về một cờ. Probe FP8 Triton đại diện thua DeepGEMM.
- Ngân sách SM 80/96/120 cho kết quả pha trộn hoặc không đạt tiêu chí nhất quán. Lần compile mô hình thật gặp assertion trước benchmark. Fixture cache/API C++ kiểm tra logic helper, nhưng không chạy tích hợp GPU, khởi động phân tán hay chất lượng serving.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Gói attention nhiều yếu tố có điểm thấp hơn; probe kernel đại diện thua; kiểm tra SM pha trộn; compile mô hình thật không có điểm; fixture C++ chỉ chạy CPU.
- **Giả thuyết:** Bố trí attention, kernel, ngân sách SM, đường compile hoặc API cache khác có thể cải thiện dịch vụ đầy đủ.
- **Kết luận được hỗ trợ:** Có thể đóng một đầu mối thành phần hoặc giữ nó như nhận xét mã nguồn, nhưng chưa chứng minh tăng tốc mô hình đầy đủ. Các dạng Triton đã thử không vượt DeepGEMM.
- **Chưa biết / giới hạn:** Dạng khác hoặc giao diện compile tương thích có thể cho kết quả khác; chưa có lần chạy mô hình compile đầy đủ nào qua.

### Lời nói mẫu

Một số hàng thử kernel GPU nhỏ, một số chạy helper trên CPU, một số chỉ đọc mã nguồn. Chúng giúp loại bỏ ý tưởng không được hỗ trợ, nhưng không khởi chạy mô hình phân tán đầy đủ để chấm câu trả lời. Lần compile thật đi vào mã Qwen rồi dừng khi phép mã hóa vị trí xoay gặp giao diện cache key-value hợp nhất không tương thích. Không có điểm serving.

### Điều không nên nói

Không biến probe kernel, fixture CPU hay kiểm tra đường code thành khẳng định về tốc độ hoặc độ đúng của mô hình đầy đủ.

### Câu chuyển slide

Slide sau mô tả cấu hình serving H200 được chọn và cấu hình H100 riêng.

---

<a id="slide-27"></a>

## Slide 27 — Appendix · the selected AI deployment is N64

### Nói nhanh · 10–20 giây

Cấu hình H200 được chọn giữ tối đa 64 request đồng thời, dùng hai nhóm bốn GPU xử lý prompt và một nhóm tám GPU sinh token. H100 dùng cấu hình riêng. Đây là cách triển khai có bằng chứng đo, chưa phải chứng nhận chất lượng câu trả lời của BTC.

![Slide 27](../../submission-review/ai-journey-update-20261030/slides/assets/slide-27.png)

### Slide muốn nói gì

Mô tả cấu hình AI được giữ lại mà không hàm ý kết quả H100 và H200 có thể so sánh trực tiếp.

### Giải thích kết quả và lập luận

Đọc mỗi hàng như một lựa chọn vận hành: xử lý đầu vào (prefill), sinh token (decode), nhóm GPU song song hoặc độ chính xác số. H200 dùng concurrency client 64; quan sát H100 riêng dùng 54 cùng backend/chunk prefill khác. Cả hai dùng trọng số đích FP8 và activation/trạng thái KV BF16. Dòng cuối nêu thành phần decode và giao tiếp chung. Do phần cứng và cài đặt khác nhau, đây là sơ đồ triển khai, không phải benchmark phần cứng.

### Thuật ngữ và ký hiệu cần hiểu

- **prefill / decode:** Prefill xử lý prompt trước khi sinh; decode tạo token câu trả lời từng bước.
- **TP / EP:** Tensor parallelism chia phép toán tensor qua GPU. Expert parallelism phân phối các khối expert của mô hình mixture-of-experts.
- **FP8 / BF16:** Trọng số FP8 dùng số dấu phẩy động 8 bit. Activation và KV BF16 dùng định dạng 16 bit; đây là hai loại tensor khác nhau.
- **HPC-Ops / DeepGEMM:** Backend thực thi GPU dùng cho các pha dịch vụ khác nhau; tên backend tự nó không chứng minh tăng tốc.
- **FlashInfer / MNNVL:** FlashInfer cung cấp kernel attention decode; MNNVL cung cấp giao tiếp collective GPU. Chúng có vai trò khác nhau.
- **round-robin:** Request được phân lần lượt cho hai worker prefill.
- **sơ đồ triển khai:** Mô tả cách cấu hình dịch vụ đã đo, không chứng minh GPU hay cài đặt khác có cùng hiệu năng.

### Cách diễn giải số liệu hoặc sơ đồ

- Cấu hình H200 chọn hai worker prefill TP4 với DeepGEMM và chunk 8.192, cộng một worker decode TP8/EP8 HPC-Ops. Bộ graph decode dày có bucket từ 1 đến 64.
- H100 giữ hai worker prefill TP4 HPC-Ops với chunk 4.096 và cùng nhóm decode TP8/EP8. FlashInfer cho attention decode, MNNVL cho giao tiếp, và định tuyến vòng tròn giữa hai worker prefill được dùng chung.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** H200 và H100 khác concurrency cùng backend/chunk prefill, nhưng giữ các định dạng trọng số và activation/KV như đã nêu.
- **Giả thuyết:** Cấu hình H200 N64 có cơ sở chọn làm chính tốt hơn vì đã có nhiều lần chạy đầy đủ.
- **Kết luận được hỗ trợ:** Báo cáo H100 riêng; vài cài đặt trùng nhau không biến chúng thành phép so sánh phần cứng có kiểm soát.
- **Chưa biết / giới hạn:** Độ chính xác chính thức và xác minh triển khai portable đầy đủ sau sửa reader vẫn còn mở.

### Lời nói mẫu

Đây là cấu hình H200 được chọn, không phải cuộc đua trực tiếp với H100. H200 xử lý prompt trên hai nhóm, mỗi nhóm bốn GPU, rồi sinh token trên một nhóm tám GPU có phân phối các expert. H100 dùng ít request đồng thời hơn và backend/chunk xử lý prompt khác. Cả hai giữ trọng số 8 bit và activation cùng KV 16 bit. Bản sửa reader được kiểm tra trên dữ liệu thật nhưng chưa qua phát lại GPU đầy đủ.

### Điều không nên nói

Không gộp điểm H100 và H200, suy ra hệ số đổi phần cứng, hay nhầm trọng số FP8 với activation/KV BF16.

### Câu chuyển slide

Tiếp theo, so sánh tài nguyên capture graph decode thưa đã tiết kiệm với tác động lên goodput.

---

<a id="slide-28"></a>

## Slide 28 — Appendix · sparse graphs save memory, not goodput

### Nói nhanh · 10–20 giây

Giảm số dạng đồ thị GPU lưu để phát lại giúp bộ nhớ capture mỗi tiến trình giảm từ 1,15 xuống 0,36 GB. Tuy nhiên, thông lượng đạt chuẩn lại giảm khoảng 0,37%. Tiết kiệm phần bộ nhớ này chưa giúp dịch vụ nhanh hơn, nên nhóm giữ cấu hình cũ.

![Slide 28](../../submission-review/ai-journey-update-20261030/slides/assets/slide-28.png)

### Slide muốn nói gì

Giải thích đánh đổi của graph thưa: bộ nhớ capture theo log trên mỗi rank giảm, pha capture ngắn hơn chút ít, nhưng goodput đo được thấp hơn.

### Giải thích kết quả và lập luận

So sánh cùng các đại lượng giữa hai cấu hình. Thay đổi 64 xuống 12 là số bucket dạng decode được capture, không phải số request đồng thời hay GPU. Bucket là một dạng thực thi đã capture để tái dùng; request không khớp chính xác có thể được đệm hoặc ánh xạ vào bucket gần đó. Ít bucket có thể giảm bộ nhớ graph và buffer capture đi kèm, nhưng có thể tăng công việc padding. Phép thử này không tách riêng lượng hay chi phí padding. Mức 1.15/0.36 GB là bộ nhớ liên quan capture trên mỗi rank decode, không phải tổng VRAM: trọng số, KV cache, workspace và cấp phát khác nằm riêng. Thời gian capture chỉ tính pha capture.

### Thuật ngữ và ký hiệu cần hiểu

- **bucket graph decode:** Một dạng thực thi GPU được capture để server phát lại cho một nhóm batch decode. Đây không phải số request.
- **padding:** Đệm batch hoặc hình dạng lên kích cỡ graph được hỗ trợ. Ít bucket có thể cần đệm nhiều hơn, nhưng lần chạy này không đo lượng hay chi phí đó.
- **bộ nhớ graph capture:** Bộ nhớ liên quan các graph GPU đã ghi để tái dùng và buffer đi kèm, báo cáo trên mỗi rank decode.
- **VRAM / GB / GiB:** VRAM là toàn bộ bộ nhớ GPU. Log ghi GB capture trên mỗi rank, không phải tổng VRAM hay GiB; trọng số và KV cache còn dùng bộ nhớ khác.
- **rank:** Một tiến trình worker phân tán; số liệu tính trên từng rank decode, không cộng tám rank.
- **goodput / ITL:** Goodput là request đủ điều kiện/giây nhân 200 token đầu ra yêu cầu. ITL là khoảng thời gian giữa các token sinh.
- **compile off:** Biên dịch mô hình bị tắt trong phép thử capture; capture thành công không xác nhận đường mô hình compile hoạt động.

### Cách diễn giải số liệu hoặc sơ đồ

- Ứng viên giảm bucket từ 64 xuống 12; capture được ghi nhận trên cả tám rank decode khi compile tắt. Bộ nhớ capture theo log giảm từ 1.15 xuống 0.36 GB mỗi rank. Thời gian capture đổi từ 101.46–101.49 xuống 95.98–96.05 giây.
- Goodput giảm từ 3,041.119598 ở đối chứng trước 27376 xuống 3,029.861122 ở ứng viên 27510, tức giảm 0.370208%. Mean request ITL tăng từ 14.991 lên 15.136 ms, dù TTFT tốt hơn.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Bộ nhớ capture của ứng viên thấp hơn và thời gian capture ngắn hơn chút ít; goodput thấp hơn đối chứng trước 0.370208%.
- **Giả thuyết:** Ít dạng graph hơn có thể tiết kiệm tài nguyên capture mà vẫn giữ mục tiêu dịch vụ.
- **Kết luận được hỗ trợ:** Ứng viên không cải thiện goodput; nhóm giữ graph dày. Không nói padding gây đổi điểm vì chưa đo riêng padding.
- **Chưa biết / giới hạn:** Chỉ có một đối chứng trước, seed engine khác nhau, và bộ nhớ capture không phải tổng bộ nhớ GPU.

### Lời nói mẫu

Ứng viên capture 12 dạng decode thay vì 64. Bộ nhớ graph capture theo log giảm từ 1.15 xuống 0.36 gigabyte mỗi rank, còn thời gian capture chỉ đổi vài giây. Nhưng goodput thấp hơn 0.370208 phần trăm và khoảng token trung bình tăng nhẹ. Ít dạng graph có thể cần padding thêm, nhưng lần này chưa đo padding. Nhóm giữ graph dày và không quy nguyên nhân cho chênh lệch điểm.

### Điều không nên nói

Không gọi số bucket là concurrency, bộ nhớ capture là tổng VRAM, hay thời gian capture là tổng thời lượng job. Padding chỉ là cơ chế có thể có, chưa phải giải thích đã đo.

### Câu chuyển slide

Tiếp theo là phạm vi của điểm serving tổng hợp và các kiểm tra chất lượng mô hình riêng còn mở.

---

<a id="slide-29"></a>

## Slide 29 — Appendix · what the benchmark actually measures

### Nói nhanh · 10–20 giây

Benchmark dùng prompt tổng hợp 4.000 token và yêu cầu sinh 200 token để đo tốc độ phục vụ, không chấm nội dung trả lời. Chất lượng phải được đánh giá riêng so với điểm tham chiếu của BTC; yêu cầu đạt ít nhất 99% điểm tham chiếu vẫn chưa được xác minh.

![Slide 29](../../submission-review/ai-journey-update-20261030/slides/assets/slide-29.png)

### Slide muốn nói gì

Giải thích benchmark serving đo trong khoảng nào, tính điểm ra sao và vì sao kết quả này tách biệt với độ chính xác mô hình.

### Giải thích kết quả và lập luận

Điểm chính là phân biệt workload được yêu cầu với bằng chứng được tính điểm. Client tổng hợp yêu cầu 4.000 token vào và 200 token ra, đồng thời giữ concurrency theo kiểu vòng kín. Worker và đường serving được làm nóng bằng lưu lượng riêng; sau đó AIPerf có warmup 60 giây, profiling 120 giây được chấm, và grace 30 giây. Chỉ profiling tính vào chỉ số hiệu năng. Grace kết thúc request còn dở, không phải cửa sổ chấm bổ sung. Tiêu chí 99% riêng là đánh giá chất lượng toàn tập, không phải độ trễ serving.

### Thuật ngữ và ký hiệu cần hiểu

- **AIPerf / vòng kín:** AIPerf gửi request và tính chỉ số. Tải vòng kín thay mỗi request vừa xong để duy trì mục tiêu số request đang xử lý.
- **protocol 60/120/30:** Số giây cho warmup AIPerf, profiling được chấm và grace. Chỉ 120 giây ở giữa tính điểm; grace cho request còn lại hoàn tất.
- **goodput:** Số request đủ điều kiện mỗi giây. Good output tokens/s chính thức bằng goodput AIPerf nhân với 200 token đầu ra yêu cầu.
- **giới hạn độ trễ request:** Request chỉ được tính tốt nếu TTFT không quá 3.000 ms và ITL trung bình request không quá 20 ms; ít nhất 90% mọi request phải đạt cả hai.
- **yêu cầu độ chính xác 99%:** Ban tổ chức yêu cầu chất lượng toàn tập ít nhất 99% tham chiếu FP8. Kiểm tra đầu ra nhỏ do nhóm chạy trên cluster được giao không chứng minh điều này.
- **token yêu cầu và token thực:** 4.000/200 là độ dài client yêu cầu. Chúng không chứng minh chính xác số token ID mô hình đã đọc hay sinh cho từng request.

### Cách diễn giải số liệu hoặc sơ đồ

- Goodput là số request đủ điều kiện mỗi giây theo AIPerf nhân với 200 token đầu ra yêu cầu. Không chia mọi request hoàn tất cho 120: request có thể kết thúc trong warmup hoặc grace, còn goodput chỉ đếm request đạt giới hạn dịch vụ.
- Độ dài token yêu cầu là cấu hình client; token hóa lại đầu vào và ID/lượng token thực sinh chưa được lưu đầy đủ. Prompt serving tổng hợp không phải bộ dữ liệu chất lượng của ban tổ chức. Độ chính xác toàn tập vẫn UNKNOWN.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Serving dùng request tổng hợp 4.000/200 token với lịch warmup/profiling/grace 60/120/30 giây.
- **Giả thuyết:** Workload và cửa sổ tính điểm cố định cho phép so sánh hữu ích khi protocol và cấu hình khớp nhau.
- **Kết luận được hỗ trợ:** Kết quả mô tả hiệu năng serving theo workload này; nó không chứng nhận độ chính xác và không thể thay bằng phép chia tổng request hoàn tất.
- **Chưa biết / giới hạn:** ID/lượng token thực từng request và điểm toàn tập chính thức chưa được xác lập.

### Lời nói mẫu

Bài serving dùng prompt tổng hợp, yêu cầu 4.000 token vào và 200 token ra. Client benchmark duy trì số request đang chạy, làm nóng hệ thống, chấm một cửa sổ cố định 120 giây rồi cho request còn lại hoàn tất. Goodput chỉ đếm request đạt cả hai giới hạn độ trễ; nhân với 200 ra token đầu ra tốt mỗi giây. Bài này không kiểm tra bộ chất lượng toàn tập của ban tổ chức; yêu cầu 99% vẫn chưa biết.

### Điều không nên nói

Không chia mọi request hoàn tất cho 120, tính grace vào cửa sổ chấm, suy ra token thực từ độ dài yêu cầu, hay nói đã đạt độ chính xác.

### Câu chuyển slide

Tiếp theo, so sánh các lần chạy chunk bằng cùng protocol chấm điểm đầy đủ.

---

<a id="slide-30"></a>

## Slide 30 — Appendix · larger prefill chunks did not help

### Nói nhanh · 10–20 giây

Tăng số token xử lý trong mỗi phần prompt không giúp nhanh hơn: thông lượng đạt chuẩn giảm từ khoảng 3.045 xuống 3.021 token mỗi giây, đồng thời phần request chậm token đầu xấu hơn. Mỗi cài đặt mới đo một lần, nên nhóm giữ chunk 8.192 token cho cấu hình này.

![Slide 30](../../submission-review/ai-journey-update-20261030/slides/assets/slide-30.png)

### Slide muốn nói gì

Cho thấy chunk prefill lớn hơn qua kiểm tra nhóm trên cluster được giao nhưng làm giảm goodput và xấu đuôi TTFT trong phép so sánh có giới hạn này.

### Giải thích kết quả và lập luận

Mỗi hàng là một lần chạy N64 đầy đủ; so cùng cột điểm và độ trễ giữa các chunk. Kích thước chunk là lượng công việc đầu vào xử lý cùng nhau, không phải concurrency client. Token đầu ra tốt/giây là tốc độ dịch vụ đủ điều kiện; SLA chung là tỷ lệ request đạt đồng thời hai giới hạn; p95 TTFT mô tả nhóm request chậm. Khi chunk tăng 8.192 → 10.240 → 12.288, goodput giảm còn p95 TTFT tăng. Mỗi cấu hình chỉ có một lần chạy, nên đây là cơ sở giữ 8.192 cho cấu hình này, không phải tối ưu phổ quát.

### Thuật ngữ và ký hiệu cần hiểu

- **chunk prefill:** Số token prompt được xử lý cùng nhau trong một đơn vị lập lịch prefill; khác với concurrency client.
- **SLA / p95 / TTFT:** SLA là tỷ lệ request đạt cả hai giới hạn độ trễ. p95 là phân vị 95. TTFT là thời gian từ lúc bắt đầu request đến token đầu tiên.
- **đánh giá local:** Ở đây “local” nghĩa là nhóm chạy và xem xét kết quả trên cluster được giao. Không có nghĩa chạy trên laptop hay được ban tổ chức duyệt.
- **kiểm tra chấp nhận:** Các kiểm tra protocol, runtime, độ trễ và đầu ra của nhóm. Qua chúng xác lập kết quả nội bộ hợp lệ, không phải chấp nhận chính thức hay cải thiện hữu ích.
- **arm:** Một cấu hình được thử; ở đây mỗi mức chunk là một arm. Mỗi arm chỉ có một lần chạy đầy đủ.
- **seed 2026:** Seed workload đã cấu hình. Seed do engine tạo vẫn khác nhau giữa các lần khởi chạy.

### Cách diễn giải số liệu hoặc sơ đồ

- Ở chunk 8.192, job 26766 ghi nhận 3,045.501509 token tốt/giây, SLA chung 98.580%, p95 TTFT 1,311.69 ms. Với 10.240, job 26768 đạt 3,034.088251, 98.524% và 1,518.87 ms.
- Với 12.288, job 26770 đạt 3,020.943099, 98.310% và 1,624.12 ms. Cả ba là lần N64 đầy đủ 60/120/30, yêu cầu 4.000/200 token, cùng mô hình/runtime và prefix lạnh; mỗi mức chunk chỉ đo một lần.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Goodput giảm và p95 TTFT tăng liên tục qua ba kích thước chunk được quan sát.
- **Giả thuyết:** Chunk lớn hơn có thể tăng thông lượng nhờ xử lý nhiều token prompt hơn trong một batch.
- **Kết luận được hỗ trợ:** Giữ chunk 8.192 cho cấu hình dịch vụ này; các chunk lớn hơn đã thử không cải thiện mục tiêu.
- **Chưa biết / giới hạn:** Mỗi cấu hình một lần nên thứ tự và seed engine có thể góp phần; đây không phải bằng chứng tối ưu toàn cục.

### Lời nói mẫu

Cả ba phép thử dùng cùng protocol đầy đủ với 64 request đồng thời. Chunk prompt 8.192 token đạt khoảng 3.045 token tốt mỗi giây; chunk lớn hơn đạt khoảng 3.034 và 3.021. Kiểm tra của nhóm trên cluster được giao đều qua, nhưng điều đó chỉ xác lập kết quả nội bộ đã xem xét, không phải duyệt của ban tổ chức hay cải thiện. Chunk lớn cũng làm đuôi token đầu chậm hơn. Mỗi mức chỉ có một lần chạy, nên giữ 8.192 cho dịch vụ này, không gọi là tốt nhất phổ quát.

### Điều không nên nói

Local ở đây là bằng chứng được nhóm xem xét trên cluster được giao, không phải phê duyệt của ban tổ chức. Không coi một arm qua kiểm tra là cải thiện hay tối ưu toàn cục.

### Câu chuyển slide

Slide sau tách một lần chạy serving GPU hoàn tất khỏi hậu xử lý bằng reader kết quả.

---

<a id="slide-31"></a>

## Slide 31 — A real replay can invalidate a static deployment claim

### Nói nhanh · 10–20 giây

Hai job GPU đã chạy xong benchmark nhưng lỗi chương trình đọc kết quả. Sửa chương trình giúp đọc lại điểm khoảng 3.055 token đạt chuẩn mỗi giây từ dữ liệu đã lưu. Job gốc vẫn thất bại; kiểm tra lại trên CPU chưa thay thế việc chạy toàn bộ triển khai sau sửa.

![Slide 31](../../submission-review/ai-journey-update-20261030/slides/assets/slide-31.png)

### Slide muốn nói gì

Giải thích rằng client serving đã hoàn tất, nhưng mỗi job toàn allocation ban đầu vẫn kết thúc FAILED ở khâu reader kết quả; kiểm tra CPU sau đó không chạy lại serving.

### Giải thích kết quả và lập luận

Theo dõi chuỗi theo từng bước. Kiểm tra tĩnh và giả lập chỉ dùng ví dụ chuẩn bị sẵn nên không mô phỏng thư mục export thật của AIPerf. Trong job 27136, cả hai đường prefill/decode ngữ nghĩa và client GPU hoàn tất, rồi reader lỗi vì đường dẫn export lồng thư mục. Job 27145 cũng chạy xong client, nhưng phần tổng hợp lỗi vì hai bí danh cùng thư mục home bị so sánh như hai chuỗi khác nhau. Job 27152 chạy reader đã sửa trên CPU với cả hai bộ dữ liệu thật. Nó chỉ xác minh hậu xử lý; trạng thái cuối của job GPU gốc vẫn là FAILED.

### Thuật ngữ và ký hiệu cần hiểu

- **portable replay:** Chạy triển khai đóng gói và client trên môi trường đích riêng, gồm filesystem và đường dẫn kết quả thật.
- **reader / hậu xử lý:** Mã tìm export client, ghép với metadata và tính báo cáo sau serving. Reader có thể lỗi sau khi GPU serving đã hoàn tất.
- **đường dẫn canonical và dạng chữ:** Canonical phân giải liên kết/bí danh về một vị trí filesystem; dạng chữ là chuỗi đường dẫn ghi nguyên. Hai chuỗi có thể khác nhưng cùng chỉ một thư mục.
- **phát lại toàn allocation:** Job đầy đủ gồm triển khai GPU, client và xử lý kết quả trên allocation được cấp. Kiểm tra reader chỉ chạy CPU không phải lần này.
- **scheduler FAILED:** Trạng thái job cuối cùng của scheduler vẫn là thất bại, dù số đo raw có thể được khôi phục và đọc về sau.
- **điểm raw khôi phục:** Chỉ số đọc được từ đầu ra còn lưu của job thất bại. Nó không đổi job thành triển khai thành công.
- **compute-only:** Job CPU không GPU, dùng ở đây để kiểm reader trên bộ dữ liệu thật đã lưu; nó không khởi chạy Qwen hay gửi request serving.

### Cách diễn giải số liệu hoặc sơ đồ

- Bản sửa đầu nhận diện export trong thư mục con trực tiếp. Bản sửa thứ hai chuẩn hóa /scratch/home và /home về cùng gốc đầu vào trước khi so sánh. Đây là lỗi reader thật sau khi client hoàn tất, không phải suy giảm serving đã đo.
- Điểm raw khôi phục của 27145 là 3,055.330517 token đầu ra tốt/giây. Có thể xem đây là số liệu hiệu năng raw, nhưng job scheduler không hoàn tất thành công toàn bộ triển khai trên allocation và chưa chạy lại toàn GPU allocation sau sửa.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Hai job GPU thật chạy xong client và các đường ngữ nghĩa nhưng lỗi khi đọc kết quả; job không GPU 27152 qua cả hai reader đã sửa trên hai bộ dữ liệu lưu lại.
- **Giả thuyết:** Lỗi xử lý đường dẫn gây ra trạng thái lỗi sau khi client hoàn tất.
- **Kết luận được hỗ trợ:** Reader đã sửa được xác minh với đầu ra thật; trạng thái scheduler của 27136/27145 vẫn FAILED.
- **Chưa biết / giới hạn:** Chưa chạy lại triển khai end-to-end với reader đã sửa trên toàn bộ GPU allocation.

### Lời nói mẫu

Job GPU portable đầu tiên xử lý xong prompt, sinh token và chạy xong client, rồi lỗi vì reader tìm nhầm thư mục export. Job tiếp theo cũng hoàn tất serving, nhưng phần tổng hợp coi hai tên của cùng thư mục home là hai đường dẫn khác nhau. Một job CPU về sau kiểm tra reader đã sửa trên cả hai bộ dữ liệu thật. Job GPU ban đầu vẫn thất bại; nhóm không chạy lại toàn allocation sau sửa.

### Điều không nên nói

Không đổi bản ghi scheduler FAILED thành thành công, không gọi kiểm reader CPU là phát lại GPU, và không trình bày 3,055.330517 như lần chạy toàn allocation thành công sau sửa.

### Câu chuyển slide

Slide cuối tách phát hiện được giữ lại khỏi công việc xác minh còn là đề xuất hoặc chưa biết.

---

<a id="slide-32"></a>

## Slide 32 — What the evidence supports next

### Nói nhanh · 10–20 giây

Nhóm giữ cấu hình 64 request đồng thời có kết quả đã chạy lại, thay vì chọn một đỉnh đơn lẻ. Hai việc còn thiếu là chấm chất lượng chính thức và chạy lại toàn bộ bản triển khai đóng gói sau sửa chương trình đọc. Đây là đề xuất kiểm chứng, chưa phải kết quả mới.

![Slide 32](../../submission-review/ai-journey-update-20261030/slides/assets/slide-32.png)

### Slide muốn nói gì

Tóm tắt kết luận mà bằng chứng hiện có hỗ trợ và nói rõ các kiểm tra tiếp theo là đề xuất, chưa phải lần chạy đã hoàn tất.

### Giải thích kết quả và lập luận

Ba ý tạo thành chuỗi quyết định theo bằng chứng: giữ dịch vụ target-only N64 đã lặp lại; yêu cầu bằng chứng kích hoạt, truyền KV và đầu ra cho mọi đường mới; sau đó mới hoàn tất kiểm tra độc lập. Kết quả graph thưa không đổi lựa chọn vì tiết kiệm bộ nhớ nhưng không tăng goodput. Các kiểm tra còn thiếu là độ chính xác toàn tập chính thức và phát lại portable toàn allocation sau sửa reader. Không ý nào được trình bày như công việc đã lên lịch.

### Thuật ngữ và ký hiệu cần hiểu

- **target-only / EAGLE:** Target-only chỉ phục vụ mô hình chính. EAGLE đề xuất token draft để mô hình chính xác minh; cấu hình nông đầy đủ đã thử làm giảm hiệu năng.
- **xác minh độc lập:** Kiểm tra riêng độ chính xác toàn tập chính thức hoặc triển khai đầy đủ, vượt ra ngoài điểm serving và fixture helper.
- **chọn cấu hình:** Quyết định dùng nó làm cấu hình nộp bài/triển khai sau khi xem xét bằng chứng. Một điểm cao đơn lẻ không đủ.
- **bằng chứng mã nguồn hoặc CPU:** Mã nguồn cho biết code có thể hỗ trợ gì; fixture CPU thử hành vi helper hẹp. Cả hai không chứng minh service GPU đã kích hoạt đường đó và cho đầu ra đúng.
- **chưa biết:** Không có phép đo lưu lại đủ để kết luận. Không được mô tả như bằng không, đã qua hoặc khỏe mạnh.
- **độ chính xác chính thức:** Đánh giá chất lượng toàn tập của ban tổ chức; cần đạt ít nhất 99% tham chiếu FP8 và hiện chưa được xác minh.

### Cách diễn giải số liệu hoặc sơ đồ

- Giữ cấu hình target-only N64 đã lặp lại thay vì điểm cao riêng lẻ. Thay đổi cache, cap và polling chưa có lợi ích hữu ích; cấu hình EAGLE đầy đủ với bước dự đoán nông bị giảm hiệu năng; goodput graph thưa thấp hơn đối chứng trước 0.370208%.
- Triển khai mới cần chứng minh backend dự định thực sự chạy, KV được chuyển đúng và đầu ra hợp lệ trước khi diễn giải điểm. Fixture CPU hoặc đọc mã nguồn riêng lẻ không đáp ứng tiêu chuẩn đó.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Dịch vụ N64 được chọn có bằng chứng nhiều lần chạy đầy đủ; vài thử nghiệm tối ưu không cho lợi ích. Độ chính xác và phát lại portable sau sửa vẫn còn mở.
- **Giả thuyết:** Kiểm tra runtime và đầu ra riêng cho từng đường giúp tránh khẳng định triển khai thiếu căn cứ.
- **Kết luận được hỗ trợ:** Giữ dịch vụ đã tái lập; xem xác minh liệt kê là việc tương lai, không phải nghiên cứu đã làm hay đang xếp hàng.
- **Chưa biết / giới hạn:** Độ chính xác chính thức, hành vi triển khai đầy đủ sau sửa reader, và đường compile RoPE/KV tương thích vẫn chưa biết.

### Lời nói mẫu

Giữ cấu hình đã lặp lại, chỉ phục vụ mô hình đích ở tải 64 request đồng thời; một điểm cao đơn lẻ chưa đủ để thay thế. Với phương pháp mới, trước hết phải chứng minh backend đã chạy, trạng thái attention được truyền đúng và câu trả lời qua kiểm tra. Hai việc còn mở là bài accuracy toàn tập của ban tổ chức và phát lại GPU portable đầy đủ sau sửa reader. Đó là bước xác minh đề xuất, chưa phải việc đã lên lịch hay hoàn tất.

### Điều không nên nói

Không khẳng định đã đạt độ chính xác chính thức, đã phát lại serving portable đầy đủ sau sửa, graph thưa tăng goodput, hay giao diện compile đã được sửa.

### Câu chuyển slide

Dừng tại đây. Khi trả lời, tách quan sát đo được, kết luận có căn cứ và điều còn chưa biết.

---

<a id="slide-33"></a>

## Slide 33 — The task: same 65-million-cell airflow calculation

### Nói nhanh · 10–20 giây

Bài toán được giữ cố định với 65,3 triệu ô lưới, bốn nút và 512 MPI rank. Chúng tôi chạy đủ 150 bước bộ giải, trong đó 149 bước được tính giờ. Chỉ số là số giây trung bình mỗi bước; thấp hơn là tốt hơn.

![Slide 33](transcript-assets/slide-33.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Xác định khối lượng tính toán CPU cố định và đại lượng hiệu năng cần tối ưu. Phép so sánh giữ nguyên bài toán được quy định, rồi xem cụm máy thực hiện nó hiệu quả đến đâu.

### Giải thích kết quả và lập luận

Các con số xác định khối lượng công việc cố định: 65.334.765 ô lưới được chia trên bốn nút và 512 MPI rank, tức 128 rank mỗi nút. MPI rank là một tiến trình phần mềm, không đồng nghĩa với một lõi CPU vật lý. Phép tính quy định chạy 150 vòng lặp bộ giải; có 149 mẫu được tính giờ vì vòng đầu không nằm trong trung bình báo cáo. Đơn vị là giây thời gian thực trên mỗi bước bộ giải; số nhỏ hơn nghĩa là mỗi vòng lặp mất ít thời gian hơn. Slide định nghĩa công việc và chỉ số, chưa báo cáo kết quả tối ưu.

### Thuật ngữ và ký hiệu cần hiểu

- **65,3 triệu:** Số làm tròn từ lưới chính xác gồm 65.334.765 ô.
- **MPI rank:** Một tiến trình bộ giải phân tán; 512 rank tổng cộng tương ứng 128 rank mỗi nút.
- **s/step:** Giây thời gian thực trên mỗi vòng lặp bộ giải, không phải giây thời gian lái xe mô phỏng.
- **lõi CPU vật lý:** Một lõi thực thi phần cứng. MPI rank là tiến trình phần mềm; rank có thể được gắn với lõi, nhưng cần xác minh ánh xạ thay vì mặc định là một-một.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

So sánh hợp lệ phải giữ mọi bước chuẩn bị và đủ 150 bước bộ giải. Phân rã gán ô lưới cho rank; CPU affinity gán rank vào CPU. Đây là hai lựa chọn riêng và cả hai đều có thể ảnh hưởng thời gian chạy.

![Slide 34](transcript-assets/slide-34.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Giải thích vì sao chỉ số hiệu năng chỉ có ý nghĩa khi giữ nguyên toàn bộ quy trình bắt buộc, đồng thời phân biệt phân rã lưới với gán tiến trình vào CPU.

### Giải thích kết quả và lập luận

Trình tự này là một phần của công việc được đo: decomposePar gán ô lưới cho MPI rank; renumberMesh đổi thứ tự dữ liệu ô cục bộ; potentialFoam khởi tạo trường dòng chảy; applyBoundaryLayer áp dụng điều kiện lớp biên bắt buộc; sau đó simpleFoam thực hiện đủ 150 bước. Phân rã quyết định tiến trình sở hữu ô nào, từ đó quyết định trao đổi dữ liệu qua ranh giới tiến trình. CPU affinity quyết định rank chạy ở đâu. Affinity có thể ảnh hưởng việc rank truy cập lõi CPU và bộ nhớ gần nó, nhưng không đổi các ô mà rank sở hữu. Hai quyết định đều có thể ảnh hưởng hiệu năng và không nên nhầm lẫn.

### Thuật ngữ và ký hiệu cần hiểu

- **MPI:** Message Passing Interface; các rank riêng biệt trao đổi dữ liệu, đặc biệt ở ranh giới phân vùng.
- **decomposePar:** Tiện ích OpenFOAM chia ô lưới cho các rank.
- **CPU affinity:** Gắn tiến trình hoặc rank với tài nguyên CPU; khác với việc gán ô lưới.
- **trao đổi ô lân cận:** Các rank trao đổi giá trị trường cho ô nằm hai phía ranh giới phân vùng; nhiều cạnh bị cắt chỉ là proxy cho lượng và chi phí lưu lượng này.

### Cách diễn giải số liệu hoặc sơ đồ

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

Slide chỉ cho trình tự, không cho thời gian từng giai đoạn và cũng không xác nhận affinity đã được đo hay tối ưu trong một kết quả cụ thể.

### Câu chuyển slide

Khi khối lượng và quy trình đã cố định, slide tiếp theo kiểm tra liệu graph cut, một chỉ số đại diện cho biên phân vùng, có dự báo được thời gian bộ giải hay không.

---

<a id="slide-35"></a>

## Slide 35 — A smaller partition cut did not make the solver faster

### Nói nhanh · 10–20 giây

Phân vùng NUMA giảm proxy graph cut 10,63%, nhưng thời gian bộ giải trung bình xấu đi 3,4416%, từ 13,881 lên 14,359 giây mỗi bước. Chỉ số đại diện này không dự báo được runtime; phép đo cũng chưa xác định nguyên nhân khiến lần chạy chậm hơn.

![Slide 35](transcript-assets/slide-35.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Trình bày giả thuyết NUMA về tính cục bộ không thành công và giải thích vì sao chỉ số đại diện của đồ thị phân vùng không thể thay phép đo thời gian chạy.

### Giải thích kết quả và lập luận

Mức −10,63% màu cam là mức giảm của proxy graph cut: ít kết nối lưới có trọng số hơn đi qua ranh giới cục bộ đã chọn. Điều đó không có nghĩa thời gian trao đổi dữ liệu giảm 10,63%. Trao đổi thực tế còn phụ thuộc kích thước và tần suất thông điệp, mạng và hoạt động MPI; thời gian bộ giải cũng gồm tính toán, đồng bộ, truy cập bộ nhớ và công việc khác. Trung bình đo được lại xấu đi, từ 13,881 lên 14,359 giây mỗi bước (+3,4416%, chậm hơn). Vì vậy, proxy tốt hơn không tạo ra cải thiện runtime trong phép so sánh này. Nguyên nhân còn bỏ ngỏ vì chưa đo MPI wait, băng thông, tần số CPU, công suất và vị trí trang bộ nhớ.

### Thuật ngữ và ký hiệu cần hiểu

- **NUMA:** Truy cập bộ nhớ không đồng nhất: chi phí truy cập có thể phụ thuộc socket CPU hoặc vùng cục bộ sở hữu bộ nhớ.
- **graph cut:** Chỉ số proxy về số hoặc trọng số kết nối phân vùng đi qua ranh giới được chọn; không đo trực tiếp thời gian trao đổi.
- **−10,63%:** Proxy graph cut giảm 10,63% ở cấu hình này.
- **+3,4416%:** Thời gian trung bình bộ giải tăng, tức chậm hơn 3,4416% trong quan sát so sánh.
- **graph cut của phân vùng:** Tổng có trọng số của các kết nối ô lưới lân cận bị chia giữa các phân vùng. Nó ước lượng lưu lượng giao diện tiềm năng, nhưng không đo byte đã truyền, MPI wait, thời gian mạng hay runtime tổng thể.
- **tính cục bộ NUMA:** Trên máy nhiều socket, lõi CPU thường truy cập bộ nhớ gắn với socket của nó trực tiếp hơn bộ nhớ thuộc socket khác; cách đặt tiến trình vì vậy có thể ảnh hưởng độ trễ và băng thông.
- **MPI wait:** Thời gian một tiến trình phải chờ tiến trình khác hoặc trao đổi dữ liệu hoàn tất; slide ghi nhận đại lượng này chưa được đo.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

Phương pháp dẫn đầu thay đổi theo cấp phát: Hierarchical thấp hơn ở một và hai nút, còn Scotch thấp hơn ở bốn nút. Vì độ dài lần chạy và cấp phát khác nhau, đây là các quan sát mô tả, không phải kết quả mở rộng nhân quả.

![Slide 36](transcript-assets/slide-36.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

So sánh thời gian trung bình quan sát được của Scotch và hierarchical trên các cấp phát một, hai và bốn nút, đồng thời giới hạn kết luận vì điểm kết thúc công việc và cấp phát khác nhau.

### Giải thích kết quả và lập luận

Nhãn Scotch màu cam và Hierarchical xanh đậm cho biết hai phương pháp phân rã; mọi giá trị là thời gian trung bình tính bằng giây mỗi bước bộ giải, nên thấp hơn là nhanh hơn. Hierarchical thấp hơn trong quan sát một nút (14,366 so với 14,451) và hai nút (7,170 so với 7,463); Scotch thấp hơn ở bốn nút (3,678 so với 3,820). Đây không phải các điểm của một đường cong mở rộng có kiểm soát: mỗi điểm dùng một cấp phát riêng, còn điểm kết thúc bắt buộc thay đổi từ 40 lên 80 rồi 150 bước. Vì vậy, số nút, độ dài lần chạy, điều kiện cấp phát và cấu hình cùng thay đổi. Các thanh mô tả quan sát; chúng không tách riêng được số nút là nguyên nhân đổi thứ hạng.

### Thuật ngữ và ký hiệu cần hiểu

- **Scotch:** Phương pháp phân rã lưới dựa trên đồ thị trong quy trình OpenFOAM.
- **Hierarchical:** Phương pháp phân rã lưới chia không gian theo cấu trúc phân cấp.
- **s/step:** Số giây thời gian thực trung bình trên mỗi vòng lặp bộ giải được tính giờ; thấp hơn là tốt hơn.
- **so sánh mô tả:** Báo cáo các giá trị đã quan sát. Vì số nút, điểm kết thúc bước và cấp phát cùng thay đổi, phép so sánh không tách riêng ảnh hưởng của một yếu tố.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

Trên bốn nút, Hierarchical có trung bình thấp hơn ở 64 và 96 rank mỗi nút; Scotch thấp hơn ở 128. Giá trị 3,678 giây mỗi bước của Scotch-128 là trung bình thấp nhất đã xem xét, nhưng vẫn là quan sát ứng viên cần xác nhận.

![Slide 37](transcript-assets/slide-37.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Cho thấy thứ hạng phân rã trên bốn nút thay đổi theo mật độ tiến trình và xác định giá trị trung bình thấp nhất đã được xem xét, nhưng không nâng nó thành tối ưu phổ quát.

### Giải thích kết quả và lập luận

Trên bốn nút, các thanh so sánh số giây trung bình mỗi bước tại 64, 96 và 128 MPI rank mỗi nút. Màu cam là Scotch, xanh đậm là Hierarchical. Hierarchical có trung bình thấp hơn ở 64 rank (4,489 so với 10,310) và 96 rank (4,922 so với 7,146); Scotch thấp hơn một chút ở 128 rank (3,678 so với 3,820). Trên bốn nút, các cấu hình này lần lượt dùng 256, 384 và 512 rank, nhưng rank là tiến trình, không mặc nhiên tương ứng với một lõi vật lý. Quan sát Scotch-128 có trung bình thấp nhất trong sáu log đã xem xét. Cấp phát riêng và số CPU yêu cầu khác nhau làm nhiễu phép so sánh; đây là ứng viên cần chạy lặp, không chứng minh mật độ rank hay phương pháp riêng lẻ gây ra chênh lệch.

### Thuật ngữ và ký hiệu cần hiểu

- **ranks per node:** Số tiến trình MPI đặt trên mỗi nút; trên bốn nút, các cấu hình hiển thị tương ứng 256, 384 và 512 rank.
- **s/step:** Số giây thời gian thực trung bình được đo trên mỗi bước bộ giải.
- **lowest reviewed mean:** Trung bình nhỏ nhất trong nhóm quan sát đã xem xét, không phải bằng chứng tối ưu toàn cục.
- **mật độ rank:** Số tiến trình MPI được gán cho mỗi nút. Khái niệm này khác số lõi vật lý và tự nó không chứng minh tiến trình được gắn CPU hay dùng lõi độc quyền.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

Phần lớn bước mất khoảng 3,3 đến 3,8 giây, nhưng một bước lên tới 35,884 giây. Chúng tôi giữ cả 149 mẫu trong trung bình số học; đột biến có trong lần chạy này, còn nguyên nhân vẫn chưa rõ.

![Slide 38](transcript-assets/slide-38.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Giải thích vì sao mọi vòng lặp được tính giờ, kể cả bước chậm cực độ, vẫn nằm trong trung bình số học kiểu chính thức; đồng thời phân biệt quan sát với chẩn đoán nguyên nhân.

### Giải thích kết quả và lập luận

Đây là các thống kê phân bố của 149 bước được tính giờ: trung vị 3,298742 giây, phân vị thứ 95 là 3,795740 giây, và cực đại 35,883552 giây tại solver Time 119. Trung vị là quan sát ở giữa; p95 là mốc mà khoảng 95% quan sát nằm tại hoặc thấp hơn. Trung bình số học khác với hai đại lượng đó: cộng mọi mẫu rồi chia cho 149, nên bước 35,9 giây vẫn được giữ và kéo trung bình lên. Giữ mẫu này phản ánh lần chạy thực tế thay vì che đi một sự kiện chậm. Vạch cam và đỏ phân biệt thời gian điển hình với cực đại; con số in sẵn cho biết đơn vị chính xác. Đột biến được nhìn thấy, nhưng chỉ các thời gian này không xác định được nguyên nhân.

### Thuật ngữ và ký hiệu cần hiểu

- **median:** Giá trị ở giữa sau khi sắp xếp 149 mẫu tính giờ.
- **95th percentile (p95):** Giá trị mà xấp xỉ 95% mẫu nằm tại hoặc dưới đó, theo quy ước phân vị sử dụng.
- **maximum:** Mẫu lớn nhất được ghi nhận; ở đây là 35,883552 giây tại solver Time 119.
- **Time 119:** Chỉ số thời gian/vòng lặp bộ giải được báo cáo, không phải 119 giây thời gian thực.
- **trung bình số học:** Tổng mọi giá trị thời gian chia cho số lượng giá trị. Khác trung vị, một mẫu rất lớn có thể làm trung bình tăng đáng kể.
- **phần đuôi:** Phần chậm nhất của phân bố thời gian; p95 tóm tắt phân vị cao, còn cực đại là mẫu chậm nhất duy nhất.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

Scotch với 128 tiến trình mỗi nút đạt khoảng 3,678 giây mỗi bước. Tuy nhiên, tại thời điểm ghi trên slide ngày 23 tháng 10, job chạy lại vẫn đang chờ tài nguyên, chưa có kết quả. Vì vậy đây là ứng viên cần xác nhận, chưa phải điểm chính thức.

![Slide 39](transcript-assets/slide-39.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Phân biệt thời gian ứng viên đã được xem xét với kết quả chính thức được chấp nhận, đồng thời liệt kê bằng chứng cần có từ lần xác nhận độc lập.

### Giải thích kết quả và lập luận

Bên trái là quan sát ứng viên đã được xem xét: Scotch-128 đạt trung bình 3,677906731 giây mỗi bước trên 149 mẫu. Bên phải là trạng thái bằng chứng khác: job 25940700 được ghi đang chờ trong Q/q5 lúc 15:06 UTC vì thiếu tài nguyên node_pool, chưa có kết quả. Gói 54 tệp đóng băng là bộ đầu vào cố định, không thay đổi; hash và dấu kiểm tra xác nhận nguồn, lưới và đầu ra trùng với các tệp đã ghi nhận. Provenance là hồ sơ cho biết đầu vào, lệnh, tài nguyên và đầu ra nào tạo nên lần chạy. Danh sách còn yêu cầu mã trả về thành công ở mọi giai đoạn và bằng chứng thực sự cấp phát 512 lõi CPU vật lý trên bốn máy. Đây là yêu cầu xác nhận, chưa phải các kiểm tra đã đạt.

### Thuật ngữ và ký hiệu cần hiểu

- **Q/q5:** Nhãn hàng đợi/trạng thái bộ lập lịch trong quan sát đã ghi; slide nói job đang chờ, không phải đang chạy.
- **Scotch-128:** Phân rã Scotch với 128 MPI rank mỗi nút trên bốn nút.
- **seal:** Bằng chứng ghi nhận danh tính/tính toàn vẹn của tệp nguồn, lưới hoặc đầu ra; đây là kiểm tra yêu cầu, chưa phải kiểm tra đã hoàn tất.
- **gói đầu vào đóng băng:** Tập hợp tệp đầu vào có phiên bản, được giữ nguyên khi chạy lặp để các phép so sánh dùng cùng bộ đầu vào đã khai báo.
- **hash / dấu kiểm tra:** Giá trị băm mật mã hoặc hồ sơ toàn vẹn dùng kiểm tra tệp có trùng từng byte với phiên bản đã ghi nhận hay không; đây là bằng chứng cần xác minh, không phải kết quả hiệu năng.
- **provenance:** Hồ sơ truy xuất gồm danh tính đầu vào, phần mềm/mã nguồn, lệnh chạy, tài nguyên được cấp và đầu ra tạo ra.
- **bằng chứng kết thúc từ bộ lập lịch:** Bản ghi của bộ lập lịch cho thấy trạng thái cuối xác định như hoàn tất hoặc thất bại, thay vì chỉ đang chờ hay đang chạy.
- **mã trả về:** Trạng thái thoát của chương trình; kiểm tra từng giai đoạn giúp xác nhận mọi lệnh bắt buộc hoàn tất thành công.

### Cách diễn giải số liệu hoặc sơ đồ

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

### Nói nhanh · 10–20 giây

Nhóm chọn ứng viên theo thời gian thực chạy, giữ cả bước chậm và yêu cầu chạy lại để xác nhận. Ứng viên thấp nhất khoảng 3,678 giây mỗi bước; ngày 23 tháng 10 lần xác nhận vẫn chưa có kết quả. Bài học là điểm nhanh cần đi cùng bằng chứng đủ.

![Slide 40](transcript-assets/slide-40.png)

**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**

### Slide muốn nói gì

Khép lại phần HPC bằng bốn nguyên tắc đo lường và điểm quyết định tiếp theo: xem xét bằng chứng xác nhận đầy đủ trước khi chọn cấu hình khác.

### Giải thích kết quả và lập luận

Bốn nguyên tắc nối phép đo đáng tin cậy với bằng chứng có thể tái lập: tính cả khâu chuẩn bị và toàn bộ lời giải; đánh giá runtime thay vì proxy graph cut; giữ mọi mẫu, kể cả sự kiện chậm ở phần đuôi; và chạy lặp độc lập. Dòng trạng thái là ảnh chụp lịch sử: ngày 23 October lúc 15:06 UTC, job 25940700 vẫn chờ tài nguyên node_pool và chưa có kết quả. Truy vấn bộ lập lịch hoặc hồ sơ kết thúc chứng minh job có chạy hay không và kết thúc thế nào; bản thân chúng không chứng minh đầu vào đúng hoặc phép đo hợp lệ. Hash, mã trả về từng giai đoạn, bằng chứng bố trí tài nguyên và provenance đầu ra đầy đủ giải quyết các câu hỏi riêng đó. Hành động kế tiếp ghi trên slide là xem bằng chứng kết thúc và phần đuôi thời gian của lần xác nhận, rồi lấy mẫu phần cứng có giới hạn để nghiên cứu độ ổn định. Không khẳng định kết quả nào xảy ra sau đó.

### Thuật ngữ và ký hiệu cần hiểu

- **terminal proof:** Bằng chứng job đã tới trạng thái kết thúc xác định trong bộ lập lịch, đi cùng đầu ra đầy đủ và mã trả về.
- **bounded hardware samples:** Các mẫu đo phần cứng có phạm vi và giới hạn được hoạch định, không phải phiên profiling không giới hạn.
- **Q/q5:** Hàng đợi/trạng thái trong ảnh chụp đã ghi, không phải truy vấn hiện tại.
- **lấy mẫu phần cứng có giới hạn:** Một tập nhỏ phép đo phần cứng được hoạch định trước cho khoảng thời gian hoặc giai đoạn xác định, với phạm vi giới hạn để không làm thay đổi đáng kể khối lượng công việc.

### Cách diễn giải số liệu hoặc sơ đồ

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
