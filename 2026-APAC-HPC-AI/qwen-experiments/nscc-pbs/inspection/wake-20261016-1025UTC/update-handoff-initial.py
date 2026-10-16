from pathlib import Path
import json,datetime,fcntl,shutil
root=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments'); notes=Path('/home/apacsc42/workspace/notes'); auto=Path('/home/apacsc42/workspace/research-autopilot'); evidence=root/'nscc-pbs/inspection/wake-20261016-1025UTC'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def prepend(path,section):
 path.write_text(section+'\n\n'+path.read_text())
result='''# DP + DeepEP N54: final review, 16Oct2026 10:28 UTC

Job23934 completed exit0 at08:11:21UTC after9m17s. Fresh sacct10:25 agrees
with the terminal seal. All47sealed files rehash, frozen submitted payload and
12execution files match BOTH DP N52 controls23780/23859. Full60/120/30 and
actual phase timing pass:802warmup,1598profiling requests, zero errors/cancel.
Eight NIXL decode ranks and both P/D warmups pass. Resolved ServerArgs match
both controls except engine random_seed: TP8/DP8/EP8, attentionDP, DeepGEMM,
DeepEP low_latency, dispatcherFP8. Raw132baseline and8candidate output cases
were rescored; candidate remains7/8, only the known reverse failure.

| Point | Good tokens/s | SLA | TTFT ms | ITL ms |
|---|---:|---:|---:|---:|
|DP N52 mean23780/23859|2543.6386|see individual runs|606.7911|16.9590|
|DP N54 23934|2555.4232|98.7484%|751.9882|16.8873|
|MNNVL N54 23924|2634.0344|98.9024%|600.4446|17.1102|

DP N54 vs EACH N52:+0.2443%/+0.6833%; vs mean:+0.4633%, TTFT+145.1971ms,
ITL−0.0717ms. Versus MNNVL at the SAME N54:−2.9844%goodput,
TTFT+151.5435ms, ITL−0.2229ms. One N54 observation per package does not prove
repeatability, statistical significance or an isolated kernel effect. Engine
seed/node/time can confound. Observed199–200tokens; metric convention stays
200tokens per good request. KV auto is not independent proof of effective dtype.

Decision: close the existing bounded three-point DP branch at N54; do not open
another DP repeat or N56 on this small load gain. Prioritize the queued MNNVL
N54 confirmation and combo N52 replications/fresh control/long diagnostic.
No promotion or organiser accuracy claim. Leave the fifth slot free until a
useful next experiment meets the documented gates; queue capacity alone is not
a research hypothesis. No scheduler/payload/watcher changes in this review.

Evidence: [full N54 review](../nscc-pbs/inspection/wake-20261016-1025UTC/n54-23934-review.json),
[same-load and raw output crosscheck](../nscc-pbs/inspection/wake-20261016-1025UTC/n54-same-load-and-output-review.json),
[fresh scheduler](../nscc-pbs/inspection/wake-20261016-1025UTC/slurm_accounting.json).
'''
(root/'serving-tuning-08/DP_N54_RESULT.md').write_text(result)
prepend(root/'serving-tuning/N54_REVIEW.md','''## Current result —16Oct2026 10:28UTC

BOTH N54 jobs now have terminal independent reviews.23934 COMPLETED exit0
at08:11:21UTC:2555.4232goodt/s,SLA98.7484%,TTFT751.9882ms,ITL16.8873ms.
Fullseal/raw/protocol/runtime/short pass;47files,802warmup/1598profiling,
0errors/cancel,knownreverse only. DP vs its N52mean:+0.4633% withTTFT+145.1971ms;
vs MNNVL23924 SAME N54:−2.9844%,TTFT+151.5435ms,ITL−0.2229ms.
[Final result and limits](../serving-tuning-08/DP_N54_RESULT.md).
No extraDP repeat/N56; continue queued24009 andwave10. Earlier pending/current
statements below are dated historical snapshots, superseded by this section.''')
prepend(root/'serving-tuning-08/REPEAT_REVIEW.md','''Current update16Oct2026 10:28UTC:23934 is COMPLETED exit0 and independently
reviewed. [Final N54 result](DP_N54_RESULT.md):2555.4232goodt/s,SLA98.7484%,
+0.4633%vs DP N52mean,TTFT+145.1971ms. No extraDP repeat/N56.
Pending23934 statements below describe historical15Oct snapshots.''')
with (root/'serving-tuning-10/PLAN.md').open('a') as f:f.write('''
## Next-step decision after DP N54 —16Oct2026 10:28UTC

23934 final review passes full protocol/runtime/outputs at2555.4232goodt/s,
SLA98.7484%, but gains only0.4633%over its N52mean whileTTFT rises145.1971ms.
It is2.9844%below23924 MNNVL at the sameN54. Close the bounded DP wave here;
no extraDP repeat or blindN56. [Evidence](../serving-tuning-08/DP_N54_RESULT.md).

Fresh scheduler10:25UTC has23973/23974/23975/24009 PENDING(Resources),4/5slots;
watcher419440 remains alive. Preserve all four frozen jobs and queue positions.
Next useful step is review-wave10.py after each seal and
review-mnnvl-n54-repeat.py for24009; do not rerun unchanged waiting-path audits.
Read23975 long PASSED/FAILED/DEFERRED separately and compare both combo repeats
with fresh23974 and all controls. Only if the existing full combo gain/SLA95%/
ITL19.3/zeroerror/short/long gate passes, write a bounded comboN54 plan with
one point, unchanged execution except actual load52→54 and experiment labels,
maximum17minutes/16H200, source review and fresh ownqueue before arming via
existing watcher. This conditional plan is not a submitted job or promotion.
If gates fail or freshcontrol drift removes gain, retain negative evidence and
investigate the observed cause; do not fill a slot with arbitrary variants.
MNNVL24009 is the one planned confirmation; no third successfulrepeat/N56.
''')
with (root/'nscc-pbs/NEXT_H100_CONFIRMATION.md').open('a') as f:f.write('''
## Access and evidence update —16Oct2026 10:28UTC

At10:25 the existing helper finds no live VPN session before SSH. PBS terminal
states/ownqueue/credit for220720–220722 remain UNKNOWN, not cancelled or done.
No new auth/DUO, qsub or reservation release. Keep4608SU until fresh reconciliation.
A06:26 archive attempt exited1 because tar saw the running n38/confirm directory
change. Its102members enumerate to end; selected finishedN32/N34/N36 exports,
phase manifests and rawrequests were recovered without modifying the source.
Full60/120/30, actual timings/counts/latencies/lengths/goodrequest sums match for
those historical points; no errors/cancel. This is NOT a terminal seal or final
runtime/quality result. N38 remains excluded. Original archive/stderr retained.
Seeinspection/wake-20261016-1025UTC/h100-historical-live-point-review.json.
Resume the above conditional control/candidate pair only after all existing
terminal/quality/runtime/queue/credit gates; do not bypass missingNSCCaccess.
''')
# Preserve the old handoff before replacing current policy/report.
shutil.copy2(auto/'POLICY.md',auto/'POLICY-before-20261016-1025UTC.md')
shutil.copy2(auto/'LATEST.md',evidence/'LATEST-before-run.md')
# Mark unknown state explicitly; retain historical values and all reservations.
base=root/'nscc-pbs'
with (base/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 p=base/'nscc-budget.json';d=json.loads(p.read_text());d['updated_utc']=now
 for job in d['jobs']:
  if job['job_id'] in d['active_pbs_jobs']:
   job['last_confirmed_state']=job['state'];job['state']='UNKNOWN_ACCESS_LOST';job['state_fresh']=False;job['latest_attempted_check_utc']='2026-10-16T10:25:28Z'
 d['active_pbs_jobs_verified']=False;d['uncertain_pbs_jobs']=list(d['active_pbs_jobs'])
 d['ledger']['freshness_note']='Historical ledger asof14:00Singapore queried06:17UTC; VPN unavailable10:25UTC beforeSSH, no new credit or terminal reconciliation. Keep4608SU full reserve.'
 d['latest_access_check']={'checked_utc':'2026-10-16T10:25:28Z','state':'NO_LIVE_VPN_SESSION_BEFORE_SSH','pbs_and_credit_refreshed':False,'new_vpn_authentication_attempted':False,'ssh_batch_attempted':True,'credentials_supplied':False,'qsub_attempted':False,'source':str(evidence/'pbs_credit.json'),'last_confirmed_job_state':'Historical06:17UTC:220720R;220721H;220722H afteranychain'}
 d['reconciliation_note']='All three chain states UNKNOWN at10:25UTC. Retain4608SU conservative reserve/headroom9394.631SU; no duplicate or newqsub before fresh ownqueue/credit/terminal accounting.'
 d['evidence'].append('inspection/wake-20261016-1025UTC/pbs_credit.json');p.write_text(json.dumps(d,indent=2)+'\n')
 p=base/'continuous-plan.json';d=json.loads(p.read_text());d['updated_utc']=now
 for group in ('pilots','startup_pilots'):
  for pilot in d[group]:
   pilot['last_confirmed_state']=pilot['state'];pilot['state']='UNKNOWN_ACCESS_LOST';pilot['latest_attempted_check_utc']='2026-10-16T10:25:28Z'
 d['last_confirmed_current_job']=d['current_job'];d['current_job']=None;d['current_job_state']='UNKNOWN_ACCESS_LOST'
 d['latest_evidence']='inspection/wake-20261016-1025UTC/';d['access_status']='No live VPN session at10:25UTC; no newauthentication. Three existing job states and credit unknown; preserve reservations, no duplicate.'
 d['historical_recovered_points']={'job':'220720.pbs111','capture_utc':'2026-10-16T06:26:32Z','state':'RAW_PROTOCOL_CHECKED_NOT_TERMINAL','ns':[32,34,36],'report':'inspection/wake-20261016-1025UTC/h100-historical-live-point-review.json'}
 p.write_text(json.dumps(d,indent=2)+'\n')
