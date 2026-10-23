"""Reconcile the single terminal full-span probe only against a fresh AI ledger."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,fcntl,json,re,shlex,subprocess
O=Path(__file__).resolve().parent;P=O.parent/'nscc-pbs'
parser=argparse.ArgumentParser();parser.add_argument('--control-socket',required=True);a=parser.parse_args()
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);path=P/'nscc-budget.json';b=json.loads(path.read_text());assert b['project']=='59010042'
 code='''import subprocess,json
q=subprocess.run(['qselect','-u','apacsc42','-P','59010042'],capture_output=True,text=True,check=True)
r=subprocess.run(['myprojects'],capture_output=True,text=True,check=True)
lines=[];selected=False
for line in r.stdout.splitlines():
 if 'Project 59010042 balance as of' in line:selected=True
 elif selected and ('Usage breakdown' in line or (line.startswith('Project ') and '59010042' not in line)):selected=False
 if selected:lines.append(line)
print(json.dumps({'queue_ids':q.stdout.split(),'credit':'\\n'.join(lines)}))
'''
 command=['ssh','-F','/dev/null','-S',a.control_socket,'-o','ControlMaster=no','-o','BatchMode=yes','apacsc42@aspire2p.nscc.sg','bash -lc '+shlex.quote('python3 -c '+shlex.quote(code))]
 result=subprocess.run(command,capture_output=True,text=True,timeout=30);assert result.returncode==0,result.stderr
 snapshot=json.loads(result.stdout);snapshot['checked_utc']=datetime.now(timezone.utc).isoformat();(O/'fresh-selected-credit.json').write_text(json.dumps(snapshot,indent=2)+'\n')
 text=re.sub(r'(?<![\d.])-0\.000(?=\s*\|)','0.000',snapshot['credit']);m=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',text);assert m
 grant,used,balance,doubt=map(float,m.groups());assert abs(grant-used-balance-doubt)<.01
 unposted=[x for x in b['jobs'] if not x.get('included_in_ledger_used')];assert len(unposted)==1 and unposted[0]['job_id']=='224157.pbs111'
 j=unposted[0];cost=json.loads((O/'REVIEW.json').read_text())['cost'];delta=used-b['ledger']['used_su'];posted=abs(delta-cost['estimated_allocated_charge_su'])<.002
 assert posted or abs(delta)<.001,'Unexpected posted charge; retain reserve and inspect'
 j.update(state='F',exit_status=0,observed_walltime='00:08:00',estimated_charge_su=cost['estimated_allocated_charge_su'],last_checked_utc=snapshot['checked_utc'])
 if posted:
  j.update(included_in_ledger_used=True,accounting_pending=False)
  for row in b['pending_reservations']:
   if row.get('job_id')=='224157.pbs111':row.update(state='RECONCILED_IN_LEDGER',reconciliation_source=str(O/'fresh-selected-credit.json'),last_checked_utc=snapshot['checked_utc'])
 excluded={'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'};outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in excluded)
 headroom=b['commissioning_cap_su']-used-outstanding;b.update(updated_utc=snapshot['checked_utc'],active_pbs_jobs=snapshot['queue_ids'],campaign_headroom_after_reserved_su=headroom,unallocated_commissioning_su=headroom)
 b['ledger'].update(used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=snapshot['checked_utc'],source=str(O/'fresh-selected-credit.json'),as_of=re.search(r'balance as of (\S+)',text).group(1),freshness_note='Selected AI project only; terminal full-span probe charge assessed separately from passing byte gates and failed PBS exit.')
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(b,indent=2)+'\n');tmp.replace(path)
 proof=dict(job='224157.pbs111',checked_utc=snapshot['checked_utc'],posted=posted,published_delta_su=delta,estimated_allocated_charge_su=cost['estimated_allocated_charge_su'],outstanding_max_su=outstanding,internal_headroom_su=headroom,public_used_su=used,public_balance_su=balance,in_doubt_su=doubt,active_selected_ai_jobs=snapshot['queue_ids'],new_submission_or_budget_increase=False)
 (O/'RECONCILIATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
