# OpenFOAM: tối ưu CPU, giữ nguyên phép tính

## 1. Bài toán và máy chạy

Case occDrivAerStaticMesh có ~65 triệu cells, solver `simpleFoam`, OpenFOAM openfoam.com v2512, double precision. MPI chia mesh thành phần cho từng rank. Rank là tiến trình CPU, không phải GPU.

Bài chấm chạy **4 CPU nodes Gadi hoặc ASPIRE-2A**; cluster 2×H200 hiện tại không phải nền tảng chấm HPC này. Iris chỉ luyện tập. Cần tài khoản/project ở một trong hai máy thi CPU; chưa xác minh đội có quyền truy cập nào.

Metric phải tối thiểu hóa: dòng `Average wall-clock time per time step`, từ step thứ hai, ở run 4-node/150 steps. Không nhầm với toàn job walltime, thời gian load/prepare hay SU.

Scaling: 1 node/40, 2 nodes/80, 4 nodes/150. Vì số steps khác nhau, tính scaling từ seconds/step, không lấy tổng walltime các run để tính speedup.

[Task Rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/2.%20OpenFOAM%20HPC%20Task%20Rules.md).

## 2. Baseline mới của BTC

Nguồn trực tiếp: [Gadi Notes](../2026-APAC-HPC-AI/4.2%20OpenFOAM%20Application%20Notes%20-%20Gadi.md) và [ASPIRE-2A Notes](../2026-APAC-HPC-AI/4.3%20OpenFOAM%20Application%20Notes%20-%20ASPIRE-2A.md), kèm logs trong repo.

| Máy | Method | 1 node s/step | 2 nodes s/step | 4 nodes s/step | MPI ranks ở 4 nodes |
|---|---|---:|---:|---:|---:|
| Gadi | hierarchical | 8.605 | 4.249 | 2.380 | 416 |
| Gadi | scotch | 8.478 | 4.213 | 2.126 | 416 |
| ASPIRE-2A | hierarchical | 14.669 | 7.118 | 3.415 | 512 |
| ASPIRE-2A | scotch | 14.049 | 7.196 | 3.576 | 512 |

**Đây là số BTC, không phải của đội.** Gadi scotch giảm thời gian/step khoảng 10.7% so với split hierarchical tham chiếu; nói speedup theo ratio thì khoảng 1.12×. ASPIRE không cho phép kết luận scotch chắc chắn chậm: cùng decomposition scotch có 5 lần chạy từ 3.191 tới 3.576 s/step, chênh khoảng 12%, dù coefficient.dat giống nhau.

Không so trực tiếp raw time giữa hai platforms để quyết định điểm cuộc thi. Gadi và ASPIRE khác CPU, MPI và ranks. Baseline cần so với chính mình trên cùng máy.

## 3. Ưu tiên A: decomposition và rank count

