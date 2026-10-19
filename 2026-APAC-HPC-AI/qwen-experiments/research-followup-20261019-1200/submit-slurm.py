"""Submit exactly this reviewed H200 batch once, recording every receipt immediately."""
from pathlib import Path
import csv,datetime,fcntl,json,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;D=R/'serving-tuning';receipt=O/'slurm-receipts.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
assert not receipt.exists(),'Existing receipts: do not rerun the batch'
assert json.loads((O/'validation.json').read_text())['passed']
assert json.loads((R/'research-followup-20261019-0600/24724-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS'
pilots=[p for p in json.loads((O/'pilots.json').read_text()) if p['platform']=='H200']
with (D/'watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 queue=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(O/'slurm-pre-submit.txt').write_text(queue);active=[x for x in queue.splitlines() if x.strip()];assert len(active)+len(pilots)<=5
 state=json.loads((D/'registry.json').read_text());assert not any(p['id']==e['id'] for p in pilots for e in state['entries'])
 ids=['24723','24724'];raw=subprocess.check_output(['sacct','-X','-j',','.join(ids),'-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'],text=True);(O/'slurm-source-accounting.txt').write_text(raw);statuses={x['JobID']:x for x in csv.DictReader(raw.splitlines(),delimiter='|')};statuspath=R/'job-status.json';allstatus=json.loads(statuspath.read_text());allstatus.update(statuses);save(statuspath,allstatus)
 for e in state['entries']:
  for a in e['attempts']:
   if a['job'] in ids:
    j=a['job'];assert statuses[j]['State']=='COMPLETED' and statuses[j]['ExitCode']=='0:0';a.update(status=statuses[j],state='COMPLETED',measurements=json.loads((R/'runs'/j/'summary.json').read_text()));e.update(state='MEASURED',benchmark_complete=True,missing_ns=[])
 save(D/'registry.json',state);receipts=[]
 for p in pilots:
  bundle=Path(p['bundle']);subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,check=True)
  record=dict(id=p['id'],state='SUBMISSION_IN_PROGRESS',attempted_utc=now());receipts.append(record);save(receipt,receipts)
  try:result=subprocess.run(['sbatch','--parsable',str(bundle/'job.sbatch')],cwd=R,capture_output=True,text=True,timeout=60)
  except Exception:
   record['state']='SUBMISSION_UNCERTAIN';save(receipt,receipts);raise
  (O/(p['id']+'-submit.stdout')).write_text(result.stdout);(O/(p['id']+'-submit.stderr')).write_text(result.stderr);job=result.stdout.strip().split(';')[0]
  if result.returncode or not job.isdigit():record['state']='SUBMISSION_UNCERTAIN';save(receipt,receipts);raise RuntimeError('Uncertain sbatch: do not retry')
  record.update(job=job,state='SUBMITTED',submitted_utc=now());save(receipt,receipts)
  entry={**p,'state':'ACTIVE','attempts':[dict(job=job,bundle=str(bundle),state='SUBMITTED',submitted_utc=record['submitted_utc'])]};state['entries'].append(entry);state.update(updated_utc=now(),active=True);save(D/'registry.json',state)
  planpath=R/'serving-tuning-10/prepared-pilots.json';plan=json.loads(planpath.read_text());plan['pilots'].append({**p,'state':'SUBMITTED','job':job});plan.update(updated_utc=now(),state='ACTIVE');save(planpath,plan);print(p['id'],job,flush=True)
 queue=subprocess.check_output(['squeue','-u','apacsc42','-o','%.18i %.12P %.32j %.8T %.10M %.6D %R'],text=True);(O/'slurm-post-submit.txt').write_text(queue)
