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
 fcntl.flock(lock,fcntl.LOCK_EX);q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(O/'slurm-pre-submit.txt').write_text(q);assert len([s for s in q.splitlines() if s.strip()])+1<=5
 record=dict(id=pilot['id'],kind='isolated_microbenchmark',model_loaded=False,state='SUBMISSION_IN_PROGRESS',attempted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(receipt,[record])
 try:z=subprocess.run(['sbatch','--parsable',str(bundle/'job.sbatch')],cwd=R,capture_output=True,text=True,timeout=60)
 except Exception:record['state']='SUBMISSION_UNCERTAIN';save(receipt,[record]);raise
 (O/'slurm-submit.stdout').write_text(z.stdout);(O/'slurm-submit.stderr').write_text(z.stderr);job=z.stdout.strip().split(';')[0]
 if z.returncode or not job.isdigit():record['state']='SUBMISSION_UNCERTAIN';save(receipt,[record]);raise RuntimeError('Uncertain sbatch; no retry')
 record.update(job=job,state='SUBMITTED',submitted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(receipt,[record]);(O/'slurm-post-submit.txt').write_text(subprocess.check_output(['squeue','-u','apacsc42','-o','%.12i %.10T %.28j %.10M %R'],text=True));print(job,flush=True)
