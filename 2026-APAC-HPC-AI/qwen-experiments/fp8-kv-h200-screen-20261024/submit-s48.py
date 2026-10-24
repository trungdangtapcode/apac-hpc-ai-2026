"""Submit one frozen FP8 KV matched performance candidate under the Slurm lock."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,hashlib,json,re,subprocess
O=Path(__file__).resolve().parent;R=O.parent
proof=json.loads((O/'S48_ROOT_REVIEW.json').read_text());assert proof['ready']
B=Path(proof['bundle']);receipt=O/'s48-slurm-receipt.json'
assert hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest()==proof['manifest_sha256']
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=B,capture_output=True,check=True)
subprocess.run(['python3','-B',str(B/'preflight-assets.py')],capture_output=True,check=True)
def save(r):receipt.write_text(json.dumps(r,indent=2)+'\n')
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);assert not receipt.exists(),'Do not blindly retry any recorded submission'
 partition=subprocess.check_output(['scontrol','show','partition','hpcai'],text=True);(O/'s48-partition-preflight.txt').write_text(partition)
 assert 'MaxTime=00:17:00' in partition or 'MaxTime=UNLIMITED' in partition
 queue=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(O/'s48-pre-submit.txt').write_text(queue);assert len(queue.splitlines())+1<=5
 row=dict(state='SUBMISSION_IN_PROGRESS',attempted_utc=datetime.now(timezone.utc).isoformat(),bundle=str(B),gpus=16,nodes=2,minutes=17,pbs_su_reserved=0,diagnostic_only=True,purpose='Matched FP8 KV candidate after actual control25863 passes; independent control replay before workers')
 save(row)
 try:r=subprocess.run(['sbatch','--parsable','--dependency=afterok:25863',str(B/'job.sbatch')],cwd=R,capture_output=True,text=True,timeout=30)
 except BaseException:row['state']='SUBMISSION_UNCERTAIN';save(row);raise
 (O/'s48-submit.stdout').write_text(r.stdout);(O/'s48-submit.stderr').write_text(r.stderr);job=r.stdout.strip().split(';')[0]
 if r.returncode or not job.isdigit():row['state']='SUBMISSION_UNCERTAIN';save(row);raise RuntimeError('Inspect scheduler before another attempt')
 row.update(job=job,state='SUBMITTED',submitted_utc=datetime.now(timezone.utc).isoformat());save(row)
 detail=subprocess.check_output(['scontrol','show','job',job],text=True);(O/'s48-post-submit.txt').write_text(detail);assert 'TimeLimit=00:17:00' in detail
 print(job,'FP8 KV matched performance candidate /16H200 /17minutes /noPBS SU')
