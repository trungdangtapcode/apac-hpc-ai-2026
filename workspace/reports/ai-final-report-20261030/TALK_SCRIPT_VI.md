# Kịch bản nói phần AI — tiếng Việt

Đây là kịch bản đề xuất cho 16 slide AI, chưa phải bản ghi một buổi thuyết trình đã diễn ra hay được bấm giờ. Hãy tập nói khoảng 10–11 phút và thống nhất phần còn lại trong tổng 15–20 phút cho người trình bày HPC. Theo quy định công khai, phần hỏi đáp có thêm 10 phút. Hai người nói AI và HPC cần thống nhất phần chia; nếu bài nói chỉ có 15 phút thì mục tiêu 10–11 phút cho AI để lại ít nhất bốn phút cho HPC.

## Slide 1 — Điểm số phải đi cùng độ trễ

Bài toán là phục vụ Qwen3-235B trên hai máy, mỗi máy có tám H200. Workload cố định dùng 4.000 token đầu vào và sinh 200 token đầu ra. Yêu cầu chỉ đạt nếu token đầu tiên xuất hiện trong ba giây và khoảng cách trung bình giữa các token sau không quá hai mươi mili giây. Ít nhất chín mươi phần trăm tất cả yêu cầu, kể cả lỗi, phải đồng thời đạt cả hai điều kiện. Vì vậy ta cần thông lượng hữu ích mà vẫn đáp ứng độ trễ.

## Slide 2 — Ba loại kết luận

Nhóm tách ba loại công việc. Chọn cách chia số GPU là quyết định kỹ thuật. Sửa cách tạo mô tả vùng KV theo từng yêu cầu là phần triển khai của nhóm. Đo backend và mức tải là kết quả thực nghiệm. Các kernel GPU có sẵn do runtime cung cấp; đóng góp của nhóm là tích hợp, chọn cấu hình và kiểm tra bằng phép đo có đối chứng. Trước hết phải biết một cấu hình chạy được, sau đó mới biết nó có cải thiện mục tiêu hay không.

## Slide 3 — Vì sao giữ topology này

Mười bảy cấu hình dùng được giúp tìm ra các cách bố trí có thể nạp mô hình FP8 và phục vụ hai giai đoạn. Ba điểm minh họa được đo tại N32, N40 và N48, tức số yêu cầu đồng thời khác nhau. Do tải khác nhau, không thể nhìn ba điểm đó rồi kết luận cấu hình nào thắng trong một phép so sánh công bằng. Nhóm giữ hai worker prefill TP4 và một worker decode TP8/EP8 vì nó vừa ngân sách hai máy, qua kiểm tra tương thích và đường xử lý thực tế, rồi tiếp tục được dùng ở các phép đo sau. Đây là lựa chọn thực dụng đã kiểm chứng vận hành, không phải tối ưu toàn cục.

## Slide 4 — Công việc chạy ở đâu

Máy thứ nhất chạy hai worker prefill, mỗi worker dùng bốn GPU theo tensor parallel. Cách này chia phép tính tensor của mô hình qua nhiều GPU; expert parallel chia các chuyên gia của mô hình MoE qua GPU. Chúng xử lý prompt dài rồi gửi trạng thái KV qua NIXL sang máy thứ hai. Máy thứ hai chạy một worker decode dùng tám GPU theo tensor và expert parallel để sinh câu trả lời. Giữ nhóm tensor parallel trong cùng máy phù hợp với cách bố trí phần cứng. Đổi lại, mỗi yêu cầu phải chuyển KV giữa hai vai trò.

## Slide 5 — Lỗi xuất hiện trước khi benchmark

Nhóm xem lại một nhánh dùng tensor parallel khác nhau giữa prefill và decode. Mô hình đã nạp xong và worker báo sẵn sàng, nhưng bước khởi động cặp prefill/decode hết ba trăm sáu mươi giây. AIPerf chưa hề chấm yêu cầu nào. Ta biết lỗi nằm trước phép benchmark ổn định, nhưng chưa biết một thành phần khởi động cụ thể nào gây lỗi. Đọc mã nguồn thấy phần tạo descriptor dường như duyệt cả vùng KV đã dành trước, nên nhóm chọn kiểm tra giả thuyết hẹp đó trước.

## Slide 6 — Vì sao thử descriptor trước

