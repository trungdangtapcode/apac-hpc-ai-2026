import json,datetime,fcntl,hashlib
from pathlib import Path
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments'); N=Path('/home/apacsc42/workspace/notes'); A=Path('/home/apacsc42/workspace/research-autopilot'); O=Path(__file__).resolve().parent
utc=datetime.datetime.now(datetime.timezone.utc).isoformat();live=json.loads((O/'live-check.json').read_text());checked=live['checked_utc'];evidence=str(O.relative_to(R/'nscc-pbs'))
access='No PBS/credit refresh at22:10:26UTC: helper reports no live VPN session before SSH.220575 current state/result unknown; retain1536SU reserve. Historical04:00SGT ledger unchanged; no authentication/qsub.'
with (R/'nscc-pbs/budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 p=R/'nscc-pbs/nscc-budget.json';d=json.loads(p.read_text());(O/'budget-before-update.json').write_text(json.dumps(d,indent=2)+'\n')
 d.update(updated_utc=utc,reconciliation_note=access)
 d['latest_access_check'].update(checked_utc=checked,source=evidence+'/live-check.json')
 for j in d['jobs']:
  if j['job_id']=='220575.pbs111':j.update(scheduler_comment=access,latest_attempted_check_utc=checked,state_fresh=False)
 d['evidence'].append(evidence+'/live-check.json')
 p.write_text(json.dumps(d,indent=2)+'\n')
 p=R/'nscc-pbs/continuous-plan.json';d=json.loads(p.read_text());d.update(updated_utc=utc,access_status=access,latest_evidence=evidence+'/live-check.json');p.write_text(json.dumps(d,indent=2)+'\n')
p=R/'serving-tuning-08/REPEAT_REVIEW.md';s=p.read_text();s+='''
At22:12:35UTC the existing watcher had submitted DP N54 **23934**, now
PENDING(Resources), alongside23904–23906/23924: sharedcap5full. Its132-response
baseline comparison was independently recomputed for both DP runs; no newly
failed cases. Collect23934 after terminal, use both23780/23859 and mean2543.64
as N52 references, retain measured latency tradeoffs. Scope ends atN54;
no automaticN56 or contest promotion. See final-live-check.json and
short-output-and-next-job.json in the same evidence directory.
''';p.write_text(s)
p=N/'CURRENT.md';s=p.read_text().replace('lượt research22:05–22:08UTC','lượt research22:10–22:14UTC')
s=s.replace('| H200,DP-attention+DeepEP,N52 | 23780 | **2549,20**, SLA98,87%, không lỗi/hủy; một lượt |','| H200,DP-attention+DeepEP,N52 | 23780 /23859 | **2549,20 /2538,08**, SLA98,87%, không lỗi/hủy; đã lặp độc lập |')
start=s.index('Gate hiện có mởN54\n**23924**');end=s.index('\nNSCC **220575.pbs111**',start)
s=s[:start]+'''Gate hiện có mởN54
**23924** (MNNVL) và **23934** (DP; watcher gửi22:12:24UTC sau repeat đạt).
Kiểm tra queue mới **22:12:35UTC**: **23904–23906,23924,23934 đềuPENDING(Resources)**,
đủcap5; watcher3514431 còn sống.23859 **COMPLETED exit0 lúc22:11:34UTC**.
Các snapshot23859RUNNING22:06 vàallPENDING21:50 là lịch sử.
[Review MNNVL](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/MNNVL_REPEAT_REVIEW.md).
DP mean2lượt **2543,64**, repeat−0,436%; hơncontrol23607 **5,98%**, thấp hơn
MNNVLmean **1,89%**. MeanTTFT606,79ms tăng259,95ms so23607; meanITL16,959ms
giảm2,566ms. Không quy kết hiệu ứng riêng cho một kernel.
''' +s[end:]
s=s.replace('helper mới22:05:24UTC','helper mới22:10:26UTC')
start=s.index('Đã audit DP-repeat23859 lúc22:06UTC:');end=s.index('\n## Tự động hóa',start)
s=s[:start]+'''Đã audit cuối DP-repeat23859 lúc22:12UTC: seals23780/23859 rehashđạt,
12file thực thi giống nhau, config chỉ khác tên/mụcđích. Full60/120/30 vàthờigian
phaseđạt;791warmup/1586measured,0lỗi/hủy;8rankNIXL/UCX và2P/Dwarmupđạt.
Short7/8, chỉreverseđãbiết; recomputeđốichiếu132responsebaselineđạt.
[Review vàbướcđọc23934](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/REPEAT_REVIEW.md)
so với cả23780/23859; gateN54đãmở23934,không tựmởN56. Snapshot22:06chưaNIXL/export
là lịch sử. AuditCPUđầu false-reject vìartifactdirtheojobđãsửa, giữattempt01;
khôngsửapayload. Bằngchứng:`nscc-pbs/inspection/wake-20261015-2210UTC/`.
''' +s[end:];p.write_text(s)
p=A/'POLICY.md';s=p.read_text().replace('current handoff2026-10-15 22:08UTC','current handoff2026-10-15 22:14UTC')
start=s.index('  at21:00:05UTC. Latest check22:06:58UTC:');end=s.index('\n- NSCC PBS helper',start)
s=s[:start]+'''  at21:00:05UTC. DP23859 COMPLETED exit0 at22:11:34UTC; repeat2538.08,
  SLA98.8651%,ITL16.9557ms,0errors/cancel; fullprotocol,seal,NIXL8ranks,
  twoP/Dwarmup andshortnonregression independently audited. DPmean2543.64,
  +5.98% vs23607,−1.89% vsMNNVLmean. Existingwatcher submittedDP N54 **23934**
  at22:12:24UTC. Latestqueue22:12:35UTC:23904–23906,23924,23934 allPENDING(Resources),
  cap5full; watcher3514431alive. Prior23859RUNNINGsnapshot is historical.
  Comparewave9 against23778 AND23839; DP N54 against23780 AND23859.
  No automaticN56 extension. Reviews:serving-tuning-07/MNNVL_REPEAT_REVIEW.md
  andserving-tuning-08/REPEAT_REVIEW.md.''' +s[end:]
s=s.replace('At22:05:24UTC helper again found','At22:10:26UTC helper again found')
s=s.replace('H20023780 attentionDP+DeepEP:2549.20,SLA98.87%,0errors/cancel.\n  MNNVL independently reproduced by23839; attentionDP confirmation pending; organiser accuracy unverified.','H20023780/23859 attentionDP+DeepEP:2549.20/2538.08,SLA98.87%,0errors/cancel.\n  MNNVL independently reproduced by23839; attentionDP reproduced by23859; organiser accuracy unverified.')
s+='''
## Handoff wake22:10–22:14UTC

- DP23859 COMPLETED exit0 at22:11:34UTC; independentfinalaudit passes,fullprotocol,
  1586measured/791warmup,0errors/cancel,8NIXLranks,2P/Dwarmup,short7/8knownreverse.
  Mean23780/23859=2543.638582goodt/s;repeat−0.4361%,+5.9839%vs23607,
  −1.8863%vsMNNVLmean. MeanTTFT+259.951ms,ITL−2.56594msvs23607.
- Watcher submitted23934 DPN54 afterexistinggate.22:12:35UTC ownqueue5PENDING
  (23904–23906/23924/23934),watcheralive. No newcontroller/schedule/duplicatejob.
- NSCC22:10:26UTC helper missingVPN beforeSSH;220575/creditcurrentunknown;
  noauth/qsub,1536SUreserve,campaign16384SU and04→05priorityunchanged.
- Evidence:nscc-pbs/inspection/wake-20261015-2210UTC/. InitialCPUaudit mistakenly
  requiredsameartifactdestination;correctedallowonlyjobpath/endpointdifferences,
  allremainingclientsettingsmatch. Retainedattempt01. No benchmarkpayloadchange.
- Next:watchercollectbothN54/wave9;do notextendN56. NSCCneedsaccess/terminal220575/
  baselineN32/ownqueue/livecredit before04. Independentworkcomplete;endpromptly.
''';p.write_text(s)
p=Path('/home/apacsc42/workspace/tutorial/14-so-tay-hoi-dap.md');s=p.read_text();s+='''

**15/10/2026,22:14UTC — Repeat DP-attention có xác nhận tăng tốc không; vì sao chưa chọn nó?**

Có:23780/23859 đạt2549,20/2538,08goodtokens/s, trungbình2543,64; chênh−0,436%.
Cảhai đủprotocol60/120/30,0lỗi/hủy vàkhôngcócaseoutputmớithấtbại. Mean hơn
RRcontrol23607 5,98%, nhưngthấphơnMNNVLmean1,89%. MeanITL giảm2,566ms còn16,959ms,
TTFT tăng259,95ms lên606,79ms socontrol: tănggoodputvàgiảmITL vẫn cóđánhđổiTTFT.
Đây làhiệuứngcủagóiDP8+DeepEP, khôngtácriêngđượcđónggópmỗikernel.

Runtime8rankNIXL/UCX vàcả2P/Dwarmupđạt; frozenpayload12filegiốngnhau,
sealsđạt. Watcherđãgửi23934(N54) theoexistinggate,hiệnchờResources22:12:35UTC;
queuedchưalàsốđo. Short7/8chỉreverseđãbiếtvẫnlàdiagnostic,khôngphảichứngnhận
accuracyBTC99%. Xemserving-tuning-08/REPEAT_REVIEW.md vàevidencewake-20261015-2210UTC.
''';p.write_text(s)
latest='''# Báo cáo Qwen — 2026-10-15 22:14 UTC

- **Repeat DP H20023859 đã COMPLETED exit0 lúc22:11:34UTC:**2538,08goodtokens/s,SLA98,87%,ITL16,956ms,0lỗi/hủy. Audit seals/protocol/8rankNIXL/2P/Dwarmup/shortnonregressionđạt.
- **Kết luận:**mean23780/23859=2543,64;repeat−0,436%,hơncontrol23607 5,98%,thấphơnMNNVLmean1,89%. MeanTTFT tăng259,95ms vàITL giảm2,566ms socontrol. Chưa xácnhậnaccuracyBTC.
- **Queue22:12:35UTC:**watcherđãgửi23934(DPN54) theoexistinggate;23904–23906,23924,23934đềuPENDING(Resources),đủcap5;watchercònsống. Khôngtạocontroller/lịch/jobtrùng;khôngmởN56.
- **NSCC22:10:26UTC:**chưacóphiênVPN;220575/creditcurrentchưaxácminh. Giữ1536SUdựtrùvàtrần16384SU;khôngauth/qsub;04→05vẫngiữưu tiênkhiđủgate.
- Đã cậpnhậtCURRENT,POLICY,Q&A,review,plan/budgetdướilock. ĐãgiữattemptCPUfalse-rejectartifactdirvàbảnsửa;payloadkhôngđổi. Phầnđộclậphoàntất,kếtthúcsớm.

[Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/REPEAT_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-2210UTC/).
'''
(A/'LATEST.md').write_text(latest)
with (A/'HISTORY.md').open('a') as f:f.write('\n\n'+latest.replace('# Báo cáo Qwen','## Báo cáo Qwen'))
(O/'wake-summary.json').write_text(json.dumps(dict(updated_utc=utc,evidence=evidence,dp_repeat_job='23859',dp_mean_good_tokens_s=2543.638581726158,next_job='23934',submitted_by='existing watcher',own_h200_pending=5,nscc_access=False,qsub_attempted=False,new_auth_attempted=False,reserved_su=1536,campaign_cap_su=16384),indent=2)+'\n')
print('Updated review,CURRENT,POLICY,Q&A,LATEST,HISTORY,plan,budget; unchanged campaign/reserve and frozen payloads.')
