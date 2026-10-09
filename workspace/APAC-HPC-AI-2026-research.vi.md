# APAC HPC-AI 2026: nghiên cứu và hướng dẫn chuẩn bị nộp bài

**Cập nhật 09/10/2026:** repo đã được cập nhật đến commit `fb0378f` (07/10); nay có tài liệu Gadi `4.2`, ASPIRE-2A `4.3` và logs tham chiếu. Các nhận xét bên dưới về việc thiếu hai tài liệu này chỉ phản ánh lần đọc tháng 9. Đọc [nghiên cứu tối ưu mới](research-optimization/README.md) để xem baseline và kế hoạch thử nghiệm hiện hành.

Tra cứu ngày 27/09/2026. Repo chính thức đã clone tại `2026-APAC-HPC-AI/`, commit `5a67229` (26/09/2026). Đã đọc cả 5 tài liệu Markdown. Addendum mang ngày 25/09/2026 thay thế các điều khoản cũ được chỉ rõ trong tài liệu.

## Cuộc thi và lịch

Đây là kỳ thứ 9, dành cho các đội sinh viên khu vực châu Á–Thái Bình Dương, do HPC-AI Advisory Council, NSCC Singapore, NCI Australia và Firmus AI Cloud tổ chức. Hai bài là tối ưu mô phỏng OpenFOAM trên CPU và inference Qwen trên GPU. Luật hiện tại yêu cầu mỗi đội nộp Basic cho cả hai bài.

Website công bố: chốt đội 22/05; bắt đầu training 08/06; truy cập máy thi từ 03/08; nộp slides và code **trước 09/10/2026**; công bố lịch interview 16/10; interview từ 19/10; công bố kết quả tại SC26 tháng 11. Giải nhất có suất đại diện APAC tại ISC Student Cluster Competition 2027.

Nguồn: https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/

Quy định tham gia trên website không giới hạn số sinh viên/đội, cho phép đại học và sau đại học, cần coach. Đừng nhầm yêu cầu 3–5 sinh viên của chương trình tài trợ riêng RIKEN với luật chung.
Nguồn: https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/need-to-know.php

## Nộp ở đâu và khi nào?

**Chưa xác minh được kênh nhận bài cuối cùng.** Các tài liệu công khai đã đọc không chỉ rõ portal upload, email nhận package, quy tắc đặt tên archive hay giới hạn dung lượng. Không có hướng dẫn phải mở PR vào repo. Trang Register là đăng ký tham gia, không nên coi là cổng nộp kết quả.

Cần xem thông báo/pin trên Slack cuộc thi hoặc hỏi BTC qua `info@hpcadvisorycouncil.com` để xác nhận: link nhận bài, deadline chính xác và múi giờ, định dạng package, cách cung cấp container/shared-storage cho tài khoản chấm. Đây là địa chỉ liên hệ, chưa được xác nhận là địa chỉ nhận bài.

FAQ có câu trả lời cuối ngày ở bất kỳ múi giờ nào, nhưng nằm trong phần FAQ các năm trước. Không nên tự coi đó là xác nhận giờ chốt năm 2026. Khuyến nghị nội bộ: hoàn tất trước ngày 09/10, thay vì đợi cuối ngày đó.
Nguồn: https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/faqs.php
Slack: xem Technical Support trong hai file Task Rules hoặc link trên trang Benchmarking chính thức.

`sbatch`/`qsub` là gửi job chạy trên cluster; chạy job thành công chưa có nghĩa đã nộp hồ sơ dự thi.

## Checklist AI / Qwen

Nguồn: [Qwen Task Rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md), gồm Addendum Q0–Q4.

