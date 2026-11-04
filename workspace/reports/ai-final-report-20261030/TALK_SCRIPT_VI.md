# Kịch bản nói phần AI — tiếng Việt

Bản nói theo 16 slide AI hiện có. Mỗi đoạn là một ý để nói; dùng “nhóm” thống nhất và làm tròn số khi trình bày. Không đọc các ghi chú ôn tập cuối tài liệu. Mục tiêu phần AI là 12–13 phút; bản chỉnh này chưa được tập trực tiếp và bấm giờ.

## Slide 1 — Fast tokens count only when requests meet both latency limits

Câu hỏi của nhóm không chỉ là mô hình sinh token nhanh đến đâu. Ta phải phục vụ Qwen3-235B trên hai máy, mỗi máy tám GPU H200, với 4.000 token đầu vào và 200 token đầu ra. Một yêu cầu chỉ đạt nếu token đầu tiên đến trong ba giây và khoảng cách trung bình giữa các token sau không quá hai mươi mili giây. Ít nhất 90% mọi yêu cầu, kể cả lỗi, phải đạt đồng thời hai giới hạn. Vì vậy tốc độ chỉ có ích khi đủ nhiều yêu cầu vẫn đạt điều kiện dịch vụ.

## Slide 2 — Three investigations support three different kinds of claim

Nhóm có ba loại đóng góp.

Thứ nhất là quyết định kiến trúc: với 16 GPU, chia thế nào giữa xử lý prompt và sinh token? Nhóm khảo sát các cách bố trí, kiểm tra khả năng chạy và giữ cấu hình phù hợp để tối ưu tiếp.

Thứ hai là thay đổi mã trong đường tích hợp NIXL, một thư viện truyền dữ liệu có sẵn. Nhóm sửa cách chuẩn bị danh sách vùng nhớ cần truyền: theo request, thay vì duyệt cả pool KV đã dành trước.

Thứ ba là tích hợp và thử nghiệm các lựa chọn backend cùng mức tải client. Nhóm dùng các dự án có sẵn như SGLang, NIXL, DeepGEMM, FlashInfer và HPC-Ops; đóng góp nằm ở kiểm tra tương thích, thiết kế phép so sánh và lựa chọn dựa trên kết quả.

## Slide 3 — Replica count and parallel width compete for the same 16 GPUs

Câu hỏi thiết kế đầu tiên là dùng 16 GPU thế nào khi prefill và decode cùng cần tài nguyên.

Tăng số worker prefill giúp xử lý nhiều prompt độc lập. Dành nhiều GPU hơn cho decode có thể hỗ trợ pha sinh token. Nhưng cả hai cùng chia sẻ ngân sách 16 GPU, nên tăng tài nguyên cho bên này sẽ giảm phần còn lại của bên kia.

Nhóm khảo sát 17 cấu hình topology để kiểm tra những cách chia khả thi. Các kết quả giúp nhóm thu hẹp lựa chọn và chọn cấu hình để nghiên cứu tiếp; đây không phải phép thử hết mọi khả năng với cùng một mức tải.

## Slide 4 — Two TP4 prefills feed one TP8 decode within the two-node budget

Nhóm giữ hai worker prefill và một worker decode. Cách chia này sử dụng vừa hai máy và đã chạy được qua cả hai pha trong các lượt benchmark đầy đủ.

Máy thứ nhất chạy hai worker prefill, mỗi worker dùng bốn GPU để xử lý prompt dài. TP4 nghĩa là bốn GPU cùng chia phép tính của một worker. Máy thứ hai chạy một worker decode dùng tám GPU, với TP8/EP8; tám GPU này vừa chia phép tính vừa phân bố các expert của mô hình MoE.

Như vậy, mỗi nhóm tensor parallel nằm trong cùng một máy. Đổi lại, sau khi xử lý prompt, prefill phải gửi trạng thái attention KV sang máy decode để tiếp tục sinh token. Vì vậy, nhóm kiểm tra riêng việc thiết lập và tính đúng đắn của đường chuyển này.

## Slide 5 — Ready workers still failed before the first usable benchmark

