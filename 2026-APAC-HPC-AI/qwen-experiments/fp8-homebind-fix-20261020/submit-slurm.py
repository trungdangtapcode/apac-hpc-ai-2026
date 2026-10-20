"""Submit one bounded repaired micro screen; preserve all existing model jobs."""
from pathlib import Path
import datetime,fcntl,json,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;receipt=O/'slurm-receipts.json';bundle=R/'serving-tuning-10/s25-fp8-workbind'
def save(d):receipt.write_text(json.dumps(d,indent=2)+'\n')
assert not receipt.exists(),'Do not retry an existing or uncertain submission'
assert json.loads((O/'validation.json').read_text())['passed']
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,check=True,capture_output=True)
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(O/'slurm-pre-submit.txt').write_text(q)
 assert len(q.splitlines())<5
 record=dict(state='SUBMISSION_IN_PROGRESS',attempted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bundle=str(bundle),model_loaded=False,replaces_failed_job='24990');save(record)
 try:z=subprocess.run(['sbatch','--parsable',str(bundle/'job.sbatch')],cwd=R,capture_output=True,text=True,timeout=60)
 except Exception:record['state']='SUBMISSION_UNCERTAIN';save(record);raise
 (O/'submit.stdout').write_text(z.stdout);(O/'submit.stderr').write_text(z.stderr);job=z.stdout.strip().split(';')[0]
 if z.returncode or not job.isdigit():record['state']='SUBMISSION_UNCERTAIN';save(record);raise RuntimeError('Do not retry uncertain sbatch')
 record.update(state='SUBMITTED',job=job,submitted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(record)
 (O/'slurm-post-submit.txt').write_text(subprocess.check_output(['squeue','-u','apacsc42','-o','%.12i %.10T %.28j %.10M %R'],text=True));print(job)
