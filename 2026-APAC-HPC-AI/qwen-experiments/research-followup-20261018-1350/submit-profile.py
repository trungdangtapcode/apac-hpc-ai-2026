"""Refresh terminal accounting, reserve two justified trials, submit a strict chain."""
from pathlib import Path
import subprocess,shlex,json,re,fcntl,datetime,itertools
R=Path.cwd();P=R/'nscc-pbs';O=R/'research-followup-20261018-1350';H='/home/apacsc42/workspace/vpn-rootless/vpn.sh';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015';names=['h100-hpc-both-profile-36']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def remote(cmd,stdin=None):return subprocess.run(['bash',H,'ssh-batch','bash -lc '+shlex.quote(cmd)],stdin=stdin,capture_output=True,timeout=60)
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
assert all(json.loads((O/(j+'-review.json')).read_text())['state']=='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS' for j in ['221339.pbs111'])
with (O/'next-pbs.tar.gz').open('rb') as f:r=remote('cd '+REMOTE+' && tar -xzf - && for name in '+' '.join(names)+'; do (cd "$name" && sha256sum --check SHA256SUMS) || exit; done',f)
(O/'pbs-upload.txt').write_bytes(r.stdout);(O/'pbs-upload.stderr').write_bytes(r.stderr);assert r.returncode==0
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b.get('uncertain_pbs_jobs')
 r=remote('qstat -u apacsc42; qstat -xf 221316.pbs111 221339.pbs111; myprojects');(O/'pbs-pre-submit.txt').write_bytes(r.stdout);(O/'pbs-pre-submit.stderr').write_bytes(r.stderr);assert r.returncode==0;s=r.stdout.decode()
 blocks={m.group(1):m.group(2) for m in re.finditer(r'Job Id: (\d+\.pbs\d+)\n(.*?)(?=Job Id: |Project\s*:|\Z)',s,re.S)};active={m.group(1) for m in re.finditer(r'^\s*(\d+\.pbs\d+)\s+',s,re.M)};assert active<= {'221340.pbs111','221341.pbs111'}
 terminal=[]
 for job in ['221316.pbs111','221339.pbs111']:
  block=blocks[job];state=re.search(r'job_state\s*=\s*(\w+)',block).group(1)
  assert state=='F'
  exitcode=int(re.search(r'Exit_status\s*=\s*(-?\d+)',block).group(1));wall=re.search(r'resources_used.walltime\s*=\s*(\S+)',block).group(1)
  h,mn,sec=map(int,wall.split(':'));charge=128*16*(h+mn/60+sec/3600);item=next(x for x in b['jobs'] if x['job_id']==job);terminal.append((job,wall,charge,exitcode,item.get('included_in_ledger_used',False)))
 for job,wall in [('221316.pbs111','00:15:14'),('221339.pbs111','00:11:04')]:assert any(x[0]==job and x[1]==wall and x[3]==0 for x in terminal)
 mm=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',s);assert mm;grant,used,balance,doubt=map(float,mm.groups());assert abs(grant-used-balance-doubt)<.01
 notaccounted=[x for x in terminal if not x[4]];delta=used-b['ledger']['used_su'];possibilities=[list(seq) for size in range(len(notaccounted)+1) for seq in itertools.combinations(notaccounted,size)];accounted=next((seq for seq in possibilities if abs(sum(x[2] for x in seq)-delta)<.01),None);assert accounted is not None,('Unreconciled ledger change',delta);ids={x[0] for x in accounted}
 for job,wall,charge,exitcode,wasincluded in terminal:
  included=wasincluded or job in ids
  for x in b['jobs']:
   if x['job_id']==job:x.update(state='F',exit_status=exitcode,observed_walltime=wall,estimated_charge_su_from_allocated_walltime=charge,included_in_ledger_used=included,accounting_pending=not included,last_checked_utc=now())
  for x in b['pending_reservations']:
   if x.get('job_id')==job:x.update(state='RECONCILED_IN_LEDGER' if included else 'TERMINAL_PENDING_LEDGER_CONSERVATIVE_RESERVE',last_checked_utc=now())
 outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in ['RECONCILED_IN_LEDGER','CANCELLED','RELEASED']);assert used+outstanding+1536<=b['commissioning_cap_su'];assert grant-used-outstanding-1536>=b['retain_project_su'];assert len(active)+1<=3
 b['ledger'].update(grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'pbs-pre-submit.txt'),as_of=re.search(r'balance as of (\S+)',s).group(1),freshness_note='Reconcile only charges reflected in Used; retain full maximum reservations for ledger lag. Balance already excludes prepayment.');b['active_pbs_jobs']=sorted(active)
 reservations=[]
 for name in names:
  z=dict(purpose=name,state='RESERVED_NOT_SUBMITTED',max_charge_su=1536,requested_gpus=16,requested_walltime='00:45:00',reserved_utc=now());reservations.append(z);b['pending_reservations'].append(z)
 b['campaign_headroom_after_reserved_su']=b['commissioning_cap_su']-used-outstanding-1536;b['unallocated_commissioning_su']=b['campaign_headroom_after_reserved_su'];b['reconciliation_note']='HPC-Ops gain passes a fresh control comparison. Reserve 1536 SU for replicated both-phase HPC-Ops N50 score plus separate post-score profile. Reconcile old terminal charges and retain any ledger-lag reserve.';save(P/'nscc-budget.json',b)
 previous='221341.pbs111';validation=json.loads((O/'next-validation.json').read_text())
 for z in reservations:
  name=z['purpose'];z.update(state='SUBMISSION_IN_PROGRESS',dependency_afterany=previous);save(P/'nscc-budget.json',b)
  try:r=remote('cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub '+('-W depend=afterany:'+previous+' ' if previous else '')+'benchmark.pbs')
  except Exception:
   z['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise
  (O/(name+'-submit.stdout')).write_bytes(r.stdout);(O/(name+'-submit.stderr')).write_bytes(r.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',r.stdout.decode(),re.M)
  if r.returncode or len(ids)!=1:
   z['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise RuntimeError('Uncertain submission; retain reserve, do not retry')
  job=ids[0];z.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now());b['jobs'].append(dict(job_id=job,bundle=name,state='SUBMITTED',requested_gpus=16,requested_walltime='00:45:00',max_charge_su=1536,included_in_ledger_used=False,accounting_pending=True,dependency_afterany=previous,planned_ns=[52] if name.endswith('35') else [50],submitted_utc=now()));b['active_pbs_jobs'].append(job);b['updated_utc']=now();save(P/'nscc-budget.json',b)
  p=P/'continuous-plan.json';plan=json.loads(p.read_text());plan['pilots'].append(dict(id=name,bundle=str(P/name),job_id=job,state='H' if previous else 'Q',max_su=1536,minutes=45,ns=[52] if name.endswith('35') else [50],dependency_afterany=previous,uploaded=True,payload_sha256=validation['payloads'][name],accuracy_verified=False,result_state='AWAITING_BENCHMARK'));plan.update(updated_utc=now(),next_bounded_step='Review new decode-only control and both-phase N52, then classify actual HPC-Ops kernel trace names from both-phase profile. Close losing branches; no blind load increase.');save(p,plan);print(name,job,flush=True);previous=job
 r=remote('qstat -u apacsc42; qstat -f '+' '.join(z['job_id'] for z in reservations));(O/'pbs-submitted-queue.txt').write_bytes(r.stdout);(O/'pbs-submitted-queue.stderr').write_bytes(r.stderr);assert r.returncode==0;unfold=re.sub(r'\n\t','',r.stdout.decode());assert all('afterany:'+z['dependency_afterany'] in unfold for z in reservations if z['dependency_afterany'])
 print('Dependencies verified; new reserve 1536 SU; planning headroom',b['campaign_headroom_after_reserved_su'],flush=True)