Khi kiểm tra đường chuyển, nhóm gặp một nhánh mà các worker đã nạp model và báo sẵn sàng, nhưng request warmup đi qua cả prefill và decode vẫn chưa hoàn tất sau 360 giây. Benchmark chưa bắt đầu nên lượt đó chưa có điểm.

Đọc mã nguồn, nhóm thấy bước tạo descriptor chuẩn bị thông tin địa chỉ vùng nhớ cho cả KV pool, dù request chỉ dùng một phần. Descriptor là danh sách địa chỉ và độ dài vùng nhớ, không phải dữ liệu KV.

Từ đó, nhóm thử giảm công việc thiết lập bằng cách chỉ mô tả phần KV thuộc request. Slide tiếp theo trình bày bản sửa và cách kiểm tra.

## Slide 6 — Request-scoped descriptors remove work unrelated to the request

Bản sửa gồm hai bước. Đầu tiên, chỉ tạo descriptor cho những trang KV thuộc request đang xử lý. Sau đó, gộp các vùng nhớ liên tiếp thành một vùng lớn hơn để rút ngắn danh sách descriptor.

Ví dụ, ba vùng nhớ liên tiếp, mỗi vùng 100 byte, có thể được mô tả bằng một descriptor dài 300 byte. Số descriptor giảm nhưng các byte cần chuyển vẫn giữ nguyên. Nếu giữa hai vùng có khoảng trống thì không được gộp qua khoảng trống đó.

Để kiểm tra tính đúng, nhóm chạy 720 trường hợp trên CPU, đối chiếu các vùng byte mà cách cũ và cách mới mô tả. Tất cả đều đạt. Bước tiếp theo là kiểm chứng bản sửa trên đường chạy GPU thực tế.

## Slide 7 — The patched path became usable; descriptor-only speedup is unknown

Sau khi sửa cách tạo descriptor, cặp prefill–decode đã hoàn tất warmup và chạy hết benchmark, không có request lỗi được chấm.

Như vậy, nhánh trước đó bị timeout đã trở thành đường serving sử dụng được. Nhóm giữ bản sửa để tiếp tục thử nghiệm hiệu năng trên đường chạy đã hoạt động đầu-cuối.

## Slide 8 — Profiles identify candidates for investigation, not a proven time budget

Khi đường serving đã chạy được, câu hỏi tiếp theo là nên thử tối ưu phần tính toán nào.

Lượt profiling riêng ở mức 48 request đồng thời cho thấy các nhóm phép nhân ma trận, giao tiếp và attention đáng xem xét. Đây là những công việc xuất hiện trong profile; thời gian các kernel có thể chồng lấp nên biểu đồ này không phải cách chia toàn bộ thời gian chờ của một request.

Nhóm cũng xem xét sự khác nhau giữa hai pha. Prefill xử lý nhiều token cùng lúc, còn decode sinh từng token nối tiếp, nên hai pha có thể phù hợp với backend khác nhau. Nhóm thử DeepGEMM cho prefill với decode giữ cố định, rồi dùng phép đo toàn dịch vụ để quyết định. Sau khi cải thiện prefill, nhóm chuyển sang kiểm tra lựa chọn decode.

## Slide 9 — Test the decode implementation while holding the serving setup fixed

Ở bước này, nhóm so sánh hai lựa chọn cho phần MoE ở decode: để SGLang tự chọn backend và chỉ định HPC-Ops. HPC-Ops là thư viện tính toán GPU có sẵn của Tencent.

Cả hai chạy trên cùng 16 H200, dùng DeepGEMM cho prefill với chunk 8192 và 60 request đồng thời. Cách chia GPU, workload, attention và transport được giữ nguyên để đánh giá tác động của việc đổi backend decode.

Kết quả được trình bày ở slide tiếp theo.

## Slide 10 — Higher goodput came with slower first tokens and faster streaming

So với chế độ tự chọn backend decode của SGLang, HPC-Ops tăng goodput khoảng 5,3% trong cùng setup.

Đánh đổi là token đầu chậm thêm trung bình khoảng 125 mili giây, nhưng khoảng cách giữa các token giảm khoảng 1,6 mili giây. Nghĩa là request bắt đầu trả lời chậm hơn một chút, nhưng sau đó sinh token nhanh hơn, và toàn dịch vụ tạo ra nhiều token đạt chuẩn hơn.

