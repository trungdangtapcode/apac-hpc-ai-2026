"""Submit one frozen observed load-frontier candidate under the AI queue lock, never retry uncertain."""
from pathlib import Path
from datetime import datetime,timezone
import csv,fcntl,json,subprocess
O=Path(__file__).resolve().parent;R=O.parent;D=R/'serving-tuning';receipt=O/'slurm-receipts.json'
def now():return datetime.now(timezone.utc).isoformat()
def save(p,d):tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(p)
assert not receipt.exists(),'Existing attempt: do not repeat uncertain sbatch'
assert json.loads((O/'validation.json').read_text())['passed']
review=json.loads((R/'research-review-24962-20261021/REVIEW.json').read_text());assert review['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS'
pilots=json.loads((O/'pilots.json').read_text());assert len(pilots)==1;p=pilots[0];bundle=Path(p['bundle'])
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True,capture_output=True)
with (D/'watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(O/'slurm-pre-submit.txt').write_text(q);active=[line for line in q.splitlines() if line.strip()];assert len(active)+1<=5
 registry=json.loads((D/'registry.json').read_text());assert not any(e['id']==p['id'] for e in registry['entries'])
 raw=subprocess.check_output(['sacct','-X','-j','24962','-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'],text=True);(O/'slurm-source-accounting.txt').write_text(raw);statuses={row['JobID']:row for row in csv.DictReader(raw.splitlines(),delimiter='|')};assert statuses['24962']['State']=='COMPLETED' and statuses['24962']['ExitCode']=='0:0'
 for e in registry['entries']:
  for a in e['attempts']:
   if a['job']=='24962':a.update(status=statuses['24962'],state='COMPLETED',measurements=json.loads((R/'runs/24962/summary.json').read_text()));e.update(state='MEASURED',benchmark_complete=True,missing_ns=[])
 save(D/'registry.json',registry)
 statuspath=R/'job-status.json';state=json.loads(statuspath.read_text());state.update(statuses);save(statuspath,state)
 record=dict(id=p['id'],state='SUBMISSION_IN_PROGRESS',attempted_utc=now(),dependency_afterok=None,requested_gpus=16,minutes=22);save(receipt,[record])
 try:result=subprocess.run(['sbatch','--parsable',str(bundle/'job.sbatch')],cwd=R,capture_output=True,text=True,timeout=60)
 except Exception:record['state']='SUBMISSION_UNCERTAIN';save(receipt,[record]);raise
 (O/'slurm-submit.stdout').write_text(result.stdout);(O/'slurm-submit.stderr').write_text(result.stderr);job=result.stdout.strip().split(';')[0]
 if result.returncode or not job.isdigit():record['state']='SUBMISSION_UNCERTAIN';save(receipt,[record]);raise RuntimeError('Uncertain submission: do not retry')
 record.update(state='SUBMITTED',job=job,submitted_utc=now());save(receipt,[record])
 registry['entries'].append({**p,'state':'ACTIVE','attempts':[dict(job=job,bundle=str(bundle),state='SUBMITTED',submitted_utc=record['submitted_utc'],dependency_afterok=None)]});registry.update(updated_utc=now(),active=True);save(D/'registry.json',registry)
 planpath=R/'serving-tuning-10/prepared-pilots.json';plan=json.loads(planpath.read_text());assert not any(x['id']==p['id'] for x in plan['pilots']);plan['pilots'].append({**p,'state':'SUBMITTED','job':job});plan.update(updated_utc=now(),state='ACTIVE');save(planpath,plan)
 post=subprocess.check_output(['squeue','-u','apacsc42','-o','%.18i %.12P %.32j %.8T %.10M %.6D %R'],text=True);(O/'slurm-post-submit.txt').write_text(post)
 detail=subprocess.check_output(['scontrol','show','job',job],text=True);(O/'slurm-job-detail.txt').write_text(detail);assert 'Dependency=(null)' in detail
 print(job,'16H200 max22min, same-deployment observed N62->N64, no PBS SU')
