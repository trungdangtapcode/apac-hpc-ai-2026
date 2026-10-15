import datetime
import fcntl
import hashlib
import json
import re
import subprocess
from pathlib import Path

R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
N=Path('/home/apacsc42/workspace/notes')
A=Path('/home/apacsc42/workspace/research-autopilot')
O=Path(__file__).resolve().parent
utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
live=json.loads((O/'live-check.json').read_text())
checked=live['checked_utc']
assert live['nscc']['returncode']==1 and 'Expected one live VPN session' in live['nscc']['stderr']
review=json.loads((O/'runtime-review.json').read_text())
assert review['payload_hashes_verified'] and review['pair_warmup_complete_at_snapshot']
assert review['mnnvl_ranks']==review['flashinfer_decode_ranks']==review['nixl_ucx_ranks']==list(range(8))
queue=subprocess.check_output(['squeue','--noheader','--user','apacsc42','--format=%i|%T|%R'],text=True)
rows=[line.strip().split('|') for line in queue.splitlines() if line.strip()]
assert len(rows)==5
assert {r[0]:r[1] for r in rows}=={'23904':'RUNNING','23905':'PENDING','23906':'PENDING','23924':'PENDING','23934':'PENDING'}, rows
final=dict(checked_utc=utc,queue=rows,watcher=subprocess.check_output(['ps','-p',(R/'serving-tuning/watcher.pid').read_text().strip(),'-o','pid,lstart,args'],text=True))
(O/'final-queue.json').write_text(json.dumps(final,indent=2)+'\n')
evidence=str(O.relative_to(R/'nscc-pbs'))
access='No PBS/credit refresh at22:55:57UTC: helper found no live VPN session before SSH.220575 current state/result unknown; retain1536SU reserve. Historical04:00SGT ledger unchanged; no authentication/qsub.'
with (R/'nscc-pbs/budget.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    p=R/'nscc-pbs/nscc-budget.json';d=json.loads(p.read_text())
    (O/'budget-before-update.json').write_text(json.dumps(d,indent=2)+'\n')
    assert d['commissioning_cap_su']==16384
    assert sum(j['max_charge_su'] for j in d['pending_reservations'])==1536
    d.update(updated_utc=utc,reconciliation_note=access)
    d['latest_access_check'].update(checked_utc=checked,source=evidence+'/live-check.json',state='VPN_SESSION_MISSING_BEFORE_SSH',pbs_and_credit_refreshed=False,new_authentication_attempted=False,qsub_attempted=False)
    for j in d['jobs']:
        if j['job_id']=='220575.pbs111':j.update(scheduler_comment=access,latest_attempted_check_utc=checked,state_fresh=False)
    d['evidence'].append(evidence+'/live-check.json')
    p.write_text(json.dumps(d,indent=2)+'\n')
    p=R/'nscc-pbs/continuous-plan.json';d=json.loads(p.read_text())
    d.update(updated_utc=utc,access_status=access,latest_evidence=evidence+'/live-check.json')
    p.write_text(json.dumps(d,indent=2)+'\n')

p=R/'serving-tuning-09/MATCHED_REVIEW.md';s=p.read_text()
s=s.replace('All three jobs remain PENDING(Resources) at21:50:29UTC. This is CPU preparation,','Historical preflight: all three jobs were PENDING(Resources) at21:50:29UTC. This was CPU preparation,')
s+=f'''

## Runtime audit — 2026-10-15 {stamp} UTC

23904 RUNNING since22:51:04UTC on g1/g4;23905/23906/23924/23934 remain
PENDING(Resources) at{stamp}UTC. The five-job shared cap remains full and the
existing watcher is alive. This supersedes the all-pending historical snapshot.

23904 frozen and copied payload hashes, SHA256SUMS and Slurm-stored batch script
all match. Captured logs confirm all8ranks initialize MNNVL, hybrid FlashInfer
decode/FA3 prefill attention and NIXL/UCX. Both prefill instances use chunk4096;
decode graph sizes1–64 match; both P/D paths warmed successfully. Comparing
resolved ServerArgs against EACH of23778/23839 yields only the requested decode
attention change plus engine-generated random_seed differences. AIPerf's fixed
random-seed2026 is distinct from that unpinned server seed. Frozen payloads are
unchanged; this audit does not retroactively control seeds or quantify their
effect, nor does it establish deterministic output or noise bounds.

No full export or output-smoke result was available in this runtime audit;
initialization is not a measured speedup or accuracy result. Captured log
prefixes have hashes and timestamps, not final artifact seals. After terminal,
follow the checklist above and compare goodput/TTFT/ITL with both baselines.
No repeat/N56 is submitted by this audit.

Evidence: [runtime audit](../nscc-pbs/{evidence}/runtime-review.json),
[final queue](../nscc-pbs/{evidence}/final-queue.json).
'''
p.write_text(s)

p=N/'CURRENT.md';s=p.read_text()
s=re.sub(r'Cập nhật kiến thức: \*\*.*?\*\*\.',f'Cập nhật kiến thức: **15/10/2026, lượt research22:55–{stamp[:5]}UTC**.',s,count=1)
old='Kiểm tra queue mới **22:17:19UTC**: **23904–23906,23924,23934 đềuPENDING(Resources)**,\nđủcap5; watcher3514431 còn sống.'
new=f'Kiểm tra queue mới **{stamp}UTC**: **23904 RUNNING** từ22:51:04 trên g1/g4;\n**23905,23906,23924,23934 PENDING(Resources)**, đủcap5; watcher3514431 còn sống.\nSnapshot cả5PENDING22:17 là lịch sử.'
assert old in s;s=s.replace(old,new)
s=s.replace('Kiểm tra helper mới22:15:28UTC','Kiểm tra helper mới22:55:57UTC')
s=s.replace('chưa\ncó bằng chứngruntime vì cả3cònPENDING. Không sửa payload đangqueue.','chưa\ncó bằng chứngruntime tại snapshot21:51 vì cả3cònPENDING (lịch sử). Không sửa payload đangqueue.')
paragraph=f'''
Đã audit runtime23904 lúc22:56:40UTC: checksum frozen/copied payload và script
thựcSlurm đạt;8rank cùng khởi tạo MNNVL+FlashInferdecode vàNIXL/UCX,2P/Dwarmup
đạt,2prefillchunk4096,decodegraph1–64 đúng. So resolvedServerArgs với CẢ23778/23839:
chỉ khácdecode_attention_backend vàrandom_seed engine tự sinh. SeedAIPerf2026
không khóa seedengine; giữ caveat này khi đọc repeat, không tự đổi payload.
Chưa có full export/smoke tại audit nên chưa có sốđo mới hay xácnhậnaccuracy.
Logprefix được giữ/hash riêng, chưa phải finalseal. Bằngchứng:
`nscc-pbs/{evidence}/`. Tiếp: watcherthu23904 và4jobcònchờ;
không thêmrepeat/N56. NSCC04→05 vẫn cần truycập,terminal220575,baseline,queue,credit.
'''
s=s.replace('\n## Tự động hóa', '\n'+paragraph+'\n## Tự động hóa');p.write_text(s)

p=A/'POLICY.md';s=p.read_text()
s=re.sub(r'current handoff2026-10-15 \d\d:\d\dUTC',f'current handoff2026-10-15 {stamp[:5]}UTC',s,count=1)
old='Latestqueue22:17:19UTC:23904–23906,23924,23934 allPENDING(Resources),\n  cap5full; watcher3514431alive.'
assert old in s
s=s.replace(old,f'Latestqueue{stamp}UTC:23904RUNNING since22:51:04 on g1/g4;\n  23905/23906/23924/23934PENDING(Resources),cap5full;watcher3514431alive.\n  The all-pending22:17snapshot is historical;23904runtime audit confirms8ranks\n  MNNVL+FlashInferdecode/NIXL and2P/Dwarmup,not a performance/accuracy result.')
s=s.replace('At22:15:28UTC helper again found','At22:55:57UTC helper again found')
s+=f'''
## Handoff wake22:55–{stamp[:5]}UTC

- FreshH200{stamp}UTC:23904RUNNING since22:51:04,g1/g4;four other jobs
  PENDING(Resources),sharedcap5full;watcher3514431alive. No newjob/controller/schedule.
- Runtime23904 audit: frozen/copied payload andSlurmstoredscript match;
  all8ranks MNNVL+FlashInferdecode+NIXL/UCX,2P/Dwarmup,chunk4096/graph64 pass.
  ServerArgs versusBOTH23778/23839 differ onlydecodeattention andunfixedengine
  random_seed; AIPerf2026 isseparate. No newperformance/accuracy result yet.
- NSCC22:55:57UTC noexistingVPN beforeSSH;220575/result/creditunverified.
  Noauth/qsub;1536SUreserve,campaign16384SU and04→05gates unchanged.
- Evidence:nscc-pbs/{evidence}/. Logprefixeshashed,notfinalseals.
  Independent runtimeprepcomplete;endpromptly,watchercollectsfinalartifacts.
  No repeat/N56 extension; no idlewaiting orVPNauthenticationretry.
''';p.write_text(s)

p=Path('/home/apacsc42/workspace/tutorial/14-so-tay-hoi-dap.md')
with p.open('a') as f:f.write(f'''

**15/10/2026,{stamp[:5]}UTC — AIPerf seed2026 có khóa seed của SGLang không?**

Không. Seed2026 trong benchmark điều khiển phía AIPerf; nó không tự đặt
`ServerArgs.random_seed` của engine. Audit runtime23904 so với cả23778/23839
cho thấy seed engine tự sinh khác nhau ở cảprefill vàdecode. Các ServerArgs
khác chỉ thaydecode_attention_backend sangFlashInfer đúng thiết kế. Temperature0
vàpayloadhash giống nhau không đồng nghĩa đã khóa toàn bộ nguồn biến thiên.
Chưa đo riêng tác động seed, không quy mọi chênh lệch cho seed hay cho kernel.
Giữ frozenpayload, ghi caveat và xem repeat như bằng chứng thực nghiệm có giới hạn.

23904 đã khởi tạo đủ8rankMNNVL/FlashInfer/NIXL và2P/Dwarmup, nhưng snapshot này
chưa phải phép đo hoàn tất hay xácnhậnaccuracy. [Audit và bước đọc tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md).
''')

latest=f'''# Báo cáo Qwen — 2026-10-15 {stamp[:5]} UTC

- **H200 lúc {stamp} UTC:** 23904 RUNNING từ22:51:04 trên g1/g4;23905/23906/23924/23934 PENDING(Resources), đủcap5; watcher còn sống.
- **Tiến triển:** audit payload và runtime23904 đạt: scriptSlurm/checksum khớp, đủ8rankMNNVL+FlashInferdecode+NIXL/UCX, hai đườngP/Dwarmup,chunk4096 vàgraph64. So cả23778/23839 chỉ khácbackend attention vàseed engine tự sinh; đã ghi giới hạn seedAIPerf2026 không khóa seedengine. Chưa có sốđo mới/accuracyBTC.
- **NSCC lúc22:55:57 UTC:** chưa có phiênVPN trướcSSH;220575 vàcredit hiện tại chưa xác minh. Giữ1536SU dự trù vàtrần16384SU; khôngauth/qsub. Pilot04→05 chờ đủgate truycập/baseline/queue/credit.
- Đã cậpnhậtCURRENT,POLICY,Q&A,review vàplan/budget dướilock; giữrawlogprefix cùnghash. Không thêmjob/lịch/repeat/N56. Kếtthúc sau phầnviệc độclập; watcher tiếp tục thu kếtquả.

[Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md) · [Bằng chứng]({O}/).
'''
(A/'LATEST.md').write_text(latest)
with (A/'HISTORY.md').open('a') as f:f.write('\n\n'+latest.replace('# Báo cáo Qwen','## Báo cáo Qwen',1))
(O/'wake-summary.json').write_text(json.dumps(dict(updated_utc=utc,h200=rows,runtime_audit_passed=True,new_performance_result=False,new_authentication=False,qsub=False,nscc_reserve_su=1536,campaign_cap_su=16384),indent=2)+'\n')
print('Updated CURRENT,POLICY,Q&A,matched review,LATEST,HISTORY,budget/plan; no GPU submission or payload edits.')
