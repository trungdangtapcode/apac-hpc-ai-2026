"""Record this wake without changing frozen jobs, reservations or submission gates."""
import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT = Path(__file__).resolve().parent
WORK = Path('/home/apacsc42/workspace')
now = datetime.datetime.now(datetime.timezone.utc)
stamp = now.strftime('%H:%M UTC')
evidence = str(OUT.relative_to(ROOT))
final = {'checked_utc':now.isoformat()}
for name, cmd in {
    'queue':['squeue','--noheader','--user','apacsc42','--format=%A|%T|%S|%M|%N|%R'],
    'accounting':['sacct','-X','-n','-P','-j','23906,23924,23934','--format=JobID,State,ExitCode,Start,End,Elapsed,NodeList'],
    'watcher':['ps','-p','3514431','-o','pid,lstart,etime,args']}.items():
    p = subprocess.run(cmd,capture_output=True,text=True,timeout=25)
    assert p.returncode == 0, (name,p.stderr)
    final[name] = {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
assert '23906|RUNNING|' in final['queue']['stdout'], 'Reassess handoff: job state changed'
assert '23924|PENDING|' in final['queue']['stdout'] and '23934|PENDING|' in final['queue']['stdout']
assert 'watch-serving-tuning.py --run' in final['watcher']['stdout']
(OUT/'final-queue.json').write_text(json.dumps(final,indent=2)+'\n')
review=json.loads((OUT/'runtime-review.json').read_text())
assert review['mnnvl_ranks']==review['nixl_ucx_ranks']==list(range(8))
live=json.loads((OUT/'live-check.json').read_text())
assert live['nscc']['returncode']==1 and 'Expected one live VPN session' in live['nscc']['stderr']

paths=[WORK/'notes/CURRENT.md',WORK/'research-autopilot/POLICY.md',
       WORK/'research-autopilot/LATEST.md',ROOT/'serving-tuning-09/MATCHED_REVIEW.md']
for p in paths:
    (OUT/(p.name+'.before')).write_bytes(p.read_bytes())

runtime = f'''## Runtime chunk8192 — 16/10/2026 {stamp}

23906 RUNNING từ01:38:03UTC trên g1/g4; lần kiểm scheduler {now.strftime('%H:%M:%S')}UTC:
23924/23934 PENDING(Resources),3/5slot; watcher3514431 sống. Các snapshot
23906PENDING trước01:38 là lịch sử. Chưa có phép đo hoàn chỉnh mới.

Audit01:41:56UTC: frozen/copied payload, registryhash và Slurm-storedscript đạt;
11file chung giống CẢ23778/23839, worker chỉ đổi chunk4096→8192. Runtime cả hai
prefill xác nhận chunk8192 và breakable CUDAgraphmax_bs8192; so baseline4096,
capture bổ sung4608/5120/5632/6144/6656/7168/7680/8192. Các trường graph khác
và decodegraph1–64 giữ nguyên. ResolvedServerArgs chỉ khácchunk/graph và seed
engine tự sinh. Cả8rankMNNVL/NIXL đạt; P/Dwarmup chưa hoàn tất tại snapshot audit,
không coi đây là startupfailure. Logprefix đã hash, không phải finalseal.

Tiếp: watcher thu23906 rồi kiểm terminalexit/seal/full60/120/30/rawmetrics,
shortnonregression và2P/Dwarmup; so CẢ23778/23839 vàmean2592,542986, kèmTTFT/ITL.
Không quy kết riêng chunk scheduling; không thêmrepeat/N56/job/controller.
NSCC01:40:59UTC helper thiếuVPN trướcSSH;220575/result/credit vẫn chưa xác minh.
Giữ1536SUreserve,campaign16384SU và04→05→06 gates; không xác thực mới/qsub.
Bằng chứng:`{evidence}/`.
'''
current=paths[0].read_text()
current=current.replace('Cập nhật kiến thức: **16/10/2026, lượt research00:55–00:59UTC**.',
                        f'Cập nhật kiến thức: **16/10/2026, lượt research01:40–{stamp}**.')
anchor='## Điều cần nhớ trước tiên'
current=current.replace(anchor,runtime+'\n'+anchor,1)
current=current.replace('Kiểm tra queue mới **16/10 00:58:48UTC**:',
                        'Snapshot lịch sử **16/10 00:58:48UTC**:')
current=current.replace('Snapshot mới00:58:48UTC:', 'Snapshot lịch sử00:58:48UTC:')
paths[0].write_text(current)

policy=paths[1].read_text().replace('current handoff2026-10-16 00:59UTC',f'current handoff2026-10-16 {stamp}')
policy=policy.replace('Latestqueue16Oct00:58:48UTC:23906/23924/23934 PENDING(Resources),\n  threeofcap5;watcher3514431alive.',
    f'Latestqueue16Oct{now.strftime("%H:%M:%S")}UTC:23906RUNNING since01:38:03UTC,g1/g4;\n  23924/23934PENDING(Resources),threeofcap5;watcher3514431alive. Runtime23906\n  confirmschunk8192ANDprefillgraph8192;nofinalexportat01:41:56audit. Earlierpending\n  snapshotsarehistorical. Seehandoffbelow.')
policy=policy.replace('At16Oct00:55:29UTC helper again found NO liveVPNsession',
                      'At16Oct01:40:59UTC helper again found NO liveVPNsession')
policy+='\n\n'+runtime
paths[1].write_text(policy)

guide=paths[3].read_text().replace('| 23906 | prefill chunk8192 | pending | pending | pending | pending |',
    '| 23906 | prefill chunk8192; runtime graph8192 confirmed | running; no final result | — | — | — |')
guide+='\n\n'+runtime
paths[3].write_text(guide)

qa=WORK/'tutorial/14-so-tay-hoi-dap.md'
with qa.open('a') as f:
    f.write(f'''\n\n**16/10/2026, {stamp} — Chunk8192 có thực sự giữ graph prefill như baseline4096 không?**

Không. Runtime job23906 xác nhận cả hai worker prefill dùng chunk8192 và
breakable CUDAgraph max_bs8192, bổ sung8capture4608–8192 so với hai baseline
23778/23839. Decodegraph1–64 giữ nguyên; các trường graph khác không đổi.
Kết hợp bằng chứng chunk2048 trước đó, ba cấu hình đã đổi cả chunk lẫn graph
prefill được engine suy ra. Không quy riêng hiệu ứng goodput/startup cho chunk
scheduling. Đây là audit log khởi tạo, chưa có kết quả benchmark mới hay chứng
nhận accuracy. Khi có final export, kiểm seal/protocol/raw output và so cả hai
baseline với TTFT/ITL. [Bằng chứng]({OUT}/runtime-review.json).
''')

access_note=('No PBS/credit refresh at2026-10-16 01:40:59UTC: existing-access helper found no live VPN '
    'session before SSH.220575 current state/result unknown; retain1536SU reserve. Historical04:00SGT16Oct '
    'ledger unchanged. New authentication prohibited by current user instruction; no authentication/qsub.')
with (ROOT/'nscc-pbs/budget.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    budget_path=ROOT/'nscc-pbs/nscc-budget.json'
    budget=json.loads(budget_path.read_text())
    (OUT/'budget-before-update.json').write_text(json.dumps(budget,indent=2)+'\n')
    budget['updated_utc']=now.isoformat()
    budget['reconciliation_note']=access_note
    for job in budget['jobs']:
        if job['job_id']=='220575.pbs111':
            job['scheduler_comment']=access_note
            job['latest_attempted_check_utc']=live['checked_utc']
            job['state_fresh']=False
    budget['latest_access_check'].update(checked_utc=live['checked_utc'],source=evidence+'/live-check.json')
    budget['evidence'].append(evidence+'/live-check.json')
    budget_path.write_text(json.dumps(budget,indent=2)+'\n')
    plan_path=ROOT/'nscc-pbs/continuous-plan.json'
    plan=json.loads(plan_path.read_text())
    plan.update(updated_utc=now.isoformat(),latest_evidence=evidence+'/live-check.json',access_status=access_note)
    plan_path.write_text(json.dumps(plan,indent=2)+'\n')

report=f'''# Báo cáo Qwen — 2026-10-16 {stamp}

- **H200 {now.strftime('%H:%M:%S')} UTC:** 23906 RUNNING từ01:38:03 trên g1/g4; 23924/23934 PENDING(Resources), 3/5 slot; watcher còn sống. Chưa có kết quả benchmark mới.
- **Tiến triển:** audit23906 đạt checksum payload/script; cả8rank MNNVL/NIXL. Hai worker prefill dùng chunk8192 **đồng thời graph prefill tăng4096→8192**, thêm8capture; decodegraph giữ nguyên. So cả hai baseline, chỉ khác chunk/graph và seed tự sinh. Không quy kết riêng cho chunk scheduling.
- Đã ghi checklist thu/đối soát final23906 trong review; log khởi tạo có hash, chưa phải finalseal. P/Dwarmup chưa xong tại audit01:41:56, không coi là lỗi. Watcher tiếp tục thu23906 và hai N54; không thêmjob/repeat/N56/lịch.
- **NSCC01:40:59 UTC:** thiếuVPN trướcSSH;220575/kết quả/credit vẫn chưa xác minh. Giữ1536SU dự trù, campaign16384SU, pilot04→05→06 và các gate. Không xác thực mới/qsub.
- Đã cập nhật CURRENT/POLICY/Q&A/review và budget/plan dưới lock; giữ bằng chứng. Kết thúc sau phần việc độc lập, không chờ queue.

[Review]({ROOT}/serving-tuning-09/MATCHED_REVIEW.md) · [Bằng chứng]({OUT}/runtime-review.json).
'''
paths[2].write_text(report)
with (WORK/'research-autopilot/HISTORY.md').open('a') as f:
    f.write('\n\n'+report)
(OUT/'wake-summary.json').write_text(json.dumps(dict(finished_utc=now.isoformat(),
    benchmark_result_claimed=False,new_jobs_submitted=False,new_authentication_attempted=False,
    independent_runtime_audit_passed=True,nscc_reserve_su=1536),indent=2)+'\n')
print(json.dumps(final,indent=2))
