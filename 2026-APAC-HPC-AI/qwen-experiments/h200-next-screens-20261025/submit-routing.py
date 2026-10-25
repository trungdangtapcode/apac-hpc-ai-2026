#!/usr/bin/env python3
"""One explicit bounded routing-pair admission; never retry uncertain sbatch."""
from pathlib import Path
import datetime,fcntl,json,subprocess
Q=Path(__file__).resolve().parents[1]
OUT=Path(__file__).with_name('receipts-routing.json')
assert not OUT.exists(), 'Receipt exists: inspect before any further admission'
with (Q/'.slurm-admission.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    queue=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i %T %j %R'],text=True)
    assert len(queue.splitlines())+2<=5,queue
    record={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'queue_before':queue,'gpus_per_job':16,'max_minutes_per_job':17,'pbs_su':0,'jobs':[]}
    OUT.write_text(json.dumps(record,indent=2)+'\n')
    control=None
    for name in ('s65-h200-router-rr-control','s64-h200-prefill-power-of-two'):
        bundle=Q/'serving-tuning-11'/name
        subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=bundle,check=True,stdout=subprocess.DEVNULL)
        dependency=['--dependency=afterany:'+control] if control else []
        test=subprocess.run(['sbatch','--test-only',*dependency,str(bundle/'job.sbatch')],cwd=Q,capture_output=True,text=True)
        row={'bundle':str(bundle),'test_returncode':test.returncode,'test_stdout':test.stdout,'test_stderr':test.stderr,'dependency':dependency}
        record['jobs'].append(row);OUT.write_text(json.dumps(record,indent=2)+'\n')
        assert test.returncode==0,row
        fresh=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True)
        assert len(fresh.splitlines())<5
        result=subprocess.run(['sbatch','--parsable',*dependency,str(bundle/'job.sbatch')],cwd=Q,capture_output=True,text=True)
        row.update(submit_returncode=result.returncode,submit_stdout=result.stdout,submit_stderr=result.stderr)
        OUT.write_text(json.dumps(record,indent=2)+'\n')
        assert result.returncode==0,result.stderr
        job=result.stdout.strip().split(';')[0]
        assert job.isdigit(),'Uncertain receipt: do not repeat sbatch'
        row['job_id']=job;OUT.write_text(json.dumps(record,indent=2)+'\n')
        if control is None:control=job
        state=subprocess.run(['scontrol','show','job',job],capture_output=True,text=True)
        row['scontrol']=state.stdout;row['scontrol_returncode']=state.returncode
        OUT.write_text(json.dumps(record,indent=2)+'\n')
        assert str(Q/'runs'/f'{job}.out') in state.stdout,'Unexpected stdout path; inspect actual submitted job'
        print(json.dumps({'bundle':name,'job':job,'dependency':dependency}),flush=True)
