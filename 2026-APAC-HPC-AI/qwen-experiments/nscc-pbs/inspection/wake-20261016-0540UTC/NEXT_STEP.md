# Phiếu bước tiếp —16/10/2026 05:42 UTC

Đã chuẩn bị từ các tool/plan hiện hành, chưa chạy lệnh review khi không có seal.
Làm việc tại `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments`.
Thư mục `NEW_REVIEW_DIR` phải là thư mục evidence mới của lượt tiếp theo.

| Trigger đã xác minh | Việc tiếp theo | Điều kiện kết luận |
|---|---|---|
| Watcher đã thu seal23934 | Chạy reviewer N54 dưới đây | So cả23780/23859 vàmean; giữ SLAfail riêng với thiếuevidence, không mởN56 |
| Có seal23973/23974/23975 | Chạy reviewerwave10 | Đọc mọirepeat,3control vàdrift,không chọnpeak; longfail/deferred/thiếu vẫn giữ số đo |
| Có seal24009 | Chạy reviewerMNNVLrepeat | So23924 vàN52controls,mean táchload; nếu replacement thì reviewmọiattempt bằng tay |
| Combo repeat vàlong đều đạtgate | Viết plancomboN54 cógiới hạn,kiểm queue mới | Cả3comboSLA>=95%,mỗiITL<=19,3ms,0error/cancel,no newshort,longPASSED,gainreproduced; không tựsubmit chỉ từcờ |
| SSH xác thực hiện có dùng được | Refresh ownPBSqueue+credit,thu220575 | Chưa có terminal/accounting thì khôngduplicate/qsub,khônggiải phóng1536SUreserve |
| 220575terminal,baselineN32đạt,ownqueue/credit/budget đủ | Tiếp pilot04 rồi05 rồi06 đãchuẩn bị | Dựtrù dướibudget.lock,1ownPBSjob,<=16GPU,<=45min,campaign16384SU,reserveproject13000SU |

Lệnh chỉ đọc evidence, output file phải mới:

```bash
python3 serving-tuning/review-n54.py 23934 --out NEW_REVIEW_DIR/dp-n54.json
python3 serving-tuning-10/review-wave10.py --out NEW_REVIEW_DIR/wave10.json
python3 serving-tuning-10/review-mnnvl-n54-repeat.py --out NEW_REVIEW_DIR/mnnvl-n54-repeat.json
```

Không cần chạy cả3tool mỗi lần pending; chỉ đọc nhánh vừa có seal mới. Không
rehash/audit lại snapshot bất biến khi không có câu hỏi mới. Queue05:40:37 đủ
5slot vàPriority; không hủy/requeue chỉ vìPriority.

Khi truy cập SSH thật sự được khôi phục, dùng quy trình thu vàreview đã có ở
`nscc-pbs/LOAD_SWEEP_REVIEW.md`. Không dùng `connect`/DUO/password để vượt lỗi
BatchMode trong lượt này. Quan sát snx-tun hiện có không chứng minh phiên24h.

EAGLE3 đã có suite14caCPU vàcapture/comparator; bước cần evidence mới là
runtimecontrol→controlrepeat→candidate sau khi gateGPU/target/draft được phép.
Chưa tải draft/upload/chạyGPU,không cho preflight thay quality/accuracy.
Không thêm mocktest hoặc staging trùng. Không thirdsuccessfulN54repeat,N56,
promotion hoặc đổi payloadqueued.
