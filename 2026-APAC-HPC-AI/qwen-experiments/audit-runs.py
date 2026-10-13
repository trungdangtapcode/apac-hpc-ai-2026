"""Inventory finished raw artifacts once; include failures in a readable run ledger."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent
notes = json.loads((root / 'run-notes.json').read_text())
status = json.loads((root / 'job-status.json').read_text())
terminal = {'COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT', 'NODE_FAIL',
            'OUT_OF_MEMORY', 'PREEMPTED', 'BOOT_FAIL', 'DEADLINE', 'REVOKED'}
metrics = json.loads((root / 'comparison.json').read_text())
def fmt(value, percent=False):
    if value is None: return 'chưa có'
    return f'{value:.2%}' if percent else f'{value:.2f}'
lines = ['# Sổ các lần chạy Qwen', '',
         'Cập nhật UTC: ' + datetime.now(timezone.utc).isoformat(), '',
         'Mỗi job là dữ kiện: lỗi deploy dùng sửa quy trình; số đo qua/trượt SLA '
         'dùng chọn cấu hình. Không lấy job lỗi trước benchmark làm số liệu tốc độ.', '',
         '| Job | Topology | Trạng thái | Lượt đo đã có | Có manifest checksum |',
         '|---|---|---|---:|---|']

for job, note in notes.items():
    run = root / 'runs' / job
    state = status.get(job, {}).get('State', 'unknown')
    manifest_path = run / 'artifact-manifest.json'
    if run.is_dir() and state.split()[0].rstrip('+') in terminal and not manifest_path.exists():
        paths = [p for p in run.rglob('*') if p.is_file()
                 and p.name not in {'summary.json', 'artifact-manifest.json'}]
        paths.extend(p for p in [root / 'runs' / f'{job}.out',
                                 root / 'runs' / f'{job}.err'] if p.exists())
        files = []
        for path in sorted(paths):
            digest = hashlib.sha256()
            with path.open('rb') as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b''):
                    digest.update(chunk)
            files.append({'path': str(path.relative_to(root)),
                          'bytes': path.stat().st_size, 'sha256': digest.hexdigest()})
        manifest = {'job': job, 'sealed_utc': datetime.now(timezone.utc).isoformat(),
                    'status_at_seal': status[job],
                    'scope': 'Existing finished files inventoried now; not a checksum recorded at submission time. Derived summary.json is excluded.',
                    'files': files}
        temp = manifest_path.with_suffix('.json.tmp')
        temp.write_text(json.dumps(manifest, indent=2))
        temp.replace(manifest_path)
    count = sum(m['job'] == job for m in metrics)
    seal = f'[manifest](runs/{job}/artifact-manifest.json)' if manifest_path.exists() else 'Chưa: job chưa kết thúc'
    lines.append(f'| [{job}](runs/{job}/) | {note["topology"]} | {state} | {count} | {seal} |')

for job, note in notes.items():
    lines += ['', f'## Job {job}', '', f'**Mục đích:** {note["purpose"]}', '',
              f'**Quan sát:** {note["finding"]}', '', f'**Bài học:** {note["lesson"]}', '',
              f'[stdout](runs/{job}.out) · [stderr](runs/{job}.err) · [thư mục artifacts](runs/{job}/)']
    if note.get('provenance_note'):
        lines += ['', '**Ghi chú lịch sử file:** ' + note['provenance_note']]
    for m in metrics:
        if m['job'] != job:
            continue
        raw = Path(m['export']).relative_to(root)
        lines += ['', f'- {m["phase"]}/N{m["concurrency"]}: '
                  f'{fmt(m["good_request_fraction"],True)} đạt SLA, '
                  f'{fmt(m["good_output_tokens_s"])} good tokens/s, '
                  f'cancelled={m["cancelled_requests"]}; [raw export]({raw}).']

lines += ['', '## Đã lưu và giới hạn', '',
          '- Raw logs, scripts/snapshot đang có, worker.sh và config.txt ở `runs/<job>/`; '
          'stdout/stderr ở `runs/<job>.out` và `.err`. Job đang chờ có thể chưa có log.',
          '- Lượt đo hoàn thành có `inputs.json`, `profile_export.jsonl`, '
          '`profile_export_aiperf.json`, CSV, phase manifest và client logs. '
          'Dataset và metrics từng request được giữ; không chỉ giữ điểm tốt nhất.',
          '- `profile_export.jsonl` hiện chứa metadata/timing/metrics; '
          'không tuyên bố đã lưu toàn bộ văn bản output của mọi request.',
          '- Job chưa đi tới client có thể không có dataset/export/client versions; '
          'job lỗi trước benchmark không có score hợp lệ.',
          '- Images và model weights dùng từ /scratch, chưa được copy thành archive riêng; '
          'manifest không đảm bảo external image/checkpoint sẽ không thay đổi.',
          '- Checksum được tạo sau khi job kết thúc, dùng kiểm tra file có đổi sau mốc này; '
          'không chứng minh trạng thái nguyên gốc ở lúc submit. '
          'Giữ snapshot lỗi cũ, không sửa chúng để giả thành script đã thành công.',
          '- `comparison.json`, `RESULTS.md`, `summary.json` là báo cáo có thể tái tạo từ raw; '
          'watcher cập nhật khi có thêm dữ liệu. Manifest không hash các báo cáo dẫn xuất.',
          ('- Profiler GPU traces hiện có trong diagnostic-profile/ của các job: '
           + ', '.join(job for job in notes if any((root/'runs'/job/'diagnostic-profile').glob('*/*trace.json*')))
           + '; profiling riêng, không dùng làm điểm benchmark. Accuracy của BTC chưa được xác nhận.')
          if any(any((root/'runs'/job/'diagnostic-profile').glob('*/*trace.json*')) for job in notes)
          else '- Chưa có GPU profiler traces hoặc kết quả accuracy của BTC; các bước này chưa hoàn thành.',
          '', 'Đọc [bảng số đo](RESULTS.md) và [tổng hợp máy đọc được](comparison.json).']
(root / 'RUNS.md').write_text('\n'.join(lines) + '\n')
