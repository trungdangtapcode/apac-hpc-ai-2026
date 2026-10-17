"""Reserve and submit one reversed-order I/O confirmation pair, allowing ledger lag."""
from pathlib import Path
import subprocess,shlex,json,re,fcntl,datetime
R=Path.cwd();P=R/'nscc-pbs';O=R/'research-followup-20261017-2335';H='/home/apacsc42/workspace/vpn-rootless/vpn.sh';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def remote(cmd,stdin=None):return subprocess.run(['bash',H,'ssh-batch','bash -lc '+shlex.quote(cmd)],stdin=stdin,capture_output=True,timeout=60)
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
with (O/'io-pair.tar.gz').open('rb') as f:r=remote('cd '+REMOTE+' && tar -xzf - && for name in h100-prefetch-repeat-21 h100-io-control-22; do (cd "$name" && sha256sum --check SHA256SUMS) || exit; done',f)
(O/'io-upload.txt').write_bytes(r.stdout);(O/'io-upload.stderr').write_bytes(r.stderr);assert r.returncode==0
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b.get('uncertain_pbs_jobs')
 r=remote('qstat -u apacsc42; qstat -xf 221153.pbs111 221177.pbs111 221181.pbs111; myprojects');(O/'io-pre-submit.txt').write_bytes(r.stdout);(O/'io-pre-submit.stderr').write_bytes(r.stderr);assert r.returncode==0;s=r.stdout.decode()
 blocks={m.group(1):m.group(2) for m in re.finditer(r'Job Id: (\d+\.pbs\d+)\n(.*?)(?=Job Id: |Project\s*:|\Z)',s,re.S)};assert set(blocks)=={'221153.pbs111','221177.pbs111','221181.pbs111'}
 terminal=[]
 for job,wall in [('221153.pbs111','00:15:45'),('221177.pbs111','00:25:28')]:
  block=blocks[job];assert re.search(r'job_state\s*=\s*F',block) and re.search(r'Exit_status\s*=\s*0\s',block);assert 'resources_used.walltime = '+wall in block
  h,mn,sec=map(int,wall.split(':'));charge=128*16*(h+mn/60+sec/3600);terminal.append((job,wall,charge))
 active={m.group(1) for m in re.finditer(r'^\s*(\d+\.pbs\d+)\s+',s,re.M)};assert active=={'221181.pbs111'},active
 mm=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',s);assert mm;grant,used,balance,doubt=map(float,mm.groups());assert abs(grant-used-balance-doubt)<.01
 delta=used-b['ledger']['used_su'];possibilities=[[],[terminal[0]],terminal];accounted=next((seq for seq in possibilities if abs(sum(x[2] for x in seq)-delta)<.01),None);assert accounted is not None,('Unreconciled ledger increment',delta)
 accounted_ids={x[0] for x in accounted}
 for job,wall,charge in terminal:
  included=job in accounted_ids
  for item in b['jobs']:
   if item['job_id']==job:item.update(state='F',exit_status=0,observed_walltime=wall,estimated_charge_su_from_allocated_walltime=charge,included_in_ledger_used=included,accounting_pending=not included,last_checked_utc=now())
  for reservation in b['pending_reservations']:
   if reservation.get('job_id')==job:reservation.update(state='RECONCILED_IN_LEDGER' if included else 'TERMINAL_PENDING_LEDGER_CONSERVATIVE_RESERVE',last_checked_utc=now())
 outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in ['RECONCILED_IN_LEDGER','CANCELLED','RELEASED'])
 assert used+outstanding+3072<=b['commissioning_cap_su'];assert grant-used-outstanding-3072>=b['retain_project_su'];assert len(active)+2<=b['max_gpu_jobs_pending_or_running']
 b['ledger'].update(grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'io-pre-submit.txt'),as_of=re.search(r'balance as of (\S+)',s).group(1),freshness_note='Terminal charges reconciled where reflected in Used; retain full maximum reserve for terminal ledger lag. Balance already excludes In Doubt; do not subtract prepaid credit twice.');b['active_pbs_jobs']=sorted(active)
 reservations=[]
 for name in ['h100-prefetch-repeat-21','h100-io-control-22']:
  z=dict(purpose=name,state='RESERVED_NOT_SUBMITTED',max_charge_su=1536,requested_gpus=16,requested_walltime='00:45:00',reserved_utc=now());reservations.append(z);b['pending_reservations'].append(z)
 b['campaign_headroom_after_reserved_su']=b['commissioning_cap_su']-used-outstanding-3072;b['unallocated_commissioning_su']=b['campaign_headroom_after_reserved_su'];b['reconciliation_note']='Reversed-order prefetch/control pair reserved at 3072 SU maximum. Outstanding terminal jobs not yet reflected in Used retain their full reservations. Project Balance already excludes In Doubt prepayment; the grant-minus-used planning calculation counts each outstanding reservation once.';save(P/'nscc-budget.json',b)
 previous='221181.pbs111';validation=json.loads((O/'io-pair-validation.json').read_text())
 for z in reservations:
  name=z['purpose'];z.update(state='SUBMISSION_IN_PROGRESS',dependency_afterany=previous);save(P/'nscc-budget.json',b)
  try:r=remote('cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub -W depend=afterany:'+previous+' benchmark.pbs')
  except Exception:
   z['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise
  (O/(name+'-submit.stdout')).write_bytes(r.stdout);(O/(name+'-submit.stderr')).write_bytes(r.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',r.stdout.decode(),re.M)
  if r.returncode or len(ids)!=1:
   z['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise RuntimeError('Uncertain submission; retain reserve and do not retry')
  job=ids[0];z.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now());b['jobs'].append(dict(job_id=job,bundle=name,state='SUBMITTED',requested_gpus=16,requested_walltime='00:45:00',max_charge_su=1536,included_in_ledger_used=False,accounting_pending=True,dependency_afterany=previous,planned_ns=[50],submitted_utc=now()));b['active_pbs_jobs'].append(job);b['updated_utc']=now();save(P/'nscc-budget.json',b)
  p=P/'continuous-plan.json';plan=json.loads(p.read_text());plan['pilots'].append(dict(id=name,bundle=str(P/name),job_id=job,state='H',max_su=1536,minutes=45,ns=[50],dependency_afterany=previous,uploaded=True,payload_sha256=validation['payloads'][name],accuracy_verified=False,result_state='AWAITING_BENCHMARK'));plan['updated_utc']=now();save(p,plan);print(name,job,flush=True);previous=job
 r=remote('qstat -u apacsc42; qstat -f '+' '.join(z['job_id'] for z in reservations));(O/'io-submitted-queue.txt').write_bytes(r.stdout);(O/'io-submitted-queue.stderr').write_bytes(r.stderr);assert r.returncode==0;unfold=re.sub(r'\n\t','',r.stdout.decode())
 for z in reservations:
  block=next(x for x in re.split('Job Id: ',unfold) if x.startswith(z['job_id']));assert 'afterany:'+z['dependency_afterany'] in block
 print('Both dependency links verified; 3072 SU maximum new reservation',flush=True)
