"""Refresh the owned GPU ledger under lock; do not reserve or submit work."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,importlib.util,json,re,shlex,subprocess
O=Path(__file__).resolve().parent;P=O.parent/'nscc-pbs';stamp=datetime.now(timezone.utc).isoformat();helper='/home/apacsc42/workspace/vpn-rootless/vpn.sh'
spec=importlib.util.spec_from_file_location('costs',O.parent/'cpu-envelope-balance-20261020/reconcile_costs.py');costs=importlib.util.module_from_spec(spec);spec.loader.exec_module(costs)
def save(p,d):tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(p)
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text())
 ids=list(dict.fromkeys(['222407.pbs111','222408.pbs111']+[j['job_id'] for j in b['jobs'] if not j.get('included_in_ledger_used')]))
 argv=[['qstat','-u','apacsc42'],['qstat','-xf']+ids,['myprojects']]
 code='import subprocess,json\nrows=[]\nfor a in '+repr(argv)+':\n r=subprocess.run(a,capture_output=True,text=True);rows.append(dict(argv=a,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))\nprint(json.dumps(rows))'
 r=subprocess.run(['bash',helper,'ssh-batch','bash -lc '+shlex.quote('python3 -c '+shlex.quote(code))],capture_output=True,text=True,timeout=90)
 (O/'terminal-accounting-commands.json').write_text(r.stdout);(O/'terminal-accounting.stderr').write_text(r.stderr);assert r.returncode==0
 rows=json.loads(r.stdout);assert all(x['returncode']==0 for x in rows);text='\n'.join(x['stdout'] for x in rows);(O/'terminal-accounting.txt').write_text(text)
 text=re.sub(r'(?<![\d.])-0\.000(?=\s*\|)','0.000',text);proof=costs.reconcile(b,text,stamp,str(O/'terminal-accounting.txt'))
 active=re.findall(r'^\s*(\d+\.pbs\d+)\s+',rows[0]['stdout'],re.M);b['active_pbs_jobs']=active
 excluded={'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'};outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in excluded)
 b.update(updated_utc=stamp,campaign_headroom_after_reserved_su=b['commissioning_cap_su']-b['ledger']['used_su']-outstanding,unallocated_commissioning_su=b['commissioning_cap_su']-b['ledger']['used_su']-outstanding)
 b['ledger'].update(queried_utc=stamp,source=str(O/'terminal-accounting.txt'),as_of=re.search(r'balance as of (\S+)',text).group(1),freshness_note='Terminal 223055 review: own GPU queue and published AI ledger only; unique posted deltas reconciled, no new reservation or HPC CPU access.')
 save(O/'terminal-reconciliation.json',dict(**proof,checked_utc=stamp,active_gpu_jobs=active,outstanding_max_su=outstanding,internal_headroom_su=b['campaign_headroom_after_reserved_su']));save(P/'nscc-budget.json',b)
 planpath=P/'continuous-plan.json';plan=json.loads(planpath.read_text())
 for p in plan['pilots']:
  if p.get('job_id')=='223055.pbs111':p.update(state='F',result_state='ALL_ROLES_READY_PD_TRANSPORT_FAILED',estimated_charge_su=734*16*128/3600)
  if p.get('job_id')=='223053.pbs111':p.update(state='F',result_state='ALL_ROLES_READY_WARMUP_LAUNCHER_FAILED',estimated_charge_su=507*16*128/3600)
 plan.update(updated_utc=stamp,next_bounded_step='Inspect initial NIXL remote disconnect and false warmup marker; no full-model retry or screen without supported repair and semantic pair receipt.');save(planpath,plan)
 print(json.dumps(dict(ledger=b['ledger'],outstanding_max_su=outstanding,headroom_su=b['campaign_headroom_after_reserved_su'],reconciled=proof['reconciled_jobs'],active_gpu_jobs=active),indent=2))