Lần chạy độc lập cho kết quả gần tương đương, nên nhóm giữ HPC-Ops cho decode và tiếp tục tối ưu số request đồng thời.

## Slide 11 — N64 survives a full repeat; N68 loses its short-test advantage

Nhóm cần cân bằng giữa thông lượng và độ trễ khi tăng số request đồng thời. Nhiều request hơn giúp tận dụng GPU, nhưng cũng có thể khiến request chờ lâu và vượt giới hạn thời gian token đầu.

Tăng từ 62 lên 64 request giúp goodput tăng khoảng 1,1%, với kết quả được tái hiện ở lần chạy độc lập. Tăng tiếp lên 68 có vẻ tốt ở lượt thử ngắn, nhưng phép đo đầy đủ chỉ cải thiện khoảng 0,08% so với N64, dưới ngưỡng hữu ích 1% của nhóm.

Vì vậy, nhóm giữ N64: mức tải cho cải thiện rõ ràng, còn tăng thêm chưa mang lại lợi ích đáng kể. N64 là 64 request client đồng thời, không phải số GPU hay batch decode.

## Slide 12 — The remaining latency failures are first-token tails

Sau khi chọn N64, nhóm muốn biết những request chưa đạt SLA đang gặp vấn đề gì, thay vì chỉ nhìn goodput tổng.

Mỗi chấm trong biểu đồ là một request. Trục ngang là thời gian chờ token đầu, trục dọc là khoảng cách trung bình giữa các token, đều tính bằng mili giây. Hai đường đỏ đánh dấu giới hạn ba giây và hai mươi mili giây; request đạt chuẩn phải nằm phía dưới bên trái, tính cả điểm đúng biên.

Khoảng 98,6% request đạt cả hai điều kiện. Các chấm xanh xám là request đạt chuẩn. Các chấm cam đều nằm bên phải giới hạn ba giây nhưng vẫn dưới giới hạn giữa token. Nghĩa là những request này bắt đầu trả lời chậm, còn khi đã bắt đầu thì vẫn sinh token đủ nhanh. Có 27 request như vậy, và không có lỗi request.

Vì vậy, nếu tiếp tục cải thiện cấu hình này, nhóm cần tập trung tìm nguyên nhân khiến một số request chờ token đầu lâu.

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

## Ghi chú ôn tập cho slide 8 — không đọc thành phần trình bày

- Thử DeepGEMM riêng cho prefill: job 24291 trên 16 H200, N56, đạt khoảng 2.716 good tokens/s, tăng 1,81% so với control 24263; khoảng 98,82% request đạt SLA. Đây là kết quả prefill, khác phép thử decode tăng 5,3% ở slide 10.
- Phép thử HPC-Ops prefill về sau trên H200, cùng chunk 8192, thấp hơn cấu hình DeepGEMM khoảng 4,52%. Đây là bằng chứng bổ sung cho lựa chọn, không phải lượt thử trước bước chọn decode trong câu chuyện đang trình bày.
- Thử Triton ở mức kernel riêng trên H100 không tìm được lợi ích trong các trường hợp đã kiểm tra. Không dùng kết quả này như benchmark toàn model trên H200.
- SGLang là framework serving; NIXL là thư viện chuyển dữ liệu; DeepGEMM và HPC-Ops cung cấp đường tính toán; FlashInfer có vai trò attention trong cấu hình giữ lại. Chúng không phải các client tương đương nhau.
- Slide 8 hiện trình bày profiling, không hiển thị bảng so sánh prefill. Các số trên dành cho ôn tập và Q&A; slide 9 trình bày setup so sánh decode, slide 10 mới trình bày kết quả decode.

## Ghi chú ôn tập cho slide 7 — không đọc thành phần trình bày

Bằng chứng ủng hộ việc giữ bản sửa là đường chạy đã hoàn tất warmup và benchmark. Không có lượt chưa sửa hoàn tất để tính mức tăng tốc riêng, cũng chưa đo riêng thời gian tạo descriptor; không quy toàn bộ tác động cho một nguyên nhân duy nhất. Chi tiết giữ trong phần dự phòng.
