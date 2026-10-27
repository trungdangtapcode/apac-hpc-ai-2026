#!/usr/bin/env python3
"""Admit the two full native-runtime load bracket jobs exactly once under cap five."""
from pathlib import Path
import datetime,fcntl,hashlib,json,subprocess
S=Path(__file__).resolve().parent;Q=S.parent;OUT=S/'submission-receipts.json'
assert __import__('json').loads((S/'verification.json').read_text())['state']=='CPU_PREPARATION_PASS_NOT_GPU_ACCEPTANCE'
assert not OUT.exists(),'Existing attempt: inspect definite/uncertain IDs before another submission'
names=['s78-h200-full-chunk12288']
with (Q/'.slurm-admission.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 queue=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i %T %j %R'],text=True);assert len(queue.splitlines())+len(names)<=5,queue
 record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queue_before':queue,'gpus_per_job':16,'max_minutes_per_job':17,'pbs_su':0,'jobs':[]};OUT.write_text(json.dumps(record,indent=2)+'\n')
 previous=None
 for name in names:
  b=Q/'serving-tuning-11'/name
  subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,check=True,stdout=subprocess.DEVNULL)
  dep=['--dependency=afterany:'+previous] if previous else []
  test=subprocess.run(['sbatch','--test-only',*dep,str(b/'job.sbatch')],cwd=Q,capture_output=True,text=True)
  row={'bundle':name,'manifest_sha256':hashlib.sha256((b/'SHA256SUMS').read_bytes()).hexdigest(),'test_returncode':test.returncode,'test_stdout':test.stdout,'test_stderr':test.stderr,'dependency':dep};record['jobs'].append(row);OUT.write_text(json.dumps(record,indent=2)+'\n');assert test.returncode==0,row
  fresh=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True);assert len(fresh.splitlines())<5
  sub=subprocess.run(['sbatch','--parsable',*dep,str(b/'job.sbatch')],cwd=Q,capture_output=True,text=True)
  row.update(submit_returncode=sub.returncode,submit_stdout=sub.stdout,submit_stderr=sub.stderr);OUT.write_text(json.dumps(record,indent=2)+'\n');assert sub.returncode==0,sub.stderr
  job=sub.stdout.strip().split(';')[0];assert job.isdigit(),'Uncertain receipt: never retry blindly'
  row.update(job=job,submitted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());OUT.write_text(json.dumps(record,indent=2)+'\n')
  row['scontrol']=subprocess.check_output(['scontrol','show','job',job],text=True);OUT.write_text(json.dumps(record,indent=2)+'\n')
  assert str(Q/'runs'/f'{job}.out') in row['scontrol'] and 'TimeLimit=00:17:00' in row['scontrol']
  previous=job;print(json.dumps({'job':job,'bundle':name,'dependency':dep}),flush=True)
 record['queue_after']=subprocess.check_output(['squeue','-u','apacsc42','-o','%.12i %.24j %.10T %.10M %.4D %R'],text=True);OUT.write_text(json.dumps(record,indent=2)+'\n');print(record['queue_after'])
