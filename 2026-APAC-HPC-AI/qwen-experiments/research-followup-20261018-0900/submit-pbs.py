"""Reconcile two finished jobs, reserve and submit three controlled PBS trials."""
from pathlib import Path
import subprocess,shlex,json,re,fcntl,datetime
R=Path.cwd();P=R/'nscc-pbs';O=R/'research-followup-20261018-0900';H='/home/apacsc42/workspace/vpn-rootless/vpn.sh';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
names=['h100-hpc-repeat-25','h100-hpc-control-26','h100-hpc-n52-27']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def remote(cmd,stdin=None):return subprocess.run(['bash',H,'ssh-batch','bash -lc '+shlex.quote(cmd)],stdin=stdin,capture_output=True,timeout=60)
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
with (O/'next-pbs.tar.gz').open('rb') as f:r=remote('cd '+REMOTE+' && tar -xzf - && for name in '+' '.join(names)+'; do (cd "$name" && sha256sum --check SHA256SUMS) || exit; done',f)
(O/'pbs-upload.txt').write_bytes(r.stdout);(O/'pbs-upload.stderr').write_bytes(r.stderr);assert r.returncode==0
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b.get('uncertain_pbs_jobs')
 r=remote('qstat -u apacsc42; qstat -xf 221262.pbs111 221263.pbs111; myprojects');(O/'pbs-pre-submit.txt').write_bytes(r.stdout);(O/'pbs-pre-submit.stderr').write_bytes(r.stderr);assert r.returncode==0;s=r.stdout.decode()
 blocks={m.group(1):m.group(2) for m in re.finditer(r'Job Id: (\d+\.pbs\d+)\n(.*?)(?=Job Id: |Project\s*:|\Z)',s,re.S)}
 terminal=[]
 for job,wall in [('221262.pbs111','00:13:56'),('221263.pbs111','00:13:10')]:
  block=blocks[job];assert re.search(r'job_state\s*=\s*F',block) and re.search(r'Exit_status\s*=\s*0\s',block);assert 'resources_used.walltime = '+wall in block
  h,mn,sec=map(int,wall.split(':'));terminal.append((job,wall,128*16*(h+mn/60+sec/3600)))
 active={m.group(1) for m in re.finditer(r'^\s*(\d+\.pbs\d+)\s+',s,re.M)};assert not active,active
 mm=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',s);assert mm;grant,used,balance,doubt=map(float,mm.groups());assert abs(grant-used-balance-doubt)<.01
 assert abs((used-b['ledger']['used_su'])-sum(x[2] for x in terminal))<.01,('Unreconciled ledger',used)
 for job,wall,charge in terminal:
  for x in b['jobs']:
   if x['job_id']==job:x.update(state='F',exit_status=0,observed_walltime=wall,estimated_charge_su_from_allocated_walltime=charge,included_in_ledger_used=True,accounting_pending=False,last_checked_utc=now())
  for x in b['pending_reservations']:
   if x.get('job_id')==job:x.update(state='RECONCILED_IN_LEDGER',reconciled_utc=now())
 outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in ['RECONCILED_IN_LEDGER','CANCELLED','RELEASED']);assert outstanding==0
 assert used+4608<=b['commissioning_cap_su'];assert grant-used-4608>=b['retain_project_su']
 b['ledger'].update(grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'pbs-pre-submit.txt'),as_of=re.search(r'balance as of (\S+)',s).group(1),freshness_note='Both prior terminal charges reconciled against Used. No residual ledger lag reservation.');b['active_pbs_jobs']=[]
 reservations=[]
 for name in names:
  z=dict(purpose=name,state='RESERVED_NOT_SUBMITTED',max_charge_su=1536,requested_gpus=16,requested_walltime='00:45:00',reserved_utc=now());reservations.append(z);b['pending_reservations'].append(z)
 b['campaign_headroom_after_reserved_su']=b['commissioning_cap_su']-used-4608;b['unallocated_commissioning_su']=b['campaign_headroom_after_reserved_su'];b['reconciliation_note']='Prior two terminal charges total 925.013 SU reconciled. Three controlled trials reserve 4608 SU maximum. Planning cap and reserve unchanged.';save(P/'nscc-budget.json',b)
 previous=None;validation=json.loads((O/'next-validation.json').read_text())
 for z in reservations:
  name=z['purpose'];z.update(state='SUBMISSION_IN_PROGRESS',dependency_afterany=previous);save(P/'nscc-budget.json',b)
  cmd='cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub '+('-W depend=afterany:'+previous+' ' if previous else '')+'benchmark.pbs'
  try:r=remote(cmd)
  except Exception:
   z['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise
  (O/(name+'-submit.stdout')).write_bytes(r.stdout);(O/(name+'-submit.stderr')).write_bytes(r.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',r.stdout.decode(),re.M)
  if r.returncode or len(ids)!=1:
   z['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise RuntimeError('Uncertain submission: retain reserve, do not retry')
  job=ids[0];z.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now());b['jobs'].append(dict(job_id=job,bundle=name,state='SUBMITTED',requested_gpus=16,requested_walltime='00:45:00',max_charge_su=1536,included_in_ledger_used=False,accounting_pending=True,dependency_afterany=previous,planned_ns=[52] if name.endswith('27') else [50],submitted_utc=now()));b['active_pbs_jobs'].append(job);b['updated_utc']=now();save(P/'nscc-budget.json',b)
  p=P/'continuous-plan.json';plan=json.loads(p.read_text());plan['pilots'].append(dict(id=name,bundle=str(P/name),job_id=job,state='Q' if previous is None else 'H',max_su=1536,minutes=45,ns=[52] if name.endswith('27') else [50],dependency_afterany=previous,uploaded=True,payload_sha256=validation['payloads'][name],accuracy_verified=False,result_state='AWAITING_BENCHMARK'));plan.update(updated_utc=now(),next_bounded_step='Review independent HPC-Ops N50 repeat versus fresh control, then N52 operating point. No automatic N54 or unchanged retry on quality/backend failure.');save(p,plan);print(name,job,flush=True);previous=job
 r=remote('qstat -u apacsc42; qstat -f '+' '.join(z['job_id'] for z in reservations));(O/'pbs-submitted-queue.txt').write_bytes(r.stdout);(O/'pbs-submitted-queue.stderr').write_bytes(r.stderr);assert r.returncode==0;unfold=re.sub(r'\n\t','',r.stdout.decode());assert all('afterany:'+reservations[i-1]['job_id'] in unfold for i in range(1,len(reservations)))
 print('PBS chain verified; 4608 SU maximum reserved; balance',balance,flush=True)
