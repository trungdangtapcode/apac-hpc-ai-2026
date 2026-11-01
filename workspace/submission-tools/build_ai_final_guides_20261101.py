#!/usr/bin/env python3
"""Render bilingual learning transcripts for the frozen 42-slide presentation."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

WORKSPACE = Path(__file__).resolve().parents[1]
REPORT = WORKSPACE / 'reports/ai-final-report-20261030'
REVIEW = WORKSPACE / 'submission-review/ai-final-update-20261101'
DECK = REVIEW / 'TripleU_APAC2026_Presentation.pptx'

GLOSSARY = [
    ('cluster / node / job', 'A cluster is a group of connected compute servers; a node is one server. A scheduler job requests resources and runs commands there. A job ID identifies that execution, not its performance rank.', 'Cluster là cụm máy tính kết nối với nhau; node là một máy trong cụm. Job là công việc xin tài nguyên qua scheduler rồi chạy lệnh trên máy được cấp. Job ID nhận diện lần thực thi, không phải thứ hạng hiệu năng.'),
    ('allocation', 'A scheduler grant of particular nodes, CPUs/GPUs and time. A new allocation is a new grant; it can reuse the same physical GPUs. It is not automatically an independent hardware sample.', 'Một lần scheduler cấp máy, CPU/GPU và thời gian chạy. Lần cấp mới có thể vẫn dùng đúng những GPU cũ; không tự động là kiểm tra trên phần cứng khác.'),
    ('serving / inference', 'Inference computes a model response. Serving keeps the model loaded behind an API and schedules multiple incoming requests; the benchmark measures that service.', 'Inference là tính câu trả lời bằng model. Serving giữ model trong bộ nhớ, mở API nhận request và điều phối nhiều request; benchmark ở đây đo dịch vụ đó.'),
    ('Qwen3-235B-A22B', 'The model has about 235 billion total parameters, with about 22 billion active per token. The total weights still need storage; active count is not the total model-memory footprint.', 'Model có khoảng 235 tỷ tham số tổng cộng và khoảng 22 tỷ tham số hoạt động cho mỗi token. Vẫn phải lưu trọng số của model; số tham số hoạt động không phải tổng bộ nhớ cần chứa model.'),
    ('checkpoint / container image', 'A checkpoint stores the model parameters. A container image supplies the software and dependencies used to run them. Changing one is different from changing the other.', 'Checkpoint chứa tham số đã học của model. Container image chứa môi trường phần mềm và thư viện để chạy model. Đổi checkpoint và đổi image là hai thay đổi khác nhau.'),
    ('runtime / backend / native', 'Runtime is the software path executing the service. A backend is a selected implementation of one operation, such as attention. Native names the built-in execution path in this pinned software; it does not mean personal-machine execution or automatically faster code.', 'Runtime là phần mềm/đường thực thi chạy dịch vụ. Backend là cách triển khai được chọn cho một phép tính, như attention. Native trong tài liệu chỉ đường thực thi tích hợp của phiên bản phần mềm đã dùng; không có nghĩa chạy máy cá nhân hoặc mặc nhiên nhanh hơn.'),
    ('request', 'One prompt submitted to the service and its generated response.', 'Một prompt gửi đến dịch vụ và câu trả lời được sinh ra.'),
    ('token', 'A model vocabulary unit: a word, word fragment, or punctuation; it is not necessarily one word.', 'Đơn vị trong từ vựng của model: có thể là từ, mảnh từ hoặc dấu câu; không nhất thiết là một từ.'),
    ('prefill / decode', 'Prefill processes the prompt; decode repeatedly generates the next token.', 'Prefill xử lý prompt đầu vào; decode lặp lại việc sinh token tiếp theo.'),
    ('TTFT', 'Time to first token, in milliseconds (ms). Includes the observed wait before the first response token.', 'Thời gian chờ token đầu tiên, đơn vị mili giây (ms). Bao gồm thời gian chờ quan sát được trước token đầu tiên.'),
    ('ITL', 'Inter-token latency. The gate here uses each request’s mean interval between output tokens, in ms.', 'Độ trễ giữa các token. Ngưỡng ở đây áp dụng cho khoảng thời gian trung bình giữa các token trong từng request, đơn vị ms.'),
    ('SLO / SLA fraction', 'The latency objective / fraction of all requests jointly meeting both latency limits. This is not model accuracy.', 'Mục tiêu độ trễ / tỷ lệ trên toàn bộ request đồng thời đạt cả hai ngưỡng độ trễ. Đây không phải độ chính xác của model.'),
    ('goodput', 'Qualifying requests per second. The official displayed score is this value multiplied by 200 output tokens per request.', 'Số request đạt chuẩn mỗi giây. Điểm hiển thị chính thức bằng số này nhân 200 token đầu ra cho mỗi request.'),
    ('N / concurrency', 'Maximum simultaneous in-flight benchmark requests in the closed-loop workload; not the GPU count.', 'Số request benchmark tối đa đang được xử lý đồng thời trong tải vòng kín; không phải số GPU.'),
    ('closed-loop', 'Keep up to N requests in flight; after one finishes, send another. There is no separate fixed request rate.', 'Duy trì tối đa N request đang hoạt động; một request kết thúc thì gửi request mới. Không có tốc độ gửi request cố định riêng.'),
    ('p50 / median; p95; max', 'Median: half the samples are at or below it. p95: 95% are at or below it. Max: largest observed value. A mean is a different statistic.', 'Trung vị: một nửa mẫu không vượt mức đó. p95: 95% mẫu không vượt mức đó. Max: giá trị lớn nhất quan sát được. Mean là trung bình cộng, một thống kê khác.'),
    ('TP / EP / replica', 'Tensor parallelism splits model computation; expert parallelism distributes MoE experts; a replica is another worker instance.', 'TP chia phép tính của model; EP phân phối các expert của model MoE; replica là một bản worker khác.'),
    ('MoE', 'Mixture of Experts: a model routes each token to selected expert networks rather than activating every expert.', 'Model có nhiều mạng expert; mỗi token được định tuyến đến một số expert thay vì kích hoạt toàn bộ expert.'),
    ('KV cache', 'Stored attention keys and values representing processed context, used when generating later tokens.', 'Key và value của attention đã lưu, biểu diễn ngữ cảnh được xử lý để dùng khi sinh các token tiếp theo.'),
    ('attention', 'The model operation that lets the current token use relevant earlier context. Keeping earlier keys and values avoids recomputing those stored representations from scratch at every decode step.', 'Phép tính giúp token hiện tại sử dụng những phần ngữ cảnh trước đó có liên quan. Lưu key/value giúp không phải tính lại từ đầu các biểu diễn đã lưu ở mỗi bước decode.'),
    ('batch / queue / in-flight', 'A batch groups work for one engine execution. A queue holds work waiting to run. In-flight includes requests sent but not finished. Client concurrency is not necessarily the instantaneous GPU batch size.', 'Batch gom công việc cho một lượt thực thi của engine. Queue chứa công việc đang chờ. In-flight là request đã gửi nhưng chưa xong. Concurrency của client không nhất thiết bằng kích thước batch GPU ở một thời điểm.'),
    ('NIXL', 'The transfer layer used here to move KV state between prefill and decode workers.', 'Lớp truyền dữ liệu được dùng ở đây để chuyển KV từ worker prefill sang worker decode.'),
    ('FP8 / BF16', '8-bit floating-point / 16-bit bfloat formats. Weights, activations and KV can use different formats.', 'Định dạng số thực 8 bit / bfloat 16 bit. Trọng số, activation và KV có thể dùng định dạng khác nhau.'),
    ('FI / FA3 / DG / HPC-Ops', 'FlashInfer / FlashAttention 3 / DeepGEMM / the reused HPC-Ops kernel implementation. HPC-Ops is not the OpenFOAM HPC track.', 'FlashInfer / FlashAttention 3 / DeepGEMM / triển khai kernel HPC-Ops được tái sử dụng. HPC-Ops không phải track HPC OpenFOAM.'),
    ('kernel / GEMM', 'A GPU computation routine / general matrix multiplication. Faster isolated kernels do not automatically improve the whole service.', 'Một chương trình tính toán trên GPU / phép nhân ma trận tổng quát. Kernel riêng lẻ nhanh hơn chưa chắc làm cả dịch vụ nhanh hơn.'),
    ('profiling / GPU utilization', 'Profiling records selected execution events to investigate time and work. GPU activity shows whether sampled GPU work was active; 100% activity does not establish peak FLOPs, a compute bottleneck, or absence of communication stalls.', 'Profiling ghi một số sự kiện thực thi để điều tra thời gian và công việc. GPU activity cho biết GPU có hoạt động trong khoảng lấy mẫu; 100% hoạt động không chứng minh đạt FLOPs tối đa, bị nghẽn tính toán hay không phải chờ giao tiếp.'),
    ('MNNVL / collective', 'Multi-node NVLink communication path / an operation in which multiple ranks communicate together. The actual enabled path must be checked.', 'Đường giao tiếp Multi-node NVLink / phép giao tiếp có nhiều rank cùng tham gia. Cần kiểm tra đường thực thi thực tế được bật.'),
    ('CUDA graph / bucket', 'A captured GPU execution graph / a selected execution shape to capture. Bucket count is not request concurrency.', 'Đồ thị thực thi GPU được capture / một kích thước thực thi được chọn để capture. Số bucket không phải concurrency.'),
    ('baseline / control / candidate', 'Reference configuration / comparison arm / proposed changed configuration. State the exact baseline for every percentage.', 'Cấu hình mốc / nhánh đối chứng / cấu hình thử thay đổi. Mỗi phần trăm tăng giảm cần chỉ rõ mốc so sánh.'),
    ('matched trial / repeat', 'A comparison preserving intended factors except the tested change / another allocation to check reproducibility. Neither automatically proves causality.', 'So sánh giữ các yếu tố dự định, chỉ đổi yếu tố cần thử / lần cấp tài nguyên khác để kiểm tra tái lập. Cả hai không tự động chứng minh quan hệ nhân quả.'),
    ('gate / promotion / close a branch', 'A gate is a stated acceptance condition. Promotion means choosing a candidate as the retained setting. Closing a branch means deciding not to repeat the unchanged losing setting; none of these words implies organiser approval.', 'Gate là điều kiện cần đạt. Promotion là chọn ứng viên thay cấu hình đang giữ. Đóng một nhánh là quyết định không lặp tiếp cùng cài đặt không có ích; các từ này không có nghĩa BTC phê duyệt.'),
    ('99% of reference', 'A relative model-quality requirement, separate from the request latency fraction. As an arithmetic illustration, if a reference metric were 80 points, 99% of it would be 79.2 points, not 99% of answers correct. This example is not a measured contest result.', 'Yêu cầu chất lượng tương đối so với điểm tham chiếu, tách biệt tỷ lệ request đạt độ trễ. Ví dụ tính toán: nếu điểm tham chiếu là 80 thì 99% của nó là 79,2 điểm; không có nghĩa phải trả lời đúng 99% câu hỏi. Ví dụ này không phải kết quả đo của cuộc thi.'),
    ('cold prefix / cold startup', 'Cold prefix means requests cannot reuse prompt KV from earlier requests. Cold startup means the service is newly starting; OS file caches can still be warm. These are different states.', 'Cold prefix nghĩa là request không dùng lại KV prompt từ request trước. Cold startup là dịch vụ mới khởi động; cache tệp của hệ điều hành vẫn có thể chứa dữ liệu. Không được coi các trạng thái này là một.'),
    ('ms / s / tokens/s / req/s', '1,000 ms = 1 s. tokens/s counts tokens per second; req/s counts requests per second.', '1.000 ms = 1 giây. tokens/s là token mỗi giây; req/s là request mỗi giây.'),
    ('% / percentage points', 'A move from 90% to 95% is +5 percentage points, or +5.56% relative to 90%; these are different.', 'Từ 90% lên 95% là tăng 5 điểm phần trăm, hoặc tăng tương đối 5,56% so với 90%; hai cách nói khác nhau.'),
    ('2,989.175 / 2.989,175', 'The deck uses English separators: comma for thousands and point for decimals. These two forms express the same value in English and Vietnamese conventions.', 'Slide dùng kiểu Anh: dấu phẩy tách hàng nghìn, dấu chấm tách phần thập phân. 2,989.175 trên slide tương đương 2.989,175 theo cách viết Việt; không phải hai kết quả khác nhau.'),
    ('MPI rank / affinity / NUMA', 'An MPI process / placement on CPU cores / a CPU memory architecture with different local and remote access costs. CPU HPC ranks differ from GPU serving ranks.', 'Một tiến trình MPI / gắn tiến trình vào lõi CPU / kiến trúc bộ nhớ CPU có chi phí truy cập gần và xa khác nhau. Rank trong HPC CPU khác với rank serving GPU.'),
    ('Scotch / Hierarchical / graph cut', 'Mesh partitioning methods / another partitioning method / a partition-boundary proxy. A smaller cut is not automatically faster runtime.', 'Các phương pháp chia lưới / một phương pháp chia lưới khác / chỉ số đại diện cho biên giữa các phần chia. Cut nhỏ hơn không tự động có thời gian chạy nhanh hơn.'),
]


def introduction(lang, digest):
    if lang == 'vi':
        return f'''# Transcript và hướng dẫn hiểu từng slide — Tiếng Việt

Đây là **lời thuyết trình mẫu và tài liệu học**, không phải bản chép lại một buổi nói đã diễn ra. Tài liệu đi theo đúng 42 slide của bản trình chiếu hiện tại. Bản tiếng Việt được tạo theo yêu cầu riêng của bạn; mã nguồn và các báo cáo khác vẫn dùng tiếng Anh.

**Cách dùng:** mỗi slide mở đầu bằng **“Nói nhanh · 10–20 giây”**, có thể nói ngay: ý chính, số liệu nổi bật và ý nghĩa của chúng. Các từ cần thiết được giải thích ngay trong đoạn ngắn, ví dụ “repeated” là chạy lại benchmark để kiểm tra kết quả có tái lập. Thời lượng là mục tiêu để luyện, không phải bản ghi đã bấm giờ. Khi cần hiểu sâu hoặc trả lời câu hỏi, đọc tiếp “Slide muốn nói gì”, phần lập luận, thuật ngữ và lời nói mẫu dài bên dưới.

- **Slide 1–16:** phần AI chính. Dùng [kế hoạch AI gọn khoảng 10–12 phút](PRESENTATION_PLAN.md), trong phần trình bày chung AI và HPC 15–20 phút, sau đó có 10 phút Q&A riêng; không chiếm thời gian đã thống nhất của OpenFOAM.
- **Slide 17–34:** phần AI dự phòng khi được hỏi. Slide dự phòng được ẩn khi trình chiếu PowerPoint; từ AI 16 sẽ chuyển sang OpenFOAM 35. Tài liệu này vẫn giữ đủ 42 slide để học và tra cứu.
- **Slide 35–42:** giải thích phần HPC đang có trong cùng deck, chỉ đọc và diễn giải. Trạng thái job trên các slide này là **ảnh chụp ngày 23/10**, không phải trạng thái scheduler hiện tại. Hướng dẫn này không cập nhật hay xác nhận kết quả HPC mới. Thời lượng AI không bao gồm mặc định phần HPC.
- Mỗi slide có nhãn **Phần cứng** ngay dưới tiêu đề. H200 là Firmus, H100 là NSCC ASPIRE 2A+; slide có cả hai hoặc có phép kiểm tra CPU sẽ ghi riêng. Nhãn “chung” chỉ quy tắc hoặc bố trí dùng trên cả hai hệ thống, không biến chúng thành một phép so hiệu năng cùng điều kiện.
- Màu sắc có ý nghĩa **theo từng slide**. Cam không luôn là “thắng” hay “thua”. Ảnh nền, gradient và đường trang trí cuối slide không biểu diễn dữ liệu.
- **↑ / ↓** thường là hướng mong muốn tối ưu, không khẳng định số liệu thực tế đã tăng/giảm. “Không có trục” nghĩa là sơ đồ/bảng/card, không cần tự suy ra trục X/Y.
- Nghiên cứu đã dừng theo yêu cầu. Các việc “tiếp theo” trong slide là đề xuất hoặc câu chuyện tại thời điểm đó, không phải job mới đã chạy.

Nguồn: [PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), [PDF](../../submission-review/ai-final-update-20261101/TripleU_APAC2026_Presentation.pdf), [bản tiếng Anh](TRANSCRIPT_EN.md). SHA-256 của PowerPoint: `{digest}`. Đây là transcript của phiên bản này; đổi deck thì cần kiểm tra lại hướng dẫn.

## Những cách gọi cần hiểu trước khi thuyết trình

**“Nhóm tự đo” thay cho “chạy cục bộ”:** benchmark chạy trên cluster được cấp, gồm các compute node H200 hoặc H100 nêu ở từng kết quả. Nhóm tự gửi job và kiểm tra dữ liệu. Chữ “local” trong bản cũ nói về phạm vi xác minh của nhóm; nó không có nghĩa chạy trên laptop, trên login node hay chỉ một node. Kết quả trên hạ tầng được cấp vẫn chưa tự động thành điểm BTC chấm và xác nhận.

**“Phép đo đầy đủ”:** trong chiến dịch này là 60 giây warmup để dịch vụ hoạt động trước, 120 giây profiling để thu số đo, và 30 giây grace cho request còn lại hoàn tất. “Đầy đủ” phân biệt với phép thử ngắn dùng sàng lọc ý tưởng. Nó không có nghĩa đã chạy mọi bài đánh giá chất lượng hay mọi request đều đạt. Theo luật, ít nhất 90% request phải đồng thời đạt hai giới hạn độ trễ.

**“Đã kiểm tra đạt”:** nhóm kiểm tra dữ liệu theo những điều kiện đã triển khai cho lần chạy đó, chẳng hạn protocol, cấu hình thực sự được bật, độ trễ/lỗi và kiểm tra đầu ra nhỏ. Cần đọc điều kiện cụ thể của từng run; việc scheduler ghi COMPLETED chỉ cho biết script trả mã thành công. Cả hai chưa thay thế đánh giá chất lượng chính thức ≥99% điểm tham chiếu của BTC; yêu cầu đó vẫn chưa được xác minh.

**“Đối chứng” và “ứng viên”:** đối chứng là cấu hình giữ để làm mốc; ứng viên là cấu hình đổi yếu tố muốn thử. Ví dụ cache mới 27378 phải so với đối chứng mới 27376. So nó với trung bình lịch sử của một chuỗi khác sẽ trộn thay đổi cần thử với khác biệt thời điểm và môi trường.

**“Lặp lại” và “cải thiện có ích”:** chạy lại bằng job khác cho kết quả gần nhau làm bằng chứng chắc hơn một đỉnh đơn lẻ, nhưng vẫn có thể dùng lại GPU cũ. Nhóm đặt ngưỡng tăng >1% cho các phép thử gần cuối để chọn nhánh đáng chạy xác nhận; đây là quy tắc quyết định của nhóm, không phải quy định BTC. Kết quả tăng 0,24% chưa đạt quy tắc đó và chưa chứng minh tách được khỏi biến động giữa các lần chạy.

**“Quan sát”, “giả thuyết”, “kết luận”:** “TTFT tăng” là số đã đo; “TTFT tăng do hàng đợi dài hơn” là giả thuyết nếu chưa tách thời gian chờ khỏi thời gian tính; số lượng request chờ tăng trong mẫu đo là quan sát, chưa đủ chứng minh nguyên nhân; “giữ cấu hình cũ vì ứng viên chưa vượt ngưỡng đã đặt” là quyết định được dữ liệu hỗ trợ. Nêu rõ điều chưa đo giúp giải thích trung thực, thay vì biến một suy đoán hợp lý thành nguyên nhân đã chứng minh.

**Ví dụ job có số nhưng vẫn lỗi:** GPU/client có thể đo xong và lưu JSON, rồi script đọc/tổng hợp JSON lỗi khiến cả job FAILED. Sửa chương trình đọc giúp lấy lại số từ dữ liệu cũ; nó không biến job gốc thành thành công, cũng không thay thế việc chạy lại toàn bộ triển khai sau sửa.

## Từ vựng dùng xuyên suốt

| Ký hiệu / thuật ngữ | Hiểu đơn giản |
|---|---|
'''
    return f'''# Slide-by-slide transcript and learning guide — English

This is a **proposed speaking script and learning guide**, not a verbatim record of a delivered talk. It follows all 42 slides of the current presentation. The separately requested Vietnamese companion is a narrow language exception; code and other reports remain English.

**How to use it:** each slide starts with a **“Quick brief · 10–20 seconds”** that can be spoken directly: the main point, a standout result and its meaning. Essential terminology is explained within the brief, such as repeated meaning rerunning a benchmark to check reproducibility. Timing is a rehearsal target, not a timed recording. Continue with the purpose, technical interpretation, terms and longer script for deeper preparation or questions.

- **Slides 1–16:** main AI talk. Follow the [compact 10–12 minute AI rehearsal plan](PRESENTATION_PLAN.md), within the combined public 15–20 minute talk plus a separate 10-minute Q&A; preserve the agreed OpenFOAM allocation.
- **Slides 17–34:** AI backup material. Backups are hidden in the PowerPoint slide show: AI 16 advances to OpenFOAM 35. This guide keeps all 42 slides for study and questions.
- **Slides 35–42:** read-only explanation of the preserved HPC section. Its scheduler statements are **23 October snapshots**, not current scheduler status. This guide neither updates nor independently certifies later HPC work. Do not automatically include HPC in the AI time allowance.
- Every slide has a **Hardware** label below its title. H200 means Firmus; H100 means NSCC ASPIRE 2A+. Mixed-platform and CPU-only evidence is attributed separately. Shared labels describe common rules or layouts, not a matched performance comparison.
- Colors have **slide-local meanings**. Orange does not always mean a win or a failure. Background photographs, gradients and footer decorations are not measurements.
- **↑ / ↓** generally indicate the desired optimization direction, not an observed increase/decrease. “No axes” means a table, card or schematic; do not invent X/Y quantities.
- Research has stopped at the owner's request. Future actions shown on slides are proposals or historical next decisions, not newly executed jobs.

Sources: [PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), [PDF](../../submission-review/ai-final-update-20261101/TripleU_APAC2026_Presentation.pdf), [Vietnamese companion](TRANSCRIPT_VI.md). PowerPoint SHA-256: `{digest}`. This guide describes that version; recheck it if the deck changes.

## Understand the claims before presenting them

**Team-measured, formerly called “local”:** the benchmark ran on the assigned cluster's H200 or H100 compute nodes identified for that result. The team submitted the job and reviewed the data. Local described the scope of validation; it did not mean a laptop, the login node or a single compute node. Running on provided infrastructure does not itself make a result an organiser-scored or certified result.

**Full run:** the campaign protocol uses 60 seconds of warmup, 120 seconds of profiling, and 30 seconds of grace for outstanding requests to finish. Full distinguishes it from a shorter idea-screening test. It does not mean all model-quality datasets were evaluated or every request passed. The latency rule requires at least 90% of all requests to jointly meet both limits.

**Reviewed pass:** the team examined retained data against the checks implemented for that run, such as protocol, actual runtime settings, latency/errors and small output checks. Read each run's exact conditions. Scheduler COMPLETED alone means the script returned successfully. Neither label substitutes for the official model-quality evaluation requiring at least 99% of the organiser reference; that remains unverified.

**Control and candidate:** a control is the retained comparison configuration; a candidate changes the factor being tested. Cache candidate 27378 should be compared with fresh control 27376. Comparing it against a historical mean from another series mixes the tested change with time and environment differences.

**Repeat and useful gain:** another job returning a similar result is stronger evidence than one peak, although it may use the same physical GPUs. For late trials, the team used a prospective >1% gain threshold to select changes worth confirming. This is a team decision rule, not an organiser rule. A 0.24% observed increase did not meet it and was not shown to be separable from run-to-run variation.

**Observation, hypothesis and conclusion:** “TTFT rose” is measured. “Longer queuing caused the TTFT increase” is a hypothesis until wait and computation times are separated. A sampled queue increase is an observation, but does not alone establish the latency cause. “Keep the old setting because the candidate did not exceed our stated threshold” is a supported decision. State missing measurements rather than turning a plausible explanation into an established cause.

**A score inside a failed job:** GPU inference and the client can finish and save JSON, followed by a reader/summary exception that makes the job FAILED. Repairing that reader can recover a score from old data; it does not change the original job status or replace a fresh full-deployment replay after the fix.

## Shared vocabulary

| Symbol / term | Plain explanation |
|---|---|
'''


def render(records, lang, digest):
    vi = lang == 'vi'
    out = [introduction(lang, digest)]
    for term, en, vn in GLOSSARY:
        out.append(f'| {term} | {vn if vi else en} |\n')
    out.append('\n## ' + ('Mục lục theo slide' if vi else 'Slide navigation') + '\n\n')
    for s in records:
        assert '\u2026' not in json.dumps(s, ensure_ascii=False), f'Truncated text on slide {s["slide"]}'
        out.append(f"- [Slide {s['slide']:02d} — {s['title']}](#slide-{s['slide']:02d})\n")
    labels = ['Slide muốn nói gì', 'Giải thích kết quả và lập luận', 'Thuật ngữ và ký hiệu cần hiểu', 'Cách diễn giải số liệu hoặc sơ đồ', 'Đánh đổi và mức độ bằng chứng', 'Lời nói mẫu', 'Điều không nên nói', 'Câu chuyển slide'] if vi else ['Purpose', 'Technical interpretation and reasoning', 'Terms and symbols to understand', 'Interpreting the evidence or diagram', 'Tradeoff and strength of evidence', 'Spoken script', 'Avoid this interpretation', 'Transition']
    evidence = [('observation', 'Quan sát', 'Observation'), ('hypothesis', 'Giả thuyết', 'Hypothesis'), ('conclusion', 'Kết luận được hỗ trợ', 'Supported conclusion'), ('unknown', 'Chưa biết / giới hạn', 'Unknown / limitation')]
    for s in records:
        n = s['slide']; d = s[lang]
        image_path = f'../../submission-review/ai-final-update-20261101/slides/assets/slide-{n:02d}.png' if n <= 34 else f'transcript-assets/slide-{n:02d}.png'
        out.append(f'\n---\n\n<a id="slide-{n:02d}"></a>\n\n## Slide {n:02d} — {s["title"]}\n\n')
        hardware_label = 'Phần cứng' if vi else 'Hardware'
        out.append(f'**{hardware_label}: {d["hardware"]}**\n\n')
        if d.get('claim_type'):
            claim_label = 'Loại nội dung' if vi else 'Claim type'
            out.append(f'**{claim_label}: {d["claim_type"]}.**\n\n')
        brief_heading = 'Nói nhanh · 10–20 giây' if vi else 'Quick brief · 10–20 seconds'
        out.append(f'### {brief_heading}\n\n{d["brief"]}\n\n')
        if d.get('hardware_details'):
            out.append(('**Phân biệt từng kết quả:**' if vi else '**Attribute each result separately:**') + '\n\n')
            for detail in d['hardware_details']:
                out.append(f'- {detail}\n')
            out.append('\n')
        out.append(f'![Slide {n:02d}]({image_path})\n\n')
        if n == 17:
            out.append('**Phần dự phòng AI: chỉ mở khi cần giải thích sâu hơn.**\n\n' if vi else '**AI backup section: open when a deeper explanation is needed.**\n\n')
        if n >= 35:
            out.append('**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**\n\n' if vi else '**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**\n\n')
        if n <= 16 and d.get('reasoning'):
            out.append(('### Mạch suy luận để nói\n\n' if vi else '### Reasoning to communicate\n\n'))
            reasoning_labels = [('problem','Vấn đề','Problem'),('why_it_matters','Vì sao quan trọng','Why it matters'),('why_this_test','Vì sao chọn phép thử này','Why this test'),('what_we_learned','Điều rút ra','What we learned'),('next_logic','Vì sao chuyển sang bước tiếp','Why the next step follows')]
            for key,vn,en in reasoning_labels:
                out.append(f'- **{vn if vi else en}:** {d["reasoning"][key]}\n')
            out.append('\n')
        for label, key in [(labels[0], 'purpose'), (labels[1], 'visual')]:
            out.append(f'### {label}\n\n{d[key]}\n\n')
        out.append(f'### {labels[2]}\n\n')
        for term in d['terms']:
            out.append(f'- **{term["symbol"]}:** {term["meaning"]}\n')
        out.append(f'\n### {labels[3]}\n\n')
        for item in d['reading']:
            out.append(f'- {item}\n')
        out.append(f'\n### {labels[4]}\n\n')
        for key, vn, en in evidence:
            out.append(f'- **{vn if vi else en}:** {d["tradeoff"][key]}\n')
        for label, key in [(labels[5], 'script'), (labels[6], 'caution'), (labels[7], 'transition')]:
            out.append(f'\n### {label}\n\n{d[key]}\n')
    return ''.join(out)


def main():
    source = json.loads((REPORT / 'transcript-slide-source.json').read_text())
    digest = hashlib.sha256(DECK.read_bytes()).hexdigest()
    assert digest == source['presentation_sha256'], 'Deck changed: review the transcripts before rendering.'
    records = json.loads((REPORT / 'investigation-transcript.json').read_text())
    records.sort(key=lambda s: s['slide'])
    assert [s['slide'] for s in records] == list(range(1, 43)), 'Need exactly 42 unique slides.'
    for s in records:
        actual = source['slides'][s['slide'] - 1]
        assert s['title'] in [' '.join(t.split()) for t in actual['texts']], f'Title mismatch on slide {s["slide"]}'
        for lang in ['en', 'vi']:
            d = s[lang]
            if lang == 'en':
                assert not re.search('[ăâđêôơưĂÂĐÊÔƠƯ]', json.dumps(d, ensure_ascii=False)), f'Unexpected Vietnamese prose in English slide {s["slide"]}'
            assert all(d[k] for k in ['hardware', 'brief', 'purpose', 'visual', 'terms', 'reading', 'tradeoff', 'script', 'caution', 'transition'])
            assert 20 <= len(d['brief'].split()) <= (80 if lang == 'vi' else 50), f'Brief length on slide {s["slide"]}/{lang}'
            assert all(d['tradeoff'][k] for k in ['observation', 'hypothesis', 'conclusion', 'unknown'])
            assert len(d['script'].split()) >= 25
    for lang in ['vi', 'en']:
        body = render(records, lang, digest)
        assert len(re.findall(r'^## Slide \d{2} —', body, re.MULTILINE)) == 42
        for section in re.split(r'^## Slide \d{2} —', body, flags=re.MULTILINE)[1:]:
            quick = '### Nói nhanh' if lang == 'vi' else '### Quick brief'
            purpose = '### Slide muốn nói gì' if lang == 'vi' else '### Purpose'
            hardware = '**Phần cứng:' if lang == 'vi' else '**Hardware:'
            assert section.index(hardware) < section.index(quick)
            assert section.index(quick) < section.index(purpose)
        for target in re.findall(r'\]\(([^)]+)\)', body):
            if not target.startswith(('#', 'https://', 'http://')):
                assert (REPORT / unquote(target)).is_file(), f'Missing local link: {target}'
        (REPORT / f'TRANSCRIPT_{lang.upper()}.md').write_text(body)
    summary = dict(deck_sha256=digest, slides=42, ai_main=list(range(1, 17)), ai_backup=list(range(17, 35)), existing_hpc=list(range(35, 43)), languages=['vi', 'en'], scope='Source-matched learning guides for the authorised final AI update; HPC explanatory records preserved and renumbered; no new experiment.', checks=['42 unique source-matched titles in both languages', 'All per-slide explanatory fields populated', '42 concise spoken briefs per language before detailed slide purpose', 'Brief word counts bounded for rehearsal; speaking duration is an estimate', 'All relative document and image links resolve', 'No truncated ellipsis placeholders', 'Guide identity bound to the newly staged deck'], files={})
    for lang in ['VI', 'EN']:
        p = REPORT / f'TRANSCRIPT_{lang}.md'
        summary['files'][p.name] = dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
    (REPORT / 'transcript-validation.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
