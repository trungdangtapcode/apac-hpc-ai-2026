"""Persist this bounded wake; scheduler and budget snapshots keep timestamps."""
import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT = Path(__file__).resolve().parent
WORK = Path('/home/apacsc42/workspace')
now = datetime.datetime.now(datetime.timezone.utc)
stamp = now.strftime('%H:%M:%S UTC')
evidence = str(OUT.relative_to(ROOT))
final = {'checked_utc': now.isoformat()}
for name, cmd in {
    'queue': ['squeue', '-h', '-u', 'apacsc42', '-o', '%i|%T|%S|%M|%R'],
    'accounting': ['sacct', '-X', '-n', '-P', '-j', '23906,23924,23934',
                   '--format=JobID,State,ExitCode,Start,End,Elapsed,NodeList'],
    'watcher': ['ps', '-p', (ROOT / 'serving-tuning/watcher.pid').read_text().strip(),
                '-o', 'pid,lstart,etime,args']}.items():
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    assert p.returncode == 0, (name, p.stderr)
    final[name] = {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
(OUT / 'final-queue.json').write_text(json.dumps(final, indent=2) + '\n')
assert '23906|RUNNING|' in final['queue']['stdout'], 'State changed: perform terminal review first'
assert all(f'{job}|PENDING|' in final['queue']['stdout'] for job in ('23924', '23934'))
assert 'watch-serving-tuning.py --run' in final['watcher']['stdout']
review = json.loads((OUT / 'runtime-review.json').read_text())
assert review['pair_warmup_complete_at_snapshot'] is True

block = f'''## Bàn giao 16/10/2026 {stamp}

Scheduler vừa kiểm tra: 23906 RUNNING từ 01:38:03 UTC trên g1/g4;
23924/23934 PENDING(Resources), 3/5 slot; watcher 3514431 sống.
Snapshot 01:43 trước đó là lịch sử. Chưa có final seal hoặc kết quả mới.

Audit 01:46:33 UTC xác nhận cả hai P/D paths đã warmup, 8 rank MNNVL/NIXL,
payload frozen/copied và script Slurm đã lưu đều khớp. Chunk8192 đồng thời
tăng graph prefill lên8192; decode graph giữ nguyên. Logprefix có hash,
chưa phải final seal. Trạng thái chưa warmup lúc01:41 đã được thay thế.

Đã chuẩn bị `{evidence}/review-chunk8192.py`: chỉ đọc job23906 sau terminal/seal,
kiểm protocol60/120/30, raw request/good/latency/length, short non-regression,
runtime và so CẢ23778/23839 cùng mean. Replay hai baseline từ sealed artifact
đạt2592,1624/2592,9236 goodtokens/s; đây là dữ liệu cũ, không phải repeat mới.
Terminal path của công cụ chưa được kiểm bằng23906 hoàn chỉnh.

NSCC01:45:30UTC: helper thiếuVPN trướcSSH;220575/result/credit chưa xác minh.
Giữ1536SU reserve, campaign16384SU, pilot04→05→06 và gate hiện có.
Không xác thực mới/qsub, thêm job/repeat/N56/controller/schedule.
Tiếp: watcher thu23906 và haiN54; chạy review khi có finalseal.
Bằng chứng: `{evidence}/`.
'''
paths = [WORK / 'notes/CURRENT.md', WORK / 'research-autopilot/POLICY.md',
         WORK / 'research-autopilot/LATEST.md', ROOT / 'serving-tuning-09/MATCHED_REVIEW.md']
for path in paths:
    (OUT / (path.name + '.before')).write_bytes(path.read_bytes())
current = paths[0].read_text()
current = re.sub(r'Cập nhật kiến thức: \*\*[^\n]+',
                 f'Cập nhật kiến thức: **16/10/2026, lượt research01:45–{now.strftime("%H:%M")}UTC**.',
                 current, count=1)
start = current.index('## Runtime chunk8192')
end = current.index('## Điều cần nhớ trước tiên', start)
current = current[:start] + block + '\n' + current[end:]
paths[0].write_text(current)
policy = re.sub(r'^# Autonomous Qwen research[^\n]*',
                f'# Autonomous Qwen research — current handoff2026-10-16 {stamp}',
                paths[1].read_text(), count=1)
policy = policy.replace('Latestqueue16Oct01:43:17UTC:', f'Latestqueue16Oct{now.strftime("%H:%M:%S")}UTC:')
policy = policy.replace('At16Oct01:40:59UTC helper again', 'At16Oct01:45:30UTC helper again')
policy += '\n\n' + block
paths[1].write_text(policy)
guide = paths[3].read_text() + '\n\n' + block + f'''
Read-only replay once watcher has sealed terminal23906:

```bash
python3 {OUT}/review-chunk8192.py
```

The command reports INCOMPLETE while running or unsealed. It does not poll,
submit jobs, change the watcher, or approve configuration promotion.
'''
paths[3].write_text(guide)

live = json.loads((OUT / 'live-check.json').read_text())
assert live['pbs']['rc'] == 1 and 'Expected one live VPN session' in live['pbs']['stderr']
note = ('No PBS/credit refresh at2026-10-16 01:45:30UTC: existing-access helper found no live VPN '
        'session before SSH.220575 current state/result unknown; retain1536SU reserve. Historical '
        'ledger unchanged. New authentication prohibited; no authentication/qsub.')
with (ROOT / 'nscc-pbs/budget.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    bp = ROOT / 'nscc-pbs/nscc-budget.json'
    budget = json.loads(bp.read_text())
    (OUT / 'budget-before-update.json').write_text(json.dumps(budget, indent=2) + '\n')
    budget.update(updated_utc=now.isoformat(), reconciliation_note=note)
    for job in budget['jobs']:
        if job['job_id'] == '220575.pbs111':
            job.update(scheduler_comment=note, latest_attempted_check_utc=live['checked_utc'], state_fresh=False)
    budget['latest_access_check'].update(checked_utc=live['checked_utc'], source=evidence + '/live-check.json')
    budget['evidence'].append(evidence + '/live-check.json')
    bp.write_text(json.dumps(budget, indent=2) + '\n')
    pp = ROOT / 'nscc-pbs/continuous-plan.json'
    plan = json.loads(pp.read_text())
    plan.update(updated_utc=now.isoformat(), latest_evidence=evidence + '/live-check.json', access_status=note)
    pp.write_text(json.dumps(plan, indent=2) + '\n')

report = f'''# Báo cáo Qwen — 16/10/2026 {stamp}

- **H200:** 23906 RUNNING;23924/23934 PENDING(Resources),3/5slot;watcher sống. Chưa có kết quả benchmark hoàn chỉnh mới.
- **Audit mới:** hai P/D paths đã warmup;8rank MNNVL/NIXL và checksum payload/script đạt. Thay thế snapshot01:41 chưa warmup. Chunk8192 cũng tăng graph prefill lên8192; không quy riêng hiệu ứng cho scheduling.
- Đã chuẩn bị công cụ chỉ đọc đối soát final23906 với cả hai baseline/mean; replay seal/rawmetrics hai baseline đạt. Đây là dữ liệu cũ; terminal path còn chờ23906 hoàn chỉnh. Watcher tiếp tục thu; không thêmjob/repeat/N56/lịch.
- **NSCC01:45:30UTC:** thiếuVPN trướcSSH;220575/kết quả/credit chưa xác minh. Giữ1536SUreserve,campaign16384SU và gate04→05→06; không xác thực mới/qsub.
- Đã cập nhật CURRENT/POLICY/review và budget/plan dưới lock; kết thúc sau phần việc độc lập, không chờ queue.

[Bằng chứng]({OUT}/runtime-review.json) · [Công cụ final]({OUT}/review-chunk8192.py).
'''
paths[2].write_text(report)
with (WORK / 'research-autopilot/HISTORY.md').open('a') as f:
    f.write('\n\n' + report)
(OUT / 'wake-summary.json').write_text(json.dumps(dict(finished_utc=now.isoformat(),
    benchmark_result_claimed=False, new_jobs_submitted=False, new_authentication_attempted=False,
    independent_work='Final-review preparation and historical baseline replay; warmup now verified',
    nscc_reserve_su=1536), indent=2) + '\n')
manifest = [{'path': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
            for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'evidence-sha256.json']
(OUT / 'evidence-sha256.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(final, indent=2))
