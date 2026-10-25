#!/usr/bin/env python3
"""Admit the two reviewed phase-isolated screens once within the cap of five."""
from pathlib import Path
import datetime,fcntl,hashlib,json,subprocess
S=Path(__file__).resolve().parent;Q=S.parent;OUT=S/'submission-receipts.json'
assert not OUT.exists(),'Prior receipt exists: inspect; never blindly repeat admission'
with (Q/'.slurm-admission.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 queue=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i %T %j %R'],text=True)
 assert len(queue.splitlines())+2<=5,queue
 control=subprocess.check_output(['scontrol','show','job','26083'],text=True)
 assert 'UserId=apacsc42' in control and ('JobState=PENDING' in control or 'JobState=RUNNING' in control or 'JobState=COMPLETED' in control), 'Fresh control not in admissible state'
 report={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queue_before':queue,'control_before':control,'gpus_per_job':16,'max_minutes_per_job':17,'pbs_su':0,'jobs':[]};OUT.write_text(json.dumps(report,indent=2)+'\n')
 for stage,sid in [('prefill',66),('decode',67)]:
  b=Q/f'serving-tuning-11/s{sid}-h200-{stage}-fused-qk-rope'
  subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,check=True,stdout=subprocess.DEVNULL)
  dep='--dependency=afterany:26083'
  t=subprocess.run(['sbatch','--test-only',dep,str(b/'job.sbatch')],cwd=Q,capture_output=True,text=True)
  row={'bundle':str(b),'bundle_sha256sums_sha256':hashlib.sha256((b/'SHA256SUMS').read_bytes()).hexdigest(),'dependency':dep,'test_returncode':t.returncode,'test_stdout':t.stdout,'test_stderr':t.stderr};report['jobs'].append(row);OUT.write_text(json.dumps(report,indent=2)+'\n');assert t.returncode==0,row
  fresh=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True);assert len(fresh.splitlines())<5
  result=subprocess.run(['sbatch','--parsable',dep,str(b/'job.sbatch')],cwd=Q,capture_output=True,text=True)
  row.update(submit_returncode=result.returncode,submit_stdout=result.stdout,submit_stderr=result.stderr);OUT.write_text(json.dumps(report,indent=2)+'\n');assert result.returncode==0,result.stderr
  job=result.stdout.strip().split(';')[0];assert job.isdigit(),'Uncertain receipt: do not repeat'
  row['job_id']=job;OUT.write_text(json.dumps(report,indent=2)+'\n')
  state=subprocess.run(['scontrol','show','job',job],capture_output=True,text=True);row['scontrol']=state.stdout;OUT.write_text(json.dumps(report,indent=2)+'\n')
  assert str(Q/'runs'/f'{job}.out') in state.stdout,'Unexpected actual scheduler stdout; inspect submitted job'
  print(json.dumps({'job':job,'bundle':b.name,'dependency':dep}),flush=True)
 report['queue_after']=subprocess.check_output(['squeue','-u','apacsc42','-o','%.16i %.24j %.10T %.10M %.4D %R'],text=True);report['checked_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();OUT.write_text(json.dumps(report,indent=2)+'\n');print(report['queue_after'])
