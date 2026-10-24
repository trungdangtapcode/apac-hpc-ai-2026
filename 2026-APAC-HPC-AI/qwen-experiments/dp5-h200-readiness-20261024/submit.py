"""Admit one sealed five-H200 startup diagnostic; no retry after an uncertain receipt."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parent
receipt=B/'slurm-receipt.json'
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 assert not receipt.exists(), 'Inspect an existing receipt instead of duplicating admission'
 review=json.loads((B/'ROOT_CANDIDATE_REVIEW_BINDING.json').read_text());assert review['state']=='ROOT_REVIEWED_READY'
 subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=B,capture_output=True,check=True)
 subprocess.run(['python3','-B',str(B/'prepare_check.py')],capture_output=True,check=True)
 subprocess.run(['python3','-B',str(B/'preflight-assets.py')],capture_output=True,check=True)
 q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(B/'pre-submit-queue.txt').write_text(q);assert len(q.splitlines())+1<=5
 partition=subprocess.check_output(['scontrol','show','partition','hpcai'],text=True);(B/'partition-preflight.txt').write_text(partition);assert 'MaxTime=00:17:00' in partition or 'MaxTime=UNLIMITED' in partition
 row={'state':'SUBMISSION_IN_PROGRESS','attempted_utc':datetime.now(timezone.utc).isoformat(),'gpus':5,'nodes':1,'wall_minutes':17,'pbs_su_reserved':0,'purpose':'Decode-only target TP5/DP5/EP5 readiness, no generation or performance claim','manifest_sha256':hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest()}
 def save():receipt.write_text(json.dumps(row,indent=2)+'\n')
 save()
 try:r=subprocess.run(['sbatch','--parsable',str(B/'job.sbatch')],cwd=R,capture_output=True,text=True,timeout=30)
 except BaseException:row['state']='SUBMISSION_UNCERTAIN';save();raise
 (B/'submit.stdout').write_text(r.stdout);(B/'submit.stderr').write_text(r.stderr)
 job=r.stdout.strip().split(';')[0]
 if r.returncode or not job.isdigit():row['state']='SUBMISSION_UNCERTAIN';save();raise RuntimeError('Inspect scheduler before another submission')
 row.update(state='SUBMITTED',job=job,submitted_utc=datetime.now(timezone.utc).isoformat());save()
 detail=subprocess.check_output(['scontrol','show','job',job],text=True);(B/'post-submit.txt').write_text(detail);assert 'TimeLimit=00:17:00' in detail
 print(job,'D5 startup readiness /5 H200 /17minutes /noPBS SU')
