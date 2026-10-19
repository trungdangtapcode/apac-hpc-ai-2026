## Language policy — 2026-10-17 10:10 UTC

The user clarified: **Vietnamese for chat only. English for the codebase and all work artifacts**, including code, comments, documentation, research plans, reports, notes, tutorials, and submission materials. This supersedes earlier permission to write tutorials or learning notes in Vietnamese. Use readable English with normal spacing and explain unfamiliar terms. Do not translate immutable raw logs or historical experiment evidence.

The current prefill experiment plan has been rewritten in English. Existing Vietnamese historical documents remain historical; this update does not claim they have all been translated.

# Bộ nhớ dự án: đọc từ đây

Đây là điểm tra cứu lâu dài của cuộc trò chuyện APAC-HPC-AI2026. Các lượt Codex
mới phải đọc file này và trạng thái hiện tại trước khi làm tiếp.

| Cần tìm gì? | Nơi đọc |
|---|---|
| Trạng thái, các điều đã sửa, bước tiếp | [CURRENT.md](CURRENT.md) |
| Kiến thức hỏi–đáp từ cuộc trò chuyện | [Sổ tay tổng hợp](../tutorial/14-so-tay-hoi-dap.md) |
| Toàn bộ hướng dẫn theo chủ đề | [Mục lục tutorial](../tutorial/README.md) |
| Yêu cầu và quyết định của người dùng | [DECISIONS.md](DECISIONS.md) |
| Các mốc, kết quả và lỗi quan trọng | [TIMELINE.md](TIMELINE.md) |
| Tiến độ tự chạy mới nhất | [LATEST.md](../research-autopilot/LATEST.md) |
| Lịch sử từng lượt tự chạy | [HISTORY.md](../research-autopilot/HISTORY.md) |
| Chính sách thực thi, budget và việc tiếp | [POLICY.md](../research-autopilot/POLICY.md) |
| Sổ thí nghiệm, logs, phép đo | [RUNS.md](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RUNS.md) |
| So sánh serving hiện có | [SERVING_TUNING_RESULTS.md](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/SERVING_TUNING_RESULTS.md) |
| Đối soát credit và khoản dự trù | [nscc-budget.json](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json) |

## Cách giữ lịch sử đúng

- Có câu hỏi kiến thức: bổ sung câu trả lời dễ hiểu vào sổ tay, link bài chi tiết.
- Có quyết định mới: cập nhật DECISIONS và POLICY nếu ảnh hưởng lượt tự chạy.
- Có kết quả/lỗi: giữ artifact, ghi job ID, thời gian, môi trường và điều đã xác minh.
- Có kết luận bị sửa: cập nhật CURRENT, nêu kết luận cũ đã sai/chưa đủ bằng chứng;
  giữ mốc lịch sử thay vì tiếp tục dùng cả hai kết luận mâu thuẫn.
- Khi báo trạng thái: kiểm tra scheduler/VPN thực; không chỉ đọc ghi chú.
- Không lưu bí mật xác thực. Đây là bộ nhớ kiến thức và công việc, không phải
  bản chép nguyên văn mọi tin nhắn hoặc bằng chứng đã nộp bài cho BTC.

## Tiết kiệm quotaCodex
CURRENT chỉgiữ trạng thái hiện tại,tối đa120dòng; lịch sử nằmriêng. Khôngđọctoàn
bộHISTORY/archive mỗi wake; chỉtra phần liênquan. Khônglặp audit bấtbiến. Xem
research-autopilot/usage-audit-20261016.json và usage-fix-validation.json.

## Trạng thái tự động

Codex autopilot đã tắt theo yêu cầu người dùng 2026-10-16 13:42:29 UTC. Không tự bật lại.
Chi tiết: [CURRENT.md](CURRENT.md). VPN và job GPU được giữ nguyên.

## Chú ý trước khi gửi job

Research + output/log/quality/runtime/chi phí các lượt trước → giả thuyết và control → kiểm budget → submit. Ưu tiên thông tin hữu ích trên mỗi SU và thời gian; không lấp queue mù quáng. Chi tiết: [DECISIONS.md](DECISIONS.md).

## Cách viết ghi chú

Viết câu rõ ràng, đầy đủ khoảng trắng; giải thích thuật ngữ khi cần. Không nén tài liệu thành chuỗi từ viết dính hoặc quá nhiều viết tắt. Đưa chi tiết kỹ thuật vào phần riêng hoặc link nguồn.

## Private GitHub publication

The private repository is [apac-hpc-ai-research](https://github.com/trungdangtapcode/apac-hpc-ai-research). Read [publication, commit history and recovery coverage](../reports/github-publication-20261019/REPORT.md). GitHub contains the Git portion; large external objects still require their separate backup.

## Research progression and next decisions

[How Qwen serving reached 2938.628 good tokens/s](../reports/research-journey-20261019/REPORT.md) explains the measured trajectory, metrics and units, matched controls, failure lessons, current evidence limits and when to change research direction. Read it as a dated report; current scheduler state still needs checking.

[Illustrated research journey](../reports/research-journey-20261019/diagram/README.md): GPU layout, six H200 stages, measured throughput trajectory, failed branches, separate H100 lane and future verification gates. SVG, PNG, PDF and editable source are retained with the dated evidence.

## Complete retained research reasoning

[Start with the complete research journal](../reports/research-journey-20261019/journal/README.md): 32 stages explaining the question, change, result, assessment and next decision, including failed branches and corrections. The dated coverage audit verifies 247 retained Markdown documents and indexes 194 own research jobs; 127 have dedicated purpose/observation/lesson sections. This is retained written history, not a guarantee that every historical chat statement survived.
