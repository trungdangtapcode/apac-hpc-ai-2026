"""Reserve and submit one bounded kernel pilot; never retry an uncertain qsub."""
from pathlib import Path
import datetime,fcntl,json,re,shlex,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015';HELPER='/home/apacsc42/workspace/vpn-rootless/vpn.sh';receipts=O/'pbs-receipts.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,data):
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(path)
def remote(command,handle=None):return subprocess.run(['bash',HELPER,'ssh-batch','bash -lc '+shlex.quote(command)],stdin=handle,capture_output=True,timeout=60)
assert not receipts.exists(),'Existing receipt: never repeat this submission'
assert json.loads((O/'validation.json').read_text())['passed']
pilot=json.loads((O/'pilot.json').read_text());name=pilot['id'];assert pilot['requested_gpus']==8 and pilot['minutes']==10
with (O/'pbs-bundles.tar.gz').open('rb') as handle:
 result=remote('cd '+REMOTE+' && test ! -e '+shlex.quote(name)+' && tar -xzf - && cd '+shlex.quote(name)+' && sha256sum --check SHA256SUMS',handle)
(O/'pbs-upload.txt').write_bytes(result.stdout);(O/'pbs-upload.stderr').write_bytes(result.stderr);assert result.returncode==0
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);budget=json.loads((P/'nscc-budget.json').read_text());assert not budget.get('uncertain_pbs_jobs')
 result=remote('qstat -u apacsc42; myprojects');(O/'pbs-pre-submit.txt').write_bytes(result.stdout);(O/'pbs-pre-submit.stderr').write_bytes(result.stderr);assert result.returncode==0
 text=result.stdout.decode();active=re.findall(r'^\s*(\d+\.pbs\d+)\s+',text,re.M);assert not active,'Own queue changed: review serialization before submitting'
 match=re.search(r'\|\s*SU\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|',text);assert match
 grant,used,balance,doubt=map(float,match.groups());assert abs(grant-used-balance-doubt)<.01;assert abs(used-budget['ledger']['used_su'])<.01,'New charge requires explicit reconciliation'
 outstanding=sum(r['max_charge_su'] for r in budget['pending_reservations'] if r['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'});assert outstanding==0
 reserve=8*128*10/60;assert abs(reserve-pilot['max_su'])<1e-6
 assert used+reserve<=budget['commissioning_cap_su'] and grant-used-reserve>=budget['retain_project_su']
 budget['ledger'].update(grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,as_of=re.search(r'balance as of (\S+)',text).group(1),queried_utc=now(),source=str(O/'pbs-pre-submit.txt'))
 reservation=dict(purpose=name,state='RESERVED_NOT_SUBMITTED',max_charge_su=reserve,requested_gpus=8,requested_walltime='00:10:00',reserved_utc=now());budget['pending_reservations'].append(reservation)
 budget.update(active_pbs_jobs=[],updated_utc=now(),campaign_headroom_after_reserved_su=budget['commissioning_cap_su']-used-reserve,unallocated_commissioning_su=budget['commissioning_cap_su']-used-reserve,reconciliation_note='All previous three model jobs reconciled first. One 8-GPU 10-minute isolated collective pilot, max170.667 SU. No budget increase or model-score claim.')
 reservation['state']='SUBMISSION_IN_PROGRESS';save(P/'nscc-budget.json',budget);record=dict(id=name,state='SUBMISSION_IN_PROGRESS',attempted_utc=now());save(receipts,[record])
 try:result=remote('cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub benchmark.pbs')
 except Exception:
  reservation['state']=record['state']='SUBMISSION_UNCERTAIN';budget['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',budget);save(receipts,[record]);raise
 (O/'submit.stdout').write_bytes(result.stdout);(O/'submit.stderr').write_bytes(result.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',result.stdout.decode(),re.M)
 if result.returncode or len(ids)!=1:
  reservation['state']=record['state']='SUBMISSION_UNCERTAIN';budget['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',budget);save(receipts,[record]);raise RuntimeError('Uncertain submission: do not retry')
 job=ids[0];record.update(state='SUBMITTED',job=job,submitted_utc=now());reservation.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now());save(receipts,[record])
 budget['jobs'].append(dict(job_id=job,bundle=name,state='SUBMITTED',requested_gpus=8,requested_walltime='00:10:00',max_charge_su=reserve,included_in_ledger_used=False,accounting_pending=True,kind='isolated_microbenchmark',model_loaded=False,submitted_utc=now()));budget['active_pbs_jobs']=[job];save(P/'nscc-budget.json',budget)
 path=P/'continuous-plan.json';plan=json.loads(path.read_text());plan['pilots'].append(dict(id=name,bundle=pilot['bundle'],job_id=job,state='Q',kind='isolated_microbenchmark',max_su=reserve,minutes=10,requested_gpus=8,ns=[],uploaded=True,payload_sha256=pilot['payload_sha256'],accuracy_verified=False,result_state='AWAITING_MICROBENCH_NOT_MODEL_SCORE'));plan.update(updated_utc=now(),current_job_state='ONE_MICROBENCH_SUBMITTED',chain_jobs=[job],last_confirmed_current_job=job,next_bounded_step='Review all eight ranks, shape/strategy/numerical/input-integrity/captured timing and trace evidence of the isolated collective pilot. It is not model goodput. Prepare full-model patch/control only on a useful signal; close unchanged flat inference-mode trials.');save(path,plan)
 result=remote('qstat -u apacsc42; qstat -f '+job);(O/'pbs-post-submit.txt').write_bytes(result.stdout);(O/'pbs-post-submit.stderr').write_bytes(result.stderr);assert result.returncode==0 and 'select = 1:ngpus=8:mpiprocs=1' in result.stdout.decode()
 print(name,job,'maximum reserve',reserve,'internal headroom',budget['campaign_headroom_after_reserved_su'],flush=True)
