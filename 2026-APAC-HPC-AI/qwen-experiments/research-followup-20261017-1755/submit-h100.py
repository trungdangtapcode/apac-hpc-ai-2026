"""Submit one prefill graph ablation after fresh queue and budget checks."""
from pathlib import Path
import subprocess,shlex,json,re,fcntl,datetime
R=Path.cwd();P=R/'nscc-pbs';O=R/'research-followup-20261017-1755';H='/home/apacsc42/workspace/vpn-rootless/vpn.sh';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015';name='h100-prefill-no-graph-20'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def remote(c,stdin=None):return subprocess.run(['bash',H,'ssh-batch','bash -lc '+shlex.quote(c)],stdin=stdin,capture_output=True,timeout=60)
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
with (O/'h100-no-graph.tar.gz').open('rb') as f:r=remote('cd '+REMOTE+' && tar -xzf - && cd '+name+' && sha256sum --check SHA256SUMS',f)
(O/'upload.txt').write_bytes(r.stdout);(O/'upload.stderr').write_bytes(r.stderr);assert r.returncode==0
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b.get('uncertain_pbs_jobs')
 r=remote('qstat -u apacsc42; qstat -f 221153.pbs111 221177.pbs111; myprojects');(O/'pre-submit-queue-credit.txt').write_bytes(r.stdout);(O/'pre-submit-queue-credit.stderr').write_bytes(r.stderr);assert r.returncode==0;s=r.stdout.decode();active={m.group(1) for m in re.finditer(r'^\s*(\d+\.pbs\d+)\s+',s,re.M)};assert active=={'221153.pbs111','221177.pbs111'},active;assert 'afterany:221153.pbs111' in s
 m=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',s);assert m;grant,used,balance,doubt=map(float,m.groups());assert doubt==0 and abs(used-b['ledger']['used_su'])<.01
 pending=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in ['RECONCILED_IN_LEDGER','CANCELLED','RELEASED']);assert pending==3072;assert used+pending+1536<=b['commissioning_cap_su'];assert balance-pending-1536>=b['retain_project_su'];assert len(active)+1<=b['max_gpu_jobs_pending_or_running']
 b['ledger'].update(queried_utc=now(),source=str(O/'pre-submit-queue-credit.txt'),freshness_note='All own queue, dependency and project ledger checked before one graph ablation. Usage unchanged.');b['ledger']['as_of']=re.search(r'balance as of (\S+)',s).group(1)
 reservation=dict(purpose=name,state='RESERVED_NOT_SUBMITTED',max_charge_su=1536,requested_gpus=16,requested_walltime='00:45:00',dependency_afterany='221177.pbs111',reserved_utc=now());b['pending_reservations'].append(reservation);b['campaign_headroom_after_reserved_su']=b['commissioning_cap_su']-used-pending-1536;b['unallocated_commissioning_su']=b['campaign_headroom_after_reserved_su'];save(P/'nscc-budget.json',b)
 reservation['state']='SUBMISSION_IN_PROGRESS';save(P/'nscc-budget.json',b)
 try:r=remote('cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub -W depend=afterany:221177.pbs111 benchmark.pbs')
 except Exception:
  reservation['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise
 (O/'submit.stdout').write_bytes(r.stdout);(O/'submit.stderr').write_bytes(r.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',r.stdout.decode(),re.M)
 if r.returncode or len(ids)!=1:
  reservation['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);raise RuntimeError('Uncertain submission: preserve reservation and do not retry')
 job=ids[0];reservation.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now());b['jobs'].append(dict(job_id=job,bundle=name,state='SUBMITTED',requested_gpus=16,requested_walltime='00:45:00',max_charge_su=1536,included_in_ledger_used=False,accounting_pending=True,dependency_afterany='221177.pbs111',planned_ns=[50],submitted_utc=now()));b['active_pbs_jobs']=sorted(active)+[job];b['updated_utc']=now();save(P/'nscc-budget.json',b);print('Submitted',job,flush=True)
 r=remote('qstat -f '+job);(O/'submitted-job.txt').write_bytes(r.stdout);(O/'submitted-job.stderr').write_bytes(r.stderr);assert r.returncode==0 and 'afterany:221177.pbs111' in r.stdout.decode()
 f=P/'continuous-plan.json';p=json.loads(f.read_text());h=json.loads((O/'validation.json').read_text())['bundles'][name];p['pilots'].append(dict(id=name,bundle=str(P/name),job_id=job,state='H',max_su=1536,minutes=45,ns=[50],dependency_afterany='221177.pbs111',uploaded=True,payload_sha256=h,result_state='AWAITING_BENCHMARK',accuracy_verified=False));p['updated_utc']=now();save(f,p);print('Verified dependency; total outstanding reservation 4608 SU',flush=True)
