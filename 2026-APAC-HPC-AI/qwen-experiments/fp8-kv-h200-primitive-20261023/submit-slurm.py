"""Submit one reviewed FP8 KV primitive, preserving uncertain attempts."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,hashlib,json,re,subprocess
O=Path(__file__).resolve().parent;R=O.parent;receipt=O/'slurm-receipt.json'
def save(row): receipt.write_text(json.dumps(row,indent=2)+'\n')
assert json.loads((O/'ROOT_REVIEW.json').read_text())['ready']
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=O,capture_output=True,check=True)
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 assert not receipt.exists(),'Inspect existing submission; never blindly retry'
 queue=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True)
 (O/'pre-submit.txt').write_text(queue);assert len(queue.splitlines())+1<=5
 row=dict(state='SUBMISSION_IN_PROGRESS',attempted_utc=datetime.now(timezone.utc).isoformat(),gpus=1,nodes=1,max_minutes=10,pbs_su_reserved=0,diagnostic_only=True,manifest_sha256=hashlib.sha256((O/'SHA256SUMS').read_bytes()).hexdigest())
 save(row)
 try:r=subprocess.run(['sbatch','--parsable',str(O/'job.sbatch')],cwd=R,capture_output=True,text=True,timeout=30)
 except BaseException:
  row['state']='SUBMISSION_UNCERTAIN';save(row);raise
 (O/'submit.stdout').write_text(r.stdout);(O/'submit.stderr').write_text(r.stderr)
 job=r.stdout.strip().split(';')[0]
 if r.returncode or not job.isdigit():
  row['state']='SUBMISSION_UNCERTAIN';save(row);raise RuntimeError('Inspect scheduler before another attempt')
 row.update(state='SUBMITTED',job=job,submitted_utc=datetime.now(timezone.utc).isoformat());save(row)
 detail=subprocess.check_output(['scontrol','show','job',job],text=True);(O/'post-submit.txt').write_text(detail)
 assert 'TimeLimit=00:10:00' in detail
 print(job,'one H200, at most 10 minutes, no PBS SU')
