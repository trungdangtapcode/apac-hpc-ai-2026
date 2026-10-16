from pathlib import Path
import json,datetime,fcntl,hashlib
base=Path('/home/apacsc42')
research=base/'2026-APAC-HPC-AI/qwen-experiments'
notes=base/'workspace/notes'
auto=base/'workspace/research-autopilot'
out=research/'nscc-pbs/inspection/wake-20261016-0540UTC'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,content):
 if path.exists(): (out/(path.name+'.before')).write_bytes(path.read_bytes())
 path.write_text(content)
 (out/(path.name+'.after')).write_bytes(path.read_bytes())
current='''## Bàn giao hiện hành 16/10/2026 05:42 UTC

Scheduler kiểm **05:40:37 UTC**: **23934/23973/23974/23975/24009 đều
PENDING(Priority), 5/5 slot**; sacct chưa có Start/End/allocation. Watcher419440
sống. Chưa có số đo GPU mới; snapshot05:36 Resources là lịch sử. Không thêmjob,
sửa queued payload hay watcher. Reviewers/suite CPU đã chuẩn bị; không cần chạy
lại audit hoặc mocktest bất biến khi chưa có seal.

**NSCC đã đổi tầng lỗi:** ssh-batch lúc05:40:37 đi qua namespace hiện có và
nhận `Permission denied (password)` từ SSH, khác lỗi thiếu VPN lúc05:30.
Kiểm chỉ đọc05:40:56 xác nhận interface snx-tun UP và route tới10.103.71.15
qua tunnel. Đây là bằng chứng mạng VPN hiện có, chưa phải SSH/PBS/credit thành
công, không xác minh ai tạo phiên/thời điểm bắt đầu/lifetime24h. Không đọc
credential/session blob, không connect/login VPN mới, không cấp password/DUO,
không lặp SSH hoặc qsub. Không kết luận password sai từ BatchMode không có
master xác thực dùng được. Các câu thiếuVPN dưới đây là snapshot lịch sử.
220575/result/credit vẫn chưa xác minh; giữ **1536SU** reserve và cap16384SU.

Đã chuẩn bị [phiếu bước tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0540UTC/NEXT_STEP.md):
thu seal qua watcher rồi review23934/wave10/24009; khi SSH xác thực sẵn dùng
được thì thu220575 và reconcile ownqueue/credit trước04→05→06. Giữ mọiattempt,
gatecomboN54 vàkhôngN56/thirdrepeat/promotion. Bộ14ca EAGLE3 vẫn chỉinputCPU,
chưamodel/GPU/accuracy. Đã đồng bộ metadata continuous-plan với suite hiện có.
Không còn việc độc lập cần làm trong lượt; kết thúc không chờqueue.
Bằng chứng: `nscc-pbs/inspection/wake-20261016-0540UTC/`.

'''
p=notes/'CURRENT.md'; text=p.read_text().replace('Cập nhật kiến thức: **16/10/2026 05:38 UTC**.','Cập nhật kiến thức: **16/10/2026 05:42 UTC**.')
text=text.replace('## Bàn giao hiện hành 16/10/2026 05:38 UTC','## Bàn giao lịch sử 16/10/2026 05:38 UTC',1)
pos=text.index('## Bàn giao lịch sử 16/10/2026 05:38 UTC');text=text[:pos]+current+text[pos:]
text=text.replace('## VPN: câu trả lời hiện tại, thay cho các suy đoán cũ','## VPN: diễn biến đã xác minh; trạng thái mới nhất xem bàn giao 05:42')
text=text.replace('chưa có phiên mới thành công với\n   cấu hình này, chưa chứng minh giữ được24giờ','tại mốc00:18 chưa có phiên mới thành công với\n   cấu hình này. Mốc05:40 đã quan sát tunnel hiện có nhưng chưa xác minh nguồn\n   khởi tạo/cấu hình/lifetime; chưa chứng minh giữ được24giờ')
save(p,text)
policy='''## Latest checked state —16Oct2026 05:42UTC

At05:40:37UTC all23934/23973/23974/23975/24009 are PENDING(Priority),5/5slots;
sacct has no start/allocation and watcher419440 is alive. No new GPU result.
Snapshots below are historical. No job/queued payload/watcher changes this wake.

NSCC existing-access ssh-batch now reaches the SSH server but returns
Permission denied(password), exit255. A read-only namespace check at05:40:56
confirms snx-tun UP and route via that tunnel. Earlier missing-VPN observations
are historical; current blocker is unavailable authenticated SSH access, not a
proven bad password. No inference about who started this tunnel, its age or
24h lifetime. No credentials/session contents read, no VPN connect/login/DUO,
no password supplied or repeated SSH/qsub.220575/result/credit stay unknown;
keep1536SU reserve,16384SU campaign cap,13000SU project reserve and04→05→06.

NEXT_STEP.md in nscc-pbs/inspection/wake-20261016-0540UTC gives the prepared
seal-review sequence and conditional NSCC recovery actions. CPU token suite and
reviewers are ready; do not repeat immutable audits/mocktests while pending.
continuous-plan metadata now reflects the prepared14case suite, not model output.
Independent work is complete; finish without waiting. Existing bounded repeats,
comboN54 gates and noN56/noextra successful repeat/no promotion remain current.

'''
p=auto/'POLICY.md';text=p.read_text().replace('# Current Qwen research handoff —16Oct2026 05:38UTC','# Current Qwen research handoff —16Oct2026 05:42UTC',1)
text=text.replace('## Latest checked state and CPU preparation —16Oct2026 05:38UTC','## Historical checked state and CPU preparation —16Oct2026 05:38UTC',1)
pos=text.index('## Historical checked state');text=text[:pos]+policy+text[pos:]
text=text.replace('no successful new tunnel; loginfailed at16Oct00:18status0,reasonunknown.','at00:18 no successful new tunnel; loginfailed status0,reasonunknown.\nAt05:40 an existing tunnel was observed, but authenticated SSH remains unavailable;\nits origin and24h lifetime are unverified. See current handoff above.')
save(p,text)
report='''# Báo cáo Qwen —16/10/2026 05:42 UTC

- **05:40:37 UTC:**23934/23973/23974/23975/24009 đều **PENDING(Priority),5/5slot**;watcher419440 sống. Chưa có số đo GPU mới; không thêmjob/sửa payload.
- **NSCC đổi tầng lỗi:** đã có snx-tun UP/route qua tunnel lúc05:40:56;ssh-batch tới SSH nhưng bị `Permission denied (password)`. Chưa truy cập PBS/credit, không kết luận password sai hay phiên24h đã đạt.
- Không loginVPN/DUO mới, không cấpcredential/thử lặpSSH/qsub.220575/result/credit vẫn chưa xác minh; giữ **1536SU** reserve,campaign **16384SU**,04→05→06.
- Đã chuẩn bị phiếu bước tiếp với lệnh reviewseal23934/wave10/24009 và các gate; đồng bộ CURRENT,POLICY,budget,continuous-plan,Q&A. Metadata EAGLE3 đã phản ánh suite14caCPU; chưa outputmodel/acceptance/accuracy.
- Reviewers vàinputsuite đã sẵn; không còn việc độc lập cần làm. Kết thúc không chờqueue; giữ giới hạnrepeat,gatecomboN54 vàkhôngN56/promotion.

[Bằng chứng scheduler](../../2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0540UTC/slurm-queue.json) · [Phiếu bước tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0540UTC/NEXT_STEP.md).
'''
save(auto/'LATEST.md',report)
p=auto/'HISTORY.md';save(p,p.read_text()+'\n\n'+report)
qa='''

**16/10/2026 05:42 UTC — SSH báo Permission denied có còn là mất VPN không?**

Không đồng nhất hai tầng lỗi. Lúc05:30 helper chưa tìm thấy namespace VPN sống;
lúc05:40 ssh-batch đã tới SSH server nhưng bị Permission denied(password).
Kiểm chỉ đọc xác nhận snx-tun UP và route tới NSCC qua tunnel. Chưa có SSH
xác thực dùng được nên PBS220575 vàcredit vẫn chưa biết. BatchMode không hỏi
password; lỗi này không chứng minh password sai. Không suy ai tạo phiên mới,
hoặc cấu hình/lifetime24h đã thành công, chỉ từ interface đang UP. Không đọc
session/credential, không thửloginVPN/DUO/password hay SSH lặp khi không có
chỉ dẫn mới. Giữ1536SU reserve đến khi thật sự thu được queue/accounting.
Bằng chứng: `nscc-pbs/inspection/wake-20261016-0540UTC/`.
'''
p=base/'workspace/tutorial/14-so-tay-hoi-dap.md';save(p,p.read_text()+qa)
access=json.loads((out/'nscc-readonly.json').read_text())
msg='At2026-10-16T05:40:37UTC existing namespace ssh-batch reached SSH but failed Permission denied(password), exit255. Read-only05:40:56 confirms snx-tun UP and route through tunnel; origin/age/24h lifetime unverified. No authenticated PBS/credit refresh;220575 state/result unknown, retain1536SU. No new VPN login/DUO, credential supplied, repeated SSH or qsub.'
with (research/'nscc-pbs/budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 p=research/'nscc-pbs/nscc-budget.json';o=json.loads(p.read_text());o['updated_utc']=now;o['reconciliation_note']=msg
 for j in o['jobs']:
  if j['job_id']=='220575.pbs111':j.update(scheduler_comment=msg,latest_attempted_check_utc=access['checked_utc'],state_fresh=False)
 source='nscc-pbs/inspection/wake-20261016-0540UTC/nscc-readonly.json'
 o['evidence'].append(source)
 o['latest_access_check']={'checked_utc':access['checked_utc'],'state':'EXISTING_TUNNEL_SSH_BATCH_AUTH_UNAVAILABLE','pbs_and_credit_refreshed':False,'new_authentication_attempted':False,'authentication_field_scope':'No new VPN authentication or credential supplied; existing-access SSH BatchMode probe was attempted.','new_vpn_authentication_attempted':False,'ssh_batch_attempted':True,'credentials_supplied':False,'qsub_attempted':False,'source':source,'network_evidence':'nscc-pbs/inspection/wake-20261016-0540UTC/vpn-network-readonly.json','last_confirmed_job_state':'220575.pbs111 R at2026-10-15T20:12:38Z'}
 save(p,json.dumps(o,indent=2,ensure_ascii=False)+'\n')
 p=research/'nscc-pbs/continuous-plan.json';o=json.loads(p.read_text());o.update(updated_utc=now,access_status=msg,latest_evidence=source)
 d=json.loads((research/'nscc-pbs/research-next/eagle3-01/design.json').read_text())
 for branch in o['research_branches']:
  if branch['id']=='eagle3-01':
   branch['native_capture_preparation']=d['native_capture_preparation']
   branch['token_suite_preparation']=d['token_suite_preparation']
 save(p,json.dumps(o,indent=2,ensure_ascii=False)+'\n')
print('Updated handoff, reports, Q&A, budget and continuous-plan; financial amounts and job state timestamps unchanged.')
