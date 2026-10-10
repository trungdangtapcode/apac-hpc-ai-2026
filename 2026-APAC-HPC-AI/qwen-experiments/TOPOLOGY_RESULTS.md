# Đợt đầu: benchmark 17 topology Qwen

Cập nhật UTC: 2026-10-10T03:52:09.521873+00:00

Bảng này giữ số liệu đợt đầu. Tiến độ và số đo chạy lại nằm ở [kết quả phục hồi](RECOVERY_RESULTS.md).

**8/17 cấu hình có đủ bốn lượt sweep. 9 cấu hình chưa đo đủ.** Job FAILED/TIMEOUT hoặc chỉ khởi động được server không được tính là benchmark xong. Xem [đính chính và sửa lỗi](TOPOLOGY_REVIEW.md).

Mỗi cấu hình dùng đủ 16 H200, FP8 checkpoint chính thức, SGLang harbor, NIXL, KV auto, context 8192, memory fraction 0.90. Decode EP bằng TP. Worker TP2/4/8 nằm trong một node. P/D chia 4+12, 8+8, 12+4; TP phải chia hết số GPU mỗi giai đoạn.

Sweep N16/32/40/48: warmup 10s, đo 20s, grace 30s. Confirm điểm sweep tốt nhất qua SLA và không cancelled: 60s/120s/30s nếu còn đủ thời gian job 17 phút. Sweep ngắn chỉ dùng sàng lọc; confirm là đo nội bộ theo thời lượng BTC, chưa có accuracy/điểm BTC.

Warm tất cả cặp P/D bằng prompt ngắn riêng trước benchmark; không dùng seed/dataset benchmark. Payload và checksum được đóng băng trước submit; mỗi job giữ config, placement, logs và exports.

| # | Topology | P workers | D workers | Job | Trạng thái | Lượt có số đo |
|---:|---|---:|---:|---|---|---:|
| 1 | P8-TP4_D8-TP4-EP4 | 2 | 2 | 22219 | COMPLETED | 5 |
| 2 | P8-TP2_D8-TP4-EP4 | 4 | 2 | 22220 | FAILED | 0 |
| 3 | P8-TP8_D8-TP4-EP4 | 1 | 2 | 22221 | FAILED | 0 |
| 4 | P8-TP4_D8-TP8-EP8 | 2 | 1 | 22222 | FAILED | 0 |
| 5 | P4-TP4_D12-TP4-EP4 | 1 | 3 | 22231 | COMPLETED | 5 |
| 6 | P12-TP4_D4-TP4-EP4 | 3 | 1 | 22232 | FAILED | 0 |
| 7 | P8-TP2_D8-TP2-EP2 | 4 | 4 | 22233 | COMPLETED | 4 |
| 8 | P8-TP2_D8-TP8-EP8 | 4 | 1 | 22234 | FAILED | 0 |
| 9 | P8-TP4_D8-TP2-EP2 | 2 | 4 | 22235 | COMPLETED | 4 |
| 10 | P8-TP8_D8-TP2-EP2 | 1 | 4 | 22236 | FAILED | 0 |
| 11 | P8-TP8_D8-TP8-EP8 | 1 | 1 | 22238 | FAILED | 0 |
| 12 | P4-TP2_D12-TP2-EP2 | 2 | 6 | 22239 | COMPLETED | 4 |
| 13 | P4-TP2_D12-TP4-EP4 | 2 | 3 | 22240 | FAILED | 0 |
| 14 | P4-TP4_D12-TP2-EP2 | 1 | 6 | 22241 | COMPLETED | 4 |
| 15 | P12-TP2_D4-TP2-EP2 | 6 | 2 | 22242 | COMPLETED | 4 |
| 16 | P12-TP2_D4-TP4-EP4 | 6 | 1 | 22245 | FAILED | 0 |
| 17 | P12-TP4_D4-TP2-EP2 | 3 | 2 | 22246 | COMPLETED | 4 |

## Số đo đã có