- Dùng đúng checkpoint công bố `Qwen/Qwen3-235B-A22B-Instruct-2507-FP8`; không tự quantize checkpoint BF16 thay thế.
- Chạy đủ 16 GPU trên hai node H200 Firmus hoặc hai node H100 ASPIRE 2A+. Basic phải tách Prefill/Decode cho từng request.
- Input 4000, output 200 tokens. Good request có TTFT ≤ 3000 ms và average ITL ≤ 20 ms; good_request_fraction ≥ 0.90.
- Metric: good output token/s = goodput (req/s) × 200, từ `profile_export_aiperf.json`.
- Nộp cách dựng lại stack: container + build files hoặc setup trên shared storage, có hướng dẫn tái tạo.
- Một script Slurm/PBS thực hiện deploy rồi chạy lệnh AIPerf chính thức liên tiếp trong cùng job. Chọn concurrency N, gateway HOST và model ID; giữ nguyên protocol/flags còn lại trong Task Rules.
- Lưu logs và JSON export, cấu hình, versions, patches nếu có. Profiling là tùy chọn.
- Official command: warmup 60 s, benchmark 120 s, grace 30 s, closed-loop, seed 2026, gateway `/v1/chat/completions`. Không dùng request-rate thay concurrency.
- BTC rebuild dưới tài khoản riêng, nên đường dẫn/quyền truy cập không được phụ thuộc tài khoản đội.
- Accuracy phải đạt 99% reference score của BTC. Bộ kiểm tra được mô tả nhưng không được đóng gói đầy đủ trong repo hiện tại.
- Nếu dùng speculative decoding: phải lossless, khai báo nguồn/kích thước/precision draft; nếu tự train thì nộp dữ liệu/phương pháp/scripts/settings theo luật. Không train draft nhắm vào workload benchmark.

## Checklist HPC / OpenFOAM

Nguồn: [OpenFOAM Task Rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/2.%20OpenFOAM%20HPC%20Task%20Rules.md), gồm Addendum F0–F5.

- OpenFOAM openfoam.com v2512, case occDrivAerStaticMesh 65M cells, simpleFoam, double precision.
- Máy chấm: 4 CPU nodes NCI Gadi (queue normalsr) hoặc NSCC ASPIRE-2A. Iris chỉ để luyện tập.
- Scaling: 1 node/40 steps, 2 nodes/80 steps, 4 nodes/150 steps. Điểm hiệu năng lấy `Average wall-clock time per time step` ở run 4 nodes, càng thấp càng tốt.
- Basic: source nguyên bản; decomposition chỉ hierarchical hoặc scotch. Được tune rank, affinity, MPI/UCX, NUMA, runtime và build đúng giới hạn F1. `-Ofast`/`-ffast-math` chuyển sang Bonus.
- Chuỗi chuẩn bị bắt buộc: `decomposePar -constant` → `restore0Dir -processor` → `renumberMesh -constant -overwrite -parallel` → `potentialFoam -initialiseUBCs -parallel` → `applyBoundaryLayer -ybl 0.0450244 -parallel` → `simpleFoam -parallel`.
- Nộp text mô tả decomposition method, ranks, coefficients; scripts và logs của toàn chuỗi; site module hoặc build recipe/flags/patch wmake nếu tự build.
- Nộp 4-node simpleFoam log và `coefficient.dat` từ `postProcessing/forceCoeffsAll/*/`; kèm logs/plots scaling 1/2/4 nodes.
- Nộp input files dạng text: decomposeParDict, controlDict, caseDefinition; slides.
- Không đóng gói mesh, processor* directories, solver binaries hay full install tree vào bộ dữ liệu OpenFOAM. Slides là deliverable riêng như ví dụ chính thức.
- Không đổi mesh, physics, fvSchemes, lượng công việc số mỗi step, không giảm precision, không bỏ function objects, không dùng GPU.

## Slides và điểm số hiện hành

