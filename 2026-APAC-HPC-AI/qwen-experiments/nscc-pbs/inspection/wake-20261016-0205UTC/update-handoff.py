"""Record CPU preparation and fresh scheduler/access evidence; no job mutation."""
import datetime
import fcntl
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
WORK = Path('/home/apacsc42/workspace')
EVID = str(OUT.relative_to(ROOT))
now = datetime.datetime.now(datetime.timezone.utc)
stamp = now.strftime('%H:%M:%S UTC')
live = json.loads((OUT/'live-check.json').read_text())
final = json.loads((OUT/'final-queue.json').read_text())
validation = json.loads((OUT/'token-review-validation.json').read_text())
assert validation['all_pass'] and validation['test_count'] == 30
assert live['pbs']['rc'] == 1 and 'Expected one live VPN session' in live['pbs']['stderr']
assert len(final['queue']['stdout'].strip().splitlines()) == 2
assert all(f'{j}|PENDING|' in final['queue']['stdout'] for j in ('23924', '23934'))
assert 'watch-serving-tuning.py --run' in final['watcher']['stdout']
queue_time = datetime.datetime.fromisoformat(final['checked_utc']).strftime('%H:%M:%S UTC')
access_time = datetime.datetime.fromisoformat(live['checked_utc']).strftime('%H:%M:%S UTC')


def backup(path):
    (OUT/(path.name+'.before')).write_bytes(path.read_bytes())


block = f'''## Bàn giao 16/10/2026 {stamp}

Scheduler kiểm lúc {queue_time}: **23924/23934 PENDING(Priority)**, 2/5 slot;
watcher3514431 sống. Chưa có runtime/export N54 hay số đo GPU mới. Snapshot
01:52 PENDING(Resources) là lịch sử. Cả ba wave9 đã finalaudit; chunk8192
23906 đạt2547,85goodtokens/s, thấp hơn mean MNNVL1,7238%; kết quả đã ghi giữ nguyên.

Đã chuẩn bị local `nscc-pbs/research-next/eagle3-01/review-token-pairs.py` và
`TOKEN_REVIEW.md`: đối chiếu native `/generate` output_ids/prompt IDs và finish
reason, không tái tokenize text hay bỏ EOS/tail. **30 ca tổng hợp CPU + 6 kiểm
source đạt**, không phải ca model/GPU. Source image thực trả output_ids cả ở
nhánh text, không cần bật logprob/skip-tokenizer chỉ để lấy IDs. 5 file hash;
chưa thử HTTP/model/EAGLE3 thật, không chứng minh lossless/accuracy BTC.
Thiết kế case đầu gồm greedy trung tính, cùng input IDs, cap1/3/4/5/200,
short/long và EOS thực; audit env simulation=-1 cùng resolved args riêng.

NSCC kiểm lúc {access_time}: helper thiếu VPN trước SSH;220575/result/credit
vẫn chưa xác minh. Giữ1536SU dự trù, campaign16384SU, ưu tiên04→05→06 và các
gate hiện có. Không xác thực mới/qsub hay tải draft/upload/payload GPU mới.
Tiếp: watcher thu hai N54, chạy review-n54.py với cả hai baseline/mean; không
thêm job/repeat/N56/controller/schedule. Phần chuẩn bị độc lập đã xong, kết thúc
không chờ queue. Bằng chứng: `{EVID}/`.
'''
current_path = WORK/'notes/CURRENT.md'
backup(current_path)
current = current_path.read_text()
current = re.sub(r'Cập nhật kiến thức: \*\*[^\n]+',
                 f'Cập nhật kiến thức: **16/10/2026, lượt research02:05–{now:%H:%M}UTC**.', current, count=1)
start = current.index('## Bàn giao ')
end = current.index('## Điều cần nhớ trước tiên', start)
current = current[:start]+block+'\n'+current[end:]
current_path.write_text(current)

policy_path = WORK/'research-autopilot/POLICY.md'
backup(policy_path)
policy = policy_path.read_text()
policy = re.sub(r'^# Autonomous Qwen research[^\n]*',
                f'# Autonomous Qwen research — current handoff2026-10-16 {stamp}', policy, count=1)
policy = re.sub(r'Latestqueue16Oct\d\d:\d\d:\d\dUTC:23924/23934PENDING\(Resources\)',
                f'Latestqueue16Oct{queue_time.replace(" UTC", "")}UTC:23924/23934PENDING(Priority)', policy, count=1)
policy = policy.replace('At16Oct01:50:59UTC helper again',
                        f'At16Oct{access_time.replace(" UTC", "")}UTC helper again', 1)
policy_path.write_text(policy+'\n\n'+block)

qa_path = WORK/'tutorial/14-so-tay-hoi-dap.md'
backup(qa_path)
with qa_path.open('a') as f:
    f.write(f'''\n\n**16/10/2026, {now:%H:%M} UTC — Có cần tái tokenize text để so token EAGLE3 không?**

Không dùng text tái tokenize làm bằng chứng token phát sinh. Source image hiện
có native `/generate` nonstreaming trả `output_ids` cả khi tokenizer hoạt động;
đặt `return_prompt_token_ids=true` để giữ input IDs. Nhánh detokenizer chuyển
raw IDs từ scheduler; không cần bật logprob hay skip-tokenizer chỉ để lấy IDs
ở image này. Chưa kiểm bằng HTTP/model thật; không suy sang mọi phiên bản.

Tool local mới so exact request/input IDs, counts, raw output IDs và finish
reason; giữ EOS/tail và phân biệt capture hỏng với khác biệt thật. 30 ca CPU
tổng hợp và6kiểm source đạt, không phải30ca Qwen/accuracy. Chuẩn bị greedy,
neutral penalties, cùng target/tokenizer, kiểm cả biên cap1/3/4/5/200, EOS và
short/long. Audit runtime/env riêng; token khớp trên suite nhỏ chưa chứng minh
lossless toàn miền, sampling tương đương hoặc accuracy BTC. Chưa tải draft,
chạy GPU hay thay thứ tự04→05→06.
[Hướng dẫn]({ROOT}/nscc-pbs/research-next/eagle3-01/TOKEN_REVIEW.md) ·
[Bằng chứng CPU/source]({OUT}/token-review-validation.json).
''')