Basic chỉ cho hierarchical/scotch. Method quyết định số mặt biên phải trao đổi và cân bằng công việc. Compiler flags không sửa được decomposition xấu. [Tài liệu OpenFOAM](https://www.openfoam.com/documentation/user-guide/3-running-applications/3.2-running-applications-in-parallel) giải thích domain decomposition và tham số methods.

Đề xuất thử có giới hạn:

1. Site module, scotch, full physical-core ranks để có baseline.
2. hierarchical đúng số ranks; bắt đầu từ coefficients của BTC, rồi một split khác phù hợp hình học nếu nhìn mesh/boundary và đo được imbalance.
3. Giảm ranks/node còn khoảng nửa số cores nếu MPI/NUMA/bandwidth là bottleneck. Gadi: 52 vs 104/node; ASPIRE: 64 vs 128/node. Đây là ứng viên, không phải tối ưu đã biết.
4. Với mỗi thay đổi ranks, dựng lại decomposition phù hợp. Số cells/rank tăng khi ranks giảm; phải kiểm tra memory.

Ít ranks có thể giảm communication nhưng tăng compute mỗi rank. Không dùng đủ cores vẫn được luật cho phép. `nHierarchical` phải có tích đúng số subdomains. Hệ tọa độ/mesh aspect ratio phải được xem trước khi chọn cắt hướng nào.

## 4. Ưu tiên B: affinity, NUMA, MPI

Cố định ranks và decomposition khi so placement; kiểm tra actual CPU binding thay vì chỉ thêm flag. Baseline dùng MPI bundled với module. OpenMPI trên Gadi và Cray MPICH trên ASPIRE có launcher/env khác nhau, không copy flags lẫn nhau.

Thử physical cores/SMT off trước; chỉ thử SMT khi đo cho thấy có lợi. Đọc profiler để biết solver chờ MPI, memory hay compute. Các biến MPI/UCX và affinity là Basic nếu không đổi phép tính. Không có một setting portable đảm bảo tăng tốc trên cả hai máy.

### Lỗi MPI shutdown được BTC phân tích trên ASPIRE

MPI mặc định có thể SIGBUS sau `End` khi finalize trên nhiều nodes. BTC đo được hai workaround riêng:

```bash
export FI_VERBS_PREFER_XRC=0
# HOẶC thử riêng:
export FI_OFI_RXM_USE_SRX=0
```

Theo ASPIRE Notes, từng biến sửa shutdown trong các phép thử và giữ coefficient.dat giống default. Đây là runtime tuning Basic, **không phải đảm bảo speedup**: 4-node scotch averages giữa settings có khoảng dao động chồng lấn.

Không áp các biến này lên cluster GPU hoặc Gadi một cách máy móc. Mục đích đầu tiên là job kết thúc cleanly. Đừng đơn giản bỏ qua mọi exit code lỗi hoặc dùng `|| true`: phải xem lỗi đến ở bước nào, logs/artifacts và thực hiện workaround đã kiểm chứng.

## 5. Ưu tiên C: tiết kiệm SU để có thêm lượt thử

Bước `decomposePar` chạy serial nhưng một job full-node giữ mọi cores idle trong lúc đó. Addendum F1 cho phép chia chain:

```text
Job nhỏ: setup → decomposePar → restore0Dir
                           |
                     dependency afterok
                           v
Job 4 nodes: renumberMesh → potentialFoam → applyBoundaryLayer → simpleFoam
```

Số đo BTC cho 4-node scotch:

| Máy | Một job đầy đủ | Split serial+parallel | Giảm SU |
|---|---:|---:|---:|
| Gadi | 226.49 | 118.82 | ~48% |
| ASPIRE-2A | 149.62 | 82.74 | ~45% |

**Đây là tiết kiệm ngân sách, không trực tiếp cải thiện metric seconds/step.** Có thể giúp thực hiện nhiều thử nghiệm hơn. Chênh lệch thời gian solver giữa các lần không chứng minh split tự tăng tốc.

Dùng dependency và run directories riêng. Full chain phải đủ các bước, giữ `-ybl 0.0450244` và default renumbering trong Basic. Những reuse/short runs trong notes chỉ để sàng lọc và không thay full-chain scored run. So Cd ở đúng 40/80/150 steps của full runs.

## 6. Compile, I/O và Bonus

Sau decomposition/placement, mới xem rebuild source v2512 nguyên bản bằng flags giữ IEEE double precision. Nộp exact build script và patch wmake nếu có. `-ffast-math`/`-Ofast` là Bonus, không phải Basic. Nên giữ module baseline có thể chạy lại trước khi rebuild.

Basic cho runtime I/O flags, node-local storage và OptimisationSwitches đúng giới hạn. Chỉ tối ưu I/O nếu thấy nó nằm trong đoạn được tính; giảm thời gian prep không tự giảm metric. Không tắt function objects, giảm logs/work hay đổi `fvSchemes`/solver tolerances.

Bonus đáng cân nhắc khi đã có Basic và thời gian self-proof: method decomposition khác, renumbering khác, communication/data-layout/source changes giữ nguyên toán. Không ưu tiên patch solver sát deadline khi chưa có baseline.

OpenFOAM Bonus ngoài ngoại lệ đổi riêng method decomposition cần pre-change baseline cùng nodes/ranks/decomposition. Cd ở 1/2/4-node runs phải bit-identical hoặc trong ±0.5% baseline; không lấy 150-step answer để thay phép kiểm 40/80 steps. Ngưỡng này không phải official gate của Basic.

## 7. Khi nào có thể tuyên bố cải thiện?

Lưu ít nhất baseline và candidate cùng platform/config, job IDs và full logs. Với ASPIRE, một thay đổi 5% trong một lần chạy có thể nằm trong noise đã quan sát. Chạy vài lần representative nếu budget/time cho phép, báo cả range; không xóa slow steps để sửa metric chấm. Official rerun mới là số tham chiếu chấm.

Kết quả nghiên cứu hiện tại: có đường thử hợp lệ và các baseline có thật; chưa có bằng chứng ứng viên của đội vượt chúng.
