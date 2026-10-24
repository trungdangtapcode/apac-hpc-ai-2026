"""Admit one reviewed unranked performance arm under the existing Slurm cap."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,fcntl,hashlib,json,subprocess
O=Path(__file__).resolve().parent;R=O.parent
p=argparse.ArgumentParser();p.add_argument('--arm',choices=['control','candidate'],required=True);arm=p.parse_args().arm
proof=json.loads((O/f'ROOT_REVIEW_{arm.upper()}.json').read_text());assert proof['ready']
B=Path(proof['bundle']);receipt=O/f'{arm}-slurm-receipt.json'
assert hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest()==proof['manifest_sha256']
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=B,capture_output=True,check=True)
subprocess.run(['python3','-B',str(B/'preflight-assets.py')],capture_output=True,check=True)
with (R/'serving-tuning/watcher.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);assert not receipt.exists(),'Existing or uncertain receipts require inspection; never blindly retry'
 queue=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%T|%j'],text=True);(O/f'{arm}-pre-submit.txt').write_text(queue);assert len(queue.splitlines())+1<=5
 part=subprocess.check_output(['scontrol','show','partition','hpcai'],text=True);(O/f'{arm}-partition.txt').write_text(part);assert 'MaxTime=00:17:00' in part or 'MaxTime=UNLIMITED' in part
 args=['sbatch','--parsable']
 if arm=='candidate':
  control=json.loads((O/'control-slurm-receipt.json').read_text());assert control['state']=='SUBMITTED'
  binding=json.loads((B/'matched-control.json').read_text());assert binding['control_job']==control['job'] and binding['control_manifest_sha256']==control['manifest_sha256']
  args += ['--dependency=afterok:'+control['job']]
 args += [str(B/'job.sbatch')]
 row={'state':'SUBMISSION_IN_PROGRESS','attempted_utc':datetime.now(timezone.utc).isoformat(),'arm':arm,'bundle':str(B),'manifest_sha256':proof['manifest_sha256'],'gpus':16,'nodes':2,'minutes':17,'pbs_su_reserved':0,'ranked':False,'quality':'UNKNOWN_NOT_EVALUATED','known_exact_ID_failure':'25862 remains FAILED; no official quality conclusion','scope':'Matched performance feasibility only, no promotion or qualified speedup'}
 def save():receipt.write_text(json.dumps(row,indent=2)+'\n')
 save()
 try:r=subprocess.run(args,cwd=R,capture_output=True,text=True,timeout=30)
 except BaseException:row['state']='SUBMISSION_UNCERTAIN';save();raise
 (O/f'{arm}-submit.stdout').write_text(r.stdout);(O/f'{arm}-submit.stderr').write_text(r.stderr);job=r.stdout.strip().split(';')[0]
 if r.returncode or not job.isdigit():row['state']='SUBMISSION_UNCERTAIN';save();raise RuntimeError('Inspect actual scheduler before another admission')
 row.update(job=job,state='SUBMITTED',submitted_utc=datetime.now(timezone.utc).isoformat());save()
 detail=subprocess.check_output(['scontrol','show','job',job],text=True);(O/f'{arm}-post-submit.txt').write_text(detail);assert 'TimeLimit=00:17:00' in detail
 print(job,arm,'unranked EAGLE performance feasibility /16H200 /17min /qualityUNKNOWN')
