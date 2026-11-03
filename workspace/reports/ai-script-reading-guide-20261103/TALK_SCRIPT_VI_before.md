# Kịch bản nói phần AI — tiếng Việt

**Bản tập nói cho tuyến 16 slide AI.** Thời lượng mục tiêu khoảng 12 phút 30 giây, đã tính khoảng dừng, với tốc độ ước tính 115–125 từ nói mỗi phút. Nhóm chưa trình bày thử trực tiếp và chưa bấm giờ. Khung công khai dành 15–20 phút cho cả AI và HPC, sau đó là 10 phút hỏi đáp; hai người nói cần thống nhất thời lượng. Mục tiêu này để khoảng 7 phút 30 giây trong khung 20 phút cho phần HPC. Nếu tổng thời lượng chỉ là 15 phút, nhóm cần thống nhất bản rút gọn AI trước khi tập.

## Slide 1 — Fast tokens count only when requests meet both latency limits

Câu hỏi của nhóm không chỉ là mô hình sinh token nhanh đến đâu. Ta phải phục vụ Qwen3-235B trên hai máy, mỗi máy tám GPU H200, với 4.000 token đầu vào và 200 token đầu ra. Một yêu cầu chỉ đạt nếu token đầu tiên đến trong ba giây và khoảng cách trung bình giữa các token sau không quá hai mươi mili giây. Ít nhất 90% mọi yêu cầu, kể cả lỗi, phải đạt đồng thời hai giới hạn. Vì vậy tốc độ chỉ có ích khi đủ nhiều yêu cầu vẫn đạt điều kiện dịch vụ.

## Slide 2 — Three investigations support three different kinds of claim

Nhóm phân biệt ba loại đóng góp. Thứ nhất là quyết định chia GPU giữa xử lý prompt và sinh câu trả lời. Thứ hai là thay đổi có giới hạn trong một đường thiết lập chuyển KV. Thứ ba là kết quả đo backend và tải client. Nhóm sử dụng SGLang, NIXL, DeepGEMM, FlashInfer và HPC-Ops là các dự án có sẵn, không phải sản phẩm do nhóm phát minh. Đóng góp là tích hợp cục bộ, kiểm tra tương thích và chọn lựa dựa trên bằng chứng. Ba câu chuyện trả lời các câu hỏi khác nhau.

## Slide 3 — Replica count and parallel width compete for the same 16 GPUs

Câu hỏi thiết kế đầu tiên là dùng mười sáu GPU thế nào khi prefill và decode cùng cần tài nguyên. Tăng số replica prefill giúp xử lý nhiều prompt độc lập; dành nhiều GPU hơn cho decode có thể hỗ trợ sinh. Nhưng mỗi lựa chọn làm phần còn lại có ít GPU hơn. Nhóm giữ hai worker prefill TP4/EP1 và một worker decode TP8/EP8 vì cách chia vừa hai máy, qua kiểm tra hình học mô hình và hai pha, rồi dùng được trong các lượt đầy đủ sau. Đây là bố trí khả thi; dữ liệu không xếp hạng công bằng mọi cách chia hay chứng minh tối ưu toàn cục.

## Slide 4 — Two TP4 prefills feed one TP8 decode within the two-node budget

Máy thứ nhất chạy hai worker prefill, mỗi worker dùng bốn GPU xử lý prompt dài. Tensor parallel chia phép tính qua GPU; expert parallel phân bố các chuyên gia của mô hình MoE. Các worker gửi trạng thái KV—trạng thái chú ý tạm thời cần để tiếp tục sinh—sang worker decode ở máy hai, dùng tám GPU sinh từng token. Cách chia này cho hai pha hình dạng worker khác nhau và giữ mỗi nhóm tensor-parallel trong một máy. Đổi lại, mỗi yêu cầu cần chuyển trạng thái giữa hai vai trò; vì vậy nhóm kiểm tra riêng việc thiết lập và tính đúng đắn của đường chuyển.

## Slide 5 — Ready workers still failed before the first usable benchmark

