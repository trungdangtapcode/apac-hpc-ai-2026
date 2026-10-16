import datetime,fcntl,hashlib,json,re,subprocess
from pathlib import Path
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');N=Path('/home/apacsc42/workspace/notes');A=Path('/home/apacsc42/workspace/research-autopilot');O=Path(__file__).resolve().parent
utc=datetime.datetime.now(datetime.timezone.utc).isoformat();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
review=json.loads((O/'wave9-final-review.json').read_text());live=json.loads((O/'live-check.json').read_text())
assert review['full_protocol_equal'] and not review['accuracy_verified']
assert live['nscc']['returncode']==1 and 'Expected one live VPN session' in live['nscc']['stderr']
queue=subprocess.check_output(['squeue','--noheader','--user','apacsc42','--format=%A|%T|%R'],text=True)
rows=[l.split('|') for l in queue.splitlines() if l.strip()]
assert {r[0]:r[1] for r in rows}=={'23906':'PENDING','23924':'PENDING','23934':'PENDING'},rows
watcher=subprocess.check_output(['ps','-p',(R/'serving-tuning/watcher.pid').read_text().strip(),'-o','pid,lstart,args'],text=True)
(O/'final-queue.json').write_text(json.dumps(dict(checked_utc=utc,queue=rows,watcher=watcher),indent=2)+'\n')
evidence=str(O.relative_to(R/'nscc-pbs'))
# Preserve previous handoff, including appended failed cron attempts, before replacing LATEST.
for p in [N/'CURRENT.md',A/'POLICY.md',A/'LATEST.md',R/'serving-tuning-09/MATCHED_REVIEW.md']:(O/(p.name+'.before')).write_bytes(p.read_bytes())
access='No PBS/credit refresh at2026-10-16 00:15:52UTC: helper found no live VPN session before SSH.220575 current state/result unknown; retain1536SU reserve. Historical04:00SGT16Oct ledger unchanged; no authentication/qsub.'
with (R/'nscc-pbs/budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 p=R/'nscc-pbs/nscc-budget.json';d=json.loads(p.read_text());(O/'budget-before-update.json').write_text(json.dumps(d,indent=2)+'\n')
 assert d['commissioning_cap_su']==16384 and sum(j['max_charge_su'] for j in d['pending_reservations'])==1536
 d.update(updated_utc=utc,reconciliation_note=access)
 d['latest_access_check'].update(checked_utc=live['checked_utc'],source=evidence+'/live-check.json',state='VPN_SESSION_MISSING_BEFORE_SSH',pbs_and_credit_refreshed=False,new_authentication_attempted=False,qsub_attempted=False)
 for j in d['jobs']:
  if j['job_id']=='220575.pbs111':j.update(scheduler_comment=access,latest_attempted_check_utc=live['checked_utc'],state_fresh=False)
 d['evidence'].append(evidence+'/live-check.json');p.write_text(json.dumps(d,indent=2)+'\n')
 p=R/'nscc-pbs/continuous-plan.json';d=json.loads(p.read_text());d.update(updated_utc=utc,access_status=access,latest_evidence=evidence+'/live-check.json');p.write_text(json.dumps(d,indent=2)+'\n')

p=R/'serving-tuning-09/MATCHED_REVIEW.md';s=p.read_text()
s=s.replace('| 23904 | add FlashInfer decode attention | pending | pending | pending | pending |','| 23904 | add FlashInfer decode attention | 2631.0854 | 99.0220% | 635.2331 | 16.2334 |')
s=s.replace('| 23905 | prefill chunk2048 | pending | pending | pending | pending |','| 23905 | prefill chunk2048 | 2331.3530 | 98.7697% | 1188.7699 | 15.8064 |')
s=s.replace('## Runtime audit — 2026-10-15 22:57:45 UTC','## Historical runtime audit — 2026-10-15 22:57:45 UTC')
s=s.replace('Shared H200 cap5 remains full;23924N54 is the existing wave7 continuation and','At the historical preflight, shared H200 cap5 was full;23924N54 is the existing wave7 continuation and')
s+=f'''

## Terminal review — 2026-10-16 {stamp} UTC

23904 completed exit0 at23:01:10UTC15Oct;23905 completed exit0 at00:05:14UTC16Oct.
At{stamp}UTC,23906/23924/23934 are PENDING(Resources), three of five allowed slots;
watcher3514431 remains alive. These final results supersede the earlier pending
and initialization-only descriptions for23904/23905.

Both candidate seals and BOTH baseline seals rehash successfully (47files each).
Frozen/copied payloads and earlier Slurm-stored scripts match;11common operational
files match each baseline, worker changes exactly the named CLI factor. Full
60/120/30 protocol and normalized client configuration match; actual phases:
23904 warmup63.205s/821requests, measured123.143s/1636requests;
23905 warmup63.832s/734requests, measured123.962s/1463requests. Zero request errors
and cancellations, both P/D paths warm, all8ranks initializeMNNVL andNIXL/UCX.
23904 also confirms all8FlashInfer decode ranks. Both short suites remain7/8,
only the independently documented reverse failure, with no newly failed case.
This remains research evidence; organiser accuracy has not been verified.

| Candidate | Gain vs23778 | Gain vs23839 | Gain vs mean | TTFT delta vs mean | ITL delta vs mean |
|---|---:|---:|---:|---:|---:|
| 23904 FlashInfer+MNNVL | +1.5016% | +1.4718% | +1.4867% | +122.9668ms | −0.9075ms |
| 23905 chunk2048+MNNVL | −10.0615% | −10.0879% | −10.0747% | +676.5036ms | −1.3345ms |

FlashInfer+MNNVL is a provisional single-run improvement, with a TTFT cost;
no repeat or promotion is performed here. Chunk2048 is a complete passing-SLA
measurement with lower goodput, not an incomplete or failed deployment. Lower
meanITL alone does not imply faster closed-loop serving when TTFT rises.

Runtime correction: the single chunk CLI factor also changes the resolved
prefill breakable CUDA graph max_bs4096→2048 and truncates capture sizes in
BOTH prefill instances. Other nested graph fields and decode graphs match.
Do not attribute the result solely to chunk scheduling or claim graph settings
were identical. The previously extracted image source server_args.py4723–4752
sets the default prefill graph maximum from chunked_prefill_size; current H200
ServerArgs independently establish the actual change. For pending23906, inspect
whether chunk8192 also resolves to graph8192; this is an expectation, not runtime
validation. The engine random_seed remains unpinned across allocations.

Raw output lengths:23904 spans199–201tokens (mean199.99878),23905 spans199–200
(mean199.99932); both baseline extrema are199–201. Raw profiling counts and token
sums/min/max match exports. Fixed200-token goodput uses the existing benchmark
convention, not a claim that every observed response has exactly200tokens.
Attempt01's overly strict max200 assertion was corrected; attempt02 exposed the
derived graph change. Both scripts and corrections remain preserved.

Next: collect23906 and the twoN54 jobs through the existing watcher; use the
same final-evidence checks and both matched baselines. No newrepeat/N56/job,
controller or schedule is introduced. NSCC04→05 still requires restored existing
access, terminal220575, passingN32 and fresh ownqueue/credit/budget checks.

Evidence: [final independent audit](../nscc-pbs/{evidence}/wave9-final-review.json),
[source excerpt and provenance](../nscc-pbs/{evidence}/prefill-graph-source.json),
[latest own queue](../nscc-pbs/{evidence}/final-queue.json).
''';p.write_text(s)

p=N/'CURRENT.md';s=p.read_text();s=re.sub(r'Cập nhật kiến thức: \*\*.*?\*\*\.',f'Cập nhật kiến thức: **16/10/2026, lượt research00:15–{stamp[:5]}UTC**.',s,count=1)
s=s.replace('| NSCC16H100,N32 | 220562.pbs111 |','| H200,MNNVL+FlashInfer,N52 | 23904 | **2631,09**, SLA99,02%, ITL16,23ms; một lượt |\n| H200,MNNVL+chunk2048,N52 | 23905 | **2331,35**, SLA98,77%, ITL15,81ms; một lượt |\n| NSCC16H100,N32 | 220562.pbs111 |')
old='Kiểm tra queue mới **22:57:45UTC**: **23904 RUNNING** từ22:51:04 trên g1/g4;\n**23905,23906,23924,23934 PENDING(Resources)**, đủcap5; watcher3514431 còn sống.\nSnapshot cả5PENDING22:17 là lịch sử.'
new=f'Kiểm tra queue mới **16/10 {stamp}UTC**: **23906/23924/23934 PENDING(Resources)**,\n3/5slot; watcher3514431 còn sống. **23904 COMPLETED exit0 lúc15/10 23:01:10UTC;\n23905 COMPLETED exit0 lúc16/10 00:05:14UTC**, finalaudit đạt. Snapshot23904RUNNING\n22:57 vàcả5PENDING22:17 là lịch sử.'
assert old in s;s=s.replace(old,new)
s=s.replace('Kiểm tra helper mới22:55:57UTC','Kiểm tra helper mới16/10 00:15:52UTC')
s=s.replace('Tiếp: watcher thu hai nhánhN54 (23924/23934) vàwave9;','Tiếp: watcher thu hai nhánhN54 (23924/23934) vàwave9 còn23906;')
s=s.replace('Chưa có full export/smoke tại audit nên chưa có sốđo mới hay xácnhậnaccuracy.','Tại snapshot22:56 chưa có full export/smoke; đây là audit lịch sử, đã được\nthay bằng finalaudit16/10 bên dưới. AccuracyBTC vẫn chưa xácnhận.')
s=s.replace('`nscc-pbs/inspection/wake-20261015-2255UTC/`. Tiếp: watcherthu23904 và4jobcònchờ;','`nscc-pbs/inspection/wake-20261015-2255UTC/`. Bước chờ23904 tại mốcđó đã hoàn tất;')
paragraph=f'''
Đã finalaudit23904/23905 lúc16/10 {stamp}UTC, so với CẢ23778/23839:
seals47file/mỗi run vàpayloadđạt,full60/120/30 vàrawphaseđạt;0lỗi/hủy,
8rankMNNVL/NIXL và2P/Dwarmup,short7/8chỉreverseđãbiết.23904đạt2631,0854goodt/s,
SLA99,0220%,TTFT635,2331ms,ITL16,2334ms; hơnmeanMNNVL **1,4867%**,TTFT+122,9668ms,
ITL−0,9075ms. Đây là một lượt cải thiện tạmthời, chưarepeat/chọncấuhình.
23905đạt2331,3530,SLA98,7697%,TTFT1188,7699ms,ITL15,8064ms; thấp hơnmean
**10,0747%**,TTFT+676,5036ms dùITL−1,3345ms. ĐủSLA nhưnggoodputkém,khôngphảijoblỗi.

Đínhchínhgiớihạn“mộtfactor”: CLIchunk2048 đồngthời làm resolvedprefillbreakable
CUDAgraphmax_bs4096→2048 vàrútgọndanh sáchcapture ởcảhaiworker; khôngđượcquy
kết riêngchunk scheduling haynóigraph giữnguyên. Decodegraphkhôngđổi.
23906cònchờ: khi chạyphảikiểmtrachunk8192 vàgraphthực,khôngtựsuyruntime.
Outputobserved23904:199–201,23905:199–200tokens; rawcount/sum/min/maxkhớp,
goodput vẫnquyước200tokens nhưbaseline,khôngkhẳngđịnhmọiresponseđúng200.
Giữattempt01CPUfalse-rejectmax200 vàattempt02 phát hiệngraph; khôngsửapayload.
[Review hiện hành](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md).
Bằngchứng:`nscc-pbs/{evidence}/`. Khôngthêmrepeat/N56;NSCCvẫnthiếuVPN,
giữ1536SUreservevàgate04→05. Các snapshottrướcđó làlịchsử.
'''
s=s.replace('\n## Tự động hóa','\n'+paragraph+'\n## Tự động hóa');p.write_text(s)

p=A/'POLICY.md';s=p.read_text();s=re.sub(r'current handoff2026-10-15 \d\d:\d\dUTC',f'current handoff2026-10-16 {stamp[:5]}UTC',s,count=1)
a=s.index('Latestqueue22:57:45UTC:');b=s.index('Prior23859RUNNINGsnapshot is historical.',a)+len('Prior23859RUNNINGsnapshot is historical.')
s=s[:a]+f'''Latestqueue16Oct{stamp}UTC:23906/23924/23934 PENDING(Resources),
  threeofcap5;watcher3514431alive.23904 COMPLETED exit0 at15Oct23:01:10UTC;
  23905 COMPLETED exit0 at16Oct00:05:14UTC. FinalauditsPASS:2631.0854/2331.3530
  goodt/s,SLA99.0220/98.7697%,0errors/cancel,fullprotocol,short7/8knownreverse.
  VersusMNNVLmean:+1.4867%/−10.0747%;23904single-runprovisional,noauto-repeat.
  Chunk2048alsochangesresolvedprefillgraphmax_bs4096→2048/captures;notisolated
  scheduling. Seeupdatedserving-tuning-09/MATCHED_REVIEW.md. Earlierpending/
  runtime-onlysnapshots and23859RUNNINGsnapshot arehistorical.''' + s[b:]
s=s.replace('At22:55:57UTC helper again found', 'At16Oct00:15:52UTC helper again found')
s+=f'''
## Handoff wake16Oct00:15–{stamp[:5]}UTC

- LiveH200{stamp}UTC:23906/23924/23934 PENDING(Resources),3/5slots;watcheralive.
  23904/23905 terminalexit0 and independentlyfinalaudited versusBOTH23778/23839.
- FlashInfer+MNNVL2631.0854goodt/s,+1.4867%vsmean,TTFT+122.9668ms,ITL−0.9075ms;
  single-runprovisional.Chunk2048:2331.3530,−10.0747%,TTFT+676.5036ms,ITL−1.3345ms.
  Fullprotocol,0errors/cancel,short7/8nonewfails;accuracyunverified.
- Newruntimefinding:chunk2048alsoresolvesprefillbreakablegraphmax_bs2048instead4096;
  graphcaptureschange;decodesame. Audit23906resolvedgraphwhenitruns. CLIonefactor
  doesnotisolateeveryderivedruntimeeffect. Rawoutputlengths199–201/199–200preserved;
  fixed200goodputisbenchmarkconvention. BothCPUauditattemptsandcorrectionsretained.
- NSCC00:15:52UTC noexistingVPNbeforeSSH;220575/results/creditunverified;
  noauth/qsub,1536SUreserve,campaign16384SU,04→05gatesunchanged.
- Evidence:nscc-pbs/{evidence}/.UpdatedCURRENT,Q&A,matchedreview,budget/planunderlock.
  Nojob/repeat/N56/controller/scheduleadded. Existingwatchercollectsthreependingjobs;
  finishpromptlyafterindependentwork,withoutidlewaiting.
''';p.write_text(s)

p=Path('/home/apacsc42/workspace/tutorial/14-so-tay-hoi-dap.md')
with p.open('a') as f:f.write(f'''

**16/10/2026,{stamp[:5]}UTC — ITL thấp hơn có chắc goodput cao hơn; một CLI factor có cô lập mọi hiệu ứng không?**

Không. 23905 giảm prefillchunk4096→2048: ITL giảm1,3345ms so meanMNNVL,
nhưngTTFT tăng676,5036ms vàgoodputgiảm10,0747% xuống2331,35goodtokens/s.
CảSLA98,77%vàprotocolđềuđạt,khônglỗihủy:đây làphépđo hoànchỉnh chothấyđánhđổi
ởclosed-loopN52. ITL chỉđophầnpháttoken,khôngđạidiệnthờigianchờtokenđầu.
Khôngquymọichênhlệchchomộtkernelhaylậpcôngthứcnhânquảtừmeanlatency.

Dùworkerchỉđổi1flagchunk,ServerArgscả2prefillcũngđổibreakableCUDAgraphmax_bs
4096→2048vàrútgọncapture sizes. Sourcetríchimagecũngđặtdefaultgraphmaximum
theochunk. Phảighiđầyđủhiệuứngruntime,khôngnóigraphgiữnguyên;decodegraphvẫngiống.
Với23906chunk8192cònPENDINGở{stamp}UTC,phảichờlogthựcđểxácminhgraph.

23904MNNVL+FlashInferđạt2631,09goodtokens/s,hơnmeanMNNVL1,4867%;TTFTtăng122,97ms
vàITLgiảm0,9075ms. Mộtlượtđotốthơnchưachứngminhlợithếlặplại;chưachọncấuhình,
short7/8chỉkhôngcólỗimới,khôngthayaccuracyBTC. Outputobserved199–201/199–200token
khôngphảimọiresponseđúng200;giữquyướcgoodput200tokensđồngnhấtvớibaseline.
[Finalaudit vàso cả2baseline](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md).
''')

latest=f'''# Báo cáo Qwen — 2026-10-16 {stamp[:5]} UTC

- **Kết quả mới đã đối soát:** 23904 (MNNVL+FlashInfer) đạt **2631,09goodtokens/s**, SLA99,02%; hơn trung bình hai baseline **1,49%**, TTFT+122,97ms, ITL−0,91ms. Một lượt, chưa xác nhận bằngrepeat.
- 23905 (chunk2048) đạt **2331,35**, SLA98,77%; goodput giảm **10,07%** dùITLgiảm1,33ms,TTFTtăng676,50ms. Runtimecũngđổigiớihạngraphprefill4096→2048; khôngquykếtriêngchunk. Cảhaiđủprotocol60/120/30,0lỗi/hủy,short7/8chỉreverseđãbiết;accuracyBTCchưaxácnhận.
- **H200 lúc{stamp}UTC:**23906/23924/23934 PENDING(Resources),3/5slot;watchercònsống. Khôngthêmjob/repeat/N56.
- **NSCC lúc00:15:52UTC:**khôngcóphiênVPNsống;220575/kếtquả/creditchưaxácminh. Giữ1536SUdựtrù,trần16384SU;khôngauth/qsub.Pilot04→05vẫnchờgate.
- ĐãcậpnhậtCURRENT,POLICY,Q&A,review,budget/plan;giữrawartifact,kiểmhash47file/mỗirun,cả2baselinevà2candidate.CácattemptCPUvàđínhchínhđượcgiữ.Kếtthúcsauphầnviệcđộclập;watchertiếptụcthu3job.

[Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md) · [Bằng chứng]({O}/).
'''
(A/'LATEST.md').write_text(latest)
with (A/'HISTORY.md').open('a') as f:f.write('\n\n'+latest.replace('# Báo cáo Qwen','## Báo cáo Qwen',1))
(O/'wake-summary.json').write_text(json.dumps(dict(updated_utc=utc,h200=rows,final_audit_passed=True,new_performance_results=['23904','23905'],new_authentication=False,qsub=False,new_jobs=False,nscc_reserve_su=1536,campaign_cap_su=16384),indent=2)+'\n')
print('Updated CURRENT,POLICY,Q&A,review,LATEST,HISTORY and budget/plan under lock. No job or payload changes.')