Lý do là có thể kiểm tra nhanh: mã nguồn tạo mô tả cho vùng nhớ không cần thiết đối với một yêu cầu; thay đổi đề xuất chỉ mô tả các trang của yêu cầu đó và gộp các đoạn liền nhau. Ta có thể kiểm tra các khoảng byte còn tương đương trên CPU trước khi chạy lại toàn bộ mô hình. Bảy trăm hai mươi ca hình học vùng nhớ đã qua kiểm tra. Con số 403,8 triệu là mục nguồn trên mỗi hạng của cả pool; 188 là số đoạn đã gộp cho một yêu cầu bốn nghìn token. Hai con số khác phạm vi, không phải tỷ lệ tăng tốc. Nhóm chưa đo bandwidth, chưa so sánh các cách bố trí KV, và chưa loại trừ scheduling bằng thực nghiệm.

## Slide 7 — Bản sửa thực sự chứng minh điều gì

Với đường chạy đã sửa, worker khởi động xong và bước warmup cặp mất khoảng 0,68 đến 0,70 giây mỗi yêu cầu. Một lượt đầy đủ ở N32 đạt 1.422,96 token đầu ra hữu ích mỗi giây; 95,87 phần trăm yêu cầu đạt đồng thời hai giới hạn độ trễ và không có lỗi được chấm. Kết quả này chứng minh đường chạy sau sửa có thể phục vụ benchmark. Bản chưa sửa dừng trước khi có điểm, nên ta không có đối chứng thành công và không biết riêng descriptor tăng throughput bao nhiêu. Không được lấy 360 chia cho 0,7 rồi gọi đó là hệ số tăng tốc.

## Slide 8 — Profiling cho hướng điều tra

Một phép profiling riêng ở N48 ghi thời lượng các kernel trên GPU. GEMM, collective cùng chuẩn hóa và attention là những hướng đáng kiểm tra. Các tỷ lệ đó tính trên tổng thời lượng kernel được ghi nhận; công việc có thể chồng lấp nên chúng không phải tỷ lệ thời gian toàn yêu cầu. Ở N64, ta cũng thấy một số yêu cầu trễ token đầu, nhưng chưa có thời điểm từng giai đoạn của từng yêu cầu để biết nguyên nhân là hàng đợi, prefill, chuyển KV hay tính toán. Profiling giúp đặt câu hỏi tiếp, chưa chứng minh bottleneck.

## Slide 9 — Một phép thử decode riêng có đối chứng

Kết quả tiếp theo đến từ thí nghiệm riêng: so sánh cấu hình decode tự chọn mới với triển khai HPC-Ops được hỗ trợ ở N60. Topology, prefill, chunk, workload, attention và transport được giữ cố định. Nhóm thử hướng này vì implementation decode là một trong vài khả năng đáng kiểm tra ở cấp dịch vụ. Tỷ lệ kernel ở slide trước không chứng minh đây là cách sửa bottleneck. Bằng chứng cho kết quả là đối chứng mới và lần lặp lại, không phải phần trăm profiling.

## Slide 10 — Throughput và độ trễ đổi chiều

Throughput token đầu ra hữu ích tăng từ 2.838,85 lên 2.989,17, khoảng 5,30 phần trăm. Thời gian token đầu tiên trung bình chậm thêm 125 mili giây, còn khoảng cách token trung bình giảm khoảng 1,64 mili giây. Lần chạy độc lập của nhánh HPC-Ops lệch khoảng âm 0,033 phần trăm so với lần trước. Nhóm ghi nhận cấu hình này có đánh đổi về token đầu tiên và dùng nó để khảo sát mức tải tiếp theo. Kết quả không cô lập một kernel và cũng không thể cộng cơ học với các cải tiến khác.

## Slide 11 — Chọn N64 bằng phép đo đầy đủ

Nhóm so sánh lượt đầy đủ N62 và N64. Throughput hữu ích tại N64 tăng khoảng 1,08 phần trăm; một lượt N64 độc lập khác cho kết quả gần như bằng nhau. Lượt ngắn N68 trông tốt hơn, nhưng đo đầy đủ chỉ tăng khoảng 0,08 phần trăm, thấp hơn ngưỡng hữu ích một phần trăm mà nhóm đặt ra. Vì vậy nhóm giữ N64 làm điểm vận hành có thể lặp lại. Concurrency ở đây là số yêu cầu của client đang chờ xử lý, không phải số GPU hay batch decode.