design_path = ROOT/'nscc-pbs/research-next/eagle3-01/design.json'
backup(design_path)
design = json.loads(design_path.read_text())
design['updated_utc'] = now.isoformat()
design['offline_token_review'] = {'script': 'review-token-pairs.py', 'guide': 'TOKEN_REVIEW.md',
    'state': 'LOCAL_CPU_VALIDATED_30_SYNTHETIC_CASES_NO_REAL_CAPTURE',
    'evidence': EVID+'/token-review-validation.json', 'gpu_executed': False,
    'capture_contract': 'Native /generate, explicit identical input_ids and neutral greedy settings; prompt/output IDs and finish reason retained. Audit runtime/env separately.'}
design_path.write_text(json.dumps(design, indent=2)+'\n')
readme_path = ROOT/'nscc-pbs/research-next/README.md'
backup(readme_path)
with readme_path.open('a') as f:
    f.write('\n\n## CPU token review16Oct02:05UTC\n\n'
        '[Native-token review preparation](eagle3-01/TOKEN_REVIEW.md) adds an offline\n'
        'comparator with30syntheticCPUchecks and6actual-image source checks. No real\n'
        'capture, model/GPU validation or submission. Source normal text output includes\n'
        'output_ids; preserve IDs/EOS/finish reasons rather than retokenize rendered text.\n'
        'Draft compatibility, CUDA verifier and organiser accuracy remain unverified.\n')

accessnote = (f'No PBS/credit refresh at2026-10-16 {access_time}: existing-access helper found no '
    'live VPN session before SSH.220575 current state/result unknown; retain1536SU reserve. '
    'Historical ledger unchanged. New authentication prohibited; no authentication/qsub.')
with (ROOT/'nscc-pbs/budget.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    for name in ('nscc-budget.json', 'continuous-plan.json'):
        path = ROOT/'nscc-pbs'/name
        backup(path)
        data = json.loads(path.read_text())
        data['updated_utc'] = now.isoformat()
        if name == 'nscc-budget.json':
            data['reconciliation_note'] = accessnote
            data['latest_access_check'].update(checked_utc=live['checked_utc'], source=EVID+'/live-check.json')
            data['evidence'].append(EVID+'/live-check.json')
            for job in data['jobs']:
                if job['job_id'] == '220575.pbs111':
                    job.update(scheduler_comment=accessnote, latest_attempted_check_utc=live['checked_utc'], state_fresh=False)
        else:
            data.update(latest_evidence=EVID+'/live-check.json', access_status=accessnote)
            for branch in data['research_branches']:
                if branch['id'] == 'eagle3-01':
                    branch['offline_token_review'] = design['offline_token_review']
        temp = path.with_suffix('.json.tmp')
        temp.write_text(json.dumps(data, indent=2)+'\n')
        temp.replace(path)

report = f'''# Báo cáo Qwen — 16/10/2026 {stamp}

- **H200 {queue_time}:**23924/23934 PENDING(Priority),2/5slot;watcher sống. Chưa có số đo GPU mới;wave9 đã finalaudit từ lượt trước.
- **Tiến triển CPU:** chuẩn bị công cụ đối chiếu token EAGLE3 và hướng dẫn capture native. 30ca tổng hợp +6kiểm source đạt;giữ input/output IDs,EOS/tail,finish reason. Source image trả output_ids cả nhánh text. Chưa thử HTTP/model/GPU hay xác nhận lossless/accuracy BTC.
- **NSCC {access_time}:**thiếu VPN trướcSSH;220575/kết quả/credit chưa xác minh. Giữ1536SU dự trù,campaign16384SU vàgate04→05→06;không xác thực mới/qsub.
- Đã cập nhật CURRENT,POLICY,Q&A,design,budget/plan dưới lock và giữ bằng chứng. Tiếp:watcher thu haiN54 rồi chạy review-n54.py so cả hai baseline/mean. Không thêmjob/repeat/N56/controller/lịch;phần chuẩn bị độc lập đã xong,kết thúc không chờ queue.

[Hướng dẫn]({ROOT}/nscc-pbs/research-next/eagle3-01/TOKEN_REVIEW.md) · [CPU/source]({OUT}/token-review-validation.json) · [Scheduler]({OUT}/final-queue.json).
'''
latest_path = WORK/'research-autopilot/LATEST.md'
backup(latest_path)
latest_path.write_text(report)
with (WORK/'research-autopilot/HISTORY.md').open('a') as f:
    f.write('\n\n'+report)
summary = {'finished_utc': now.isoformat(), 'state': 'CPU_PREPARATION_COMPLETE_GPU_JOBS_PENDING',
           'new_jobs_submitted': False, 'new_authentication_attempted': False,
           'nscc_reserve_su': 1536, 'independent_work_complete': True,
           'cpu_tests': 30, 'static_source_checks': 6}
(OUT/'wake-summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
