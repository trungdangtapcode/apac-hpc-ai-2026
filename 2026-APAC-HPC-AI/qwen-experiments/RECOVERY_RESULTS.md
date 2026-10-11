# Đang phục hồi benchmark còn thiếu

Cập nhật UTC: 2026-10-11T23:18:29.921407+00:00

**14/17 cấu hình gốc có đủ bốn lượt sweep.** **3/3 biến thể prefill EP2 có đủ số đo.** Ba cấu hình gốc TP8/EP1 không khớp block FP8 trong image hiện tại; biến thể EP2 được ghi riêng, không tính giả thành cấu hình gốc đã đo.

Job lỗi, timeout hoặc chỉ deploy server không được tính là hoàn thành benchmark. Các mức N thiếu được gửi lại dưới job ID mới. Điểm qua SLA được đo dài nếu cần.

| # | Cấu hình chạy lại | Gốc / biến thể | Job và trạng thái | Mức N còn thiếu | Confirm |
|---:|---|---|---|---|---|
| 2 | P8-TP2_D8-TP4-EP4 | gốc | 22270:COMPLETED, 22274:CANCELLED, 22414:COMPLETED | [] | True |
| 3 | P8-TP8-EP2_D8-TP4-EP4 | EP2 variant | 22271:FAILED, 22280:CANCELLED, 22294:COMPLETED | [] | True |
| 4 | P8-TP4_D8-TP8-EP8 | gốc | 22272:CANCELLED, 22305:CANCELLED, 22415:COMPLETED | [] | True |
| 6 | P12-TP4_D4-TP4-EP4 | gốc | 22273:COMPLETED, 22413:CANCELLED, 22416:COMPLETED | [] | True |
| 8 | P8-TP2_D8-TP8-EP8 | gốc | 22300:CANCELLED, 22417:COMPLETED, 22524:COMPLETED | [] | True |
| 10 | P8-TP8-EP2_D8-TP2-EP2 | EP2 variant | 22468:COMPLETED | [] | False |
| 11 | P8-TP8-EP2_D8-TP8-EP8 | EP2 variant | 22509:FAILED, 22538:FAILED, 22750:COMPLETED, 22778:FAILED, 22809:COMPLETED | [] | True |
| 13 | P4-TP2_D12-TP4-EP4 | gốc | 22517:COMPLETED | [] | True |
| 16 | P12-TP2_D4-TP4-EP4 | gốc | 22532:COMPLETED | [] | True |

Bản vá truyền KV theo request, nếu áp dụng, được ghi riêng ở cột Transport. Nó giữ weights, precision và phép tính model; số đo có bản vá là serving stack đã sửa.

## Số đo