Câu hỏi về chuyển dữ liệu bắt đầu từ một nhánh lịch sử. Worker đã nạp mô hình và báo sẵn sàng, nhưng cặp prefill/decode không hoàn tất warmup trong 360 giây. AIPerf chưa chạy nên chưa có điểm. Ta biết lỗi nằm giữa lúc worker sẵn sàng và lúc cặp xử lý được yêu cầu, nhưng chưa biết nguyên nhân. Đọc mã nguồn thấy bước tạo descriptor duyệt cả pool KV đã dành trước. Descriptor là danh sách địa chỉ vùng nhớ, không phải dữ liệu KV. Vì vậy metadata thiết lập trở thành giả thuyết hẹp để kiểm tra, không phải chẩn đoán đã đo được.

## Slide 6 — Request-scoped descriptors remove work unrelated to the request

Vì sao xem danh sách địa chỉ trước bandwidth, cách bố trí KV hay scheduling? Nhóm chưa loại trừ các hướng đó. Mã nguồn cho thấy bước thiết lập mô tả cả vùng pool không liên quan đến một yêu cầu cụ thể. Thay đổi đề xuất là chỉ tạo danh sách địa chỉ cho vùng mà yêu cầu đó cần, trong khi giữ nguyên phạm vi byte và ý nghĩa chuyển dữ liệu. Điều kiện đúng đắn này có thể kiểm tra nhanh trên CPU trước lượt chạy phân tán. 720 ca hình học đã qua. Lý do thử là loại bỏ metadata không liên quan có thể kiểm chứng, không phải ít descriptor chắc chắn làm dịch vụ nhanh hơn.

## Slide 7 — The patched path became usable; descriptor-only speedup is unknown

Sau bản sửa, cặp worker hoàn tất warmup, xử lý yêu cầu thật và chạy hết benchmark với không lỗi được chấm. Như vậy nhánh đã chuyển từ timeout trước benchmark sang đường serving sử dụng được. Nhưng nhánh chưa sửa không có đối chứng thành công được chấm điểm, và không có đồng hồ đo riêng cho khởi tạo. Do đó ta không thể khẳng định tốc độ tăng riêng của descriptor hay quy toàn bộ thay đổi cho cơ chế này. Nhóm giữ bản sửa có giới hạn đã chạy đầu-cuối, còn độ lớn và nguyên nhân của tác động hiệu năng vẫn chưa biết.

## Slide 8 — Profiles identify candidates for investigation, not a proven time budget

Phép chẩn đoán N48 riêng cho thấy các nhóm tính toán, giao tiếp và attention đáng xem xét. Tổng thời lượng kernel có thể chồng lấp nên chưa chứng minh yêu cầu mất thời gian ở đâu. Một dấu hiệu quan trọng khác là sự khác nhau giữa hai pha: cấu hình DeepGEMM ở decode từng không đạt ngưỡng độ trễ, nhưng điều đó chưa trả lời liệu nó có phù hợp với prefill, nơi nhiều token của prompt được xử lý cùng lúc. Vì vậy đáng thử riêng prefill, giữ decode cố định. Đây là cách giải thích kỹ thuật nhìn lại từ bằng chứng đã lưu; nhóm không nói profiling đã dự đoán được người thắng. Kết luận đến từ phép đo có đối chứng và lần chạy lặp lại.

## Slide 9 — Test the decode implementation while holding the serving setup fixed

Sau khi thay prefill và kích thước chunk, nhóm đặt câu hỏi: lựa chọn decode cũ còn phù hợp dưới điều kiện vận hành mới không? Đây là lý do kiểm tra lại một implementation có sẵn, thay vì lặp nguyên một thử nghiệm đã thua. Nhóm so đối chứng decode tự động mới với HPC-Ops ở N60 đầy đủ, giữ topology, prefill, chunk, workload, attention và transport giống nhau. Nếu cả dịch vụ tốt hơn và chạy lại vẫn giữ được kết quả, nhóm có cơ sở chọn cấu hình. Nếu chỉ một chỉ số nội bộ tốt hơn hoặc vi phạm SLA, nhóm sẽ loại. Phép thử kiểm tra quyết định đó; nó chưa xác định một kernel duy nhất là nguyên nhân.

## Slide 10 — Higher goodput came with slower first tokens and faster streaming

Goodput đầu ra tăng khoảng 5,30%. Thời gian token đầu trung bình chậm thêm khoảng 125 mili giây, trong khi độ trễ giữa token trung bình tốt hơn khoảng 1,64 mili giây. Lần chạy độc lập tái hiện kết quả gần như tương tự. Nhóm giữ cấu hình đã thử để nghiên cứu tải tiếp theo, đồng thời ghi nhận token đầu chậm hơn là đánh đổi thật. Đây là kết quả ở cấp cấu hình, lặp lại trong workload này; nó không chứng minh cơ chế của một kernel hay cho phép cộng cơ học mức tăng với thí nghiệm khác.