| Job | Topology | Lượt/N | SLA | Good tokens/s | TTFT TB ms | ITL TB ms | Cancelled |
|---|---|---|---:|---:|---:|---:|---:|
| 22219 | P8-TP4_D8-TP4-EP4 | confirm/N40 | 97.82% | 1666.01 | 1229.46 | 17.11 | 0 |
| 22219 | P8-TP4_D8-TP4-EP4 | sweep/N16 | 100.00% | 811.49 | 743.84 | 14.76 | 0 |
| 22219 | P8-TP4_D8-TP4-EP4 | sweep/N32 | 100.00% | 1377.22 | 962.29 | 16.71 | 0 |
| 22219 | P8-TP4_D8-TP4-EP4 | sweep/N40 | 94.03% | 1488.57 | 1005.26 | 18.06 | 0 |
| 22219 | P8-TP4_D8-TP4-EP4 | sweep/N48 | 77.50% | 1428.23 | 960.64 | 18.64 | 0 |
| 22231 | P4-TP4_D12-TP4-EP4 | confirm/N40 | 97.40% | 1382.16 | 2399.38 | 15.74 | 0 |
| 22231 | P4-TP4_D12-TP4-EP4 | sweep/N16 | 100.00% | 846.89 | 853.45 | 13.63 | 0 |
| 22231 | P4-TP4_D12-TP4-EP4 | sweep/N32 | 100.00% | 1372.49 | 1336.89 | 14.92 | 0 |
| 22231 | P4-TP4_D12-TP4-EP4 | sweep/N40 | 98.54% | 1641.19 | 1173.44 | 16.35 | 0 |
| 22231 | P4-TP4_D12-TP4-EP4 | sweep/N48 | 88.21% | 1647.94 | 1277.92 | 16.95 | 0 |
| 22233 | P8-TP2_D8-TP2-EP2 | sweep/N16 | 80.52% | 545.72 | 1196.82 | 16.96 | 0 |
| 22233 | P8-TP2_D8-TP2-EP2 | sweep/N32 | 61.81% | 721.04 | 1296.52 | 19.06 | 0 |
| 22233 | P8-TP2_D8-TP2-EP2 | sweep/N40 | 43.50% | 595.82 | 1302.71 | 20.17 | 0 |
| 22233 | P8-TP2_D8-TP2-EP2 | sweep/N48 | 46.81% | 693.65 | 1778.51 | 20.18 | 0 |
| 22235 | P8-TP4_D8-TP2-EP2 | sweep/N16 | 82.35% | 597.15 | 754.09 | 16.86 | 0 |
| 22235 | P8-TP4_D8-TP2-EP2 | sweep/N32 | 66.67% | 804.38 | 1003.90 | 19.29 | 0 |
| 22235 | P8-TP4_D8-TP2-EP2 | sweep/N40 | 32.22% | 454.63 | 984.71 | 20.81 | 0 |
| 22235 | P8-TP4_D8-TP2-EP2 | sweep/N48 | 20.79% | 334.37 | 919.29 | 21.60 | 0 |
| 22239 | P4-TP2_D12-TP2-EP2 | sweep/N16 | 79.22% | 539.18 | 1310.97 | 16.03 | 0 |
| 22239 | P4-TP2_D12-TP2-EP2 | sweep/N32 | 75.18% | 803.98 | 2012.51 | 17.38 | 0 |
| 22239 | P4-TP2_D12-TP2-EP2 | sweep/N40 | 74.23% | 959.15 | 2189.72 | 17.21 | 0 |
| 22239 | P4-TP2_D12-TP2-EP2 | sweep/N48 | 60.66% | 848.67 | 2596.56 | 17.45 | 0 |
| 22241 | P4-TP4_D12-TP2-EP2 | sweep/N16 | 82.76% | 610.74 | 881.53 | 15.71 | 0 |
| 22241 | P4-TP4_D12-TP2-EP2 | sweep/N32 | 86.00% | 1022.74 | 1348.52 | 17.72 | 0 |
| 22241 | P4-TP4_D12-TP2-EP2 | sweep/N40 | 65.57% | 971.47 | 1175.33 | 18.93 | 0 |
| 22241 | P4-TP4_D12-TP2-EP2 | sweep/N48 | 47.49% | 749.54 | 1461.30 | 19.92 | 0 |
| 22242 | P12-TP2_D4-TP2-EP2 | sweep/N16 | 76.06% | 471.17 | 1063.13 | 18.94 | 0 |
| 22242 | P12-TP2_D4-TP2-EP2 | sweep/N32 | 14.84% | 154.12 | 1199.80 | 22.44 | 0 |
| 22242 | P12-TP2_D4-TP2-EP2 | sweep/N40 | 6.49% | 79.69 | 1253.23 | 23.96 | 0 |
| 22242 | P12-TP2_D4-TP2-EP2 | sweep/N48 | 1.16% | 15.49 | 1532.32 | 24.82 | 0 |
| 22246 | P12-TP4_D4-TP2-EP2 | sweep/N16 | 58.33% | 360.17 | 806.19 | 19.56 | 0 |
| 22246 | P12-TP4_D4-TP2-EP2 | sweep/N32 | 3.85% | 40.89 | 1004.17 | 23.29 | 0 |
| 22246 | P12-TP4_D4-TP2-EP2 | sweep/N40 | 0.62% | 7.89 | 931.53 | 24.72 | 0 |
| 22246 | P12-TP4_D4-TP2-EP2 | sweep/N48 | 0.52% | 6.85 | 1145.21 | 26.42 | 0 |

