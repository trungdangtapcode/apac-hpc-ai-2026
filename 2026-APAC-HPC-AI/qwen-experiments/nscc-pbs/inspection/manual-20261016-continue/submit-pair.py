from pathlib import Path
import subprocess,shlex,json,datetime,fcntl,re
ROOT=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs')
OUT=ROOT/'inspection/manual-20261016-continue'
HELP='/home/apacsc42/workspace/vpn-rootless/vpn.sh'
REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def remote(cmd):return subprocess.run(['bash',HELP,'ssh-batch','bash -lc '+shlex.quote(cmd)],capture_output=True,text=True,timeout=60)
def save(p,d):
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
with (ROOT/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 budget=json.loads((ROOT/'nscc-budget.json').read_text())
 assert not budget.get('uncertain_pbs_jobs')
 assert not budget.get('active_pbs_jobs')
 assert not any(r.get('state') not in ['RECONCILED_IN_LEDGER','CANCELLED','RELEASED'] for r in budget['pending_reservations'])
 r=remote('qstat -u apacsc42; myprojects')
 (OUT/'pre-submit-queue-credit.txt').write_text(r.stdout);(OUT/'pre-submit-queue-credit.stderr').write_text(r.stderr)
 assert r.returncode==0
 assert not re.search(r'^\s*\d+\.\S+',r.stdout,re.M),'Own queue not empty'
 m=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',r.stdout)
 assert m,'Credit parse failed'
 grant,used,balance,doubt=map(float,m.groups())
 assert doubt==0 and abs(used-budget['ledger']['used_su'])<.002,'Reconcile new charges first'
 assert used+3072<=budget['commissioning_cap_su'] and balance-3072>=budget['retain_project_su']
 budget['ledger'].update(used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(OUT/'pre-submit-queue-credit.txt'),freshness_note='Fresh SSH query immediately before matched pair reservation; unchanged terminal charges, empty own queue')
 reservations=[]
 for name in ['h100-control-07','h100-mnnvl-repeat-08']:
  reservations.append(dict(purpose=name,state='RESERVED_NOT_SUBMITTED',max_charge_su=1536,requested_gpus=16,requested_walltime='00:45:00',reserved_utc=now()))
 budget['pending_reservations'].extend(reservations)
 budget['campaign_headroom_after_reserved_su']=16384-used-3072
 budget['unallocated_commissioning_su']=budget['campaign_headroom_after_reserved_su']
 save(ROOT/'nscc-budget.json',budget)
 previous=None
 for reservation in reservations:
  name=reservation['purpose']
  dependency=' -W depend=afterany:'+previous if previous else ''
  cmd='cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub'+dependency+' benchmark.pbs'
  reservation.update(state='SUBMISSION_IN_PROGRESS',submission_command=cmd,dependency_afterany=previous)
  save(ROOT/'nscc-budget.json',budget)
  try:r=remote(cmd)
  except Exception:
   reservation['state']='SUBMISSION_UNCERTAIN';budget['uncertain_pbs_jobs'].append(name);save(ROOT/'nscc-budget.json',budget);raise
  (OUT/(name+'-submit.stdout')).write_text(r.stdout);(OUT/(name+'-submit.stderr')).write_text(r.stderr)
  ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',r.stdout,re.M)
  if r.returncode or len(ids)!=1:
   reservation['state']='SUBMISSION_UNCERTAIN';budget['uncertain_pbs_jobs'].append(name);save(ROOT/'nscc-budget.json',budget);raise RuntimeError('Submission uncertain; inspect and reconcile, no retry')
  job=ids[0];reservation.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now())
  budget['jobs'].append(dict(job_id=job,state='SUBMITTED',requested_gpus=16,requested_walltime='00:45:00',max_charge_su=1536,included_in_ledger_used=False,reservation_recorded=True,bundle=name,dependency_afterany=previous,planned_ns=[32,34,36,38,40,42],accounting_pending=True,submitted_utc=now()))
  budget['active_pbs_jobs'].append(job);budget['updated_utc']=now();save(ROOT/'nscc-budget.json',budget)
  previous=job
  print(name,job,flush=True)
 r=remote('qstat -u apacsc42; '+ '; '.join('qstat -f '+j for j in budget['active_pbs_jobs']))
 (OUT/'submitted-pair-queue.txt').write_text(r.stdout);(OUT/'submitted-pair-queue.stderr').write_text(r.stderr)
 assert r.returncode==0
 assert 'afterany:'+budget['active_pbs_jobs'][0] in re.sub(r'\n\t','',r.stdout),'Dependency verification failed'
 budget['active_pbs_jobs_verified']=True;budget['updated_utc']=now();save(ROOT/'nscc-budget.json',budget)
 print('Verified sequential dependency and own queue',flush=True)
