#!/usr/bin/env python3
"""Apply explicit owner zero-holdback steering without inventing charge attribution."""
from pathlib import Path
import datetime,fcntl,json,re
S=Path(__file__).resolve().parent;Q=S.parent
with (Q.parent/'hpc-experiments/nscc-cpu-timing-probe-20261021/cpu-budget.lock').open('a') as cpu:
 fcntl.flock(cpu,fcntl.LOCK_EX)
 with (Q/'nscc-pbs/budget.lock').open('a') as ai:
  fcntl.flock(ai,fcntl.LOCK_EX)
  proof=json.loads((S/'terminal-and-credit.json').read_text());commands=proof['commands'];assert commands['queue']['returncode']==0 and not commands['queue']['stdout'].strip()
  bpath=Q/'nscc-pbs/nscc-budget.json';b=json.loads(bpath.read_text());assert not b.get('uncertain_pbs_jobs')
  old=json.loads((Q/'h100-access-restored-20261026/access-and-accounting.json').read_text());old_terminal={r['argv'][-1] for r in old['commands'] if r['argv'][0]=='qstat' and 'job_state = F' in r['stdout']}
  credit=commands['credit']['stdout'];m=re.search(r'\| SU\s*\|\s*([-+]?\d+(?:\.\d+)?)\s*\|\s*([-+]?\d+(?:\.\d+)?)\s*\|\s*([-+]?\d+(?:\.\d+)?)\s*\|\s*([-+]?\d+(?:\.\d+)?)',credit);assert m
  grant,used,balance,doubt=map(float,m.groups());assert grant==64000 and abs(doubt)<1e-6
  released=[];now=datetime.datetime.now(datetime.timezone.utc).isoformat()
  for row in b['pending_reservations']:
   if row['state']=='RECONCILED_IN_LEDGER':continue
   job=row['job_id'];fresh=commands[job];terminal=fresh['returncode']==0 and 'job_state = F' in fresh['stdout']
   assert terminal or job in old_terminal,(job,'No retained terminal evidence')
   released.append({'job_id':job,'historical_max_charge_su':row['max_charge_su'],'fresh_terminal':terminal,'retained_terminal_evidence':job in old_terminal})
   row.update(previous_reservation_state=row['state'],state='TERMINAL_NO_LOCAL_HOLDBACK_OWNER_POLICY',local_reservation_su=0,holdback_removed_utc=now,holdback_removal_source=str(S/'POLICY.md'),charge_attribution='Not individually certified by this policy change; historical maximum remains audit metadata.')
   for entry in b['jobs']:
    if entry['job_id']==job:
     entry.update(state='F',local_reservation_su=0,accounting_pending=not entry.get('included_in_ledger_used',False),holdback_policy='No terminal local holdback; actual fresh project balance governs spending. Individual charge attribution remains separate.')
  b['ledger'].update(as_of=credit.splitlines()[0].split('balance as of ')[1],grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=proof['checked_utc'],source=str(S/'terminal-and-credit.json'),freshness_note='Selected AI site balance after terminal225306. Owner removed discretionary and terminal local SU holdbacks; no individual charge attribution inferred.')
  b.update(updated_utc=now,commissioning_cap_su=64000,retain_project_su=0,active_pbs_jobs=[],active_pbs_jobs_verified=[],unallocated_commissioning_su=balance,campaign_headroom_after_reserved_su=balance,discretionary_buffer_su=0,terminal_local_holdback_su=0,local_reservation_policy='No discretionary buffer and no terminal job holdbacks. Preserve historical max-charge evidence. For genuinely pending/running/uncertain attempts account actual outstanding commitment once, net of site In Doubt already deducted from balance; never apply extra safety margin.',owner_no_buffer_instruction_utc=now)
  b['reconciliation_note']='Owner explicitly removed local SU holdbacks on26October. All12 formerly withheld AI jobs have retained terminal evidence; no AI job active and no uncertain submission. Full fresh site balance is available for justified work. No claim of per-job ledger reconciliation; no HPC budget change.'
  bpath.write_text(json.dumps(b,indent=2)+'\n')
  (S/'POLICY-APPLIED.json').write_text(json.dumps({'utc':now,'project':'59010042','owner_steering':'No SU buffer; use the full available H100 grant for justified research before30October.','available_site_balance_su':balance,'discretionary_buffer_su':0,'terminal_local_holdback_su':0,'released_historical_holdbacks':released,'historical_maxima_sum_su':sum(r['historical_max_charge_su'] for r in released),'individual_charge_reconciliation_claim':False,'CPU_queue_admission':'Must still be freshly checked beforeqsub; current CPU read channel is timing out.'},indent=2)+'\n')
print('No buffer/terminal holdback; actual available AI balance',balance)
