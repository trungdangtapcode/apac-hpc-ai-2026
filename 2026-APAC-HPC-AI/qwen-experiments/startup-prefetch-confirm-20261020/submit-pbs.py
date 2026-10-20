"""Reserve and submit exactly two serial own PBS pilots, with definite receipts and no uncertainty retry."""
from pathlib import Path
import datetime,fcntl,json,re,shlex,subprocess
from reconcile_costs import reconcile
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';HELPER='/home/apacsc42/workspace/vpn-rootless/vpn.sh';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015';receipt=O/'pbs-receipts.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
def remote(command,stdin=None):return subprocess.run(['bash',HELPER,'ssh-batch','bash -lc '+shlex.quote(command)],stdin=stdin,capture_output=True,timeout=60)
assert not receipt.exists(),'Existing receipts: never repeat the batch'
assert json.loads((R/'h100-hpc-smallchunk-20261020/222383.pbs111-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
assert json.loads((R/'router-queue-research-20261020/native-validation.json').read_text())['passed']
assert json.loads((O/'validation.json').read_text())['passed'];assert json.loads((R/'resource-telemetry-20261020/source-validation.json').read_text())['passed']
assert json.loads((R/'research-followup-20261020-h100-restored/222048.pbs111-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
pilots=[p for p in json.loads((O/'pilots.json').read_text()) if p['platform']=='H100'];assert len(pilots)==2 and sum(p['max_su'] for p in pilots)==2048
names=[p['id'] for p in pilots]
with (O/'pbs-bundles.tar.gz').open('rb') as f:
 command='cd '+REMOTE+' && '+' && '.join('test ! -e '+shlex.quote(n) for n in names)+' && tar -xzf - && for name in '+' '.join(names)+'; do (cd "$name" && sha256sum --check SHA256SUMS) || exit; done'
 z=remote(command,f)
(O/'pbs-upload.txt').write_bytes(z.stdout);(O/'pbs-upload.stderr').write_bytes(z.stderr);assert z.returncode==0,'Upload failed; no qsub'
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b['uncertain_pbs_jobs']
 z=remote('qstat -u apacsc42; qstat -xf 222407.pbs111 222408.pbs111 222412.pbs111; myprojects');(O/'pbs-pre-submit.txt').write_bytes(z.stdout);(O/'pbs-pre-submit.stderr').write_bytes(z.stderr);assert z.returncode==0;s=z.stdout.decode();active=re.findall(r'^\s*(\d+\.pbs\d+)\s+',s,re.M);assert set(active)<={'222412.pbs111'} and len(active)+2<=3,'Unexpected active allocation; preserve queue and stop'
 proof=reconcile(b,s,now(),str(O/'pbs-pre-submit.txt'));save(O/'reconciliation.json',proof)
 m=re.search(r'\|\s*SU\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|',s);assert m;grant,used,balance,doubt=map(float,m.groups());assert abs(grant-used-balance-doubt)<.01;assert abs(used-b['ledger']['used_su'])<.01,'Unexplained ledger delta; reconcile before new spending'

 outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'});reserve=sum(x['max_su'] for x in pilots);assert used+outstanding+reserve<=b['commissioning_cap_su'];assert grant-used-outstanding-reserve>=b['retain_project_su']
 b['ledger'].update(as_of=re.search(r'balance as of (\S+)',s).group(1),grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'pbs-pre-submit.txt'),freshness_note='Posted older charges reconcile; retain all unposted maxima before reverse-order prefetch confirmation.')
 reservations=[]
 for p in pilots:
  item=dict(purpose=p['id'],state='RESERVED_NOT_SUBMITTED',max_charge_su=p['max_su'],requested_gpus=16,requested_walltime='00:30:00',reserved_utc=now());reservations.append(item);b['pending_reservations'].append(item)
 b.update(active_pbs_jobs=active.copy(),updated_utc=now(),unallocated_commissioning_su=b['commissioning_cap_su']-used-outstanding-reserve,campaign_headroom_after_reserved_su=b['commissioning_cap_su']-used-outstanding-reserve,reconciliation_note='Reserve at most 2048 SU for one serial observed prefill round-robin/power-of-two pair. Unchanged budget caps; no overlap or uncertain retry.');save(P/'nscc-budget.json',b)
 records=[];previous='222412.pbs111'
 for p,reservation in zip(pilots,reservations):
  record=dict(id=p['id'],state='SUBMISSION_IN_PROGRESS',attempted_utc=now(),dependency_afterany=previous);records.append(record);save(receipt,records);reservation.update(state='SUBMISSION_IN_PROGRESS',dependency_afterany=previous);save(P/'nscc-budget.json',b)
  try:z=remote('cd '+REMOTE+'/'+p['id']+' && sha256sum --check SHA256SUMS >/dev/null && qsub '+('-W depend=afterany:'+previous+' ' if previous else '')+'benchmark.pbs')
  except Exception:
   record['state']=reservation['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(p['id']);save(receipt,records);save(P/'nscc-budget.json',b);raise
  (O/(p['id']+'-submit.stdout')).write_bytes(z.stdout);(O/(p['id']+'-submit.stderr')).write_bytes(z.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',z.stdout.decode(),re.M)
  if z.returncode or len(ids)!=1:
   record['state']=reservation['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(p['id']);save(receipt,records);save(P/'nscc-budget.json',b);raise RuntimeError('Uncertain qsub: do not retry')
  job=ids[0];record.update(state='SUBMITTED',job=job,submitted_utc=now());reservation.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=record['submitted_utc']);save(receipt,records)
  b['jobs'].append(dict(job_id=job,bundle=p['id'],state='SUBMITTED',requested_gpus=16,requested_walltime='00:30:00',max_charge_su=p['max_su'],included_in_ledger_used=False,accounting_pending=True,planned_ns=p['planned_ns'],dependency_afterany=previous,submitted_utc=record['submitted_utc']));b['active_pbs_jobs'].append(job);save(P/'nscc-budget.json',b)
  path=P/'continuous-plan.json';plan=json.loads(path.read_text());assert not any(x['id']==p['id'] for x in plan['pilots']);plan['pilots'].append(dict(id=p['id'],bundle=p['bundle'],job_id=job,state='H' if previous else 'Q',max_su=p['max_su'],minutes=30,ns=p['planned_ns'],uploaded=True,payload_sha256=p['payload_sha256'],resource_monitor=p['resource_monitor'],scheduler_recv_interval_decode=p['scheduler_recv_interval_decode'],dependency_afterany=previous,diagnostic_profile=True,profile_activities=['CPU','GPU'],accuracy_verified=False,result_state='AWAITING_BENCHMARK'));plan.update(updated_utc=now(),next_bounded_step='Apply the prospective reverse-order cost/readiness and score-tolerance gates. Close or mark inconclusive if not reproduced; no automatic third repeat.');save(path,plan);print(p['id'],job,flush=True);previous=job
 z=remote('qstat -u apacsc42; qstat -f '+' '.join(x['job'] for x in records));(O/'pbs-post-submit.txt').write_bytes(z.stdout);(O/'pbs-post-submit.stderr').write_bytes(z.stderr);assert z.returncode==0;s=re.sub(r'\n\t','',z.stdout.decode());assert all('afterany:'+records[i]['job'] in s for i in range(len(records)-1));print('Verified serial dependencies; reserved 2048 SU; headroom',b['campaign_headroom_after_reserved_su'],flush=True)