## Slide 11 — N64 survives a full repeat; N68 loses its short-test advantage

Sau khi đổi backend, nhóm kiểm tra lại concurrency của client. Nhiều yêu cầu đang bay có thể giúp chồng lấp công việc, nhưng cũng có thể tăng thời gian chờ và làm token đầu chậm hơn. Các lượt đầy đủ N62/N64 cho thấy N64 tăng goodput khoảng 1,08%, rồi một lượt N64 độc lập cho điểm gần như tương tự. Lượt N68 ngắn có vẻ tốt, nhưng phép đo đầy đủ chỉ tăng khoảng 0,08%, dưới ngưỡng hữu ích 1% của nhóm. Nhóm giữ N64 và đóng nhánh N68. Concurrency là số yêu cầu client đang bay, không phải số GPU hay batch decode.

## Slide 12 — The remaining latency failures are first-token tails

Trong một lượt N64 đầy đủ riêng, 1.875 trên 1.902 yêu cầu đạt cả hai giới hạn độ trễ. Cả 27 yêu cầu trượt đều chậm token đầu; không yêu cầu nào trượt độ trễ trung bình giữa token và không có lỗi được chấm. Điều này cho biết điều kiện dịch vụ nào bị trượt. Nhưng thiếu thời gian từng pha nên chưa thể quy token đầu chậm cho hàng đợi, prefill, chuyển dữ liệu hay nguyên nhân khác. Nhóm báo triệu chứng đã đo, chưa gán nguyên nhân nội bộ.

## Slide 13 — A complete portable run reproduces the retained operating level

Gói nộp cũng phải sẵn sàng, phục vụ yêu cầu thật, qua bộ đọc kết quả phía client và dọn dẹp đúng. Kiểm tra sẵn sàng ban đầu thấy router khỏe trước khi mô hình đăng ký xong nên dừng trước benchmark. Nhóm điều chỉnh điều kiện chờ để xác nhận danh sách model và worker còn sống, rồi chạy job 28197 được chấp nhận với công thức đã giữ. Job hoàn tất chuỗi triển khai, phục vụ, đọc kết quả và dọn dẹp, đạt 3.051,52 token đầu ra hữu ích mỗi giây. Không có đối chứng ghép cặp và công thức phục vụ không đổi, nên đây là bằng chứng gói portable được chấp nhận, không phải tối ưu mới.

## Slide 14 — Direct H200 tests decide which H100 ideas transfer

Nhóm đo trực tiếp một số ý tưởng từ H100 trên H200, với đối chứng mới. Công thức H100 đầy đủ bị giảm; thay chunk khôi phục một phần nhánh đó: phép thử ghép cặp tăng 6,57% so với đối chứng chunk 4096, nhưng vẫn thấp hơn công thức H200 hiện dùng 4,52%. Một số chế độ theo pha có kết quả dương, nhưng dưới 0,14%; không phương án nào vượt ngưỡng hữu ích 1%. Nhóm giữ công thức riêng cho H200. Các phép đo không ủng hộ nâng cấp những cấu hình này trong điều kiện đã thử, chứ không kết luận thư viện luôn chậm hơn.

## Slide 15 — Better proxy metrics did not always improve qualifying throughput

Sparse graph giảm chỉ số bộ nhớ capture được ghi lại nhưng goodput giảm nhẹ. Cấu hình speculative decoding nông cũng giảm goodput. Nhóm đóng cả hai nhánh đã thử thay vì coi bộ đếm thấp hơn hay tính năng chạy được là cải thiện. Chỉ số phụ có thể gợi ra câu hỏi; muốn giữ cấu hình thì workload đầy đủ phải tăng đầu ra hữu ích mà vẫn đạt độ trễ và chất lượng. Kết quả âm giúp thu hẹp công thức và vẫn là bằng chứng cần giữ lại.

## Slide 16 — The retained recipe survives performance and quality checks

