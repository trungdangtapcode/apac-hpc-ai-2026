"""Persist completed chunk8192 review; no scheduler mutation or authentication."""
from pathlib import Path
import datetime, fcntl, hashlib, json, re, subprocess
ROOT=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
WORK=Path('/home/apacsc42/workspace')
OUT=Path(__file__).resolve().parent
EVID=str(OUT.relative_to(ROOT))
now=datetime.datetime.now(datetime.timezone.utc)
stamp=now.strftime('%H:%M:%S UTC')
review=json.loads((OUT/'chunk8192-final-review.json').read_text())
assert review['state']=='MEASURED_PASS_SLA'
assert review['runs']['23906']['sealed_files']==47
live=json.loads((OUT/'live-check.json').read_text())
assert live['pbs']['rc']==1 and 'Expected one live VPN session' in live['pbs']['stderr']
final={'checked_utc':now.isoformat()}
for name,cmd in {
 'queue':['squeue','-h','-u','apacsc42','-o','%i|%T|%S|%M|%R'],
 'accounting':['sacct','-X','-n','-P','-j','23906,23924,23934','--format=JobID,State,ExitCode,Start,End,Elapsed,NodeList'],
 'watcher':['ps','-p',(ROOT/'serving-tuning/watcher.pid').read_text().strip(),'-o','pid,lstart,etime,args']}.items():
 p=subprocess.run(cmd,text=True,capture_output=True,timeout=25)
 assert p.returncode==0,(name,p.stderr)
 final[name]={'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
assert len(final['queue']['stdout'].strip().splitlines())==2
assert all(f'{j}|PENDING|' in final['queue']['stdout'] for j in ['23924','23934'])
assert '23906|COMPLETED|0:0|' in final['accounting']['stdout']
assert 'watch-serving-tuning.py --run' in final['watcher']['stdout']
(OUT/'final-queue.json').write_text(json.dumps(final,indent=2)+'\n')
paths=[WORK/'notes/CURRENT.md',WORK/'research-autopilot/POLICY.md',WORK/'research-autopilot/LATEST.md',ROOT/'serving-tuning-09/MATCHED_REVIEW.md',WORK/'tutorial/14-so-tay-hoi-dap.md']
for p in paths:
 (OUT/(p.name+'.before')).write_bytes(p.read_bytes())
block=f'''## Bàn giao 16/10/2026 {stamp}

23906 **COMPLETED exit0** lúc01:48:16UTC, đã được watcher thu và finalaudit độc lập.
Tại{stamp}:23924/23934 **PENDING(Resources)**,2/5slot;watcher3514431 sống.
Các snapshot23906RUNNING/chưa seal trước01:48 và pending trước01:38 là lịch sử.

Chunk8192 đạt **2547,8540 goodtokens/s**,SLA98,8672%,TTFT735,5602ms,
ITL16,3160ms;thấp hơn mean23778/23839 **1,7238%** (từng baseline−1,7093%/−1,7382%).
So mean,TTFT+223,2940ms dù ITL−0,8249ms. Full60/120/30,47file seal/mỗi run,
frozen/copied payload và script Slurm lưu trước đó khớp;789warmup/1589profiling,
0lỗi/hủy request;8rankMNNVL/NIXL,2P/Dwarmup;short7/8,chỉreverse đã biết.
Observed output200–201tokens,rawsum317801 khớp;goodput vẫn dùng convention200.
ChunkCLI đồng thời đổi prefillgraph4096→8192;decodegraph không đổi,engine seed
chưa khóa. Đây là một điểm đo đủSLA nhưng goodput thấp hơn,các kết quả không cô
lập hiệu ứng scheduling. Chưa chọn cấu hình hay xác nhận accuracyBTC.

Công cụ final đã chạy đạt trên23906;không còn chỉ là prototype chờ terminal.
Cả ba wave9 đã finalaudit;chỉFlashInfer+MNNVL23904 có lợi thế một lượt+1,4867%,
chưa repeat/chọn cấu hình. Tiếp:watcher thu haiN54,chạy`serving-tuning/review-n54.py`
và so cả hai baseline/mean. Không thêmjob/repeat/N56/controller/schedule.

NSCC01:50:59UTC helper vẫn thiếuVPN trướcSSH;220575/result/credit chưa xác minh.
Giữ1536SUreserve,campaign16384SU,04→05→06 và các gate hiện có;khôngauth/qsub.
Bằng chứng:`{EVID}/chunk8192-final-review.json`;raw artifact giữ tại`runs/23906/`.
'''
current=paths[0].read_text()
current=re.sub(r'Cập nhật kiến thức: \*\*[^\n]+',f'Cập nhật kiến thức: **16/10/2026, lượt research01:50–{now.strftime("%H:%M")}UTC**.',current,count=1)
start=current.index('## Bàn giao ')
end=current.index('## Điều cần nhớ trước tiên',start)
current=current[:start]+block+'\n'+current[end:]
current=current.replace('| H200,MNNVL+chunk2048,N52 | 23905 | **2331,35**, SLA98,77%, ITL15,81ms; một lượt |','| H200,MNNVL+chunk2048,N52 | 23905 | **2331,35**, SLA98,77%, ITL15,81ms; một lượt |\n| H200,MNNVL+chunk8192,N52 | 23906 | **2547,85**, SLA98,87%, ITL16,32ms; một lượt |')
current=current.replace('Tiếp: watcher thu hai nhánhN54 (23924/23934) vàwave9 còn23906;','Tiếp: watcher thu hai nhánhN54 (23924/23934); cả ba wave9 đã hoàn tất/finalaudit;')
paths[0].write_text(current)
policy=paths[1].read_text()
policy=re.sub(r'^# Autonomous Qwen research[^\n]*',f'# Autonomous Qwen research — current handoff2026-10-16 {stamp}',policy,count=1)
start=policy.index('Latestqueue16Oct')
end=policy.index('23904 COMPLETED',start)
policy=policy[:start]+f'''Latestqueue16Oct{now.strftime('%H:%M:%S')}UTC:23924/23934PENDING(Resources),twoofcap5;
  watcher3514431alive.23906COMPLETEDexit0at01:48:16UTC;finalauditPASS,2547.8540goodt/s,
  SLA98.8672%,TTFT735.5602ms,ITL16.3160ms,0requesterrors/cancel,short7/8knownreverse.
  Versusboth23778/23839:−1.7093%/−1.7382%;versusmean−1.7238%,TTFT+223.2940ms,
  ITL−0.8249ms.47-file-seals/rawcounts/protocol/runtimeallverified.
  Chunk8192ANDprefillgraph8192;noisolatedschedulingclaim. Allwave9terminalaudited.
  Earlierpending/running/unsealeddescriptionsarehistorical. '''+policy[end:]
policy=policy.replace('At16Oct01:45:30UTC helper again','At16Oct01:50:59UTC helper again')
policy+='\n\n'+block
paths[1].write_text(policy)
guide=paths[3].read_text().replace('| 23906 | prefill chunk8192; runtime graph8192 confirmed | running; no final result | — | — | — |','| 23906 | prefill chunk8192 and derived graph8192 | 2547.8540 | 98.8672% | 735.5602 | 16.3160 |')
guide+='\n\n'+block+f'''
Final candidate phases: warmup62.995751311s/789requests;profiling123.319468811s/
1589requests,1571good. Output extrema200–201,mean200.0006293,sum317801.
All47files in each candidate/baseline seal rehashed. Runtimecopied logs now
terminal, replacing growing-prefix status in historical audits. The original
01:45 review remains an archived prototype; this run copied it into a new
inspection directory before execution, preserving previous evidence unchanged.

| Candidate | Gain vs23778 | Gain vs23839 | Gain vs mean | TTFT delta vs mean | ITL delta vs mean |
|---|---:|---:|---:|---:|---:|
| 23906 chunk8192+MNNVL | −1.7093% | −1.7382% | −1.7238% | +223.2940ms | −0.8249ms |

[Final review](../{EVID}/chunk8192-final-review.json) and
[terminal runtime audit](../{EVID}/runtime-review.json).
'''
paths[3].write_text(guide)
qa=paths[4].read_text()
qa=qa.replace('Với23906chunk8192cònPENDINGở00:19:38UTC,phảichờlogthựcđểxácminhgraph.','Snapshot23906PENDINGở00:19:38UTC là lịch sử;runtime01:43 xác nhận graph8192,\nfinalaudit01:51 bên dưới đã hoàn tất.')
qa=qa.replace('scheduling. Đây là audit log khởi tạo, chưa có kết quả benchmark mới hay chứng\nnhận accuracy. Khi có final export, kiểm seal/protocol/raw output và so cả hai\nbaseline với TTFT/ITL.','scheduling. Đoạn01:43 này là audit khởi tạo lịch sử;finalaudit01:51 bên dưới\nđã có đủ export/seal/protocol/raw output;accuracyBTC vẫn chưa xác nhận.')
qa+=f'''

**16/10/2026, {now.strftime('%H:%M')} UTC — Tăng chunk8192 có tốt hơn baseline4096 sau khi đo đủ không?**

Lần23906 đạt2547,85goodtokens/s,SLA98,87%,0lỗi/hủy request;seal/raw/protocol đềuđạt.
So meanhai baseline23778/23839,goodputgiảm1,7238%;TTFTtăng223,294ms dùITLgiảm0,8249ms.
Đây là điểm đo hoàn chỉnh nhưng kém vềgoodput,chưa phải cấu hình nên chọn.
Cảchunk2048 và8192 đều cómeanITLthấp hơn4096 nhưnggoodputthấp hơn trong các lượt này;
không suy ra ITLthấp hơn luôn phục vụnhanh hơn,hay khẳngđịnh4096tốiưu mọi tải.

Chunk8192 còn tănggraphprefilltheo giátrịchunk;không cô lập hiệuứng scheduling.
Observedoutput200–201token,rawsum317801/1589request khớp;quyướcgoodputvẫn200tokens.
Short7/8chỉreverseđãbiết chứngminh không thêm lỗi trong suite nhỏ,khôngthayaccuracyBTC.
[Finalaudit]({OUT}/chunk8192-final-review.json).
'''
paths[4].write_text(qa)
accessnote=('No PBS/credit refresh at2026-10-16 01:50:59UTC: existing-access helper found no live VPN '
 'session before SSH.220575 current state/result unknown; retain1536SU reserve. Historical '
 'ledger unchanged. New authentication prohibited; no authentication/qsub.')
with (ROOT/'nscc-pbs/budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for name in ['nscc-budget.json','continuous-plan.json']:
  p=ROOT/'nscc-pbs'/name
  (OUT/(name+'.before')).write_bytes(p.read_bytes())
  d=json.loads(p.read_text());d['updated_utc']=now.isoformat()
  if name=='nscc-budget.json':
   d['reconciliation_note']=accessnote
   for j in d['jobs']:
    if j['job_id']=='220575.pbs111': j.update(scheduler_comment=accessnote,latest_attempted_check_utc=live['checked_utc'],state_fresh=False)
   d['latest_access_check'].update(checked_utc=live['checked_utc'],source=EVID+'/live-check.json')
   d['evidence'].append(EVID+'/live-check.json')
  else: d.update(latest_evidence=EVID+'/live-check.json',access_status=accessnote)
  tmp=p.with_suffix('.json.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(p)
report=f'''# Báo cáo Qwen — 16/10/2026 {stamp}

- **23906 đã hoàn tất exit0 lúc01:48:16UTC.** Finalaudit đạt:2547,85goodtokens/s,SLA98,87%,TTFT735,56ms,ITL16,32ms;0lỗi/hủy request,short7/8chỉreverseđãbiết.
- **Chunk8192 thấp hơn meanhai baseline1,7238%**;TTFT+223,294ms dùITL−0,8249ms. Rehash47file/mỗi run,full60/120/30,raw789warmup/1589profiling,payload/runtime đềuđạt. Chunkcũngđổigraphprefill;chưa chọncấuhình/accuracyBTC.
- **H200 hiện tại:**23924/23934PENDING(Resources),2/5slot;watcher sống. Cả3wave9 đãfinalaudit;tiếp tục thu haiN54 và dùngreview-n54.py,không thêmjob/repeat/N56/lịch.
- **NSCC01:50:59UTC:**không cóVPN trướcSSH;220575/kết quả/credit chưa xác minh. Giữ1536SUreserve,campaign16384SU vàgate04→05→06;khôngauth/qsub.
- Đã cập nhật CURRENT,POLICY,Q&A,matchedreview,budget/plan dướilock;giữrawartifact và bằngchứng cũ. Kết thúc sauaudit,không chờqueue.

[Bằng chứng final]({OUT}/chunk8192-final-review.json) · [Scheduler]({OUT}/final-queue.json).
'''
paths[2].write_text(report)
with (WORK/'research-autopilot/HISTORY.md').open('a') as f:f.write('\n\n'+report)
(OUT/'wake-summary.json').write_text(json.dumps(dict(finished_utc=now.isoformat(),job23906='MEASURED_PASS_SLA_LOWER_GOODPUT_THAN_BOTH_BASELINES',new_jobs_submitted=False,new_authentication_attempted=False,nscc_reserve_su=1536,independent_work_complete=True),indent=2)+'\n')
print(json.dumps(final,indent=2))
