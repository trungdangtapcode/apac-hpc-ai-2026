"""Persist CPU capture preparation and live scheduler checks; no GPU job mutation."""
import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
WORK=Path('/home/apacsc42/workspace')
BRANCH=ROOT/'nscc-pbs/research-next/eagle3-01'
EVID=str(OUT.relative_to(ROOT))
now=datetime.datetime.now(datetime.timezone.utc)
stamp=now.strftime('%H:%M:%S UTC')
live=json.loads((OUT/'live-check.json').read_text())
final=json.loads((OUT/'final-queue.json').read_text())
tests=json.loads((OUT/'attempt02/capture-validation.json').read_text())
assert tests['all_pass'] and tests['test_count']==35
assert tests['source_sha256']==hashlib.sha256((BRANCH/'capture-native-tokens.py').read_bytes()).hexdigest()
assert all(f'{j}|PENDING|' in final['queue']['stdout'] for j in ('23924','23934'))
assert 'watch-serving-tuning.py --run' in final['watcher']['stdout']
assert live['pbs']['rc']==1 and 'Expected one live VPN session' in live['pbs']['stderr']
qt=datetime.datetime.fromisoformat(final['checked_utc']).strftime('%H:%M:%S UTC')
at=datetime.datetime.fromisoformat(live['checked_utc']).strftime('%H:%M:%S UTC')

def backup(p):
 (OUT/(p.name+'.before')).write_bytes(p.read_bytes())

def write_json(p,obj):
 tmp=p.with_suffix('.json.tmp');tmp.write_text(json.dumps(obj,indent=2)+'\n');tmp.replace(p)

p=BRANCH/'TOKEN_REVIEW.md';backup(p)
with p.open('a') as f:
 f.write(f'''

## Bộ thu HTTP cục bộ — 16/10/2026 {stamp}

`capture-native-tokens.py` đã kiểm **35 ca HTTP giả lập/CPU**, không có Qwen,
model/GPU hay HTTP SGLang thực. Report final ở `{EVID}/attempt02/capture-validation.json`.
Attempt đầu34ca được giữ lịch sử; bản final thêm kiểm Content-Length bị thiếu dù
body có thể parse JSON hợp lệ. Không thay comparator hay payload GPU đang chờ.

Đầu vào là suiteJSON có schema1,target_revision,tokenizer_sha256 và cases giống
contract ở trên, nhưng mỗi case chỉ có case_id/request, KHÔNG có response. Dùng
input IDs đã chuẩn bị bằng tokenizer/chat template đúng target; SHA256 trong suite
phải khớp file tokenizer.json truyền vào. Tool chỉ kiểm hash file local, không
chứng thực provenance target/revision hay tạo chat template. Không lấy tokenizer
của checkpoint khác để thay cho bước xác minh.

Khi đã có deployment và forward được cho phép, thu lần lượt control, control-repeat
và candidate với cùng suite, cùng thứ tự. Ví dụ dùng endpoint loopback đã thiết lập:

```bash
python3 nscc-pbs/research-next/eagle3-01/capture-native-tokens.py \\
  --suite verified-token-suite.json --tokenizer /verified/target/tokenizer.json \\
  --endpoint http://127.0.0.1:30000/generate --outdir new-control-capture
```

Sau đó dùng `new-control-capture/capture.json` cho comparator; so control tự lặp
trước khi diễn giải khác biệt candidate. Tool không khởi động server, mở tunnel,
xác thực hay gửi job. Chỉ hỗ trợ numeric loopback HTTP, không auth/query/redirect,
không proxy, không retry. Endpoint phải trỏ đúng deployment được audit riêng.

Mọi request greedy/trung tính được kiểm trước khi kết nối; giới hạn64case,
cap1..200,min0 và input+cap<=8192. Từng request tuần tự, lưu exactJSON bytes,
response bytes nguyên bản, hash/status HTTP và journal đã flush/fsync. Lỗi thì
ngừng, giữ request và phần response đã nhận; không ghi capture hoàn chỉnh khi
count/IDs/finish/HTTP lỗi. Không sửa EOS/tail hay chuẩn hóa output thành PASS.
Mỗi outdir phải mới; không ghi đè bằng chứng cũ. Thời gian monotonic chỉ diagnostic,
không phải throughput/TTFT/ITL benchmark. Header xác thực/session không được thu.

Còn phải chuẩn bị suite thực, xác minh tokenizer/template, audit image/weights/
resolved args và simulation=-1, chạy nativeHTTP/model thật rồi đánh giá compatibility,
EOS, output và acceptance. Chưa tải draft/upload hay đổi04→05→06/queue/credit/budget.
''')