Kết thúc là ba bài học. Một, chọn cách chia pha và backend theo phần cứng đích; cấu hình H100 không tự động phù hợp H200. Hai, chỉ giữ mức tăng qua phép đo đầy đủ và lặp lại; loại kết quả ngắn không đạt ngưỡng hữu ích. Ba, kiểm tra riêng triển khai, hiệu năng và chất lượng câu trả lời. Gói portable được chấp nhận đạt khoảng 3.052 token hữu ích mỗi giây. Trên cùng 16 H200 và 12.032 câu MMLU-Pro, dịch vụ tối ưu đúng 9.452 câu so với 9.460 của bản FP8 tham chiếu: giữ lại 99,9154% điểm, cao hơn ngưỡng cục bộ 99%. Đây là phép kiểm tra cục bộ, không phải chứng nhận BTC. Tôi xin bàn giao cho người trình bày HPC.

## Backup 19 — Backup · full-set accuracy verification

Nếu được hỏi chi tiết: hai dịch vụ cùng nhận 12.032 câu, mỗi câu một lần. Bản tham chiếu đạt 78,6237%; ứng viên đạt 78,5572%, chênh ròng tám câu đúng. Câu trả lời không phân tích được và câu chạm giới hạn 2.048 token vẫn nằm trong mẫu số. Con số 99,9154% là điểm ứng viên chia cho điểm tham chiếu, không phải tỷ lệ câu trả lời đúng. Đây là một phép so sánh cục bộ đầy đủ, không chứng minh tương đương thống kê cho workload tương lai và không phải chứng nhận của BTC. Phát lại dữ liệu đã lưu tái tạo đúng các số đếm.

## Backup 20 — Backup · request-scoped descriptor construction

Đường cũ duyệt pool KV đã dành trước trong khi yêu cầu chỉ cần các trang của chính nó. Điều kiện đúng là danh sách địa chỉ mới phải bao phủ đúng cùng byte và giữ nguyên ý nghĩa chuyển dữ liệu, thông báo. Các ca hình học CPU kiểm tra điều kiện đó. 403,8 triệu mục nguồn trên mỗi hạng và 188 vùng cho một yêu cầu chỉ minh họa khác biệt về phạm vi; chúng không phải tỷ lệ tăng tốc. Không có bằng chứng loại trừ bandwidth, bố trí KV hay scheduling.

## Backup 21 — Backup · what the KV recovery run actually proves

Job chưa sửa 22271 timeout trước khi chấm điểm. Job đã sửa 22294 hoàn tất yêu cầu prefill/decode thật và benchmark N32 đầy đủ, không có lỗi được chấm. Kết quả chứng minh đường chạy đã sửa trở nên sử dụng được. Vì thiếu đối chứng chưa sửa có điểm và bộ hẹn giờ khởi tạo riêng, tốc độ tăng riêng của descriptor và quy kết nguyên nhân vẫn chưa biết.

## Backup 31 — Backup · real failures led to a complete portable acceptance

Gói ban đầu kiểm tra router trước khi đăng ký model hoàn tất nên dừng trước benchmark. Bản sửa chờ danh sách model hợp lệ và worker còn sống. Job 28197 được chấp nhận sau đó hoàn tất trên 16 H200, qua serving P/D, bộ đọc kết quả, điều kiện hiệu năng và dọn dẹp, đạt 3.051,518 token đầu ra hữu ích mỗi giây. Các lượt N64 trước có trung bình 3.044,40; lượt native đạt 3.045,50; một lượt hợp lệ cũ đạt 2.830,92 vẫn chưa giải thích được. Đây là quan sát riêng, không phải đối chứng tối ưu ghép cặp. Job được chấp nhận không có đối chứng và không đổi công thức phục vụ.

## Chi tiết dự phòng khi hỏi

Chín lượt H200 cuối được rà soát. Đối chứng mới đạt 3.038,02; decode FA3 đạt 2.999,25. Công thức H100 chuyển sang đạt 2.721,82. HPC-Ops prefill với chunk 6.144 và 8.192 đạt 2.821,88 và 2.900,61. Hai biến thể inference mode chỉ bật ở decode hoặc prefill nhỉnh hơn đôi chút so với đối chứng, nhưng đều dưới ngưỡng hữu ích 1%. Không biến thể nào thay công thức được giữ. Xem [FULL_RESULTS.md](../ai-quality-verification-20261103/FULL_RESULTS.md) để biết phương pháp kiểm tra chất lượng và [MOCK_QA_EVIDENCE.md](MOCK_QA_EVIDENCE.md) để tra nguồn cùng giới hạn của từng kết quả. Chưa có mock thuyết trình trực tiếp được bấm giờ.
