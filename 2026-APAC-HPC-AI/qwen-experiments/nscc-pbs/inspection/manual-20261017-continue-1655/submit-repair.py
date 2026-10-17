"""Reconcile completed jobs, reserve one bounded retry, then submit once."""
from pathlib import Path
import datetime,subprocess,shlex,re,json,fcntl
R=Path.cwd();P=R/'nscc-pbs';O=P/'inspection/manual-20261017-continue-1655';H='/home/apacsc42/workspace/vpn-rootless/vpn.sh';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015';name='h100-prefill-deepgemm-retry-19'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def remote(cmd,stdin=None):return subprocess.run(['bash',H,'ssh-batch','bash -lc '+shlex.quote(cmd)],stdin=stdin,capture_output=True,timeout=60)
def save(path,data):
 t=path.with_suffix('.tmp');t.write_text(json.dumps(data,indent=2)+'\n');t.replace(path)
with (O/'h100-retry.tar.gz').open('rb') as f:r=remote('cd '+REMOTE+' && tar -xzf - && cd '+name+' && sha256sum --check SHA256SUMS',f)
(O/'upload.txt').write_bytes(r.stdout);(O/'upload.stderr').write_bytes(r.stderr);assert r.returncode==0
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b.get('uncertain_pbs_jobs')
 r=remote('qstat -u apacsc42; qstat -xf 221151.pbs111 221152.pbs111 221153.pbs111; myprojects');(O/'pre-submit-state-credit.txt').write_bytes(r.stdout);(O/'pre-submit-state-credit.stderr').write_bytes(r.stderr);assert r.returncode==0;s=r.stdout.decode()
 blocks={m.group(1):m.group(2) for m in re.finditer(r'Job Id: (\d+\.pbs\d+)\n(.*?)(?=Job Id: |Project\s*:|\Z)',s,re.S)}
 assert set(blocks)=={'221151.pbs111','221152.pbs111','221153.pbs111'}
 expected_charge=0
 for job,wall,exit_code in [('221151.pbs111','00:24:51',0),('221152.pbs111','00:20:13',1)]:
  block=blocks[job];assert re.search(r'job_state\s*=\s*F',block);assert re.search(r'Exit_status\s*=\s*'+str(exit_code)+r'\s',block);assert 'resources_used.walltime = '+wall in block
  hh,mm,ss=map(int,wall.split(':'));charge=128*16*(hh+mm/60+ss/3600);expected_charge+=charge
  for item in b['jobs']:
   if item['job_id']==job:item.update(state='F',exit_status=exit_code,observed_walltime=wall,included_in_ledger_used=True,accounting_pending=False,estimated_charge_su_from_allocated_walltime=charge,last_checked_utc=now())
  for reservation in b['pending_reservations']:
   if reservation.get('job_id')==job:reservation.update(state='RECONCILED_IN_LEDGER',reconciled_utc=now())
 m=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',s);assert m;grant,used,balance,doubt=map(float,m.groups());assert doubt==0;assert abs(used-b['ledger']['used_su']-expected_charge)<.01,(used,b['ledger']['used_su'],expected_charge)
 active={m.group(1) for m in re.finditer(r'^\s*(\d+\.pbs\d+)\s+',s,re.M)};assert active=={'221153.pbs111'},active
 assert re.search(r'job_state\s*=\s*Q',blocks['221153.pbs111'])
 reserve=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in ['RECONCILED_IN_LEDGER','CANCELLED','RELEASED']);assert reserve==1536,reserve
 assert used+reserve+1536<=b['commissioning_cap_su'];assert balance-reserve-1536>=b['retain_project_su'];assert len(active)+1<=b['max_gpu_jobs_pending_or_running']
 b['active_pbs_jobs']=sorted(active);b['ledger'].update(grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'pre-submit-state-credit.txt'),freshness_note='Fresh ledger and all own jobs checked; terminal charges reconcile within 0.01 SU.')
 stamp=re.search(r'balance as of (\S+)',s);b['ledger']['as_of']=stamp.group(1) if stamp else 'See raw ledger'
 reservation=dict(purpose=name,state='RESERVED_NOT_SUBMITTED',max_charge_su=1536,requested_gpus=16,requested_walltime='00:45:00',reserved_utc=now(),dependency_afterany='221153.pbs111');b['pending_reservations'].append(reservation);b['campaign_headroom_after_reserved_su']=b['commissioning_cap_su']-used-reserve-1536;b['unallocated_commissioning_su']=b['campaign_headroom_after_reserved_su'];save(P/'nscc-budget.json',b)
 reservation['state']='SUBMISSION_IN_PROGRESS';save(P/'nscc-budget.json',b)
 try:r=remote('cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub -W depend=afterany:221153.pbs111 benchmark.pbs')
 except Exception:
  reservation['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise
 (O/'submit.stdout').write_bytes(r.stdout);(O/'submit.stderr').write_bytes(r.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',r.stdout.decode(),re.M)
 if r.returncode or len(ids)!=1:
  reservation['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise RuntimeError('Uncertain submission; retain reservation and do not retry.')
 job=ids[0];reservation.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now());b['jobs'].append(dict(job_id=job,state='SUBMITTED',requested_gpus=16,requested_walltime='00:45:00',max_charge_su=1536,included_in_ledger_used=False,accounting_pending=True,bundle=name,dependency_afterany='221153.pbs111',planned_ns=[50],submitted_utc=now()));b['active_pbs_jobs'].append(job);b['updated_utc']=now();b['reconciliation_note']='221151 (24:51) and failed 221152 (20:13) charges total 1538.2756 SU, matching the ledger increment. Both reservations are reconciled. Prefetch 221153 and one readiness-only retry retain 3072 SU total maximum reservation.';save(P/'nscc-budget.json',b);print('Submitted',job,flush=True)
 r=remote('qstat -f '+job);(O/'submitted-job.txt').write_bytes(r.stdout);(O/'submitted-job.stderr').write_bytes(r.stderr);assert r.returncode==0;assert 'afterany:221153.pbs111' in r.stdout.decode();print('Verified afterany dependency and reserved credit',flush=True)
 v=json.loads((O/'validation.json').read_text());f=P/'continuous-plan.json';p=json.loads(f.read_text())
 for item in p['pilots']:
  if item.get('job_id')=='221151.pbs111':item.update(state='F',result_state='REVIEWED_PROTOCOL_RUNTIME_SHORT_LONG_PASS',terminal_review=str(O/'review-221151.json'),accuracy_verified=False)
  if item.get('job_id')=='221152.pbs111':item.update(state='F',result_state='FAILED_BEFORE_BENCHMARK_READINESS_TIMEOUT',exit_status=1,benchmark_complete=False)
 p['pilots'].append(dict(id=name,bundle=str(P/name),job_id=job,state='H',max_su=1536,minutes=45,ns=[50],dependency_afterany='221153.pbs111',uploaded=True,payload_sha256=v['pbs'][name],retry_of='221152.pbs111',result_state='AWAITING_BENCHMARK',accuracy_verified=False));p['updated_utc']=now();save(f,p)
