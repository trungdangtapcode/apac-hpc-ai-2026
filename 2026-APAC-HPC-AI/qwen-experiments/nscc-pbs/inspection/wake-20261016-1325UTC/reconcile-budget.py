from pathlib import Path
import json,re,fcntl,datetime,shutil
root=Path(__file__).resolve().parents[2]
evidence=Path(__file__).resolve().parent
text=(evidence/'pbs-credit.txt').read_text()
segments=re.split(r'(?=Job Id:)',text)[1:]
records={}
for s in segments:
 job=re.match(r'Job Id: (\S+)',s)[1]
 def get(k):return re.search(r'^\s*'+re.escape(k)+r'\s*=\s*(.+)$',s,re.M)[1].strip()
 assert get('job_state')=='F' and get('Exit_status')=='0'
 h,m,sec=map(int,get('resources_used.walltime').split(':'))
 records[job]={'state':'F','exit_status':0,'observed_walltime':get('resources_used.walltime'),'estimated_charge_su_from_allocated_walltime':16*128*(h+m/60+sec/3600)}
assert set(records)=={'220720.pbs111','220721.pbs111','220722.pbs111'}
# Empty qstat own active queue was captured between UTC date and first Job Id.
prefix=text.split('Job Id:')[0]
assert '.pbs' not in prefix
used,balance,doubt=map(float,re.search(r'\| SU\s*\|\s*64000\.000\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',text).groups())
assert doubt==0
asof=re.search(r'balance as of (\S+)',text)[1]
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (root/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 path=root/'nscc-budget.json';data=json.loads(path.read_text())
 shutil.copy2(path,evidence/'nscc-budget-before.json')
 old_used=data['ledger']['used_su'];estimated=sum(r['estimated_charge_su_from_allocated_walltime'] for r in records.values())
 assert abs(used-old_used-estimated)<.01,(used-old_used,estimated)
 for job in data['jobs']:
  if job['job_id'] in records:
   job.update(records[job['job_id']],included_in_ledger_used=True,accounting_pending=False,state_fresh=True,last_checked_utc=stamp,latest_attempted_check_utc=stamp,last_confirmed_state='F')
 for reserve in data['pending_reservations']:
  if reserve.get('job_id') in records:reserve.update(state='RECONCILED_IN_LEDGER',reconciled_utc=stamp)
 data['ledger'].update(as_of=datetime.datetime.strptime(asof,'%d/%m/%Y-%H:%M:%S').replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8))).isoformat(),used_su=used,balance_su=balance,in_doubt_su=doubt,source=str(evidence/'pbs-credit.txt'),queried_utc='2026-10-16T13:25:39+00:00',freshness_note='Live SSH queue/accounting/credit refreshed13:25:39UTC; three terminal charges reconciled to ledger delta within0.001SU.')
 data.update(updated_utc=stamp,active_pbs_jobs=[],active_pbs_jobs_verified=True,uncertain_pbs_jobs=[],unallocated_commissioning_su=round(data['commissioning_cap_su']-used,3),campaign_headroom_after_reserved_su=round(data['commissioning_cap_su']-used,3),reconciliation_note='Three F/exit0, empty ALL own active queue, InDoubt0. Ledger delta3281.352SU matches16allocatedGPU*128*sumwalltime96m08s within0.001SU. No outstanding reservation or newqsub; retainproject13000SU.')
 data['latest_access_check']={'checked_utc':'2026-10-16T13:25:39+00:00','state':'EXISTING_SSH_SUCCESS','pbs_and_credit_refreshed':True,'new_vpn_authentication_attempted':False,'ssh_batch_attempted':True,'credentials_supplied':False,'qsub_attempted':False,'source':str(evidence/'pbs-credit.txt')}
 data['evidence'].append(str(evidence/'pbs-credit.txt'))
 path.write_text(json.dumps(data,indent=2)+'\n')
 report={'ledger_delta_su':used-old_used,'estimated_charge_su':estimated,'difference_su':used-old_used-estimated,'jobs':records,'used_su':used,'headroom_su':data['unallocated_commissioning_su'],'active_queue_empty':True,'new_reservation':False,'resources_used_ngpus_caveat':'PBS reports resources_used.ngpus0; charge cross-check uses requested allocated16GPUs and walltime, not that zero counter.'}
 (evidence/'budget-reconciliation.json').write_text(json.dumps(report,indent=2)+'\n')
 planpath=root/'continuous-plan.json';plan=json.loads(planpath.read_text());shutil.copy2(planpath,evidence/'continuous-plan-before.json')
 for group in ('pilots','startup_pilots'):
  for pilot in plan[group]:
   if pilot.get('job_id') in records:pilot.update(records[pilot['job_id']],last_checked_utc=stamp,state_fresh=True,result_state='TERMINAL_ARTIFACT_REVIEW_IN_PROGRESS')
 planpath.write_text(json.dumps(plan,indent=2)+'\n')
 print(json.dumps(report,indent=2))
