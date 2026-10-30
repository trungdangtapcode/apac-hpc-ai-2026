#!/usr/bin/env python3
"""Render bilingual learning transcripts for the frozen 40-slide presentation."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

WORKSPACE = Path(__file__).resolve().parents[1]
REPORT = WORKSPACE / 'reports/ai-final-report-20261030'
DECK = WORKSPACE / 'VNUHCM - TripleU/Presentation/TripleU_APAC2026_Presentation.pptx'

GLOSSARY = [
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
    ('NIXL', 'The transfer layer used here to move KV state between prefill and decode workers.', 'Lớp truyền dữ liệu được dùng ở đây để chuyển KV từ worker prefill sang worker decode.'),
    ('FP8 / BF16', '8-bit floating-point / 16-bit bfloat formats. Weights, activations and KV can use different formats.', 'Định dạng số thực 8 bit / bfloat 16 bit. Trọng số, activation và KV có thể dùng định dạng khác nhau.'),
    ('FI / FA3 / DG / HPC-Ops', 'FlashInfer / FlashAttention 3 / DeepGEMM / the reused HPC-Ops kernel implementation. HPC-Ops is not the OpenFOAM HPC track.', 'FlashInfer / FlashAttention 3 / DeepGEMM / triển khai kernel HPC-Ops được tái sử dụng. HPC-Ops không phải track HPC OpenFOAM.'),
    ('kernel / GEMM', 'A GPU computation routine / general matrix multiplication. Faster isolated kernels do not automatically improve the whole service.', 'Một chương trình tính toán trên GPU / phép nhân ma trận tổng quát. Kernel riêng lẻ nhanh hơn chưa chắc làm cả dịch vụ nhanh hơn.'),
    ('MNNVL / collective', 'Multi-node NVLink communication path / an operation in which multiple ranks communicate together. The actual enabled path must be checked.', 'Đường giao tiếp Multi-node NVLink / phép giao tiếp có nhiều rank cùng tham gia. Cần kiểm tra đường thực thi thực tế được bật.'),
    ('CUDA graph / bucket', 'A captured GPU execution graph / a selected execution shape to capture. Bucket count is not request concurrency.', 'Đồ thị thực thi GPU được capture / một kích thước thực thi được chọn để capture. Số bucket không phải concurrency.'),
    ('baseline / control / candidate', 'Reference configuration / comparison arm / proposed changed configuration. State the exact baseline for every percentage.', 'Cấu hình mốc / nhánh đối chứng / cấu hình thử thay đổi. Mỗi phần trăm tăng giảm cần chỉ rõ mốc so sánh.'),
    ('matched trial / repeat', 'A comparison preserving intended factors except the tested change / another allocation to check reproducibility. Neither automatically proves causality.', 'So sánh giữ các yếu tố dự định, chỉ đổi yếu tố cần thử / lần cấp tài nguyên khác để kiểm tra tái lập. Cả hai không tự động chứng minh quan hệ nhân quả.'),
    ('ms / s / tokens/s / req/s', '1,000 ms = 1 s. tokens/s counts tokens per second; req/s counts requests per second.', '1.000 ms = 1 giây. tokens/s là token mỗi giây; req/s là request mỗi giây.'),
    ('% / percentage points', 'A move from 90% to 95% is +5 percentage points, or +5.56% relative to 90%; these are different.', 'Từ 90% lên 95% là tăng 5 điểm phần trăm, hoặc tăng tương đối 5,56% so với 90%; hai cách nói khác nhau.'),
    ('2,989.175 / 2.989,175', 'The deck uses English separators: comma for thousands and point for decimals. These two forms express the same value in English and Vietnamese conventions.', 'Slide dùng kiểu Anh: dấu phẩy tách hàng nghìn, dấu chấm tách phần thập phân. 2,989.175 trên slide tương đương 2.989,175 theo cách viết Việt; không phải hai kết quả khác nhau.'),
    ('MPI rank / affinity / NUMA', 'An MPI process / placement on CPU cores / a CPU memory architecture with different local and remote access costs. CPU HPC ranks differ from GPU serving ranks.', 'Một tiến trình MPI / gắn tiến trình vào lõi CPU / kiến trúc bộ nhớ CPU có chi phí truy cập gần và xa khác nhau. Rank trong HPC CPU khác với rank serving GPU.'),
    ('Scotch / Hierarchical / graph cut', 'Mesh partitioning methods / another partitioning method / a partition-boundary proxy. A smaller cut is not automatically faster runtime.', 'Các phương pháp chia lưới / một phương pháp chia lưới khác / chỉ số đại diện cho biên giữa các phần chia. Cut nhỏ hơn không tự động có thời gian chạy nhanh hơn.'),
]


def introduction(lang, digest):
    if lang == 'vi':
        return f'''# Transcript và hướng dẫn hiểu từng slide — Tiếng Việt

Đây là **lời thuyết trình mẫu và tài liệu học**, không phải bản chép lại một buổi nói đã diễn ra. Tài liệu đi theo đúng 40 slide của bản trình chiếu hiện tại. Bản tiếng Việt được tạo theo yêu cầu riêng của bạn; mã nguồn và các báo cáo khác vẫn dùng tiếng Anh.

**Cách dùng:** mở slide, đọc phần “Slide muốn nói gì”, nhìn hình theo “Cách đọc”, rồi luyện phần “Lời nói mẫu”. Các phần còn lại giúp chuẩn bị trả lời câu hỏi. Không cần đọc toàn bộ hướng dẫn thành tiếng. Hãy dùng “chúng tôi quan sát”, “giả thuyết của chúng tôi”, và “chưa xác định được” đúng với mức bằng chứng.

- **Slide 1–24:** phần AI chính. Dùng [kế hoạch 15–20 phút](PRESENTATION_PLAN.md); không đọc hết 24 lời nói mẫu nếu vượt thời gian.
- **Slide 25–32:** phần AI dự phòng khi được hỏi. Slide 31–32 vẫn thuộc nhóm dự phòng dù tiêu đề không có chữ Appendix.
- **Slide 33–40:** giải thích phần HPC đang có trong cùng deck, chỉ đọc và diễn giải. Trạng thái job trên các slide này là **ảnh chụp ngày 23/10**, không phải trạng thái trực tiếp ngày 30/10. Hướng dẫn này không cập nhật hay xác nhận kết quả HPC mới. Thời lượng AI không bao gồm mặc định phần HPC.
- Màu sắc có ý nghĩa **theo từng slide**. Cam không luôn là “thắng” hay “thua”. Ảnh nền, gradient và đường trang trí cuối slide không biểu diễn dữ liệu.
- **↑ / ↓** thường là hướng mong muốn tối ưu, không khẳng định số liệu thực tế đã tăng/giảm. “Không có trục” nghĩa là sơ đồ/bảng/card, không cần tự suy ra trục X/Y.
- Nghiên cứu đã dừng theo yêu cầu. Các việc “tiếp theo” trong slide là đề xuất hoặc câu chuyện tại thời điểm đó, không phải job mới đã chạy.

Nguồn: [PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), [PDF](../../submission-review/ai-journey-update-20261030/TripleU_APAC2026_Presentation.pdf), [bản tiếng Anh](TRANSCRIPT_EN.md). SHA-256 của PowerPoint: `{digest}`. Đây là transcript của phiên bản này; đổi deck thì cần kiểm tra lại hướng dẫn.

## Từ vựng dùng xuyên suốt

| Ký hiệu / thuật ngữ | Hiểu đơn giản |
|---|---|
'''
    return f'''# Slide-by-slide transcript and learning guide — English

This is a **proposed speaking script and learning guide**, not a verbatim record of a delivered talk. It follows all 40 slides of the current presentation. The separately requested Vietnamese companion is a narrow language exception; code and other reports remain English.

**How to use it:** open the slide, read its purpose, follow the reading instructions, then rehearse the spoken script. Use the other sections to prepare answers. Do not read every explanatory paragraph aloud. Distinguish “we observed,” “our hypothesis was,” and “we have not established.”

- **Slides 1–24:** main AI talk. Follow the [15–20 minute plan](PRESENTATION_PLAN.md); select and shorten the scripts when rehearsing.
- **Slides 25–32:** AI backup material. Slides 31–32 remain backups even though their titles omit Appendix.
- **Slides 33–40:** read-only explanation of the existing HPC section. Its scheduler statements are **23 October snapshots**, not live 30 October status. This guide neither updates nor independently certifies later HPC work. Do not automatically include HPC in the AI time allowance.
- Colors have **slide-local meanings**. Orange does not always mean a win or a failure. Background photographs, gradients and footer decorations are not measurements.
- **↑ / ↓** generally indicate the desired optimization direction, not an observed increase/decrease. “No axes” means a table, card or schematic; do not invent X/Y quantities.
- Research has stopped at the owner's request. Future actions shown on slides are proposals or historical next decisions, not newly executed jobs.

Sources: [PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx), [PDF](../../submission-review/ai-journey-update-20261030/TripleU_APAC2026_Presentation.pdf), [Vietnamese companion](TRANSCRIPT_VI.md). PowerPoint SHA-256: `{digest}`. This guide describes that version; recheck it if the deck changes.

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
    labels = ['Slide muốn nói gì', 'Nhìn thấy gì trên slide', 'Thuật ngữ và ký hiệu', 'Cách đọc hình, trục, đơn vị và màu', 'Đánh đổi và mức độ bằng chứng', 'Lời nói mẫu', 'Điều không nên nói', 'Câu chuyển slide'] if vi else ['Purpose', 'What is on the slide', 'Terms and symbols', 'How to read the figure, axes, units and colors', 'Tradeoff and strength of evidence', 'Spoken script', 'Avoid this interpretation', 'Transition']
    evidence = [('observation', 'Quan sát', 'Observation'), ('hypothesis', 'Giả thuyết', 'Hypothesis'), ('conclusion', 'Kết luận được hỗ trợ', 'Supported conclusion'), ('unknown', 'Chưa biết / giới hạn', 'Unknown / limitation')]
    for s in records:
        n = s['slide']; d = s[lang]
        image_path = f'../../submission-review/ai-journey-update-20261030/slides/assets/slide-{n:02d}.png' if n <= 32 else f'transcript-assets/slide-{n:02d}.png'
        out.append(f'\n---\n\n<a id="slide-{n:02d}"></a>\n\n## Slide {n:02d} — {s["title"]}\n\n')
        out.append(f'![Slide {n:02d}]({image_path})\n\n')
        if n == 25:
            out.append('**Phần dự phòng AI: chỉ mở khi cần giải thích sâu hơn.**\n\n' if vi else '**AI backup section: open when a deeper explanation is needed.**\n\n')
        if n >= 33:
            out.append('**Phần HPC giữ nguyên: diễn giải slide hiện có, không phải cập nhật trạng thái hay kết quả mới.**\n\n' if vi else '**Unchanged HPC section: explanation of the existing slide, not a new status or result update.**\n\n')
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
    records = []
    for path in sorted((REPORT / 'transcript-parts').glob('*.json')):
        records.extend(json.loads(path.read_text()))
    records.sort(key=lambda s: s['slide'])
    assert [s['slide'] for s in records] == list(range(1, 41)), 'Need exactly 40 unique slides.'
    for s in records:
        actual = source['slides'][s['slide'] - 1]
        assert s['title'] in [' '.join(t.split()) for t in actual['texts']], f'Title mismatch on slide {s["slide"]}'
        for lang in ['en', 'vi']:
            d = s[lang]
            assert all(d[k] for k in ['purpose', 'visual', 'terms', 'reading', 'tradeoff', 'script', 'caution', 'transition'])
            assert all(d['tradeoff'][k] for k in ['observation', 'hypothesis', 'conclusion', 'unknown'])
            assert len(d['script'].split()) >= 25
    for lang in ['vi', 'en']:
        body = render(records, lang, digest)
        assert len(re.findall(r'^## Slide \d{2} —', body, re.MULTILINE)) == 40
        for target in re.findall(r'\]\(([^)]+)\)', body):
            if not target.startswith(('#', 'https://', 'http://')):
                assert (REPORT / unquote(target)).is_file(), f'Missing local link: {target}'
        (REPORT / f'TRANSCRIPT_{lang.upper()}.md').write_text(body)
    summary = dict(deck_sha256=digest, slides=40, ai_main=list(range(1, 25)), ai_backup=list(range(25, 33)), existing_hpc=list(range(33, 41)), languages=['vi', 'en'], scope='Standalone learning transcripts; no deck, package, HPC payload, research or scheduler mutation.', checks=['40 unique source-matched titles in both languages', 'All per-slide explanatory fields populated', 'All relative document and image links resolve', 'No truncated ellipsis placeholders', 'Deck identity unchanged'], files={})
    for lang in ['VI', 'EN']:
        p = REPORT / f'TRANSCRIPT_{lang}.md'
        summary['files'][p.name] = dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
    (REPORT / 'transcript-validation.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