Theo [README Addendum](https://github.com/hpcac/2026-APAC-HPC-AI#addendum-2026-09-25): mỗi bài 50 điểm = Basic do giám khảo chấm 20 + Bonus 15 + hiệu năng/re-verification 15. Tổng hai bài 100. Tỷ trọng cũ 60/40 đã bị thay bởi 70/30.

Một buổi interview cho cả hai bài: trình bày 15–20 phút + hỏi đáp 10 phút. Dùng một deck chung; giải thích bottleneck, giả thuyết, từng tối ưu và số liệu trước/sau, scaling, tính đúng và khả năng tái lập. Basic tuning tốt cũng có thể được Bonus; không bắt buộc sửa source để kiếm Bonus.

Bonus không thay Basic. Với thử nghiệm ngoài Basic, cần patch/script/flags chính xác, lập luận giữ nguyên phép tính, bằng chứng đúng và speedup so với Basic trên cùng máy. Qwen dùng accuracy check. OpenFOAM có kiểm tra Cd so với baseline trước thay đổi, cùng decomposition/ranks/nodes ở cả 3 run 40/80/150; nếu không bit-identical thì mỗi giá trị phải trong ±0.5%. Đổi riêng decomposition có ngoại lệ được mô tả ở F2. Đừng áp ±0.5% như gate chính thức cho Basic.

Addendum mới cũng thay điều khoản Qwen cũ về 0 điểm khi không đạt gate: rerun không đạt 90% good requests hoặc thấp hơn reference deployment sẽ được chấm ở mức điểm reference deployment. Các nền tảng khác nhau không so trực tiếp raw performance.

## Bố cục package đề xuất, không phải format upload bắt buộc

```text
team_name/
  README.md
  presentation/team_presentation.pptx
  qwen/
    build/
    run/submit.sbatch          # hoặc script PBS phù hợp
    results/logs/             # kèm profile_export_aiperf.json
    bonus/                    # nếu có, phân biệt với Basic
  openfoam/
    README.txt
    build/                    # nếu tự build
    run/                      # scripts cho 1/2/4 nodes, đủ prep chain
    dicts/
    results/1node/
    results/2node/
    results/4node/            # simpleFoam.log, coefficient.dat
    scaling/
    bonus/                    # nếu có, gồm baseline và self-proof
```

Khuyến nghị README ghi rõ team/contact, platform, phiên bản, entrypoint cho Basic từng bài, kết quả, job IDs, instructions và phân biệt Bonus. Cấu trúc trên tổng hợp từ ví dụ của hai Task Rules.

## Chỗ tài liệu còn thiếu hoặc không thống nhất

1. Repo chỉ có 5 Markdown files; không có `reference-scripts/` mặc dù Qwen Application Notes nhắc script 07/08/09. Cần lấy kit từ cluster/BTC; không thể chạy trực tiếp các tên file đó từ repo clone.
2. OpenFOAM Rules dẫn `4.2 OpenFOAM Application Notes - Gadi`, nhưng file này chưa có trong checkout.
3. Trang Benchmarking tổng quan nói về total execution time và chỉnh solver khá rộng; Task Rules/Addendum mới cụ thể hơn: metric HPC là average wall-clock/step và không được đổi solver tolerances/lượng công việc.
4. Overview ghi trao giải SCA2027 ở Japan; RIKEN ghi Singapore. Địa điểm cần xác nhận, không kết luận từ hai trang mâu thuẫn.
5. Chưa biết kênh nộp, timezone năm 2026, archive format và quyền truy cập artifact cho judges. Phải xác nhận từ thông báo BTC.

## Hướng triển khai đề xuất

Ưu tiên có Basic hợp lệ và tái lập cho cả hai bài, lưu logs/config/job ID ngay từ đầu. AI smoke-test nhỏ trước, rồi đo trên model thật, tune PD ratio/concurrency/parallelism theo profiling. HPC học pipeline trên Iris, sau đó tune decomposition/rank/placement trên máy thi với số lần chạy có kế hoạch. Dành thời gian cuối cho clean rerun, packaging và slides vì phần giám khảo chiếm 70%.

Nguồn bổ sung:
- https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/benchmarking.php
- https://github.com/hpcac/2026-APAC-HPC-AI
- https://www.r-ccs.riken.jp/en/outreach/schools/20260128-20270331/
