from pathlib import Path
import json,datetime,fcntl
base=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs')
ws=Path('/home/apacsc42/workspace')
out=base/'inspection/wake-20261016-0055UTC'
live=json.loads((out/'live-check.json').read_text());q=json.loads((out/'final-queue.json').read_text())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
evidence='inspection/wake-20261016-0055UTC/live-check.json'
access='No PBS/credit refresh at2026-10-16 00:55:29UTC: existing-access helper found no live VPN session before SSH.220575 current state/result unknown; retain1536SU reserve. Historical04:00SGT16Oct ledger unchanged. New authentication prohibited by current user instruction; no authentication/qsub.'
with (base/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 p=base/'nscc-budget.json';d=json.loads(p.read_text());d['updated_utc']=now;d['reconciliation_note']=access
 d['evidence'].append(evidence)
 d['latest_access_check'].update(checked_utc=live['checked_utc'],source=evidence)
 for j in d['jobs']:
  if j['job_id']=='220575.pbs111':j.update(scheduler_comment=access,latest_attempted_check_utc=live['checked_utc'],state_fresh=False)
 p.write_text(json.dumps(d,indent=2)+'\n')
 p=base/'continuous-plan.json';d=json.loads(p.read_text());d.update(updated_utc=now,latest_evidence=evidence,access_status=access)
 for branch in d['research_branches']:
  if branch['id']=='eagle3-01':branch.update(source_review='research-next/eagle3-01/SOURCE_REVIEW.md',source_review_state='12_STATIC_CHECKS_PASS_NO_GPU_VALIDATION',next_quality_constraints='Simulation disabled inside workers; all-greedy neutral requests; max-running-requests48 matched control/candidate. Compiled CUDA and Instruct-2507 output compatibility remain unverified.')
 p.write_text(json.dumps(d,indent=2)+'\n')
p=ws/'notes/CURRENT.md';s=p.read_text().replace('lượt research00:45–00:52UTC','lượt research00:55–00:59UTC')
s=s.replace('16/10 00:50:03UTC**: **23906/23924/23934 PENDING(Resources)**','16/10 00:58:48UTC**: **23906/23924/23934 PENDING(Resources)**')
s=s.replace('Kiểm tra helper mới16/10 00:46:05UTC','Kiểm tra helper mới16/10 00:55:29UTC')
marker='## Tự động hóa và bộ nhớ'
addition='''## Chuẩn bị EAGLE3 mới — 16/10 00:59 UTC

Đã kiểm tra source thực trong image bằng CPU: target forward→greedy argmax→
compiled verifier được xác minh ở tầng gọi Python, chưa chạy CUDA/model.
Hai threshold1.0 không nằm ở nhánh greedy và không tự chứng minh output giống
control. Source có simulation ghi đè acceptance/token sau verifier; future worker
phải đặt và ghi `SGLANG_SIMULATE_ACC_LEN=-1` bên trong container. Không có bằng
chứng run cũ bật simulation, không sửa kết quả cũ.

Hook EAGLE mặc định max_running_requests48 khi chưa đặt; thiết kế local đã đặt
rõ48 và yêu cầu control giống vậy. Kiểm output đầu dùng toàn request greedy,
neutral penalties, không grammar/logitbias; lưu token IDs thật, điều tra khác biệt
FP8/batching/kernel trước mọi quality/performance claim. Qwen có API capture aux
hidden states nhưng compatibility Instruct-2507, token map, memory và native CUDA
vẫn chưa xác minh. 12 kiểm tra source đạt,72 file được hash; không phải GPU test.
Không tải draft, không job/reservation mới;04→05→06 và mọi gate hiện có giữ nguyên.
[Review EAGLE3](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/SOURCE_REVIEW.md).

Snapshot mới00:58:48UTC:23906/23924/23934 PENDING(Resources),watcher sống;
00:55:29UTC helper thiếuVPN trướcSSH,220575/result/credit chưa xác minh.
Giữ1536SUreserve,campaign16384SU;khôngauth/qsub. Snapshot00:50/00:46 ở trên là
lịch sử,không phải lần kiểm mới. Bằng chứng:`nscc-pbs/inspection/wake-20261016-0055UTC/`.

'''
assert marker in s;s=s.replace(marker,addition+marker);p.write_text(s)
p=ws/'tutorial/14-so-tay-hoi-dap.md'
with p.open('a') as f:f.write('''

**16/10/2026, 00:59 UTC — EAGLE3 đặt threshold1.0 đã đủ chứng minh lossless chưa?**

Chưa. Source trong image đang dùng cho thấy nhánh toàn request greedy lấy
argmax từ logits target rồi gọi compiled greedy verifier; hai threshold được
truyền ở nhánh sampling. Đây là bằng chứng luồng gọi, chưa kiểm CUDA/output thật.
FP8, cách batch và kernel verify có thể khác decode thường; phải lưu token IDs
và đối chiếu control cùng target/settings. Không suy rộng kết luận greedy sang
phân phối sampling, request penalties hoặc grammar.

Đặc biệt `SGLANG_SIMULATE_ACC_LEN > 0` có thể ghi đè acceptance sau verifier,
thậm chí điền token100 hay ép nhận draft. Default trong image là -1; future worker
phải ghi rõ -1 bên trong container. Không có bằng chứng các run trước bật chế độ
này. EAGLE hook còn tự đặt max_running_requests48 khi chưa có giá trị: control
và candidate phải cùng48 để tránh so khác giới hạn. Thiết kế hiện có3steps/topk1/
4tokens nhất quán với hook; chưa có draft weights/GPU test hay kết luận accuracy.
12 kiểm tra source/72 file hash không phải phép đo serving hoặc kiểm output.
[Review thực tế và bước thử tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/SOURCE_REVIEW.md).
''')
p=ws/'research-autopilot/POLICY.md';s=p.read_text().replace('current handoff2026-10-16 00:52UTC','current handoff2026-10-16 00:59UTC')
s=s.replace('Latestqueue16Oct00:50:03UTC','Latestqueue16Oct00:58:48UTC').replace('At16Oct00:46:05UTC helper again found','At16Oct00:55:29UTC helper again found')
s+='''

## Handoff wake16Oct00:55–00:59UTC

- Live00:58:48UTC:23906/23924/23934 PENDING(Resources),3/5slots;watcher3514431alive.
  No GPU result or new job/repeat/N56/controller/schedule.
- EAGLE3 independentCPUadvance: actual image source confirms target-forward→
  greedy-argmax→compiled-verifier dispatch.12staticchecks pass,72Pythonfiles hashed.
  Not nativeCUDA/model validation. Simulation can override real acceptance;
  future worker must record SGLANG_SIMULATE_ACC_LEN=-1 inside container. No evidence
  old benchmarks used simulation; no old performance result changed.
- Localdesign now explicitly matches max-running-requests48 in monolithic control/
  candidate (EAGLE default48 is a confounder otherwise). Initial quality requests
  all-greedy/neutral/no grammar, preserve real token IDs; threshold1.0 alone does
  not prove FP8 token equality or stochastic equivalence. Actual CUDA, Instruct2507
  compatibility/acceptance, hiddenstates/tokenmap/memory/PD still unvalidated.
  No draft weights downloaded; no GPU payload or reservation changed.
- NSCC00:55:29UTC noexistingVPNbeforeSSH;220575/result/credit unknown. No newauth/
  qsub;1536SUreserve,campaign16384SU,04→05→06priority and runtime gates unchanged.
- Evidence nscc-pbs/inspection/wake-20261016-0055UTC/. Source review and updated
  design:nscc-pbs/research-next/eagle3-01/SOURCE_REVIEW.md. CURRENT/Q&A/plan/budget
  updated. Preparation complete; finish without idle queue wait or login retry.
''';p.write_text(s)
report='''# Báo cáo Qwen — 2026-10-16 00:59 UTC

- **H200 00:58:48 UTC:** 23906/23924/23934 vẫn PENDING(Resources), 3/5 slot; watcher còn sống. Chưa có số đo GPU mới.
- **Tiến triển CPU:** kiểm source EAGLE3 trong image, 12 kiểm tra cấu trúc đạt, 72 file được hash. Đã làm rõ nhánh target verification, yêu cầu tắt simulation acceptance và đặt cùng giới hạn 48 request cho control/candidate. Thiết kế tiếp theo đã cập nhật; CUDA/output/compatibility Instruct-2507 vẫn chưa kiểm chứng.
- **NSCC 00:55:29 UTC:** thiếu phiên VPN trước SSH; 220575/kết quả/credit chưa xác minh. Giữ 1536 SU dự trù, campaign 16384 SU; pilot 04→05→06 giữ thứ tự và gate. Không xác thực mới/qsub/tải draft.
- Đã cập nhật CURRENT, POLICY, Q&A, plan/budget và giữ bằng chứng. Không thêm job/repeat/N56/lịch; kết thúc sau phần chuẩn bị, watcher tiếp tục thu ba job.

[Review EAGLE3](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/SOURCE_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0055UTC/).
'''
(ws/'research-autopilot/LATEST.md').write_text(report)
with (ws/'research-autopilot/HISTORY.md').open('a') as f:f.write('\n\n'+report.replace('# Báo cáo','## Báo cáo',1))
print('Handoff and budget access status updated; SU amounts and gates unchanged.')
