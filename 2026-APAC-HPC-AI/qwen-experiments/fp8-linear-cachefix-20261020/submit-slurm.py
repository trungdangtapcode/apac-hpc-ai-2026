"""Submit the standalone kernel screen once without exposing it as a model score."""
from pathlib import Path
import datetime,fcntl,json,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;receipt=O/'slurm-receipts.json'
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
assert not receipt.exists(),'Never repeat an existing or uncertain sbatch'
assert json.loads((O/'validation.json').read_text())['passed']
pilot=next(p for p in json.loads((O/'pilots.json').read_text()) if p['platform']=='H200');bundle=Path(pilot['bundle']);subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True,capture_output=True)
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(O/'slurm-pre-submit.txt').write_text(q)
 old_rows=[line.split('|') for line in q.splitlines() if line.split('|')[0]=='24983']
 if old_rows:
  assert len(old_rows)==1 and old_rows[0][2]=='ap42-fp8-linear-micro'
  if old_rows[0][1]!='PENDING':raise RuntimeError('Original micro has started; preserve it and defer replacement')
  cancellation=dict(job='24983',state_before='PENDING',reason='Replace unconfigured standalone cache harness; four model jobs untouched')
  save(O/'old-slurm-cancellation.json',cancellation)
  z=subprocess.run(['scancel','--state=PENDING','24983'],capture_output=True,text=True,timeout=60)
  cancellation.update(returncode=z.returncode,stdout=z.stdout,stderr=z.stderr);save(O/'old-slurm-cancellation.json',cancellation);assert z.returncode==0
 q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(O/'slurm-after-replacement-cancel.txt').write_text(q)
 assert not any(line.split('|')[0]=='24983' for line in q.splitlines()),'Old micro not removed; no new sbatch'
 assert len([line for line in q.splitlines() if line.strip()])+1<=5
 record=dict(id=pilot['id'],kind='isolated_microbenchmark',model_loaded=False,state='SUBMISSION_IN_PROGRESS',attempted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(receipt,[record])
 try:z=subprocess.run(['sbatch','--parsable',str(bundle/'job.sbatch')],cwd=R,capture_output=True,text=True,timeout=60)
 except Exception:record['state']='SUBMISSION_UNCERTAIN';save(receipt,[record]);raise
 (O/'slurm-submit.stdout').write_text(z.stdout);(O/'slurm-submit.stderr').write_text(z.stderr);job=z.stdout.strip().split(';')[0]
 if z.returncode or not job.isdigit():record['state']='SUBMISSION_UNCERTAIN';save(receipt,[record]);raise RuntimeError('Uncertain sbatch; no retry')
 record.update(job=job,state='SUBMITTED',submitted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(receipt,[record]);(O/'slurm-post-submit.txt').write_text(subprocess.check_output(['squeue','-u','apacsc42','-o','%.12i %.10T %.28j %.10M %R'],text=True));print(job,flush=True)
