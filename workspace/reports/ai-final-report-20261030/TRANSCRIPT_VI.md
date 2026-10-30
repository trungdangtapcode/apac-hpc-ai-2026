# Transcript và hướng dẫn hiểu từng slide — Tiếng Việt

Đây là **lời thuyết trình mẫu và tài liệu học**, không phải bản chép lại một buổi nói đã diễn ra. Tài liệu đi theo đúng 40 slide của bản trình chiếu hiện tại. Bản tiếng Việt được tạo theo yêu cầu riêng của bạn; mã nguồn và các báo cáo khác vẫn dùng tiếng Anh.

**Cách dùng:** mỗi slide mở đầu bằng **“Nói nhanh · 10–20 giây”**, có thể nói ngay: ý chính, số liệu nổi bật và ý nghĩa của chúng. Các từ cần thiết được giải thích ngay trong đoạn ngắn, ví dụ “repeated” là chạy lại benchmark để kiểm tra kết quả có tái lập. Thời lượng là mục tiêu để luyện, không phải bản ghi đã bấm giờ. Khi cần hiểu sâu hoặc trả lời câu hỏi, đọc tiếp “Slide muốn nói gì”, phần lập luận, thuật ngữ và lời nói mẫu dài bên dưới.

- **Slide 1–20:** phần AI chính. Dùng [kế hoạch 15–20 phút](PRESENTATION_PLAN.md); không đọc hết mọi lời nói mẫu nếu vượt thời gian.
- **Slide 21–32:** phần AI dự phòng khi được hỏi. Phần chính đi theo bốn câu hỏi nghiên cứu; lịch sử chi tiết ở phần dự phòng.
- **Slide 33–40:** giải thích phần HPC đang có trong cùng deck, chỉ đọc và diễn giải. Trạng thái job trên các slide này là **ảnh chụp ngày 23/10**, không phải trạng thái trực tiếp ngày 30/10. Hướng dẫn này không cập nhật hay xác nhận kết quả HPC mới. Thời lượng AI không bao gồm mặc định phần HPC.
- Mỗi slide có nhãn **Phần cứng** ngay dưới tiêu đề. H200 là Firmus, H100 là NSCC ASPIRE 2A+; slide có cả hai hoặc có phép kiểm tra CPU sẽ ghi riêng. Nhãn “chung” chỉ quy tắc hoặc bố trí dùng trên cả hai hệ thống, không biến chúng thành một phép so hiệu năng cùng điều kiện.
- Màu sắc có ý nghĩa **theo từng slide**. Cam không luôn là “thắng” hay “thua”. Ảnh nền, gradient và đường trang trí cuối slide không biểu diễn dữ liệu.
- **↑ / ↓** thường là hướng mong muốn tối ưu, không khẳng định số liệu thực tế đã tăng/giảm. “Không có trục” nghĩa là sơ đồ/bảng/card, không cần tự suy ra trục X/Y.
- Nghiên cứu đã dừng theo yêu cầu. Các việc “tiếp theo” trong slide là đề xuất hoặc câu chuyện tại thời điểm đó, không phải job mới đã chạy.

Nguồn: [PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), [PDF](../../submission-review/ai-reasoning-update-20261030/TripleU_APAC2026_Presentation.pdf), [bản tiếng Anh](TRANSCRIPT_EN.md). SHA-256 của PowerPoint: `171fa7ce896ecbfc3708c1d15e5b603cb4bf80ee46a9c3a9f59af1ae0a1995d8`. Đây là transcript của phiên bản này; đổi deck thì cần kiểm tra lại hướng dẫn.

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

