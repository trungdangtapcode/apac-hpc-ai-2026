"""Single bounded submission, reserve locally first and preserve uncertain outcomes."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl, json, re, shlex, subprocess
root=Path(__file__).resolve().parents[3]
ev=Path(__file__).resolve().parent
budget_path=root/'nscc-pbs/nscc-budget.json'
remote_script='''import subprocess,re,sys
from pathlib import Path
root=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015')
queue=subprocess.check_output(['qstat','-u','apacsc42'],text=True)
print('OWN_QUEUE\\n'+queue,flush=True)
assert not re.search(r'^\\s*\\d+\\.pbs\\d+',queue,re.M),'Own GPU job active; refuse submission'
history=subprocess.check_output(['qstat','-x','-u','apacsc42'],text=True)
print('OWN_HISTORY\\n'+history,flush=True)
known={'220453.pbs111','220454.pbs111','220456.pbs111','220457.pbs111','220486.pbs111','220489.pbs111'}
seen=set(re.findall(r'^\\s*(\\d+\\.pbs\\d+)',history,re.M))
assert seen<=known,('Unreconciled PBS job',seen-known)
ledger=subprocess.check_output(['myprojects'],text=True)
print('CREDIT\\n'+ledger,flush=True)
m=re.search(r'\\| SU\\s*\\|\\s*([\\d.]+)\\s*\\|\\s*([\\d.]+)\\s*\\|\\s*([\\d.]+)\\s*\\|\\s*([\\d.]+)',ledger)
assert m,'Cannot parse credit'
grant,used,balance,doubt=map(float,m.groups())
assert used==539.307 and doubt==0,('Ledger changed, reconcile before submission',used,doubt)
assert used+1024<=4096 and balance-1024>=13000
bundle=root/'baseline-n32-readiness-02'
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True)
job=subprocess.check_output(['qsub',str(bundle/'benchmark.pbs')],cwd=root,text=True).strip()
assert re.fullmatch(r'\\d+\\.pbs\\d+',job),('Uncertain qsub reply',job)
print('SUBMITTED_JOB='+job,flush=True)
'''
(ev/'remote-submit-guard.py').write_text(remote_script)
with (root/'nscc-pbs/budget.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 budget=json.loads(budget_path.read_text())
 assert not budget['active_pbs_jobs'] and not budget['pending_reservations']
 used=budget['ledger']['used_su'];reserve=1024
 assert used+reserve<=budget['commissioning_cap_su']
 assert budget['ledger']['balance_su']-reserve>=budget['retain_project_su']
 stamp=datetime.now(timezone.utc).isoformat()
 reservation={'reservation_id':'baseline-n32-readiness-02-20261015T1915UTC','job_id':None,'max_charge_su':reserve,'requested_gpus':16,'requested_walltime':'00:30:00','bundle':'baseline-n32-readiness-02','retry_of':'220489.pbs111','recorded_utc':stamp,'state':'SUBMITTING_UNCERTAIN_UNTIL_RECONCILED'}
 budget['pending_reservations']=[reservation];budget['unallocated_commissioning_su']=round(4096-used-reserve,3);budget['next_baseline_reserved']=True;budget['updated_utc']=stamp
 budget['evidence'].append('inspection/wake-20261015-1915UTC/retry-preflight-jobs-credit.txt')
 def save():
  temp=budget_path.with_suffix('.json.tmp');temp.write_text(json.dumps(budget,indent=2)+'\n');temp.replace(budget_path)
 save();(ev/'budget-before-qsub.json').write_text(json.dumps(budget,indent=2)+'\n')
 r=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch',"bash -lc 'python3 -'"],input=remote_script,text=True,capture_output=True,timeout=60)
 (ev/'retry-submit.txt').write_text(r.stdout);(ev/'retry-submit.stderr').write_text(r.stderr)
 m=re.search(r'^SUBMITTED_JOB=(\d+\.pbs\d+)$',r.stdout,re.M)
 if r.returncode or not m:raise RuntimeError('Submission uncertain or rejected; retain reservation and reconcile, never blindly repeat')
 job=m.group(1);reservation.update(job_id=job,state='SUBMITTED_PENDING_SCHEDULER_CHECK')
 budget['jobs'].append({'job_id':job,'state':'SUBMITTED_PENDING_SCHEDULER_CHECK','requested_gpus':16,'requested_walltime':'00:30:00','max_charge_su':1024,'included_in_ledger_used':False,'reservation_recorded':True,'retry_of':'220489.pbs111','bundle':'baseline-n32-readiness-02','submitted_utc':datetime.now(timezone.utc).isoformat()})
 budget['active_pbs_jobs']=[job];budget['latest_access_check']={'state':'AUTHENTICATED','checked_utc':datetime.now(timezone.utc).isoformat(),'pbs_and_ledger_refreshed':True,'source':'inspection/wake-20261015-1915UTC/retry-submit.txt'}
 budget['reconciliation_note']='All six prior jobs terminal and covered by ledger539.307SU. One readiness retry reserved1024SU and submitted; keep reservation until accounting reconciles. No measured NSCC export yet.'
 budget['ledger']['source']='Live myprojects read2026-10-15 19:18UTC; inspection/wake-20261015-1915UTC/retry-submit.txt'
 budget['ledger']['balance_semantics']='Balance excludes any in-doubt prepayment shown in that snapshot; local1024SU reservation is a separate conservative cap until reconciliation.'
 budget['updated_utc']=datetime.now(timezone.utc).isoformat();save()
 print(job)
