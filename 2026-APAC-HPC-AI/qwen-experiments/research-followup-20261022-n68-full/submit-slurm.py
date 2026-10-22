"""Submit the frozen full pair once, under the shared GPU queue lock."""
from pathlib import Path
from datetime import datetime,timezone
import csv,fcntl,json,re,subprocess
O=Path(__file__).resolve().parent;R=O.parent;D=R/'serving-tuning';receipt=O/'slurm-receipts.json'
def now():return datetime.now(timezone.utc).isoformat()
def save(p,data):tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(p)
assert not receipt.exists(),'Existing submission attempt; do not repeat uncertain sbatch'
assert json.loads((O/'validation.json').read_text())['passed']
review=json.loads((R/'research-review-25371-20261022/REVIEW.json').read_text());assert review['state']=='SHORT_LOCAL_PROTOCOL_SLA_OUTPUT_PASS' and review['practical_one_percent_screen_gate']
pilots=json.loads((O/'pilots.json').read_text());assert len(pilots)==2
for p in pilots:subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=p['bundle'],check=True,capture_output=True)
with (D/'watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 part=subprocess.check_output(['scontrol','show','partition','hpcai'],text=True);(O/'partition-preflight.txt').write_text(part);limit=re.search(r'MaxTime=(\S+)',part)[1];assert limit=='UNLIMITED' or sum(int(n)*factor for n,factor in zip(limit.split(':'),(3600,60,1)))>=17*60
 queue=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(O/'slurm-pre-submit.txt').write_text(queue);assert len(queue.splitlines())+2<=5
 raw=subprocess.check_output(['sacct','-X','-j','25371,25373','-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'],text=True);(O/'slurm-source-accounting.txt').write_text(raw);statuses={r['JobID']:r for r in csv.DictReader(raw.splitlines(),delimiter='|')};assert set(statuses)=={'25371','25373'} and all(s['State']=='COMPLETED' and s['ExitCode']=='0:0' for s in statuses.values())
 registry=json.loads((D/'registry.json').read_text());assert all(not any(e['id']==p['id'] for e in registry['entries']) for p in pilots)
 for entry in registry['entries']:
  for attempt in entry['attempts']:
   if attempt['job'] in statuses:
    attempt.update(status=statuses[attempt['job']],state='COMPLETED')
    if entry['state'] not in ('MEASURED','SCREEN_MEASURED'):entry['state']='COMPLETED_REVIEW_REQUIRED'
 save(D/'registry.json',registry)
 statusfile=R/'job-status.json';state=json.loads(statusfile.read_text());state.update(statuses);save(statusfile,state)
 receipts=[];dependency=None
 for p in pilots:
  record=dict(id=p['id'],state='SUBMISSION_IN_PROGRESS',attempted_utc=now(),dependency_afterok=dependency,requested_gpus=16,minutes=17);receipts.append(record);save(receipt,receipts)
  command=['sbatch','--parsable']+(['--dependency=afterok:'+dependency] if dependency else [])+[str(Path(p['bundle'])/'job.sbatch')]
  try:result=subprocess.run(command,cwd=R,capture_output=True,text=True,timeout=60)
  except Exception:record['state']='SUBMISSION_UNCERTAIN';save(receipt,receipts);raise
  (O/(p['id']+'-submit.stdout')).write_text(result.stdout);(O/(p['id']+'-submit.stderr')).write_text(result.stderr);job=result.stdout.strip().split(';')[0]
  if result.returncode or not job.isdigit():record['state']='SUBMISSION_UNCERTAIN';save(receipt,receipts);raise RuntimeError('Uncertain submission; never retry blindly')
  record.update(job=job,state='SUBMITTED',submitted_utc=now());save(receipt,receipts)
  registry['entries'].append({**p,'state':'ACTIVE','attempts':[dict(job=job,bundle=p['bundle'],state='SUBMITTED',submitted_utc=record['submitted_utc'],dependency_afterok=dependency)]});registry.update(updated_utc=now(),active=True);save(D/'registry.json',registry)
  path=R/'serving-tuning-10/prepared-pilots.json';plan=json.loads(path.read_text());assert not any(row['id']==p['id'] for row in plan['pilots']);plan['pilots'].append({**p,'state':'SUBMITTED','job':job});plan.update(updated_utc=now(),state='ACTIVE');save(path,plan)
  detail=subprocess.check_output(['scontrol','show','job',job],text=True);(O/(job+'-detail.txt')).write_text(detail);assert 'TimeLimit=00:17:00' in detail and 'Reason=PartitionTimeLimit' not in detail
  if dependency:assert 'afterok:'+dependency in detail
  dependency=job;print(job,p['id'],'16H200 max17min; no PBS SU',flush=True)
 (O/'slurm-post-submit.txt').write_text(subprocess.check_output(['squeue','-u','apacsc42','-o','%i %T %M %j %R'],text=True))