prep={'script':'capture-native-tokens.py','state':'LOCAL_LOOPBACK_MOCK_VALIDATED_35_CASES_NO_MODEL_GPU',
      'evidence':EVID+'/attempt02/capture-validation.json','gpu_executed':False,
      'uploaded':False,'limits':'No real suite/model/SGLang HTTP capture; runtime and provenance audit remain separate.'}
p=BRANCH/'design.json';backup(p);design=json.loads(p.read_text());design.update(updated_utc=now.isoformat(),native_capture_preparation=prep);write_json(p,design)

block=f'''## Bàn giao 16/10/2026 {stamp}

Scheduler kiểm lúc {qt}: **23924/23934 PENDING(Resources)**, 2/5 slot;
watcher3514431 sống. Snapshot02:09PENDING(Priority) là lịch sử. Chưa có runtime/
export N54 hay số đo GPU mới; cả ba wave9 đã finalaudit, kết quả giữ nguyên.

Đã chuẩn bị local `nscc-pbs/research-next/eagle3-01/capture-native-tokens.py`:
thu tuần tự native /generate vào thư mục mới, kiểm suite/hash tokenizer trước
khi gửi, giữ request/response bytes và hash/journal, dừng khi lỗi, không retry.
**35 ca HTTP giả lập/CPU đạt**, gồm EOS, token khác, count/IDs/finish sai,
redirect, body thiếu và bảo toàn evidence; không phải thử SGLang/Qwen/GPU.
Chưa có suite/capture model thực; tool không chứng thực target/runtime/accuracy.
Giữ attempt34ca lịch sử; final thêm chặn Content-Length thiếu dù JSON hợp lệ.
Hướng dẫn ở TOKEN_REVIEW.md; chưa tải draft/upload/đổi frozen payload.

NSCC kiểm lúc {at}: helper thiếu VPN trước SSH;220575/result/credit vẫn
chưa xác minh. Giữ1536SU dự trù,campaign16384SU,ưu tiên04→05→06 và các gate.
Không xác thực mới/qsub,thêm job/repeat/N56/controller/schedule. Tiếp:watcher
thu haiN54 rồi chạy review-n54.py so cả hai baseline/mean. Phần chuẩn bị độc lập
đã xong,kết thúc không chờ queue. Bằng chứng:`{EVID}/`.
'''
p=WORK/'notes/CURRENT.md';backup(p);s=p.read_text()
s=re.sub(r'Cập nhật kiến thức: \*\*[^\n]+',f'Cập nhật kiến thức: **16/10/2026, lượt research02:15–{now:%H:%M}UTC**.',s,count=1)
a=s.index('## Bàn giao ');b=s.index('## Điều cần nhớ trước tiên',a);s=s[:a]+block+'\n'+s[b:]
s=s.replace('23906cònchờ: khi chạyphảikiểmtrachunk8192 vàgraphthực,khôngtựsuyruntime.',
 'Tại snapshot lịch sử00:19,23906cònchờ; đã finalaudit01:52 (xemPOLICY).\nRuntime chunk8192/prefillgraph8192 đã xác minh,không quy kết riêng scheduling.')
p.write_text(s)

p=WORK/'research-autopilot/POLICY.md';backup(p);s=p.read_text()
s=re.sub(r'^# Autonomous Qwen research[^\n]*',f'# Autonomous Qwen research — current handoff2026-10-16 {stamp}',s,count=1)
s=re.sub(r'Latestqueue16Oct\d\d:\d\d:\d\dUTC:23924/23934PENDING\([^)]*\)',f'Latestqueue16Oct{qt.replace(" UTC", "")}UTC:23924/23934PENDING(Resources)',s,count=1)
s=re.sub(r'At16Oct\d\d:\d\d:\d\dUTC helper again',f'At16Oct{at.replace(" UTC", "")}UTC helper again',s,count=1)
p.write_text(s+'\n\n'+block)