## Slide 12 — Yêu cầu nào không đạt

Biểu đồ từng yêu cầu đến từ một lượt N64 đầy đủ riêng. Trong 1.902 yêu cầu, có 1.875 yêu cầu đạt đồng thời cả hai giới hạn. Hai mươi bảy yêu cầu còn lại đều trễ token đầu; không yêu cầu nào vi phạm ITL trung bình và không có lỗi được tính điểm. Biểu đồ cho biết điều kiện nào bị trượt trong lượt đó, nhưng không cho biết nguyên nhân bên trong server.

## Slide 13 — Lần lặp đáng tin hơn một đỉnh đơn

Ba lượt N64 đầy đủ trước đó trung bình đạt 3.044,40 token hữu ích mỗi giây. Một lượt native riêng đạt 3.045,50, gần cùng mức. Thử cache đạt 3.048,45 nhưng chỉ hơn đối chứng mới 0,24 phần trăm, thấp hơn ngưỡng một phần trăm. Một lượt hợp lệ cũ thấp hơn đáng kể và nhóm chưa xác định được nguyên nhân. Vì vậy kết luận là một mức vận hành có tính lặp lại, đồng thời giữ lại dấu hiệu drift, chứ không chọn con số đơn lẻ lớn nhất làm người thắng ổn định.

## Slide 14 — Đem ý tưởng từ H100 sang kiểm tra trên H200

H100 giúp nhóm sàng lọc tương thích và lựa chọn ứng viên, nhưng điểm H100 không xếp hạng cấu hình H200. Sau đó nhóm đo các lựa chọn đã chọn cùng một đối chứng mới trên đúng mười sáu H200. Công thức H100 đầy đủ khi chuyển sang H200 đạt 2.721,82, thấp hơn đối chứng H200 khoảng 10,41 phần trăm. Decode FA3 thấp hơn 1,28 phần trăm. Hai chunk prefill HPC-Ops và hai chế độ inference theo từng pha cũng không vượt đối chứng theo ngưỡng một phần trăm. Kết luận là giữ công thức riêng cho H200; không suy ra thư viện nào luôn chậm hơn trong mọi trường hợp.

## Slide 15 — Không chọn proxy thay cho mục tiêu dịch vụ

Một số thay đổi cải thiện chỉ số phụ nhưng không cải thiện dịch vụ. Sparse graph giảm lượng bộ nhớ capture được ghi nhận, nhưng goodput lại thấp hơn một chút so với đối chứng. Một lượt speculative decoding nông cũng giảm goodput. Nhóm đóng các cấu hình đã thử đó. Bộ nhớ giảm hay tính năng chạy được chưa đủ; cả workload phải cải thiện và vẫn giữ giới hạn độ trễ cùng chất lượng.

## Slide 16 — Nêu giới hạn rồi bàn giao

Kết luận hiện tại là một công thức H200 đã được đo lặp lại: prefill DeepGEMM, chunk 8.192; decode HPC-Ops, attention FlashInfer, truyền dữ liệu MNNVL tại N64. Nhóm chưa chứng minh đây là tối ưu toàn cục. Đánh giá chất lượng chính thức so với bộ tham chiếu của ban tổ chức vẫn chưa biết; nhóm cũng chưa chạy lại toàn bộ GPU sau khi sửa bộ đọc kết quả portable. Bây giờ tôi bàn giao phần OpenFOAM cho thành viên phụ trách kết quả CPU.

## Bản dự phòng khi hỏi

Chín job H200 cuối ngày 31/10 đều đã được rà soát. Đối chứng mới 27777 đạt 3.038,02; FA3 decode 27779 đạt 2.999,25. Công thức H100 chuyển sang H200 ở N64, job 27783, đạt 2.721,82. HPC-Ops prefill với chunk 6.144 và 8.192 đạt 2.821,88 và 2.900,61. Chỉ thử inference mode ở decode và prefill lần lượt đạt 3.039,36 và 3.043,14, so với đối chứng riêng 3.039,17. Không ứng viên nào qua ngưỡng hữu ích một phần trăm nên cấu hình H200 không đổi. Các job qua kiểm tra nội bộ; điều đó không thay cho chứng nhận chất lượng chính thức của ban tổ chức.
