"""Reconcile the three completed allocations against the published ledger."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';path=P/'nscc-budget.json'
raw=(O/'pbs-status.txt').read_text();jobs=['221923.pbs111','221924.pbs111','221966.pbs111']
blocks={m.group(1):m.group(2) for m in re.finditer(r'Job Id: (\d+\.pbs\d+)\n(.*?)(?=Job Id: |Project\s*:|\Z)',raw,re.S)}
m=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',raw);assert m
grant,used,balance,doubt=map(float,m.groups());assert abs(grant-used-balance-doubt)<.01
charges={};walls={}
for j in jobs:
 block=blocks[j];assert re.search(r'job_state\s*=\s*F\b',block) and re.search(r'Exit_status\s*=\s*0\b',block)
 walls[j]=re.search(r'resources_used.walltime\s*=\s*(\S+)',block).group(1);h,m,s=map(int,walls[j].split(':'));charges[j]=16*128*(h+m/60+s/3600)
now=datetime.now(timezone.utc).isoformat()
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads(path.read_text());assert not b.get('uncertain_pbs_jobs')
 if not (O/'budget-before.json').exists():(O/'budget-before.json').write_text(json.dumps(b,indent=2)+'\n')
 unrec=[j for j in jobs if not next(x for x in b['jobs'] if x['job_id']==j).get('included_in_ledger_used')]
 delta=used-b['ledger']['used_su'];assert abs(delta-sum(charges[j] for j in unrec))<.01,('Unexpected ledger delta',delta)
 for j in jobs:
  item=next(x for x in b['jobs'] if x['job_id']==j);item.update(state='F',exit_status=0,observed_walltime=walls[j],estimated_charge_su=charges[j],included_in_ledger_used=True,accounting_pending=False,last_checked_utc=now)
  for item in b['pending_reservations']:
   if item.get('job_id')==j:item.update(state='RECONCILED_IN_LEDGER',last_checked_utc=now,reconciliation_source=str(O/'pbs-status.txt'))
 outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'})
 b['ledger'].update(as_of=re.search(r'balance as of (\S+)',raw).group(1),grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now,source=str(O/'pbs-status.txt'),freshness_note='Three terminal charges match published Used; reservations reconciled without double deduction of prepayment.')
 b.update(updated_utc=now,active_pbs_jobs=[],campaign_headroom_after_reserved_su=b['commissioning_cap_su']-used-outstanding,unallocated_commissioning_su=b['commissioning_cap_su']-used-outstanding)
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(b,indent=2)+'\n');tmp.replace(path)
result=dict(charges_su=charges,walltimes=walls,observed_delta_su=delta,balance_su=balance,outstanding_reserve_su=outstanding,headroom_su=b['campaign_headroom_after_reserved_su'],checked_utc=now)
(O/'reconciliation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