p=WORK/'tutorial/14-so-tay-hoi-dap.md';backup(p)
with p.open('a') as f:
 f.write(f'''

**16/10/2026 {stamp} — HTTP200 hoặc JSON parse được có đủ làm capture token hợp lệ?**

Chưa đủ. Phải giữ exact request/response bytes, kiểm prompt IDs/count và output
IDs/count/cap/finish reason. Body có thể là JSON hợp lệ nhưng HTTP Content-Length
vẫn thiếu; bộ thu mới chặn trường hợp này, giữ raw body, không nhận là capture đủ.
Kết nối đứt giữa chừng thì giữ phần bytes đã đọc, không retry tự động hoặc cắt
EOS/tail để ép khớp. Chỉ tạo capture.json sau khi tất cả case hợp lệ; lỗi giữ
failure.json/journal và raw files trong outdir riêng.

Tool mới đã qua35ca HTTP giả lập trên loopbackCPU, không phải model/Qwen hay
HTTP SGLang thật. Suite/hash tokenizer cần chuẩn bị/xác minh đúng target; tool
không xác nhận deployment, image, weights, simulation hay accuracy. So control tự
lặp trước rồi mới so candidate; thời gian thu là diagnostic, không phải benchmark.
[Hướng dẫn]({BRANCH}/TOKEN_REVIEW.md) · [Bằng chứng]({OUT}/attempt02/capture-validation.json).
''')

accessnote=(f'No PBS/credit refresh at2026-10-16 {at}: existing-access helper found no live VPN session '
 'before SSH.220575 current state/result unknown; retain1536SU reserve. Historical ledger unchanged. '
 'New authentication prohibited; no authentication/qsub.')
with (ROOT/'nscc-pbs/budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for name in ('nscc-budget.json','continuous-plan.json'):
  p=ROOT/'nscc-pbs'/name;backup(p);data=json.loads(p.read_text());data['updated_utc']=now.isoformat()
  if name=='nscc-budget.json':
   data['reconciliation_note']=accessnote
   data['latest_access_check'].update(checked_utc=live['checked_utc'],source=EVID+'/live-check.json')
   data['evidence'].append(EVID+'/live-check.json')
   for job in data['jobs']:
    if job['job_id']=='220575.pbs111':job.update(scheduler_comment=accessnote,latest_attempted_check_utc=live['checked_utc'],state_fresh=False)
  else:
   data.update(latest_evidence=EVID+'/live-check.json',access_status=accessnote)
   for branch in data['research_branches']:
    if branch['id']=='eagle3-01':branch['native_capture_preparation']=prep
  write_json(p,data)

report=f'''# Báo cáo Qwen — 16/10/2026 {stamp}

- **H200 {qt}:**23924/23934 PENDING(Resources),2/5slot;watcher sống. Chưa có số đo GPU mới.
- **Tiến triển CPU:**chuẩn bị bộ thu token nativeHTTP tuần tự,giữ raw request/response/hash và evidence lỗi.35ca HTTP giả lập đạt;chưa thử SGLang/Qwen/GPU,chưa có suite thực hay chứng minh accuracy.
- **NSCC {at}:**thiếu VPN trướcSSH;220575/result/credit chưa xác minh. Giữ1536SU dự trù,campaign16384SU vàgate04→05→06;không xác thực mới/qsub.
- Đã cập nhật CURRENT,POLICY,Q&A,design,budget/plan và giữ raw evidence. Tiếp:watcher thu haiN54,chạy review-n54.py so cả hai baseline/mean. Không thêmjob/repeat/N56/controller/lịch;kết thúc vì chuẩn bị độc lập đã xong.

[Hướng dẫn]({BRANCH}/TOKEN_REVIEW.md) · [CPU/mockHTTP]({OUT}/attempt02/capture-validation.json) · [Scheduler]({OUT}/final-queue.json).
'''
p=WORK/'research-autopilot/LATEST.md';backup(p);p.write_text(report)
with (WORK/'research-autopilot/HISTORY.md').open('a') as f:f.write('\n\n'+report)
summary={'finished_utc':now.isoformat(),'new_gpu_jobs':False,'new_authentication':False,
 'nscc_reserve_su':1536,'cpu_mock_tests':35,'real_model_http_executed':False,
 'state':'PREPARATION_COMPLETE_EXISTING_JOBS_PENDING','evidence':EVID}
(OUT/'wake-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
