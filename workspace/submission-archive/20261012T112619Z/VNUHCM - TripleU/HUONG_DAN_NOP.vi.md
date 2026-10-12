# Bộ hồ sơ hiện có để gửi BTC

Cập nhật **12/10/2026**. ZIP nằm cạnh thư mục: **VNUHCM - TripleU.zip**.
Giữ cấu trúc Presentation, AI_Task và HPC_Task. Đây là hồ sơ Qwen hiện có,
chưa upload cho BTC và chưa đầy đủ phần HPC.

## Kết quả và slide mới

- [PowerPoint](Presentation/TripleU_APAC2026_Presentation.pptx): 19 slide tiếng Anh, ghi chú tiếng Việt.
- [PDF](Presentation/TripleU_APAC2026_Presentation.pdf) và [Markdown](Presentation/TripleU_APAC2026_Presentation.md).
- [Bảng kết quả](AI_Task/logs/RESULTS.md): **89 lượt đo**, có liên kết đến export gốc.

**Best local:** `P8-TP4_D8-TP8-EP8`, bản vá NIXL hetero-TP, N48, job **22415**:
**1.912,30 good tokens/s**, **97,44% SLA**, 0 lỗi/hủy, đo dài 60/120/30.
Cao hơn best cũ 1.666,01 khoảng **14,78%**; topology, concurrency và transport
đều thay đổi nên không quy mức tăng riêng cho bản vá.

Job cuối **22809** đã đủ bốn sweep và confirm N32: **1.507,96 good tokens/s**,
**95,38% SLA**, 0 lỗi/hủy. Đã đo đủ **14 cấu hình gốc và 3 biến thể EP2**;
ba bản gốc EP1 không tương thích vẫn được ghi riêng.

## Phân biệt script portable với best mới

`AI_Task/job_scripts/submit.sbatch` vẫn là entry **09/N40 unpatched**, từ job
22219: **1.666,01 good tokens/s**, **97,82% SLA**. Nó chưa tự chuyển sang best
có bản vá. Slide, log best 22415, payload lịch sử và diff NIXL đều đã cập nhật
để review. Payload trong `archive/` có đường dẫn account gốc, dùng để audit;
không chạy nó như entry portable cho BTC.

[Hướng dẫn replay](AI_Task/job_scripts/BUILD_AND_RUN.md) mô tả entry hiện tại.
Wrapper đóng gói mới chỉ có kiểm tra CPU/static/mock, chưa chạy trên GPU.
Chuyển winning stack sang wrapper và xác nhận lại trên GPU vẫn còn phải làm.

## Những phần còn thiếu

Accuracy full-set (ít nhất 99% điểm tham chiếu) và xác nhận BTC chưa có.
Không có script/log OpenFOAM trong workspace; phần HPC ghi rõ thiếu bằng chứng.
Tạo ZIP hay chạy sbatch không tự nộp bài. Upload qua kênh BTC đã thông báo;
chưa có biên nhận nộp bài trong workspace.

## Kiểm tra sau giải nén

```bash
cd 'VNUHCM - TripleU'
sha256sum --check SHA256SUMS
```

Bản ZIP snapshot ngày 10/10 được giữ riêng để đối chiếu. Hồ sơ đóng gói là
snapshot, không tự thay đổi theo các job về sau.