## Điểm đo dài cao nhất trong đợt này

Mốc trước đợt này: 09/N40, job 22200, **1649.27 good tokens/s, 97.81% SLA**, cancelled=0.

**P8-TP4_D8-TP4-EP4 /N40**: **1666.01 good tokens/s**, 97.82% SLA, job 22219. Đây là số đo một deployment, chưa đánh giá độ dao động.

## Lỗi được giữ làm dữ kiện

- Job 22220, P8-TP2_D8-TP4-EP4, FAILED:
  - [runs/22220/decode-0.log](runs/22220/decode-0.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22220/decode-1.log](runs/22220/decode-1.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22220/pair-warmup.log](runs/22220/pair-warmup.log): `srun: error: g1: task 0: Exited with exit code 1`
- Job 22221, P8-TP8_D8-TP4-EP4, FAILED:
  - [runs/22221.err](runs/22221.err): `FATAL: worker/router step 1545193 exited before readiness`
  - [runs/22221/decode-0.log](runs/22221/decode-0.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22221/decode-1.log](runs/22221/decode-1.log): `srun: error: Timed out waiting for job step to complete`
- Job 22222, P8-TP4_D8-TP8-EP8, FAILED:
  - [runs/22222/decode-0.log](runs/22222/decode-0.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22222/pair-warmup.log](runs/22222/pair-warmup.log): `srun: error: g1: task 0: Exited with exit code 1`
  - [runs/22222/prefill-0.log](runs/22222/prefill-0.log): `srun: error: Timed out waiting for job step to complete`
- Job 22232, P12-TP4_D4-TP4-EP4, FAILED:
  - [runs/22232/decode-0.log](runs/22232/decode-0.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22232/pair-warmup.log](runs/22232/pair-warmup.log): `srun: error: g1: task 0: Exited with exit code 1`
  - [runs/22232/prefill-0.log](runs/22232/prefill-0.log): `srun: error: Timed out waiting for job step to complete`
- Job 22234, P8-TP2_D8-TP8-EP8, FAILED:
  - [runs/22234.err](runs/22234.err): `FATAL: worker/router step 1585227 exited before readiness`
  - [runs/22234/decode-0.log](runs/22234/decode-0.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22234/prefill-0.log](runs/22234/prefill-0.log): `srun: error: Timed out waiting for job step to complete`
- Job 22236, P8-TP8_D8-TP2-EP2, FAILED:
  - [runs/22236.err](runs/22236.err): `FATAL: worker/router step 1599156 exited before readiness`
  - [runs/22236/decode-0.log](runs/22236/decode-0.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22236/decode-1.log](runs/22236/decode-1.log): `srun: error: Timed out waiting for job step to complete`
- Job 22238, P8-TP8_D8-TP8-EP8, FAILED:
  - [runs/22238.err](runs/22238.err): `FATAL: worker/router step 1602373 exited before readiness`
  - [runs/22238/decode-0.log](runs/22238/decode-0.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22238/prefill-0.log](runs/22238/prefill-0.log): `srun: error: g1: task 0: Killed`
- Job 22240, P4-TP2_D12-TP4-EP4, FAILED:
  - [runs/22240/decode-0.log](runs/22240/decode-0.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22240/decode-1.log](runs/22240/decode-1.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22240/decode-2.log](runs/22240/decode-2.log): `srun: error: Timed out waiting for job step to complete`
- Job 22245, P12-TP2_D4-TP4-EP4, FAILED:
  - [runs/22245/decode-0.log](runs/22245/decode-0.log): `srun: error: Timed out waiting for job step to complete`
  - [runs/22245/pair-warmup.log](runs/22245/pair-warmup.log): `srun: error: g1: task 0: Exited with exit code 1`
  - [runs/22245/prefill-0.log](runs/22245/prefill-0.log): `srun: error: Timed out waiting for job step to complete`

[Registry cấu hình, hash payload, trạng thái và metrics](topology-sweep/registry.json) · [JSON tất cả số đo](topology-comparison.json) · [Sổ lỗi/các lần chạy trước](RUNS.md)
