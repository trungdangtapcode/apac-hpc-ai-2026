import datetime,fcntl,hashlib,json,re
from pathlib import Path
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');N=Path('/home/apacsc42/workspace/notes');A=Path('/home/apacsc42/workspace/research-autopilot');O=Path(__file__).resolve().parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat();live=json.loads((O/'live-check.json').read_text());final=json.loads((O/'final-queue.json').read_text());val=json.loads((O/'offline-validation.json').read_text());ev=str(O.relative_to(R/'nscc-pbs'))
assert len(val['cpu_cases'])==21 and all(c['pass'] for c in val['cpu_cases'])
assert all(k in val['historical_baselines'] for k in ['23778','23839','23780','23859'])
assert live['nscc']['returncode']==1 and 'Expected one live VPN session' in live['nscc']['stderr']
assert all(final[k]['returncode']==0 for k in ['queue','accounting','watcher'])
rows=[l.split('|') for l in final['queue']['stdout'].splitlines() if l.strip()]
assert {r[0]:r[1] for r in rows}=={'23906':'PENDING','23924':'PENDING','23934':'PENDING'},rows
for p in [N/'CURRENT.md',A/'POLICY.md',A/'LATEST.md']:(O/(p.name+'.before')).write_bytes(p.read_bytes())
access='No PBS/credit refresh at2026-10-16 00:46:05UTC: existing-access helper found no live VPN session before SSH.220575 current state/result unknown; retain1536SU reserve. Historical04:00SGT16Oct ledger unchanged. New authentication prohibited by current user instruction; no authentication/qsub.'
with (R/'nscc-pbs/budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 p=R/'nscc-pbs/nscc-budget.json';d=json.loads(p.read_text());(O/'budget-before-update.json').write_text(json.dumps(d,indent=2)+'\n')
 assert d['commissioning_cap_su']==16384 and sum(x['max_charge_su'] for x in d['pending_reservations'])==1536
 d.update(updated_utc=now,reconciliation_note=access)
 d['latest_access_check'].update(checked_utc=live['checked_utc'],source=ev+'/live-check.json',state='VPN_SESSION_MISSING_BEFORE_SSH',pbs_and_credit_refreshed=False,new_authentication_attempted=False,qsub_attempted=False)
 for j in d['jobs']:
  if j['job_id']=='220575.pbs111':j.update(scheduler_comment=access,latest_attempted_check_utc=live['checked_utc'],state_fresh=False)
 d['evidence'].append(ev+'/live-check.json');p.write_text(json.dumps(d,indent=2)+'\n')
 p=R/'nscc-pbs/continuous-plan.json';d=json.loads(p.read_text());d.update(updated_utc=now,access_status=access,latest_evidence=ev+'/live-check.json');p.write_text(json.dumps(d,indent=2)+'\n')
p=N/'CURRENT.md';s=p.read_text();s=re.sub(r'Cập nhật kiến thức: \*\*.*?\*\*\.', 'Cập nhật kiến thức: **16/10/2026, lượt research00:45–00:52UTC**.',s,count=1)
s=s.replace('Kiểm tra queue mới **16/10 00:19:38UTC**','Kiểm tra queue mới **16/10 00:50:03UTC**')
s=s.replace('Kiểm tra helper mới16/10 00:15:52UTC','Kiểm tra helper mới16/10 00:46:05UTC')
paragraph='''
Đã chuẩn bị công cụ CPU `serving-tuning/review-n54.py` để đọc hai job hiện có
23924/23934 sau khi watcher thu xong. Kiểm tra offline qua **21 ca**, rehash bốn
N52 baseline và tái tính đúng goodput cũ; **không có số đo GPU mới**. Tool so cả
hai baseline/mean, kiểm tra seal/payload/protocol, raw count/length/good/mean latency,
NIXL/warmup, resolved ServerArgs và phân biệt thiếu bằng chứng với đo đủ nhưng
fail SLA. Hiện cả hai N54 chưa có terminal seal; chưa xác minh runtime N54.
Không tự mở job/repeat/N56 và không thay watcher hay frozen payload.

Phát hiện khi đối soát bốn export N52: goodput dùng số good request chia khoảng
profiling phase trong manifest; `benchmark_duration` ngắn hơn khoảng 2,8–4,0 ms.
Đã giữ đúng convention hiện có, không sửa số liệu cũ hay suy ra nguyên nhân clock.
DP original/repeat cũng có max observed length 200/201; extrema là diagnostic,
không phải điều kiện phải giống hệt. Các prototype false-reject được giữ cùng
đính chính. [Hướng dẫn N54](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md).
Bằng chứng: `nscc-pbs/inspection/wake-20261016-0045UTC/`. Snapshot 00:19 là lịch sử;
00:50:03 vẫn ba job PENDING(Resources), watcher sống; NSCC 00:46:05 thiếu VPN,
220575/credit vẫn chưa xác minh, giữ 1536 SU và gate 04→05. Không xác thực mới.
'''
s=s.replace('\n## Tự động hóa','\n'+paragraph+'\n## Tự động hóa');p.write_text(s)
p=A/'POLICY.md';s=p.read_text();s=s.replace('current handoff2026-10-16 00:19UTC','current handoff2026-10-16 00:52UTC',1)
s=s.replace('Latestqueue16Oct00:19:38UTC:','Latestqueue16Oct00:50:03UTC:',1)
s=s.replace('At16Oct00:15:52UTC helper again found','At16Oct00:46:05UTC helper again found',1)
s+='''

## Handoff wake16Oct00:45–00:52UTC

- Live00:50:03UTC:23906/23924/23934 PENDING(Resources),3/5slots;watcher3514431alive.
  No new benchmark result, GPU job, repeat/N56, controller or schedule.
- Prepared serving-tuning/review-n54.py: local offline terminal-evidence review
  for existing23924/23934.21CPUcases pass and four historicalN52baselines rehash/
  rawmetric replay pass. Pending jobs correctly report no terminal evidence.
  Actual N54 terminal path remains unvalidated until collection; no promotion.
- Four historical exports: goodput denominator matches profiling manifest elapsed,
  slightly different from benchmark_duration by2.8–4.0ms. Use existing convention;
  no changed results or universal timing/causal claim. Observed extrema vary even
  between DP repetitions; report ranges rather than inventing a hard equality gate.
- NSCC00:46:05UTC no existing VPN beforeSSH.220575/result/credit still unknown;
  no new authentication/qsub,1536SUreserve,campaign16384SU,04→05gates unchanged.
  Latest user prohibition on new VPN authentication remains controlling.
- Evidence nscc-pbs/inspection/wake-20261016-0045UTC/.UpdatedCURRENT,Q&A,review,
  budget/planunderlock,LATEST,HISTORY. Finish after preparation; no idle queue wait.
''';p.write_text(s)
p=Path('/home/apacsc42/workspace/tutorial/14-so-tay-hoi-dap.md')
with p.open('a') as f:f.write('''

**16/10/2026, 00:52 UTC — Tái tính goodput bằng thời gian nào, và kiểm thử offline có phải repeat mới không?**

Trong bốn export N52 của 23778/23839/23780/23859, `good_request_count / goodput`
khớp đúng khoảng profiling phase `(end_ns-start_ns)/1e9` trong manifest.
`benchmark_duration` ngắn hơn lần lượt 2,798247 / 3,975055 / 2,993710 / 2,870008 ms.
Khi đối soát các run này, dùng thời gian phase để giữ convention benchmark;
không thay bằng đúng 120 giây hay thời gian job Slurm. Chưa xác định nguyên nhân
khác biệt và không suy rộng thành quy tắc mọi phiên bản AIPerf.

`review-n54.py` được kiểm bằng bốn run đã lưu và 21 ca CPU. Tái tính đúng số cũ
chỉ chứng minh bộ đọc/đối soát hoạt động với bằng chứng đó; không tạo phép đo GPU
hay independent repeat mới. Hai job N54 vẫn pending tại 00:50:03 UTC; chưa có
terminal seal thì tool không báo đã đo. Một run có đầy đủ bằng chứng nhưng SLA
thấp hơn 90% phải được ghi là điểm đo fail SLA; startup thiếu export là loại khác.

Đừng đặt thêm điều kiện observed extrema phải giống hệt giữa hai run: DP original
và repeat có max 200/201 tokens. Giữ raw count/sum/min/max và suite kiểm chất lượng;
điều này không đồng nghĩa mọi response đúng 200 hay accuracy BTC đã đạt.
[Hướng dẫn và giới hạn công cụ](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md).
''')
latest='''# Báo cáo Qwen — 2026-10-16 00:52 UTC

- **H200 kiểm tra 00:50:03 UTC:** 23906/23924/23934 đều PENDING(Resources), 3/5 slot; watcher còn sống. Chưa có số đo GPU mới.
- Đã chuẩn bị **công cụ đối soát N54**: qua 21 ca CPU, rehash và tái tính đúng bốn baseline đã lưu. So từng baseline và trung bình, kiểm tra bằng chứng thô; phân biệt thiếu export với điểm đo đủ nhưng fail SLA. Runtime N54 còn chờ.
- Khi tái tính bốn run cũ, goodput dùng thời gian profiling phase trong manifest; `benchmark_duration` lệch khoảng 2,8–4,0 ms. Đã ghi rõ convention và giữ các prototype/đính chính, không sửa số liệu cũ.
- **NSCC 00:46:05 UTC:** thiếu phiên VPN; 220575/kết quả/credit chưa xác minh. Giữ 1536 SU dự trù, trần campaign 16384 SU, pilot 04→05 chờ các gate hiện hành. Không xác thực mới hay qsub.
- Đã cập nhật CURRENT, POLICY, Q&A, review, budget/plan và HISTORY. Không thêm job/repeat/N56 hay lịch; kết thúc sau phần chuẩn bị, watcher tiếp tục thu ba job.

[Hướng dẫn N54](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0045UTC/).
'''
(A/'LATEST.md').write_text(latest)
with (A/'HISTORY.md').open('a') as f:f.write('\n\n'+latest.replace('# Báo cáo','## Báo cáo',1))
summary={'updated_utc':now,'h200_checked_utc':final['checked_utc'],'h200':rows,'cpu_cases_pass':21,'new_gpu_measurement':False,'new_jobs':False,'new_authentication':False,'qsub':False,'nscc_reserved_su':1536,'campaign_cap_su':16384,'remaining':'Watch existing three jobs; NSCC access/terminal220575/baseline/queue/credit gates before04. No independent work remains in this wake.'}
(O/'wake-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Handoff updated; budget unchanged, no jobs/authentication/schedules.')