| Job | Config | Transport | Lượt/N | SLA | Good tokens/s | Cancelled |
|---|---|---|---|---:|---:|---:|
| 22270 | P8-TP2_D8-TP4-EP4 | image gốc | sweep/N16 | 91.95% | 676.49 | 0 |
| 22270 | P8-TP2_D8-TP4-EP4 | image gốc | sweep/N32 | 96.08% | 1212.82 | 0 |
| 22270 | P8-TP2_D8-TP4-EP4 | image gốc | sweep/N40 | 96.72% | 1406.54 | 0 |
| 22270 | P8-TP2_D8-TP4-EP4 | image gốc | sweep/N48 | 92.08% | 1540.68 | 0 |
| 22414 | P8-TP2_D8-TP4-EP4 | image gốc | confirm/N48 | 86.17% | 1479.32 | 0 |
| 22294 | P8-TP8-EP2_D8-TP4-EP4 | hetero-tp-request-descriptors-v1 | confirm/N32 | 95.87% | 1422.96 | 0 |
| 22294 | P8-TP8-EP2_D8-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N16 | 100.00% | 834.55 | 0 |
| 22294 | P8-TP8-EP2_D8-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N32 | 98.82% | 1419.14 | 0 |
| 22294 | P8-TP8-EP2_D8-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N40 | 78.64% | 1292.36 | 0 |
| 22294 | P8-TP8-EP2_D8-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N48 | 67.90% | 1299.88 | 0 |
| 22415 | P8-TP4_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | confirm/N48 | 97.44% | 1912.30 | 0 |
| 22415 | P8-TP4_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | sweep/N16 | 100.00% | 910.22 | 0 |
| 22415 | P8-TP4_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | sweep/N32 | 99.42% | 1462.13 | 0 |
| 22415 | P8-TP4_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | sweep/N40 | 95.75% | 1744.23 | 0 |
| 22415 | P8-TP4_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | sweep/N48 | 90.95% | 1788.65 | 0 |
| 22273 | P12-TP4_D4-TP4-EP4 | image gốc | sweep/N16 | 100.00% | 742.33 | 0 |
| 22273 | P12-TP4_D4-TP4-EP4 | image gốc | sweep/N32 | 70.62% | 905.91 | 0 |
| 22273 | P12-TP4_D4-TP4-EP4 | image gốc | sweep/N40 | 48.19% | 751.15 | 0 |
| 22273 | P12-TP4_D4-TP4-EP4 | image gốc | sweep/N48 | 15.00% | 272.46 | 0 |
| 22416 | P12-TP4_D4-TP4-EP4 | image gốc | confirm/N16 | 100.00% | 828.11 | 0 |
| 22417 | P8-TP2_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | confirm/N32 | 94.21% | 1233.68 | 0 |
| 22417 | P8-TP2_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | sweep/N16 | 89.77% | 666.52 | 0 |
| 22417 | P8-TP2_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | sweep/N32 | 91.03% | 1089.79 | 0 |
| 22417 | P8-TP2_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | sweep/N40 | 86.47% | 1202.92 | 0 |
| 22417 | P8-TP2_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | sweep/N48 | 79.38% | 615.97 | 1 |
| 22524 | P8-TP2_D8-TP8-EP8 | hetero-tp-request-descriptors-v1 | sweep/N48 | 62.26% | 785.31 | 0 |
| 22468 | P8-TP8-EP2_D8-TP2-EP2 | hetero-tp-request-descriptors-v1 | sweep/N16 | 80.72% | 574.18 | 0 |
| 22468 | P8-TP8-EP2_D8-TP2-EP2 | hetero-tp-request-descriptors-v1 | sweep/N32 | 62.60% | 686.56 | 0 |
| 22468 | P8-TP8-EP2_D8-TP2-EP2 | hetero-tp-request-descriptors-v1 | sweep/N40 | 51.90% | 639.09 | 0 |
| 22468 | P8-TP8-EP2_D8-TP2-EP2 | hetero-tp-request-descriptors-v1 | sweep/N48 | 39.88% | 569.57 | 0 |
| 22750 | P8-TP8-EP2_D8-TP8-EP8 | image gốc | sweep/N16 | 97.17% | 906.64 | 0 |
| 22750 | P8-TP8-EP2_D8-TP8-EP8 | image gốc | sweep/N32 | 94.08% | 1373.62 | 0 |
| 22809 | P8-TP8-EP2_D8-TP8-EP8 | equal-tp8-request-descriptors-v1 | confirm/N32 | 95.38% | 1507.96 | 0 |
| 22809 | P8-TP8-EP2_D8-TP8-EP8 | equal-tp8-request-descriptors-v1 | sweep/N16 | 98.15% | 933.50 | 0 |
| 22809 | P8-TP8-EP2_D8-TP8-EP8 | equal-tp8-request-descriptors-v1 | sweep/N32 | 93.02% | 1393.62 | 0 |
| 22809 | P8-TP8-EP2_D8-TP8-EP8 | equal-tp8-request-descriptors-v1 | sweep/N40 | 89.50% | 1624.14 | 0 |
| 22809 | P8-TP8-EP2_D8-TP8-EP8 | equal-tp8-request-descriptors-v1 | sweep/N48 | 86.06% | 1708.25 | 0 |
| 22517 | P4-TP2_D12-TP4-EP4 | hetero-tp-request-descriptors-v1 | confirm/N16 | 98.67% | 837.15 | 0 |
| 22517 | P4-TP2_D12-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N16 | 91.76% | 691.90 | 0 |
| 22517 | P4-TP2_D12-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N32 | 86.39% | 1024.23 | 0 |
| 22517 | P4-TP2_D12-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N40 | 80.59% | 1109.96 | 0 |
| 22517 | P4-TP2_D12-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N48 | 65.97% | 984.81 | 0 |
| 22532 | P12-TP2_D4-TP4-EP4 | hetero-tp-request-descriptors-v1 | confirm/N16 | 100.00% | 776.25 | 0 |
| 22532 | P12-TP2_D4-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N16 | 91.46% | 640.97 | 0 |
| 22532 | P12-TP2_D4-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N32 | 85.61% | 979.41 | 0 |
| 22532 | P12-TP2_D4-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N40 | 36.47% | 521.40 | 0 |
| 22532 | P12-TP2_D4-TP4-EP4 | hetero-tp-request-descriptors-v1 | sweep/N48 | 18.88% | 299.64 | 0 |

[Registry phục hồi](topology-repair/recovery.json) · [Đợt đầu](TOPOLOGY_RESULTS.md) · [Log và lịch sử](RUNS.md)
