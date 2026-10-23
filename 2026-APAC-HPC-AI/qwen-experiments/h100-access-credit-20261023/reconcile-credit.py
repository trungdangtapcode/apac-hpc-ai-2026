"""Reconcile one uniquely explained posted AI charge under the existing lock."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re
O=Path(__file__).resolve().parent;P=O.parent/'nscc-pbs'
snapshot=json.loads((O/'access-and-accounting.json').read_text());rows=snapshot['commands']
assert all(x['returncode']==0 for x in rows)
assert rows[1]['argv']==['qselect','-u','apacsc42','-P','59010042'] and not rows[1]['stdout'].strip()
account=rows[2]['stdout'];published=rows[3]['stdout']
assert 'Job Id: 223132.pbs111' in account and re.search(r'project\s*=\s*59010042',account)
assert re.search(r'job_state\s*=\s*F\b',account) and re.search(r'Exit_status\s*=\s*0\b',account)
h,m,s=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',account).groups());seconds=h*3600+m*60+s
match=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',published)
assert match;grant,used,balance,doubt=map(float,match.groups());assert abs(grant-used-balance-doubt)<.01
stamp=datetime.now(timezone.utc).isoformat()
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);path=P/'nscc-budget.json';b=json.loads(path.read_text());assert b['project']=='59010042' and b['commissioning_cap_su']==51000 and b['retain_project_su']==13000
 unposted=[x for x in b['jobs'] if not x.get('included_in_ledger_used')]
 assert len(unposted)==1 and unposted[0]['job_id']=='223132.pbs111','Do not reconcile a changed or ambiguous ledger'
 job=unposted[0];charge=seconds*job['requested_gpus']*b['billing_su_per_gpu_hour']/3600;delta=used-b['ledger']['used_su'];assert abs(charge-delta)<.002,(charge,delta)
 job.update(included_in_ledger_used=True,accounting_pending=False,state='F',last_checked_utc=stamp,estimated_charge_su=charge,observed_walltime=f'{h:02d}:{m:02d}:{s:02d}')
 released=[]
 for row in b['pending_reservations']:
  if row.get('job_id')=='223132.pbs111' and row['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'}:
   released.append(row['max_charge_su']);row.update(state='RECONCILED_IN_LEDGER',reconciliation_source=str(O/'access-and-accounting.json'),last_checked_utc=stamp)
 outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'})
 b['ledger'].update(grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,as_of=re.search(r'balance as of (\S+)',published).group(1),queried_utc=snapshot['checked_utc'],source=str(O/'access-and-accounting.json'),freshness_note='Read-only existing authenticated AI SSH connection; selected project59010042 only. Unique22.4-SU posted native-registration charge reconciled. No new reservation or submission.'.replace('project590','project 590').replace('Unique22','Unique 22'))
 headroom=b['commissioning_cap_su']-used-outstanding
 b.update(updated_utc=stamp,active_pbs_jobs=[],active_gpu_queue_scope='qselect -u apacsc42 -P59010042; no other project queried',campaign_headroom_after_reserved_su=headroom,unallocated_commissioning_su=headroom)
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(b,indent=2)+'\n');tmp.replace(path)
 proof=dict(reconciled_utc=stamp,project='59010042',job='223132.pbs111',walltime_s=seconds,allocated_gpus=job['requested_gpus'],posted_delta_su=delta,estimated_charge_su=charge,released_max_reservations_su=released,outstanding_max_su=outstanding,internal_headroom_su=headroom,public_balance_su=balance,public_used_su=used,in_doubt_su=doubt,new_gpu_spend_or_submission=False,unchanged_cap_su=51000,unchanged_project_reserve_su=13000)
 (O/'RECONCILIATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
