#!/usr/bin/env python3
"""Admit only this reviewed bounded bracket, preserving live queue and frozen payloads."""
from pathlib import Path
import datetime,fcntl,hashlib,json,subprocess
D=Path(__file__).resolve().parent;Q=D.parent
prep=json.loads((D/'preparation.json').read_text());valid=json.loads((D/'validation.json').read_text())
assert valid['state']=='PASS_CPU_FIXTURES_ONLY' and len(valid['fixtures'])==27 and all(x['passed'] for x in valid['fixtures'])
assert len(prep['bundles'])==3 and [b['interval'] for b in prep['bundles']]==[1,2,4]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
with (Q/'.slurm-admission.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 initial=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%j|%T|%M|%D|%R'],text=True)
 assert len(initial.splitlines())+3<=5, 'Preserve own live/pending cap 5; do not cancel existing jobs'
 for item in prep['bundles']:
  B=Q/item['bundle'];k=item['interval'];out=D/f'admission-interval{k}';out.mkdir(exist_ok=False)
  queue=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i|%j|%T|%M|%D|%R'],text=True)
  assert len(queue.splitlines())<5
  assert hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest()==item['manifest_sha256']
  subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
  test=subprocess.run(['sbatch','--test-only',str(B/'job.sbatch')],cwd=Q,text=True,capture_output=True)
  assert test.returncode==0,test.stdout+test.stderr
  reservation={'utc':now(),'state':'READY_NOT_SUBMITTED','queue_before':queue,'interval':k,'H200':16,'nodes':2,'minutes':17,'maximum_GPU_hours':16*17/60,'PBS_SU':0,'manifest_sha256':item['manifest_sha256'],'reason':'Prospectively bounded full polling interval 1/2/4 bracket, fresh target-only control and two distinct admission/coordination tradeoffs'}
  (out/'reservation.json').write_text(json.dumps(reservation,indent=2)+'\n')
  run=subprocess.run(['sbatch','--parsable',str(B/'job.sbatch')],cwd=Q,text=True,capture_output=True)
  receipt={'utc':now(),'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'test_only':test.stdout+test.stderr,'payload':str(B/'job.sbatch'),'manifest_sha256':item['manifest_sha256'],'interval':k,'state':'REJECTED_NO_JOB'}
  if run.returncode==0:
   token=run.stdout.strip().split(';')[0];assert token.isdigit(),receipt
   job=int(token);receipt.update(job=job,state='SUBMITTED_NOT_MEASURED')
   reservation.update(job=job,state='SUBMITTED')
   (out/'reservation.json').write_text(json.dumps(reservation,indent=2)+'\n')
   # Save the definite sbatch receipt BEFORE any secondary scheduler query.
   (out/'submission-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
   info=subprocess.run(['scontrol','show','job',str(job)],text=True,capture_output=True)
   receipt.update(scontrol_returncode=info.returncode,scontrol=info.stdout,scontrol_error=info.stderr)
  (out/'submission-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
  assert run.returncode==0,receipt
  print(json.dumps({'interval':k,'job':job,'state':receipt['state']}),flush=True)
 print(subprocess.check_output(['squeue','-u','apacsc42','-o','%.18i %.24j %.8T %.10M %.6D %R'],text=True))