- [Slide 01 — How do we reason about a fast Qwen service?](#slide-01)
- [Slide 02 — Define success before choosing an optimisation](#slide-02)
- [Slide 03 — Which GPU layouts are feasible candidates?](#slide-03)
- [Slide 04 — Why keep two TP4 prefills and one TP8 decode?](#slide-04)
- [Slide 05 — Worker readiness did not prove a working service](#slide-05)
- [Slide 06 — What does the profile identify—and what does it not?](#slide-06)
- [Slide 07 — Why investigate descriptor setup before bandwidth?](#slide-07)
- [Slide 08 — Do attention and communication choices interact?](#slide-08)
- [Slide 09 — Does a decode change improve the service objective?](#slide-09)
- [Slide 10 — Where should we stop increasing concurrency?](#slide-10)
- [Slide 11 — Which requests still fail after goodput improves?](#slide-11)
- [Slide 12 — Keep an intervention only if the objective improves](#slide-12)
- [Slide 13 — Did speculative decoding solve this workload?](#slide-13)
- [Slide 14 — Does the improvement survive another deployment?](#slide-14)
- [Slide 15 — Why did a later replay score lower?](#slide-15)
- [Slide 16 — Can one platform predict another reliably?](#slide-16)
- [Slide 17 — What does passing latency leave unverified?](#slide-17)
- [Slide 18 — Does the packaged deployment complete end to end?](#slide-18)
- [Slide 19 — Four decisions, each with an evidence boundary](#slide-19)
- [Slide 20 — What should the next iteration establish?](#slide-20)
- [Slide 21 — Backup · two platforms, separate experimental systems](#slide-21)
- [Slide 22 — Backup · FP8 geometry constrains a topology](#slide-22)
- [Slide 23 — Backup · historical milestones behind the decisions](#slide-23)
- [Slide 24 — Backup · request-scoped descriptor construction](#slide-24)
- [Slide 25 — Backup · what the KV recovery run actually proves](#slide-25)
- [Slide 26 — Backup · H100: first-token gain, goodput loss](#slide-26)
- [Slide 27 — Backup · does a startup saving survive reversed order?](#slide-27)
- [Slide 28 — Backup · source-supported changes that did not win](#slide-28)
- [Slide 29 — Backup · scope limits of kernel and source evidence](#slide-29)
- [Slide 30 — Backup · the retained settings on each platform](#slide-30)
- [Slide 31 — Backup · workload control and prefill chunk trial](#slide-31)
- [Slide 32 — Backup · less graph memory did not raise goodput](#slide-32)
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

## Slide 01 — How do we reason about a fast Qwen service?

**Phần cứng: H200 + H100 — tổng quan bốn câu hỏi AI; H200 là hệ thống chính.**

### Nói nhanh · 10–20 giây

Nhóm trả lời bốn câu hỏi: chia 16 H 200 thế nào, dịch vụ bị hạn chế ở đâu, thay đổi nào tăng thông lượng đạt chuẩn và kết quả có tái lập không. Chúng tôi trình bày bằng chứng cho quyết định, cả giả thuyết thất bại và những điều chưa xác minh.

![Slide 01](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-01.png)

### Slide muốn nói gì

Mở bài bằng bốn câu hỏi nghiên cứu và cách suy luận để trả lời, thay vì kể lần lượt từng job.

### Giải thích kết quả và lập luận

Bốn câu hỏi là chia GPU thế nào, bằng chứng cho thấy hạn chế gì, thay đổi nào có ích và kết quả có bền vững không. Mỗi vòng đi từ vấn đề, quan sát, phân tích, giả thuyết, thay đổi và đo, đánh giá nguyên nhân đến quyết định.

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

Nhóm trả lời bốn câu hỏi: chia 16 H 200 thế nào, dịch vụ bị hạn chế ở đâu, thay đổi nào tăng thông lượng đạt chuẩn và kết quả có tái lập không. Chúng tôi trình bày bằng chứng cho quyết định, cả giả thuyết thất bại và những điều chưa xác minh.

### Điều không nên nói

Không gọi đây là chiến thắng, được ban tổ chức chấp nhận, hay đã chứng nhận accuracy. Ngày tháng giới hạn kết luận ở bản cập nhật này.

### Câu chuyển slide

Trước khi chọn phương án, cần xác định bài toán cố định và điều kiện thành công.

---

<a id="slide-02"></a>

## Slide 02 — Define success before choosing an optimisation

**Phần cứng: H200 · Firmus — bài toán 16 GPU; quy tắc độ trễ dùng chung.**

### Nói nhanh · 10–20 giây

Bài toán cố định là Qwen 3-235 B trên hai node, mỗi node tám H 200. Request có 4000 token vào và yêu cầu 200 token ra. Ít nhất 90% phải đạt cả hai ngưỡng chờ token đầu và khoảng token. Nhóm tối ưu thông lượng đạt chuẩn, không chỉ tổng token sinh ra.

![Slide 02](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-02.png)

### Slide muốn nói gì

Đặt model, giới hạn phần cứng, tải và điều kiện độ trễ trước khi so các cấu hình.

### Giải thích kết quả và lập luận

Qwen 3-235 B FP 8 chạy trong hai node, mỗi node tám H 200. Workload yêu cầu 4000 token vào và 200 token ra. Sinh nhiều token chỉ có ích nếu từng request đạt cả hai giới hạn độ trễ, đồng thời tỷ lệ đạt trên toàn bộ request không dưới 90%.

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

Bài toán cố định là Qwen 3-235 B trên hai node, mỗi node tám H 200. Request có 4000 token vào và yêu cầu 200 token ra. Ít nhất 90% phải đạt cả hai ngưỡng chờ token đầu và khoảng token. Nhóm tối ưu thông lượng đạt chuẩn, không chỉ tổng token sinh ra.

### Điều không nên nói

Không suy ra tỷ lệ đạt theo từng yêu cầu từ một giá trị trung bình tổng hợp. Không bỏ lỗi khỏi mẫu số và không thay 200 bằng độ dài đầu ra khác.

### Câu chuyển slide

Khi đã rõ điều kiện thành công, câu hỏi đầu tiên là cách chia GPU nào khả thi.

---

<a id="slide-03"></a>

## Slide 03 — Which GPU layouts are feasible candidates?

**Phần cứng: H200 · Firmus — chiến dịch topology.**

### Nói nhanh · 10–20 giây

Nhóm so các cách đánh đổi giữa số worker và số GPU cùng xử lý một model. Có 17 cấu hình đo được để làm bằng chứng. Bố trí được chọn đạt khoảng 1912 token đạt chuẩn mỗi giây ở 48 request đồng thời. Vì tải và lịch sử truyền khác nhau, chưa thể kết luận đây là topology tối ưu toàn cục.

![Slide 03](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-03.png)

### Slide muốn nói gì

Dùng chiến dịch topology làm bằng chứng cho quyết định bố trí tài nguyên khả thi, không lấy số lượng cấu hình làm câu chuyện chính.

### Giải thích kết quả và lập luận

Worker TP rộng hơn chia một model lên nhiều GPU hơn, nên ngân sách GPU cố định chứa được ít bản worker hơn. Nhiều worker có thể nhận request riêng nhưng mỗi worker có ít bộ nhớ GPU hơn và chi phí giao tiếp khác. Chỉ đo cấu hình nạp được shard FP 8 tương thích, truyền đúng và trả lời hợp lệ.

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

Nhóm so các cách đánh đổi giữa số worker và số GPU cùng xử lý một model. Có 17 cấu hình đo được để làm bằng chứng. Bố trí được chọn đạt khoảng 1912 token đạt chuẩn mỗi giây ở 48 request đồng thời. Vì tải và lịch sử truyền khác nhau, chưa thể kết luận đây là topology tối ưu toàn cục.

### Điều không nên nói

Không hiểu 07 hay 09 là phiên bản phần mềm. Không quy toàn bộ tăng thông lượng cho topology đang hiển thị vì N và lịch sử thử nghiệm cũng khác.

### Câu chuyển slide

Bố trí được chọn là quyết định theo ràng buộc đã quan sát; hình sau cho thấy cách dùng hai node.

---

<a id="slide-04"></a>

## Slide 04 — Why keep two TP4 prefills and one TP8 decode?

**Phần cứng: H200 · Firmus — bố trí được chọn trên 16 GPU.**

### Nói nhanh · 10–20 giây

Nhóm giữ hai worker bốnGPU xử lý prompt và một worker támGPU sinh token. Nhóm TP nằm trong từng node, còn hai giai đoạn dùng cách thực thi riêng. Đổi lại phải truyền KV đúng. Số đo hỗ trợ lựa chọn khả thi này, chưa chứng minh mọi phương án đã được so ở cùng tải.

![Slide 04](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-04.png)

### Slide muốn nói gì

Giải thích đánh đổi kỹ thuật khi giữ hai prefill TP 4 và một decode TP 8/EP 8; không tự gán toàn bộ tăng tốc cho một thay đổi topology.

### Giải thích kết quả và lập luận

Node đầu chạy hai worker prefill, mỗi worker bốnGPU; node sau chạy một worker decode támGPU. Các nhóm TP nằm trong một node. Tách giai đoạn cho phép chọn cách tính riêng, nhưng cần truyền KV. Đây là bố trí đã đo chạy được; bảng lịch sử chưa tách riêng tác dụng của từng đổi kiến trúc.

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

Nhóm giữ hai worker bốnGPU xử lý prompt và một worker támGPU sinh token. Nhóm TP nằm trong từng node, còn hai giai đoạn dùng cách thực thi riêng. Đổi lại phải truyền KV đúng. Số đo hỗ trợ lựa chọn khả thi này, chưa chứng minh mọi phương án đã được so ở cùng tải.

### Điều không nên nói

Thông số TP/EP chỉ đúng cho từng worker trong cấu hình cụ thể này. Không xem mỗi ô vuông là mức sử dụng GPU đo được và không nói sơ đồ đã chứng minh tăng tốc.

### Câu chuyển slide

Bố trí nạp được model vẫn phải chứng minh request đi hết dịch vụ.

---

<a id="slide-05"></a>

## Slide 05 — Worker readiness did not prove a working service

**Phần cứng: H200 · Firmus — nhánh khôi phục hetero-TP, khác bố trí được chọn.**

### Nói nhanh · 10–20 giây

Ở job 22271, worker H200 đã nạp mô hình nhưng warmup giữa prefill và decode hết thời gian chờ sau 360 giây. AIPerf chưa chạy, nên đây là lỗi sẵn sàng truyền dữ liệu, không phải phép đo thông lượng.

![Slide 05](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-05.png)

### Slide muốn nói gì

Xác lập lỗi đã quan sát trước khi giải thích cách sửa. Worker đã nạp mô hình, nhưng đường prefill sang decode thực tế chưa sẵn sàng phục vụ yêu cầu benchmark. Cần phân biệt triệu chứng lúc khởi động/truyền dữ liệu với một vấn đề hiệu năng steady-state giả định.

### Giải thích kết quả và lập luận

Giới thiệu slide này như giai đoạn nền của chuỗi suy luận bảy bước: triệu chứng, bằng chứng job và ranh giới lỗi. Đối lập trong tiêu đề là theo nghĩa đen: worker sẵn sàng, còn warmup cặp thì không. Không có biểu đồ số hay trục nào được ngụ ý.

### Thuật ngữ và ký hiệu cần hiểu

- **H200 Firmus:** Nền tảng GPU và địa điểm của phép thử lịch sử này; không gộp kết quả với phép đo H100 ở NSCC.
- **P8 / D8:** Nhãn nhóm phía prefill và decode trong topology này; giữ nguyên nhãn, không mặc định chúng có nghĩa là tám worker.
- **TP8/EP2 → TP4/EP4:** Prefill dùng tensor parallelism tám và expert parallelism hai; decode dùng tensor parallelism bốn và expert parallelism bốn. Hai vai trò có cấu hình khác nhau.
- **job 22271:** Job nền được lưu lại. Worker đã nạp mô hình, nhưng warmup cặp kết thúc bằng HTTP TimeoutError sau 360 giây.
- **360 seconds:** Thời lượng timeout của lần thử pair-warmup, không phải cửa sổ benchmark.
- **AIPerf:** Client/xuất kết quả benchmark. AIPerf không chạy trong job 22271 vì warmup thất bại trước đó.
- **P/D pair warmup:** Yêu cầu đi qua cả hai vai trò prefill và decode để kiểm tra hệ thống tách rời có thể phục vụ trước khi chấm điểm.

### Cách diễn giải số liệu hoặc sơ đồ

- Bước 1 — Triệu chứng: client không hoàn tất pair-warmup dù worker đã nạp mô hình.
- Bước 2 — Bằng chứng và ranh giới: job 22271 timeout sau 360 giây với HTTP TimeoutError; không có bản xuất AIPerf hay điểm throughput.
- Topology dùng TP khác nhau giữa vai trò: P8 TP8/EP2 sang D8 TP4/EP4. Nó không phải topology hai worker prefill TP4 cộng một worker decode TP8/EP8 được chọn về sau.
- Bản rà soát cùng thời điểm ghi bootstrap/truyền chưa được chứng minh; nó không xác định nghẽn băng thông hay bản sao KV chậm đã được đo.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Job 22271 nạp được worker mô hình nhưng yêu cầu warmup P/D với TP khác nhau bị timeout sau 360 giây. Log lưu lại kết thúc bằng HTTP TimeoutError; AIPerf chưa chạy nên không có điểm số.
- **Giả thuyết:** Lỗi tức thời nằm đâu đó trong bootstrap lạnh hoặc độ sẵn sàng truyền P/D; riêng triệu chứng này chưa xác lập nút thắt descriptor cụ thể.
- **Kết luận được hỗ trợ:** Xem đây là lỗi sẵn sàng trước benchmark, đồng thời giữ lại topology và bằng chứng trạng thái kết thúc chính xác. Không gọi đây là suy giảm throughput.
- **Chưa biết / giới hạn:** Chỉ từ timeout không thể xác định công đoạn bị kẹt, định lượng độ trễ truyền hay loại trừ các nguyên nhân bootstrap và bố trí khác.

### Lời nói mẫu

Triệu chứng ban đầu của chúng tôi khá cụ thể. Trên H200 Firmus, job 22271 dùng layout TP khác nhau giữa hai vai trò: prefill P8 với TP8, EP2 gửi sang decode D8 với TP4, EP4. Worker đã nạp mô hình, nhưng yêu cầu đi qua cặp prefill–decode không hoàn tất warmup. Log được giữ lại kết thúc bằng lỗi HTTP timeout sau 360 giây. AIPerf chưa chạy, vì vậy job này không có điểm benchmark. Bằng chứng cho thấy đường lạnh chưa sẵn sàng, chứ không chứng minh mạng nghẽn steady-state hay bản sao KV chậm. Topology này cũng khác cấu hình được chọn về sau với hai worker prefill TP4 và decode TP8/EP8.

### Điều không nên nói

Không báo cáo 22271 như điểm số thấp hoặc so thời gian timeout với warmup 0,68–0,70 giây sau đó như mức tăng tốc đã đo. Baseline này không có kết quả AIPerf.

### Câu chuyển slide

Tiếp theo xem quan sát hiệu năng và phân biệt chúng với bằng chứng nguyên nhân bottleneck.

---

<a id="slide-06"></a>

## Slide 06 — What does the profile identify—and what does it not?

**Phần cứng: H200 · Firmus — profile N48 riêng; quan sát N64 thuộc lần chạy khác.**

### Nói nhanh · 10–20 giây

Profile N 48 riêng cho thấy nhiều công việc ma trận, giao tiếp và attention. Giao tiếp cùng chuẩn hóa chiếm khoảng 23,48% tổng thời lượng kernel đã ghi. Đây là cơ sở đặt phép thử, chưa chứng minh 23,48% thời gian request bị nghẽn ở đó. Các request chậm token đầu về sau cũng chưa có nguyên nhân được tách rõ.

![Slide 06](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-06.png)

### Slide muốn nói gì

Đưa quan sát lên trước tối ưu và tách thành phần đáng nghi khỏi bottleneck đã chứng minh.

### Giải thích kết quả và lập luận

Profile N 48 riêng ghi công việc ma trận, giao tiếp/chuẩn hóa và attention. Tổng thời lượng kernel gợi ý hướng thử, không phải tỷ trọng thời gian thực vì kernel có thể chồng lấp. Lần N 64 về sau có request trượt TTFT, nhưng chưa tách hết thời gian queue/prefill/truyền để giải thích. Đây là bằng chứng từ các lần chạy khác nhau.

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

Profile N 48 riêng cho thấy nhiều công việc ma trận, giao tiếp và attention. Giao tiếp cùng chuẩn hóa chiếm khoảng 23,48% tổng thời lượng kernel đã ghi. Đây là cơ sở đặt phép thử, chưa chứng minh 23,48% thời gian request bị nghẽn ở đó. Các request chậm token đầu về sau cũng chưa có nguyên nhân được tách rõ.

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

Ví dụ sau cho thấy cách chọn một giả thuyết hẹp có cơ sở source, đồng thời giữ các nguyên nhân khác ở trạng thái chưa loại trừ.

---

<a id="slide-07"></a>

## Slide 07 — Why investigate descriptor setup before bandwidth?

**Phần cứng: H200 · nhánh khôi phục; CPU và source dùng điều tra descriptor.**

### Nói nhanh · 10–20 giây

Rà soát source thấy khoảng 403,8 triệu descriptor cho toàn pool trên mỗi rank nguồn, so với 188 cho một yêu cầu liên tục 4.000 token. Điều đó đủ để thử giảm việc khởi tạo trước, nhưng chưa loại trừ nguyên nhân từ mạng hay bố trí.

![Slide 07](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-07.png)

### Slide muốn nói gì

Giải thích quyết định ưu tiên: triệu chứng xảy ra trước khi chấm điểm, còn kiểm tra source cho thấy khối lượng chuẩn bị descriptor lớn, phù hợp với lỗi warmup lạnh. Đây là lý do thử giả thuyết về setup, không phải bằng chứng rằng không có nút thắt khác.

### Giải thích kết quả và lập luận

Trình bày chuỗi bằng chứng ở bước 3 và 4 của luồng bảy bước: xác định thành phần liên quan, rồi nêu vì sao ưu tiên chi phí setup của nó. Hai số có phạm vi khác nhau—toàn pool mỗi rank so với một yêu cầu—không được diễn giải thành tỷ lệ thời gian hay tăng tốc.

### Thuật ngữ và ký hiệu cần hiểu

- **NIXL:** Đường truyền liên quan đến việc chuyển trạng thái KV giữa worker prefill và decode tách rời.
- **heterogeneous TP:** Kích thước tensor parallelism attention khác nhau ở prefill và decode; điều này làm thay đổi cách ánh xạ KV head và dải byte giữa các peer.
- **descriptor:** Metadata mô tả dải bộ nhớ cần truyền, không phải payload tensor KV.
- **403.8 million per source rank:** Số gần đúng descriptor nguồn cho toàn pool được suy ra với hình học TP8 đại diện từ 2.148.119 KV slot, 94 layer và các mục K/V.
- **188 per request:** Số từ kiểm tra hình học CPU cho yêu cầu liên tục 4.000 token TP8 sang TP4 sau khi gộp dải kề nhau.
- **source rank:** Một tiến trình/phân vùng mô hình phía nguồn trong phân tán, nơi danh sách descriptor được chuẩn bị.
- **steady-state traffic:** Luồng yêu cầu được tính điểm sau khi worker và đường truyền sẵn sàng; khác với bootstrap và warmup lạnh.

### Cách diễn giải số liệu hoặc sơ đồ

- Bước 3 — Thành phần: kiểm tra source xác định phần việc liên quan ở khâu chuẩn bị và truyền descriptor KV NIXL với TP khác nhau.
- Bước 4 — Bằng chứng để ưu tiên: ghi chú source suy ra khoảng 403,8 triệu descriptor cho cả pool mỗi rank, trong khi hình học CPU cho 188 descriptor với yêu cầu liên tục 4.000 token.
- Các số đếm descriptor, không phải byte, giây, băng thông hay tốc độ. Phạm vi hai số khác nhau và chúng không đo thời gian setup.
- Vì lỗi xảy ra trước chấm điểm và thay đổi đề xuất nhắm vào setup, đây là hướng có bằng chứng trực tiếp hơn so với việc chỉnh bandwidth steady-state, bố trí KV hay vị trí scheduler. Các phương án đó chưa bị loại trừ bằng thí nghiệm.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Hình học dựa trên source cho thấy khối lượng liệt kê toàn pool rất lớn—khoảng 403,8 triệu descriptor mỗi rank nguồn—so với 188 dải đã gộp cho một yêu cầu đại diện.
- **Giả thuyết:** Tạo descriptor chỉ cho các trang của yêu cầu hiện tại có thể giảm việc setup lúc lạnh và giúp warmup cặp hoàn tất.
- **Kết luận được hỗ trợ:** Setup descriptor là mục tiêu hợp lý để thử trước vì khớp triệu chứng trước benchmark và có tín hiệu chi phí cụ thể từ source. Đây là ưu tiên kiểm tra, không phải chẩn đoán nguyên nhân duy nhất.
- **Chưa biết / giới hạn:** Không đo thời gian khởi tạo của code cũ. Mức sử dụng băng thông, bố trí KV, lịch đặt tài nguyên/vị trí và công việc bootstrap khác vẫn có thể góp phần.

### Lời nói mẫu

Sau khi khoanh vùng lỗi ở đường prefill–decode lạnh, chúng tôi xem phần chuẩn bị descriptor NIXL cho tensor parallelism khác nhau. Hình học từ source cho lý do để thử bước setup này trước. Với rank nguồn TP8 đại diện, mô tả toàn pool KV cần khoảng 403,8 triệu entry. Với yêu cầu liên tục 4.000 token TP8 sang TP4, phép tính hình học CPU cho 188 entry đã gộp. Đây là số descriptor với phạm vi khác nhau, không phải byte, giây hay mức tăng tốc đo được. Vì triệu chứng xuất hiện trước bước chấm điểm và tạo descriptor là một chi phí setup có thể xác định, đây là thử nghiệm trực tiếp hơn so với chỉnh băng thông steady-state, bố trí KV hay vị trí scheduler trước. Tuy nhiên, các phương án đó chưa bị loại trừ.

### Điều không nên nói

Không chia 403,8 triệu cho 188 rồi gọi đó là tăng tốc hai triệu lần. Không có phép đo thời gian setup cũ-mới, mức dùng mạng hay phân rã nhân quả.

### Câu chuyển slide

Cách sửa và bằng chứng chạy được nằm ở slide dự phòng24–25; tiếp theo thử thay đổi theo thông lượng dịch vụ đạt chuẩn.

---

<a id="slide-08"></a>

## Slide 08 — Do attention and communication choices interact?

**Phần cứng: H200 · Firmus · N52.**

### Nói nhanh · 10–20 giây

Ở H200 N52, tổ hợp attention và giao tiếp đo cao hơn control MNNVL sau đó khoảng 1,43 phần trăm. Kết quả ủng hộ tổ hợp tại tải này, không chứng minh gain từng phần cộng lại hay quy tắc phổ quát.

![Slide 08](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-08.png)

### Slide muốn nói gì

Đặt câu hỏi liệu lựa chọn attention và backend giao tiếp tập thể có phối hợp tốt hơn khi dùng cùng nhau ở một tải H200 cố định hay không. Kết quả gợi ý nên thử tổ hợp; chưa chứng minh gain của hai thành phần cộng tuyến tính.

### Giải thích kết quả và lập luận

Đọc các kết quả N52 như các cấu hình backend riêng ở cùng tải: FlashInfer 2.440,386; MNNVL 2.592,162; tổ hợp 2.631,085; control MNNVL đo sau đó 2.594,028 good tokens/s. Đối chiếu tổ hợp với control MNNVL cùng tải: cao hơn khoảng 1,43%.

### Thuật ngữ và ký hiệu cần hiểu

- **N52:** Cấu hình concurrency client 52 request đã gửi nhưng chưa hoàn tất; không phải số GPU hay batch decode.
- **FlashInfer:** Cách triển khai attention trên GPU được thử trong đường phục vụ.
- **MNNVL:** Đường giao tiếp collective qua NVIDIA NVLink.
- **Tương tác:** Kết quả dùng hai thành phần cùng lúc có thể khác điều dự đoán từ từng thành phần riêng; cần phép đo tổ hợp có đối chứng.
- **Good tokens/s:** Request đủ điều kiện mỗi giây nhân mục tiêu cố định 200 output token.

### Cách diễn giải số liệu hoặc sơ đồ

- Câu hỏi là: chọn cả cách triển khai attention và backend giao tiếp có cải thiện dịch vụ không? Ở H200 N52, các quan sát riêng và kết hợp lần lượt là 2.440,386; 2.592,162; 2.631,085 good tokens/s. Control MNNVL đo sau đó tại cùng tải đạt 2.594,028; quan sát kết hợp cao hơn khoảng 1,43%.
- Bằng chứng ủng hộ việc xem tổ hợp này là operating point đáng quan tâm trong cấu hình đo. Nó không chứng minh quy luật tương tác chung, không cô lập phần đóng góp nhân quả của từng backend và không cho phép cộng chênh lệch riêng như thể hai thành phần độc lập.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Quan sát kết hợp cao hơn control MNNVL đo sau khoảng 1,43% tại H200 N52; các quan sát FlashInfer và MNNVL riêng thấp hơn.
- **Giả thuyết:** Attention và backend giao tiếp có thể phối hợp thuận lợi khi chạy cùng nhau.
- **Kết luận được hỗ trợ:** Tổ hợp đo được có triển vọng tại tải này và đáng so sánh như một cấu hình dịch vụ hoàn chỉnh.
- **Chưa biết / giới hạn:** Kết quả không lượng hóa gain nhân quả từng thành phần và chưa cho biết tải, model hay phần cứng khác sẽ ra sao.

### Lời nói mẫu

Chúng tôi hỏi liệu attention và giao tiếp có tương tác hay không. Ở H200 N52, tổ hợp đạt 2.631 good token mỗi giây, cao hơn control MNNVL đo sau ở 2.594 khoảng 1,43 phần trăm. Các phép đo riêng giúp hình thành giả thuyết, nhưng không thể cộng lại để dự đoán tổ hợp. Kết quả ủng hộ operating point đã thử, không phải quy tắc backend phổ quát.

### Điều không nên nói

Đây là các quan sát cùng tải, chưa phải chứng minh factorial đầy đủ rằng mỗi thành phần gây ra một phần gain. Không cộng gain đo riêng.

### Câu chuyển slide

Sau khi nhận diện tổ hợp có triển vọng, tiếp theo hỏi thay đổi decode runner có cải thiện mục tiêu dịch vụ đầy đủ không.

---

<a id="slide-09"></a>

## Slide 09 — Does a decode change improve the service objective?

**Phần cứng: H200 · Firmus · N60 đầy đủ.**

### Nói nhanh · 10–20 giây

Ở H200 full N60, thay đổi decode tăng goodput 5,295 phần trăm và giảm ITL, nhưng TTFT trung bình tăng khoảng 125 mili giây. Lần treatment lặp gần bằng; kết luận chỉ áp dụng cho setting này. Đây là đánh đổi throughput với thời gian chờ token đầu.

![Slide 09](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-09.png)

### Slide muốn nói gì

Đánh giá thay đổi decode runner bằng kết quả dịch vụ hoàn chỉnh. Control ghép cặp giúp hỏi treatment có đổi goodput ở cấu hình này không; các hàng độ trễ cho thấy cái giá đi kèm.

### Giải thích kết quả và lập luận

So sánh control auto-decode mới 24912 với lần lặp decode HPC-Ops 24913 ở cùng cấu hình full N60. Goodput tăng 2.838,853→2.989,175 token/s; TTFT trung bình tăng 822,292→947,627 ms; ITL trung bình/request giảm 16,579→14,934 ms; SLA đồng thời đổi 98,7599%→98,8178%.

### Thuật ngữ và ký hiệu cần hiểu

- **Full N60:** Benchmark đầy đủ với concurrency client 60; cả hai nhánh giữ DeepGEMM prefill và chunk 8.192.
- **HPC-Ops:** Decode runner/backend được cung cấp và thử ở đây; nhóm không phát minh backend này.
- **TTFT:** Thời gian từ lúc request bắt đầu tới token đầu tiên được sinh.
- **ITL trung bình/request:** Khoảng thời gian trung bình giữa các token trong một request.
- **Control ghép cặp:** Run auto-decode mới dùng làm đối chứng cho thay đổi decode runner dự định.

### Cách diễn giải số liệu hoặc sơ đồ

- Goodput từ control sang treatment tăng 5,295%. TTFT trung bình tăng 125,335 ms, còn ITL trung bình/request giảm 1,644 ms. Tỷ lệ SLA đồng thời chỉ nhích nhẹ. Treatment lặp 24913 thấp hơn treatment ban đầu 24738 đạt 2.990,151 token/s là 0,033%.
- Kết quả hỗ trợ một tương tác có thể lặp lại giữa decode runner và dịch vụ H200 N60 này. Nó không chứng minh HPC-Ops luôn tốt hơn. Lần kiểm tra mở rộng 24913 không có chuỗi telemetry phần cứng liên tục riêng; profile kernel N48 khác không thể giải thích nhân quả cho kết quả N60.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Goodput tăng 5,295%, ITL cải thiện, nhưng TTFT trung bình tăng khoảng 125 ms; deployment treatment riêng lặp goodput gần bằng.
- **Giả thuyết:** Thay đổi decode runner có thể tăng throughput hữu ích trong cấu hình này và đồng thời đổi cân bằng độ trễ giữa token đầu với token sau.
- **Kết luận được hỗ trợ:** Kết quả đầy đủ có đối chứng và lần lặp treatment độc lập hỗ trợ operating point H200 N60 này.
- **Chưa biết / giới hạn:** Nguyên nhân kernel chính xác, phân rã hàng đợi/tính toán, khái quát sang phần cứng khác và quality full-set official chưa xác minh.

### Lời nói mẫu

Ở full N60, control auto-decode mới đạt 2.839 good token mỗi giây. Lần lặp decode HPC-Ops đạt 2.989, tăng 5,295 phần trăm. TTFT trung bình chậm hơn khoảng 125 mili giây, còn khoảng cách token cải thiện. Lần treatment độc lập thấp hơn bản đầu chỉ 0,033 phần trăm. Kết quả ủng hộ setting đã thử cùng tradeoff độ trễ, không chứng minh HPC-Ops luôn nhanh hơn.

### Điều không nên nói

Treatment lặp dùng cùng cấu hình phục vụ và họ phần cứng; không phải so sánh thế hệ GPU thứ hai. Không dùng profile N48 riêng để giải thích nhân quả N60.

### Câu chuyển slide

Tiếp theo đo xem lợi ích full-run kéo dài tới đâu khi tăng concurrency client từ N62 lên N64.

---

<a id="slide-10"></a>

## Slide 10 — Where should we stop increasing concurrency?

**Phần cứng: H200 · Firmus · cặp N62/N64 và kiểm chứng tải.**

### Nói nhanh · 10–20 giây

N64 tăng goodput đầy đủ 1,083 phần trăm so với N62 và lặp trong 0,014 phần trăm. TTFT tăng nhẹ. Lợi thế N68 từ phép thử ngắn còn 0,083 phần trăm ở cặp đầy đủ, nên N64 là điểm dừng được bằng chứng hỗ trợ.

![Slide 10](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-10.png)

### Slide muốn nói gì

Chọn mức concurrency có ích bằng control đầy đủ và lần lặp N64 độc lập, đồng thời không chạy theo kết quả sàng lọc ngắn lớn hơn nhưng chưa được xác nhận.

### Giải thích kết quả và lập luận

Đọc ba cột: control N62 25365; candidate N64 25366; lần lặp N64 25373. Goodput lần lượt 3.011,875 / 3.044,490 / 3.044,075 token/s. Gain N64 đầy đủ so với N62 là 1,082867%; lần lặp N64 thấp hơn candidate chỉ 0,013634%. TTFT tăng nhẹ, ITL gần như giữ nguyên, SLA giảm chút ít; lỗi/hủy bằng không.

### Thuật ngữ và ký hiệu cần hiểu

- **Concurrency N62/N64:** Số request client được phép chạy đồng thời; không phải batch decode thực tế.
- **Full 60/120/30:** Warmup 60 giây, đo tính điểm 120 giây, grace 30 giây cho request chưa xong.
- **Goodput:** Tốc độ request đủ điều kiện × 200 output token cố định.
- **Sàng lọc N68:** Phép thử ngắn gợi ý +2,27% nhưng cặp đầy đủ chỉ còn +0,083%.
- **Allocation độc lập:** Lần scheduler cấp tài nguyên/run mới; không chứng minh GPU duy nhất hay thế hệ phần cứng khác.

### Cách diễn giải số liệu hoặc sơ đồ

- Control N62 đầy đủ 25365 so với candidate N64 25366 tăng 1,082867%. Run N64 độc lập 25373 đạt 3.044,075 token/s, thấp hơn candidate 0,013634%. Hai run N64 lấy mẫu cùng tập GPU UUID, nên mức đa dạng phần cứng bị giới hạn và không tạo khoảng tin cậy.
- TTFT trung bình là 1.037,630 ms tại N62 và 1.110,463 ms tại N64; ITL trung bình đổi từ 14,958 lên 15,003 ms. SLA đồng thời là 98,7227% so với 98,6330%, không lỗi/hủy. Kết quả sàng lọc N68 thuận lợi không lặp lại: gain cặp đầy đủ chỉ 0,083056%.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** N64 tăng goodput khoảng 1,083% so với N62 và lặp trong 0,014%; TTFT tăng nhẹ, SLA giảm chút, ITL gần như không đổi.
- **Giả thuyết:** Concurrency client tăng vừa phải có thể tăng sử dụng pipeline đủ để cải thiện throughput.
- **Kết luận được hỗ trợ:** Giữ N64 như operating point đã lặp; không chọn kết quả N68 ngắn thay cho bằng chứng đầy đủ.
- **Chưa biết / giới hạn:** Các run không tách riêng hàng đợi, truyền dữ liệu và tính toán; không tạo khoảng tin cậy hay tìm optimum toàn cục.

### Lời nói mẫu

Control N62 đầy đủ đạt 3.012 good token mỗi giây. N64 đạt 3.044 và lần N64 độc lập gần như trùng kết quả. Đây là gain 1,083 phần trăm, kèm TTFT tăng nhẹ và SLA đồng thời thấp hơn chút ít. Sàng lọc N68 ngắn có vẻ tốt hơn, nhưng cặp đầy đủ chỉ còn 0,083 phần trăm. Chúng tôi dừng ở N64 vì gain tồn tại qua run đầy đủ và lần lặp; không gọi đây là mức tối đa toàn cục.

### Điều không nên nói

N62/N64/N68 là mức concurrency client, không phải số GPU hay batch decode. Hai allocation lặp không tạo khoảng tin cậy chính thức.

### Câu chuyển slide

Dù phần lớn request đạt giới hạn kết hợp, slide sau xem cụ thể những request vẫn trượt.

---

<a id="slide-11"></a>

## Slide 11 — Which requests still fail after goodput improves?

**Phần cứng: H200 · Firmus · dữ liệu từng request của job 26766.**

### Nói nhanh · 10–20 giây

Biểu đồ H200 N64 cho thấy 1.875 trong 1.902 request đạt cả hai giới hạn. 27 request còn lại chỉ trượt TTFT. Thời điểm gần admission là manh mối cần nghiên cứu, không phải bằng chứng nguyên nhân. Nhóm request đầu đáng xem thêm, nhưng biểu đồ chưa xác định nguyên nhân.

![Slide 11](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-11.png)

### Slide muốn nói gì

Chuyển từ số trung bình sang tiêu chí đạt ở từng request. Biểu đồ cho thấy mọi miss quan sát được đều nằm ở TTFT, nhưng cần phân biệt mối liên hệ gần thời điểm admission với lời giải thích nhân quả.

### Giải thích kết quả và lập luận

Mỗi điểm là một request: trục x là thời gian tới token đầu (TTFT, ms), trục y là ITL trung bình của request đó (ms). Ngưỡng đỏ dọc/ngang là TTFT 3.000 ms và ITL 20 ms. Teal đậm #23373B (có thể nhìn xanh lam-lục) đạt cả hai; cam #EB811B (có thể nhìn vàng) trượt ít nhất một. Vùng xanh nhạt chỉ biểu thị TTFT, không phải đạt đồng thời. Điểm chồng đậm hơn do alpha, không phải lớp riêng.

### Thuật ngữ và ký hiệu cần hiểu

- **TTFT:** Thời gian từ lúc request bắt đầu tới token đầu tiên được sinh.
- **ITL trung bình/request:** Khoảng cách trung bình giữa các token được sinh trong một request.
- **Đạt đồng thời:** Một request đạt cả TTFT ≤ 3.000 ms và ITL trung bình/request ≤ 20 ms.
- **P95:** Phân vị 95; 95% quan sát không vượt giá trị này, mô tả phần đuôi chứ không phải trung bình.
- **Native runtime:** Đường thực thi server của job 26766, khác đường phần mềm portable replay.

### Cách diễn giải số liệu hoặc sơ đồ

- Job native-runtime đầy đủ 26766 đạt 3.045,501509 good output tokens/s. Trong 1.902 request được profile, 1.875 (98,580%) đạt cả hai giới hạn. 27 request trượt TTFT; không request nào trượt ITL trung bình, không có lỗi hay hủy request.
- TTFT trung bình/p95 là 1.108,869/1.311,693 ms; ITL trung bình/p95 là 15,0075/15,1930 ms. Cả 27 miss bắt đầu trong 13,004085 ms sau admission của profile. Đây là tương quan nhóm đầu, không chứng minh startup, hàng đợi, prefill, truyền dữ liệu hay tính toán gây miss.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** 1.875/1.902 request đạt đồng thời; cả 27 miss chỉ trượt TTFT, không lỗi/hủy request.
- **Giả thuyết:** Request vào ở đầu cửa sổ profile có thể gặp tác động startup/admission riêng.
- **Kết luận được hỗ trợ:** Phân bố cho thấy khoảng cách chấp nhận còn lại trong run này nằm ở phần đuôi TTFT.
- **Chưa biết / giới hạn:** Mối liên hệ thời điểm không chỉ ra hàng đợi, prefill, truyền KV hay tính toán nào gây miss TTFT.

### Lời nói mẫu

Mỗi chấm là một request. Request chỉ đạt nếu TTFT không quá 3.000 mili giây và ITL trung bình không quá 20. Có 1.875 trên 1.902 request đạt cả hai; 27 miss đều chỉ do TTFT, không có lỗi request. Chúng bắt đầu gần thời điểm profile nhận tải. Đây là dấu hiệu đáng nghiên cứu, nhưng thời điểm không chứng minh startup là nguyên nhân.

### Điều không nên nói

Vùng xanh nhạt chỉ kiểm tra TTFT. Không hiểu đó là vùng đạt kết hợp; giữ đủ 1.902 request trong mẫu số.

### Câu chuyển slide

Slide sau đặt các kết quả can thiệp riêng cạnh nhau để hỏi thay đổi nào thực sự cải thiện mục tiêu.

---

<a id="slide-12"></a>

## Slide 12 — Keep an intervention only if the objective improves

**Phần cứng: H200 và H100 — ba phép thử độc lập, không phải so phần cứng.**

### Nói nhanh · 10–20 giây

Ba can thiệp riêng cải thiện metric phụ nhưng không đạt quy tắc áp dụng dịch vụ: gain cache H200 dưới 1%, sparse graph mất goodput, FA3 H100 mất goodput dù TTFT nhanh hơn. Không gộp kết quả của chúng.

![Slide 12](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-12.png)

### Slide muốn nói gì

Đây là bảng quyết định, không phải một thí nghiệm duy nhất hay một phép so phần cứng. Bảng đặt cạnh ba kết quả can thiệp H200 độc lập và một kết quả attention H100 riêng. Mỗi hàng phải so thay đổi với control riêng và áp dụng quy tắc mức tăng hữu ích.

### Giải thích kết quả và lập luận

Đọc riêng bốn nhóm bằng chứng: cache prefill H200 27376→27378 tăng 0,240921%, thấp hơn ngưỡng lợi ích định trước 1%; sparse decode graph H200 giảm bộ nhớ capture 1,15→0,36 GB/rank nhưng goodput giảm 0,370208%; cặp decode FlashInfer→FA3 H100 N54 riêng giảm TTFT 118,922 ms nhưng goodput giảm 0,812%. Không so throughput thô của chúng như một thí nghiệm.

### Thuật ngữ và ký hiệu cần hiểu

- **Ngưỡng mức tăng hữu ích:** Yêu cầu định trước lớn hơn 1% dùng để quyết định áp dụng thay đổi H200; kết quả dương nhỏ chưa đủ.
- **Cache prefill:** Bộ nhớ đệm có thể tái sử dụng trạng thái tiền tố prompt đã xử lý; thử nghiệm H200 tắt cache này cho prefill.
- **Sparse decode graph:** Chỉ capture một số batch decode đã chọn thay vì dải dày; bộ nhớ capture không phải toàn bộ VRAM.
- **Bộ nhớ capture mỗi rank:** Bộ nhớ graph capture dùng bởi một tiến trình phân tán, đơn vị GB/rank.
- **TTFT / goodput:** Thời gian tới token đầu / output token đủ điều kiện mỗi giây; cải thiện một metric có thể làm metric kia xấu đi.

### Cách diễn giải số liệu hoặc sơ đồ

- Cặp cache H200: control mới 27376 đạt 3.041,119598; candidate 27378 đạt 3.048,446289, chênh +0,240921%. Candidate đạt điều kiện request/output nội bộ (1.879/1.905 request đạt đồng thời; không lỗi), nhưng không qua ngưỡng quyết định mức tăng hữu ích >1% đã đặt trước.
- Job sparse graph H200 27510 đạt 3.029,861122 so với control 27376 đạt 3.041,119598, tức −0,370208%. Bộ nhớ capture graph decode giảm 1,15 xuống 0,36 GB mỗi rank; giảm tài nguyên này không cải thiện goodput. Riêng cặp H100 N54, FA3 giảm TTFT trung bình 118,922 ms nhưng tăng ITL và latency request trung bình; goodput giảm 0,812%. Đây là các thử nghiệm riêng trên phần cứng riêng, có control riêng.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Cache tăng 0,240921%; sparse graph tiết kiệm bộ nhớ capture nhưng mất 0,370208% goodput; FA3 H100 giảm TTFT nhưng mất 0,812% goodput.
- **Giả thuyết:** Thay cache, graph capture hoặc attention có thể cải thiện một metric tài nguyên/độ trễ mà không hại mục tiêu dịch vụ.
- **Kết luận được hỗ trợ:** Giữ setting N64/cache đã lặp; giữ dense graph và FlashInfer decode cho cấu hình đã đo. Không can thiệp nào đạt tiêu chí áp dụng.
- **Chưa biết / giới hạn:** Ba kết quả không chung control hay phần cứng; không thể cộng tác động, xếp hạng theo số thô hoặc khái quát ngoài từng cấu hình.

### Lời nói mẫu

Slide này gộp các quyết định độc lập, không phải một factorial experiment. Trên H200, tắt cache prefill tăng 0,24 phần trăm, thấp hơn ngưỡng hữu ích 1 phần trăm. Sparse graph tiết kiệm bộ nhớ capture từ 1,15 xuống 0,36 gigabyte mỗi rank nhưng goodput giảm 0,37 phần trăm. Ở cặp H100 N54 riêng, FA3 cải thiện TTFT nhưng goodput giảm 0,812 phần trăm. Giữ setting hỗ trợ mục tiêu đầy đủ hơn; không cộng các gain không liên quan.

### Điều không nên nói

Cặp H100 không phải hàng H200. Bộ nhớ capture không phải tổng VRAM; TTFT hay bộ nhớ thấp hơn một mình chưa chứng minh cấu hình dịch vụ tốt hơn.

### Câu chuyển slide

Một đề xuất giảm latency là speculative decoding; tiếp theo theo dõi giả thuyết thất bại và các lần thử sau.

---

<a id="slide-13"></a>

## Slide 13 — Did speculative decoding solve this workload?

**Phần cứng: H200 · Firmus · EAGLE3.**

### Nói nhanh · 10–20 giây

Vị trí draft EAGLE3 làm trượt latency; validator được sửa; cả retry ngắn và thử nghiệm shallow đầy đủ riêng đều mất goodput. Cách đã thử không giúp workload này, dù còn cấu hình khác chưa được đo. Bằng chứng hiện tại chỉ áp dụng cho các cấu hình đã thử trên H200.

![Slide 13](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-13.png)

### Slide muốn nói gì

Theo dõi chuỗi lập luận EAGLE3: giả thuyết về vị trí chạy draft, lỗi validator, retry ngắn sau khi sửa và một phép đo đầy đủ riêng. Sửa công cụ đo giúp lần chạy sau hợp lệ; không biến kết quả hiệu năng thua thành thắng.

### Giải thích kết quả và lập luận

Đọc theo thứ tự: draft trên mọi worker 25948 trượt quy tắc latency đồng thời; thử decode-only 25988 bị validator từ chối vì đòi KV draft ở prefill chỉ chạy target; run ngắn sau sửa 25998 qua protocol giới hạn nhưng mất 4,74% goodput; run shallow đầy đủ riêng 27238 mất 2,080318% so với control 26949.

### Thuật ngữ và ký hiệu cần hiểu

- **Speculative decoding EAGLE3:** Model draft đề xuất token output, model target xác minh; truyền đúng không tự chứng minh phục vụ nhanh hơn.
- **Prefill chỉ chạy target:** Worker xử lý prompt bằng model target nhưng không chạy model draft.
- **KV region:** Vùng nhớ giữ trạng thái key/value; validator chỉ kiểm tra ở role thực sự chạy draft.
- **Protocol ngắn:** Run giới hạn, không thay thế workload cố định đầy đủ để kết luận hiệu năng dịch vụ.
- **Mất goodput:** Số output token đủ điều kiện mỗi giây thấp hơn control target-only ghép cặp.

### Cách diễn giải số liệu hoặc sơ đồ

- Thử nghiệm ban đầu mọi worker 25948 trượt giới hạn latency đồng thời. Chuyển draft sang decode-only được giả thuyết là giảm thời gian tới token đầu. Sau đó attempt 25988 bị validator từ chối vì validator áp sai số KV region của draft lên prefill chỉ chạy target; sửa theo role nhưng vẫn lưu lỗi ban đầu.
- Retry ngắn 25998 qua protocol giới hạn nhưng mất 4,74% goodput so với control target-only riêng. Run shallow đầy đủ sau đó 27238 đạt 2.971,628430 so với control 26949 ở 3.034,761104, giảm 2,080318%. Acceptance draft thấp là telemetry mô tả, không phải giải thích nhân quả cho thời gian.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Sau khi sửa validator, retry decode-only ngắn mất 4,74%; thử nghiệm shallow đầy đủ riêng mất 2,080318% goodput.
- **Giả thuyết:** Giới hạn draft vào decode hoặc dùng draft nông có thể giảm TTFT mà không mất throughput dịch vụ tổng thể.
- **Kết luận được hỗ trợ:** Các cấu hình đã thử không giải quyết được workload này; dừng chúng và giữ lịch sử lỗi/sửa công cụ.
- **Chưa biết / giới hạn:** Quan sát chưa chỉ ra pha dịch vụ nào chính xác gây chậm và cũng không bác bỏ mọi cấu hình speculative khác.

### Lời nói mẫu

Chúng tôi thử EAGLE3 để giảm độ trễ sinh token. Chạy draft trên mọi worker trượt quy tắc latency kết hợp. Chuyển draft sang decode-only là giả thuyết hợp lý, nhưng validator kiểm tra sai prefill chỉ chạy target. Chúng tôi sửa và giữ lại lỗi đó. Retry ngắn chạy được nhưng mất 4,74 phần trăm goodput; thử nghiệm shallow đầy đủ riêng mất 2,08 phần trăm. Các cấu hình này không giúp workload hiện tại. Truyền draft đúng chức năng không đồng nghĩa dịch vụ nhanh hơn.

### Điều không nên nói

Phân biệt lỗi validator với lỗi model, và retry ngắn với run đầy đủ. Không biến telemetry acceptance thấp thành phân tích nhân quả latency.

### Câu chuyển slide

Tiếp theo hỏi cải thiện N64 có lặp qua các deployment không và so sánh các run đầy đủ thế nào cho công bằng.

---

<a id="slide-14"></a>

## Slide 14 — Does the improvement survive another deployment?

**Phần cứng: H200 · Firmus — ba lần lịch sử, native riêng và ứng viên cache.**

### Nói nhanh · 10–20 giây

Ba run H200 N64 đầy đủ trung bình 3.044,40. Kết quả native-runtime được tách riêng. Cache cao hơn chỉ 0,24 phần trăm so control riêng, dưới ngưỡng hữu ích; raw data phục hồi từ job lỗi không phải lần lặp đầy đủ thành công.

![Slide 14](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-14.png)

### Slide muốn nói gì

Phân biệt operating point được lặp lại với đỉnh đơn lẻ và chuỗi runtime phần mềm về sau. Chọn cấu hình dựa trên tính lặp lại và ngưỡng lợi ích định trước, không dựa vào số lớn nhất.

### Giải thích kết quả và lập luận

Ba run N64 đầy đủ lịch sử 25366/25373/25487 trung bình 3.044,400475 good tokens/s. Job native-runtime 26766 là kết quả đầy đủ riêng: 3.045,501509 và SLA đồng thời 98,580442%. Candidate cache 27378 có số cao hơn 3.048,446289, nhưng control mới ghép cặp 27376 là 3.041,119598, nên gain chỉ +0,240921%, thấp hơn ngưỡng hữu ích >1%.

### Thuật ngữ và ký hiệu cần hiểu

- **Lần triển khai lặp độc lập:** Run scheduler khác của cùng cấu hình; kiểm tra tính lặp lại, không nhất thiết dùng GPU riêng hay hệ thống phần cứng khác.
- **Native runtime:** Môi trường thực thi phần mềm server khác, không phải thế hệ GPU mới.
- **Control mới ghép cặp:** Run so sánh mới dùng setting baseline của cặp cache.
- **Run đầy đủ do nhóm review:** Nhóm chạy protocol đầy đủ trên cluster accelerator được cấp, rồi kiểm tra raw request output và runtime gates. Đây không phải run trên laptop cá nhân, không phải ranking hay xác nhận accuracy chính thức của ban tổ chức.
- **Ngưỡng lợi ích hữu ích:** Yêu cầu cải thiện định trước >1% để xem can thiệp là có ích.

### Cách diễn giải số liệu hoặc sơ đồ

- Ba run N64 đầy đủ lịch sử trung bình 3.044,400475 good tokens/s và hỗ trợ chọn N64 vì được lặp lại. Native-runtime 26766 riêng đạt 3.045,501509 và 98,580442%; không gộp với ba run lịch sử vì đường runtime server khác.
- Candidate cache đầy đủ cao nhất 27378 đạt 3.048,446289, nhưng so với control mới riêng 27376 đạt 3.041,119598, gain là +0,240921%, thấp hơn ngưỡng hữu ích >1%. Số cao nhất chưa phải cải thiện hữu ích được xác nhận. Điểm raw portable 3.055,330517 được phục hồi từ job 27145, nhưng job scheduler thất bại ở hậu xử lý; đây không phải lần triển khai toàn allocation thành công.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Ba lần lặp N64 lịch sử trung bình 3.044,400475; job native 26766 tương tự nhưng riêng; cache 27378 chỉ hơn control mới của nó 0,240921%.
- **Giả thuyết:** Điểm được lặp lại là cơ sở chọn cấu hình đáng tin hơn một quan sát đơn lẻ cao nhất.
- **Kết luận được hỗ trợ:** Giữ N64 được lặp lại và không chọn chênh lệch cache nhỏ làm gain hữu ích.
- **Chưa biết / giới hạn:** Không kết quả nào chứng minh optimum toàn cục, nhân quả giữa runtime, ranking của ban tổ chức hay quality model official.

### Lời nói mẫu

Ba run N64 đầy đủ lịch sử trung bình 3.044,40 good token mỗi giây. Run native-runtime sau đó tương tự nhưng được báo riêng vì đường phần mềm thực thi khác. Candidate cache cao nhất đạt 3.048,45, chỉ hơn control mới của nó 0,24 phần trăm, dưới ngưỡng hữu ích một phần trăm. Chúng tôi giữ N64 đã lặp lại thay vì chọn số đơn lẻ lớn nhất. Điểm raw phục hồi từ job lỗi hậu xử lý không phải deployment đầy đủ thành công.

### Điều không nên nói

Lần triển khai lặp không nhất thiết là phần cứng vật lý mới. Run đầy đủ do nhóm review không phải ranking hay chứng nhận quality official. Không thay trạng thái job thất bại bằng raw data phục hồi.

### Câu chuyển slide

Ngay trong H200, các kết quả replay sau khác nhau; tiếp theo xem runtime và workload có thể gây nhiễu, không mặc định một nguyên nhân duy nhất.

---

<a id="slide-15"></a>

## Slide 15 — Why did a later replay score lower?

**Phần cứng: H200 · Firmus — các protocol và đường thực thi khác nhau.**

### Nói nhanh · 10–20 giây

N64 đầy đủ lịch sử trung bình 3.044,40, còn control ngắn mới khoảng 2.560. Graph policy, giới hạn admission server và quy trình đo đều thay đổi. Phép thử hoàn tất không cô lập nguyên nhân, nên giữ drift mà không quy cho một flag.

![Slide 15](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-15.png)

### Slide muốn nói gì

Điều tra chênh lệch thay vì giải thích bằng một flag thuận tiện. Bằng chứng xác định settings và bối cảnh đo đã đổi, nhưng so sánh hoàn tất không cô lập được một nguyên nhân duy nhất đủ giải thích.

### Giải thích kết quả và lập luận

Câu hỏi là vì sao N64 đầy đủ lịch sử trung bình 3.044,400475 trong khi control ngắn mới khoảng 2.560. ServerArgs cho thấy policy prefill graph và giới hạn max-running-request đã đổi; harness/cách quan sát cũng khác. Replay legacy chính xác 26313 đạt 2.830,923547; run native mới 26766 đạt 3.045,501509. Đây là các chuỗi runtime/protocol khác nhau, không phải thang đo một yếu tố duy nhất.

### Thuật ngữ và ký hiệu cần hiểu

- **ServerArgs:** Tham số cấu hình server runtime, điều khiển graph policy, giới hạn admission và hành vi khác.
- **Prefill graph policy:** Quy định các shape xử lý prompt nào được capture/chạy bằng GPU graph.
- **Max running requests:** Giới hạn phía server cho request được nhận/đang chạy đồng thời; khác concurrency client.
- **Harness / protocol quan sát:** Quy trình client và đo lường xác định warmup, cửa sổ điểm và cách tính.
- **Yếu tố gây nhiễu:** Yếu tố cùng thay đổi với phép so và cũng ảnh hưởng kết quả, khiến không thể quy cho một nguyên nhân.

### Cách diễn giải số liệu hoặc sơ đồ

- N64 đầy đủ lịch sử trung bình 3.044,400475, trong khi control ngắn mới xấp xỉ 2.560. ServerArgs thực tế cho thấy policy prefill graph và giới hạn max-running-request đã đổi; harness và điều kiện quan sát cũng khác.
- Replay vận hành legacy chính xác 26313 đạt 2.830,923547; run native-runtime đầy đủ 26766 đạt 3.045,501509. Factorial graph/admission đã hoàn tất nhưng không xác định một nguyên nhân hữu ích duy nhất. Vì vậy không thể ghi toàn bộ chênh lệch cho việc phục hồi một flag hay chỉ đổi launcher.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Điểm số khác nhau giữa chuỗi full lịch sử, control ngắn, replay legacy và native runtime; nhiều setting và điều kiện đo cùng thay đổi.
- **Giả thuyết:** Graph policy, giới hạn admission server, runtime hoặc harness đo có thể góp phần tạo drift.
- **Kết luận được hỗ trợ:** Giữ kết quả thấp hợp lệ và ghi rõ protocol/runtime; chưa xác lập giải thích một yếu tố.
- **Chưa biết / giới hạn:** Bằng chứng factorial không cô lập được yếu tố nhân quả duy nhất đủ giải thích chênh lệch lịch sử với kết quả mới.

### Lời nói mẫu

Control ngắn mới đạt khoảng 2.560, thấp hơn trung bình N64 đầy đủ lịch sử 3.044. Kiểm tra server settings thực tế cho thấy cả policy prefill graph lẫn giới hạn request phía server đã đổi; harness và cửa sổ đo cũng khác. Replay legacy và run native mới trả lời so sánh khác nhau, còn factorial hoàn tất không cô lập được nguyên nhân. Vì vậy chúng tôi báo drift cùng yếu tố gây nhiễu, không ghi công cho một flag hay launcher riêng.

### Điều không nên nói

Control ngắn không so trực tiếp với run đầy đủ. Replay legacy chính xác không chứng minh một flag duy nhất gây ra chênh lệch.

### Câu chuyển slide

Các phép đo xuyên nền tảng đặt ra câu hỏi độ vững khác: calibration trên accelerator này có dự báo được accelerator kia không?

---

<a id="slide-16"></a>

## Slide 16 — Can one platform predict another reliably?

**Phần cứng: H100 là dữ liệu dự báo; H200 là phép đo kiểm chứng.**

### Nói nhanh · 10–20 giây

Tỷ số H200/H100 N52 là 1,1881. Dự báo khóa trước cho H200 N50 sai −1,5371 phần trăm, trong dung sai ±2 của nhóm nhưng ngoài sensitivity range chưa đầy đủ. Một phép thử không xác nhận quy đổi phổ quát.

![Slide 16](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-16.png)

### Slide muốn nói gì

Đánh giá dự báo xuyên nền tảng mà không sửa nó sau khi thấy kết quả kiểm tra. Bằng chứng ủng hộ một phép kiểm tra vận hành gần kề, đồng thời cho thấy sensitivity range trước đó bỏ sót một nguồn bất định dự báo.

### Giải thích kết quả và lập luận

Ở cùng combo N52, H100 trung bình 2.215,460 good tokens/s trên hai allocation; H200 2.632,181 trên bốn; tỷ số H200/H100 = 1,188096805. Dùng tỷ số với trung bình H100 N50 để khóa dự báo H200 N50 là 2.642,244. Job held-out 24272 đo 2.601,629, sai số −1,5371%, nằm trong dung sai ±2% do nhóm đặt nhưng ngoài sensitivity range đầu vào trước đó.

### Thuật ngữ và ký hiệu cần hiểu

- **Allocation:** Một lần scheduler cấp tài nguyên/run; số allocation không phải số loại phần cứng hay chắc chắn số thiết bị riêng.
- **Tỷ số calibration:** Trung bình H200 chia H100 trong cùng cấu hình N52; không đơn vị và chỉ đúng phạm vi setting đó.
- **Kết quả held-out:** Phép đo không dùng tính dự báo, chỉ xem sau đó để kiểm tra khả năng chuyển sang quan sát mới.
- **Sensitivity range:** Khoảng tạo khi thay đổi một số đầu vào; ở đây bỏ sai số mô hình nên không phải toàn bộ bất định dự báo.
- **Dung sai ±2%:** Khoảng chấp nhận vận hành do nhóm đặt trước; không phải khoảng tin cậy 95% hay thanh sai số đo.

### Cách diễn giải số liệu hoặc sơ đồ

- Tại N52, H100 trung bình 2.215,460 token/s qua hai allocation; H200 2.632,181 qua bốn. Tỷ số 1,188096805 là liên hệ hệ thống cho cùng combo này, không phải hệ số phần cứng phổ quát. Lặp allocation không chứng minh dùng GPU vật lý riêng.
- Trước khi có kết quả job H200 N50 24272, dự báo được khóa ở 2.642,244 good tokens/s. Kết quả đo là 2.601,629, sai số −1,5371%, trong dung sai vận hành ±2% do nhóm đặt trước. Tuy nhiên, kết quả nằm ngoài sensitivity range trước đó vì phạm vi đó thay đổi đầu vào nhưng bỏ model error. Không fit lại hệ số; độ tin cậy dự báo rộng chưa được chứng minh.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Một kết quả H200 N50 held-out thấp hơn dự báo 1,5371%: trong dung sai ±2% nhưng ngoài sensitivity range chưa đầy đủ.
- **Giả thuyết:** Tỷ số N52 có thể chuyển đủ tốt để dự báo operating point H200 N50 gần đó.
- **Kết luận được hỗ trợ:** Phép kiểm tra dự báo trước duy nhất này đạt dung sai vận hành của nhóm; vẫn giữ giới hạn thiếu model error.
- **Chưa biết / giới hạn:** Độ chính xác ở tải/cấu hình khác, bất định đầy đủ và quy tắc quy đổi H100-H200 phổ quát đều chưa biết.

### Lời nói mẫu

Chúng tôi đo cùng cấu hình N52 trên H100 và H200, được tỷ số 1,1881. Dùng nó để khóa dự báo H200 N50 trước khi job 24272 chạy. Dự báo 2.642,244; phép đo 2.601,629, sai số −1,5371 phần trăm, trong dung sai ±2 phần trăm đặt trước. Kết quả nằm ngoài sensitivity range cũ vì phạm vi đó bỏ sai số mô hình. Đây là một kiểm tra, không phải quy tắc quy đổi phổ quát.

### Điều không nên nói

Hai và bốn allocation là số lần lặp, không chứng minh thiết bị vật lý riêng. Dung sai ±2% không phải khoảng tin cậy; không fit lại sau khi xem held-out.

### Câu chuyển slide

Dịch vụ đạt latency vẫn có thể chưa rõ chất lượng câu trả lời; slide sau xác định ranh giới đó.

---

<a id="slide-17"></a>

## Slide 17 — What does passing latency leave unverified?

**Phần cứng: H200 · Firmus — số đo latency; chất lượng chính thức vẫn chưa xác minh.**

### Nói nhanh · 10–20 giây

H200 N64 đạt quy tắc latency kết hợp trên 98,580 phần trăm request. Kiểm tra nhỏ không xác minh yêu cầu riêng là đạt ít nhất 99 phần trăm reference, nên chất lượng model vẫn chưa rõ. Hai tiêu chí này cần phép đánh giá khác nhau, không thể thay thế nhau.

![Slide 17](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-17.png)

### Slide muốn nói gì

Tách hiệu năng dịch vụ khỏi chất lượng model. Đạt giới hạn latency trả lời câu hỏi dịch vụ phản hồi đủ nhanh không; không xác lập câu trả lời sinh ra có đạt ngưỡng quality full-set của ban tổ chức hay không.

### Giải thích kết quả và lập luận

Đọc ba mức bằng chứng: H200 job 26766 đạt latency kết hợp 98,580442%; smoke do nhóm chạy 7/8 không có regression mới và retrieval 12/12; yêu cầu quality official tối thiểu 99% reference vẫn chưa xác minh. Kiểm tra nhỏ chỉ dò regression, không thay đánh giá quality full-set bắt buộc.

### Thuật ngữ và ký hiệu cần hiểu

- **SLA latency đồng thời:** Quy tắc cấp request đòi đạt cả giới hạn TTFT và ITL trung bình/request.
- **Smoke / retrieval check:** Kiểm tra regression và retrieval quy mô nhỏ do nhóm chạy trong môi trường H200 được cấp; không phải đánh giá accuracy full-set theo quy trình của ban tổ chức.
- **Quality model official:** So sánh do ban tổ chức quy định giữa câu trả lời model với reference trên toàn bộ tập đánh giá.
- **99% reference:** Mức tối thiểu so với chuẩn quality official; hiện chưa đo được.
- **Trọng số FP8 / activation-KV BF16:** Định dạng số giữ trong đường model được chọn; riêng định dạng không chứng nhận chất lượng trả lời.

### Cách diễn giải số liệu hoặc sơ đồ

- Job N64 đầy đủ 26766 đạt SLA latency đồng thời 98,580442%. Smoke do nhóm chạy là 7/8, không phát hiện regression mới; retrieval là 12/12. Bộ kiểm tra nhỏ này không ước lượng điểm full-set của ban tổ chức.
- Ngưỡng quality bắt buộc là ít nhất 99% reference trên đánh giá official và hiện vẫn chưa biết. Primary giữ trọng số FP8 cùng activation/KV BF16; không dùng KV lượng tử hóa hay speculative decoding. Kết quả latency không tạo chứng nhận accuracy hay ranking từ ban tổ chức.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Chấp nhận latency và kiểm tra regression nhỏ đạt trong phạm vi đã nêu; quality full-set official chưa xác minh.
- **Giả thuyết:** Tách thay đổi model khỏi thay đổi serving giúp đo throughput mà không nhập nhằng với ảnh hưởng tới chất lượng câu trả lời.
- **Kết luận được hỗ trợ:** Báo latency dịch vụ và quality model official như hai câu hỏi riêng; chỉ khẳng định latency đã đo.
- **Chưa biết / giới hạn:** Hệ thống có đạt ít nhất 99% reference trong đánh giá official đầy đủ hay không vẫn chưa biết.

### Lời nói mẫu

Kết quả này đo hành vi dịch vụ, không đo accuracy câu trả lời. Job H200 26766 đạt cả hai giới hạn latency với 98,580 phần trăm request. Smoke và retrieval nhỏ không có regression mới trong phạm vi ít trường hợp. Yêu cầu riêng của ban tổ chức là ít nhất 99 phần trăm reference trên đánh giá quality đầy đủ; chúng tôi chưa xác minh điều đó. Vì vậy báo cáo latency đạt, không tuyên bố quality official hay ranking.

### Điều không nên nói

Không gọi 7/8 hoặc 12/12 là điểm chất lượng. Đạt SLA latency không đồng nghĩa câu trả lời đúng hay được ban tổ chức chấp nhận.

### Câu chuyển slide

Câu hỏi bằng chứng cuối là deployment đóng gói có chạy trọn từ khởi động đến xử lý kết quả không.

---

<a id="slide-18"></a>

## Slide 18 — Does the packaged deployment complete end to end?

**Phần cứng: H200 chạy benchmark; CPU chỉ kiểm reader trên dữ liệu đã lưu.**

### Nói nhanh · 10–20 giây

Hai job portable H200 thật hoàn tất serving nhưng lỗi khi đọc kết quả. Job zero-GPU xác minh reader đã sửa trên export thật. Điều này chưa chứng minh deployment đầy đủ sau sửa; hai job ban đầu vẫn thất bại.

![Slide 18](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-18.png)

### Slide muốn nói gì

Phân biệt suy luận GPU thành công với đóng gói đầu-cuối thành công. Hai allocation portable thật hoàn thành serving nhưng lỗi khi reader tìm và đọc kết quả; kiểm tra CPU-only sau đó xác nhận sửa reader, không phải xác nhận một allocation GPU đầy đủ đã sửa.

### Giải thích kết quả và lập luận

Theo dõi pipeline theo thứ tự: job portable thật 27136 và 27145 chạy GPU client chính thức và cả hai route P/D ngữ nghĩa, rồi lỗi ở bước xử lý kết quả. Bản sửa đầu xử lý export nằm trong thư mục con trực tiếp; bản sửa sau chuẩn hóa input root khi /scratch/home và /home cùng trỏ tới file. Job compute zero-GPU 27152 chạy qua cả hai reader sửa trên cả hai dataset thật. Giữ trạng thái scheduler gốc là FAILED.

### Thuật ngữ và ký hiệu cần hiểu

- **Deployment đầu-cuối:** Toàn tuyến từ khởi chạy server/route, official load client, export dữ liệu tới tạo kết quả đã review.
- **Route P/D ngữ nghĩa:** Đường dịch vụ prefill và decode; cả hai đã hoàn tất trong job GPU thật.
- **Result reader:** Code hậu xử lý tìm file export, phân tích file và tính summary.
- **Canonical path:** Danh tính filesystem đã resolve; /home và /scratch/home có thể là alias cùng vị trí dữ liệu.
- **Xác minh compute-only:** Job CPU kiểm tra reader đã sửa trên export thật mà không khởi chạy lại dịch vụ GPU.

### Cách diễn giải số liệu hoặc sơ đồ

- Job portable H200 thật 27136 và 27145 hoàn tất cả hai route dịch vụ và official client, nhưng job scheduler thất bại khi hậu xử lý. Ở 27136, AIPerf 0.12 đặt export trong thư mục con trực tiếp; bản sửa đầu xử lý layout đó. Ở 27145, đường /home dạng từ vựng và /scratch/home canonical gây mismatch alias; chuẩn hóa root khắc phục lỗi thứ hai.
- Job zero-GPU 27152 sau đó chạy reader đã sửa trên cả hai dataset thật và đạt. Điểm raw 3.055,330517 của 27145 là bằng chứng khôi phục từ job gốc thất bại, không phải lần chạy lại toàn allocation thành công sau sửa. Không tuyên bố deployment GPU đầy đủ sau sửa.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Hai job GPU thật hoàn tất inference và client nhưng lỗi đọc kết quả; job CPU-only 27152 xác minh hai sửa reader trên output thật.
- **Giả thuyết:** Lỗi còn lại của deployment đến từ giả định sai về layout file và alias đường dẫn ở hậu xử lý, không phải serving execution.
- **Kết luận được hỗ trợ:** Hai lỗi reader cụ thể đã sửa và xác minh trên dataset thật; deployment đầy đủ sau sửa vẫn chưa được xác nhận.
- **Chưa biết / giới hạn:** Chưa biết allocation mới có đi qua toàn bộ launch, inference, export, reader và các gate sau khi sửa hay không.

### Lời nói mẫu

Hai job portable GPU thật hoàn tất route prefill, decode và official client, nhưng đều lỗi khi hậu xử lý đọc export. Một reader tìm sai tầng thư mục; reader kia nhầm hai alias đường dẫn của cùng file. Chúng tôi sửa cả hai và kiểm tra reader trên output thật bằng job CPU zero-GPU. Việc đó xác nhận sửa reader, không xác nhận allocation GPU đầy đủ sau sửa. Hai job scheduler gốc vẫn giữ trạng thái thất bại.

### Điều không nên nói

Không báo 3.055,330517 là deployment đầy đủ thành công. Job gốc thất bại; kiểm tra reader CPU không chạy lại GPU inference hay allocation đầy đủ.

### Câu chuyển slide

Nhìn chung, các slide trả lời bốn câu hỏi: chọn topology có số đo, thử tương tác giới hạn hiệu năng, chỉ giữ gain hữu ích và giới hạn tuyên bố về tính lặp lại/chất lượng.

---

<a id="slide-19"></a>

## Slide 19 — Four decisions, each with an evidence boundary

**Phần cứng: H200 là kết quả chính; H100 được báo riêng.**

### Nói nhanh · 10–20 giây

Bốn quyết định theo bằng chứng là giữ bố trí GPU chạy được, kiểm thử thay vì đoán bottleneck, chỉ giữ thay đổi giúp dịch vụ đạt chuẩn và ưu tiên kết quả đã chạy lại. N 64 lịch sử trung bình khoảng 3044 token đạt chuẩn mỗi giây. Chất lượng chính thức và kiểm chứng triển khai đầy đủ sau sửa vẫn còn mở.

![Slide 19](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-19.png)

### Slide muốn nói gì

Trả lời bốn câu hỏi bằng quyết định và giới hạn bằng chứng đỡ cho từng quyết định.

### Giải thích kết quả và lập luận

Bố trí GPU là lựa chọn chạy được trên 16 H 200; profile gợi ý chứ chưa chứng minh mọi bottleneck; giữ thay đổi có mức tăng dịch vụ hữu ích trong so sánh phù hợp; các lần N 64 lặp lại hỗ trợ một điểm vận hành. Chất lượng chưa xác minh, phần cứng chưa đa dạng và phát lại portable đầy đủ chưa xong giới hạn tuyên bố về độ bền vững.

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

Bốn quyết định theo bằng chứng là giữ bố trí GPU chạy được, kiểm thử thay vì đoán bottleneck, chỉ giữ thay đổi giúp dịch vụ đạt chuẩn và ưu tiên kết quả đã chạy lại. N 64 lịch sử trung bình khoảng 3044 token đạt chuẩn mỗi giây. Chất lượng chính thức và kiểm chứng triển khai đầy đủ sau sửa vẫn còn mở.

### Điều không nên nói

Luôn kèm đơn vị và cấu hình; không nêu giả thuyết như nguyên nhân đã đo.

### Câu chuyển slide

Slide cuối nêu việc vòng tiếp theo phải chứng minh; hiện nghiên cứu đã dừng.

---

<a id="slide-20"></a>

## Slide 20 — What should the next iteration establish?

**Phần cứng: Đề xuất xác minh — chưa có job hay số đo mới.**

### Nói nhanh · 10–20 giây

Vòng sau nên khép ba khoảng trống: chất lượng model chính thức, chạy trọn bản đóng gói sau sửa reader và đo từng pha trước khi khẳng định bottleneck. Trước mắt giữ dịch vụ 64 request đã có phép đo lặp. Đây là việc đề xuất để xác minh; báo cáo này không khởi chạy thí nghiệm mới.

![Slide 20](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-20.png)

### Slide muốn nói gì

Để đề xuất tiếp theo xuất phát từ điều chưa chứng minh, thay vì chỉ chạy thêm để tăng số điểm.

### Giải thích kết quả và lập luận

Đánh giá chất lượng toàn tập chính thức mới trả lời yêu cầu accuracy. Phát lại portable đầy đủ mới kiểm triển khai sau sửa reader. Muốn tuyên bố lợi ích compile hay bottleneck cần đường model tương thích và đo thời gian từng pha có kiểm soát. Đây là đề xuất, không phải job đã gửi.

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

Vòng sau nên khép ba khoảng trống: chất lượng model chính thức, chạy trọn bản đóng gói sau sửa reader và đo từng pha trước khi khẳng định bottleneck. Trước mắt giữ dịch vụ 64 request đã có phép đo lặp. Đây là việc đề xuất để xác minh; báo cáo này không khởi chạy thí nghiệm mới.

### Điều không nên nói

Không khẳng định đã đạt độ chính xác chính thức, đã phát lại serving portable đầy đủ sau sửa, graph thưa tăng goodput, hay giao diện compile đã được sửa.

### Câu chuyển slide

Kết phần AI chính tại đây; mở slide dự phòng phù hợp khi được hỏi. Phần HPC độc lập có mạch trình bày riêng.

---

<a id="slide-21"></a>

## Slide 21 — Backup · two platforms, separate experimental systems

**Phần cứng: H200 · Firmus + H100 · NSCC — hai môi trường riêng.**

### Nói nhanh · 10–20 giây

Cả hai hệ thống cấp mười sáu GPU và dùng cùng checkpoint Qwen cùng workload đã staging. Firmus dùng H200; NSCC dùng H100. Phần cứng, scheduler, container và điều kiện node khác nhau, nên đây là các phép đo riêng, không phải hệ số quy đổi GPU.

![Slide 21](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-21.png)

**Phần dự phòng AI: chỉ mở khi cần giải thích sâu hơn.**

### Slide muốn nói gì

Đặt ranh giới so sánh cho các kết quả nền tảng sau: cùng model và client giúp phép thử gần nhau hơn, nhưng không xóa khác biệt phần cứng và stack triển khai.

### Giải thích kết quả và lập luận

Bảng đối chiếu phân bổ GPU, scheduler, công cụ chạy container, phần mềm serving/client và model. Các hàng giống nhau là điểm kiểm soát hữu ích: cả hai có hai node tám GPU và dùng cùng artifact đã staging cùng checkpoint Qwen3-235B FP8. Các hàng khác nhau có thể ảnh hưởng độ trễ và thông lượng. Slurm và PBS cấp tài nguyên; chúng không thực thi suy luận model. Pyxis/Enroot và Singularity là đường chạy container khác nhau; SGLang phục vụ request còn AIPerf tạo và đo lưu lượng client. Vì vậy mỗi điểm số cần gắn với nền tảng, topology, backend và tải.

### Thuật ngữ và ký hiệu cần hiểu

- **Firmus / NSCC ASPIRE 2A+:** Hai địa điểm tính toán riêng: Firmus cấp node H200; NSCC ASPIRE 2A+ cấp node H100.
- **2 × 8 H200 / 2 × 8 H100:** Hai node, mỗi node tám GPU, tổng cộng mười sáu GPU mỗi allocation. Mẫu GPU và hệ thống khác nhau.
- **Slurm / PBS:** Scheduler cấp phát và quản lý job tính toán; không phải engine phục vụ model.
- **Pyxis / Enroot / Singularity:** Công cụ khởi chạy container. Container đóng gói phần mềm, nhưng launcher và host khác nhau vẫn có thể ảnh hưởng thực thi.
- **SGLang / AIPerf:** SGLang chạy serving model; AIPerf gửi request benchmark và ghi chỉ số dịch vụ.
- **checkpoint FP8:** Trọng số model chung dùng biểu diễn số dấu phẩy động tám bit; dùng chung trọng số không làm hai lần chạy GPU tương đương.
- **so sánh nền tảng:** So sánh toàn hệ thống. Cần workload khớp cùng thông tin phần cứng, phần mềm, topology và thời gian; tên GPU không phải hệ số quy đổi.

### Cách diễn giải số liệu hoặc sơ đồ

- Các điểm kiểm soát chung là phân bổ hai node, mười sáu GPU, artifact serving/client đã staging và checkpoint Qwen.
- Khác biệt gồm thế hệ GPU H200 so với H100, Slurm so với PBS, và launcher container khác nhau. CPU, driver, mạng, cache node và vị trí tiến trình cũng có thể khác.
- Bảng cung cấp bối cảnh; nó không phải kết quả hiệu năng có kiểm soát và không định lượng đóng góp riêng của từng khác biệt.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Cả hai site cấp mười sáu GPU trên hai node và dùng chung image đã staging cùng checkpoint, nhưng khác họ GPU, scheduler, launcher và môi trường host.
- **Giả thuyết:** Khớp model và workload request là cần thiết, nhưng khác biệt nền tảng vẫn có thể ảnh hưởng số đo serving.
- **Kết luận được hỗ trợ:** Báo cáo kết quả từng nền tảng riêng và ghi rõ điều kiện triển khai.
- **Chưa biết / giới hạn:** Bảng không cô lập tác động của khác biệt nền tảng nào và không đưa ra hệ số đổi điểm H100 sang H200.

### Lời nói mẫu

Chúng tôi đo trên hai hệ thống, mỗi hệ thống có mười sáu GPU. Firmus dùng H200, Slurm và container Enroot; NSCC ASPIRE 2A+ dùng H100, PBS và Singularity. Cả hai dùng cùng checkpoint và artifact benchmark đã staging, nhưng driver, mạng, cache máy chủ và đường khởi chạy vẫn có thể khác. Vì vậy slide này mô tả môi trường thí nghiệm, không so tốc độ. Mỗi điểm số cần ghi nền tảng và cài đặt riêng.

### Điều không nên nói

Không gộp số đo H100 và H200 thành một chuỗi hoặc suy ra tốc độ chỉ từ mẫu GPU hay dung lượng bộ nhớ.

### Câu chuyển slide

Phần tiếp theo giải thích ràng buộc tương thích cụ thể do cách chia trọng số trên H200.

---

<a id="slide-22"></a>

## Slide 22 — Backup · FP8 geometry constrains a topology

**Phần cứng: H200 · đường FP8 đã thử; phép tính block không phải số đo tốc độ.**

### Nói nhanh · 10–20 giây

Phân vùng TP8/EP1 thất bại có 192 phần tử, dư 64 so với block FP8 rộng 128. EP2 đổi phép chia hiệu dụng thành 384 phần tử, vừa ba block đầy. Điều này sửa sai hình dạng tensor, chưa chứng minh serving nhanh hay đúng.

![Slide 22](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-22.png)

### Slide muốn nói gì

Giải thích lỗi tương thích cụ thể từ hình học trọng số của model và phân biệt cách chia có thể tải với triển khai đã qua kiểm tra dịch vụ.

### Giải thích kết quả và lập luận

Bắt đầu từ chiều trung gian MoE gồm 1.536 phần tử, rồi chia cho tensor-parallel hiệu dụng. TP8/EP1 cho 1.536 ÷ 8 = 192. Kernel đã thử cần block FP8 nguyên 128 phần tử, nên 192 gồm một block đầy cộng 64 phần tử dư không thể tải. TP8/EP2 đổi tensor parallelism MoE hiệu dụng thành bốn: 1.536 ÷ 4 = 384, vừa đúng ba block đầy. Phần dư màu đỏ biểu thị lỗi tương thích lúc tải, không phải mất token đầu ra. Phép tính giải thích vì sao hình dạng cũ lỗi và hình dạng thay thế tương thích; đây không phải biểu đồ benchmark.

### Thuật ngữ và ký hiệu cần hiểu

- **block FP8:** Nhóm cố định 128 phần tử trọng số mà đường kernel đã thử yêu cầu. Phân vùng kết thúc giữa block thì đường này không tải được.
- **MoE:** Mixture of Experts: tầng model định tuyến token tới các mạng con chuyên gia. Expert parallelism thay đổi cách phân phối các chuyên gia đó.
- **TP8 / EP1:** Tensor parallelism tám phần, một phân vùng chuyên gia. Tensor split MoE hiệu dụng là tám, tạo 192 phần tử mỗi phân vùng.
- **TP8 / EP2:** Tensor parallelism tám phần, hai phân vùng chuyên gia. Tensor split MoE hiệu dụng là bốn, tạo 384 phần tử mỗi phân vùng.
- **128 + 64:** Shard TP8/EP1 gồm một block đầy 128 cộng 64 phần tử dư, gây lỗi tải trong đường đã thử.
- **3 × 128 = 384:** Shard EP2 có ba block đầy. Cách chia giữ nguyên mọi trọng số và chuyên gia; chỉ thay đổi phân vùng.
- **tương thích và hiệu năng:** Tương thích nghĩa là hình dạng tensor đáp ứng đầu vào kernel. Khởi động, độ trễ, chất lượng đầu ra và thông lượng vẫn phải đo riêng.

### Cách diễn giải số liệu hoặc sơ đồ

- Hai phép tính là bằng chứng chính: TP8/EP1 tạo 192 phần tử; TP8/EP2 tạo 384.
- Phần dư 64 phần tử giải thích vì sao đường đầu tiên lỗi khi tải. EP2 bỏ phần dư bằng cách phân phối lại chuyên gia, không đổi độ chính xác hay kích thước model.
- Dòng cuối nhắc các bằng chứng còn cần sau tương thích: khởi động thành công, kiểm tra độ trễ dịch vụ và kiểm tra chất lượng đầu ra.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** TP8/EP1 cho phân vùng 192 phần tử, không chia hết theo block rộng 128; TP8/EP2 cho 384 phần tử, vừa ba block.
- **Giả thuyết:** Đổi phân vùng chuyên gia có thể làm trọng số FP8 hiện có tương thích với kernel mà vẫn giữ nguyên nội dung model.
- **Kết luận được hỗ trợ:** EP2 sửa hình học block đã thử và cho phép thử triển khai tương thích; đây là thay đổi bố trí kết hợp, không phải tăng tốc TP riêng lẻ.
- **Chưa biết / giới hạn:** Căn chỉnh đúng chưa xác nhận toàn bộ khởi động, SLA request, chất lượng đầu ra hay thông lượng tăng.

### Lời nói mẫu

Chiều trung gian model có 1.536 phần tử, còn kernel FP8 này yêu cầu block đủ 128. Với TP8 và một phân vùng chuyên gia, mỗi shard có 192 phần tử: 128 cộng 64 dư, nên tải lỗi. Với hai phân vùng chuyên gia, phép chia hiệu dụng là bốn và mỗi shard có 384, đúng ba block. Trọng số và chuyên gia vẫn giữ nguyên; chỉ đổi cách phân phối. Đây là hình dạng tương thích, chưa chứng minh dịch vụ đầy đủ nhanh hay đúng.

### Điều không nên nói

Số 64 màu đỏ là phần dư của trọng số, không phải GPU hay token. Không gọi tương thích là kết quả thông lượng hoặc tăng tốc TP riêng.

### Câu chuyển slide

Backup tiếp theo dùng biểu đồ lịch sử để chỉ ra cách chiến dịch đi tới các điểm vận hành về sau.

---

<a id="slide-23"></a>

## Slide 23 — Backup · historical milestones behind the decisions

**Phần cứng: H200 · Firmus — tất cả cột lịch sử.**

### Nói nhanh · 10–20 giây

Biểu đồ H200 tăng từ 1.297 token tốt/giây ở N32 lên trung bình N64 là 3.044. Nó cho thấy các điểm vận hành đo được tốt hơn, nhưng mỗi mốc đổi tải hoặc cấu hình nên không quy được mức tăng cho từng tối ưu.

![Slide 23](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-23.png)

### Slide muốn nói gì

Dùng biểu đồ lịch sử làm bối cảnh cho câu hỏi nghiên cứu: nó cho thấy các điểm vận hành nào dẫn tới phép thử có kiểm soát sau này, đồng thời giải thích vì sao chuỗi tăng dần không phải thí nghiệm nhân quả tích lũy.

### Giải thích kết quả và lập luận

Trục ngang liệt kê mốc có tên, không phải ngày tháng hay khoảng thời gian đều nhau. Trục dọc là token đầu ra tốt mỗi giây; cột cao hơn nghĩa là nhiều request đạt giới hạn độ trễ hơn trong workload của mốc đó. Màu xám chỉ layout ban đầu, xanh chỉ chuyên biệt hóa backend, cam chỉ tinh chỉnh và lặp về sau. Biểu đồ đi từ 1.297 ở N32 và 1.666 ở N40, qua 1.912 ở N48 và 2.631 ở N52, tới trung bình N64 lịch sử đã làm tròn là 3.044. Vì concurrency, bố trí worker, backend và điều kiện runtime đổi theo các mốc, biểu đồ cho thấy nhóm tìm được cấu hình đo tốt hơn; nó không cho biết từng thay đổi gây ra bao nhiêu.

### Thuật ngữ và ký hiệu cần hiểu

- **good output tokens/s:** Số request đủ điều kiện mỗi giây nhân 200 token đầu ra yêu cầu; giá trị cao hơn nghĩa là nhiều đầu ra hữu ích hơn theo giới hạn độ trễ.
- **biểu đồ mốc:** Lịch sử các điểm vận hành được phân nhóm. Khoảng cách ngang là phân loại, không phải thời gian; hai cột cạnh nhau chưa chắc là phép thử ghép cặp.
- **N32–N64:** Mức request đồng thời mục tiêu của client, không phải số GPU. Tăng N đổi tải đưa vào và có thể đổi độ trễ cùng thông lượng hữu ích.
- **điểm lặp:** Cấu hình được đo lại để kiểm tra khả năng tái lập. Lần lặp kiểm tra độ ổn định, không cô lập nguyên nhân của mức tăng trước đó.
- **ablation nhân quả:** So sánh đổi một yếu tố đã định nghĩa trong khi giữ yếu tố khác đủ ổn định. Biểu đồ lịch sử không phải ablation tích lũy như vậy.

### Cách diễn giải số liệu hoặc sơ đồ

- Các mốc là 1.297 (07 ban đầu/N32), 1.666 (09 ban đầu/N40), 1.912 (split/N48), 2.631 (FlashInfer cộng MNNVL/N52), 2.716 (DeepGEMM prefill/N56), 2.939 (DeepGEMM cộng HPC-Ops/N58), 2.989 (N60 lặp), 3.023 (N62 lặp) và 3.044 (ba lần N64 lịch sử). Nhãn đã làm tròn.
- Các lần N62 về sau đạt 3,022.034919 và 3,023.072304; hai lần N64 lặp đạt 3,044.489701 và 3,044.074628. Chúng hỗ trợ độ lặp lại ở các cài đặt đó, không xác lập tối ưu phổ quát hay nguyên nhân cho từng bước.
- Màu sắc nhóm giai đoạn công việc, không biểu thị đạt/trượt. Chiều cao cột là điểm đo, không phải khoảng tin cậy.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Thông lượng token đầu ra tốt tăng qua các điểm vận hành có tên, từ 1.297 ở N32 tới khoảng 3.044 ở N64 lịch sử.
- **Giả thuyết:** Khôi phục split và đường truyền dùng được, rồi chuyên biệt hóa attention, collective, prefill và decode, có thể giúp tìm cấu hình mạnh hơn.
- **Kết luận được hỗ trợ:** Biểu đồ là bản đồ mốc và đích lặp về sau; nó không chứng minh các tối ưu nêu tên cộng lại tạo toàn bộ mức tăng.
- **Chưa biết / giới hạn:** Tải, topology, runtime và điều kiện quan sát thay đổi; chưa xác lập đóng góp nhân quả riêng hay tối ưu toàn cục.

### Lời nói mẫu

Biểu đồ tóm tắt hành trình H200 từ khoảng 1.300 token tốt mỗi giây ở N32 lên khoảng 3.044 ở N64. Trục ngang ghi mốc, không phải ngày; trục dọc là tốc độ đầu ra đạt giới hạn độ trễ. Màu sắc nhóm giai đoạn nghiên cứu. Nhưng tải và cài đặt phần mềm đổi giữa các cột, nên đây là lịch sử điểm đo tốt hơn, không chứng minh mỗi tối ưu gây ra toàn bộ mức tăng.

### Điều không nên nói

Không đọc khoảng cách ngang như thời gian, cộng chênh lệch cột thành gain độc lập, hay hiểu màu là đạt/trượt. N là concurrency request, không phải số GPU.

### Câu chuyển slide

Backup tiếp theo ghép hai quan sát H100 riêng để giải thích đánh đổi khi đổi attention decode.

---

<a id="slide-24"></a>

## Slide 24 — Backup · request-scoped descriptor construction

**Phần cứng: CPU — phép kiểm hình học cho đường truyền hetero-TP trên H200.**

### Nói nhanh · 10–20 giây

Bản vá tạo descriptor cho các trang KV cần thiết rồi gộp dải liên tục, đồng thời giữ nguyên ánh xạ và stride. Kiểm tra CPU đạt 720 trường hợp hình học; fixture ghi rõ chưa xác minh truyền GPU thật.

![Slide 24](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-24.png)

### Slide muốn nói gì

Mô tả chính xác thay đổi và đặt bằng chứng đúng ở cấp độ của nó. Bản vá đổi phạm vi descriptor và cách gộp trong đường truyền TP khác nhau, đồng thời giữ hành vi ánh xạ liên quan; kiểm tra tương đương trên CPU không đồng nghĩa đã xác minh truyền thật trên GPU.

### Giải thích kết quả và lập luận

Đây là bước 5 và nửa đầu bước 6 trong chuỗi bảy bước: thay đổi cụ thể, rồi cổng đúng đắn thực sự đã chạy. Cần giữ rõ khác biệt giữa tương đương dải địa chỉ và truyền GPU thật.

### Thuật ngữ và ký hiệu cần hiểu

- **request-scoped descriptors:** Tạo metadata truyền chỉ cho các trang KV mà yêu cầu hiện tại cần, thay vì liệt kê cả pool KV.
- **coalesce contiguous ranges:** Gộp các dải bộ nhớ liền kề thành ít descriptor hơn nhưng vẫn giữ đúng vị trí và bước nhảy cần cho truyền dữ liệu.
- **KV head mapping:** Ánh xạ KV head nguồn sang dải peer decode; metadata bản vá ghi rằng ánh xạ này được giữ nguyên.
- **per-token stride:** Khoảng cách giữa các vị trí dữ liệu gắn với token khi chỉ gửi một lát KV head; phải giữ đúng sau khi gộp.
- **720 cases:** Số trường hợp tương đương byte-range giữa hình học CPU code cũ và mới đã được giữ lại và vượt qua.
- **real GPU transport: false:** Fixture hình học lưu rõ rằng nó không xác minh một lần truyền GPU thật.
- **notifications:** Tín hiệu báo hoàn tất truyền được giữ nguyên trong phạm vi bản vá; đây không phải yếu tố thí nghiệm bị đổi.

### Cách diễn giải số liệu hoặc sơ đồ

- Bước 5 — Can thiệp: thay việc liệt kê descriptor nguồn và đích cho toàn pool bằng descriptor theo yêu cầu, sau đó gộp các dải liên tục.
- Phạm vi bản vá giữ nguyên hành vi TP bằng nhau, trọng số, độ chính xác, ánh xạ KV head, stride theo token khi gửi lát head và thông báo hoàn tất.
- Bước 6, phần đúng đắn: 720 trường hợp hình học CPU so sánh code cũ và mới vượt kiểm tra tương đương byte-range.
- Fixture ghi xác minh truyền GPU thật là false. Vì vậy, kiểm tra ánh xạ CPU chưa chứng minh truyền GPU, server sẵn sàng hay phản hồi hợp lệ.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Bản vá triển khai chuẩn bị descriptor theo yêu cầu và gộp dải liền kề; 720 trường hợp CPU đã lưu vượt kiểm tra tương đương dải, gồm ví dụ yêu cầu liên tục có 188 descriptor.
- **Giả thuyết:** Nếu giữ nguyên ánh xạ nhưng bỏ các dải toàn pool không liên quan, bước setup có thể làm ít việc descriptor hơn mà không đổi byte KV yêu cầu cần.
- **Kết luận được hỗ trợ:** Fixture CPU hỗ trợ tính tương đương địa chỉ và byte-range cho các hình học đã thử. Đây là cổng đúng đắn cho ánh xạ, chưa phải xác minh triển khai đầy đủ.
- **Chưa biết / giới hạn:** Fixture chưa xác minh truyền GPU thật. Nó cũng không đo thời gian tạo descriptor cũ và mới hoặc xác lập thay đổi này một mình đã giải quyết timeout trước đó.

### Lời nói mẫu

Bản vá thay đổi phạm vi chuẩn bị descriptor. Thay vì liệt kê dải nguồn và đích cho cả pool KV, nó tạo descriptor cho yêu cầu hiện tại rồi gộp các dải liền kề. Metadata ghi rằng truyền TP bằng nhau, trọng số mô hình, độ chính xác, ánh xạ KV head, stride theo token cần thiết và thông báo truyền vẫn được giữ nguyên. Sau đó, chúng tôi kiểm tra hành vi địa chỉ và byte-range giữa bản gốc với bản vá trên CPU qua 720 trường hợp hình học. Các kiểm tra đó hỗ trợ tính đúng của ánh xạ đã thử. Fixture được lưu rõ là chưa xác minh truyền GPU thật. Vì thế bước này chưa chứng minh bản sao GPU chạy được, server đã sẵn sàng hay yêu cầu trả về đầu ra hợp lệ. Đây là một cổng đúng đắn trong chuỗi, chưa phải kết quả đầu cuối.

### Điều không nên nói

Không gọi 720 trường hợp hình học CPU là 720 lần truyền GPU. Không nói bản vá đổi mọi kiểu truyền NIXL hoặc thay đổi trọng số/độ chính xác.

### Câu chuyển slide

Slide cuối của chuỗi nêu điều gì đã xảy ra trong lần chạy có bản vá và điều gì về tăng tốc, quan hệ nhân quả vẫn chưa được đo.

---

<a id="slide-25"></a>

## Slide 25 — Backup · what the KV recovery run actually proves

**Phần cứng: H200 · Firmus — job 22271 và 22294 trên cùng nhánh topology.**

### Nói nhanh · 10–20 giây

Job 22294 có bản vá warmup cặp mất 0,68–0,70 giây mỗi yêu cầu; benchmark N32 đạt 1.422,96 good tokens/s, SLA kết hợp 95,87% và không có lỗi. Chưa có đối chứng cùng topology để đo mức tăng tốc trong lần này.

![Slide 25](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-25.png)

### Slide muốn nói gì

Khép chuỗi bảy bước bằng bằng chứng đầu cuối thật và giới hạn được nêu rõ. Topology TP khác nhau có bản vá đã hoàn tất warmup P/D và phép xác nhận N32 đầy đủ, nhưng không có lần chạy không bản vá tương đương thành công nên không thể quy mức tăng tốc cho quan hệ nhân quả.

### Giải thích kết quả và lập luận

Đây là bước 6 và 7: kết quả đường chạy thật, sau đó là quyết định và điều chưa biết. Nêu thời gian warmup, điểm benchmark, SLA kết hợp và không lỗi như kết quả của job 22294 có bản vá, không phải mức tăng tốc so sánh ghép cặp trực tiếp với 22271.

### Thuật ngữ và ký hiệu cần hiểu

- **job 22294:** Lần chạy có bản vá được lưu lại trên topology dị thể P8 TP8/EP2 sang D8 TP4/EP4 cùng nhánh.
- **0.68–0.70 seconds/request:** Thời gian warmup cặp quan sát được trên mỗi yêu cầu sau khi server sẵn sàng; không phải bộ định giờ riêng cho khởi tạo descriptor.
- **N32:** Mục tiêu concurrency 32 yêu cầu đang xử lý cho benchmark xác nhận đầy đủ.
- **1,422.96 good tokens/s:** Thông lượng token đầu ra đạt chuẩn đo được trong xác nhận đầy đủ N32 trên topology có bản vá.
- **95.87% joint SLA:** Tỷ lệ yêu cầu được đánh giá đồng thời đạt giới hạn TTFT và mean ITL trong kết quả này.
- **zero errors/cancellations:** Kết quả xác nhận được lưu không báo lỗi yêu cầu hoặc yêu cầu bị hủy.
- **matched unpatched control:** Lần chạy tương đương nhưng không có bản vá, cần để quy chênh lệch hiệu năng cho bản vá; không có lần nào thành công trên đúng topology này.

### Cách diễn giải số liệu hoặc sơ đồ

- Bước 6, phần đầu cuối: job 22294 có bản vá hoàn tất cả hai đường warmup prefill/decode thật trong 0,68–0,70 giây mỗi yêu cầu sau khi worker sẵn sàng.
- Sau đó job hoàn tất xác nhận N32: 1.422,96 good output tokens/s, SLA kết hợp 95,87%, không lỗi và không hủy.
- Bước 7 — Quyết định: lần chạy chứng minh topology dị thể có bản vá khả thi và đã phục vụ yêu cầu theo giao thức benchmark cục bộ trong lần chạy này.
- Nó không xác lập mức tăng tốc độc lập của bản vá: không có đối chứng đầu cuối không bản vá thành công trên cùng topology, cũng không có bộ định giờ setup descriptor cũ/mới hay phân rã độ trễ nhân quả.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Job 22294 có bản vá hoàn tất warmup P/D trong 0,68–0,70 giây mỗi yêu cầu sau khi server sẵn sàng, rồi đạt 1422,96 good tokens/s ở N32 với SLA kết hợp 95,87%, không lỗi hay hủy.
- **Giả thuyết:** Setup descriptor theo yêu cầu có thể đã giúp topology trước đó bị chặn đạt trạng thái phục vụ, nhưng khác biệt giữa hai lần thử cũng có thể giải thích sự tương phản.
- **Kết luận được hỗ trợ:** Khẳng định có căn cứ là đường chạy có bản vá khả thi và có kết quả đầu cuối cho lần chạy P8 TP8/EP2 sang D8 TP4/EP4 này. Mức tăng tốc của bản vá chưa được đo.
- **Chưa biết / giới hạn:** Không có lần chạy không bản vá thành công được ghép cặp trên topology chính xác này; thời gian setup cũ-mới, mức sử dụng mạng, phân rã warmup nhân quả và phần goodput riêng do bản vá đóng góp đều chưa biết. Băng thông, bố trí KV, vị trí tài nguyên và bootstrap khác chưa bị loại trừ.

### Lời nói mẫu

Kết quả có bản vá mạnh hơn kiểm tra hình học CPU, nhưng cách diễn giải vẫn có giới hạn. Trong job 22294 trên H200 Firmus với layout TP khác nhau P8 TP8/EP2 sang D8 TP4/EP4, cả hai đường warmup prefill và decode thật đều hoàn tất trong 0,68 đến 0,70 giây mỗi yêu cầu sau khi worker sẵn sàng. Phép xác nhận đầy đủ N32 đo được 1.422,96 good output tokens mỗi giây, SLA kết hợp 95,87%, không lỗi và không hủy. Điều đó chứng minh topology có bản vá đã phục vụ yêu cầu trong lần chạy này. Nó không đo mức tăng tốc của bản vá: chúng tôi thiếu đối chứng không bản vá thành công trên cùng topology, thời gian descriptor cũ-mới tách riêng và phân rã độ trễ nhân quả. Mức dùng mạng, bố trí KV, vị trí tài nguyên và công việc bootstrap khác vẫn có thể liên quan.

### Điều không nên nói

Không lấy timeout 360 giây chia cho 0,68–0,70 giây rồi báo là mức tăng tốc. Baseline timeout không có AIPerf; lần chạy có bản vá là lần thử khác và thời gian setup chưa được tách riêng.

### Câu chuyển slide

Bài học của chuỗi bảy bước là đi từ triệu chứng đến giả thuyết dựa trên source, xác minh từng lớp, báo cáo kết quả đầu cuối rồi dừng kết luận đúng tại giới hạn của đối chứng hiện có.

---

<a id="slide-26"></a>

## Slide 26 — Backup · H100: first-token gain, goodput loss

**Phần cứng: H100 · NSCC · cặp decode N54; các đỉnh H100 khác báo riêng.**

### Nói nhanh · 10–20 giây

Trong một cặp H100 N54 khớp điều kiện, FA3 giảm TTFT trung bình từ 713,199 xuống 594,276 ms, nhưng goodput giảm từ 2.420,945 xuống 2.401,284 token/s, khoảng 0,812%. Token đầu đến nhanh hơn không cải thiện mục tiêu toàn request.

![Slide 26](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-26.png)

### Slide muốn nói gì

Giải thích vì sao chỉ nhìn thời gian token đầu có thể dẫn tới chọn sai backend decode: còn phải xét độ trễ của câu trả lời dài và thông lượng request đạt chuẩn.

### Giải thích kết quả và lập luận

Cặp thử chỉ đổi attention decode từ FlashInfer sang FA3, còn H100, tải N54 và phần đường thử khác được giữ khớp. So từng chỉ số: FA3 giảm TTFT trung bình 118,922 ms nhưng tăng ITL trung bình 0,773 ms. Lặp qua khoảng 199 khoảng token, phần tăng cộng lại khoảng 154 ms. Độ trễ request trung bình tăng từ 4.337,853 lên 4.372,813 ms, goodput giảm 0,812%. Vậy phản hồi ban đầu nhanh hơn nhưng toàn câu trả lời chậm hơn trung bình và ít request đạt chuẩn hơn mỗi giây. Đây là một cặp cho cấu hình decode H100 này, không phải xếp hạng thư viện attention nói chung.

### Thuật ngữ và ký hiệu cần hiểu

- **FA3:** FlashAttention-3, cách triển khai attention được thử cho decode ở đây. FA3 vẫn được dùng cho prefill H100 trong cặp này.
- **FlashInfer:** Cách triển khai attention decode làm đối chứng trong cặp khớp điều kiện.
- **TTFT:** Time to first token, thời gian từ lúc bắt đầu request đến khi token trả lời đầu tiên xuất hiện.
- **ITL:** Inter-token latency, khoảng thời gian giữa hai token sinh liên tiếp. Tăng nhẹ lặp qua câu trả lời dài có thể làm tổng thời gian tăng đáng kể.
- **goodput:** Tốc độ request đạt quy tắc độ trễ dịch vụ, đổi ra token đầu ra tốt/giây. Chỉ số này bao quát hơn độ trễ lúc bắt đầu.
- **H100 N54:** Hệ H100 với mục tiêu 54 request client đồng thời; không phải điểm vận hành H200 N64.
- **cặp khớp điều kiện:** Hai lần chạy chỉ có một thay đổi dự định, còn workload/cấu hình khác được căn chỉnh. Một cặp hỗ trợ so sánh cục bộ, không xếp hạng phổ quát.

### Cách diễn giải số liệu hoặc sơ đồ

- FlashInfer → FA3: token đầu ra tốt/giây 2.420,945 → 2.401,284; TTFT trung bình 713,199 → 594,276 ms; ITL trung bình 18,214 → 18,988 ms; độ trễ request trung bình 4.337,853 → 4.372,813 ms.
- Cả hai lần chạy qua kiểm tra protocol, runtime và đầu ra do nhóm xem xét trên cluster được giao; FA3 được xác nhận hoạt động trên cả tám rank decode. Điều đó chứng minh can thiệp đã chạy, không chứng minh nó cải thiện dịch vụ.
- Đỉnh H100 lịch sử 2,433.019859 và đối chứng N54 mới 2,399.186728 chỉ là bối cảnh, không phải hai nhánh của cặp này. Chúng không tạo hệ số quy đổi H100/H200.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** FA3 cải thiện TTFT trung bình 118,922 ms nhưng làm ITL tăng 0,773 ms, độ trễ request tăng 34,960 ms; goodput giảm 0,812%.
- **Giả thuyết:** Đổi attention decode có thể làm chi phí lúc bắt đầu và chi phí mỗi token biến động ngược chiều.
- **Kết luận được hỗ trợ:** Giữ FlashInfer cho cấu hình decode H100 đã thử; FA3 tiếp tục dùng cho prefill.
- **Chưa biết / giới hạn:** Một cặp khớp điều kiện không xếp hạng backend nói chung hay cô lập chính xác nguyên nhân ở mức kernel.

### Lời nói mẫu

FA3 giúp token đầu đến sớm hơn khoảng 119 mili giây. Nhưng khoảng cách giữa các token sau dài hơn một chút. Với câu trả lời dài, những khoảng tăng này cộng lại: độ trễ request trung bình tăng khoảng 35 mili giây và goodput giảm khoảng 0,81 phần trăm. Cả hai lần đo được nhóm kiểm tra trên cluster H100 được giao; FA3 chạy trên đủ rank decode. Với cấu hình này, nhóm giữ FlashInfer cho decode, không xếp hạng thư viện cho mọi workload.

### Điều không nên nói

Không chọn backend chỉ từ TTFT, không khái quát kết quả 0,812% của một cặp, và không so trực tiếp đỉnh H100 với kết quả H200.

### Câu chuyển slide

Backup tiếp theo kiểm tra liệu tiết kiệm thời gian khởi động còn giữ được khi đảo thứ tự chạy hay không.

---

<a id="slide-27"></a>

## Slide 27 — Backup · does a startup saving survive reversed order?

**Phần cứng: H100 · NSCC — thử chi phí khởi động và đảo thứ tự.**

### Nói nhanh · 10–20 giây

Read-first ban đầu giảm walltime scheduler 18,74%, nhưng phép xác nhận đảo thứ tự chỉ tiết kiệm 9,84%, thấp hơn ngưỡng 10% đã đặt. Goodput đổi nhẹ ở cả hai cặp; cache chưa rõ nên không thể kết luận nguyên nhân do lưu trữ lạnh.

![Slide 27](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-27.png)

### Slide muốn nói gì

Giải thích vì sao một cặp đo thuận lợi chưa đủ để chọn tối ưu khởi động: thứ tự chạy, trạng thái cache, node và ngưỡng chi phí đặt trước đều ảnh hưởng cách diễn giải.

### Giải thích kết quả và lập luận

So sánh cặp đầu với lần xác nhận đảo thứ tự. Ở cặp đầu, walltime off/read-first là 934/759 giây, tiết kiệm 18,74%, còn goodput giảm 0,659%. Ở cặp đảo thứ tự, walltime là 854/770 giây, tiết kiệm 9,84%, goodput đổi −0,326388%. Quy tắc đặt trước yêu cầu tiết kiệm walltime ít nhất 10% và mất không quá 2% goodput. Cặp đảo đạt dung sai thông lượng nhưng không đạt yêu cầu walltime. Walltime scheduler gồm khởi động và dọn dẹp; nó không phải cửa sổ điểm serving ổn định 120 giây.

### Thuật ngữ và ký hiệu cần hiểu

- **read-first:** Đọc checkpoint prefill trước pha serving được tính điểm để thử xem có rút ngắn khởi động không.
- **walltime scheduler:** Thời gian thực của cả job đã lập lịch, gồm startup và cleanup. Nó khác goodput ổn định và cửa sổ profiling được chấm.
- **xác nhận đảo thứ tự:** Chạy lại hai điều kiện theo thứ tự ngược để kiểm tra thứ tự hoặc cache ấm có ảnh hưởng kết quả đầu không.
- **ngưỡng định trước:** Quy tắc quyết định viết trước khi xem kết quả xác nhận: tiết kiệm ít nhất 10% walltime và mất không quá 2% goodput.
- **prefix lạnh và cache hệ điều hành lạnh:** Prefix lạnh nghĩa là không tái dùng tiền tố/KV prompt. Cache hệ điều hành lạnh nghĩa là trang file checkpoint chưa ở bộ nhớ. Thí nghiệm không xác minh cache hệ điều hành lạnh.
- **goodput:** Thông lượng request đạt quy tắc độ trễ kết hợp; khác với walltime toàn job.

### Cách diễn giải số liệu hoặc sơ đồ

- Cặp đầu có vẻ thuận lợi cho thời gian khởi động nhưng goodput giảm 0,659%. Cặp đảo thứ tự làm mức tiết kiệm thấp hơn ngưỡng quyết định 10%.
- Goodput của cặp đảo đổi 0,326388%, vẫn trong dung sai 2%; điều đó không cứu được nhánh vì ngưỡng walltime chính không đạt.
- Node khác nhau và trạng thái cache file chưa kiểm chứng nên không thể quy kết quả cho lưu trữ lạnh. Prefix lạnh là trạng thái KV cache của model, không phải trang file lạnh của hệ thống tệp.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Read-first tiết kiệm 18,74% walltime ở thứ tự đầu nhưng chỉ 9,84% sau khi đảo; goodput đổi −0,659% và −0,326388%, tương ứng.
- **Giả thuyết:** Đọc trọng số prefill trước khi startup được đo có thể giảm walltime khởi động.
- **Kết luận được hỗ trợ:** Lần xác nhận đảo thứ tự không đạt ngưỡng tiết kiệm 10% đã đặt trước, nên nhóm không chọn thay đổi này.
- **Chưa biết / giới hạn:** Cache hệ điều hành chưa xác minh và node khác nhau nên chưa thể giải thích nhân quả là do lưu trữ lạnh.

### Lời nói mẫu

Đọc trọng số trước khi phục vụ ban đầu có vẻ tiết kiệm khoảng 19 phần trăm thời gian job. Nhưng nhóm lặp lại cặp thử theo thứ tự ngược. Mức tiết kiệm còn 9,84 phần trăm, thấp hơn yêu cầu 10 phần trăm đặt trước. Goodput chỉ đổi nhẹ và vẫn trong dung sai, nhưng ngưỡng tiết kiệm chính không đạt. Vì vậy nhóm không chọn read-first chỉ dựa vào cặp đầu. Cache file chưa kiểm chứng nên cũng không thể quy cho lưu trữ lạnh.

### Điều không nên nói

Không đánh đồng walltime scheduler với thời gian serving được chấm, không gọi cache tiền tố prompt là cache hệ thống tệp, và không khẳng định nguyên nhân do lưu trữ lạnh.

### Câu chuyển slide

Tiếp theo là các thay đổi full-model có căn cứ mã nguồn nhưng không đạt tiêu chí lợi ích hữu ích.

---

<a id="slide-28"></a>

## Slide 28 — Backup · source-supported changes that did not win

**Phần cứng: H200 · Firmus — các phép so toàn model.**

### Nói nhanh · 10–20 giây

Một số thay đổi H200 đã được kích hoạt và đo, nhưng mức tăng nhỏ, âm hoặc làm xấu chỉ số đuôi. Chẳng hạn, thay attention prefill làm goodput giảm 6,385%. Cờ hoạt động được chưa đủ để đổi cấu hình đang chọn.

![Slide 28](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-28.png)

### Slide muốn nói gì

Cho thấy nhóm dùng đọc mã nguồn, xác nhận runtime kích hoạt, control ghép cặp và xem đầu ra để quyết định can thiệp nhỏ có đáng chọn hay không.

### Giải thích kết quả và lập luận

Các hàng là giả thuyết độc lập, không phải phần của một tối ưu tích lũy. Đọc mã nguồn cho biết runtime có thể dùng cài đặt; log xác nhận nó thực sự chạy; run serving đầy đủ mới đo kết quả. Goodput tăng nhẹ vẫn có thể dưới ngưỡng hữu ích hoặc làm xấu p95 TTFT. Vì vậy kết quả âm và trung tính cũng trả lời câu hỏi: tính năng hoạt động là điều kiện cần, nhưng chỉ cải thiện mục tiêu dịch vụ mới biện minh đổi cấu hình đang giữ.

### Thuật ngữ và ký hiệu cần hiểu

- **đọc mã nguồn:** Đọc code để biết cài đặt được hỗ trợ và chọn nhánh nào. Việc này dự đoán hành vi nhưng không chứng minh runtime đã dùng nó.
- **kiểm tra kích hoạt runtime:** Bằng chứng trong log hoặc trạng thái từng rank cho thấy backend/cờ dự định đã chạy trong job đo.
- **control ghép cặp:** Lần đối chứng chỉ đổi yếu tố dự định, còn workload/cấu hình khác được giữ đủ giống để so sánh.
- **ngưỡng tăng hữu ích:** Mức cải thiện tối thiểu đặt trước để đáng giữ thay đổi vận hành; phần trăm dương rất nhỏ có thể là nhiễu hoặc không đủ quan trọng.
- **p95 TTFT:** Phân vị 95 của thời gian tới token đầu. Nó đo đuôi chậm, có thể xấu đi dù độ trễ trung bình tốt hơn.
- **TRT-LLM / MNNVL:** Hai backend giao tiếp collective thay thế nhau; chọn một backend cần xác nhận kích hoạt và đo toàn serving.
- **ChunkCache / RadixCache:** Hai cách cache prefill được so trong cặp serving đầy đủ; chênh goodput nhỏ đi kèm p95 TTFT của ChunkCache xấu hơn.
- **attention page 1:** Cài đặt FlashInfer prefill tác động trang attention đầu; thay đổi đã thử giảm ITL nhưng mất goodput.

### Cách diễn giải số liệu hoặc sơ đồ

- Thay đổi thời gian chờ tokenizer đo +0,192% và +0,270%; nhóm giữ batching tokenizer tắt. Đổi collective prefill runtime tự chọn từ TRT-LLM sang MNNVL kích hoạt trên tám rank prefill nhưng chỉ tăng +0,109807% ở full run 27138.
- Đổi RadixCache sang ChunkCache cho prefill tăng +0,240921%, nhưng p95 TTFT xấu hơn nên giữ RadixCache. So sánh giới hạn request và polling tăng +0,26% hoặc âm, chưa chứng minh lợi ích hữu ích.
- FlashInfer prefill page 1 giảm ITL nhưng mất 6,385% goodput. Các phần trăm thuộc nhánh riêng, không cộng như thành phần của một lần chạy.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Thay đổi được kiểm tra mã nguồn/runtime và có quan sát serving đầy đủ, nhưng mức tăng nhỏ, âm hoặc pha trộn với đuôi độ trễ xấu hơn.
- **Giả thuyết:** Thay đổi tokenizer, collective, cache, giới hạn request, polling hoặc attention có thể tăng goodput.
- **Kết luận được hỗ trợ:** Chỉ giữ thay đổi khi đường dự định thật sự chạy và so sánh có kiểm soát cải thiện mục tiêu đủ đáng kể.
- **Chưa biết / giới hạn:** Chênh lệch nhỏ từ một lần chạy có thể do biến động; các hàng không xác lập bottleneck CPU hay xếp hạng tính năng phổ quát.

### Lời nói mẫu

Đây là các phép thử toàn model riêng, không chỉ là phỏng đoán từ source. Nhóm kiểm tra cài đặt có được hỗ trợ, xác nhận nó thật sự kích hoạt, rồi đo serving so với control. Một vài thay đổi dương nhẹ nhưng lợi ích quá nhỏ hoặc đi cùng đuôi độ trễ xấu hơn. Thay attention prefill còn làm mất khoảng 6,4 phần trăm goodput. Vì vậy nhóm giữ lựa chọn cũ: cờ hoạt động chưa đủ nếu mục tiêu dịch vụ không tốt hơn.

### Điều không nên nói

Không cộng phần trăm từ nhánh riêng, coi runtime kích hoạt là tăng tốc, hay gọi mức tăng nhỏ trong một lần đo là chiến thắng bền vững.

### Câu chuyển slide

Slide kế tiếp giới hạn các đầu mối kernel và mã nguồn theo đúng bằng chứng chúng tạo ra.

---

<a id="slide-29"></a>

## Slide 29 — Backup · scope limits of kernel and source evidence

**Phần cứng: H200 + H100 + CPU — đọc đúng nguồn từng dòng.**

### Nói nhanh · 10–20 giây

Gói attention N52 đạt 2.549,20 nhưng đổi nhiều yếu tố; Triton probe, fixture CPU và đọc mã nguồn trả lời câu hỏi hẹp hơn. Compile Qwen đầy đủ dừng ở assertion RoPE/KV. Không bằng chứng nào trong số đó tự chứng minh serving toàn model tăng tốc.

![Slide 29](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-29.png)

### Slide muốn nói gì

Trả lời kernel, profile và đọc mã nguồn chứng minh được điều gì, đồng thời tránh nhầm kết quả thành phần trên một họ phần cứng với bằng chứng toàn mô hình ở hệ khác.

### Giải thích kết quả và lập luận

Đọc mỗi hàng như một ranh giới bằng chứng. Gói attention H200 N52 là điểm serving thật nhưng đổi nhiều yếu tố cùng lúc. Triton probe H100 thử một số dạng kernel, không phải mọi dạng của model. Ngân sách SM là kiểm tra kernel/runtime giới hạn, không phải tốc độ toàn model. Log NCCL sửa cách hiểu trước đây: nhãn LL không có nghĩa control được thử dùng giao thức độ trễ thấp cho mọi thông điệp. Compile Qwen thật tới assertion native RoPE/fused-KV trước khi chấm điểm. Fixture C++ CPU và nhận xét source có phạm vi hẹp hơn nữa. Gộp các hàng này sẽ trộn bằng chứng H200, H100 và CPU.

### Thuật ngữ và ký hiệu cần hiểu

- **gói attention-DP:** Cấu hình serving H200 N52 kết hợp attention data parallel với DeepGEMM/DeepEP; nhiều yếu tố đổi cùng lúc nên không tách được đóng góp riêng.
- **Triton probe:** Phép thử kernel GPU nhỏ trên dạng đại diện. Thua ở các dạng đó chỉ là bằng chứng cho các dạng ấy, không phải mọi phép toán Qwen.
- **ngân sách SM:** Giới hạn streaming multiprocessor GPU được kernel dùng. Kết quả kernel/runtime có thể không chuyển thành goodput toàn dịch vụ.
- **NCCL LL / Simple:** Hai giao thức giao tiếp collective. Chỉ nhãn LL chưa chứng minh LL được chọn; log cho thấy control liên quan chọn Simple cho thông điệp lớn.
- **torch.compile / RoPE / fused-KV:** Biên dịch PyTorch cho model thật dừng khi mã hóa vị trí xoay gặp giao diện cache key-value hợp nhất không được hỗ trợ. Không có điểm mô hình đầy đủ.
- **fixture C++:** Phép thử CPU cho helper/cache. Nó phát hiện lỗi số học hoặc API nhưng không tải Qwen hay phục vụ request trên GPU.
- **nhận xét source:** Đọc code cho thấy cờ/API có thể có hoặc không có nơi sử dụng. Điều đó không chứng minh runtime đã kích hoạt.
- **phạm vi phần cứng:** Điểm serving H200, probe kernel H100 và fixture CPU là bằng chứng khác phạm vi, không gộp thành một so sánh.

### Cách diễn giải số liệu hoặc sơ đồ

- Gói attention-DP cộng DeepGEMM/DeepEP trên H200 N52 đạt 2.549,20, thấp hơn điểm MNNVL được giữ; các cài đặt ghép không cho phép quy một yếu tố.
- Probe FP8 Triton đại diện trên H100 thua DeepGEMM ở các dạng đã thử. Ngân sách SM 80/96/120 pha trộn hoặc không đạt tiêu chí ổn định; giữ 132 mà không khẳng định model tăng tốc.
- Điểm NCCL nhỏ 0,2315% không đủ để chọn sau khi log cho thấy control đã chọn Simple với thông điệp lớn. Compile Qwen lỗi trước khi có điểm; fixture CPU không thử serving.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Bằng chứng trải từ điểm serving H200 qua probe kernel/tài nguyên H100 đến helper CPU và đọc source; phạm vi của chúng khác nhau.
- **Giả thuyết:** Kernel, giao thức giao tiếp, ngân sách tài nguyên hoặc API khác có thể cải thiện một phần cụ thể của serving.
- **Kết luận được hỗ trợ:** Dùng bằng chứng thành phần để chọn phép thử toàn model khi code path và phần cứng hỗ trợ; không tuyên bố dịch vụ tốt hơn chỉ từ probe hay source.
- **Chưa biết / giới hạn:** Dạng và cấu hình chưa thử có thể khác. Compile Qwen thất bại cùng test CPU chưa giải quyết tương thích hay hiệu năng toàn model.

### Lời nói mẫu

Slide này trộn bằng chứng H200, H100 và CPU nên cần giữ phạm vi riêng. Gói attention là điểm serving H200 thật nhưng đổi nhiều yếu tố. Triton probe chỉ thử một số dạng kernel H100. Fixture CPU chỉ kiểm helper. Compile Qwen thật dừng ở assertion giữa mã hóa vị trí và giao diện KV, không có điểm. Những kết quả này giúp loại bỏ hoặc ưu tiên ý tưởng; không cái nào tự chứng minh serving toàn model nhanh hơn.

### Điều không nên nói

Không gộp kết quả H200, H100 và CPU, không khái quát kernel đại diện cho mọi dạng, không suy giao thức từ nhãn kernel, và không tự thêm điểm cho compile thất bại.

### Câu chuyển slide

Backup tiếp theo tổng hợp cài đặt H200 và H100 thực tế được nhóm giữ lại.

---

<a id="slide-30"></a>

## Slide 30 — Backup · the retained settings on each platform

**Phần cứng: Cấu hình H200 N64 và H100 N54 — hai cách triển khai riêng.**

### Nói nhanh · 10–20 giây

Cấu hình H200 dùng N64, hai worker prefill TP4 với DeepGEMM và chunk 8.192, cùng decode TP8/EP8 HPC-Ops. H100 là cấu hình riêng: N54, prefill HPC-Ops với chunk 4.096 và số đo riêng. Đây là mô tả cài đặt đã đo, không xác nhận chất lượng toàn tập.

![Slide 30](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-30.png)

### Slide muốn nói gì

Ghi rõ cài đặt triển khai để diễn giải kết quả trước mà không trộn cấu hình nền tảng hoặc coi nhãn cài đặt là bằng chứng hiệu năng.

### Giải thích kết quả và lập luận

Đọc các cột trong từng nền tảng, không coi H200 và H100 là benchmark ghép điều kiện. Cả hai dùng trọng số FP8, activation và KV BF16, decode TP8/EP8, FlashInfer cho attention decode, MNNVL cho collective và định tuyến vòng tròn tới hai worker prefill. Cấu hình H200 chọn N64, prefill DeepGEMM, chunk 8.192 và bucket graph decode dày từ 1 đến 64. H100 dùng N54, prefill HPC-Ops và chunk 4.096. Bảng định nghĩa điểm vận hành; nó không khẳng định năng lực tương đương hay xếp hạng phần cứng.

### Thuật ngữ và ký hiệu cần hiểu

- **H200 N64 / H100 N54:** Nền tảng GPU cùng mức concurrency client: 64 request ở H200, 54 ở cấu hình H100 riêng.
- **prefill / decode:** Prefill xử lý token prompt; decode sinh token trả lời tự hồi quy từng bước.
- **TP / EP:** Tensor parallelism chia phép toán tensor qua GPU. Expert parallelism phân phối chuyên gia MoE; decode được giữ dùng TP8/EP8.
- **DeepGEMM / HPC-Ops:** DeepGEMM là backend prefill được chọn trên H200. HPC-Ops dùng cho decode ở cả hai hệ và prefill ở H100.
- **FP8 / BF16:** Trọng số dùng số dấu phẩy động 8 bit; activation và KV cache dùng brain floating point 16 bit. Đây là các loại dữ liệu khác nhau.
- **FlashInfer / MNNVL:** FlashInfer triển khai attention decode; MNNVL xử lý giao tiếp collective GPU. Chúng có chức năng riêng.
- **round-robin:** Gateway gửi các request liên tiếp luân phiên tới hai worker prefill.
- **graph decode dày:** Cấu hình H200 capture dạng decode từ 1 đến 64. Đây là thiết lập dạng graph, không phải 64 request đồng thời.

### Cách diễn giải số liệu hoặc sơ đồ

- H200: concurrency client 64; hai worker prefill TP4/EP1; DeepGEMM; chunk 8.192; một worker decode HPC-Ops TP8/EP8.
- H100: concurrency 54; hai worker prefill TP4/EP1 HPC-Ops; chunk 4.096; decode HPC-Ops TP8/EP8. Điểm H100 cần tách khỏi điểm H200.
- Cả hai dùng độ chính xác trọng số/activation/KV như đã nêu cùng attention decode, collective, định tuyến và quy tắc chất lượng request chung. Bảng không chứng nhận accuracy toàn tập chính thức.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Các cấu hình được giữ có chung một số thiết lập decode và độ chính xác, nhưng khác phần cứng, concurrency, backend prefill và chunk.
- **Giả thuyết:** Ghi riêng cài đặt từng nền tảng giúp điểm vận hành lặp lại được và dễ diễn giải.
- **Kết luận được hỗ trợ:** Dùng cài đặt H200 N64 cho cấu hình chính đã chọn và báo cáo H100 N54 độc lập.
- **Chưa biết / giới hạn:** Bảng không xác lập các cài đặt là tối ưu hay hiệu năng chuyển đổi được giữa hai nền tảng.

### Lời nói mẫu

Bảng ghi hai điểm vận hành riêng. H200 dùng 64 request đồng thời, hai nhóm bốn GPU xử lý prompt và một worker tám GPU decode có phân phối expert. H100 dùng 54 request, backend và chunk xử lý prompt khác. Cả hai dùng trọng số FP8 cùng activation và KV cache BF16. Thành phần chung không làm hai chuỗi hiệu năng có thể thay thế nhau.

### Điều không nên nói

Không trình bày H100 và H200 như phép so sánh khớp điều kiện hoặc suy hiệu năng chỉ từ precision và số worker.

### Câu chuyển slide

Backup tiếp theo dùng cùng protocol workload để so sánh đầy đủ kích thước chunk prefill.

---

<a id="slide-31"></a>

## Slide 31 — Backup · workload control and prefill chunk trial

**Phần cứng: H200 · thử chunk; workload và cách chấm dùng chung hai hệ thống.**

### Nói nhanh · 10–20 giây

Cùng workload N64 đầy đủ, tăng chunk prefill từ 8.192 lên 12.288 làm goodput giảm từ 3.045,50 xuống 3.020,94 token/s và p95 TTFT xấu hơn. Mỗi cấu hình có một lần H200 được nhóm xem xét; chưa xác lập tối ưu chung.

![Slide 31](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-31.png)

### Slide muốn nói gì

Giải thích protocol benchmark phía sau bảng chunk để kết quả âm được hiểu là phép so sánh có kiểm soát trong phạm vi giới hạn, không phải kết luận cho mọi workload.

### Giải thích kết quả và lập luận

Bảng so sánh ba lần chạy đầy đủ, cùng concurrency mục tiêu, độ dài prompt/câu trả lời yêu cầu, seed, prefix lạnh, model, precision và đường runtime. Chỉ kích thước chunk prefill thay đổi: 8.192, 10.240 hoặc 12.288 token đầu vào được xử lý cùng lúc. Good output tokens/s là thông lượng đạt chuẩn; joint SLA là tỷ lệ request đạt cả hai giới hạn; p95 TTFT là đuôi request phản hồi chậm. Goodput và đuôi đều xấu hơn khi chunk lớn. Một lần mỗi mức đủ để giữ 8.192 cho cấu hình này, nhưng không xác định tối ưu chung.

### Thuật ngữ và ký hiệu cần hiểu

- **4.000 / 200 token yêu cầu:** Client yêu cầu 4.000 token vào và 200 token ra. Độ dài yêu cầu không chứng minh ID token thực được đọc/sinh trong mọi request.
- **closed-loop N64:** Client giữ 64 request đang xử lý và thay mỗi request hoàn tất bằng request mới.
- **protocol 60/120/30:** Warmup 60 giây, profiling được tính điểm 120 giây và grace 30 giây. Chỉ profiling tính điểm; grace kết thúc request còn lại.
- **prefix lạnh:** Request không tái dùng mục KV cache của tiền tố prompt đã làm nóng. Điều này tự nó không có nghĩa cache hệ thống tệp lạnh.
- **kích thước chunk:** Số token đầu vào xử lý cùng nhau trong một đơn vị lập lịch prefill; không phải số request đồng thời.
- **SLA / p95 TTFT:** SLA là tỷ lệ request đạt cả hai giới hạn độ trễ. p95 TTFT là phân vị 95 thời gian chờ token đầu, cho thấy các request chậm.
- **kết quả local do nhóm xem xét:** Ở đây local nghĩa là nhóm chạy và xem xét trên cluster H200 được giao. Không phải kết quả laptop hay sự phê duyệt của ban tổ chức.
- **một lần mỗi cấu hình:** Mỗi kích thước chunk là một cấu hình thí nghiệm chỉ có một lần chạy đầy đủ; thứ tự và seed engine có thể góp phần tạo khác biệt.

### Cách diễn giải số liệu hoặc sơ đồ

- Chunk 8.192, job 26766 đạt 3,045.501509 token đầu ra tốt/giây, joint SLA 98.580% và p95 TTFT 1,311.69 ms. Chunk 10.240, job 26768 đạt 3,034.088251, 98.524% và 1,518.87 ms.
- Chunk 12.288, job 26770 đạt 3,020.943099, 98.310% và 1,624.12 ms. Cả ba là lần N64 đầy đủ cùng lịch 60/120/30 và workload yêu cầu 4.000/200; mỗi mức chunk chỉ đo một lần.
- Các lần chạy qua kiểm tra protocol, runtime, độ trễ và đầu ra của nhóm, không có lỗi/hủy trong profiling. Đây là kết quả được xem xét trên cluster được giao, không phải chứng nhận chất lượng của ban tổ chức.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Goodput giảm từ 3.045,50 xuống 3.020,94 token/s và p95 TTFT tăng từ 1.311,69 lên 1.624,12 ms khi chunk tăng từ 8.192 lên 12.288.
- **Giả thuyết:** Chunk prefill lớn hơn có thể tăng thông lượng bằng cách xử lý nhiều token đầu vào hơn trong mỗi batch lập lịch.
- **Kết luận được hỗ trợ:** Giữ 8.192 cho cấu hình dịch vụ này; các chunk lớn hơn đã thử không cải thiện mục tiêu dịch vụ.
- **Chưa biết / giới hạn:** Mỗi mức chỉ một lần nên phép so sánh có giới hạn; chưa xác lập tối ưu cho workload khác hay loại trừ biến động thứ tự/seed.

### Lời nói mẫu

Cả ba lần chạy dùng 64 request đồng thời, cùng yêu cầu 4.000 token vào và 200 token ra, cùng lịch warmup, profiling và grace đầy đủ. Chỉ chunk xử lý prompt thay đổi. Goodput giảm khoảng 3.045 xuống 3.021 khi chunk lớn dần, còn đuôi token đầu chậm hơn. Nhóm kiểm tra các lần chạy trên cluster H200 được giao, nhưng mỗi mức chỉ đo một lần nên chưa chứng minh cài đặt tốt nhất phổ quát. Nhóm giữ 8.192 cho triển khai này.

### Điều không nên nói

Qua kiểm tra của nhóm không phải phê duyệt của ban tổ chức. Không suy token thực từ độ dài yêu cầu, tính grace vào thời gian chấm hay khái quát một lần đo cho mọi workload.

### Câu chuyển slide

Backup cuối đối chiếu phần tài nguyên capture tiết kiệm được với chỉ số dịch vụ mà nó cần hỗ trợ.

---

<a id="slide-32"></a>

## Slide 32 — Backup · less graph memory did not raise goodput

**Phần cứng: H200 · graph thưa 27510 so với đối chứng 27376.**

### Nói nhanh · 10–20 giây

Capture thưa giảm bộ nhớ log từ 1,15 xuống 0,36 GB mỗi rank decode, nhưng goodput giảm 0,370208% và ITL trung bình xấu hơn. Chưa đo padding để quy nguyên nhân. Nhóm giữ graph dày; cặp này không chứng minh quan hệ nhân quả.

![Slide 32](../../submission-review/ai-reasoning-update-20261030/slides/assets/slide-32.png)

### Slide muốn nói gì

Giải thích vì sao chỉ số tài nguyên thấp hơn không tự động là dịch vụ tốt hơn, đồng thời tách bộ nhớ capture khỏi tổng bộ nhớ GPU và thông lượng end-to-end.

### Giải thích kết quả và lập luận

So sánh đối chứng dày 27376 với ứng viên thưa 27510. Ứng viên lưu 12 bucket graph decode thay vì 64 và giảm bộ nhớ graph capture theo log trên mỗi rank, nhưng goodput là 3,029.861122 so với 3,041.119598, thấp hơn 0,370208%. Mean request ITL tăng từ 14.991 lên 15.136 ms; TTFT cải thiện. Ít bucket hơn có thể buộc request vào dạng đệm kém khớp hơn, làm tăng việc xử lý, nhưng lần này không tách hay đo padding. Bộ nhớ capture không gồm cấp phát GPU khác như trọng số và KV cache, nên không phải dung lượng VRAM. Điểm dịch vụ, không phải con số capture nhỏ hơn, quyết định thay đổi có ích không.

### Thuật ngữ và ký hiệu cần hiểu

- **bucket graph decode:** Một dạng thực thi GPU đã capture để phát lại cho một lớp batch decode; số bucket không phải concurrency hay số GPU.
- **padding:** Đệm batch để khớp dạng graph được hỗ trợ. Ít bucket có thể tăng padding, nhưng phép thử này không đo lượng hay chi phí đó.
- **bộ nhớ capture:** Bộ nhớ mỗi rank liên quan các graph tái sử dụng đã ghi và buffer capture. Đây chỉ là một phần sử dụng bộ nhớ GPU.
- **VRAM / GB / GiB:** VRAM là tổng bộ nhớ GPU. Log ghi GB liên quan capture mỗi rank, không phải tổng VRAM hay GiB; trọng số, KV cache, workspace và cấp phát khác nằm ngoài số này.
- **rank:** Một tiến trình worker phân tán. Số 1,15 và 0,36 GB là mỗi rank decode, không phải tổng của tám GPU.
- **ITL / TTFT:** ITL là khoảng giữa các token sinh; TTFT là thời gian đợi token đầu. Chúng đo phần độ trễ request khác nhau.
- **full local pass:** Nhóm chạy và xem xét workload đầy đủ trên cluster H200 được giao theo kiểm tra protocol/runtime/độ trễ/đầu ra nội bộ. Đây không phải phê duyệt hay chứng nhận accuracy của ban tổ chức.

### Cách diễn giải số liệu hoặc sơ đồ

- Đối chứng dày có 64 bucket, bộ nhớ capture 1,15 GB mỗi rank, thời gian capture 101.46–101.49 giây, 3,041.119598 token đầu ra tốt/giây và ITL trung bình 14.991 ms.
- Ứng viên thưa có 12 bucket, 0,36 GB/rank, capture 95.98–96.05 giây, 3,029.861122 token tốt/giây và ITL trung bình 15.136 ms. Capture được xác nhận trên cả tám rank decode khi compile mô hình tắt.
- TTFT trung bình/p95 của ứng viên là 1,102.404/1,240.481 ms và cải thiện; ITL trung bình/p95 là 15.136/15.324 ms và xấu hơn. Một đối chứng trước, seed engine khác và instrumentation startup chỉ ở ứng viên hạn chế kết luận nhân quả.

### Đánh đổi và mức độ bằng chứng

- **Quan sát:** Capture thưa giảm bộ nhớ graph theo log mỗi rank từ 1,15 xuống 0,36 GB và rút ngắn capture chút ít, trong khi goodput giảm 0,370208% so với đối chứng trước.
- **Giả thuyết:** Ít dạng capture hơn có thể tiết kiệm tài nguyên mà vẫn giữ throughput; padding là cơ chế có thể có nhưng chưa đo.
- **Kết luận được hỗ trợ:** Mục tiêu dịch vụ không cải thiện, nên nhóm giữ graph dày cho triển khai này.
- **Chưa biết / giới hạn:** Chỉ có một đối chứng trước và seed tạo sinh khác nhau; tổng VRAM và tác động padding chưa được đo bằng chỉ số bộ nhớ capture.

### Lời nói mẫu

Ứng viên thưa dùng 12 dạng decode đã capture thay vì 64. Bộ nhớ graph theo log giảm từ 1,15 xuống 0,36 gigabyte mỗi rank, nhưng goodput cũng giảm khoảng 0,37 phần trăm. Khoảng token trung bình dài hơn chút dù thời gian token đầu tốt hơn. Số bộ nhớ này chỉ nói về capture graph, không phải toàn bộ GPU. Ít dạng có thể tạo thêm padding nhưng chưa đo. Nhóm giữ graph dày; phép so sánh quá giới hạn để kết luận nhân quả.

### Điều không nên nói

Không gọi bucket là request hay GPU, không hiểu bộ nhớ capture là tổng VRAM, và không nói padding gây chênh lệch điểm. Chỉ giảm bộ nhớ capture chưa phải cải thiện goodput.

### Câu chuyển slide

Đến đây là phần bằng chứng backup đã chọn; kết luận chính vẫn dựa vào serving lặp lại và giới hạn xác minh rõ ràng.

---

<a id="slide-33"></a>

## Slide 33 — The task: same 65-million-cell airflow calculation

**Phần cứng: CPU · track HPC OpenFOAM — không phải phép đo suy luận H100/H200.**

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

**Phần cứng: CPU · track HPC OpenFOAM — không phải phép đo suy luận H100/H200.**

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

**Phần cứng: CPU · track HPC OpenFOAM — không phải phép đo suy luận H100/H200.**

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

**Phần cứng: CPU · track HPC OpenFOAM — không phải phép đo suy luận H100/H200.**

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

**Phần cứng: CPU · track HPC OpenFOAM — không phải phép đo suy luận H100/H200.**

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

**Phần cứng: CPU · track HPC OpenFOAM — không phải phép đo suy luận H100/H200.**

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

**Phần cứng: CPU · track HPC OpenFOAM — không phải phép đo suy luận H100/H200.**

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

**Phần cứng: CPU · track HPC OpenFOAM — không phải phép đo suy luận H100/H200.**

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
