"""Generate a Vietnamese report from canonical measurement exports only."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent
ids = {'22135': 'baseline07', '22143': 'baseline07', '22147': 'baseline07', '22197': 'baseline07', '22131': 'candidate09', '22200': 'candidate09'}
rows = []
for job, topology in ids.items():
    p = root / 'runs' / job
    if p.is_dir():
        out = subprocess.run(
            ['python3', str(root / 'summarize.py'), str(p)],
            capture_output=True, text=True, check=True,
        )
        metrics = json.loads(out.stdout)
        (p / 'summary.json').write_text(out.stdout)
        rows.extend({'job': job, 'topology': topology, **r} for r in metrics)
(root / 'comparison.json').write_text(json.dumps(rows, indent=2))

lines = [
    '# Kết quả thử Qwen trên 16 H200', '',
    'Cập nhật UTC: ' + datetime.now(timezone.utc).isoformat(), '',
    '**Phạm vi:** model chính thức Qwen3-235B-A22B-Instruct-2507-FP8; '
    'cùng images SGLang/AIPerf, workload 4000 input /200 output, seed 2026. '
    'Đây là benchmark nội bộ, chưa phải điểm BTC hoặc kiểm tra chất lượng.', '',
    '- **07:** 4 prefill worker × TP2; 2 decode worker × TP4/EP4.',
    '- **09:** 2 prefill worker × TP4; 2 decode worker × TP4/EP4.',
    '- `sweep`: warmup 15s /đo 30s /grace 30s, dùng để chọn concurrency.',
    '- `confirm`: warmup 60s /đo 120s /grace 30s. '
    '09 chọn N32 từ sweep; 07 được gửi đo thêm N32 ở job 22197 với warmup đủ 8 cặp P/D.',
    '- SLA: mỗi request cần TTFT ≤3000ms và ITL trung bình ≤20ms; '
    'ít nhất 90% request đạt cả hai, tính cả lỗi vào mẫu số.',
    '- Good tokens/s = giá trị `goodput` trong export ×200.', '',
    '| Job | Cấu hình | Lượt | N | Request đạt chuẩn | Good tokens/s | TTFT TB ms | ITL TB ms | Qua SLA | Request bị hủy |',
    '|---|---|---|---:|---:|---:|---:|---:|---|---:|',
]
status_file = root / 'job-status.json'
if status_file.exists():
    status = json.loads(status_file.read_text())
    lines[6:6] = ['## Trạng thái job', '',
        '| Job | Mục đích | Trạng thái | Thời gian chạy |',
        '|---|---|---|---|',
        *[f'| {job} | {purpose} | {status.get(job, {}).get("State", "chưa rõ")} | '
          f'{status.get(job, {}).get("Elapsed", "")} |'
          for job, purpose in [('22130','Lần đầu lỗi tokenizer'),
                               ('22131','09: sweep và đo dài'),
                               ('22135','07: sweep'),
                               ('22143','07: lỗi cổng metrics trước khi đo'),
                               ('22147','07: lỗi worker registration trước khi đo'),
                               ('22197','07: chờ worker registration, đo dài N32'),
                               ('22200','09: thử N40/N48, đo dài điểm tốt nhất')]], '']

def fmt(v):
    return f'{v:.2f}' if isinstance(v, (int, float)) else 'chưa có'

for r in rows:
    fraction = r['good_request_fraction']
    lines.append('| ' + ' | '.join([
        r['job'], r['topology'], r['phase'], str(r['concurrency']),
        f'{fraction:.1%}' if fraction is not None else 'chưa có',
        fmt(r['good_output_tokens_s']), fmt(r['ttft_avg_ms']),
        fmt(r['itl_avg_ms']), 'Có' if r['sla_pass'] else 'Không',
        str(r['cancelled_requests']) if r['cancelled_requests'] is not None else 'chưa có',
    ]) + ' |')

confirm = {}
for r in rows:
    if r['phase'] != 'confirm':
        continue
    old = confirm.get(r['topology'])
    rank = (bool(r['sla_pass']) and r['cancelled_requests'] == 0, r['good_output_tokens_s'] or 0)
    old_rank = ((bool(old['sla_pass']) and old['cancelled_requests'] == 0), old['good_output_tokens_s'] or 0) if old else None
    if old is None or rank > old_rank:
        confirm[r['topology']] = r
lines += ['', '## Nhận xét từ số đo', '']
if all(t in confirm for t in ('baseline07', 'candidate09')):
    b, c = confirm['baseline07'], confirm['candidate09']
    if b['sla_pass'] and c['sla_pass'] and b['good_output_tokens_s']:
        delta = (c['good_output_tokens_s'] / b['good_output_tokens_s'] - 1) * 100
        lines.append(
            f'Ở lượt đo dài tốt nhất đã hoàn thành, 07 đạt **{b["good_output_tokens_s"]:.2f}** '
            f'good tokens/s tại N={b["concurrency"]}; 09 đạt '
            f'**{c["good_output_tokens_s"]:.2f}** tại N={c["concurrency"]}. '
            f'Chênh lệch 09 so với 07: **{delta:+.2f}%**.'
        )
        if b['concurrency'] != c['concurrency']:
            lines.append('Đây là so sánh mức tốt nhất đã thử của mỗi cấu hình; '
                         'concurrency khác nhau nên không tách riêng tác động topology.')
    else:
        lines.append('Có lượt đo dài chưa qua ngưỡng SLA; '
                     'không thể dùng goodput của lượt đó làm điểm hiệu năng hợp lệ.')
else:
    lines.append('Chưa đủ kết quả đo dài của cả hai cấu hình để kết luận cấu hình nào tốt hơn.')
failed = [r for r in rows if r['sla_pass'] is False]
if failed:
    lines.append('Các dòng “Không” bị loại dù throughput có thể cao. '
                 'ITL/TTFT trung bình toàn bộ request dưới ngưỡng vẫn chưa đủ: '
                 'ngưỡng SLA được xét từng request rồi tính tỷ lệ đạt chuẩn.')
lines += [
    '', '## Log và giới hạn', '',
    '- [Log sweep đối chứng 22135](runs/22135.out), '
    '[log đo dài đối chứng 22197](runs/22197.out), [log ứng viên 22131](runs/22131.out).',
    '- [Số liệu JSON kèm đường dẫn raw export, request count, lỗi và p95](comparison.json).',
    '- Job 22130 lỗi tokenizer trước khi đo; loại khỏi so sánh. '
    'Đã sửa bằng official tokenizer ID và cache offline; không đổi weights.',
    '- Job 22143 lỗi gateway warmup trước benchmark: các gateway trùng cổng '
    'Prometheus 29000. Đã đặt cổng riêng cho từng gateway, kiểm tra bằng parser '
    'trong đúng image và gửi lại thành 22147. Lỗi này không phải số đo hiệu năng.',
    '- Job 22147 lỗi 503 trước benchmark: gateway healthy nhưng workers chưa đăng ký xong. '
    'Đã thêm retry có giới hạn cho lỗi no-workers, kiểm tra tình huống này trên CPU cho 8 cặp '
    'và gửi lại job 22197; job đó đã hoàn thành đo dài 07.',
    '- Chỉ đọc export chính ở `artifacts/profile_export_aiperf.json`; '
    'không cộng trùng bản sao ở `phases/profiling/` hoặc lấy warmup làm kết quả.',
    '- Chưa có chuỗi đối chứng lặp A/B qua nhiều deployment; '
    'startup/cache và bước khởi tạo đường truyền trước benchmark có thể khác nhau. '
    'Lượt confirm đều giữ warmup 60s và thời lượng đo 120s.',
    '- Lượt sweep N16 của 07 còn chịu khởi tạo các đường truyền KV: '
    'log có request chờ bootstrap và client kết thúc grace khi còn request đang chạy. '
    'Không dùng số thấp ở lượt này để khẳng định 09 tăng tốc nhiều lần; '
    'ưu tiên so các lượt confirm đã warmup.',
    '- Cột tỷ lệ đạt chuẩn giữ nguyên giá trị từ export BTC yêu cầu. '
    'Request bị client hủy khi hết grace được ghi riêng; '
    'lượt bị hủy không được dùng để kết luận hiệu năng ổn định.',
    '- Chưa chạy accuracy check theo yêu cầu BTC. '
    'Không suy rộng kết quả sang topology hoặc concurrency chưa đo.',
]
report = '\n'.join(lines) + '\n'
(root / 'RESULTS.md').write_text(report)
print(report)
