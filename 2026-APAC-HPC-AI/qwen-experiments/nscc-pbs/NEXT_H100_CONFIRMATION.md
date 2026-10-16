# Bước xác nhận H100 sau 04→05→06 — 16/10/2026 06:28 UTC

Đây là kế hoạch có điều kiện trong research đã được giao, chưa phải job đã gửi,
chưa reserve thêm SU. Không sửa ba payload đang chạy/chờ hoặc release dependency.

## Dữ liệu làm cơ sở

Snapshot 220720 lúc 06:26:01 UTC đang R: export N32/N34/N36 đạt
1692,166/1754,073/1787,737 good tokens/s, SLA 100% cả ba; hơn baseline
220575 cùng N lần lượt 7,7667%/7,9034%/31,8048%. N36 baseline chỉ SLA
82,1218%, nên phần tăng goodput tại N36 bao gồm thay đổi tỷ lệ request đạt SLA;
không coi 31,8% là tăng raw throughput. Đây là export live, chưa terminal,
chưa đủ raw/protocol/runtime/short/long. Chưa có control cùng N38 trở lên.
Evidence: inspection/wake-20261016-0625UTC/live-point-summary.json.

## Thu và chọn câu hỏi tiếp

1. Thu terminal 220720, 220721, 220722 qua collect-run.py; rehash seal,
   review-candidate-sweep.py so từng candidate độc lập với 220575 cùng N.
   Capture serverinfo 05/06 khi own/R qua collector đã chuẩn bị, một lần khi
   endpoint sẵn sàng. Giữ mọi điểm fail/deferred và mọi collection attempt.
2. Đọc PBS stdout khai báo và log role: reported backend không đủ census 8rank,
   KV auto chưa chứng minh BF16. Nếu terminal vẫn thiếu log, ưu tiên chuẩn bị
   logging trực tiếp bên trong task pbsdsh cho CẢ control và candidate tiếp;
   không tăng throughput claim hoặc coi runtime gate đã đạt.
3. Chỉ chọn candidate khi terminal exit0, payload đúng, full60/120/30 và
   không lỗi/hủy ở các điểm dùng so sánh, short không có regression mới,
   long PASSED, runtime được review. Nếu long missing/deferred hoặc runtime
   thiếu thì xử lý đúng lỗ hổng quan sát trước khi kết luận; không promotion.
4. Chọn một candidate có lợi thế cùng N32/N34 rõ ràng và không đổi chất lượng.
   MNNVL04 hiện là giả thuyết mạnh, chưa chọn winner trước kết quả05/06.
   Prefetch06 là policy startup: đánh giá bằng reported load/readiness và
   confounder node/cache/TP/EP; không chọn nó chỉ vì một điểm throughput cao.

## Cặp xác nhận giới hạn

Nếu đủ gates và queue/budget cho phép, chuẩn bị đúng HAI allocation nối đuôi:
control mới từ load-sweep-03 và repeat của một candidate đã chọn. Mỗi allocation
16H100, tối đa45phút/1536SU, tổng max3072SU; không reserve cho đến khi reviewed
source và refresh toàn bộ ownqueue/myprojects, reconcile terminal charges dưới
budget.lock. Giữ cap16384SU total, projectreserve13000SU, max3PBS active và chỉ
1 allocation16GPU running bằng afterany. Có thể nối sau220722 khi slot hợp lệ;
không gửi duplicate hoặc vượt3active. Tại snapshot06:25 đủ3slot nên chưa qsub.

Hai allocation giữ cùng image/model/tokenizer/FP8, topology2P×TP4+1D×TP8EP8,
RR/NIXL, protocol60/120/30, seed/dataset/SLO, diagnostic và logging như nhau.
Giữ gridN32/34/36/38/40/42 và stop-on-fail hiện có; không tự thêmN44 trở lên.
So mỗi N với control cũ và control mới khi cả hai có điểm đó; nếu control dừng
ở36 thì N38+ của candidate vẫn chỉ là thông tin capacity, không gain cùngN.
Giữ caveat engine seed/node/cache/time drift và một cặp chưa đủ thống kê.

Cờ xác nhận mô tả chỉ khi candidate repeat có fullSLA>=90%,0errors/cancel,
short không regression,long PASSED,runtime đúng và hơn freshcontrol tại các
điểm cùngN đã định N32/N34; giữ mọi số đo và không chọn riêng peak.
Nếu lợi thế biến mất hoặc quality fail thì ghi kết quả âm, không gửi repeat
thứ ba tự động. Nếu các backend đều không đạt, chọn sửa nguyên nhân quan sát
được hoặc startup policy; không mở hàng loạt config/speculative draft branch.
Accuracy99% reference BTC và quyền promotion vẫn chưa được xác minh.

## Access and evidence update —16Oct2026 10:28UTC

At10:25 the existing helper finds no live VPN session before SSH. PBS terminal
states/ownqueue/credit for220720–220722 remain UNKNOWN, not cancelled or done.
No new auth/DUO, qsub or reservation release. Keep4608SU until fresh reconciliation.
A06:26 archive attempt exited1 because tar saw the running n38/confirm directory
change. Its102members enumerate to end; selected finishedN32/N34/N36 exports,
phase manifests and rawrequests were recovered without modifying the source.
Full60/120/30, actual timings/counts/latencies/lengths/goodrequest sums match for
those historical points; no errors/cancel. This is NOT a terminal seal or final
runtime/quality result. N38 remains excluded. Original archive/stderr retained.
Seeinspection/wake-20261016-1025UTC/h100-historical-live-point-review.json.
Resume the above conditional control/candidate pair only after all existing
terminal/quality/runtime/queue/credit gates; do not bypass missingNSCCaccess.

## Chuẩn bị CPU — 16/10/2026 10:59 UTC

Existingaccess vẫn thiếu10:55:37UTC,không refreshđược PBS/credit;giữ4608SU.
[Task logging](research-next/pbs-task-logging-01/README.md) có stagedshim/wrapper,
12/12CPUstub đạt, chưa tíchhợp/upload/PBS thật. Nếu finalrolelogs vẫnthiếu, áp
dụng cùnghai file/hash vàoCẢ hai bundlemới rồi reviewfullsource/seal; chưa chọn
candidate/reserve/submit. Đọcsidecar task-*.log khi review, không chỉ role.log.
Giữmọigate ởtrên;không chạyallocation riêng chỉđểtestlogging.
