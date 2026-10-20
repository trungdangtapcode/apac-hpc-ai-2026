"""Release terminal reservations only when their walltime charges reconcile published Used."""
from pathlib import Path
import datetime,fcntl,json,re
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';raw=(O/'pbs-status.txt').read_text();jobs=['222048.pbs111','222049.pbs111','222050.pbs111']
blocks={m.group(1):m.group(2) for m in re.finditer(r'Job Id: (\d+\.pbs\d+)\n(.*?)(?=Job Id: |Project\s*:|\Z)',raw,re.S)}
m=re.search(r'\|\s*SU\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|',raw);assert m;grant,used,balance,doubt=map(float,m.groups());assert abs(grant-used-balance-doubt)<.01
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);path=P/'nscc-budget.json';b=json.loads(path.read_text());assert not b['uncertain_pbs_jobs'];before=json.loads(json.dumps(b));charges={};walls={}
 for job in jobs:
  row=next(x for x in b['jobs'] if x['job_id']==job);block=blocks[job];assert re.search(r'job_state\s*=\s*F\b',block) and re.search(r'Exit_status\s*=\s*0\b',block)
  wall=re.search(r'resources_used.walltime\s*=\s*(\S+)',block).group(1);h,m,s=map(int,wall.split(':'));charge=row['requested_gpus']*128*(h+m/60+s/3600);walls[job]=wall
  if not row.get('included_in_ledger_used'):charges[job]=charge
 delta=used-b['ledger']['used_su'];assert abs(delta-sum(charges.values()))<.01,('Unexplained ledger delta',delta,charges)
 for job in jobs:
  row=next(x for x in b['jobs'] if x['job_id']==job);row.update(state='F',exit_status=0,observed_walltime=walls[job],included_in_ledger_used=True,accounting_pending=False,last_checked_utc=now)
  if job in charges:row['estimated_charge_su_from_allocated_walltime']=charges[job]
  for q in b['pending_reservations']:
   if q.get('job_id')==job:q.update(state='RECONCILED_IN_LEDGER',last_checked_utc=now,reconciliation_source=str(O/'pbs-status.txt'))
 reserve=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'})
 b['ledger'].update(as_of=re.search(r'balance as of (\S+)',raw).group(1),grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,source=str(O/'pbs-status.txt'),queried_utc=now,freshness_note='Three completed observer/polling model walltime charges reconcile the published delta; all corresponding reservations released.')
 b.update(updated_utc=now,active_pbs_jobs=[],unallocated_commissioning_su=b['commissioning_cap_su']-used-reserve,campaign_headroom_after_reserved_su=b['commissioning_cap_su']-used-reserve)
 (O/'budget-before.json').write_text(json.dumps(before,indent=2)+'\n');t=path.with_suffix('.tmp');t.write_text(json.dumps(b,indent=2)+'\n');t.replace(path)
result=dict(checked_utc=now,charges_su=charges,walltimes=walls,published_delta_su=delta,outstanding_max_reserve_su=reserve,internal_headroom_su=b['campaign_headroom_after_reserved_su']);(O/'reconciliation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
